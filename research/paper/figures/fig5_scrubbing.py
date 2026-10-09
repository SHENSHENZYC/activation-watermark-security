"""F5 — scrubbing under the exact test (§5.5): detection after scrubbing (top) and scrub success (bottom) against ρ for
the two paraphrasers (with the length-matched controls and the originals' miss rate) and for the 5% word edits (true
key, the attacker's estimate, random), with the 50% bar. Reads study2_v0.1/results.json (percent units); asserts every
plotted median against the per-key rates; writes build/F5.png and build/values_fig5.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("fig5")
res = C.load(C.OUT / "study2_v0.1" / "results.json")
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
RHO = [float(v) for v in LEVELS]
MODELS, ARMS, B5, BAR = ["qwen", "phi"], ["true", "est", "rand"], "0.05", 50
SHORT = {"qwen": "P-Qwen", "phi": "P-Phi", "true": "E-true (true key)", "est": "E-est (Route A estimate)", "rand": "E-rand (random)"}
MK = {"qwen": "o", "phi": "s", "true": "^", "est": "D", "rand": "v"}
plt = C.fig_style()


def chk(d):
    pk = list(d["per_key"].values())
    assert len(pk) == 8 and abs(float(np.median(pk)) - d["median"]) < 1e-9 and d["ci95"][0] <= d["median"] + 1e-9 and d["median"] - 1e-9 <= d["ci95"][1]
    return d


def band(ax, ys, col, lab, mk, ls="-", hollow=False, ci=None):
    if ci is not None:
        ax.fill_between(RHO, [c[0] for c in ci], [c[1] for c in ci], color=col, alpha=0.12, linewidth=0)
    ax.plot(RHO, ys, ls, color=col, lw=2 if not hollow else 1.4, marker=mk, ms=6.5, mfc="white" if hollow else col, mec=col, label=lab)


fig, axs = plt.subplots(2, 2, figsize=(9.6, 7.6), sharex=True)
before = [chk(res["levels"][lv]["P1"]["detected_before"]) for lv in LEVELS]
for ax in axs[0]:
    band(ax, [b["median"] for b in before], C.INK, "unscrubbed originals", "o", ci=[b["ci95"] for b in before])
for m in MODELS:
    d = [chk(res["levels"][lv][f"S1_{m}"]["detected_after"]) for lv in LEVELS]
    band(axs[0, 0], [x["median"] for x in d], C.PAL[m], SHORT[m], MK[m], ci=[x["ci95"] for x in d])
    band(axs[0, 0], [res["secondary"]["length_matched"][m][lv] for lv in LEVELS], C.PAL[m], f"{SHORT[m]}: originals cut to the paraphrase's length", MK[m], ls="--", hollow=True)
    s = [chk(res["levels"][lv][f"S1_{m}"]["success"]) for lv in LEVELS]
    band(axs[1, 0], [x["median"] for x in s], C.PAL[m], SHORT[m], MK[m], ci=[x["ci95"] for x in s])
miss = [chk(res["levels"][lv]["S1_qwen"]["originals_miss"])["median"] for lv in LEVELS]
band(axs[1, 0], miss, C.CTRL, "originals' miss rate", "o", ls=":", hollow=True)
for a in ARMS:
    d = [chk(res["levels"][lv][f"E-{a} {B5}"]["detected_after"]) for lv in LEVELS]
    s = [chk(res["levels"][lv][f"E-{a} {B5}"]["success"]) for lv in LEVELS]
    ls = "--" if a == "rand" else "-"
    band(axs[0, 1], [x["median"] for x in d], C.PAL[a], SHORT[a], MK[a], ls=ls, ci=[x["ci95"] for x in d])
    band(axs[1, 1], [x["median"] for x in s], C.PAL[a], SHORT[a], MK[a], ls=ls, ci=[x["ci95"] for x in s])
for ax in axs[1]:
    ax.axhline(BAR, color=C.INK, lw=1, ls="--")
    ax.text(0.775, BAR + 1.5, "50% bar", color=C.INK, fontsize=7.5, ha="right", va="bottom")
    ax.set_xlabel(C.XLAB_RHO)
for ax in axs.flat:
    ax.set_xticks(RHO)
    ax.set_xlim(0.22, 0.78)
    ax.set_ylim(-3, 104)
axs[0, 0].set_ylabel("attributed by the exact test at p ≤ 0.01 (%)")
axs[1, 0].set_ylabel("scrub success (%): not attributed and\nall four quality conditions pass")
axs[0, 0].set_title("paraphrase (no key)")
axs[0, 1].set_title("word edits at 5% of the tokens")
for j in range(2):
    h, lab = axs[0, j].get_legend_handles_labels()
    h2, lab2 = axs[1, j].get_legend_handles_labels()
    extra = [(a, b) for a, b in zip(h2, lab2) if b not in lab]
    axs[1, j].legend(h + [a for a, _ in extra], lab + [b for _, b in extra], fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
fig.tight_layout()
C.save_fig(fig, "F5")
for lv in LEVELS:
    V.set(f"f5_S1_qwen_{lv.replace('.', '')}", res["levels"][lv]["S1_qwen"]["verdict"])
p = V.save()
print("F5 written; values:", p.name, len(V.d))
