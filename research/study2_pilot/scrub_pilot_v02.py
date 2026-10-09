"""Study 2 scrubbing pilot v0.2 (SCRUB_PILOT_SPEC_v0.2.md): the edit component with float32 editor passes, budgets
2/5/10% and 5% rounds, on v0.1's tuning texts. Reuses v0.1's runner helpers and data (bars, refs, original gradients).

Phases:
  validate  inputs only: v0.1 inputs and hashes; the float32 editor on 2 unwatermarked texts outside the pilot set
            (finite differences vs float32 autograd, edit counts, hooks); timing and peak memory
  run       edits (3 arms, float32 editor) and check I1, then scoring (bfloat16 S4, as Study 3); checkpointed.
            Refuses unless the spec is FIXED and committed.
  analyse   results.json (spec §3-4)
Run: .venv/bin/python research/study2_pilot/scrub_pilot_v02.py --phase validate|run|analyse
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scrub_core as SC  # noqa: E402
import scrub_pilot as P1  # noqa: E402  (v0.1: tuning sets, keys, stand-ins, helpers)
from scrub_core import PP, core  # noqa: E402

ROOT = SC.ROOT
SPEC = HERE / "SCRUB_PILOT_SPEC_v0.2.md"
D1 = P1.DATA                                   # v0.1 data
DATA = D1 / "v02"
OUT = ROOT / "research" / "outputs" / "study2_pilot_v0.2"
OUT1 = P1.OUT
BUDGETS = (0.02, 0.05, 0.10)
ROUND = 0.05                                   # v0.1 rule A2
ARMS = ("true", "est", "rand")
ALPHA = 0.01
I5_BUDGET_H = 30.0
STUDY = {"genuine": 3200, "null": 1000, "phi_genuine": 1600}
PROBE_S_PER_TEXT = 0.05
LEVELS = P1.LEVELS
TUNING = P1.TUNING
SEED_RAND_EDIT = 20261011                      # v0.2's E-rand stream (v0.1 used 20261001)
SEED_SMOKE = 20261013
jload, jsave, now, sha = P1.jload, P1.jsave, P1.now, P1.sha


def inputs():
    return {"bars": D1 / "bars.json", "refs": D1 / "refs.npz", "G_orig_wm": D1 / "G_orig_wm.npy",
            "v01_results": OUT1 / "results.json", "para_qwen_P2": D1 / "para_qwen_P2.json",
            "para_phi_P2": D1 / "para_phi_P2.json", "para_qwen": D1 / "para_qwen.json", "para_phi": D1 / "para_phi.json",
            "v01_score_rates": D1 / "score_rates.json"}


def footprint_peak_gb():
    r = subprocess.run(["footprint", str(os.getpid())], capture_output=True, text=True).stdout
    for line in r.splitlines():
        if "phys_footprint_peak:" in line:
            v = line.split(":")[1].strip()
            num, unit = v.split()
            return float(num) / (1024 if unit == "MB" else 1)
    return float("nan")


def spec_guard():
    if "**Status:** FIXED" not in SPEC.read_text():
        sys.exit("refused: the spec is not marked FIXED (Yichen's approval comes first)")
    code = [SPEC, Path(__file__), HERE / "scrub_core.py", HERE / "scrub_pilot.py"]
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + [str(p) for p in code], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        sys.exit(f"refused: uncommitted changes in the spec or the code:\n{dirty}")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"commit": commit, "sha256": {p.name: sha(p) for p in code},
            "inputs_sha256": {k: sha(p) for k, p in inputs().items()}, "utc": now()}


# ---------------------------------------------------------------- run
def step_edits(wm, arm):
    f = DATA / f"edits_{arm}.json"
    if f.exists():
        return jload(f)
    sd = np.load(D1 / "refs.npz")["att_sd14"]
    SC.free()
    tok, m32 = SC.load_base_fp32()
    ed = SC.Editor(tok, m32)
    rng = np.random.default_rng(SEED_RAND_EDIT) if arm == "rand" else None
    recs, t0, n = [None] * len(wm), time.time(), 0
    for s in TUNING:
        for rho in LEVELS:
            idx = [i for i, x in enumerate(wm) if x["key"] == s and x["rho"] == rho]
            texts = [wm[i]["text"] for i in idx]
            if arm == "rand":
                out = ed.run(texts, "random", rng=rng, round_frac=ROUND, budgets=BUDGETS)
            else:
                v = P1.tuning_key(s, rho) if arm == "true" else P1.standin(s)
                out = ed.run(texts, "guided", direction=v / sd, layer=SC.LAYER, round_frac=ROUND, budgets=BUDGETS)
            for i, r in zip(idx, out):
                recs[i] = r
            n += len(idx)
            print(f"  v02 edits {arm}: key {s} rho {rho} done ({n} texts, {now()})", flush=True)
    res = {"arm": arm, "recs": recs, "edit_s": time.time() - t0, "n_texts": n, "peak_gb": footprint_peak_gb()}
    if arm == "true":                                           # check I1 needs the float32 editor
        idx = [i for i, x in enumerate(wm) if x["key"] == 9001 and x["rho"] == 0.50]
        v = P1.tuning_key(9001, 0.50)
        wh = (v / sd) / np.linalg.norm(v / sd)
        G = np.load(D1 / "G_orig_wm.npy")[idx]
        rho_tok = []
        from scipy.stats import spearmanr
        for i in idx[:10]:
            ids = tok(wm[i]["text"], add_special_tokens=False)["input_ids"][:SC.NEW_TOKENS]
            w = torch.tensor(wh, dtype=torch.float32)
            c = {}
            for sf in (SC.S_FD, SC.S_FD / 2):
                H = ed._passes([ids, ids], [sf * w, -sf * w], SC.LAYER)
                c[sf] = ((ed._gather(H[0], ids)[0] - ed._gather(H[1], ids)[0]) / (2 * sf)).cpu().numpy()
            rho_tok.append(float(spearmanr(c[SC.S_FD], c[SC.S_FD / 2]).statistic))
        auto = (G @ wh).tolist()
        fd = [recs[i]["obj"]["0"] for i in idx]
        res["check_I1"] = {"autograd": auto, "finite_difference": fd, "r": float(np.corrcoef(auto, fd)[0, 1]),
                           "slope_fd_on_auto": float(np.polyfit(auto, fd, 1)[0]),
                           "per_token_spearman_s_vs_half_s": rho_tok}
    jsave(f, res)
    del ed, m32, tok
    SC.free()
    return res


def step_score(wm, edits):
    SC.free()
    tok, model = SC.load_base()
    E = SC.Embedder()
    t_s4 = t_q = 0.0
    n_s4 = 0
    for arm in ARMS:
        for f in BUDGETS:
            fg, fq = DATA / f"G_edit_{arm}_{f}.npy", DATA / f"Q_edit_{arm}_{f}.json"
            if fg.exists() and fq.exists():
                continue
            texts = [r["texts"][str(f)] for r in edits[arm]["recs"]]
            t0 = time.time()
            np.save(fg, SC.Owner.grads(tok, model, texts))
            t_s4 += time.time() - t0
            t0 = time.time()
            q = SC.raw_quality(tok, model, E, [x["prompt"] for x in wm], texts, [x["text"] for x in wm])
            t_q += time.time() - t0
            jsave(fq, {k: np.asarray(v).tolist() for k, v in q.items()})
            n_s4 += len(texts)
            print(f"  v02 scored edit_{arm}_{f}: {len(texts)} texts ({now()})", flush=True)
    if n_s4:
        jsave(DATA / "score_rates.json", {"s4_s_per_text": t_s4 / n_s4, "quality_s_per_text": t_q / n_s4})
    del model, E, tok
    SC.free()


def run():
    guard = spec_guard()
    DATA.mkdir(parents=True, exist_ok=True)
    jsave(DATA / "pilot_guard.json", guard)
    wm, _ = P1.tuning_sets()
    print(f"v02 run start {now()}: {len(wm)} watermarked tuning texts", flush=True)
    edits = {arm: step_edits(wm, arm) for arm in ARMS}
    step_score(wm, edits)
    print("v02 run complete", now(), flush=True)


# ---------------------------------------------------------------- analysis
def analyse():
    guard = spec_guard()
    wm, _ = P1.tuning_sets()
    bars = jload(D1 / "bars.json")
    refs = np.load(D1 / "refs.npz")
    owner = SC.Owner.__new__(SC.Owner)
    owner.ref = {"mu_g": refs["owner_mu"], "sd_g": refs["owner_sd"]}
    owner.nm = PP.null_matrix()
    orig = {q: np.asarray(v) for q, v in bars["orig"]["wm"].items()}
    keys = np.stack([SC.unit(P1.tuning_key(x["key"], 1.0)) for x in wm])
    X0 = owner.x(np.load(D1 / "G_orig_wm.npy"))
    p0 = PP.pvalues((X0 * keys).sum(1), X0 @ owner.nm.T)
    edits = {arm: jload(DATA / f"edits_{arm}.json") for arm in ARMS}
    v01 = jload(OUT1 / "results.json")

    def pkm(vals, rho):
        per = {str(s): float(np.mean([v for v, x in zip(vals, wm) if x["key"] == s and x["rho"] == rho]) * 100)
               for s in TUNING}
        return {"per_key": per, "median": float(np.median(list(per.values())))}

    res = {"guard": guard, "spec_sha256": sha(SPEC), "methods": {}, "edits": {}, "v01_bf16_same_budgets": {}}
    stats = {}
    for arm in ARMS:
        for f in BUDGETS:
            name = f"E-{arm} {int(round(f * 100))}%"
            X = owner.x(np.load(DATA / f"G_edit_{arm}_{f}.npy"))
            T = (X * keys).sum(1)
            p = PP.pvalues(T, X @ owner.nm.T)
            zq = {k: np.asarray(v) for k, v in jload(DATA / f"Q_edit_{arm}_{f}.json").items()}
            c = SC.conditions(orig, zq, bars["A"])
            succ = (p > ALPHA) & c["all"]
            alt = {b: (p > ALPHA) & SC.conditions(orig, zq, bars[b])["all"] for b in ("A_model_p95", "A_human_median")}
            stats[name] = {"T": T, "p": p}
            res["methods"][name] = {}
            for rho in LEVELS:
                sel = [i for i, x in enumerate(wm) if x["rho"] == rho]
                res["methods"][name][str(rho)] = {
                    "detected_before": pkm(p0 <= ALPHA, rho), "detected_after": pkm(p <= ALPHA, rho),
                    "success": pkm(succ, rho),
                    "success_stricter_bars": {b: pkm(v, rho)["median"] for b, v in alt.items()},
                    "pass": {k: pkm(c[k], rho) for k in ("ppl", "rep", "len", "cos", "all")},
                    "median_len_ratio": float(np.median(zq["len"][sel] / np.minimum(orig["len"][sel], SC.NEW_TOKENS))),
                    "median_ppl_ratio": float(np.median(zq["ppl"][sel] / orig["ppl"][sel])),
                    "median_cos": float(np.median(zq["cos"][sel])),
                    "keys_success_ge_50": int(sum(v >= 50 for v in pkm(succ, rho)["per_key"].values()))}
            if name in v01["methods"]:
                res["v01_bf16_same_budgets"][name] = {str(rho): {"success": v01["methods"][name][str(rho)]["success"]["median"],
                                                                 "detected_after": v01["methods"][name][str(rho)]["detected_after"]["median"]}
                                                      for rho in LEVELS}
        recs = edits[arm]["recs"]
        res["edits"][arm] = {"edit_s_per_text": edits[arm]["edit_s"] / edits[arm]["n_texts"],
                             "peak_gb": edits[arm]["peak_gb"],
                             "stalled": int(sum(r["stalled_at"] is not None for r in recs)),
                             "n_diff_exact": all(r["n_diff"][str(f)] == math.ceil(f * r["T"]) or r["stalled_at"] is not None
                                                 for r in recs for f in BUDGETS),
                             "median_drift": {str(f): float(np.median([r["drift"][str(f)] for r in recs])) for f in BUDGETS}}
        if arm != "rand":
            res["edits"][arm]["median_objective"] = {k: float(np.median([r["obj"][k] for r in recs]))
                                                     for k in ["0"] + [str(f) for f in BUDGETS]}
    from scipy.stats import wilcoxon
    T0 = (X0 * keys).sum(1)
    d_true, d_rand = stats["E-true 5%"]["T"] - T0, stats["E-rand 5%"]["T"] - T0
    w = wilcoxon(d_true, d_rand, alternative="less")
    i1 = edits["true"]["check_I1"]
    drift_ok = all(v <= 0.02 for a in res["edits"] for v in res["edits"][a]["median_drift"].values())
    checks = {"I1": {"pass": bool(i1["r"] >= 0.99 and np.median(i1["per_token_spearman_s_vs_half_s"]) >= 0.8),
                     "r": i1["r"], "slope": i1["slope_fd_on_auto"],
                     "per_token_spearman_median": float(np.median(i1["per_token_spearman_s_vs_half_s"]))},
              "I2": {"pass": bool(w.pvalue < 0.01 and np.median(d_true) < 0), "wilcoxon_p": float(w.pvalue),
                     "median_change_true": float(np.median(d_true)), "median_change_rand": float(np.median(d_rand))},
              "I3": {"pass": bool(all(res["edits"][a]["n_diff_exact"] for a in ARMS) and drift_ok),
                     "n_diff_exact": {a: res["edits"][a]["n_diff_exact"] for a in ARMS}, "median_drift_le_2pct": drift_ok,
                     "hook_removed": "VALIDATION.json"}}
    # I5': Study 2 under the revised scope
    rates1 = jload(D1 / "score_rates.json")
    rates2 = jload(DATA / "score_rates.json")
    proj, first_share = {}, {}
    for m, n_orig in (("qwen", STUDY["genuine"] + STUDY["null"]), ("phi", STUDY["phi_genuine"] + STUDY["null"])):
        P = jload(D1 / f"para_{m}.json")
        n_att = sum(1 for a in range(SC.MAX_ATTEMPTS) for S in ("wm", "van") for r in P[S]["attempts"][a] if r)
        per_attempt = (P["wm"]["paraphrase_s"] + P["van"]["paraphrase_s"]) / n_att
        P2 = jload(D1 / f"para_{m}_P2.json")["wm"]
        factor = sum(1 for a in range(SC.MAX_ATTEMPTS) for r in P2["attempts"][a] if r) / len(P2["kept"])
        first_share[m] = float(np.mean([k > 0 for k in P2["kept"]]))
        proj[f"paraphrase_{m}_h"] = factor * (per_attempt + rates1["quality_s_per_text"]) * n_orig / 3600
        proj[f"{m}_attempts_per_original_P2"] = factor
    for arm in ARMS:
        proj[f"edits_{arm}_h"] = res["edits"][arm]["edit_s_per_text"] * STUDY["genuine"] / 3600
    n_para = (STUDY["genuine"] + STUDY["null"]) + (STUDY["phi_genuine"] + STUDY["null"])
    n_first = (STUDY["genuine"] + STUDY["null"]) * first_share["qwen"] + (STUDY["phi_genuine"] + STUDY["null"]) * first_share["phi"]
    n_full = n_para + 3 * len(BUDGETS) * STUDY["genuine"] + STUDY["genuine"]
    full = rates2["s4_s_per_text"] + rates2["quality_s_per_text"]
    proj["scoring_h"] = (n_full * (full + PROBE_S_PER_TEXT) + n_first * full
                         + (STUDY["genuine"] + STUDY["phi_genuine"]) * rates2["s4_s_per_text"]) / 3600
    proj["estimate_layer_scales_h"] = 16 * P1.N_REF_C * rates2["s4_s_per_text"] / 3600
    proj["total_h"] = float(sum(v for k, v in proj.items() if k.endswith("_h")))
    checks["I5prime"] = {"pass": proj["total_h"] <= I5_BUDGET_H, "projection": proj, "budget_h": I5_BUDGET_H}
    res["checks"] = checks
    res["samples"] = []
    for s in (9001, 9002):
        i = next(i for i, x in enumerate(wm) if x["key"] == s and x["rho"] == 0.50 and x["j"] == 0)
        smp = {"key": s, "original": wm[i]["text"], "p_original": float(p0[i])}
        for arm in ARMS:
            for f in (0.05, 0.10):
                name = f"E-{arm} {int(round(f * 100))}%"
                smp[name] = edits[arm]["recs"][i]["texts"][str(f)]
                smp["p_" + name] = float(stats[name]["p"][i])
        res["samples"].append(smp)
    res["all_checks_pass"] = all(c["pass"] for c in checks.values())
    OUT.mkdir(parents=True, exist_ok=True)
    jsave(OUT / "results.json", res)
    print(json.dumps({"checks": {k: v["pass"] for k, v in checks.items()}, "I1": checks["I1"],
                      "projection_h": proj["total_h"]}, indent=1))


# ---------------------------------------------------------------- validation (inputs only)
def validate():
    OUT.mkdir(parents=True, exist_ok=True)
    checks, t_start = {}, time.time()
    f = inputs()
    missing = [k for k, p in f.items() if not p.exists()]
    wm, _ = P1.tuning_sets()
    G = np.load(f["G_orig_wm"]) if not missing else None
    checks["1_inputs"] = {"pass": bool(not missing and len(wm) == 400 and G.shape == (400, SC.D)),
                          "missing": missing, "sha256": {k: sha(p) for k, p in f.items() if p.exists()}}
    smoke = jload(P1.CAL / "texts_van_k9001.json")[P1.PER:P1.PER + 2]
    tok, m32 = SC.load_base_fp32()
    ed = SC.Editor(tok, m32)
    rng = np.random.default_rng(SEED_SMOKE)
    fd, au = [], []
    for t in smoke:
        enc = core._encode(tok, [t]).to(SC.dev())
        cm = enc.pop("content_mask")
        b = torch.zeros(1, 1, SC.D, device=SC.dev(), dtype=torch.float32, requires_grad=True)
        hd = m32.model.layers[SC.LAYER].register_forward_hook(PP._hook(b))
        try:
            ll = PP._loglik(m32, enc, cm)
            ll.backward()
        finally:
            hd.remove()
        g = b.grad[0, 0].detach().cpu().numpy().astype(np.float64)
        ids = tok(t, add_special_tokens=False)["input_ids"][:SC.NEW_TOKENS]
        for _ in range(8):
            u = rng.normal(size=SC.D)
            u /= np.linalg.norm(u)
            w = torch.tensor(u, dtype=torch.float32)
            H = ed._passes([ids, ids], [SC.S_FD * w, -SC.S_FD * w], SC.LAYER)
            fd.append(float(((ed._gather(H[0], ids)[0] - ed._gather(H[1], ids)[0]) / (2 * SC.S_FD)).sum()))
            au.append(float(g @ u))
    r_fd = float(np.corrcoef(fd, au)[0, 1])
    enc = core._encode(tok, [smoke[1]]).to(SC.dev())
    enc.pop("content_mask")
    with torch.no_grad():
        before = m32(**enc).logits.float().cpu()
    dirn = core.make_key(SEED_SMOKE, SC.D, 1.0).numpy().astype(np.float64)
    t0 = time.time()
    rg = ed.run(smoke, "guided", direction=dirn, layer=SC.LAYER, round_frac=ROUND, budgets=BUDGETS)
    tg = (time.time() - t0) / 2
    t0 = time.time()
    rr = ed.run(smoke, "random", rng=rng, round_frac=ROUND, budgets=BUDGETS)
    tr = (time.time() - t0) / 2
    with torch.no_grad():
        after = m32(**enc).logits.float().cpu()
    hook = float((before - after).abs().max())
    exact = all(r["n_diff"][str(b_)] == math.ceil(b_ * r["T"]) for r in rg + rr for b_ in BUDGETS if r["stalled_at"] is None)
    peak = footprint_peak_gb()
    checks["2_float32_editor"] = {"pass": bool(r_fd >= 0.999 and hook == 0.0 and exact), "r_fd_vs_fp32_autograd": r_fd,
                                  "n_pairs": len(fd), "hook_max_abs_logit_diff": hook, "n_diff_exact": exact,
                                  "note": "unwatermarked texts outside the pilot set; random directions"}
    proj = (400 * (2 * tg + tr) + 3600 * 0.36) / 3600
    checks["3_timing_memory"] = {"pass": bool(peak <= 10.0 and proj <= 2.0), "guided_s_per_text": tg,
                                 "random_s_per_text": tr, "peak_gb": peak, "projected_pilot_h": proj}
    res = {"spec": SPEC.name, "spec_sha256": sha(SPEC), "date_utc": now(), "checks": checks,
           "all_pass": all(c["pass"] for c in checks.values()), "elapsed_s": time.time() - t_start,
           "note": "inputs only: no tuning-key watermarked text was edited or scored"}
    jsave(OUT / "VALIDATION.json", res)
    for k, c in checks.items():
        print(k, "PASS" if c["pass"] else "FAIL", {x: y for x, y in c.items() if x != "sha256"})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["validate", "run", "analyse"], required=True)
    {"validate": validate, "run": run, "analyse": analyse}[ap.parse_args().phase]()
