"""TA4 — the attackers' self-checks and layer choices (Appendix C): (a) Study 1 v0.4's perplexity-and-repetition check
per route, strength and budget (layers chosen, the top candidate kept, no candidate passed, the recovered cosine, the
check's agreement with the evaluation); (b) Study 5's Route A′ on the fixed key (the layer search beside the known
layer); (c) the per-context attacker's mechanics for the hashed arms (contexts estimated, coverage, count-weighted
cosine); (d) the clustering attacker on rotation (keys recovered, the forging cluster's cosine). Reads
study1_v0.4/results.json and study5_v0.1/results.json; re-counts what can be re-counted and asserts it; writes
build/tabA4.md and build/values_tabA4.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA4")
r4 = C.load(C.OUT / "study1_v0.4" / "results.json")
r5 = C.load(C.OUT / "study5_v0.1" / "results.json")
assert r4["integrity"]["pass"] is True

# ---------------------------------------------------------------- (a) v0.4: the attacker's check
rows_a = []
hits14_total, cells = 0, 0
for rho in ("0.35", "0.5", "0.7"):
    L = r4["levels"][rho]
    for cond in ("A_n64", "A_n256", "B_n64", "B_n256"):
        a = L["attacks"][cond]
        route, n = cond.split("_n")
        assert a["layer_hits"] == sum(1 for l in a["selected_layers"] if l == 14), (rho, cond)
        assert a["none_passed"] == sum(1 for k in a["n_kept"] if k == 0), (rho, cond)
        assert len(a["selected_layers"]) == 8
        hits14_total += a["layer_hits"]
        cells += 1
        rows_a.append([rho, route, n, ", ".join(map(str, a["selected_layers"])), a["layer_hits"], a["selected_is_top_candidate"], a["none_passed"],
                       f"{float(np.median(a['n_kept'])):g}", ", ".join(map(str, a["m_selected"])), C.f3(a["median_cos_true"]), C.pct(a["check_vs_eval_agreement"], 0)])
        V.set(f"v04_{route}_n{n}_{rho.replace('.', '')}_layer_hits", a["layer_hits"])
        V.set(f"v04_{route}_n{n}_{rho.replace('.', '')}_median_cos", C.f3(a["median_cos_true"]))
        V.set(f"v04_{route}_n{n}_{rho.replace('.', '')}_none_passed", a["none_passed"])
    V.set(f"v04_F1_A_{rho.replace('.', '')}", L["rules"]["F1"]["A"])
    V.set(f"v04_F1_B_{rho.replace('.', '')}", L["rules"]["F1"]["B"])
V.set("v04_layer14_hits_total", hits14_total)
V.set("v04_layer14_cells", cells * 8)
cosB = [r4["levels"][rho]["attacks"][c]["median_cos_true"] for rho in ("0.35", "0.5", "0.7") for c in ("B_n64", "B_n256")]
cosA = [r4["levels"][rho]["attacks"][c]["median_cos_true"] for rho in ("0.35", "0.5", "0.7") for c in ("A_n64", "A_n256")]
V.set("v04_B_median_cos_max", C.f3(max(cosB)))
V.set("v04_A_median_cos_max", C.f3(max(cosA)))
C.write_table("TA4a", ["ρ", "Route", "n", "layer selected per key (1001–1008)", "layer = 14 (of 8)", "top candidate kept (of 8)", "no candidate passed (of 8)",
                       "candidates passing (median of 5)", "repetitive trials of the selected candidate (of 16), per key", "median cos(v̂, v)", "check agrees with evaluation (%)"],
              rows_a, "Study 1 v0.4: the attacker's perplexity-and-repetition check and its layer choice (descriptive; counts out of 8 keys)",
              ["The check keeps a candidate layer if its 16 trial texts have median continuation perplexity ≤ 1.2 × the observed texts' and at most 2 trials with seq-rep-4 above the observed 95th percentile; the kept candidate with the largest footprint profile is used. 'Agrees' is the share of keys where 'some candidate passed' matches 'the forgery's median perplexity and seq-rep-4 are both at or below the evaluation's bars'."])

# ---------------------------------------------------------------- (b) Study 5: Route A′ on the fixed key
rows_b = []
for rho in ("0.35", "0.5"):
    F = r5["fixed"][rho]
    for n in ("64", "256", "1024"):
        rec = F["recovery"][n]
        assert 0 <= rec["layer_hits_search"] <= 8
        rows_b.append([rho, f"{int(n):,}", C.f3(rec["median_cos_known"]), C.f3(rec["median_cos_search"]), rec["layer_hits_search"]])
        V.set(f"s5_fixed_{rho.replace('.', '')}_n{n}_cos_known", C.f3(rec["median_cos_known"]))
        V.set(f"s5_fixed_{rho.replace('.', '')}_n{n}_cos_search", C.f3(rec["median_cos_search"]))
        V.set(f"s5_fixed_{rho.replace('.', '')}_n{n}_layer_hits", rec["layer_hits_search"])
    V.set(f"s5_P0_{rho.replace('.', '')}", F["P0"]["verdict"])
    fs = F["forge_search_FA"]
    V.set(f"s5_fixed_{rho.replace('.', '')}_forge_search_FA", C.pct_ci(fs))
    V.set(f"s5_fixed_{rho.replace('.', '')}_forge_search_FA_med", C.pct(fs["median"]))
    V.set(f"s5_fixed_{rho.replace('.', '')}_forge_search_n", fs["n"])
C.write_table("TA4b", ["ρ", "n", "median cos(v̂, v), known layer", "median cos(v̂, v), layer search", "layer search finds layer 14 (keys of 8)"],
              rows_b, "Study 5: Route A′ (the gradient-mean estimator) on the fixed key, at the known layer and with the layer search over all 28 layers (medians over 8 keys)")

# ---------------------------------------------------------------- (c) the per-context attacker (hashed arms)
rows_c = []
for arm in ("h1", "h4"):
    h = r5["arms"][arm]["h"]
    for rho in ("0.35", "0.5"):
        L = r5["arms"][arm]["levels"][rho]
        for n in ("64", "256", "1024"):
            rec, fa = L["recovery"][n], L["forge_FA"][n]
            assert 0.0 <= rec["coverage"] <= 1.0 and rec["n_contexts"] >= 0
            assert abs(float(np.median(fa["per_key"])) - fa["median"]) < 1e-12
            rows_c.append([f"h = {h}", rho, f"{int(n):,}", f"{rec['n_contexts']:g}", C.f3(rec["coverage"]), C.f3(rec["cos_weighted"]), C.pct_ci(fa)])
            V.set(f"s5_{arm}_{rho.replace('.', '')}_n{n}_contexts", f"{rec['n_contexts']:g}")
            V.set(f"s5_{arm}_{rho.replace('.', '')}_n{n}_coverage", C.f3(rec["coverage"]))
            V.set(f"s5_{arm}_{rho.replace('.', '')}_n{n}_cosw", C.f3(rec["cos_weighted"]))
            V.set(f"s5_{arm}_{rho.replace('.', '')}_n{n}_FA", C.pct_ci(fa))
        V.set(f"s5_{arm}_{rho.replace('.', '')}_D1", L["D1"]["verdict"])
C.write_table("TA4c", ["arm", "ρ", "n", "contexts estimated (median over keys)", "coverage of a genuine text's positions", "count-weighted cos with the true per-context keys", "forgery FA % [95% CI]"],
              rows_c, "Study 5: the per-context attacker (Route A′-h) on the context-hashed arms, against the budget n (medians over 8 keys)",
              ["A context is estimated once it has been seen at least 16 times among the n observed texts (4 largest |mean| coordinates of the standardised per-position gradients); coverage is the share of a genuine text's scored positions whose context has an estimate."])

# ---------------------------------------------------------------- (d) rotation: the clustering attacker
rows_d = []
for rho in ("0.35", "0.5"):
    Rr = r5["rotation"][rho]
    for n in ("64", "256", "1024"):
        cl = Rr["cluster"][n]
        clusters = cl["clusters"]
        rec = len({c["best_key"] for c in clusters.values() if c["best_cos"] >= 0.5})
        assert rec == cl["keys_recovered_ge_0.5"], (rho, n)
        chosen = clusters[str(cl["chosen_cluster"])]
        best_cos = max(c["best_cos"] for c in clusters.values())
        med_best = float(np.median([c["best_cos"] for c in clusters.values()]))
        naive_best = max(Rr["naive"][n].values())
        fa = Rr["forge_FA"]
        fa_c = fa["cluster"][n] if isinstance(fa.get("cluster"), dict) and n in fa["cluster"] else None
        fa_n = fa["naive"][n] if isinstance(fa.get("naive"), dict) and n in fa["naive"] else None
        rows_d.append([rho, f"{int(n):,}", len(clusters), rec, C.f3(med_best), C.f3(best_cos), f"{cl['chosen_cluster']} (size {chosen['size']}; cos {C.f3(chosen['best_cos'])}; z-profile {C.f2(chosen['profile'])})",
                       C.f3(naive_best), C.pct_ci(fa_c) if fa_c else "—", C.pct_ci(fa_n) if fa_n else "—"])
        t = rho.replace(".", "")
        V.set(f"s5_rot_{t}_n{n}_keys_recovered", rec)
        V.set(f"s5_rot_{t}_n{n}_chosen_cos", C.f3(chosen["best_cos"]))
        V.set(f"s5_rot_{t}_n{n}_best_cos", C.f3(best_cos))
        V.set(f"s5_rot_{t}_n{n}_naive_best_cos", C.f3(naive_best))
        if fa_c:
            V.set(f"s5_rot_{t}_n{n}_cluster_FA", C.pct_ci(fa_c))
        if fa_n:
            V.set(f"s5_rot_{t}_n{n}_naive_FA", C.pct_ci(fa_n))
    V.set(f"s5_rot_{rho.replace('.', '')}_D1_naive", Rr["D1"]["naive"]["verdict"])
    V.set(f"s5_rot_{rho.replace('.', '')}_D1_cluster", Rr["D1"]["cluster"]["verdict"])
C.write_table("TA4d", ["ρ", "n", "clusters with ≥ 2 texts", "keys recovered (best cos ≥ 0.5)", "median best cos over clusters", "largest best cos", "forging cluster by the pre-registered rule (largest z-profile)",
                       "naive attacker: best cos with any key", "forgery FA %, clustering [95% CI]", "forgery FA %, naive [95% CI]"],
              rows_d, "Study 5: the clustering attacker on rotation among 8 keys (spherical k-means with K = 8 on the standardised summed gradients, then Route A′ per cluster)",
              ["The pre-registered forgery used the cluster with the largest standardised mean-gradient profile; at ρ = 0.35 that rule picked a small cluster whose estimate has cosine near 0 with every key, which is why the forgery acceptance is low although most keys were recovered (the labelled post-hoc addendum, Appendix G, forges with every cluster)."])

p = V.save()
print("TA4 written; values:", p.name, len(V.d))
