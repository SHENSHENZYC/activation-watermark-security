"""F4 — the detector's statistic steals the fixed key; the keyed arms against the budget (§5.4, §5.6): key recovery
(cosine with the true key) and forgery FA against n ∈ {64, 256, 1,024} at ρ = 0.35 and 0.50 for the fixed key under
Route A′ (known layer and layer search), the context-hashed arms h = 1 and h = 4 (the per-context attacker's
count-weighted cosine), and rotation (the naive and the clustering attacker), with the D1 bars and the controls. With --pilot a
third row, labelled as a pilot on tuning keys, shows the threat check's recovery at n = 4–100 (build/F4_pilot.png;
not used in the paper by decision of 2026-10-05). Reads study5_v0.1/results.json and study5_threat_v0.1/results.json;
asserts every median against the per-key records; writes build/F4.png and build/values_fig4.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

PILOT = "--pilot" in sys.argv          # decided 2026-10-05 (section-level review): the main-text F4 has no tuning-key row
V = C.Values("fig4_pilot" if PILOT else "fig4")
res = C.load(C.OUT / "study5_v0.1" / "results.json")
thr = C.load(C.OUT / "study5_threat_v0.1" / "results.json")
LEVELS = ["0.35", "0.5"]
NG = [64, 256, 1024]
X = np.log2(np.array(NG, dtype=float))
KEYS = [str(k) for k in range(1001, 1009)]
NAME = {"fixed": "fixed key (h = 0)", "h1": "context-hashed, h = 1", "h4": "context-hashed, h = 4", "rot": "rotation (K = 8)"}
MK = {"fixed": "o", "h1": "s", "h4": "^", "rot": "D"}
plt = C.fig_style()


def chk(d, per_key=None):
    assert abs(float(np.median(d["per_key"])) - d["median"]) < 1e-12 and d["ci95"][0] <= d["median"] + 1e-12 and d["median"] - 1e-12 <= d["ci95"][1]
    if per_key is not None:
        assert abs(float(np.median(per_key)) - d["median"]) < 1e-12
    return d


def line(ax, ys, col, lab, mk, ls="-", hollow=False, ci=None, x=X):
    if ci is not None:
        ax.fill_between(x, [c[0] for c in ci], [c[1] for c in ci], color=col, alpha=0.12, linewidth=0)
    ax.plot(x, ys, ls, color=col, lw=2 if not hollow else 1.4, marker=mk, ms=6.5, mfc="white" if hollow else col, mec=col, label=lab)


def nx(ax, ns=NG):
    xs = np.log2(np.array(ns, dtype=float))
    ax.set_xticks(xs, [f"{n:,}" for n in ns])
    ax.set_xlim(xs[0] - 0.4, xs[-1] + 0.4)
    ax.set_xlabel("observed watermarked texts n")


nrow = 3 if PILOT else 2
fig, axs = plt.subplots(nrow, 2, figsize=(9.6, 3.6 * nrow + 0.4 - (0.9 if PILOT else 0)), gridspec_kw={"height_ratios": [1, 1, 0.75] if PILOT else [1, 1]})
for j, lv in enumerate(LEVELS):
    F, R = res["fixed"][lv], res["rotation"][lv]
    ax = axs[0, j]
    for n in NG:
        assert abs(float(np.median([F["per_key"][k]["cos_known"][str(n)] for k in KEYS])) - F["recovery"][str(n)]["median_cos_known"]) < 1e-12
        assert abs(float(np.median([F["per_key"][k]["cos_search"][str(n)] for k in KEYS])) - F["recovery"][str(n)]["median_cos_search"]) < 1e-12
    line(ax, [F["recovery"][str(n)]["median_cos_known"] for n in NG], C.PAL["fixed"], "fixed key, Route A′, known layer", MK["fixed"])
    line(ax, [F["recovery"][str(n)]["median_cos_search"] for n in NG], C.PAL["fixed"], "fixed key, Route A′, layer search", MK["fixed"], ls="--", hollow=True)
    for a in ("h1", "h4"):
        L = res["arms"][a]["levels"][lv]
        line(ax, [L["recovery"][str(n)]["cos_weighted"] for n in NG], C.PAL[a], f"{NAME[a]}: count-weighted cos", MK[a])
    line(ax, [C.med([c["best_cos"] for c in R["cluster"][str(n)]["clusters"].values()]) for n in NG], C.PAL["rot"], "rotation: clustering attacker (median cluster)", MK["rot"])
    line(ax, [max(R["naive"][str(n)].values()) for n in NG], C.PAL["rot"], "rotation: naive attacker (best key)", MK["rot"], ls="--", hollow=True)
    ax.set_ylim(-0.03, 1.03)
    ax.set_title(f"ρ = {float(lv):.2f}: key recovery (study keys)")
    nx(ax)
    ax = axs[1, j]
    for n in NG:
        chk(F["forge_FA"][str(n)], [F["per_key"][k]["forge_FA"][str(n)] for k in KEYS])
    line(ax, [100 * F["forge_FA"][str(n)]["median"] for n in NG], C.PAL["fixed"], "fixed key", MK["fixed"], ci=[[100 * c for c in F["forge_FA"][str(n)]["ci95"]] for n in NG])
    for a in ("h1", "h4"):
        L = res["arms"][a]["levels"][lv]
        for n in NG:
            chk(L["forge_FA"][str(n)], [L["per_key"][k]["forge_FA"][str(n)] for k in KEYS])
        line(ax, [100 * L["forge_FA"][str(n)]["median"] for n in NG], C.PAL[a], NAME[a], MK[a], ci=[[100 * c for c in L["forge_FA"][str(n)]["ci95"]] for n in NG])
    for who, ls, hol, lab in (("cluster", "-", False, "rotation, clustering attacker"), ("naive", "--", True, "rotation, naive attacker")):
        line(ax, [100 * R["forge_FA"][who][str(n)]["mean"] for n in NG], C.PAL["rot"], lab, MK["rot"], ls=ls, hollow=hol, ci=[[100 * c for c in R["forge_FA"][who][str(n)]["ci95"]] for n in NG])
    bars = [100 * F["P0"]["bar"]] + [100 * res["arms"][a]["levels"][lv]["D1"]["bar"] for a in ("h1", "h4")]
    ax.axhspan(min(bars), max(bars), color=C.GRID, alpha=0.9, zorder=0, label=f"bar: half of each arm's genuine FA ({min(bars):.0f}–{max(bars):.0f}%)")
    ctrl = [100 * F["random_FA"]["median"]] + [100 * res["arms"][a]["levels"][lv]["control_FA"]["median"] for a in ("h1", "h4")]
    ax.axhline(max(ctrl), color=C.CTRL, lw=1, ls=":", label=f"random-key / random-secret controls (max {max(ctrl):.0f}%)")
    ax.set_ylim(-3, 104)
    ax.set_title(f"ρ = {float(lv):.2f}: forgery acceptance (study keys)")
    nx(ax)
    if PILOT:
        ax = axs[2, j]
        TL = thr["levels"][lv]
        tn = thr["n_grid"]
        for est, lab, col, mk, ls, hol in (("grad", "Route A′ (gradient mean, layer search)", C.PAL["fixed"], "o", "-", False), ("act", "Route A (activation mean)", C.PAL["A"], "^", "-", False)):
            ys = [TL["median"][str(n)][est]["cos"] for n in tn]
            for n in tn:
                pk = [TL["per_key"][k][str(n)][est]["cos"] for k in TL["per_key"]]
                assert abs(float(np.median(pk)) - TL["median"][str(n)][est]["cos"]) < 1e-9
            line(ax, ys, col, lab, mk, ls=ls, hollow=hol, x=np.log2(np.array(tn, dtype=float)))
        ax.set_ylim(-0.03, 1.03)
        ax.set_title(f"ρ = {float(lv):.2f}: key recovery on the tuning keys (pilot)")
        nx(ax, tn)
axs[0, 0].set_ylabel("cosine with the true key (median over 8 keys)")
axs[1, 0].set_ylabel("forgery FA (%): attributed at p ≤ 0.01 and fluent")
if PILOT:
    axs[2, 0].set_ylabel("cosine with the true key\n(median over 4 tuning keys)")
for i in range(nrow):
    h, lab = axs[i, 0].get_legend_handles_labels()
    axs[i, 1].legend(h, lab, fontsize=7, loc="upper left", bbox_to_anchor=(1.02, 1.0))
fig.tight_layout()
C.save_fig(fig, "F4_pilot" if PILOT else "F4")
V.set("f4_pilot_variant" if PILOT else "f4_pilot_row", "yes" if PILOT else "no")
V.set("f4_threat_n_grid", ", ".join(str(n) for n in thr["n_grid"]))
p = V.save()
print("F4 written; values:", p.name, len(V.d))
