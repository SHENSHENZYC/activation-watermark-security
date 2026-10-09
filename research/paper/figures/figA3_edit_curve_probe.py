"""FA3 — scrubbing secondaries (Appendix F): top row, scrub success against the edit budget (0, 2, 5, 10% of the tokens)
for the true key, the attacker's estimate and random edits, per strength, with 95% bands and the 50% bar (0% is the
originals' miss rate); bottom row, the owner's probe (hollow) against the exact test S4 (filled) on the same scrubbed
texts, per method and strength (the C11 lead, labelled). Reads study2_v0.1/results.json and, for the unscrubbed probe
rate, study3_v0.1/results.json; asserts every median; writes build/FA3.png and build/values_figA3.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("figA3")
res = C.load(C.OUT / "study2_v0.1" / "results.json")
r3 = C.load(C.OUT / "study3_v0.1" / "results.json")
SEC = res["secondary"]
ARMS = [("true", "E-true (true key)"), ("est", "E-est (Route A estimate)"), ("rand", "E-rand (random)")]
MK = {"true": "^", "est": "D", "rand": "v"}
XB, B = [0, 2, 5, 10], ["0.02", "0.05", "0.1"]
plt = C.fig_style()
fig, axs = plt.subplots(2, 4, figsize=(11.0, 6.6))
for j, rho in enumerate(C.LEVELS4):
    L = res["levels"][rho]
    miss = L["S1_qwen"]["originals_miss"]["median"]
    ax = axs[0, j]
    for a, lab in ARMS:
        ds = [L[f"E-{a} {b}"]["success"] for b in B]
        for d in ds:
            C.chk(d)
        y = [miss] + [d["median"] for d in ds]
        lo = [miss] + [d["ci95"][0] for d in ds]
        hi = [miss] + [d["ci95"][1] for d in ds]
        ax.fill_between(XB, lo, hi, color=C.PAL[a], alpha=0.12, linewidth=0)
        ax.plot(XB, y, "--" if a == "rand" else "-", color=C.PAL[a], lw=2, marker=MK[a], ms=6, label=lab)
    ax.axhline(50, color=C.INK, lw=1, ls="--")
    ax.axvline(5, color=C.MUTED, lw=1, ls=":")
    ax.set_xticks(XB)
    ax.set_xlim(-0.6, 10.6)
    ax.set_ylim(-3, 104)
    ax.set_title(f"ρ = {C.rho_lab(rho)}")
    ax.set_xlabel("edited tokens (%)")
    if j == 0:
        ax.set_ylabel("scrub success (%)")
        ax.text(5.3, 100, "judged\nat 5%", color=C.MUTED, fontsize=7, va="top", ha="left")
    # bottom: probe vs S4 dumbbell
    ax = axs[1, j]
    RW = [("unscrubbed", None)] + [(lab, f"para_{m}_gen") for m, lab in (("qwen", "P-Qwen"), ("phi", "P-Phi"))] + [(f"{lab.split(' (')[0]} 5%", f"edit_{a}_0.05") for a, lab in ARMS]
    for i, (lab, nm) in enumerate(RW):
        if nm is None:
            pr, ex = 100 * r3["S4"]["levels"][rho]["oracle"]["probe_acceptance_median"], L["P1"]["detected_before"]["median"]
        else:
            pr = SEC["probe"][nm][rho]
            ex = (L[f"S1_{nm.split('_')[1]}"] if nm.startswith("para") else L[f"E-{nm.split('_')[1]} 0.05"])["detected_after"]["median"]
        ax.plot([pr, ex], [i, i], color=C.GRID, lw=2.4, zorder=1)
        ax.scatter([pr], [i], s=44, color="white", edgecolor=C.CTRL, linewidth=1.4, zorder=2, label="the owner's probe" if i == 0 else None)
        ax.scatter([ex], [i], s=44, color=C.PAL["exact"], edgecolor="white", linewidth=0.8, zorder=3, label="the exact test S4" if i == 0 else None)
    ax.axvline(1, color=C.MUTED, lw=1, ls=":")
    ax.set_xlim(-4, 104)
    ax.set_yticks(range(len(RW)), [r[0] for r in RW] if j == 0 else [""] * len(RW), fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("scrubbed texts still attributed (%)")
    if j == 0:
        ax.set_title("the probe vs the exact test on the same texts (lead, labelled)")
h, lab = axs[0, 0].get_legend_handles_labels()
h2, lab2 = axs[1, 0].get_legend_handles_labels()
fig.legend(h + h2, lab + lab2, fontsize=7.5, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(rect=(0, 0.05, 1, 1))
C.save_fig(fig, "FA3")
for rho in C.LEVELS4:
    t = C.tag(rho)
    V.set(f"fa3_Etrue_10_{t}", C.f1(res["levels"][rho]["E-true 0.1"]["success"]["median"]))
    V.set(f"fa3_probe_Pqwen_{t}", C.f1(SEC["probe"]["para_qwen_gen"][rho]))
    V.set(f"fa3_S4_Pqwen_{t}", C.f1(res["levels"][rho]["S1_qwen"]["detected_after"]["median"]))
p = V.save()
print("FA3 written; values:", p.name, len(V.d))
