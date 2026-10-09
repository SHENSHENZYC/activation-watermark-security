"""TA6 — per-key fluent acceptance (FA, v0.4's definition) at n = 256 (Appendix D): keys 1001–1008 for the genuine
(oracle) texts, the random-key control and the v0.4 Route A and Route B forgeries at each strength, with the F1 bar
(half the oracle's median FA) and the count of keys at or above it; the per-key quality bars (perplexity and seq-rep-4
cut-offs) beside them. Reads study1_v0.4/results.json; asserts every median against its per-key values and the bar
against the oracle; writes build/TA6.md and build/values_tabA6.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA6")
r4 = C.load(C.OUT / "study1_v0.4" / "results.json")
assert r4["integrity"]["pass"] is True
SETS = [("oracle", "genuine (oracle)"), ("random", "random key (generic steering)"), ("v04_A_n256", "v0.4 Route A, n = 256"), ("v04_B_n256", "v0.4 Route B, n = 256")]
rows = []
for rho in C.LEVELS3:
    L, t = r4["levels"][rho], C.tag(rho)
    bar = 0.5 * L["oracle"]["FA"]["median"]
    V.set(f"ta6_bar_{t}", C.pct(bar))
    for s, lab in SETS:
        pk = C.chk(L[s]["FA"])
        above = sum(v >= bar for v in pk)
        rows.append([C.rho_lab(rho), lab] + [C.pct0(v) for v in pk] + [C.pct(L[s]["FA"]["median"]), f"{above}" if s != "oracle" else "—"])
        V.set(f"ta6_{s}_{t}_min", C.pct0(min(pk)))
        V.set(f"ta6_{s}_{t}_max", C.pct0(max(pk)))
        V.set(f"ta6_{s}_{t}_keys_ge_bar", above)
        V.set(f"ta6_{s}_{t}_keys_ge_50", sum(v >= 0.5 for v in pk))
    cut = L["cut_per_key"]
    assert len(cut["ppl"]) == 8 and len(cut["seqrep4"]) == 8
    rows.append([C.rho_lab(rho), "perplexity bar (the key's oracle 95th percentile)"] + [C.f1(v) for v in cut["ppl"]] + [C.f1(float(np.median(cut["ppl"]))), "—"])
    rows.append([C.rho_lab(rho), "seq-rep-4 bar (the key's oracle 95th percentile)"] + [C.f3(v) for v in cut["seqrep4"]] + [C.f3(float(np.median(cut["seqrep4"]))), "—"])
    V.set(f"ta6_cut_ppl_{t}_min", C.f1(min(cut["ppl"])))
    V.set(f"ta6_cut_ppl_{t}_max", C.f1(max(cut["ppl"])))
    V.set(f"ta6_cut_rep_{t}_min", C.f3(min(cut["seqrep4"])))
    V.set(f"ta6_cut_rep_{t}_max", C.f3(max(cut["seqrep4"])))
    V.set(f"ta6_F1_A_{t}", L["rules"]["F1"]["A"])
    V.set(f"ta6_F1_B_{t}", L["rules"]["F1"]["B"])
# the bimodal Route A reading at 0.70 and the per-key spread behind the 0.35 verdict
a07 = C.chk(r4["levels"]["0.7"]["v04_A_n256"]["FA"])
V.set("ta6_A_07_keys_ge_50", sum(v >= 0.5 for v in a07))
V.set("ta6_A_07_keys_le_20", sum(v <= 0.2 for v in a07))
C.write_table("TA6", ["ρ", "texts"] + [str(k) for k in C.KEYS] + ["median", "keys ≥ the F1 bar (of 8)"], rows,
              "Study 1 v0.4: per-key fluent acceptance (FA, %) by the owner's probe at its 1% threshold, n = 256 forgeries, with the per-key quality bars",
              ["FA counts a text as accepted by the probe, with perplexity and seq-rep-4 at or below the key's oracle 95th percentiles "
               "(the bars in the last two rows of each strength). The F1 bar is half the oracle's median FA; the F1 verdicts (Table T3) use the median over keys with its "
               "cluster-bootstrap interval, so a set can be 'not practical' or 'inconclusive' while some keys exceed the bar."])
p = V.save()
print("TA6 written; values:", p.name, len(V.d))
