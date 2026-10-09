"""F2 — forging the trained probe without the key (§5.2): fluent, non-repetitive acceptance (FA) against ρ for the oracle
(true key), the random key, and Route A and Route B at n = 64 and 256, with the F1 bar (half the oracle FA). Reads
study1_v0.4/results.json; asserts every plotted median is the median of the per-key rates and the bands are the file's
intervals; writes build/F2.png and build/values_fig2.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("fig2")
r4 = C.load(C.OUT / "study1_v0.4" / "results.json")
assert r4["integrity"]["pass"] is True
LEVELS = ["0.35", "0.5", "0.7"]
rho = [float(v) for v in LEVELS]
plt = C.fig_style()


def series(c):
    out = []
    for lv in LEVELS:
        d = r4["levels"][lv][c]["FA"]
        assert abs(float(np.median(d["per_key"])) - d["median"]) < 1e-12 and d["ci95"][0] <= d["median"] <= d["ci95"][1]
        out.append((100 * d["median"], 100 * d["ci95"][0], 100 * d["ci95"][1]))
    return out


fig, ax = plt.subplots(figsize=(6.4, 4.1))
SER = [("oracle", "genuine (true key, true layer)", C.INK, "-", "o", True),
       ("random", "random key (generic steering)", C.CTRL, "--", "s", True),
       ("v04_A_n256", "Route A forgery, n = 256", C.PAL["A"], "-", "^", True),
       ("v04_A_n64", "Route A forgery, n = 64", C.PAL["A"], ":", "^", False),
       ("v04_B_n256", "Route B forgery, n = 256", C.PAL["B"], "-", "D", True),
       ("v04_B_n64", "Route B forgery, n = 64", C.PAL["B"], ":", "D", False)]
for c, lab, col, ls, mk, band in SER:
    s = series(c)
    if band:
        ax.fill_between(rho, [x[1] for x in s], [x[2] for x in s], color=col, alpha=0.10, linewidth=0)
    ax.plot(rho, [x[0] for x in s], ls, color=col, lw=2 if band else 1.3, marker=mk, ms=6 if band else 4.5, mfc=col if band else "white", mec=col, label=lab)
bar = [50 * r4["levels"][lv]["oracle"]["FA"]["median"] for lv in LEVELS]
ax.plot(rho, bar, color=C.MUTED, lw=1, ls=(0, (1, 2)))
ax.text(rho[-1] + 0.008, bar[-1], "F1 bar:\nhalf the\ngenuine FA", color=C.MUTED, fontsize=7, va="center")
# selective direct labels: the one practical verdict and the strongest level's generic-steering value
b035 = r4["levels"]["0.35"]["v04_B_n256"]["FA"]["median"]
ax.text(0.302, 100 * b035, f"{100 * b035:.1f}%:\npractical (F1)", fontsize=7, color=C.PAL["B"], ha="left", va="center")
ax.set_xticks(rho)
ax.set_xlim(0.30, 0.78)
ax.set_ylim(-2, 104)
ax.set_xlabel(C.XLAB_RHO)
ax.set_ylabel("accepted by the probe at a 1% FPR,\nfluent and non-repetitive: FA (%)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), fontsize=7.5, ncol=3)
fig.tight_layout()
C.save_fig(fig, "F2")
for lv in LEVELS:
    V.set(f"f2_F1_B_{lv.replace('.', '')}", r4["levels"][lv]["rules"]["F1"]["B"])
V.set("f2_n_levels", len(LEVELS))
p = V.save()
print("F2 written; values:", p.name, len(V.d))
