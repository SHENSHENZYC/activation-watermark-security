"""TA3 — the secondary statistic S3 (unstandardised gradient) beside the primary S4 on the study keys, and the
probe-and-exact combinations (Appendix B). Reads research/outputs/study3_v0.1/results.json; re-computes the pooled
false-positive rates from the per-key rates, re-counts the calibrated keys, re-derives the P1 and E1 verdicts from the
rules, and asserts them; writes build/tabA3.md and build/values_tabA3.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA3")
res = C.load(C.OUT / "study3_v0.1" / "results.json")
assert res["primary"] == "S4" and res["M"] == 999 and res["M2"] == 9999 and res["alpha"] == 0.01
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
LATE = ["0.35", "0.5", "0.7"]
V.set("s3_M", f"{res['M']:,}")
V.set("s3_M2", f"{res['M2']:,}")
V.set("s3_alpha_pct", C.f1(100 * res["alpha"]))
V.set("s3_alpha2_pct", f"{100 * res['alpha2']:.1f}")
V.set("s3_boot_B", f"{res['boot_B']:,}")

rows_cal, rows_lvl = [], []
for c in ("S4", "S3"):
    Rc = res[c]
    g1, g2, h1 = Rc["G1"], Rc["G2"], Rc["H1"]
    per = {int(k): v for k, v in g2["per_key_fpr_pct"].items()}
    assert abs(np.mean(list(per.values())) - g1["pooled_fpr_pct"]) < 1e-9, c
    assert g1["pass"] == (g1["range"][0] <= g1["pooled_fpr_pct"] <= g1["range"][1]), c
    cal = sorted(k for k, v in per.items() if v <= g2["max_pct"])
    assert cal == sorted(g2["calibrated_keys"]) and g2["n_calibrated"] == len(cal), c
    hper = {int(k): v for k, v in h1["per_key_fpr_pct"].items()}
    assert abs(np.mean(list(hper.values())) - h1["pooled_fpr_pct"]) < 1e-9
    assert h1["n_keys_above_max"] == sum(v > g2["max_pct"] for v in hper.values())
    uncal = sorted(set(per) - set(cal))
    rows_cal.append([c, f"{C.f2(g1['pooled_fpr_pct'])} ({'pass' if g1['pass'] else 'fail'}; range {g1['range'][0]}–{g1['range'][1]})",
                     f"{len(cal)} of {len(per)}" + (f" (key {', '.join(map(str, uncal))} at {', '.join(C.f1(per[k]) for k in uncal)}%)" if uncal else ""),
                     f"{C.f1(min(per.values()))}–{C.f1(max(per.values()))}", f"{C.f2(h1['pooled_fpr_pct'])}; {h1['n_keys_above_max']} key(s) above {g2['max_pct']:.0f}%",
                     f"{C.f1(min(hper.values()))}–{C.f1(max(hper.values()))}"])
    V.set(f"s3_{c}_G1_pooled_pct", C.f2(g1["pooled_fpr_pct"]))
    V.set(f"s3_{c}_G1_pass", "pass" if g1["pass"] else "fail")
    V.set(f"s3_{c}_n_calibrated", len(cal))
    V.set(f"s3_{c}_n_keys", len(per))
    V.set(f"s3_{c}_perkey_min_pct", C.f1(min(per.values())))
    V.set(f"s3_{c}_perkey_max_pct", C.f1(max(per.values())))
    V.set(f"s3_{c}_uncalibrated_keys", ", ".join(map(str, uncal)) if uncal else "none")
    V.set(f"s3_{c}_H1_pooled_pct", C.f2(h1["pooled_fpr_pct"]))
    V.set(f"s3_{c}_H1_max_pct", C.f1(max(hper.values())))
    V.set(f"s3_{c}_H1_keys_above", h1["n_keys_above_max"])
    for rho in LEVELS:
        L = Rc["levels"][rho]
        p1, e1 = L["P1"], L["E1"]
        assert p1["pass"] == (p1["oracle_tpr_median"] >= p1["min"]) and abs(p1["oracle_tpr_median"] - L["oracle"]["acceptance"]["median"]) < 1e-12
        verdict = "exact test more powerful" if e1["ci95"][0] > 0 else ("exact test less powerful" if e1["ci95"][1] < 0 else "no clear difference")
        assert verdict == e1["verdict"], (c, rho)
        x1 = L.get("X1", "—")
        x1txt = f"A: {x1['A']}; B: {x1['B']}" if isinstance(x1, dict) else str(x1)
        v04b = L["v04_B_n256"]["exact_FA"]["median"] if rho in LATE else None
        rows_lvl.append([rho, c, f"{len(Rc['G2']['calibrated_keys'])}", C.pct(L["oracle"]["acceptance"]["median"]), C.pct(L["random"]["acceptance"]["median"]),
                         f"{100 * e1['median_diff_exact_minus_probe']:+.1f} [{100 * e1['ci95'][0]:+.1f}, {100 * e1['ci95'][1]:+.1f}]: {e1['verdict']}",
                         C.pct(v04b) if v04b is not None else "—", x1txt,
                         C.pct(L["oracle"]["probe_acceptance_median"]), C.pct(L["oracle"]["both_acceptance_median"]), C.pct(L["oracle"]["either_acceptance_median"]),
                         f"{C.pct(L['A2_joint_fpr']['both_median'])} / {C.pct(L['A2_joint_fpr']['either_median'])}"])
        tag = rho.replace(".", "")
        V.set(f"s3_{c}_tpr_{tag}", C.pct(L["oracle"]["acceptance"]["median"]))
        V.set(f"s3_{c}_random_{tag}", C.pct(L["random"]["acceptance"]["median"]))
        V.set(f"s3_{c}_E1_{tag}", f"{100 * e1['median_diff_exact_minus_probe']:+.1f}")
        V.set(f"s3_{c}_E1_verdict_{tag}", e1["verdict"])
        V.set(f"s3_{c}_probe_tpr_{tag}", C.pct(L["oracle"]["probe_acceptance_median"]))
        V.set(f"s3_{c}_both_fpr_{tag}", C.pct(L["A2_joint_fpr"]["both_median"]))
        V.set(f"s3_{c}_either_fpr_{tag}", C.pct(L["A2_joint_fpr"]["either_median"]))
        if rho in LATE:
            V.set(f"s3_{c}_X1_A_{tag}", x1["A"])
            V.set(f"s3_{c}_X1_B_{tag}", x1["B"])
    if "alpha_0.001" in Rc:
        V.set(f"s3_{c}_a001_model_pct", C.f2(Rc["alpha_0.001"]["pooled_fpr_model_pct"]))
        V.set(f"s3_{c}_a001_human_pct", C.f2(Rc["alpha_0.001"]["pooled_fpr_human_pct"]))

both_min = min(res["S4"]["levels"][r]["A2_joint_fpr"]["both_median"] for r in LEVELS)
both_max = max(res["S4"]["levels"][r]["A2_joint_fpr"]["both_median"] for r in LEVELS)
either_min = min(res["S4"]["levels"][r]["A2_joint_fpr"]["either_median"] for r in LEVELS)
either_max = max(res["S4"]["levels"][r]["A2_joint_fpr"]["either_median"] for r in LEVELS)
V.set("s3_S4_both_fpr_range", f"{C.pct(both_min)}–{C.pct(both_max)}")
V.set("s3_S4_either_fpr_range", f"{C.pct(either_min)}–{C.pct(either_max)}")
V.set("s3_S4_tpr_min", C.pct(min(res["S4"]["levels"][r]["oracle"]["acceptance"]["median"] for r in LEVELS)))
V.set("s3_S4_tpr_max", C.pct(max(res["S4"]["levels"][r]["oracle"]["acceptance"]["median"] for r in LEVELS)))
V.set("s3_S3_tpr_min", C.pct(min(res["S3"]["levels"][r]["oracle"]["acceptance"]["median"] for r in LEVELS)))
V.set("s3_S3_tpr_max", C.pct(max(res["S3"]["levels"][r]["oracle"]["acceptance"]["median"] for r in LEVELS)))

C.write_table("TA3a", ["Statistic", "G1: pooled FPR on 8 keys × 1,000 unwatermarked model texts (%)", "G2: calibrated keys (per-key FPR ≤ 3%)",
                       "per-key FPR range, model text (%)", "H1: pooled FPR on 1,000 human continuations (%)", "per-key FPR range, human text (%)"],
              rows_cal, "Calibration of the primary (S4) and secondary (S3) statistics on the study keys at p ≤ 0.01 (999 null keys)")
C.write_table("TA3b", ["ρ", "Statistic", "calibrated keys", "genuine TPR (%)", "random-key acceptance (%)", "E1: TPR(exact) − TPR(probe), points [95% CI]",
                       "v0.4 Route B, n = 256: exact-FA (%)", "X1 verdicts", "probe TPR on the same texts (%)", "both detectors (%)", "either detector (%)",
                       "FPR of both / either on pool A2 (%)"],
              rows_lvl, "S3 beside S4 per strength (medians over the keys each statistic calibrates), and the probe-and-exact combinations",
              ["'Both' and 'either' combine the owner's probe (Study 1's rule at its 1% threshold) with the exact test on the same texts. E1 uses a paired cluster bootstrap over keys and texts."])
p = V.save()
print("TA3 written; values:", p.name, len(V.d))
