"""TA7 — per-key exact acceptance (S4) on the study keys (Appendix D): (a) per key and strength, the genuine texts, the
random-key control, v0.2's Route B at n = 1,024 and v0.4's Route A and B at n = 256, with the probe's median beside the
exact test's; (b) per-key false-positive rates of S4 and S3 on unwatermarked model text (G2) and human continuations
(H1). Reads study3_v0.1/results.json; re-counts the ≥ 50% cells and asserts medians; writes build/TA7a.md, TA7b.md and
build/values_tabA7.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA7")
res = C.load(C.OUT / "study3_v0.1" / "results.json")
assert res["primary"] == "S4" and res["alpha"] == 0.01
P, P3 = res["S4"], res["S3"]
rows, hi_cells = [], []
for rho in C.LEVELS4:
    L, t = P["levels"][rho], C.tag(rho)
    sets = [("oracle", "genuine (oracle)"), ("random", "random key"), ("v02_B_n1024", "v0.2 Route B, n = 1,024")]
    if rho != "0.25":
        sets += [("v04_A_n256", "v0.4 Route A, n = 256"), ("v04_B_n256", "v0.4 Route B, n = 256")]
    else:
        sets += [("v02_A_n1024", "v0.2 Route A, n = 1,024")]
    for s, lab in sets:
        pk = C.chk(L[s]["acceptance"])
        if s not in ("oracle", "random"):
            assert np.allclose(pk, L[s]["acceptance_per_key"])
            for k, v in zip(C.KEYS, pk):
                if v >= 0.5:
                    hi_cells.append(f"{lab.replace(', n = ', ' at n = ')}, key {k} at ρ = {C.rho_lab(rho)} ({C.pct0(v)}%)")
        rows.append([C.rho_lab(rho), lab] + [C.pct0(v) for v in pk] + [C.pct(L[s]["acceptance"]["median"]), C.pct(L[s]["probe_acceptance_median"])])
        V.set(f"ta7_{s}_{t}_min", C.pct0(min(pk)))
        V.set(f"ta7_{s}_{t}_max", C.pct0(max(pk)))
        V.set(f"ta7_{s}_{t}_keys_ge_50", sum(v >= 0.5 for v in pk))
V.set("ta7_hi_cells_v04_n256", "; ".join(c for c in hi_cells if c.startswith("v0.4")))
V.set("ta7_hi_cells_v04_n256_count", sum(c.startswith("v0.4") for c in hi_cells))
V.set("ta7_hi_cells_v02_B_n1024_count", sum(c.startswith("v0.2 Route B") for c in hi_cells))
# key 1002 at 0.70 and its neighbours
o7 = C.chk(P["levels"]["0.7"]["oracle"]["acceptance"])
V.set("ta7_key1002_07_tpr", C.pct0(o7[1]))
V.set("ta7_others_07_tpr_min", C.pct0(min(v for i, v in enumerate(o7) if i != 1)))
V.set("ta7_key1004_05_A_n256", C.pct0(C.chk(P["levels"]["0.5"]["v04_A_n256"]["acceptance"])[3]))
V.set("ta7_key1004_07_A_n256", C.pct0(C.chk(P["levels"]["0.7"]["v04_A_n256"]["acceptance"])[3]))
V.set("ta7_key1004_07_B_n256", C.pct0(C.chk(P["levels"]["0.7"]["v04_B_n256"]["acceptance"])[3]))
V.set("ta7_key1003_07_B_n256", C.pct0(C.chk(P["levels"]["0.7"]["v04_B_n256"]["acceptance"])[2]))
V.set("ta7_key1006_035_B_n256", C.pct0(C.chk(P["levels"]["0.35"]["v04_B_n256"]["acceptance"])[5]))
C.write_table("TA7a", ["ρ", "texts"] + [str(k) for k in C.KEYS] + ["median (exact)", "the probe's median on the same texts"], rows,
              "Study 3: per-key acceptance by the exact test (S4, p ≤ 0.01, %) on the study keys, with the owner's probe's median beside it",
              ["Every key is calibrated (Table TA7b), so every key counts. The probe's per-key rates were not stored; its median is Study 1's on the same texts."])
# (b) per-key FPR for S4 and S3
rows_b = []
for nm, Q in (("S4 (primary)", P), ("S3 (secondary)", P3)):
    g2 = [Q["G2"]["per_key_fpr_pct"][str(k)] for k in C.KEYS]
    h1 = [Q["H1"]["per_key_fpr_pct"][str(k)] for k in C.KEYS]
    assert abs(np.mean(g2) - Q["G1"]["pooled_fpr_pct"]) < 1e-9 and abs(np.mean(h1) - Q["H1"]["pooled_fpr_pct"]) < 1e-9
    cal = [k for k, v in zip(C.KEYS, g2) if v <= Q["G2"]["max_pct"]]
    assert cal == Q["G2"]["calibrated_keys"] and len(cal) == Q["G2"]["n_calibrated"]
    rows_b.append([nm, "unwatermarked model text (pool A), G2"] + [C.f1(v) for v in g2] + [C.f2(Q["G1"]["pooled_fpr_pct"]), f"{8 - len(cal)}"])
    rows_b.append([nm, "human continuations (pool A), H1"] + [C.f1(v) for v in h1] + [C.f2(Q["H1"]["pooled_fpr_pct"]), f"{Q['H1']['n_keys_above_max']}"])
    short = nm.split()[0]
    V.set(f"ta7_{short}_G2_min", C.f1(min(g2)))
    V.set(f"ta7_{short}_G2_max", C.f1(max(g2)))
    V.set(f"ta7_{short}_n_calibrated", len(cal))
    V.set(f"ta7_{short}_H1_max", C.f1(max(h1)))
V.set("ta7_S3_key1002_G2", C.f1(P3["G2"]["per_key_fpr_pct"]["1002"]))
V.set("ta7_S4_key1002_G2", C.f1(P["G2"]["per_key_fpr_pct"]["1002"]))
C.write_table("TA7b", ["statistic", "null texts"] + [str(k) for k in C.KEYS] + ["pooled", "keys above 3%"], rows_b,
              "Study 3: per-key false-positive rates at p ≤ 0.01 (%) on 1,000 unwatermarked model texts and 1,000 human continuations per key",
              ["G2 excludes a key whose rate on model text exceeds 3%; S3 (the unstandardised gradient) loses key 1002 by that rule, S4 keeps all eight."])
p = V.save()
print("TA7 written; values:", p.name, len(V.d))
