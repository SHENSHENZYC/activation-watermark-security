"""F3 — the exact test detects the key and rejects Study 1's forgeries (§5.3): (a) texts attributed at an exact 1% FPR
against ρ, exact test vs the owner's probe, genuine and random-key texts; (b) per strength, Study 1's texts accepted by
the probe (hollow) and by the exact test (filled): the oracle, the random key, v0.4's Route A and B at n = 256 and
v0.2's Route B at n = 1,024. Reads study3_v0.1/results.json (and study1_v0.2/results.json for the probe's intervals on
the same texts); asserts the medians against the per-key rates and the probe's medians against Study 1's file; writes
build/F3.png and build/values_fig3.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("fig3")
res = C.load(C.OUT / "study3_v0.1" / "results.json")
r2 = C.load(C.OUT / "study1_v0.2" / "results.json")
P = res["S4"]
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
rho = [float(v) for v in LEVELS]
EX, PR = C.PAL["exact"], C.PAL["probe"]
plt = C.fig_style()


def med_ci(d):
    assert abs(float(np.median(d["per_key"])) - d["median"]) < 1e-12 and d["ci95"][0] <= d["median"] + 1e-12 and d["median"] - 1e-12 <= d["ci95"][1]
    return 100 * d["median"], 100 * d["ci95"][0], 100 * d["ci95"][1]


fig = plt.figure(figsize=(10.4, 4.0))
gs = fig.add_gridspec(1, 6, width_ratios=[2.4, 0.95, 1, 1, 1, 1], wspace=0.12)   # column 1 is a spacer for the row labels
ax = fig.add_subplot(gs[0, 0])
for c, ls, mk, lab in (("oracle", "-", "o", "genuine"), ("random", "--", "s", "random key")):
    e = [med_ci(P["levels"][lv][c]["acceptance"]) for lv in LEVELS]
    ax.fill_between(rho, [x[1] for x in e], [x[2] for x in e], color=EX, alpha=0.12, linewidth=0)
    ax.plot(rho, [x[0] for x in e], ls, color=EX, lw=2, marker=mk, ms=6.5, label=f"exact test: {lab}")
    pm = []
    for lv in LEVELS:
        d = r2["levels"][lv][c]
        assert abs(d["median"] - P["levels"][lv][c]["probe_acceptance_median"]) < 1e-12, (lv, c)   # the same texts, Study 1's probe
        pm.append(med_ci(d))
    ax.fill_between(rho, [x[1] for x in pm], [x[2] for x in pm], color=PR, alpha=0.08, linewidth=0)
    ax.plot(rho, [x[0] for x in pm], ls, color=PR, lw=1.5, marker=mk, ms=6.5, mfc="white", label=f"owner's probe: {lab}")
ax.axhline(1, color=C.MUTED, lw=1, ls=":")
ax.text(0.72, 4.5, "1% FPR", color=C.MUTED, fontsize=7, ha="center")
e25 = 100 * P["levels"]["0.25"]["oracle"]["acceptance"]["median"]
ax.annotate(f"{e25:.1f}%", (0.25, e25), xytext=(0.27, e25 - 12), fontsize=7.5, color=EX)
ax.set_xticks(rho)
ax.set_xlim(0.22, 0.78)
ax.set_ylim(-3, 104)
ax.set_xlabel(C.XLAB_RHO)
ax.set_ylabel("texts attributed to the key at a 1% FPR (%)")
ax.set_title("(a) genuine and random-key texts")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), fontsize=7.2, ncol=2)

ROWS = [("oracle", "genuine"), ("random", "random key"), ("v04_A_n256", "Route A, v0.4, n = 256"), ("v04_B_n256", "Route B, v0.4, n = 256"), ("v02_B_n1024", "Route B, v0.2, n = 1,024")]
axes = []
for j, lv in enumerate(LEVELS):
    axb = fig.add_subplot(gs[0, j + 2], sharey=axes[0] if axes else None)
    axes.append(axb)
    L = P["levels"][lv]
    for i, (c, lab) in enumerate(ROWS):
        if c not in L:
            continue
        pr, ex = 100 * L[c]["probe_acceptance_median"], med_ci(L[c]["acceptance"])[0]
        axb.plot([pr, ex], [i, i], color=C.GRID, lw=2.4, zorder=1)
        axb.scatter([pr], [i], s=40, color="white", edgecolor=PR, linewidth=1.3, zorder=2, label="owner's probe" if i == 0 else None)
        axb.scatter([ex], [i], s=40, color=EX, edgecolor="white", linewidth=0.9, zorder=3, label="exact test" if i == 0 else None)
    axb.axvline(1, color=C.MUTED, lw=1, ls=":")
    axb.set_xlim(-5, 105)
    axb.set_xticks([0, 50, 100])
    axb.set_title(f"ρ = {float(lv):.2f}", fontsize=8.5)
    axb.set_xlabel("accepted (%)", fontsize=8)
    if j:
        plt.setp(axb.get_yticklabels(), visible=False)
axes[0].set_yticks(range(len(ROWS)), [r[1] for r in ROWS], fontsize=7.5)
axes[0].set_ylim(len(ROWS) - 0.5, -0.5)
fig.text(0.43, 0.98, "(b) Study 1's texts: the owner's probe (hollow) vs the exact test (filled)", fontsize=9, color=C.INK, ha="left", va="top")
h, lab = axes[0].get_legend_handles_labels()
fig.legend(h, lab, loc="lower center", bbox_to_anchor=(0.74, -0.06), fontsize=7.5, ncol=2)
fig.subplots_adjust(top=0.9, bottom=0.2, left=0.07, right=0.99)
C.save_fig(fig, "F3")
for lv in LEVELS:
    V.set(f"f3_exact_tpr_{lv.replace('.', '')}", C.pct(P["levels"][lv]["oracle"]["acceptance"]["median"]))
p = V.save()
print("F3 written; values:", p.name, len(V.d))
