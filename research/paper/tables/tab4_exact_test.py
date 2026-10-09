"""T4 — the exact key test on the study keys (§5.3): per strength, genuine detection by the exact test beside the owner's
probe on the same texts (P1, E1), random-key attribution (X3), Study 1 v0.4's forgeries re-scored by the exact test
beside the probe's FA on the same texts with the X1 bar and verdicts; the calibration line (G1, G2, H1) and the stricter
level. Reads study3_v0.1/results.json; re-computes pooled rates, calibrated counts, medians, the E1, X1 and X3 verdicts
and the key-leakage lens (cells accepted ≥ 50%; Spearman of exact acceptance against the recovered cosine) from the
per-key records, and asserts them; writes build/T4.md and build/values_tab4.json.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tab4")
res = C.load(C.OUT / "study3_v0.1" / "results.json")
assert res["primary"] == "S4" and res["alpha"] == 0.01 and res["M"] == 999
P = res["S4"]
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
LATE = ["0.35", "0.5", "0.7"]
T = lambda rho: rho.replace(".", "")  # noqa: E731
SETS = {"0.25": [f"v02_{r}_n{n}" for r in "AB" for n in (64, 256, 1024)]}
for rho in LATE:
    SETS[rho] = [f"v02_{r}_n{n}" for r in "AB" for n in (64, 256, 1024)] + [f"{v}_{r}_n{n}" for v in ("v03", "v04") for r in "AB" for n in (64, 256)]


def chk(d):
    assert len(d["per_key"]) == 8 and abs(float(np.median(d["per_key"])) - d["median"]) < 1e-12
    assert d["ci95"][0] <= d["median"] + 1e-12 and d["median"] - 1e-12 <= d["ci95"][1]
    return d


# calibration
per = {int(k): v for k, v in P["G2"]["per_key_fpr_pct"].items()}
assert abs(np.mean(list(per.values())) - P["G1"]["pooled_fpr_pct"]) < 1e-9 and P["G1"]["pass"] is True
assert sorted(k for k, v in per.items() if v <= P["G2"]["max_pct"]) == sorted(P["G2"]["calibrated_keys"]) and P["G2"]["n_calibrated"] == 8
hper = {int(k): v for k, v in P["H1"]["per_key_fpr_pct"].items()}
assert abs(np.mean(list(hper.values())) - P["H1"]["pooled_fpr_pct"]) < 1e-9 and P["H1"]["n_keys_above_max"] == 0
V.set("s3x_G1_pct", C.f2(P["G1"]["pooled_fpr_pct"]))
V.set("s3x_G2_range", f"{C.f1(min(per.values()))}–{C.f1(max(per.values()))}")
V.set("s3x_H1_pct", C.f2(P["H1"]["pooled_fpr_pct"]))
V.set("s3x_H1_max_pct", C.f1(max(hper.values())))
V.set("s3x_a001_model_pct", C.f2(P["alpha_0.001"]["pooled_fpr_model_pct"]))
V.set("s3x_a001_human_pct", C.f2(P["alpha_0.001"]["pooled_fpr_human_pct"]))

rows, cos_by_route, acc_by_route, cells, cells_ge50 = [], {"A": [], "B": []}, {"A": [], "B": []}, 0, 0
for rho in LEVELS:
    L, t = P["levels"][rho], T(rho)
    chk(L["oracle"]["acceptance"])
    chk(L["random"]["acceptance"])
    chk(L["oracle"]["exact_FA"])
    chk(L["random"]["exact_FA"])
    assert L["P1"]["pass"] is (L["oracle"]["acceptance"]["median"] >= L["P1"]["min"]) and L["P1"]["pass"]
    e1 = L["E1"]
    verdict = "exact test more powerful" if e1["ci95"][0] > 0 else ("exact test less powerful" if e1["ci95"][1] < 0 else "no clear difference")
    assert verdict == e1["verdict"], rho
    bar = 0.5 * L["oracle"]["exact_FA"]["median"]
    assert abs(L["X1_bar"] - bar) < 1e-12
    assert L["X3_fluent_generic_steering_suffices"] is (L["random"]["exact_FA"]["median"] >= bar)
    # key-leakage lens: every forgery set's per-key exact acceptance beside the attacker's recovered cosine
    for s in SETS[rho]:
        d = L[s]
        chk(d["acceptance"])
        chk(d["exact_FA"])
        assert len(d["acceptance_per_key"]) == 8 and len(d["cos_to_key_per_key"]) == 8
        assert np.allclose(d["acceptance_per_key"], d["acceptance"]["per_key"])
        route = s.split("_")[1]
        cos_by_route[route] += d["cos_to_key_per_key"]
        acc_by_route[route] += d["acceptance_per_key"]
        cells += 8
        cells_ge50 += sum(a >= 0.5 for a in d["acceptance_per_key"])
    V.set(f"s3x_oracle_tpr_{t}", C.pct(L["oracle"]["acceptance"]["median"]))
    V.set(f"s3x_oracle_tpr_ci_{t}", C.pct_ci(L["oracle"]["acceptance"]))
    V.set(f"s3x_probe_tpr_{t}", C.pct(L["oracle"]["probe_acceptance_median"]))
    V.set(f"s3x_E1_{t}", f"{100 * e1['median_diff_exact_minus_probe']:+.1f} [{100 * e1['ci95'][0]:+.1f}, {100 * e1['ci95'][1]:+.1f}]")
    V.set(f"s3x_E1_verdict_{t}", e1["verdict"])
    V.set(f"s3x_random_exact_{t}", C.pct(L["random"]["acceptance"]["median"]))
    V.set(f"s3x_random_probe_{t}", C.pct(L["random"]["probe_acceptance_median"]))
    V.set(f"s3x_oracle_a001_{t}", C.pct(L["oracle"]["acceptance_0.001_median"]))
    V.set(f"s3x_oracle_exactFA_{t}", C.pct(L["oracle"]["exact_FA"]["median"]))
    V.set(f"s3x_X1_bar_{t}", C.pct(bar))
    V.set(f"s3x_X3_{t}", "yes" if L["X3_fluent_generic_steering_suffices"] else "no")
    V.set(f"s3x_v02_B_n1024_probe_acc_{t}", C.pct(L["v02_B_n1024"]["probe_acceptance_median"]))
    V.set(f"s3x_v02_B_n1024_exact_acc_{t}", C.pct(L["v02_B_n1024"]["acceptance"]["median"]))
    row = [rho, C.pct_ci(L["oracle"]["acceptance"]), C.pct(L["oracle"]["probe_acceptance_median"]), f"{V.d[f's3x_E1_{t}']}: {e1['verdict']}",
           f"{C.pct(L['random']['acceptance']['median'])} / {C.pct(L['random']['probe_acceptance_median'])}", C.pct(L["oracle"]["acceptance_0.001_median"])]
    if rho in LATE:
        x1 = L["X1"]
        for route in "AB":
            sets = {n: L[f"v04_{route}_n{n}"]["exact_FA"] for n in (64, 256)}
            prac = [n for n, s in sets.items() if s["median"] >= bar and s["ci95"][0] > L["random"]["exact_FA"]["ci95"][1]]
            got = f"practical (n={prac[0]})" if prac else ("not practical" if all(s["ci95"][1] < bar for s in sets.values()) else "inconclusive")
            assert got == x1[route], (rho, route, got, x1[route])
            V.set(f"s3x_X1_{route}_{t}", x1[route])
            for n in (64, 256):
                d = L[f"v04_{route}_n{n}"]
                V.set(f"s3x_v04_{route}_n{n}_exactFA_{t}", C.pct_ci(d["exact_FA"]))
                V.set(f"s3x_v04_{route}_n{n}_exactFA_med_{t}", C.pct(d["exact_FA"]["median"]))
                V.set(f"s3x_v04_{route}_n{n}_exactFA_hi_{t}", C.pct(d["exact_FA"]["ci95"][1]))
                V.set(f"s3x_v04_{route}_n{n}_probeFA_{t}", C.pct(d["probe_FA_median"]))
                V.set(f"s3x_v04_{route}_n{n}_exact_acc_{t}", C.pct(d["acceptance"]["median"]))
                V.set(f"s3x_v04_{route}_n{n}_probe_acc_{t}", C.pct(d["probe_acceptance_median"]))
        row += [f"{C.pct_ci(L['v04_A_n256']['exact_FA'])} (probe {C.pct(L['v04_A_n256']['probe_FA_median'])})",
                f"{C.pct_ci(L['v04_B_n256']['exact_FA'])} (probe {C.pct(L['v04_B_n256']['probe_FA_median'])})", C.pct(bar), f"A: {x1['A']}; B: {x1['B']}",
                "yes" if L["X3_fluent_generic_steering_suffices"] else "no"]
    else:
        row += ["— (no v0.4 forgeries at 0.25)", "—", C.pct(bar), "—", "yes" if L["X3_fluent_generic_steering_suffices"] else "no"]
    rows.append(row)

assert cells == 384, cells
V.set("s3x_leak_cells_total", cells)
V.set("s3x_leak_cells_ge50", cells_ge50)
for route in "AB":
    rho_s, _ = spearmanr(cos_by_route[route], acc_by_route[route])
    V.set(f"s3x_leak_spearman_{route}", C.f2(rho_s))
    V.set(f"s3x_leak_n_{route}", len(cos_by_route[route]))
late_fa = [P["levels"][r][f"v04_{ro}_n{n}"]["exact_FA"]["median"] for r in LATE for ro in "AB" for n in (64, 256)]
V.set("s3x_v04_exactFA_late_min", C.pct(min(late_fa)))
V.set("s3x_v04_exactFA_late_max", C.pct(max(late_fa)))
V.set("s3x_X1_bar_min", C.pct(min(P["levels"][r]["X1_bar"] for r in LATE)))
V.set("s3x_X1_bar_max", C.pct(max(P["levels"][r]["X1_bar"] for r in LATE)))
V.set("s3x_oracle_exactFA_late_min", C.pct(min(P["levels"][r]["oracle"]["exact_FA"]["median"] for r in LATE)))
V.set("s3x_oracle_exactFA_late_max", C.pct(max(P["levels"][r]["oracle"]["exact_FA"]["median"] for r in LATE)))
V.set("s3x_oracle_tpr_min", C.pct(min(P["levels"][r]["oracle"]["acceptance"]["median"] for r in LEVELS)))
V.set("s3x_oracle_tpr_max", C.pct(max(P["levels"][r]["oracle"]["acceptance"]["median"] for r in LEVELS)))
V.set("s3x_random_exact_max", C.pct(max(P["levels"][r]["random"]["acceptance"]["median"] for r in LEVELS)))
V.set("s3x_random_probe_max", C.pct(max(P["levels"][r]["random"]["probe_acceptance_median"] for r in LEVELS)))
V.set("s3x_key1002_07_tpr", C.pct(P["levels"]["0.7"]["oracle"]["acceptance"]["per_key"][1]))
V.set("s3x_key1002_fpr_pct", C.f1(per[1002]))
others07 = [v for i, v in enumerate(P["levels"]["0.7"]["oracle"]["acceptance"]["per_key"]) if i != 1]
V.set("s3x_others_07_tpr_min", C.pct(min(others07)))
V.set("s3x_narrowest_A_07_n64_hi", C.pct(P["levels"]["0.7"]["v04_A_n64"]["exact_FA"]["ci95"][1]))

C.write_table("T4", ["ρ", "genuine texts attributed, exact test (%) [95% CI]", "the probe on the same texts (%)", "E1: exact − probe, points [95% CI]: verdict",
                     "random-key texts attributed: exact / probe (%)", "genuine at p ≤ 0.001 (%)", "v0.4 Route A, n = 256: exact FA (%) [95% CI] (probe FA)",
                     "v0.4 Route B, n = 256: exact FA (%) [95% CI] (probe FA)", "X1 bar: half the genuine exact FA (%)", "X1 verdicts", "X3 generic steering suffices"],
              rows, "The exact key test (S4) on the study keys: detection, random-key attribution and Study 1's forgeries re-scored (medians over 8 keys; 256-token texts; p ≤ 0.01 with 999 null keys)",
              [f"Calibration: pooled false-positive rate {V.d['s3x_G1_pct']}% on 8 keys × 1,000 unwatermarked model texts (G1; range 0.3–2.5); every key calibrated at "
               f"{V.d['s3x_G2_range']}% (G2 bar 3%); {V.d['s3x_H1_pct']}% on 1,000 human continuations (H1; highest key {V.d['s3x_H1_max_pct']}%); at p ≤ 0.001 with 9,999 null keys "
               f"{V.d['s3x_a001_model_pct']}% on model text and {V.d['s3x_a001_human_pct']}% on human text. Exact FA: attributed by the exact test and fluent by v0.4's definition. "
               "X1 and X3 have the form of v0.4's F1 and F3 with the exact test in place of the probe. The probe's numbers are Study 1's, on the same texts."])
p = V.save()
print("T4 written; values:", p.name, len(V.d))
