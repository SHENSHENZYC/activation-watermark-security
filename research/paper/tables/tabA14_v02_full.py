"""TA14 — Study 1 v0.2 in full (Appendix E): (a) plain acceptance by the owner's probe at its 1% threshold for the genuine
texts, the random-key control and the Route A and Route B forgeries at n = 64, 256 and 1,024, with the median perplexity
under the unsteered model; (b) key recovery against n = 1 … 1,024 (median cosine with the key for Routes A and B, layer
hits out of 8, Route A's median support hit out of k = 4) and the pre-registered verdicts L1, R1, R2 and R3. Reads
study1_v0.2/results.json; asserts every median; writes build/TA14a.md, TA14b.md and build/values_tabA14.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA14")
res = C.load(C.OUT / "study1_v0.2" / "results.json")
assert res["gates"]["G1"] is True
V.set("ta14_G1_pct", C.f2(100 * res["G1_pooled_FPR_A2"]))
V.set("ta14_human_fpr_pct", C.f1(100 * res["human_FPR_A2"]))
SETS = [("oracle", "genuine (oracle)"), ("random", "random key")] + [(f"forge_{r}_n{n}", f"Route {r}, n = {n:,}") for r in "AB" for n in (64, 256, 1024)]
rows = []
for rho in C.LEVELS4:
    L, t = res["levels"][rho], C.tag(rho)
    for s, lab in SETS:
        d = L[s]
        C.chk(d)
        rows.append([C.rho_lab(rho), lab, C.pct_ci(d), C.f1(d["ppl_median"])])
        V.set(f"ta14_{s}_{t}_acc", C.pct(d["median"]))
        V.set(f"ta14_{s}_{t}_ppl", C.f1(d["ppl_median"]))
    V.set(f"ta14_L1_{t}", "yes" if L["rules"]["L1_working_watermark"] else "no")
    V.set(f"ta14_R1_{t}", L["rules"]["R1"])
    V.set(f"ta14_R2_A_{t}", L["rules"]["R2"]["A"])
    V.set(f"ta14_R2_B_{t}", L["rules"]["R2"]["B"])
    V.set(f"ta14_R3_{t}", "yes" if L["rules"]["R3_generic_steering_suffices"] else "no")
C.write_table("TA14a", ["ρ", "texts", "accepted by the probe (%) [95% CI]", "median perplexity under the unsteered model"], rows,
              "Study 1 v0.2: plain acceptance by the owner's probe at its 1% threshold (median over 8 keys), without any quality condition",
              [f"Calibration: pooled false-positive rate {V.d['ta14_G1_pct']}% on unwatermarked model text (G1), {V.d['ta14_human_fpr_pct']}% on human continuations (exploratory). "
               "Perplexity is the median over the set's texts under the unsteered model; a low value can also mean repetitive text (Appendix E)."])
rows_b = []
for rho in C.LEVELS4:
    L, t = res["levels"][rho], C.tag(rho)
    for n in ("1", "4", "16", "64", "256", "1024"):
        r = L["recovery"][n]
        rows_b.append([C.rho_lab(rho), f"{int(n):,}", C.f3(r["median_cos_A"]), f"{r['layer_hits_A']}", C.f2(r["median_support_hit_A"]), C.f3(r["median_cos_B"]), f"{r['layer_hits_B']}"])
        V.set(f"ta14_cosA_n{n}_{t}", C.f3(r["median_cos_A"]))
        V.set(f"ta14_cosB_n{n}_{t}", C.f3(r["median_cos_B"]))
        V.set(f"ta14_hitsA_n{n}_{t}", r["layer_hits_A"])
    rows_b.append([C.rho_lab(rho), "verdicts", f"L1 working watermark: {V.d[f'ta14_L1_{t}']}", f"R1: {L['rules']['R1']}", f"R2 A: {L['rules']['R2']['A']}", f"R2 B: {L['rules']['R2']['B']}",
                   f"R3: {V.d[f'ta14_R3_{t}']}"])
V.set("ta14_cosA_max", C.f3(max(res["levels"][r]["recovery"][n]["median_cos_A"] for r in C.LEVELS4 for n in ("1", "4", "16", "64", "256", "1024"))))
V.set("ta14_cosB_max", C.f3(max(res["levels"][r]["recovery"][n]["median_cos_B"] for r in C.LEVELS4 for n in ("1", "4", "16", "64", "256", "1024"))))
V.set("ta14_hitsA_max", max(res["levels"][r]["recovery"][n]["layer_hits_A"] for r in C.LEVELS4 for n in ("1", "4", "16", "64", "256", "1024")))
C.write_table("TA14b", ["ρ", "n", "Route A: median cos(v̂, v)", "Route A: layer 14 found (keys of 8)", "Route A: median support hit (of k = 4)", "Route B: median cos(v̂, v)", "Route B: layer 14 found (keys of 8)"],
              rows_b, "Study 1 v0.2: key recovery against the budget n (medians over 8 keys) and the pre-registered verdicts",
              ["Route A estimates the key as the mean activation difference between observed and unwatermarked texts at the attacker's chosen layer; Route B fits a probe and "
               "takes its direction. R1 asks, at some n, for a median cosine ≥ 0.9 with the layer found for at least 7 of 8 keys (the smallest such n is n*), and reads 'partial' if the median cosine at n = 1,024 is in [0.5, 0.9); it fails at every strength."])
p = V.save()
print("TA14 written; values:", p.name, len(V.d))
