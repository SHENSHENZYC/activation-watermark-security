"""Study 3 power pilot v0.1: diagnostics written AFTER the run (exploratory, labelled as such in the report).

Why: the pre-registered implementation check failed for S1 (0.00% FPR). This script asks whether that is a feature bug
or a property of the statistic.
(1) S1 on the calibration's own test split (repro_pilot's split) should reproduce calibration v0.1's cosine AUROC.
(2) Per-key (conditional) FPR on the 400 unwatermarked texts, over 1,000 fresh random keys (seeds 66,600,000 + i;
    disjoint from every other seed), against the same 999 null keys: key resampling is exact on average over keys,
    not necessarily for one fixed key.
Unwatermarked texts only in (2); no study key. Output: outputs/study3_pilot_v0.1/posthoc_diagnostics.json
Run: .venv/bin/python research/study3_pilot/posthoc_diag.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "repro"))
import power_pilot as pp  # noqa: E402
import repro_pilot as rp  # noqa: E402
import core  # noqa: E402

FRESH_SEED0, N_FRESH = 66_600_000, 1000


def main():
    F = {k: np.load(pp.DATA / f"feats_{k}.npz") for k in pp.input_files()}
    ref = {"mu_a": F["F"]["A"].mean(0), "sd_a": np.maximum(F["F"]["A"].std(0, ddof=1), 1e-12),
           "mu_g": F["F"]["G"].mean(0), "sd_g": np.maximum(F["F"]["G"].std(0, ddof=1), 1e-12)}
    nm = pp.null_matrix()
    out = {"note": "written and run after the pilot's outcomes were read; exploratory", "s1_calibration_split": {},
           "conditional_fpr": {}}
    perm = np.random.default_rng(rp.SPLIT_SEED).permutation(rp.PER_KEY)
    te = perm[rp.N_TRAIN + rp.N_VAL:]
    calib = json.loads((core.ROOT / "research/outputs/calibration_v0.1/results_qwen.json").read_text())
    for rho in pp.LEVELS:
        au = []
        for s in pp.TUNING:
            vk = pp.unit(pp.tuning_key(s, 1.0).astype(np.float64))
            w, v = F[f"{pp.tag(rho)}_k{s}"]["A"][te] @ vk, F[f"van_k{s}"]["A"][te] @ vk
            au.append(mannwhitneyu(w, v).statistic / (len(w) * len(v)))
        out["s1_calibration_split"][str(rho)] = {
            "s1_auroc_mean_over_keys": float(np.mean(au)),
            "calibration_dcos_true_key": calib["per_rho"][str(rho)]["auroc"]["dcos_true_key"],
            "calibration_mlp_faithful": calib["per_rho"][str(rho)]["auroc"]["mlp_faithful"]}
    fresh_seeds = [FRESH_SEED0 + i for i in range(N_FRESH)]
    null_seeds = {core.NULL_KEY_SEED * 100000 + j for j in range(core.N_NULL_KEYS)}
    assert not (set(fresh_seeds) & (pp.OTHER_SEEDS | null_seeds | {88_800_000 + i for i in range(10000)}))
    fresh = pp.unit(np.stack([core.make_key(s, pp.D, 1.0).numpy() for s in fresh_seeds]).astype(np.float64))
    A = np.concatenate([F[f"van_k{s}"]["A"] for s in pp.TUNING])
    G = np.concatenate([F[f"van_k{s}"]["G"] for s in pp.TUNING])
    for c in pp.CANDS:
        X = pp.transform(c, A, G, ref)
        NX = X @ nm.T
        TF = X @ fresh.T
        cond = np.array([100 * float((pp.pvalues(TF[:, i], NX) <= pp.ALPHA).mean()) for i in range(N_FRESH)])
        out["conditional_fpr"][c] = {"n_keys": N_FRESH, "n_texts": int(X.shape[0]), "mean_pct": float(cond.mean()),
                                     "share_keys_0": float((cond == 0).mean()),
                                     "share_keys_gt5": float((cond > 5).mean()),
                                     "share_keys_gt50": float((cond > 50).mean()),
                                     "p95_pct": float(np.percentile(cond, 95)), "max_pct": float(cond.max())}
    (pp.OUT / "posthoc_diagnostics.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
