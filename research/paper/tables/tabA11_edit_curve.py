"""TA11 — the edit curve (Appendix F): scrub success, detection after editing and the share passing all four quality
conditions at 2, 5 and 10% of the tokens, for the true key, the attacker's estimate and random edits, per strength
(median over 8 keys); the originals' miss rate as the 0% point. Reads study2_v0.1/results.json; asserts every median
against its per-key values; writes build/TA11.md and build/values_tabA11.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA11")
res = C.load(C.OUT / "study2_v0.1" / "results.json")
ARMS = [("true", "E-true (true key)"), ("est", "E-est (Route A estimate)"), ("rand", "E-rand (random)")]
B = ["0.02", "0.05", "0.1"]
rows = []
for rho in C.LEVELS4:
    L, t = res["levels"][rho], C.tag(rho)
    miss = L["S1_qwen"]["originals_miss"]
    C.chk(miss)
    V.set(f"ta11_miss_{t}", C.f1(miss["median"]))
    for a, lab in ARMS:
        succ, det, qual = [], [], []
        for b in B:
            d = L[f"E-{a} {b}"]
            C.chk(d["success"])
            C.chk(d["detected_after"])
            succ.append(d["success"]["median"])
            det.append(d["detected_after"]["median"])
            qual.append(d["pass"]["all"])
            bb = b.replace("0.", "").replace("1", "10") if b == "0.1" else b.replace("0.0", "")
            V.set(f"ta11_E{a}_{bb}_{t}_success", C.f1(d["success"]["median"]))
            V.set(f"ta11_E{a}_{bb}_{t}_detected", C.f1(d["detected_after"]["median"]))
            V.set(f"ta11_E{a}_{bb}_{t}_quality", C.f1(d["pass"]["all"]))
            V.set(f"ta11_E{a}_{bb}_{t}_ppl_pass", C.f1(d["pass"]["ppl"]))
        rows.append([C.rho_lab(rho), lab, C.f1(miss["median"])] + [C.f1(x) for x in succ] + [C.f1(x) for x in det] + [C.f1(x) for x in qual])
    V.set(f"ta11_S2_true_{t}", L["S2_true"]["verdict"])
    V.set(f"ta11_S2_est_{t}", L["S2_est"]["verdict"])
V.set("ta11_Etrue_10_detected_max_high", C.f1(max(res["levels"][r]["E-true 0.1"]["detected_after"]["median"] for r in ("0.5", "0.7"))))
V.set("ta11_Etrue_10_quality_min_high", C.f1(min(res["levels"][r]["E-true 0.1"]["pass"]["all"] for r in ("0.5", "0.7"))))
C.write_table("TA11", ["ρ", "arm", "success at 0% (the originals' miss rate)", "success 2%", "success 5%", "success 10%", "detected after 2%", "5%", "10%",
                       "all four quality conditions pass, 2%", "5%", "10%"], rows,
              "Study 2: the edit curve (median over 8 keys, %); the pre-registered judgement point is 5%",
              ["Detection: attributed by the exact test at p ≤ 0.01. Quality: perplexity, seq-rep-4, length and embedding similarity against the owner's human-text bars; "
               "at 10% the perplexity condition fails for most texts at ρ ≥ 0.50, which is why removal of the evidence there does not count as success."])
p = V.save()
print("TA11 written; values:", p.name, len(V.d))
