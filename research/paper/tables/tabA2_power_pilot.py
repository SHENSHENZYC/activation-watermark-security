"""TA2 — the Study 3 power pilot (Appendix B): the four candidate statistics S1–S4 under the exact key-resampling test on
the tuning keys: the implementation (FPR) check, the pre-set score, TPR and AUROC per ρ, cross-key detection, and the
post-hoc per-key false-positive diagnosis over 1,000 random keys. Reads research/outputs/study3_pilot_v0.1/results.json
and posthoc_diagnostics.json; re-computes the score and the pass flags and asserts them; writes build/tabA2.md and
build/values_tabA2.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

O = C.OUT
V = C.Values("tabA2")
res = C.load(O / "study3_pilot_v0.1" / "results.json")
post = C.load(O / "study3_pilot_v0.1" / "posthoc_diagnostics.json")
val = C.load(O / "study3_pilot_v0.1" / "VALIDATION.json")
assert val["all_pass"] is True
assert post["note"].startswith("written and run after the pilot's outcomes were read")

CANDS = ["S1", "S2", "S3", "S4"]
NAMES = {"S1": "raw cosine (token-averaged activations)", "S2": "standardised cosine", "S3": "gradient score", "S4": "standardised gradient score"}
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
WORKING = ["0.35", "0.5", "0.7"]
FPR_RANGE = (0.3, 2.5)   # the spec's implementation-check range (the pilot's fpr_check pass flags are re-derived from it below)

rows = []
for c in CANDS:
    f = res["fpr_check"][c]
    assert f["pass"] == (FPR_RANGE[0] <= f["rate_pct"] <= FPR_RANGE[1]), c
    meds = {rho: res["tpr"][c][rho]["median"] for rho in LEVELS}
    for rho in LEVELS:
        pk = list(res["tpr"][c][rho]["per_key"].values())
        assert abs(float(np.median(pk)) - meds[rho]) < 1e-9, (c, rho)
    score = float(np.mean([meds[r] for r in WORKING]))
    assert abs(score - res["score"][c]) < 1e-9, c
    au = {rho: res["auroc"][c][rho]["median"] for rho in LEVELS}
    ck = {rho: res["cross_key"][c][rho]["rate_pct"] for rho in LEVELS}
    d = post["conditional_fpr"][c]
    assert d["share_keys_gt50"] <= d["share_keys_gt5"] <= 1.0 and d["n_keys"] == 1000
    rows.append([f"{c} {NAMES[c]}", f"{C.f2(f['rate_pct'])}% ({'pass' if f['pass'] else 'FAIL'})", C.f1(score)]
                + [f"{meds[r]:.0f}" for r in LEVELS] + [f"{au[r]:.3f}" for r in LEVELS] + [f"{ck[r]:.1f}" for r in LEVELS]
                + [f"{C.f2(d['mean_pct'])} / {C.f2(d['p95_pct'])} / {C.f2(d['max_pct'])}", f"{100 * d['share_keys_0']:.1f} / {100 * d['share_keys_gt5']:.1f} / {100 * d['share_keys_gt50']:.1f}"])
    V.set(f"pilot_{c}_fpr_pct", C.f2(f["rate_pct"]))
    V.set(f"pilot_{c}_fpr_pass", "pass" if f["pass"] else "fail")
    V.set(f"pilot_{c}_score", C.f1(score))
    for rho in LEVELS:
        V.set(f"pilot_{c}_tpr_{rho.replace('.', '')}", f"{meds[rho]:.0f}")
    V.set(f"pilot_{c}_tpr_working_min", f"{min(meds[r] for r in WORKING):.0f}")
    V.set(f"pilot_{c}_tpr_working_max", f"{max(meds[r] for r in WORKING):.0f}")
    V.set(f"pilot_{c}_perkey_mean_pct", C.f2(d["mean_pct"]))
    V.set(f"pilot_{c}_perkey_max_pct", C.f2(d["max_pct"]))
    V.set(f"pilot_{c}_perkey_share_gt50_pct", C.f1(100 * d["share_keys_gt50"]))
    V.set(f"pilot_{c}_perkey_share_gt5_pct", C.f1(100 * d["share_keys_gt5"]))
    V.set(f"pilot_{c}_perkey_share_zero_pct", C.f1(100 * d["share_keys_0"]))
    V.set(f"pilot_{c}_crosskey_min", C.f1(min(ck.values())))
    V.set(f"pilot_{c}_crosskey_max", C.f1(max(ck.values())))

sel = res["selection"]
assert sel["implementation_check_pass"] is False and sel["primary"] is None and set(sel["within_tie_margin"]) == {"S3", "S4"}
V.set("pilot_top_score", C.f1(sel["top_score"]))
V.set("pilot_tie_candidates", " and ".join(sel["within_tie_margin"]))
V.set("pilot_M", res["M"])
V.set("pilot_alpha_pct", f"{100 * res['alpha']:g}")
V.set("pilot_n_tuning_keys", len(res["tpr"]["S4"]["0.35"]["per_key"]))
V.set("pilot_n_fpr_tests", f"{res['fpr_check']['S4']['n_tests']:,}")
V.set("pilot_n_crosskey_tests", f"{res['cross_key']['S4']['0.35']['n_tests']:,}")
V.set("pilot_spread_act", C.f1(res["ref_scale_spread"]["sd_a_max_over_median"]))
V.set("pilot_spread_grad", C.f1(res["ref_scale_spread"]["sd_g_max_over_median"]))
V.set("pilot_s_per_text", C.f2(res["timing_s_per_text"]))
V.set("pilot_posthoc_n_keys", f"{post['conditional_fpr']['S4']['n_keys']:,}")
V.set("pilot_posthoc_n_texts", f"{post['conditional_fpr']['S4']['n_texts']:,}")
# pooled tests (descriptive): S4 at 4 and 16 texts
pooled = res["pooled"]["S4"]
V.set("pilot_S4_pooled4_fpr_pct", C.f1(pooled["4"]["fpr_pct"]))
V.set("pilot_S4_pooled16_fpr_pct", C.f1(pooled["16"]["fpr_pct"]))
# the validation's gradient check (finite differences against the analytic gradient)
V.set("pilot_grad_fd_r", C.f3(val["checks"]["4_gradient_fd"]["r"]))
V.set("pilot_ks_p", C.f2(val["checks"]["3_pvalues_synthetic"]["ks_p"]))

hdr = ["Candidate", "FPR check (1,600 tests; pass if 0.3–2.5%)", "Score (mean median TPR, ρ 0.35–0.70)"] \
    + [f"TPR % ρ = {r}" for r in LEVELS] + [f"AUROC ρ = {r}" for r in LEVELS] + [f"cross-key % ρ = {r}" for r in LEVELS] \
    + ["per-key FPR over 1,000 keys: mean / 95th pct / max (%)", "keys never firing / above 5% / above 50% (%)"]
C.write_table("TA2", hdr, rows, "The power pilot (tuning keys 9001–9004, 100 texts per key and strength): four candidate statistics under the exact key-resampling test at p ≤ 0.01",
              ["TPR, AUROC and the score are medians over the four tuning keys; ρ = 0.25 is descriptive (the probe failed its gate there in Study 1). Cross-key: a text steered by one tuning key tested with another (1,200 tests per cell; about 1% is expected by construction). The per-key columns are the post-hoc diagnosis (written and run after the pilot's outcomes were read; exploratory): each of 1,000 fresh random keys tested on the 400 unwatermarked texts. By the pre-set rule no primary was chosen, because S1 failed the implementation check (0.00%); S4 was chosen by decision after the diagnosis (the rule's flaw and the choice are stated in Appendix B)."])
p = V.save()
print("TA2 written; values:", p.name, len(V.d))
