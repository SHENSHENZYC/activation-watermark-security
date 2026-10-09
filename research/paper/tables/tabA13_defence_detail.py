"""TA13 — the defence in detail (Appendix G): (a) P-Qwen paraphrase per arm beside the fixed key (scrub success,
detection after, quality pass, the difference d from the fixed key with its interval and key count, the verdict); (b)
the rotation addendum (post hoc, labelled): every cluster's estimate at ρ = 0.35 forged and tested with the union test
at n = 256 and 1,024, with the three selection rules; (c) the defence pilot on tuning keys 9001–9004 and its I4
addendum (the per-position h = 0 form against S4). Reads study5_v0.1/results.json, study5_v0.1/ADDENDUM_ROTATION.json,
study2_v0.1/results.json, study5_pilot_v0.1/results.json and ADDENDUM_I4.json; asserts the selection rules and medians;
writes build/TA13a.md, TA13b.md, TA13c.md and build/values_tabA13.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA13")
r5 = C.load(C.OUT / "study5_v0.1" / "results.json")
ad = C.load(C.OUT / "study5_v0.1" / "ADDENDUM_ROTATION.json")
r2 = C.load(C.OUT / "study2_v0.1" / "results.json")
pil = C.load(C.OUT / "study5_pilot_v0.1" / "results.json")
i4 = C.load(C.OUT / "study5_pilot_v0.1" / "ADDENDUM_I4.json")
K = [str(k) for k in C.KEYS]


def med(xs):
    return float(np.median(xs))


def ci(c, nd=1):
    return f"[{c[0]:+.{nd}f}, {c[1]:+.{nd}f}]"


# (a) paraphrase per arm
rows = []
for rho in C.LEVELS2:
    t = C.tag(rho)
    S1 = r2["levels"][rho]["S1_qwen"]
    assert np.allclose([S1["success"]["per_key"][k] for k in K], [100 * v for v in r5["fixed"][rho]["s2_success"]["per_key"]])
    rows.append(["fixed key (h = 0; Study 2)", C.rho_lab(rho), f"{C.f1(S1['success']['median'])} [{C.f1(S1['success']['ci95'][0])}, {C.f1(S1['success']['ci95'][1])}]",
                 C.f1(S1["detected_after"]["median"]), C.f1(S1["pass"]["all"]), "—", f"{S1['verdict']} (Study 2's S1)"])
    for a in ("h1", "h4"):
        L = r5["arms"][a]["levels"][rho]
        for fld in ("para_success", "para_detected", "para_quality_pass"):
            C.chk(L[fld])
        D2 = L["D2"]
        rows.append([f"context-hashed, h = {r5['arms'][a]['h']}", C.rho_lab(rho), C.pct_ci(L["para_success"]), C.pct_ci(L["para_detected"]), C.pct_ci(L["para_quality_pass"]),
                     f"{D2['median_diff_points']:+.1f} {ci(D2['ci95'])}; {D2['n_keys_ge_20_points']} of 8 keys ≥ 20 points", f"**{D2['verdict']}** ({D2['absolute']})"])
        V.set(f"ta13_{a}_{t}_success", C.pct_ci(L["para_success"]))
        V.set(f"ta13_{a}_{t}_detected", C.pct_ci(L["para_detected"]))
        V.set(f"ta13_{a}_{t}_quality", C.pct_ci(L["para_quality_pass"]))
        V.set(f"ta13_{a}_{t}_d", f"{D2['median_diff_points']:+.1f} {ci(D2['ci95'])}")
        V.set(f"ta13_{a}_{t}_d_keys", D2["n_keys_ge_20_points"])
        V.set(f"ta13_{a}_{t}_D2", D2["verdict"])
    R = r5["rotation"][rho]
    us = [R["per_key"][k]["union_success"] for k in K]
    rows.append(["rotation (K = 8; the union test on Study 2's paraphrases)", C.rho_lab(rho), C.pct(med(us)), "— (not in the locked results file)", "as the fixed key",
                 f"{R['D2']['median_diff_points']:+.1f} {ci(R['D2']['ci95'])}", f"**{R['D2']['verdict']}**"])
    V.set(f"ta13_rot_{t}_success", C.pct(med(us)))
    V.set(f"ta13_rot_{t}_d", f"{R['D2']['median_diff_points']:+.1f} {ci(R['D2']['ci95'])}")
    V.set(f"ta13_rot_{t}_D2", R["D2"]["verdict"])
    V.set(f"ta13_fixed_{t}_success", C.f1(S1["success"]["median"]))
    V.set(f"ta13_fixed_{t}_detected", C.f1(S1["detected_after"]["median"]))
C.write_table("TA13a", ["arm", "ρ", "scrub success (%) [95% CI]", "detected after paraphrase (%) [95% CI]", "all four quality conditions pass (%) [95% CI]",
                        "d = success − the fixed key's, points [95% CI]", "D2 verdict"], rows,
              "Study 5: P-Qwen paraphrase (with the attacker's self-check) per arm beside the fixed key (median over 8 keys; 100 paraphrases per key and strength)",
              ["D2 reads d against a 20-point materiality bar: material if the median d is at least 20 points and the interval's lower bound is above 0, immaterial if the upper bound is below 20, otherwise inconclusive (the pre-registered rule; Appendix A). Rotation's "
               "paraphrases are Study 2's, re-scored by the union test; its detection after paraphrase was computed by the report builder from the run's per-key files and "
               "is not in the locked results file, so it is not repeated here."])
# (b) the rotation addendum
assert ad["rho"] == 0.35
bar = ad["bar_half_genuine_FA"]
V.set("ta13_add_bar", C.pct(bar))
V.set("ta13_add_cut_ppl", C.f1(ad["cut_ppl"]))
V.set("ta13_add_cut_rep", C.f3(ad["cut_rep"]))
rows_b = []
for n in ("256", "1024"):
    A = ad["n"][n]
    cl = A["clusters"]
    best = max(cl, key=lambda c: cl[c]["FA"])
    largest = max(cl, key=lambda c: cl[c]["size"])
    study = max(cl, key=lambda c: cl[c]["profile"])
    assert best == A["every_cluster"]["cluster"] and abs(cl[best]["FA"] - A["every_cluster"]["FA"]) < 1e-9
    assert largest == A["largest_cluster_rule"]["cluster"] and abs(cl[largest]["FA"] - A["largest_cluster_rule"]["FA"]) < 1e-9
    assert study == A["study_rule"]["cluster"] and abs(cl[study]["FA"] - A["study_rule"]["FA"]) < 1e-9
    ge = [c for c in cl if cl[c]["best_cos"] >= 0.5]
    assert len(ge) == A["clusters_cos_ge_0.5"] and sum(cl[c]["FA"] >= bar for c in ge) == A["clusters_cos_ge_0.5_reaching_bar"]
    for c in sorted(cl, key=lambda c: -cl[c]["best_cos"]):
        x = cl[c]
        tags = [s for s, cc in (("best FA (every-cluster attacker)", best), ("largest cluster", largest), ("study rule: largest z-profile", study)) if cc == c]
        rows_b.append([f"{int(n):,}", c, x["size"], x["best_key"], C.f2(x["best_cos"]), C.f2(x["profile"]), C.pct0(x["accepted"]), C.pct0(x["fluent"]),
                       f"{C.pct0(x['FA'])} [{C.pct0(x['FA_ci95'][0])}, {C.pct0(x['FA_ci95'][1])}]", C.f1(x["median_ppl"]), "; ".join(tags)])
    V.set(f"ta13_add_n{n}_study_FA", C.pct0(A["study_rule"]["FA"]))
    V.set(f"ta13_add_n{n}_largest_FA", C.pct0(A["largest_cluster_rule"]["FA"]))
    V.set(f"ta13_add_n{n}_every_FA", C.pct0(A["every_cluster"]["FA"]))
    V.set(f"ta13_add_n{n}_every_cos", C.f2(cl[best]["best_cos"]))
    V.set(f"ta13_add_n{n}_study_cos", C.f2(cl[study]["best_cos"]))
    V.set(f"ta13_add_n{n}_study_profile", C.f2(cl[study]["profile"]))
    V.set(f"ta13_add_n{n}_study_size", cl[study]["size"])
    V.set(f"ta13_add_n{n}_study_fluent", C.pct0(cl[study]["fluent"]))
    V.set(f"ta13_add_n{n}_clusters_ge05", A["clusters_cos_ge_0.5"])
    V.set(f"ta13_add_n{n}_reaching_bar", A["clusters_cos_ge_0.5_reaching_bar"])
    V.set(f"ta13_add_n{n}_n_clusters", len(cl))
    V.set(f"ta13_add_n{n}_keys_recovered", len({cl[c]["best_key"] for c in ge}))
C.write_table("TA13b", ["n", "cluster", "texts in the cluster", "nearest study key", "cos(v̂, v) with it", "z-profile", "accepted by the union test (%)", "fluent (%)", "FA (%) [95% Wilson]",
                        "median perplexity", "selection rule"], rows_b,
              "Rotation addendum (post hoc, labelled; not pre-registered): forging with every cluster's estimate at ρ = 0.35, 100 forgeries per cluster, the union test at p ≤ 0.01",
              [f"The pre-registered forgery used the cluster with the largest standardised mean-gradient profile (z-profile), which at this strength is a small cluster whose "
               f"estimate has cosine near 0 with every key; the D1 bar is half the fixed key's genuine FA ({C.pct(bar)}%). Fluency uses the level's pooled bars (perplexity ≤ "
               f"{C.f1(ad['cut_ppl'])}, seq-rep-4 ≤ {C.f3(ad['cut_rep'])}). Study 5's pre-registered D1 verdict for rotation at 0.35 stands; this table is the labelled addendum beside it."])
# (c) the pilot on tuning keys and the I4 addendum
assert pil["validation_all_pass"] is True
rows_c = []
for a in ("h1", "h4"):
    M = pil["arms"][a]["median"]
    pk = pil["arms"][a]["per_key"]
    for fld in ("detect050_pct", "ppl_ratio_050", "forge_FA_pct", "para_success_pct", "para_detected_pct"):
        assert abs(med([pk[k][fld] for k in pk]) - M[fld]) < 1e-9, (a, fld)
    att = M["attacker"]
    rows_c.append([f"h = {pil['arms'][a]['h']}", C.f1(M["detect050_pct"]), C.f1(M["detect035_pct"]), C.f2(M["ppl_ratio_050"]), C.f2(M["ppl_ratio_035"]), C.f1(M["forge_FA_pct"]),
                   C.f1(M["control_accept_pct"]), C.f1(M["para_success_pct"]), C.f1(M["para_detected_pct"]),
                   " / ".join(f"{C.f3(att[n]['cos_weighted'])} ({C.f2(att[n]['coverage_genuine'])}; {att[n]['n_contexts']:g})" for n in ("16", "64", "100"))])
    V.set(f"ta13_pilot_{a}_detect050", C.f1(M["detect050_pct"]))
    V.set(f"ta13_pilot_{a}_detect035", C.f1(M["detect035_pct"]))
    V.set(f"ta13_pilot_{a}_ppl050", C.f2(M["ppl_ratio_050"]))
    V.set(f"ta13_pilot_{a}_forge_FA", C.f1(M["forge_FA_pct"]))
    V.set(f"ta13_pilot_{a}_para_success", C.f1(M["para_success_pct"]))
    V.set(f"ta13_pilot_{a}_para_detected", C.f1(M["para_detected_pct"]))
    V.set(f"ta13_pilot_{a}_cos100", C.f3(att["100"]["cos_weighted"]))
    V.set(f"ta13_pilot_{a}_cov100", C.f2(att["100"]["coverage_genuine"]))
    V.set(f"ta13_pilot_{a}_ctx100", f"{att['100']['n_contexts']:g}")
fx = pil["fixed_key_tuning_P_qwen_050_study2_pilot"]
V.set("ta13_pilot_fixed_before", C.f1(fx["detected_before"]["median"]))
V.set("ta13_pilot_fixed_after", C.f1(fx["detected_after"]["median"]))
V.set("ta13_pilot_fixed_success", C.f1(fx["success"]["median"]))
rt = pil["rotation_test"]
V.set("ta13_pilot_rot_union_detect_med", C.f1(med(list(rt["union_detection_pct"].values()))))
V.set("ta13_pilot_rot_union_fpr", C.f1(rt["union_fpr_pct"]))
V.set("ta13_pilot_rot_naive_best", C.f2(max(max(d.values()) for d in rt["naive"].values())))
rec = {n: len({c["best_key"] for c in rt["cluster"][n]["clusters"].values() if c["best_cos"] >= 0.5}) for n in rt["cluster"]}
V.set("ta13_pilot_rot_keys_recovered_n64", rec["64"])
V.set("ta13_pilot_rot_keys_recovered_n400", rec["400"])
V.set("ta13_pilot_rot_keys_recovered_n16", rec["16"])
tp = pil["timing"]["validation_projection"]
assert tp["pass"] is True
V.set("ta13_pilot_projected_h", C.f1(tp["projected_h"]["full"]))
V.set("ta13_pilot_budget_h", C.f1(tp["budget_h"]))
V.set("ta13_pilot_s_keyed_gen", C.f2(pil["timing"]["measured_keyed_gen_s_per_text"]))
V.set("ta13_pilot_s_para", C.f2(pil["timing"]["measured_para_s_per_original"]))
V.set("ta13_pilot_elapsed_h", C.f1(C.hours(pil["run_guard"]["elapsed_s"])))
assert i4["pass"] is True and all(i4["within_10_points"].values())
for rho in C.LEVELS2:
    t = C.tag(rho)
    h0, s4 = i4["per_position_h0_detection_pct"][rho], i4["S4_detection_pct_study3_pilot"][rho]
    assert abs(med(list(h0["per_key"].values())) - h0["median"]) < 1e-9 and abs(med(list(s4["per_key"].values())) - s4["median"]) < 1e-9
    assert abs(h0["median"] - s4["median"]) <= 10
    V.set(f"ta13_i4_h0_{t}", C.f1(h0["median"]))
    V.set(f"ta13_i4_S4_{t}", C.f1(s4["median"]))
    V.set(f"ta13_i4_diff_{t}", f"{h0['median'] - s4['median']:+.1f}")
C.write_table("TA13c", ["arm", "detection at ρ = 0.50 (%)", "at 0.35 (%)", "perplexity ratio to the fixed key, 0.50", "0.35", "forgery FA at n = 100 (%)", "random-key control (%)",
                        "P-Qwen scrub success (%)", "detected after paraphrase (%)", "per-context attacker: cos (coverage; contexts) at n = 16 / 64 / 100"], rows_c,
              "The defence pilot on tuning keys 9001–9004 at ρ = 0.50 (medians over 4 keys; no rule applies; labelled pilot)",
              [f"The pilot fixed the design before the lock; its I4 addendum measured the per-position form of the keyed test with h = 0 against S4 on the same tuning keys: "
               f"{V.d['ta13_i4_h0_035']}% against {V.d['ta13_i4_S4_035']}% at ρ = 0.35 and {V.d['ta13_i4_h0_05']}% against {V.d['ta13_i4_S4_05']}% at 0.50 (within 10 points, as "
               f"decision 6 required). The rotation code test with K = 4 tuning keys: union-test detection {V.d['ta13_pilot_rot_union_detect_med']}% (median), union false-positive "
               f"rate {V.d['ta13_pilot_rot_union_fpr']}%; the naive averaging attacker's best cosine with any key {V.d['ta13_pilot_rot_naive_best']}; the clustering attacker recovered "
               f"{V.d['ta13_pilot_rot_keys_recovered_n64']} of 4 keys at n = 64."])
p = V.save()
print("TA13 written; values:", p.name, len(V.d))
