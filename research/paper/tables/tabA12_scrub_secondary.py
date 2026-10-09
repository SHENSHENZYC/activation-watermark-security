"""TA12 — the scrubbing study's secondary readings (Appendix F): (a) per strength and method, detection after scrubbing
at p ≤ 0.01 and at the stricter p ≤ 0.001, four texts pooled, the length-matched control (the originals cut to the
paraphrase's length), the owner's probe on the same scrubbed texts (the C11 lead) and the first-attempt-only success;
(b) calibration after paraphrase: each key's false-positive rate on the paraphrased null texts, the pooled rate, the
1,000 fresh public-distribution keys (mean, share above 3%, maximum) and the probe's false-positive rate on the same
texts; (c) the paraphrase attempts and the editor's bookkeeping. Reads study2_v0.1/results.json and, for the unscrubbed
row, study3_v0.1/results.json; writes build/TA12a.md, TA12b.md and build/values_tabA12.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA12")
res = C.load(C.OUT / "study2_v0.1" / "results.json")
r3 = C.load(C.OUT / "study3_v0.1" / "results.json")
SEC = res["secondary"]
METH = [("P-Qwen", "para_qwen_gen", "S1_qwen"), ("P-Phi", "para_phi_gen", "S1_phi"), ("E-true 5%", "edit_true_0.05", "E-true 0.05"), ("E-est 5%", "edit_est_0.05", "E-est 0.05"),
        ("E-rand 5%", "edit_rand_0.05", "E-rand 0.05")]
rows = []
for rho in C.LEVELS4:
    L, t = res["levels"][rho], C.tag(rho)
    O = r3["S4"]["levels"][rho]["oracle"]
    rows.append([C.rho_lab(rho), "unscrubbed originals", C.f1(C.chk(L["P1"]["detected_before"]) and L["P1"]["detected_before"]["median"]), f"{C.pct(O['acceptance_0.001_median'])} (Study 3)",
                 f"{C.pct(O['pooled4_detection_median'])} (Study 3)", "—", f"{C.pct(O['probe_acceptance_median'])} (Study 3)", "—"])
    for lab, nm, key in METH:
        d = L[key]
        C.chk(d["detected_after"])
        para = nm.startswith("para")
        lm = C.f1(SEC["length_matched"][nm.split("_")[1]][rho]) if para else "—"
        fa = C.f1(d["first_attempt"]["success"]["median"]) if para else "—"
        rows.append([C.rho_lab(rho), lab, C.f1(d["detected_after"]["median"]), C.f1(SEC["alpha_0.001"][nm][rho]), C.f1(SEC["pooled_4"][nm][rho]), lm, C.f1(SEC["probe"][nm][rho]), fa])
        short = nm.replace("para_", "P").replace("_gen", "").replace("edit_", "E").replace("_0.05", "")
        V.set(f"ta12_{short}_{t}_detected", C.f1(d["detected_after"]["median"]))
        V.set(f"ta12_{short}_{t}_a001", C.f1(SEC["alpha_0.001"][nm][rho]))
        V.set(f"ta12_{short}_{t}_pooled4", C.f1(SEC["pooled_4"][nm][rho]))
        V.set(f"ta12_{short}_{t}_probe", C.f1(SEC["probe"][nm][rho]))
        if para:
            V.set(f"ta12_{short}_{t}_lm", lm)
            V.set(f"ta12_{short}_{t}_first_attempt", fa)
            V.set(f"ta12_{short}_{t}_ppl_ratio", C.f2(d["median_ppl_ratio"]))
            V.set(f"ta12_{short}_{t}_len_ratio", C.f2(d["median_len_ratio"]))
            V.set(f"ta12_{short}_{t}_cos", C.f3(d["median_cos"]))
            V.set(f"ta12_{short}_{t}_pass_all", C.f1(d["pass"]["all"]))
            V.set(f"ta12_{short}_{t}_pass_ppl", C.f1(d["pass"]["ppl"]))
            V.set(f"ta12_{short}_{t}_pass_len", C.f1(d["pass"]["len"]))
            V.set(f"ta12_{short}_{t}_pass_cos", C.f1(d["pass"]["cos"]))
            V.set(f"ta12_{short}_{t}_strict_model", C.f1(d["success_stricter"]["A_model_p95"]))
            V.set(f"ta12_{short}_{t}_strict_human", C.f1(d["success_stricter"]["A_human_median"]))
lm_all = [SEC["length_matched"][m][r] for m in ("qwen", "phi") for r in C.LEVELS4]
V.set("ta12_lm_min", C.f1(min(lm_all)))
V.set("ta12_lm_max", C.f1(max(lm_all)))
probe_hi = [SEC["probe"][nm][r] for nm in ("para_qwen_gen", "para_phi_gen") for r in ("0.5", "0.7")]
s4_hi = [res["levels"][r][k]["detected_after"]["median"] for k in ("S1_qwen", "S1_phi") for r in ("0.5", "0.7")]
V.set("ta12_probe_para_hi_min", C.f1(min(probe_hi)))
V.set("ta12_probe_para_hi_max", C.f1(max(probe_hi)))
V.set("ta12_S4_para_hi_min", C.f1(min(s4_hi)))
V.set("ta12_S4_para_hi_max", C.f1(max(s4_hi)))
probe_lo = [SEC["probe"][nm][r] for nm in ("para_qwen_gen", "para_phi_gen") for r in ("0.25", "0.35")]
V.set("ta12_probe_para_lo_min", C.f1(min(probe_lo)))
V.set("ta12_probe_para_lo_max", C.f1(max(probe_lo)))
V.set("ta12_Pphi_pooled4_035", C.f1(SEC["pooled_4"]["para_phi_gen"]["0.35"]))
C.write_table("TA12a", ["ρ", "method", "detected after (p ≤ 0.01)", "at p ≤ 0.001 (9,999 null keys)", "4 texts pooled: detected", "originals cut to the paraphrase's length: detected",
                        "the owner's probe accepts", "first attempt only: success"], rows,
              "Study 2: secondary readings per method (median over 8 keys, %)",
              ["The length-matched control truncates each original to its paraphrase's token count and scores it with S4; it separates less text from removed evidence. "
               "The probe column is the share of scrubbed texts the owner's trained probe (Study 1) still accepts at its own 1% threshold (the C11 lead; labelled, not a result). "
               "First attempt only: success counting only the attacker's first paraphrase attempt (its self-check allows up to three)."])
# (b) calibration after paraphrase
rows_b = []
for m, lab in (("qwen", "P-Qwen"), ("phi", "P-Phi")):
    Cm = res["calibration"][m]
    g2 = [Cm["G2"]["per_key_fpr_pct"][str(k)] for k in C.KEYS]
    assert abs(np.mean(g2) - Cm["G1"]["pooled_fpr_pct"]) < 1e-9 and Cm["G1"]["pass"] is True
    assert [k for k, v in zip(C.KEYS, g2) if v <= 3.0] == Cm["G2"]["calibrated"] and Cm["G2"]["n_calibrated"] == 8
    fk = Cm["fresh_keys"]
    rows_b.append([lab] + [C.f1(v) for v in g2] + [C.f2(Cm["G1"]["pooled_fpr_pct"]), f"{sum(v > 3.0 for v in g2)}", C.f2(fk["mean_fpr_pct"]), f"{C.f1(100 * fk['share_above_3pct'])}% (max {C.f1(fk['max_fpr_pct'])})",
                   C.f1(Cm["probe_fpr_on_paraphrased_A2_pct"]["median"])])
    V.set(f"ta12_cal_{m}_G1", C.f2(Cm["G1"]["pooled_fpr_pct"]))
    V.set(f"ta12_cal_{m}_G2_min", C.f1(min(g2)))
    V.set(f"ta12_cal_{m}_G2_max", C.f1(max(g2)))
    V.set(f"ta12_fresh_{m}_mean", C.f2(fk["mean_fpr_pct"]))
    V.set(f"ta12_fresh_{m}_share3", C.f1(100 * fk["share_above_3pct"]))
    V.set(f"ta12_fresh_{m}_max", C.f1(fk["max_fpr_pct"]))
    V.set(f"ta12_probe_fpr_{m}", C.f1(Cm["probe_fpr_on_paraphrased_A2_pct"]["median"]))
    pa = SEC["paraphrase_attempts"][m]
    tot = sum(pa["used"].values())
    V.set(f"ta12_attempts_{m}_total", f"{tot:,}")
    V.set(f"ta12_attempts_{m}_1", f"{pa['used']['1']:,}")
    V.set(f"ta12_attempts_{m}_2", f"{pa['used']['2']:,}")
    V.set(f"ta12_attempts_{m}_3", f"{pa['used']['3']:,}")
    V.set(f"ta12_attempts_{m}_failing", f"{pa['kept_failing_attacker_check']:,}")
    V.set(f"ta12_attempts_{m}_failing_pct", C.pct(pa["kept_failing_attacker_check"] / tot))
V.set("ta12_fresh_share3_min", C.f1(100 * min(res["calibration"][m]["fresh_keys"]["share_above_3pct"] for m in ("qwen", "phi"))))
V.set("ta12_fresh_share3_max", C.f1(100 * max(res["calibration"][m]["fresh_keys"]["share_above_3pct"] for m in ("qwen", "phi"))))
V.set("ta12_fresh_max_min", C.f1(min(res["calibration"][m]["fresh_keys"]["max_fpr_pct"] for m in ("qwen", "phi"))))
V.set("ta12_fresh_max_max", C.f1(max(res["calibration"][m]["fresh_keys"]["max_fpr_pct"] for m in ("qwen", "phi"))))
V.set("ta12_fresh_mean_min", C.f2(min(res["calibration"][m]["fresh_keys"]["mean_fpr_pct"] for m in ("qwen", "phi"))))
V.set("ta12_fresh_mean_max", C.f2(max(res["calibration"][m]["fresh_keys"]["mean_fpr_pct"] for m in ("qwen", "phi"))))
for a in ("true", "est", "rand"):
    e = SEC["edits"][a]
    V.set(f"ta12_edits_{a}_stalled", e["stalled"])
    V.set(f"ta12_edits_{a}_drift_max", C.f3(max(e["median_drift"].values())))
    if "median_objective" in e:
        V.set(f"ta12_edits_{a}_obj_0", C.f2(e["median_objective"]["0"]))
        V.set(f"ta12_edits_{a}_obj_10", C.f2(e["median_objective"]["0.1"]))
C.write_table("TA12b", ["paraphraser"] + [str(k) for k in C.KEYS] + ["pooled (G1)", "keys above 3% (G2)", "1,000 fresh keys: mean FPR", "fresh keys above 3% (max)", "the probe's FPR on the same texts (median)"], rows_b,
              "Study 2: false-positive rates at p ≤ 0.01 (%) on 1,000 paraphrased unwatermarked texts per key, before any verdict",
              ["Fresh keys are 1,000 public-distribution keys never used by the owner, each tested on the same paraphrased texts; the share above 3% estimates how often a "
               "newly drawn key would fail the per-key gate after paraphrase (C9). The probe column is the owner's trained probe at its own 1% threshold on the same texts."])
p = V.save()
print("TA12 written; values:", p.name, len(V.d))
