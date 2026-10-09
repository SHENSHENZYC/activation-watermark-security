"""T6 — the fixed key and the keyed arms (§5.4, §5.6): (a) detection (P1) and stealing against the budget n (P0 for the
fixed key under Route A′; D1 for the context-hashed arms h = 1, 4 and for rotation among 8 keys under the naive and the
clustering attacker), with a final labelled post-hoc row from the rotation addendum (forging with every cluster at
ρ = 0.35); (b) the robustness cost (D2: scrub success after P-Qwen beside the fixed key's, the paired difference d) and
the quality cost (D3: perplexity ratio to the fixed key, keys above 1.10). Reads study5_v0.1/results.json and
ADDENDUM_ROTATION.json; re-computes every median, calibrated count and key count from the per-key records, re-derives
P0, D1, D2 and D3 from the rules and the addendum's three selection rules from its per-cluster records, and asserts
them; writes build/T6a.md, build/T6b.md and build/values_tab6.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tab6")
res = C.load(C.OUT / "study5_v0.1" / "results.json")
add = C.load(C.OUT / "study5_v0.1" / "ADDENDUM_ROTATION.json")
assert res["alpha"] == 0.01
LEVELS = ["0.35", "0.5"]
NG = ["64", "256", "1024"]
T = lambda rho: rho.replace(".", "")  # noqa: E731
KEYS = [str(k) for k in range(1001, 1009)]
D2_BAR, D3_BAR = 20.0, 1.10


def chk(d, n=8):
    assert len(d["per_key"]) == n and abs(float(np.median(d["per_key"])) - d["median"]) < 1e-12
    assert d["ci95"][0] <= d["median"] + 1e-12 and d["median"] - 1e-12 <= d["ci95"][1]
    return d


def d1_verdict(fa_by_n, bar, ctrl_hi, centre="median"):
    prac = [n for n in NG if fa_by_n[n][centre] >= bar and fa_by_n[n]["ci95"][0] > ctrl_hi]
    if prac:
        return f"practical (n={prac[0]})"
    if all(fa_by_n[n]["ci95"][1] < bar for n in NG):  # the protocol's blocked branch: every n's upper bound below the bar
        return "stealing blocked at n <= 1024"
    return "inconclusive"


def d2_verdict(d):
    if d["median_diff_points"] >= D2_BAR and d["ci95"][0] > 0:
        return "material robustness cost"
    if d["ci95"][1] < D2_BAR:
        return "immaterial"
    return "inconclusive"


def ci_ratio(d):
    return f"{C.f3(d['median_ratio'])} [{C.f3(d['ci95'][0])}, {C.f3(d['ci95'][1])}]"


def ci_pts(d):
    return f"{d['median_diff_points']:+.1f} [{d['ci95'][0]:+.1f}, {d['ci95'][1]:+.1f}]"


# ---------------------------------------------------------------- gates
for arm in ("h1", "h4"):
    cal = res["arms"][arm]["calibration"]
    per = {int(k): v for k, v in cal["G2"]["per_key_fpr_pct"].items()}
    assert abs(np.mean(list(per.values())) - cal["G1"]["pooled_fpr_pct"]) < 1e-9 and cal["G1"]["pass"] is True
    assert cal["G2"]["n_calibrated"] == sum(v <= cal["G2"]["max_pct"] for v in per.values()) == 8
    V.set(f"s5x_{arm}_G1_pct", C.f2(cal["G1"]["pooled_fpr_pct"]))
    V.set(f"s5x_{arm}_G2_range", f"{C.f1(min(per.values()))}–{C.f1(max(per.values()))}")
assert res["rotation"]["G1"]["pass"] is True
V.set("s5x_union_G1_pct", C.f2(res["rotation"]["G1"]["pooled_fpr_pct"]))

rows_a, rows_b = [], []
for rho in LEVELS:
    t = T(rho)
    F, R = res["fixed"][rho], res["rotation"][rho]
    # --- the fixed key: P0
    chk(F["oracle_FA"])
    chk(F["random_FA"])
    for n in NG:
        chk(F["forge_FA"][n])
        assert abs(float(np.median([F["per_key"][k]["forge_FA"][n] for k in KEYS])) - F["forge_FA"][n]["median"]) < 1e-12
        assert abs(float(np.median([F["per_key"][k]["cos_known"][n] for k in KEYS])) - F["recovery"][n]["median_cos_known"]) < 1e-12
    bar0 = 0.5 * F["oracle_FA"]["median"]
    assert abs(F["P0"]["bar"] - bar0) < 1e-12
    assert d1_verdict(F["forge_FA"], bar0, F["random_FA"]["ci95"][1]) == F["P0"]["verdict"], rho
    det_fixed = float(np.median([F["per_key"][k]["detect"] for k in KEYS]))
    V.set(f"s5x_fixed_{t}_detect", C.pct(det_fixed))
    V.set(f"s5x_fixed_{t}_oracle_FA", C.pct_ci(F["oracle_FA"]))
    V.set(f"s5x_fixed_{t}_oracle_FA_med", C.pct(F["oracle_FA"]["median"]))
    V.set(f"s5x_fixed_{t}_random_FA", C.pct_ci(F["random_FA"]))
    V.set(f"s5x_fixed_{t}_P0_bar", C.pct(bar0))
    V.set(f"s5x_fixed_{t}_P0", F["P0"]["verdict"])
    for n in NG:
        V.set(f"s5x_fixed_{t}_n{n}_FA", C.pct_ci(F["forge_FA"][n]))
        V.set(f"s5x_fixed_{t}_n{n}_FA_med", C.pct(F["forge_FA"][n]["median"]))
    pk1024 = [F["per_key"][k]["forge_FA"]["1024"] for k in KEYS]
    V.set(f"s5x_fixed_{t}_n1024_FA_perkey_min", C.pct(min(pk1024), 0))
    V.set(f"s5x_fixed_{t}_n1024_FA_perkey_max", C.pct(max(pk1024), 0))
    rows_a.append([f"fixed key (h = 0), Route A′", rho, C.pct(det_fixed), " / ".join(C.f2(F["recovery"][n]["median_cos_known"]) for n in NG),
                   " / ".join(C.pct_ci(F["forge_FA"][n]) for n in NG), f"{C.pct(bar0)} (genuine FA {C.pct(F['oracle_FA']['median'])})", C.pct_ci(F["random_FA"]), f"P0: {F['P0']['verdict']}"])
    # --- the context-hashed arms: D1, D2, D3
    for arm in ("h1", "h4"):
        L, h = res["arms"][arm]["levels"][rho], res["arms"][arm]["h"]
        chk(L["detection"])
        chk(L["genuine_FA"])
        chk(L["control_FA"])
        chk(L["para_success"])
        chk(L["para_detected"])
        assert abs(float(np.median([L["per_key"][k]["detect"] for k in KEYS])) - L["detection"]["median"]) < 1e-12
        assert L["P1"]["pass"] is (100 * L["detection"]["median"] >= L["P1"]["min_pct"]) and abs(L["P1"]["median_pct"] - 100 * L["detection"]["median"]) < 1e-9
        for n in NG:
            chk(L["forge_FA"][n])
            assert abs(float(np.median([L["per_key"][k]["forge_FA"][n] for k in KEYS])) - L["forge_FA"][n]["median"]) < 1e-12
        bar = 0.5 * L["genuine_FA"]["median"]
        assert abs(L["D1"]["bar"] - bar) < 1e-12
        assert d1_verdict(L["forge_FA"], bar, L["control_FA"]["ci95"][1]) == L["D1"]["verdict"], (arm, rho)
        d2, d3 = L["D2"], L["D3"]
        assert d2_verdict(d2) == d2["verdict"], (arm, rho)
        diffs = [L["per_key"][k]["para_success"] - L["per_key"][k]["fixed_s2_success"] for k in KEYS]
        assert abs(100 * float(np.median(diffs)) - d2["median_diff_points"]) < 1e-9
        assert d2["n_keys_ge_20_points"] == sum(100 * x >= D2_BAR for x in diffs)
        assert abs(float(np.median([L["per_key"][k]["fixed_s2_success"] for k in KEYS])) - F["s2_success"]["median"]) < 1e-12
        ratios = [L["per_key"][k]["ppl_ratio_median"] for k in KEYS]
        assert abs(float(np.median(ratios)) - d3["median_ratio"]) < 1e-12 and d3["n_keys_above_1.10"] == sum(x > D3_BAR for x in ratios)
        assert (d3["verdict"] == "immaterial") is (d3["median_ratio"] <= D3_BAR and d3["ci95"][1] < D3_BAR), (arm, rho)
        V.set(f"s5x_{arm}_{t}_P1", C.pct_ci(L["detection"]))
        V.set(f"s5x_{arm}_{t}_P1_med", C.pct(L["detection"]["median"]))
        V.set(f"s5x_{arm}_{t}_genuine_FA", C.pct(L["genuine_FA"]["median"]))
        V.set(f"s5x_{arm}_{t}_control_FA", C.pct_ci(L["control_FA"]))
        V.set(f"s5x_{arm}_{t}_D1_bar", C.pct(bar))
        for n in NG:
            V.set(f"s5x_{arm}_{t}_n{n}_FA_med", C.pct(L["forge_FA"][n]["median"]))
            V.set(f"s5x_{arm}_{t}_n{n}_FA_hi", C.pct(L["forge_FA"][n]["ci95"][1]))
        V.set(f"s5x_{arm}_{t}_para_success", C.pct_ci(L["para_success"]))
        V.set(f"s5x_{arm}_{t}_para_success_med", C.pct(L["para_success"]["median"]))
        V.set(f"s5x_{arm}_{t}_para_detected", C.pct(L["para_detected"]["median"]))
        V.set(f"s5x_{arm}_{t}_d", ci_pts(d2))
        V.set(f"s5x_{arm}_{t}_d_med", f"{d2['median_diff_points']:+.1f}")
        V.set(f"s5x_{arm}_{t}_D2", d2["verdict"])
        V.set(f"s5x_{arm}_{t}_D2_keys", d2["n_keys_ge_20_points"])
        V.set(f"s5x_{arm}_{t}_ppl_ratio", ci_ratio(d3))
        V.set(f"s5x_{arm}_{t}_ppl_ratio_med", C.f2(d3["median_ratio"]))
        V.set(f"s5x_{arm}_{t}_D3", d3["verdict"])
        V.set(f"s5x_{arm}_{t}_D3_keys", d3["n_keys_above_1.10"])
        rows_a.append([f"context-hashed, h = {h}", rho, C.pct(L["detection"]["median"]), " / ".join(C.f2(L["recovery"][n]["cos_weighted"]) for n in NG),
                       " / ".join(C.pct_ci(L["forge_FA"][n]) for n in NG), f"{C.pct(bar)} (genuine FA {C.pct(L['genuine_FA']['median'])})", C.pct_ci(L["control_FA"]), f"D1: {L['D1']['verdict']}"])
        _dk = [100 * (L["per_key"][k]["para_success"] - L["per_key"][k]["fixed_s2_success"]) for k in sorted(L["per_key"], key=int)]
        assert abs(float(np.median(_dk)) - d2["median_diff_points"]) < 1e-9 and sum(x >= 20 for x in _dk) == d2["n_keys_ge_20_points"], (h, rho)
        rows_b.append([f"context-hashed, h = {h}", rho, C.pct_ci(L["para_success"]), C.pct_ci(F["s2_success"]), ci_pts(d2), f"{d2['n_keys_ge_20_points']} of 8", d2["verdict"],
                       C.pct(L["para_detected"]["median"]), ci_ratio(d3), f"{d3['n_keys_above_1.10']} of 8", d3["verdict"]])
    # --- rotation: union test, naive and clustering attackers, D2 on the union test
    chk(R["union_detection"])
    chk(R["single_detection"])
    assert abs(float(np.median([R["per_key"][k]["union_detect"] for k in KEYS])) - R["union_detection"]["median"]) < 1e-12
    assert R["P1"]["pass"] and abs(R["P1"]["median_pct"] - 100 * R["union_detection"]["median"]) < 1e-9
    for who in ("naive", "cluster"):
        assert abs(R["D1"][who]["bar"] - bar0) < 1e-12
        assert d1_verdict(R["forge_FA"][who], bar0, F["random_FA"]["ci95"][1], centre="mean") == R["D1"][who]["verdict"], (rho, who)
    rec = {n: len({c["best_key"] for c in R["cluster"][n]["clusters"].values() if c["best_cos"] >= 0.5}) for n in NG}
    for n in NG:
        assert rec[n] == R["cluster"][n]["keys_recovered_ge_0.5"]
    chosen_cos = {n: R["cluster"][n]["clusters"][str(R["cluster"][n]["chosen_cluster"])]["best_cos"] for n in NG}
    union_success = float(np.median([R["per_key"][k]["union_success"] for k in KEYS]))
    d2r = R["D2"]
    d_pts = [100 * (R["per_key"][k]["union_success"] - s2k) for k, s2k in zip(sorted(R["per_key"], key=int), F["s2_success"]["per_key"])]
    assert abs(float(np.median(d_pts)) - d2r["median_diff_points"]) < 1e-9, (rho, float(np.median(d_pts)), d2r["median_diff_points"])  # D2 for rotation: the median over keys of the paired per-key difference
    assert d2_verdict(d2r) == d2r["verdict"], rho
    V.set(f"s5x_rot_{t}_union_detect", C.pct_ci(R["union_detection"]))
    V.set(f"s5x_rot_{t}_union_detect_med", C.pct(R["union_detection"]["median"]))
    V.set(f"s5x_rot_{t}_single_detect", C.pct_ci(R["single_detection"]))
    V.set(f"s5x_rot_{t}_union_success", C.pct(union_success))
    V.set(f"s5x_rot_{t}_d", ci_pts(d2r))
    V.set(f"s5x_rot_{t}_D2", d2r["verdict"])
    V.set(f"s5x_rot_{t}_D1_naive", R["D1"]["naive"]["verdict"])
    V.set(f"s5x_rot_{t}_D1_cluster", R["D1"]["cluster"]["verdict"])
    for n in NG:
        V.set(f"s5x_rot_{t}_n{n}_keys_recovered", rec[n])
        V.set(f"s5x_rot_{t}_n{n}_chosen_cos", C.f2(chosen_cos[n]))
        V.set(f"s5x_rot_{t}_n{n}_cluster_FA", C.pct_ci(R["forge_FA"]["cluster"][n]))
        V.set(f"s5x_rot_{t}_n{n}_cluster_FA_med", C.pct(R["forge_FA"]["cluster"][n]["mean"], 0))
        V.set(f"s5x_rot_{t}_n{n}_naive_FA", C.pct_ci(R["forge_FA"]["naive"][n]))
    rows_a.append([f"rotation (K = 8), naive attacker", rho, f"{C.pct(R['union_detection']['median'])} (union test; told the key: {C.pct(R['single_detection']['median'])})",
                   " / ".join(C.f2(max(R["naive"][n].values())) for n in NG) + " (best cos with any key)",
                   " / ".join(C.pct_ci(R["forge_FA"]["naive"][n]) for n in NG), f"{C.pct(bar0)} (the fixed key's genuine FA)", C.pct_ci(F["random_FA"]), f"D1: {R['D1']['naive']['verdict']}"])
    rows_a.append([f"rotation (K = 8), clustering attacker", rho, "as above", " / ".join(f"{rec[n]} of 8 keys (forging cluster cos {C.f2(chosen_cos[n])})" for n in NG),
                   " / ".join(C.pct_ci(R["forge_FA"]["cluster"][n]) for n in NG), f"{C.pct(bar0)}", C.pct_ci(F["random_FA"]), f"D1: {R['D1']['cluster']['verdict']}"])
    rows_b.append([f"rotation (K = 8), union test", rho, f"{C.pct(union_success)} (Study 2's paraphrases under the union test)", C.pct_ci(F["s2_success"]), ci_pts(d2r), "—", d2r["verdict"],
                   "—", "unchanged by construction", "—", "not tested"])

# ---------------------------------------------------------------- the rotation addendum (post hoc, labelled)
assert add["rho"] == 0.35 and abs(add["bar_half_genuine_FA"] - res["fixed"]["0.35"]["P0"]["bar"]) < 1e-12
for n in ("256", "1024"):
    A = add["n"][n]
    cl = A["clusters"]
    every = max(cl.values(), key=lambda c: c["FA"])
    largest = max(cl.values(), key=lambda c: c["size"])
    study = max(cl.values(), key=lambda c: c["profile"])
    assert abs(A["every_cluster"]["FA"] - every["FA"]) < 1e-12 and abs(A["largest_cluster_rule"]["FA"] - largest["FA"]) < 1e-12 and abs(A["study_rule"]["FA"] - study["FA"]) < 1e-12
    assert cl[A["every_cluster"]["cluster"]]["FA"] == every["FA"] and cl[A["study_rule"]["cluster"]]["profile"] == study["profile"]
    assert A["clusters_cos_ge_0.5"] == sum(c["best_cos"] >= 0.5 for c in cl.values())
    assert A["clusters_cos_ge_0.5_reaching_bar"] == sum(c["best_cos"] >= 0.5 and c["FA"] >= add["bar_half_genuine_FA"] for c in cl.values())
    assert abs(res["rotation"]["0.35"]["forge_FA"]["cluster"][n]["mean"] - A["study_rule"]["FA"]) < 1e-9 + 0.02  # the study's rule, re-run with 100 texts
    V.set(f"s5x_add_n{n}_every_FA", C.pct(every["FA"], 0))
    V.set(f"s5x_add_n{n}_every_cos", C.f2(every["best_cos"]))
    V.set(f"s5x_add_n{n}_largest_FA", C.pct(largest["FA"], 0))
    V.set(f"s5x_add_n{n}_study_FA", C.pct(study["FA"], 0))
    V.set(f"s5x_add_n{n}_study_cos", C.f2(study["best_cos"]))
    V.set(f"s5x_add_n{n}_clusters_ge05", A["clusters_cos_ge_0.5"])
    V.set(f"s5x_add_n{n}_reaching_bar", A["clusters_cos_ge_0.5_reaching_bar"])
    rows_a.append([f"**post hoc, labelled (App. G):** rotation, clustering attacker, forging with every cluster", "0.35", "as above",
                   f"n = {int(n):,}: {A['clusters_cos_ge_0.5']} clusters with cos ≥ 0.5; the study's rule picked cos {C.f2(study['best_cos'])}",
                   f"n = {int(n):,}: best cluster {C.pct(every['FA'], 0)}; largest cluster {C.pct(largest['FA'], 0)}; the study's rule {C.pct(study['FA'], 0)}",
                   C.pct(add["bar_half_genuine_FA"]), "—", f"{A['clusters_cos_ge_0.5_reaching_bar']} of {A['clusters_cos_ge_0.5']} recovered clusters reach the bar (not pre-registered; the D1 verdict stands)"])
V.set("s5x_add_bar", C.pct(add["bar_half_genuine_FA"]))

# ranges the prose quotes
arm_hi = [res["arms"][a]["levels"][r]["forge_FA"][n]["ci95"][1] for a in ("h1", "h4") for r in LEVELS for n in NG]
V.set("s5x_arms_FA_hi_max", C.pct(max(arm_hi)))
V.set("s5x_arms_FA_med_max", C.pct(max(res["arms"][a]["levels"][r]["forge_FA"][n]["median"] for a in ("h1", "h4") for r in LEVELS for n in NG)))
V.set("s5x_h1_05_FA_trend", " → ".join(C.pct(res["arms"]["h1"]["levels"]["0.5"]["forge_FA"][n]["median"]) for n in NG))
rat = [res["arms"][a]["levels"][r]["D3"]["median_ratio"] for a in ("h1", "h4") for r in LEVELS]
V.set("s5x_ppl_ratio_min", C.f2(min(rat)))
V.set("s5x_ppl_ratio_max", C.f2(max(rat)))
V.set("s5x_D3_keys_above_total", sum(res["arms"][a]["levels"][r]["D3"]["n_keys_above_1.10"] for a in ("h1", "h4") for r in LEVELS))
pd_ = [res["arms"][a]["levels"][r]["para_detected"]["median"] for a in ("h1", "h4") for r in LEVELS]
V.set("s5x_arms_para_detected_min", C.pct(min(pd_)))
V.set("s5x_arms_para_detected_max", C.pct(max(pd_)))
V.set("s5x_arms_P1_min", C.pct(min(res["arms"][a]["levels"][r]["detection"]["median"] for a in ("h1", "h4") for r in LEVELS)))
V.set("s5x_arms_P1_max", C.pct(max(res["arms"][a]["levels"][r]["detection"]["median"] for a in ("h1", "h4") for r in LEVELS)))
V.set("s5x_N_PARA", res["scope"]["N_PARA"])
NEW_TOKENS = C.const_from_code(C.RESEARCH / "study1" / "core.py", "NEW_TOKENS")
V.set("s5x_n64_tokens", f"{64 * NEW_TOKENS:,}")
V.set("s5x_n64_tokens_k", f"{64 * NEW_TOKENS / 1000:.0f},000")
V.set("s5x_N_OBS", f"{res['scope']['N_OBS']['h1']:,}")

C.write_table("T6a", ["arm and attacker", "ρ", "genuine detection, P1 (%)", "key recovery at n = 64 / 256 / 1,024 (cosine with the key; count-weighted for the hashed arms)",
                      "forgery FA at n = 64 / 256 / 1,024 (%) [95% CI]", "bar: half the genuine FA (%)", "control FA (%) [95% CI]", "verdict"],
              rows_a, "The fixed key and the keyed arms under the gradient-averaging attacker: detection and stealing against the budget (Study 5; medians over 8 keys; rotation's forgery sets have no per-key structure and are means)",
              ["FA: attributed at p ≤ 0.01 (the keyed test for the hashed arms; the union test for rotation) and fluent by the arm's own genuine texts' bars. P0 and D1: practical at the first n "
               "where the FA reaches the bar with its lower bound above the control's upper bound; otherwise stealing blocked at n ≤ 1,024. The control is a random key (fixed arm, rotation) "
               "or a random secret (hashed arms). The last two rows are the labelled post-hoc addendum (not pre-registered); the pre-registered rotation verdict at ρ = 0.35 stands as written."])
C.write_table("T6b", ["arm", "ρ", "scrub success after P-Qwen (%) [95% CI]", "the fixed key's on the same prompts and keys (Study 2's texts and rule; Study 5's bootstrap) (%) [95% CI]", "d: paired difference (points) [95% CI]",
                      "keys ≥ 20 points", "D2 verdict", "detected after paraphrase (%)", "perplexity ratio to the fixed key [95% CI]", "keys > 1.10", "D3 verdict"],
              rows_b, "The keyed arms' robustness cost (D2) and quality cost (D3) beside the fixed key (Study 5; medians over 8 keys; 100 paraphrases per key and strength)",
              ["Scrub success is Study 2's definition (not attributed and the four quality conditions pass). D2: material if the median paired difference is at least 20 points with its lower bound "
               "above zero; immaterial if the upper bound is below 20; otherwise inconclusive. D3: immaterial if the median ratio and its upper bound are below 1.10. Rotation's texts are the "
               "fixed key's own texts, so its quality is unchanged by construction and its robustness reading is the union test's loss on Study 2's paraphrases."])
p = V.save()
print("T6 written; values:", p.name, len(V.d))
