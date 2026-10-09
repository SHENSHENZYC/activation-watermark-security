"""F6 — the frontier per arm (§5.6, §5.7): forgery FA at n = 1,024 (stealability), scrub success after P-Qwen (robustness
lost) and the perplexity ratio to the fixed key (quality) for the fixed key, h = 1, h = 4 and rotation under the naive
and the clustering attacker, at ρ = 0.35 and 0.50, with the materiality bars; rotation's clustering point at ρ = 0.35 is
shown twice, the pre-registered value and the labelled post-hoc every-cluster value (hollow). Reads
study5_v0.1/results.json and ADDENDUM_ROTATION.json; asserts every plotted median against the per-key records and the
addendum's value against its per-cluster records; writes build/F6.png and build/values_fig6.json.
"""
import sys
from pathlib import Path

import numpy as np
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("fig6")
res = C.load(C.OUT / "study5_v0.1" / "results.json")
add = C.load(C.OUT / "study5_v0.1" / "ADDENDUM_ROTATION.json")
LEVELS = ["0.35", "0.5"]
KEYS = [str(k) for k in range(1001, 1009)]
D3_BAR = 1.10
plt = C.fig_style()
ROWS = [("fixed", "fixed key (h = 0)"), ("h1", "context-hashed, h = 1"), ("h4", "context-hashed, h = 4"), ("naive", "rotation, naive attacker"), ("cluster", "rotation, clustering attacker")]
LMK = {"0.35": "o", "0.5": "s"}


def chk(d, pk=None):
    if "per_key" in d:
        assert abs(float(np.median(d["per_key"])) - d["median"]) < 1e-12
    if pk is not None:
        assert abs(float(np.median(pk)) - d["median"]) < 1e-12
    return d


fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.9), sharey=True)
for i, (arm, lab) in enumerate(ROWS):
    for lv in LEVELS:
        F, R = res["fixed"][lv], res["rotation"][lv]
        off = -0.17 if lv == "0.35" else 0.17
        col = C.PAL["rot"] if arm in ("naive", "cluster") else C.PAL[arm]
        if arm == "fixed":
            st = chk(F["forge_FA"]["1024"], [F["per_key"][k]["forge_FA"]["1024"] for k in KEYS])
            rb, qu = chk(F["s2_success"]), None
        elif arm in ("h1", "h4"):
            L = res["arms"][arm]["levels"][lv]
            st = chk(L["forge_FA"]["1024"], [L["per_key"][k]["forge_FA"]["1024"] for k in KEYS])
            rb = chk(L["para_success"], [L["per_key"][k]["para_success"] for k in KEYS])
            qu = L["D3"]
            assert abs(float(np.median([L["per_key"][k]["ppl_ratio_median"] for k in KEYS])) - qu["median_ratio"]) < 1e-12
        else:
            v = R["forge_FA"][arm]["1024"]
            st = {"median": v["mean"], "ci95": v["ci95"]}
            rb = {"median": C.med([R["per_key"][k]["union_success"] for k in KEYS]), "ci95": None}
            qu = None
        for ax, blk in ((axs[0], st), (axs[1], rb)):
            if blk["ci95"] is not None:
                ax.plot([100 * blk["ci95"][0], 100 * blk["ci95"][1]], [i + off, i + off], color=col, lw=1.2, alpha=0.6)
            ax.scatter([100 * blk["median"]], [i + off], s=42, marker=LMK[lv], color=col, edgecolor="white", linewidth=0.8, zorder=3)
        if qu is not None:
            axs[2].plot(qu["ci95"], [i + off, i + off], color=col, lw=1.2, alpha=0.6)
            axs[2].scatter([qu["median_ratio"]], [i + off], s=42, marker=LMK[lv], color=col, edgecolor="white", linewidth=0.8, zorder=3)
        elif arm == "fixed":
            axs[2].scatter([1.0], [i + off], s=42, marker=LMK[lv], color=col, edgecolor="white", linewidth=0.8, zorder=3)
        else:
            axs[2].scatter([1.0], [i + off], s=42, marker=LMK[lv], facecolor="white", edgecolor=col, linewidth=1.2, zorder=3)
# the labelled post-hoc point: rotation's clustering attacker forging with every cluster at ρ = 0.35, n = 1,024
A = add["n"]["1024"]
every = max(A["clusters"].values(), key=lambda c: c["FA"])
assert abs(A["every_cluster"]["FA"] - every["FA"]) < 1e-12 and add["rho"] == 0.35
i_cl = [r[0] for r in ROWS].index("cluster")
axs[0].plot([100 * every["FA_ci95"][0], 100 * every["FA_ci95"][1]], [i_cl - 0.17 - 0.22, i_cl - 0.17 - 0.22], color=C.PAL["rot"], lw=1.2, alpha=0.6)
axs[0].scatter([100 * every["FA"]], [i_cl - 0.17 - 0.22], s=46, marker="o", facecolor="white", edgecolor=C.PAL["rot"], linewidth=1.4, zorder=4)
axs[0].annotate("post hoc: forging with\nevery cluster (App. G)", (100 * every["FA"], i_cl - 0.39), xytext=(52, i_cl - 1.05), fontsize=6.8, color=C.PAL["rot"],
                arrowprops=dict(arrowstyle="-", color=C.PAL["rot"], lw=0.7))
V.set("f6_add_every_FA_n1024", C.pct(every["FA"], 0))
axs[0].set_yticks(range(len(ROWS)), [r[1] for r in ROWS], fontsize=8)
axs[0].set_ylim(len(ROWS) - 0.5 + 0.3, -0.6)
axs[0].set_xlabel("stealability: forgery FA at n = 1,024 (%)")
axs[1].set_xlabel("robustness lost: scrub success after P-Qwen (%)")
axs[2].set_xlabel("quality: perplexity ratio to the fixed key")
for lv in LEVELS:
    b = 100 * res["fixed"][lv]["P0"]["bar"]
    axs[0].axvline(b, color=C.MUTED, lw=0.8, ls="--")
axs[0].text(100 * res["fixed"]["0.5"]["P0"]["bar"] + 1, -0.5, "bars: half the\ngenuine FA", color=C.MUTED, fontsize=6.8, va="top")
axs[1].axvline(50, color=C.INK, lw=1, ls="--")
axs[1].text(51, len(ROWS) - 0.5 + 0.25, "50%: paraphrase\neffective", color=C.INK, fontsize=6.8, va="bottom")
axs[2].axvline(1.0, color=C.MUTED, lw=1, ls=":")
axs[2].axvline(D3_BAR, color=C.INK, lw=1, ls="--")
axs[2].text(D3_BAR + 0.01, -0.5, "D3 bar 1.10", color=C.INK, fontsize=6.8, va="top")
for ax in axs[:2]:
    ax.set_xlim(-4, 104)
axs[2].set_xlim(0.55, 1.3)
hs = [Line2D([], [], marker=LMK[lv], color=C.MUTED, ls="", ms=7, label=f"ρ = {float(lv):.2f}") for lv in LEVELS] + \
     [Line2D([], [], marker="s", color=C.MUTED, mfc="white", ls="", ms=7, label="hollow: unchanged by construction, or post hoc")]
fig.legend(handles=hs, fontsize=7.5, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.03))
fig.tight_layout(rect=(0, 0.05, 1, 1))
C.save_fig(fig, "F6")
p = V.save()
print("F6 written; values:", p.name, len(V.d))
