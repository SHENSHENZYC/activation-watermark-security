"""TA9 — per-key view of the defence study (Appendix D): for each strength, the fixed key (detection, genuine FA, the
Route A′ cosine and forgery FA at n = 64 and 1,024, Study 2's scrub success), the context-hashed arms h = 1 and h = 4
(detection, genuine and control FA, forgery FA at n = 1,024, the per-context attacker's count-weighted cosine and
coverage at n = 1,024, scrub success, its difference from the fixed key, the perplexity ratio) and rotation (union and
single-key detection, union-test scrub success); the per-key calibration of the keyed tests beside S4's. Reads
study5_v0.1/results.json and study3_v0.1/results.json; asserts every median, the D2 and D3 summaries and the key counts
against the per-key records; writes build/TA9.md and build/values_tabA9.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA9")
r5 = C.load(C.OUT / "study5_v0.1" / "results.json")
r3 = C.load(C.OUT / "study3_v0.1" / "results.json")
K = [str(k) for k in C.KEYS]
rows = []


def med(xs):
    return float(np.median(xs))


def row(arm, rho, lab, vals, fmt, median=None):
    rows.append([arm, rho, lab] + [fmt(v) for v in vals] + [fmt(med(vals) if median is None else median)])


# calibration
g2_fixed = [r3["S4"]["G2"]["per_key_fpr_pct"][k] for k in K]
row("fixed key (h = 0; S4, Study 3)", "—", "FPR on pool A, % (G2 ≤ 3)", g2_fixed, C.f1)
for a in ("h1", "h4"):
    g2 = [r5["arms"][a]["calibration"]["G2"]["per_key_fpr_pct"][k] for k in K]
    cal = [int(k) for k, v in zip(K, g2) if v <= r5["arms"][a]["calibration"]["G2"]["max_pct"]]
    assert cal == r5["arms"][a]["calibration"]["G2"]["calibrated_keys"] and len(cal) == 8
    assert abs(np.mean(g2) - r5["arms"][a]["calibration"]["G1"]["pooled_fpr_pct"]) < 1e-9
    row(f"context-hashed, h = {r5['arms'][a]['h']}", "—", "FPR on pool A, % (G2 ≤ 3)", g2, C.f1)
    V.set(f"ta9_{a}_G2_min", C.f1(min(g2)))
    V.set(f"ta9_{a}_G2_max", C.f1(max(g2)))
    V.set(f"ta9_{a}_G1_pct", C.f2(r5["arms"][a]["calibration"]["G1"]["pooled_fpr_pct"]))
V.set("ta9_union_G1_pct", C.f2(r5["rotation"]["G1"]["pooled_fpr_pct"]))
assert r5["rotation"]["G1"]["pass"] is True

for rho in C.LEVELS2:
    t = C.tag(rho)
    F = r5["fixed"][rho]
    pk = F["per_key"]
    detect = [pk[k]["detect"] for k in K]
    ofa = [pk[k]["oracle_FA"] for k in K]
    assert np.allclose(ofa, F["oracle_FA"]["per_key"]) and C.chk(F["oracle_FA"])
    row("fixed key (h = 0)", C.rho_lab(rho), "S4 detection, %", detect, C.pct0)
    row("fixed key (h = 0)", C.rho_lab(rho), "genuine FA, %", ofa, C.pct0, F["oracle_FA"]["median"])
    for n in ("64", "1024"):
        cos = [pk[k]["cos_known"][n] for k in K]
        fa = [pk[k]["forge_FA"][n] for k in K]
        assert abs(med(cos) - F["recovery"][n]["median_cos_known"]) < 1e-9
        assert np.allclose(fa, F["forge_FA"][n]["per_key"]) and C.chk(F["forge_FA"][n])
        row("fixed key (h = 0)", C.rho_lab(rho), f"Route A′ cos(v̂, v), known layer, n = {int(n):,}", cos, C.f2)
        row("fixed key (h = 0)", C.rho_lab(rho), f"Route A′ forgery FA, %, n = {int(n):,}", fa, C.pct0, F["forge_FA"][n]["median"])
        V.set(f"ta9_fixed_{t}_n{n}_cos_min", C.f2(min(cos)))
        V.set(f"ta9_fixed_{t}_n{n}_cos_max", C.f2(max(cos)))
        V.set(f"ta9_fixed_{t}_n{n}_FA_min", C.pct0(min(fa)))
        V.set(f"ta9_fixed_{t}_n{n}_FA_max", C.pct0(max(fa)))
        V.set(f"ta9_fixed_{t}_n{n}_keys_ge_bar", sum(v >= F["P0"]["bar"] for v in fa))
    s2 = C.chk(F["s2_success"])
    row("fixed key (h = 0)", C.rho_lab(rho), "Study 2 scrub success (P-Qwen), %", s2, C.pct0, F["s2_success"]["median"])
    V.set(f"ta9_fixed_{t}_P0_bar", C.pct(F["P0"]["bar"]))
    for a in ("h1", "h4"):
        L = r5["arms"][a]["levels"][rho]
        A = L["per_key"]
        name = f"context-hashed, h = {r5['arms'][a]['h']}"
        det = [A[k]["detect"] for k in K]
        assert np.allclose(det, L["detection"]["per_key"]) and C.chk(L["detection"])
        gfa = [A[k]["genuine_FA"] for k in K]
        cfa = [A[k]["control_FA"] for k in K]
        assert np.allclose(gfa, L["genuine_FA"]["per_key"]) and np.allclose(cfa, L["control_FA"]["per_key"])
        ffa = [A[k]["forge_FA"]["1024"] for k in K]
        assert np.allclose(ffa, L["forge_FA"]["1024"]["per_key"]) and C.chk(L["forge_FA"]["1024"])
        cosw = [A[k]["attacker"]["1024"]["cos_weighted"] for k in K]
        cov = [A[k]["attacker"]["1024"]["coverage_genuine"] for k in K]
        assert abs(med(cosw) - L["recovery"]["1024"]["cos_weighted"]) < 1e-9 and abs(med(cov) - L["recovery"]["1024"]["coverage"]) < 1e-9
        ps = [A[k]["para_success"] for k in K]
        assert np.allclose(ps, L["para_success"]["per_key"]) and C.chk(L["para_success"])
        fs2 = [A[k]["fixed_s2_success"] for k in K]
        assert np.allclose(fs2, s2)
        d = [100 * (p - q) for p, q in zip(ps, fs2)]
        assert abs(med(d) - L["D2"]["median_diff_points"]) < 1e-6 and sum(x >= 20 for x in d) == L["D2"]["n_keys_ge_20_points"]
        ppl = [A[k]["ppl_ratio_median"] for k in K]
        assert abs(med(ppl) - L["D3"]["median_ratio"]) < 1e-9 and sum(x > 1.10 for x in ppl) == L["D3"]["n_keys_above_1.10"]
        row(name, C.rho_lab(rho), "keyed-test detection, %", det, C.pct0, L["detection"]["median"])
        row(name, C.rho_lab(rho), "genuine FA, %", gfa, C.pct0, L["genuine_FA"]["median"])
        row(name, C.rho_lab(rho), "control (random-key) FA, %", cfa, C.pct0, L["control_FA"]["median"])
        row(name, C.rho_lab(rho), "per-context forgery FA, %, n = 1,024", ffa, C.pct0, L["forge_FA"]["1024"]["median"])
        row(name, C.rho_lab(rho), "attacker's count-weighted cos, n = 1,024", cosw, C.f3)
        row(name, C.rho_lab(rho), "coverage of a genuine text's positions, n = 1,024", cov, C.f3)
        row(name, C.rho_lab(rho), "scrub success (P-Qwen), %", ps, C.pct0, L["para_success"]["median"])
        row(name, C.rho_lab(rho), "d = success − the fixed key's, points", d, lambda x: f"{x:+.0f}", L["D2"]["median_diff_points"])
        row(name, C.rho_lab(rho), "perplexity ratio to the fixed key (median)", ppl, C.f2, L["D3"]["median_ratio"])
        V.set(f"ta9_{a}_{t}_FA1024_max", C.pct0(max(ffa)))
        V.set(f"ta9_{a}_{t}_FA1024_min", C.pct0(min(ffa)))
        V.set(f"ta9_{a}_{t}_d_min", f"{min(d):+.0f}")
        V.set(f"ta9_{a}_{t}_d_max", f"{max(d):+.0f}")
        V.set(f"ta9_{a}_{t}_d_keys_ge_20", L["D2"]["n_keys_ge_20_points"])
        V.set(f"ta9_{a}_{t}_d_keys_le_0", sum(x <= 0 for x in d))
        V.set(f"ta9_{a}_{t}_ppl_min", C.f2(min(ppl)))
        V.set(f"ta9_{a}_{t}_ppl_max", C.f2(max(ppl)))
        V.set(f"ta9_{a}_{t}_cosw_max", C.f3(max(cosw)))
        V.set(f"ta9_{a}_{t}_cov_med", C.f3(med(cov)))
        V.set(f"ta9_{a}_{t}_detect_min", C.pct0(min(det)))
        V.set(f"ta9_{a}_{t}_D2", L["D2"]["verdict"])
        V.set(f"ta9_{a}_{t}_D3", L["D3"]["verdict"])
    R = r5["rotation"][rho]
    ud = [R["per_key"][k]["union_detect"] for k in K]
    sd = [R["per_key"][k]["single_detect"] for k in K]
    us = [R["per_key"][k]["union_success"] for k in K]
    assert np.allclose(ud, R["union_detection"]["per_key"]) and C.chk(R["union_detection"]) and np.allclose(sd, R["single_detection"]["per_key"])
    assert abs(100 * med(ud) - R["P1"]["median_pct"]) < 1e-9
    d_rot = [100 * (u - q) for u, q in zip(us, s2)]
    assert abs(med(d_rot) - R["D2"]["median_diff_points"]) < 1e-6
    row("rotation (K = 8)", C.rho_lab(rho), "union-test detection, %", ud, C.pct0, R["union_detection"]["median"])
    row("rotation (K = 8)", C.rho_lab(rho), "single-key detection of the same texts, %", sd, C.pct0, R["single_detection"]["median"])
    row("rotation (K = 8)", C.rho_lab(rho), "union-test scrub success on Study 2's paraphrases, %", us, C.pct0)
    row("rotation (K = 8)", C.rho_lab(rho), "d = union-test success − the fixed key's, points", d_rot, lambda x: f"{x:+.0f}", R["D2"]["median_diff_points"])
    V.set(f"ta9_rot_{t}_union_detect_min", C.pct0(min(ud)))
    V.set(f"ta9_rot_{t}_union_detect_max", C.pct0(max(ud)))
    V.set(f"ta9_rot_{t}_union_success_med", C.pct0(med(us)))
    V.set(f"ta9_rot_{t}_d_med", f"{R['D2']['median_diff_points']:+.0f}")
    V.set(f"ta9_rot_{t}_d_max", f"{max(d_rot):+.0f}")
    V.set(f"ta9_rot_{t}_key1002_union_detect", C.pct0(ud[1]))
C.write_table("TA9", ["arm", "ρ", "reading"] + [str(k) for k in C.KEYS] + ["median"], rows,
              "Study 5: the per-key view behind every median (keys 1001–1008; every key calibrated under every test)",
              ["The fixed key's detection and FA are Study 5's re-scoring of Study 1's texts with S4; its Study 2 scrub success is Study 2's locked value for the same key "
               "and strength (asserted equal). d is the keyed arm's scrub success minus the fixed key's, per key; D2 takes its median with a cluster-bootstrap interval. "
               "Rotation's texts are the fixed key's, so its quality is unchanged by construction and its paraphrases are Study 2's, scored by the union test."])
p = V.save()
print("TA9 written; values:", p.name, len(V.d))
