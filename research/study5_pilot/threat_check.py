"""Study 5 threat check v0.1 (THREAT_CHECK_SPEC_v0.1.md): Route A' = Study 1's Route A estimator fed with gradient
features (the exact test's statistic at every layer) instead of activation features, on the tuning keys only.

Phases:
  validate  inputs only (pool C unwatermarked texts and the tuning keys); no statistic on any watermarked text
  run       per-text all-layer gradients and activation means for the tuning-key texts (refuses unless the spec is
            FIXED and committed); checkpointed per file
  analyse   estimates, cosines and the pre-set reading -> outputs/study5_threat_v0.1/{results.json, REPORT.md}
Run: .venv/bin/python research/study5_pilot/threat_check.py --phase validate|run|analyse
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in ("study1_v02", "study1", "study3_pilot"):
    sys.path.insert(0, str(ROOT / "research" / p))
import common as C2  # noqa: E402  (Study 1 v0.2, locked: configures qwen, all_layer_means)
import attack2  # noqa: E402  (Study 1 v0.2, locked: route_a; it imports study1/attack.zscores)
import power_pilot as PP  # noqa: E402  (Study 3 pilot, locked: tuning keys, hooks, loglik, text_features, unit)
from common import core  # noqa: E402

SPEC = HERE / "THREAT_CHECK_SPEC_v0.1.md"
DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study5_threat_v0.1"
CAL = ROOT / "research" / "repro" / "data" / "qwen"
V02 = ROOT / "research" / "study1_v02" / "data"
C_TEXTS, C_FEATS = V02 / "S_C_ref.json", V02 / "S_C_ref_feats.npy"
TUNING = [9001, 9002, 9003, 9004]
LEVELS = [0.35, 0.50, 0.70]
N_GRID = [4, 16, 64, 100]
N_REF = 200
K, D, NL, LAYER = C2.K_SUPPORT, C2.D_MODEL, C2.N_LAYERS, C2.LAYER   # 4, 1536, 28, 14
COS_BAR, N_MAX, SPURIOUS_MAX, TIME_BUDGET_H = 0.5, 100, 0.3, 0.5


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tag(rho):
    return f"r{int(round(rho * 100)):03d}"


def obs_file(rho, s):
    return CAL / f"texts_calib_{tag(rho)}_k{s}.json"


def load_json(p):
    return json.loads(Path(p).read_text())


def key_dir(s):
    return PP.unit(PP.tuning_key(s, 1.0).astype(np.float64))


# ---------------------------------------------------------------- features
def all_layer_grads(tok, model, text):
    """[28, d] float32: d loglik / d b_l at b_l = 0 for an additive vector b_l at the output of every decoder layer
    (one forward and one backward pass; the forward is numerically unchanged because every b_l is zero)."""
    dev = core.device()
    enc = core._encode(tok, [text]).to(dev)
    cm = enc.pop("content_mask")
    bs = [torch.zeros(1, 1, D, device=dev, dtype=torch.float32, requires_grad=True) for _ in range(NL)]
    hs = [model.model.layers[li].register_forward_hook(PP._hook(bs[li])) for li in range(NL)]
    try:
        PP._loglik(model, enc, cm).backward()
    finally:
        for h in hs:
            h.remove()
    G = np.stack([b.grad[0, 0].detach().float().cpu().numpy() for b in bs]).astype(np.float32)
    model.zero_grad(set_to_none=True)
    torch.mps.empty_cache()
    return G


def grads_for(tok, model, texts, log_every=50, label=""):
    out, t0 = [], time.time()
    for i, t in enumerate(texts):
        out.append(all_layer_grads(tok, model, t))
        if log_every and (i + 1) % log_every == 0:
            print(f"  {label} {i + 1}/{len(texts)} grads, {time.time() - t0:.0f}s", flush=True)
    return np.stack(out)


# ---------------------------------------------------------------- estimates (the attacker sees features only)
def cos(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)).clip(1e-12))


def route_a_prime(obs, ref, rho):
    """Route A' = attack2.route_a on gradient (or activation) features [n, L, d] vs [m, L, d]; unit reference norms."""
    la, va, prof = attack2.route_a(obs, ref, K, rho, np.ones(NL))
    return la, va, prof


def layer_fixed_estimate(obs, ref, layer):
    """Descriptive: the same support rule restricted to one layer (support recovery given the layer)."""
    la, va, _ = attack2.route_a(obs[:, layer:layer + 1], ref[:, layer:layer + 1], K, 1.0, np.ones(1))
    return va


def score(vhat, s):
    v = key_dir(s)
    hit = len(set(np.flatnonzero(vhat)) & set(np.flatnonzero(v))) / K
    return {"cos": cos(vhat, v), "support_hit": hit}


# ---------------------------------------------------------------- guard
def spec_guard():
    txt = SPEC.read_text()
    if "**Status:** FIXED" not in txt:
        sys.exit("refused: the spec is not marked FIXED (Yichen's approval comes first)")
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(SPEC), str(Path(__file__))], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        sys.exit(f"refused: the spec or this script has uncommitted changes:\n{dirty}")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"spec_sha256": sha(SPEC), "script_sha256": sha(Path(__file__)), "commit": commit}


# ---------------------------------------------------------------- validate (inputs only)
def validate():
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    checks, t_start = {}, time.time()
    files = {f"{tag(r)}_k{s}": obs_file(r, s) for r in LEVELS for s in TUNING}
    files["C_texts"], files["C_feats"] = C_TEXTS, C_FEATS
    missing = [k for k, p in files.items() if not p.exists()]
    counts = {k: len(load_json(p)) for k, p in files.items() if p.exists() and p.suffix == ".json"}
    cf = np.load(C_FEATS, mmap_mode="r") if C_FEATS.exists() else None
    norms_ok = all(abs(np.linalg.norm(PP.tuning_key(s, r)) - r * PP.N_REF) < 1e-3 and
                   int((PP.tuning_key(s, r) != 0).sum()) == K for s in TUNING for r in LEVELS)
    checks["1_inputs"] = {"pass": bool(not missing and all(counts[k] == 100 for k in counts if k != "C_texts")
                                       and counts.get("C_texts") == 2000 and cf is not None and cf.shape == (2000, NL, D)
                                       and norms_ok),
                          "missing": missing, "counts": counts, "C_feats_shape": list(cf.shape) if cf is not None else None,
                          "sha256": {k: sha(p) for k, p in files.items() if p.exists()}}

    tok, model = PP.load()
    ctexts = load_json(C_TEXTS)
    # 2 (bf16 part): the 28-hook gradient vs the single-hook gradient at layer 14, and the bf16 run-to-run noise
    rel_bf16, cos_bf16, rr_bf16 = [], [], []
    for t in ctexts[:3]:
        g1 = PP.text_features(tok, model, t)[1].astype(np.float64)
        g1b = PP.text_features(tok, model, t)[1].astype(np.float64)
        G = all_layer_grads(tok, model, t)[LAYER].astype(np.float64)
        rel_bf16.append(float(np.linalg.norm(G - g1) / np.linalg.norm(g1)))
        cos_bf16.append(cos(G, g1))
        rr_bf16.append(float(np.linalg.norm(g1b - g1) / np.linalg.norm(g1)))

    dev = core.device()
    enc = core._encode(tok, [ctexts[3]]).to(dev)
    enc.pop("content_mask")
    with torch.no_grad():
        before = model(**enc).logits.float().cpu()
    all_layer_grads(tok, model, ctexts[4])
    with torch.no_grad():
        after = model(**enc).logits.float().cpu()
    diff = float((before - after).abs().max())
    checks["3_hooks_removed"] = {"pass": diff == 0.0, "max_abs_logit_diff": diff}

    # 4. no spurious recovery on unwatermarked texts (also the run's reference checkpoint)
    t0 = time.time()
    fC = DATA / "grads_C.npz"
    if not fC.exists():
        np.savez(fC, G=grads_for(tok, model, ctexts[:N_REF], label="C ref"), sha=sha(C_TEXTS))
    fN = DATA / "grads_Cnull.npz"
    if not fN.exists():
        np.savez(fN, G=grads_for(tok, model, ctexts[N_REF:N_REF + 100], label="C null"), sha=sha(C_TEXTS))
    per_text = (time.time() - t0) / 300 if (time.time() - t0) > 60 else None
    refG = np.load(fC)["G"]
    nullG = np.load(fN)["G"]
    la, va, _ = route_a_prime(nullG[:100], refG, 1.0)
    spurious = {str(s): abs(cos(va, key_dir(s))) for s in TUNING}
    checks["4_no_spurious_recovery"] = {"pass": max(spurious.values()) <= SPURIOUS_MAX, "abs_cos": spurious,
                                        "layer_hat": la}

    if per_text is None:  # checkpoints existed: time 10 fresh passes
        t0 = time.time()
        for t in ctexts[300:310]:
            all_layer_grads(tok, model, t)
        per_text = (time.time() - t0) / 10
    t0 = time.time()
    C2.all_layer_means(tok, model, ctexts[:32])
    per_act = (time.time() - t0) / 32
    n_obs = len(LEVELS) * len(TUNING) * 100
    proj_h = (per_text * n_obs + per_act * n_obs) / 3600
    checks["5_timing"] = {"pass": proj_h <= TIME_BUDGET_H, "s_per_grad_text": per_text, "s_per_act_text": per_act,
                          "n_obs_texts": n_obs, "projected_h": proj_h, "budget_h": TIME_BUDGET_H}
    # 2 (float32 part): the same agreement with the model in float32 (bf16 gradients are noisy; Study 2 pilot lesson)
    del model
    import gc
    gc.collect()
    torch.mps.empty_cache()
    tok32, model32 = core.load_model()
    model32.float()
    for prm in model32.parameters():
        prm.requires_grad_(False)
    rel32 = []
    for t in ctexts[:3]:
        g1 = PP.text_features(tok32, model32, t)[1].astype(np.float64)
        G = all_layer_grads(tok32, model32, t)[LAYER].astype(np.float64)
        rel32.append(float(np.linalg.norm(G - g1) / np.linalg.norm(g1)))
    del model32
    gc.collect()
    torch.mps.empty_cache()
    checks["2_grad_agreement"] = {"pass": max(rel32) <= 1e-3 and min(cos_bf16) >= 0.99,
                                  "relative_diff_float32": rel32, "bf16_relative_diff": rel_bf16, "bf16_cos": cos_bf16,
                                  "bf16_run_to_run_relative_diff": rr_bf16}
    checks = {k: checks[k] for k in sorted(checks)}
    res = {"spec": SPEC.name, "spec_sha256": sha(SPEC), "script_sha256": sha(Path(__file__)),
           "date_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
           "note": "inputs only: pool C unwatermarked texts and the tuning keys; no statistic on any watermarked text",
           "checks": checks, "all_pass": all(c["pass"] for c in checks.values()), "elapsed_s": time.time() - t_start}
    (OUT / "VALIDATION.json").write_text(json.dumps(res, indent=2))
    for k, c in checks.items():
        print(k, "PASS" if c["pass"] else "FAIL", {x: y for x, y in c.items() if x != "sha256"})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


# ---------------------------------------------------------------- run
def run():
    guard = spec_guard()
    DATA.mkdir(parents=True, exist_ok=True)
    assert (DATA / "grads_C.npz").exists(), "run validate first (it writes the reference gradients)"
    tok, model = PP.load()
    t0 = time.time()
    for rho in LEVELS:
        for s in TUNING:
            f = DATA / f"feats_{tag(rho)}_k{s}.npz"
            if f.exists():
                continue
            texts = load_json(obs_file(rho, s))
            G = grads_for(tok, model, texts, log_every=0)
            A = C2.all_layer_means(tok, model, texts)
            np.savez(f, G=G, A=A, sha=sha(obs_file(rho, s)))
            print(f"{tag(rho)} k{s}: {len(texts)} texts, {time.time() - t0:.0f}s", flush=True)
    (DATA / "run_guard.json").write_text(json.dumps(guard, indent=2))
    print("run complete", flush=True)


# ---------------------------------------------------------------- analyse
def analyse():
    guard = spec_guard()
    refG = np.load(DATA / "grads_C.npz")["G"]
    refA = np.load(C_FEATS, mmap_mode="r")[:N_REF].astype(np.float32)
    res = {"guard": guard, "run_guard": load_json(DATA / "run_guard.json"), "n_grid": N_GRID, "levels": {}}
    for rho in LEVELS:
        L = {"per_key": {}, "median": {}}
        for s in TUNING:
            z = np.load(DATA / f"feats_{tag(rho)}_k{s}.npz")
            assert str(z["sha"]) == sha(obs_file(rho, s)), "observed texts changed since the run"
            G, A = z["G"], z["A"]
            e = {}
            for n in N_GRID:
                lg, vg, _ = route_a_prime(G[:n], refG, rho)
                la, va, _ = route_a_prime(A[:n], refA, rho)
                vf = layer_fixed_estimate(G[:n], refG, LAYER)
                e[str(n)] = {"grad": {"layer": lg, **score(vg, s)}, "act": {"layer": la, **score(va, s)},
                             "grad_layer14": score(vf, s)}
            L["per_key"][str(s)] = e
        for n in N_GRID:
            L["median"][str(n)] = {m: {"cos": float(np.median([L["per_key"][str(s)][str(n)][m]["cos"] for s in TUNING])),
                                       "support_hit": float(np.median([L["per_key"][str(s)][str(n)][m]["support_hit"]
                                                                       for s in TUNING]))}
                                   for m in ("grad", "act", "grad_layer14")}
            L["median"][str(n)]["layer_hits_grad"] = int(sum(L["per_key"][str(s)][str(n)]["grad"]["layer"] == LAYER
                                                             for s in TUNING))
            L["median"][str(n)]["layer_hits_act"] = int(sum(L["per_key"][str(s)][str(n)]["act"]["layer"] == LAYER
                                                            for s in TUNING))
        res["levels"][str(rho)] = L
    real = {str(rho): any(res["levels"][str(rho)]["median"][str(n)]["grad"]["cos"] >= COS_BAR for n in N_GRID if n <= N_MAX)
            for rho in (0.50, 0.70)}
    res["reading"] = {"bar": COS_BAR, "n_max": N_MAX, "threat_real_at": real,
                      "verdict": "threat real" if any(real.values()) else "extend to n = 1,024 (v0.2) before a verdict"}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    lines = ["# Study 5 threat check v0.1 — report (generated by threat_check.py from results.json)", "",
             f"Spec `{SPEC.name}` (sha256 {guard['spec_sha256'][:12]}), commit {guard['commit'][:7]}. "
             f"Pre-set reading: the threat is real if the median cos over the 4 tuning keys is ≥ {COS_BAR} at some n ≤ {N_MAX} "
             f"at ρ = 0.50 or 0.70. **Verdict: {res['reading']['verdict']}** (0.50: {real['0.5']}; 0.70: {real['0.7']}).", "",
             "## Median over the 4 tuning keys: cos(v̂, v), support hit rate, layer hits (of 4)", "",
             "| ρ | n | Route A′ (gradients) cos | support hit | layer = 14 | Route A (activations) cos | support hit | layer = 14 | gradients at the true layer: cos |",
             "|---|---|---|---|---|---|---|---|---|"]
    for rho in LEVELS:
        for n in N_GRID:
            m = res["levels"][str(rho)]["median"][str(n)]
            lines.append(f"| {rho} | {n} | {m['grad']['cos']:.3f} | {m['grad']['support_hit']:.2f} | {m['layer_hits_grad']} | "
                         f"{m['act']['cos']:.3f} | {m['act']['support_hit']:.2f} | {m['layer_hits_act']} | {m['grad_layer14']['cos']:.3f} |")
    lines += ["", "## Per key, Route A′ at n = 100: cos (layer)", "", "| ρ | " + " | ".join(str(s) for s in TUNING) + " |",
              "|---|" + "---|" * len(TUNING)]
    for rho in LEVELS:
        pk = res["levels"][str(rho)]["per_key"]
        lines.append(f"| {rho} | " + " | ".join(f"{pk[str(s)]['100']['grad']['cos']:.2f} ({pk[str(s)]['100']['grad']['layer']})"
                                               for s in TUNING) + " |")
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(res["reading"], indent=2))
    for rho in LEVELS:
        print(rho, {n: round(res["levels"][str(rho)]["median"][str(n)]["grad"]["cos"], 3) for n in N_GRID})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["validate", "run", "analyse"], required=True)
    {"validate": validate, "run": run, "analyse": analyse}[ap.parse_args().phase]()
