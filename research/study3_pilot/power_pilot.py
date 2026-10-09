"""Study 3 power pilot v0.1 (POWER_PILOT_SPEC_v0.1.md): four key-specific statistics under an exact key-resampling
test, on the tuning keys only.

Phases:
  validate  inputs only (pool F texts, synthetic data); no statistic on watermarked texts
  features  per-text activation mean `a` and gradient `g` at layer 14 (refuses unless the spec is fixed and committed)
  stats     p-values, TPRs, the selection rule and the descriptive outputs -> outputs/study3_pilot_v0.1/results.json
Run: .venv/bin/python research/study3_pilot/power_pilot.py --phase validate|features|stats
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
sys.path.insert(0, str(ROOT / "research" / "study1"))
import core  # noqa: E402  (Study 1 v0.1 machinery, unchanged: keys, null keys, encoding, model loading)

SPEC = HERE / "POWER_PILOT_SPEC_v0.1.md"
DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study3_pilot_v0.1"
CAL = ROOT / "research" / "repro" / "data" / "qwen"
F_TEXTS = ROOT / "research" / "study1_v02" / "data" / "S_F_van.json"

N_REF = 56.90270233154297          # median unsteered norm at layer 14 (calibration and Study 1 v0.2)
LAYER = 14
D = 1536
TUNING = [9001, 9002, 9003, 9004]
LEVELS = [0.25, 0.35, 0.50, 0.70]
WORKING = [0.35, 0.50, 0.70]
PER_KEY = 100
ALPHA = 0.01
CANDS = ["S1", "S2", "S3", "S4"]
TIE_ORDER = ["S3", "S4", "S2", "S1"]
TIE_PTS = 2.0
USABLE_PCT = 20.0
FPR_RANGE = (0.3, 2.5)
POOL_N = [4, 16]
OTHER_SEEDS = {0} | set(range(1001, 1017)) | set(range(5001, 5017)) | set(TUNING)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tag(rho):
    return f"r{int(round(rho * 100)):03d}"


def input_files():
    files = {"F": F_TEXTS}
    for s in TUNING:
        files[f"van_k{s}"] = CAL / f"texts_van_k{s}.json"
        for rho in LEVELS:
            files[f"{tag(rho)}_k{s}"] = CAL / f"texts_calib_{tag(rho)}_k{s}.json"
    return files


# ---------------------------------------------------------------- keys and p-values
def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def tuning_key(s, rho):
    v = core.make_key(s, D, 1.0)
    return (v * (rho * N_REF / v.norm())).numpy()


def null_matrix():
    """The M = 999 public null keys (core.null_keys, seeds 77,700,000 + j), unit norm, float64 [999, d]."""
    return unit(core.null_keys(D, 1.0).numpy().astype(np.float64))


def pvalues(T_true, T_null):
    """Exact key-resampling p-values: (1 + #{j: T_j >= T}) / (1 + M). T_true [n], T_null [n, M]."""
    return (1 + (T_null >= T_true[:, None]).sum(1)) / (1 + T_null.shape[1])


def transform(c, A, G, ref):
    """Candidate c's per-text vector x, unit-normalised (so that T = <x, v/||v||>)."""
    if c == "S1":
        X = A
    elif c == "S2":
        X = (A - ref["mu_a"]) / ref["sd_a"]
    elif c == "S3":
        X = G
    else:
        X = (G - ref["mu_g"]) / ref["sd_g"]
    return unit(X.astype(np.float64))


# ---------------------------------------------------------------- model passes
def load():
    tok, model = core.load_model()
    for p in model.parameters():
        p.requires_grad_(False)  # only the additive vector b needs a gradient
    return tok, model


def _hook(b, cap=None):
    def fn(module, inputs, output):
        h = output[0] if isinstance(output, tuple) else output
        if cap is not None:
            cap["h"] = h.detach()
        h2 = h + b.to(h.dtype)
        return (h2,) + tuple(output[1:]) if isinstance(output, tuple) else h2
    return fn


def _loglik(model, enc, cm):
    hs = model.model(**enc).last_hidden_state
    logits = model.lm_head(hs[:, :-1]).float()
    lp = torch.log_softmax(logits, -1).gather(2, enc["input_ids"][:, 1:].unsqueeze(-1)).squeeze(-1)
    return (lp * cm[:, 1:].to(lp.device).float()).sum()


def text_features(tok, model, text):
    """One forward and one backward pass (batch 1, continuation only, as core._encode): returns
    a = mean_t h_t/||h_t|| at the output of decoder layer 14, g = d loglik / d b at b = 0 (b added there), loglik."""
    dev = core.device()
    enc = core._encode(tok, [text]).to(dev)
    cm = enc.pop("content_mask")
    b = torch.zeros(1, 1, D, device=dev, dtype=torch.float32, requires_grad=True)
    cap = {}
    hd = model.model.layers[LAYER].register_forward_hook(_hook(b, cap))
    try:
        ll = _loglik(model, enc, cm)
        ll.backward()
    finally:
        hd.remove()
    g = b.grad[0, 0].detach().float().cpu().numpy()
    m = cm[0].to(dev).bool()
    h = cap["h"][0].float()[m]
    a = (h / h.norm(dim=-1, keepdim=True).clamp_min(1e-6)).mean(0).cpu().numpy()
    torch.mps.empty_cache()
    return a.astype(np.float32), g.astype(np.float32), float(ll.detach())


def loglik_with_bias(tok, model, text, bias):
    dev = core.device()
    enc = core._encode(tok, [text]).to(dev)
    cm = enc.pop("content_mask")
    b = torch.as_tensor(bias, dtype=torch.float32, device=dev).view(1, 1, D)
    hd = model.model.layers[LAYER].register_forward_hook(_hook(b))
    try:
        with torch.no_grad():
            return float(_loglik(model, enc, cm))
    finally:
        hd.remove()


# ---------------------------------------------------------------- validation (inputs only)
def validate():
    OUT.mkdir(parents=True, exist_ok=True)
    checks, t_start = {}, time.time()
    files = input_files()
    missing = [k for k, p in files.items() if not p.exists()]
    counts = {k: len(json.loads(p.read_text())) for k, p in files.items() if p.exists()}
    ok = not missing and counts["F"] == 200 and all(counts[k] == PER_KEY for k in counts if k != "F")
    checks["1_inputs"] = {"pass": ok, "missing": missing, "n_files": len(files),
                          "sha256": {k: sha(p) for k, p in files.items() if p.exists()}}

    norms_ok = all(abs(np.linalg.norm(tuning_key(s, r)) - r * N_REF) < 1e-3 and
                   int((tuning_key(s, r) != 0).sum()) == core.n_support(D) for s in TUNING for r in LEVELS)
    null_seeds = [core.NULL_KEY_SEED * 100000 + j for j in range(core.N_NULL_KEYS)]
    nm = null_matrix()
    nz_ok = all(int((row != 0).sum()) == core.n_support(D) for row in nm)
    tk = np.stack([unit(tuning_key(s, 1.0).astype(np.float64)) for s in TUNING])
    no_dup = float(np.max(np.abs(tk @ nm.T))) < 1 - 1e-9
    checks["2_keys"] = {"pass": bool(norms_ok and nz_ok and no_dup and not (set(null_seeds) & OTHER_SEEDS)
                                     and nm.shape == (999, D)),
                        "null_seed_range": [min(null_seeds), max(null_seeds)], "M": int(nm.shape[0]),
                        "max_abs_cos_tuning_vs_null": float(np.max(np.abs(tk @ nm.T)))}

    # 3. p-values on synthetic Gaussian data with heterogeneous coordinate scales (mimicking outlier dimensions)
    from scipy.stats import kstest
    rng = np.random.default_rng(20260930)
    scales = np.exp(rng.normal(0, 1.5, D))
    n_sim = 10000
    true = unit(np.stack([core.make_key(88_800_000 + i, D, 1.0).numpy() for i in range(n_sim)]).astype(np.float64))
    X0 = unit(rng.normal(size=(n_sim, D)) * scales)
    p0 = pvalues((X0 * true).sum(1), X0 @ nm.T)
    ks = kstest(p0, "uniform")
    grid_ok = bool(np.allclose(p0 * 1000, np.round(p0 * 1000)))
    X1 = rng.normal(size=(1000, D)) + 5.0 * true[:1000]
    X1 = unit(X1)
    p1 = pvalues((X1 * true[:1000]).sum(1), X1 @ nm.T)
    checks["3_pvalues_synthetic"] = {
        "pass": bool(ks.pvalue > 0.01 and grid_ok and (p1 <= ALPHA).mean() > 0.90),
        "ks_p": float(ks.pvalue), "null_rate_at_1pct": float((p0 <= ALPHA).mean()), "on_grid": grid_ok,
        "planted_detection": float((p1 <= ALPHA).mean())}

    # 4-6 need the model; pool F texts only
    tok, model = load()
    ftexts = json.loads(F_TEXTS.read_text())
    a, g, ll0 = text_features(tok, model, ftexts[0])
    gh = g / np.linalg.norm(g)
    fd, an = [], []
    eps = 0.5
    for k in range(8):
        r = rng.normal(size=D)
        r -= (r @ gh) * gh
        r /= np.linalg.norm(r)
        th = np.pi * k / 7
        u = np.cos(th) * gh + np.sin(th) * r
        fd.append((loglik_with_bias(tok, model, ftexts[0], eps * u) - loglik_with_bias(tok, model, ftexts[0], -eps * u))
                  / (2 * eps))
        an.append(float(g @ u))
    rr = float(np.corrcoef(fd, an)[0, 1])
    slope = float(np.polyfit(an, fd, 1)[0])
    checks["4_gradient_fd"] = {"pass": rr > 0.95, "r": rr, "slope_fd_on_analytic": slope, "eps": eps,
                               "grad_norm": float(np.linalg.norm(g)), "fd": fd, "analytic": an}

    dev = core.device()
    enc = core._encode(tok, [ftexts[1]]).to(dev)
    enc.pop("content_mask")
    with torch.no_grad():
        ref_logits = model(**enc).logits.float().cpu()
    text_features(tok, model, ftexts[2])
    with torch.no_grad():
        after = model(**enc).logits.float().cpu()
    diff = float((ref_logits - after).abs().max())
    checks["5_hook_removed"] = {"pass": diff == 0.0, "max_abs_logit_diff": diff}

    t0 = time.time()
    for t in ftexts[3:13]:
        text_features(tok, model, t)
    per = (time.time() - t0) / 10
    n_total = 200 + 400 + len(TUNING) * len(LEVELS) * PER_KEY
    proj_h = per * n_total / 3600
    checks["6_timing"] = {"pass": proj_h <= 1.0, "s_per_text": per, "n_texts": n_total, "projected_h": proj_h,
                          "budget_h": 1.0}

    res = {"spec": SPEC.name, "spec_sha256": sha(SPEC), "date_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
           "note": "inputs only: pool F texts and synthetic data; no statistic on any watermarked text",
           "checks": checks, "all_pass": all(c["pass"] for c in checks.values()),
           "elapsed_s": time.time() - t_start}
    (OUT / "VALIDATION.json").write_text(json.dumps(res, indent=2))
    for k, c in checks.items():
        print(k, "PASS" if c["pass"] else "FAIL", {x: y for x, y in c.items() if x not in ("sha256", "fd", "analytic")})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


# ---------------------------------------------------------------- guard: the spec must be fixed and committed
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


def features():
    guard = spec_guard()
    DATA.mkdir(parents=True, exist_ok=True)
    tok, model = load()
    t0 = time.time()
    for name, path in input_files().items():
        f = DATA / f"feats_{name}.npz"
        if f.exists():
            continue
        texts = json.loads(path.read_text())
        A, G, LL = zip(*(text_features(tok, model, t) for t in texts))
        np.savez(f, A=np.stack(A), G=np.stack(G), LL=np.array(LL), sha=sha(path))
        print(f"{name}: {len(texts)} texts, {time.time() - t0:.0f}s", flush=True)
    (DATA / "features_guard.json").write_text(json.dumps(guard, indent=2))


# ---------------------------------------------------------------- statistics
def auroc(pos, neg):
    from scipy.stats import mannwhitneyu
    return float(mannwhitneyu(pos, neg).statistic / (len(pos) * len(neg)))


def stats():
    guard = spec_guard()
    files = input_files()
    F = {k: np.load(DATA / f"feats_{k}.npz") for k in files}
    for k, p in files.items():
        assert str(F[k]["sha"]) == sha(p), f"input changed since features: {k}"
    ref = {"mu_a": F["F"]["A"].mean(0), "sd_a": np.maximum(F["F"]["A"].std(0, ddof=1), 1e-12),
           "mu_g": F["F"]["G"].mean(0), "sd_g": np.maximum(F["F"]["G"].std(0, ddof=1), 1e-12)}
    nm = null_matrix()
    keys = {s: unit(tuning_key(s, 1.0).astype(np.float64)) for s in TUNING}

    def stat(c, name):
        X = transform(c, F[name]["A"], F[name]["G"], ref)
        return X

    out = {"guard": guard, "M": int(nm.shape[0]), "alpha": ALPHA,
           "ref_scale_spread": {"sd_a_max_over_median": float(ref["sd_a"].max() / np.median(ref["sd_a"])),
                                "sd_g_max_over_median": float(ref["sd_g"].max() / np.median(ref["sd_g"]))},
           "fpr_check": {}, "tpr": {}, "score": {}, "auroc": {}, "cross_key": {}, "pooled": {}}
    for c in CANDS:
        Xv = {s: stat(c, f"van_k{s}") for s in TUNING}
        Xvan = np.concatenate([Xv[s] for s in TUNING])
        Nvan = Xvan @ nm.T
        det = [pvalues(Xvan @ keys[s], Nvan) <= ALPHA for s in TUNING]
        rate = 100 * float(np.mean(np.concatenate(det)))
        out["fpr_check"][c] = {"rate_pct": rate, "n_tests": int(sum(len(d) for d in det)),
                               "pass": FPR_RANGE[0] <= rate <= FPR_RANGE[1]}
        out["tpr"][c], out["auroc"][c], out["cross_key"][c] = {}, {}, {}
        out["pooled"][c] = {str(n): {"fpr_pct": None, "tpr": {}} for n in POOL_N}
        for rho in LEVELS:
            per, au, cross = {}, {}, []
            for s in TUNING:
                X = stat(c, f"{tag(rho)}_k{s}")
                NX = X @ nm.T
                per[str(s)] = 100 * float((pvalues(X @ keys[s], NX) <= ALPHA).mean())
                au[str(s)] = auroc(X @ keys[s], Xvan @ keys[s])
                cross += [pvalues(X @ keys[o], NX) <= ALPHA for o in TUNING if o != s]
            out["tpr"][c][str(rho)] = {"per_key": per, "median": float(np.median(list(per.values())))}
            out["auroc"][c][str(rho)] = {"per_key": au, "median": float(np.median(list(au.values())))}
            out["cross_key"][c][str(rho)] = {"rate_pct": 100 * float(np.mean(np.concatenate(cross))),
                                             "n_tests": int(sum(len(x) for x in cross))}
            for n in POOL_N:
                per_n = {}
                for s in TUNING:
                    X = stat(c, f"{tag(rho)}_k{s}")
                    nb = PER_KEY // n
                    Tt = (X[:nb * n] @ keys[s]).reshape(nb, n).sum(1)
                    Tn = (X[:nb * n] @ nm.T).reshape(nb, n, -1).sum(1)
                    per_n[str(s)] = 100 * float((pvalues(Tt, Tn) <= ALPHA).mean())
                out["pooled"][c][str(n)]["tpr"][str(rho)] = {"per_key": per_n,
                                                             "median": float(np.median(list(per_n.values()))),
                                                             "batches_per_key": PER_KEY // n}
        for n in POOL_N:
            d = []
            for s in TUNING:
                for o in TUNING:
                    X = Xv[s]
                    nb = PER_KEY // n
                    d.append(pvalues((X[:nb * n] @ keys[o]).reshape(nb, n).sum(1),
                                     (X[:nb * n] @ nm.T).reshape(nb, n, -1).sum(1)) <= ALPHA)
            out["pooled"][c][str(n)]["fpr_pct"] = 100 * float(np.mean(np.concatenate(d)))
        out["score"][c] = float(np.mean([out["tpr"][c][str(r)]["median"] for r in WORKING]))

    all_fpr_ok = all(v["pass"] for v in out["fpr_check"].values())
    top = max(out["score"].values())
    close = [c for c in CANDS if out["score"][c] >= top - TIE_PTS]
    primary = next(c for c in TIE_ORDER if c in close) if all_fpr_ok else None
    usable = [r for r in WORKING if primary and out["tpr"][primary][str(r)]["median"] >= USABLE_PCT]
    out["selection"] = {"implementation_check_pass": all_fpr_ok, "top_score": top, "within_tie_margin": close,
                        "primary": primary, "usable_levels": usable,
                        "viability": ("usable on single texts at " + ", ".join(map(str, usable))) if usable else
                        "not usable on single texts at any working level (pooled-test option goes to Yichen)"}
    out["timing_s_per_text"] = json.loads((OUT / "VALIDATION.json").read_text())["checks"]["6_timing"]["s_per_text"]
    (OUT / "results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"score": out["score"], "selection": out["selection"], "fpr_check": out["fpr_check"]}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["validate", "features", "stats"], required=True)
    ph = ap.parse_args().phase
    {"validate": validate, "features": features, "stats": stats}[ph]()
