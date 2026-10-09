"""T5 — scrubbing under the exact test at matched quality (§5.5): per strength, detection before (P1), and for each method
(P-Qwen, P-Phi, E-true, E-est and E-rand at 5% of the tokens) the detection after, the share passing all quality
conditions, the success with its interval, the keys at or above 50% and the verdict; the C1 contrast (E-est − E-rand);
the secondary readings the prose quotes. Reads study2_v0.1/results.json (rates are percentages there); re-computes
pooled rates, calibrated counts, medians, key counts and the S1, S2 and C1 verdicts from the rules, and asserts them;
writes build/T5.md and build/values_tab5.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tab5")
res = C.load(C.OUT / "study2_v0.1" / "results.json")
assert res["dry"] is False
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
T = lambda rho: rho.replace(".", "")  # noqa: E731
BAR, B5 = 50.0, "0.05"


def ci(d):
    return f"{C.f1(d['median'])} [{C.f1(d['ci95'][0])}, {C.f1(d['ci95'][1])}]"


def chk(d, n_keys=8):
    pk = list(d["per_key"].values())
    assert len(pk) == n_keys and abs(float(np.median(pk)) - d["median"]) < 1e-9
    assert d["ci95"][0] <= d["median"] + 1e-9 and d["median"] - 1e-9 <= d["ci95"][1]
    if "keys_ge_50" in d:
        assert d["keys_ge_50"] == sum(v >= BAR for v in pk)
    return d


def verdict(s, comp):
    """S1/S2: effective if the median success is at least 50% and its lower bound exceeds the comparator's upper bound;
    not effective if the upper bound is below 50%; otherwise inconclusive."""
    if s["median"] >= BAR and s["ci95"][0] > comp["ci95"][1]:
        return "effective"
    if s["ci95"][1] < BAR:
        return "not effective"
    return "inconclusive"


for m in ("qwen", "phi"):
    cal = res["calibration"][m]
    per = {int(k): v for k, v in cal["G2"]["per_key_fpr_pct"].items()}
    assert abs(np.mean(list(per.values())) - cal["G1"]["pooled_fpr_pct"]) < 1e-9 and cal["G1"]["pass"] is True
    assert cal["G2"]["n_calibrated"] == sum(v <= cal["G2"].get("max_pct", 3.0) for v in per.values()) == 8
    V.set(f"s2_G1_{m}_pct", C.f2(cal["G1"]["pooled_fpr_pct"]))
    V.set(f"s2_G2_{m}_range", f"{C.f1(min(per.values()))}–{C.f1(max(per.values()))}")
    fk = cal["fresh_keys"]
    V.set(f"s2_fresh_{m}_mean_pct", C.f2(fk["mean_fpr_pct"]))
    V.set(f"s2_fresh_{m}_share_above3_pct", C.f1(100 * fk["share_above_3pct"]))
    V.set(f"s2_fresh_{m}_max_pct", C.f1(fk["max_fpr_pct"]))
    V.set(f"s2_probe_fpr_para_{m}_pct", C.f1(cal["probe_fpr_on_paraphrased_A2_pct"]["median"]))

rows = []
NAMES = {"S1_qwen": "P-Qwen paraphrase", "S1_phi": "P-Phi paraphrase", "E-true": "E-true: 5% edits, true key", "E-est": "E-est: 5% edits, Route A estimate", "E-rand": "E-rand: 5% edits, random"}
for rho in LEVELS:
    L, t = res["levels"][rho], T(rho)
    chk(L["P1"]["detected_before"])
    assert L["P1"]["pass"] is (L["P1"]["detected_before"]["median"] >= 20)
    V.set(f"s2_P1_{t}", C.f1(L["P1"]["detected_before"]["median"]))
    rows.append([rho, "unscrubbed originals", C.f1(L["P1"]["detected_before"]["median"]), "—", "—", "—", "P1 pass" if L["P1"]["pass"] else "P1 fail"])
    for m in ("qwen", "phi"):
        S = L[f"S1_{m}"]
        chk(S["success"])
        chk(S["originals_miss"])
        chk(S["detected_after"])
        assert verdict(S["success"], S["originals_miss"]) == S["verdict"], (rho, m)
        assert S["keys_success_ge_50"] == S["success"]["keys_ge_50"]
        rows.append([rho, NAMES[f"S1_{m}"], C.f1(S["detected_after"]["median"]), C.f1(S["pass"]["all"]), ci(S["success"]), f"{S['keys_success_ge_50']} of 8",
                     f"S1 {S['verdict']} (originals' miss {ci(S['originals_miss'])})"])
        V.set(f"s2_S1_{m}_{t}_success", ci(S["success"]))
        V.set(f"s2_S1_{m}_{t}_success_med", C.f1(S["success"]["median"]))
        V.set(f"s2_S1_{m}_{t}_verdict", S["verdict"])
        V.set(f"s2_S1_{m}_{t}_keys", S["keys_success_ge_50"])
        V.set(f"s2_S1_{m}_{t}_detected_after", C.f1(S["detected_after"]["median"]))
        V.set(f"s2_S1_{m}_{t}_miss", ci(S["originals_miss"]))
        V.set(f"s2_S1_{m}_{t}_pass_all", C.f1(S["pass"]["all"]))
    rand = chk(L[f"E-rand {B5}"]["success"])
    for a in ("true", "est"):
        S = L[f"E-{a} {B5}"]
        chk(S["success"])
        chk(S["detected_after"])
        v = verdict(S["success"], rand)
        assert v == L[f"S2_{a}"]["verdict"] and L[f"S2_{a}"]["keys_success_ge_50"] == S["success"]["keys_ge_50"], (rho, a, v)
        rows.append([rho, NAMES[f"E-{a}"], C.f1(S["detected_after"]["median"]), C.f1(S["pass"]["all"]), ci(S["success"]), f"{S['success']['keys_ge_50']} of 8", f"S2 {v}"])
        V.set(f"s2_E{a}_{t}_success", ci(S["success"]))
        V.set(f"s2_E{a}_{t}_success_med", C.f1(S["success"]["median"]))
        V.set(f"s2_S2_{a}_{t}_verdict", v)
        V.set(f"s2_S2_{a}_{t}_keys", S["success"]["keys_ge_50"])
        V.set(f"s2_E{a}_{t}_detected_after", C.f1(S["detected_after"]["median"]))
    Sr = L[f"E-rand {B5}"]
    c1 = L["C1"]
    c1v = "the estimate helps" if c1["ci95"][0] > 0 else ("random edits do better" if c1["ci95"][1] < 0 else "no clear difference")
    assert c1v == c1["verdict"], rho
    pk = list(c1["per_key"].values())
    assert abs(float(np.median(pk)) - c1["median"]) < 1e-9
    rows.append([rho, NAMES["E-rand"], C.f1(Sr["detected_after"]["median"]), C.f1(Sr["pass"]["all"]), ci(rand), f"{rand['keys_ge_50']} of 8",
                 f"C1 E-est − E-rand: {c1['median']:+.1f} [{c1['ci95'][0]:+.1f}, {c1['ci95'][1]:+.1f}]: {c1v}"])
    V.set(f"s2_Erand_{t}_success", ci(rand))
    V.set(f"s2_Erand_{t}_success_med", C.f1(rand["median"]))
    V.set(f"s2_C1_{t}", f"{c1['median']:+.1f} [{c1['ci95'][0]:+.1f}, {c1['ci95'][1]:+.1f}]")
    V.set(f"s2_C1_{t}_verdict", c1v)
    e10 = L["E-true 0.1"]
    V.set(f"s2_Etrue10_{t}_detected_after", C.f1(e10["detected_after"]["median"]))
    V.set(f"s2_Etrue10_{t}_ppl_pass", C.f1(e10["pass"]["ppl"]))
    V.set(f"s2_Etrue10_{t}_success", C.f1(e10["success"]["median"]))

sec = res["secondary"]
lm = [v for m in ("qwen", "phi") for v in sec["length_matched"][m].values()]
V.set("s2_lm_min", C.f1(min(lm)))
V.set("s2_lm_max", C.f1(max(lm)))
hi = ["0.5", "0.7"]
V.set("s2_probe_para_hi_min", C.f1(min(sec["probe"][f"para_{m}_gen"][r] for m in ("qwen", "phi") for r in hi)))
V.set("s2_probe_para_hi_max", C.f1(max(sec["probe"][f"para_{m}_gen"][r] for m in ("qwen", "phi") for r in hi)))
V.set("s2_S4_para_hi_min", C.f1(min(res["levels"][r][f"S1_{m}"]["detected_after"]["median"] for m in ("qwen", "phi") for r in hi)))
V.set("s2_S4_para_hi_max", C.f1(max(res["levels"][r][f"S1_{m}"]["detected_after"]["median"] for m in ("qwen", "phi") for r in hi)))
V.set("s2_Eest_success_min", C.f1(min(res["levels"][r][f"E-est {B5}"]["success"]["median"] for r in LEVELS)))
V.set("s2_Eest_success_max", C.f1(max(res["levels"][r][f"E-est {B5}"]["success"]["median"] for r in LEVELS)))
V.set("s2_Erand_success_max", C.f1(max(res["levels"][r][f"E-rand {B5}"]["success"]["median"] for r in LEVELS)))
V.set("s2_key1002_07_detected_before", C.f1(res["levels"]["0.7"]["P1"]["detected_before"]["per_key"]["1002"]))
V.set("s2_key1002_07_Erand_success", C.f1(res["levels"]["0.7"][f"E-rand {B5}"]["success"]["per_key"]["1002"]))
V.set("s2_others_07_Erand_success_max", C.f1(max(v for k, v in res["levels"]["0.7"][f"E-rand {B5}"]["success"]["per_key"].items() if k != "1002")))
V.set("s2_leak_spearman", C.f2(sec["key_leakage"]["spearman_success_vs_cos"]))
V.set("s2_pooled4_qwen_025", C.f1(sec["pooled_4"]["para_qwen_gen"]["0.25"]))
V.set("s2_pooled4_qwen_07", C.f1(sec["pooled_4"]["para_qwen_gen"]["0.7"]))
V.set("s2_bar", f"{BAR:.0f}")

_p1 = [res["levels"][r]["P1"]["detected_before"]["median"] for r in LEVELS]
V.set("s2_P1_min", C.f1(min(_p1)))
V.set("s2_P1_max", C.f1(max(_p1)))

C.write_table("T5", ["ρ", "method", "detected after (%)", "all four quality conditions pass (%)", "scrub success (%) [95% CI]", "keys ≥ 50%", "pre-registered verdict (comparator)"],
              rows, "Scrubbing the fixed key's evidence under the exact test at matched quality (Study 2; medians over 8 keys; 100 genuine texts per key and strength)",
              [f"Success: not attributed by the exact test at p ≤ 0.01 and fluency, repetition, length and meaning within the owner's bars (§4). S1 and S2: effective if the median "
               f"success is at least {BAR:.0f}% and its lower bound exceeds the comparator's upper bound (the originals' miss rate for paraphrase; E-rand for the edits); not "
               f"effective if the upper bound is below {BAR:.0f}%; otherwise inconclusive. C1 is the paired difference E-est − E-rand over keys. Calibration after paraphrase: pooled "
               f"false-positive rate {V.d['s2_G1_qwen_pct']}% (P-Qwen) and {V.d['s2_G1_phi_pct']}% (P-Phi) on 8 keys × 1,000 paraphrased unwatermarked texts; every key calibrated "
               f"({V.d['s2_G2_qwen_range']}% and {V.d['s2_G2_phi_range']}%)."])
p = V.save()
print("T5 written; values:", p.name, len(V.d))
