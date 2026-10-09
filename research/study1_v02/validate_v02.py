"""Input validation for Study 1 v0.2 (protocol §12). Inputs only: no study key is used with the model, and no detector
or attack statistic is computed on watermarked model outputs. Synthetic data test the statistics; a validation-only
key (seed 0) is used for the hook, feature and timing checks.
Run: .venv/bin/python research/study1_v02/validate_v02.py  ->  research/outputs/study1_v0.2/INPUT_VALIDATION.json
"""
import inspect
import json
import time

import numpy as np
import torch

import common as C  # first: puts research/study1 on sys.path
import attack2  # noqa: E402
import detect2
import run_v02
from common import core

OUT = C.ROOT / "research" / "outputs" / "study1_v0.2"
BUDGET_H = 30.0
checks = {}


def check(name, ok, **info):
    checks[name] = {"pass": bool(ok), **info}
    print(("PASS " if ok else "FAIL ") + name, info if info else "", flush=True)


def main():
    assert not (C.HERE / "data").exists(), "Study 1 v0.2 data already exist: validation must precede any run"
    # ---- pools and keys
    P = C.pools()
    check("pools_sizes_disjoint_dev_only", True, sizes={k: len(v) for k, v in P.items()})
    try:
        core.load_prompts("c4", "holdout")
        check("holdout_sealed", False)
    except Exception as e:
        check("holdout_sealed", True, error=type(e).__name__)
    ks = set(C.STUDY_KEYS)
    check("keys_disjoint", not (ks & set(C.CONTROL_KEYS)) and not (ks & set(core.TUNING_KEY_SEEDS))
          and core.VALIDATION_KEY_SEED not in ks | set(C.CONTROL_KEYS))
    norms = [float(C.key(s, r).norm()) / (r * C.N_REF) for s in C.STUDY_KEYS[:2] for r in C.LEVELS]
    nnz = {int((C.key(s, 0.5) != 0).sum()) for s in C.STUDY_KEYS}
    check("key_norms_and_support", np.allclose(norms, 1.0, atol=1e-5) and nnz == {C.K_SUPPORT}, nnz=sorted(nnz))
    pilot_N = json.loads(C.PILOT_RESULTS.read_text())["meta"]["act_norm_median_unsteered"]
    check("N_matches_pilot", abs(pilot_N - C.N_REF) < 1e-9, N=pilot_N)

    # ---- detector on synthetic data (planted signal / none), threshold rule
    rng = np.random.default_rng(0)
    dev = core.device()
    d, T = 64, 64

    def synth(n, shift):
        X = rng.normal(size=(n, T, d)).astype(np.float16)
        X[:, :, 5] += shift
        return X, np.full(n, T)

    for shift, label in ((1.0, "planted"), (0.0, "none")):
        net = detect2.train(*synth(200, shift), *synth(200, 0.0), dev)
        sA = detect2.score(net, *synth(1000, 0.0), dev)
        thr = detect2.threshold(sA[:500])
        fpr = detect2.accept(sA[500:], thr).mean()
        tpr = detect2.accept(detect2.score(net, *synth(200, shift), dev), thr).mean()
        ok = (tpr > 0.9 if shift else tpr < 0.05) and 0.0 <= fpr <= 0.03
        check(f"detector_synthetic_{label}", ok, tpr=float(tpr), fpr_A2=float(fpr))
    z = rng.normal(size=200000)
    fprs = [detect2.accept(rng.normal(size=500), detect2.threshold(rng.normal(size=500))).mean() for _ in range(400)]
    check("threshold_rule_fpr", 0.007 <= np.mean(fprs) <= 0.014, mean_fpr=float(np.mean(fprs)))
    del z

    # ---- attack isolation and planted-signal recovery (synthetic features)
    src = inspect.getsource(attack2)
    banned = ("import core", "import common", "import detect2", "import torch", "make_key", "LAYER")
    check("attack_isolation", not any(b in src for b in banned) and
          list(inspect.signature(attack2.route_a).parameters) == ["obs", "ref", "k", "rho", "ref_norms"] and
          list(inspect.signature(attack2.route_b).parameters) == ["obs", "ref", "rho", "ref_norms"])
    L, dd = 6, 64
    ref = rng.normal(size=(2000, L, dd)) * 0.01
    v = np.zeros(dd)
    v[[3, 17, 40, 55]] = [1, -1, 0.5, -0.8]
    obs = rng.normal(size=(256, L, dd)) * 0.01
    obs[:, 4] += 0.01 * v  # z about 15 on the support (a clear planted signal)
    la, va, _ = attack2.route_a(obs, ref, 4, 0.5, np.full(L, 10.0))
    lb, vb, _ = attack2.route_b(obs, ref, 0.5, np.full(L, 10.0))
    cos = lambda x: float(x @ v / np.linalg.norm(x) / np.linalg.norm(v))  # noqa: E731
    check("attack_planted_recovery", la == 4 and lb == 4 and cos(va) > 0.9 and cos(vb) > 0.5
          and abs(np.linalg.norm(va) - 5.0) < 1e-3, route_a_cos=cos(va), route_b_cos=cos(vb))

    # ---- lock enforcement (no lock yet -> refuse)
    try:
        run_v02.check_lock()
        check("runner_refuses_without_lock", False)
    except (FileNotFoundError, AssertionError) as e:
        check("runner_refuses_without_lock", True, error=type(e).__name__)

    # ---- model: hooks, feature equivalence, timing (validation key only)
    tok, model = core.load_model()
    vk = C.key(core.VALIDATION_KEY_SEED, 0.5)
    enc = tok(["The weather today is"], return_tensors="pt").to(dev)
    with torch.no_grad():
        base = model(**enc).logits[0, -1].float()
        h = model.model.layers[C.LAYER].register_forward_hook(core.AddVector(vk.to(dev, model.dtype)))
        steered = model(**enc).logits[0, -1].float()
        h.remove()
        again = model(**enc).logits[0, -1].float()
    check("hook_changes_and_restores", float((steered - base).abs().max()) > 1e-3 and float((again - base).abs().max()) == 0.0)
    pD = C.prompts(P["D"])[:16]
    t = time.time()
    texts = core.generate(tok, model, pD, key=vk, layer=C.LAYER, seed=0)
    t_gen = (time.time() - t) / 16
    t = time.time()
    X, lens = C.layer_tokens(tok, model, texts)
    t_tok = (time.time() - t) / 16
    t = time.time()
    F = C.all_layer_means(tok, model, texts)
    t_all = (time.time() - t) / 16
    ref_f = core.reencode_features(tok, model, texts[:4])
    check("features_match_v01_reencode", np.abs(F[:4].astype(np.float32) - ref_f.astype(np.float32)).max() < 2e-3
          and X.shape == (16, core.NEW_TOKENS, C.D_MODEL) and lens.min() == core.NEW_TOKENS)
    t = time.time()
    C.perplexities(tok, model, pD[:8], texts[:8])
    t_ppl = (time.time() - t) / 8
    t = time.time()
    Xs = np.random.default_rng(1).normal(size=(200, core.NEW_TOKENS, C.D_MODEL)).astype(np.float16)
    ls = np.full(200, core.NEW_TOKENS)
    net = detect2.train(Xs, ls, Xs, ls, dev)
    t_train = time.time() - t
    t = time.time()
    detect2.score(net, Xs, ls, dev)
    t_score = (time.time() - t) / 200
    del model
    n_kl = len(C.STUDY_KEYS) * len(C.LEVELS)
    gens = 3200 + n_kl * (1024 + 200 + 100 + 100 + 2 * len(C.FORGE_N) * C.N_FORGE_TEXTS)
    per_kl_other = (1024 * t_all + 200 * t_tok + 800 * (t_tok + t_ppl) + t_train + (1500 + 800) * t_score)
    shared = 1700 * t_tok + 2000 * t_all
    hours = (gens * t_gen + n_kl * per_kl_other + shared) / 3600
    check("timing_budget", hours <= BUDGET_H, projected_hours=round(hours, 1), s_per_gen=round(t_gen, 3),
          s_per_tokens=round(t_tok, 3), s_per_all_layers=round(t_all, 3), s_per_ppl=round(t_ppl, 3),
          s_train=round(t_train, 1), s_per_score=round(t_score, 4), generations=gens)
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"all_pass": all(c["pass"] for c in checks.values()), "checks": checks,
               "note": "inputs only; no study key used with the model; no statistic on watermarked outputs",
               "code_sha256": {p.name: run_v02.sha(p) for p in run_v02.CODE}}
    (OUT / "INPUT_VALIDATION.json").write_text(json.dumps(summary, indent=2))
    print("ALL PASS" if summary["all_pass"] else "SOME CHECKS FAILED", flush=True)


if __name__ == "__main__":
    main()
