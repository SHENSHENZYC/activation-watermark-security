"""FA5 — what the repetition condition changes (Appendix E): (a, b) at n = 256 per strength and route, the v0.3 forgeries'
fluent acceptance under v0.3's perplexity-only rule and under v0.4's rule (perplexity and seq-rep-4), and the v0.4
forgeries' FA, with the genuine texts' FA as the ceiling; (c) the share of texts above the key's seq-rep-4 bar (median
over keys) for the v0.2, v0.3 and v0.4 Route B forgeries at n = 256, with the genuine and random-key texts. Reads
study1_v0.4/results.json (every set re-scored under the same bars) and study1_v0.3/results.json (asserting v0.3's locked
FA equals the perplexity-only column); writes build/FA5.png and build/values_figA5.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("figA5")
r4 = C.load(C.OUT / "study1_v0.4" / "results.json")
r3 = C.load(C.OUT / "study1_v0.3" / "results.json")
plt = C.fig_style()
fig, axs = plt.subplots(1, 3, figsize=(12.0, 4.1))
x = np.arange(3)
w = 0.26
for ax, r in zip(axs[:2], "AB"):
    bars = [(f"v03_{r}_n256", "ppl_only", "v0.3 forgeries, perplexity-only FA (v0.3's rule)", "#c9c8c1"),
            (f"v03_{r}_n256", "v04", "v0.3 forgeries, v0.4's FA (with seq-rep-4)", C.MUTED),
            (f"v04_{r}_n256", "v04", "v0.4 forgeries (repetition-screened), v0.4's FA", C.PAL[r])]
    for i, (s, m, lab, col) in enumerate(bars):
        vals = []
        for rho in C.LEVELS3:
            d = r4["levels"][rho][s]
            v = d["FA_ppl_only_median"] if m == "ppl_only" else d["FA"]["median"]
            if s.startswith("v03") and m == "ppl_only":
                assert abs(v - r3["levels"][rho][s]["FA"]["median"]) < 1e-9
            vals.append(100 * v)
            V.set(f"fa5_{s}_{m}_{C.tag(rho)}", C.f1(vals[-1]))
        ax.bar(x + (i - 1) * w, vals, w, color=col, label=lab, zorder=3)
    for j, rho in enumerate(C.LEVELS3):
        o = 100 * r4["levels"][rho]["oracle"]["FA"]["median"]
        ax.hlines(o, j - 1.5 * w, j + 1.5 * w, color=C.INK, lw=1.3, zorder=4, label="genuine texts' FA (the ceiling)" if j == 0 else None)
    ax.set_xticks(x, [f"ρ = {C.rho_lab(l)}" for l in C.LEVELS3])
    ax.set_title(f"({'a' if r == 'A' else 'b'}) Route {r}, n = 256")
    ax.set_ylim(0, 105)
axs[0].set_ylabel("fluent acceptance by the probe, median over 8 keys (%)")
ax = axs[2]
SER = [("oracle", "genuine texts", C.INK, "o", "-"), ("random", "random key", C.CTRL, "o", ":"), ("v02_B_n256", "v0.2 Route B (no quality check)", C.PAL["B"], "o", ":"),
       ("v03_B_n256", "v0.3 Route B (perplexity-screened)", C.PAL["B"], "s", "--"), ("v04_B_n256", "v0.4 Route B (perplexity and repetition)", C.PAL["B"], "D", "-"),
       ("v03_A_n256", "v0.3 Route A", C.PAL["A"], "s", "--"), ("v04_A_n256", "v0.4 Route A", C.PAL["A"], "D", "-")]
X3 = [float(l) for l in C.LEVELS3]
for s, lab, col, mk, ls in SER:
    y = [100 * r4["levels"][rho][s]["repetitive_share_median"] for rho in C.LEVELS3]
    ax.plot(X3, y, ls, color=col, lw=1.8, marker=mk, ms=6, mfc=col if ls == "-" else "white", mec=col, label=lab)
    for rho, v in zip(C.LEVELS3, y):
        V.set(f"fa5_rep_{s}_{C.tag(rho)}", C.f1(v))
ax.axhline(5, color=C.MUTED, lw=1, ls=":")
ax.text(0.705, 6, "5% (the bar's definition)", color=C.MUTED, fontsize=7, ha="right", va="bottom")
ax.set_xticks(X3, [C.rho_lab(l) for l in C.LEVELS3])
ax.set_xlabel(C.XLAB_RHO)
ax.set_ylabel("texts above the key's seq-rep-4 bar, median over keys (%)")
ax.set_title("(c) repetitive texts per forgery set, n = 256")
ax.set_ylim(-3, 104)
h0, l0 = axs[0].get_legend_handles_labels()
h2, l2 = axs[2].get_legend_handles_labels()
fig.legend(h0, l0, fontsize=7.5, loc="lower left", ncol=2, bbox_to_anchor=(0.01, -0.02))
fig.legend(h2, l2, fontsize=7.5, loc="lower right", ncol=2, bbox_to_anchor=(0.99, -0.02))
fig.tight_layout(rect=(0, 0.15, 1, 1))
C.save_fig(fig, "FA5")
p = V.save()
print("FA5 written; values:", p.name, len(V.d))
