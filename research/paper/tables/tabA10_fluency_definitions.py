"""TA10 — the forgeries of v0.2, v0.3 and v0.4 under three fluency definitions (Appendix E): plain acceptance by the
probe; FA with perplexity only (v0.3's rule); FA with perplexity and seq-rep-4 (v0.4's rule); FA with perplexity and
word rep-3; and the share of texts above the repetition bar, per strength, route, budget and attacker version. Reads
study1_v0.4/results.json (which re-scored every earlier forgery set under the same bars) and study1_v0.3/results.json
(asserting that v0.3's locked FA equals the perplexity-only column for its own forgeries); writes build/TA10.md and
build/values_tabA10.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA10")
r4 = C.load(C.OUT / "study1_v0.4" / "results.json")
r3 = C.load(C.OUT / "study1_v0.3" / "results.json")
assert r4["integrity"]["pass"] is True and r3["integrity"]["pass"] is True
rows = []
for rho in C.LEVELS3:
    L, L3, t = r4["levels"][rho], r3["levels"][rho], C.tag(rho)
    for s, lab in (("oracle", "genuine (oracle)"), ("random", "random key")):
        x = L[s]
        rows.append([C.rho_lab(rho), lab, "—", "—", C.pct(x["acceptance"]["median"]), C.pct(x["FA_ppl_only_median"]), C.pct(x["FA"]["median"]), C.pct(x["FA_rep3_median"]),
                     C.pct(x["repetitive_share_median"]), C.pct(x["fluent_share_median"])])
        V.set(f"ta10_{s}_{t}_rep_share", C.pct(x["repetitive_share_median"]))
        V.set(f"ta10_{s}_{t}_fluent_share", C.pct(x["fluent_share_median"]))
    for r in "AB":
        for n in (64, 256):
            for v in ("v02", "v03", "v04"):
                x = L[f"{v}_{r}_n{n}"]
                if v == "v03":
                    assert abs(x["FA_ppl_only_median"] - L3[f"v03_{r}_n{n}"]["FA"]["median"]) < 1e-9, (rho, r, n)
                rows.append([C.rho_lab(rho), f"Route {r}", f"{n}", v.replace("v0", "v0."), C.pct(x["acceptance"]["median"]), C.pct(x["FA_ppl_only_median"]), C.pct(x["FA"]["median"]),
                             C.pct(x["FA_rep3_median"]), C.pct(x["repetitive_share_median"]), C.pct(x["fluent_share_median"])])
                for fld, nm in (("acceptance", "acc"), ("FA_ppl_only_median", "ppl_only"), ("FA", "v04"), ("FA_rep3_median", "rep3"), ("repetitive_share_median", "rep_share"),
                                ("fluent_share_median", "fluent_share")):
                    val = x[fld]["median"] if isinstance(x[fld], dict) else x[fld]
                    V.set(f"ta10_{v}_{r}_n{n}_{t}_{nm}", C.pct(val))
# headline readings for the appendix prose
b07 = [r4["levels"]["0.7"][f"v03_B_n{n}"] for n in (64, 256)]
V.set("ta10_v03_B_07_ppl_only_min", C.pct(min(x["FA_ppl_only_median"] for x in b07)))
V.set("ta10_v03_B_07_v04_max", C.pct(max(x["FA"]["median"] for x in b07)))
V.set("ta10_v03_B_07_rep_share_min", C.pct(min(x["repetitive_share_median"] for x in b07)))
V.set("ta10_v03_B_07_rep_share_max", C.pct(max(x["repetitive_share_median"] for x in b07)))
b02 = [r4["levels"][rho][f"v02_B_n{n}"] for rho in ("0.5", "0.7") for n in (64, 256)]
V.set("ta10_v02_B_05_07_acc_min", C.pct(min(x["acceptance"]["median"] for x in b02)))
V.set("ta10_v02_B_05_07_v04_max", C.pct(max(x["FA"]["median"] for x in b02)))
V.set("ta10_v02_B_05_07_fluent_share_max", C.pct(max(x["fluent_share_median"] for x in b02)))
rep3_vs_v04 = max(abs(r4["levels"][rho][f"{v}_{r}_n{n}"]["FA_rep3_median"] - r4["levels"][rho][f"{v}_{r}_n{n}"]["FA"]["median"])
                  for rho in C.LEVELS3 for v in ("v02", "v03", "v04") for r in "AB" for n in (64, 256))
V.set("ta10_rep3_vs_v04_max_abs_diff_points", f"{100 * rep3_vs_v04:.1f}")
C.write_table("TA10", ["ρ", "route", "n", "forgeries", "accepted by the probe", "FA, perplexity only (v0.3's rule)", "FA, perplexity and seq-rep-4 (v0.4's rule)",
                       "FA, perplexity and word rep-3", "texts above the seq-rep-4 bar", "texts under the perplexity bar"], rows,
              "Study 1: the same forgeries under three fluency definitions (median over 8 keys, %); the genuine and random-key texts for reference",
              ["v0.2's attacker had no quality check, v0.3's screened its candidate layers by perplexity, v0.4's by perplexity and repetition; every set is re-scored here "
               "under v0.4's locked bars (the key's oracle 95th-percentile perplexity and seq-rep-4). The perplexity-only column for the v0.3 forgeries equals "
               "v0.3's locked FA (asserted). Word rep-3 is the share of repeated word trigrams, an exploratory alternative to seq-rep-4."])
p = V.save()
print("TA10 written; values:", p.name, len(V.d))
