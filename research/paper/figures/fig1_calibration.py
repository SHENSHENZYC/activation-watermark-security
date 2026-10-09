"""F1 — calibration (§5.1): (a) the authors' MLP probe's AUROC and (b) the perplexity ratio against ρ on Llama-3.2-1B,
Qwen2.5-1.5B and Llama-3.2-3B at 256 tokens, with the 512-token points for the first two, the two bars (AUROC 0.95;
ratio 1.25) and the published α = 5 marked as a ρ per model; no model crosses both bars at the same ρ. Reads
calibration_v0.1, v0.2 and v0.3 and repro_v0.1 (with its perplexity addendum); asserts operating_point is None in every
calibration file and the plotted values equal the per-ρ records; writes build/F1.png and build/values_fig1.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("fig1")
O = C.OUT
add = C.load(O / "repro_v0.1" / "addendum_quality_ppl.json")
MODELS = [("l1b", "Llama-3.2-1B", "m_llama1b", "s", O / "calibration_v0.1" / "results_llama.json", O / "calibration_v0.2" / "results_llama.json", O / "repro_v0.1" / "results_llama.json", "llama"),
          ("q15", "Qwen2.5-1.5B (the study model)", "m_qwen", "o", O / "calibration_v0.1" / "results_qwen.json", O / "calibration_v0.2" / "results_qwen.json", O / "repro_v0.1" / "results_qwen.json", "qwen"),
          ("l3b", "Llama-3.2-3B", "m_llama3b", "^", O / "calibration_v0.3" / "results_llama3b.json", None, None, None)]
plt = C.fig_style()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 6.6), sharex=True)
for tag, name, colk, mk, p256, p512, prepro, rtag in MODELS:
    c1 = C.load(p256)
    assert c1["operating_point"] is None and not any(d["detectable"] and d["fluent"] for d in c1["per_rho"].values())
    rhos = sorted(c1["per_rho"], key=float)
    x = [float(r) for r in rhos]
    au = [c1["per_rho"][r]["auroc"]["mlp_faithful"] for r in rhos]
    pr = [c1["per_rho"][r]["ppl_ratio"] for r in rhos]
    for r in rhos:
        per = [c1["per_key"][r][k]["mlp_faithful"]["auroc"] for k in c1["per_key"][r]]
        assert abs(float(np.mean(per)) - c1["per_rho"][r]["auroc"]["mlp_faithful"]) < 1e-9
    col = C.PAL[colk]
    ax1.plot(x, au, "-", color=col, lw=2, marker=mk, ms=6.5, label=f"{name}, 256 tokens")
    ax2.plot(x, pr, "-", color=col, lw=2, marker=mk, ms=6.5, label=f"{name}, 256 tokens")
    if p512:
        c2 = C.load(p512)
        assert c2["operating_point"] is None and c2["meta"]["tokens"] == 512
        r5 = sorted(c2["per_rho"], key=float)
        ax1.plot([float(r) for r in r5], [c2["per_rho"][r]["auroc"]["mlp_faithful"] for r in r5], ls="", marker=mk, ms=7, mfc="white", mec=col, mew=1.4, label=f"{name}, 512 tokens")
        ax2.plot([float(r) for r in r5], [c2["per_rho"][r]["ppl_ratio"] for r in r5], ls="", marker=mk, ms=7, mfc="white", mec=col, mew=1.4, label=f"{name}, 512 tokens")
    if prepro:
        rp = C.load(prepro)
        m = rp["meta"]
        rho5 = 5 * m["key_norm_per_alpha1"] / m["act_norm_median_unsteered"]
        au5 = rp["summary"]["cont_a5"]["mlp_faithful"]["auroc"]
        assert abs(float(np.mean([rp["per_key"]["cont_a5"][k]["mlp_faithful"]["auroc"] for k in rp["per_key"]["cont_a5"]])) - au5) < 1e-9
        ratio5 = add[f"{rtag}_a5"]["median"] / add[f"{rtag}_van"]["median"]
        ax1.plot([rho5], [au5], ls="", marker="*", ms=13, color=col, mec="white", mew=0.8, zorder=4, label=f"{name}: the published α = 5 (ρ = {rho5:.2f}; pilot)")
        ax2.plot([rho5], [ratio5], ls="", marker="*", ms=13, color=col, mec="white", mew=0.8, zorder=4, label=f"{name}: the published α = 5 (ρ = {rho5:.2f}; pilot)")
        if rho5 > 1:      # the Llama-3.2-1B star sits alone at the right: label to its left
            ax1.annotate(f"α = 5 (ρ = {rho5:.2f})", (rho5, au5), xytext=(rho5 - 0.03, au5 - 0.03), fontsize=6.8, color=col, ha="right", va="top")
            ax2.annotate(f"α = 5 (ρ = {rho5:.2f})", (rho5, ratio5), xytext=(rho5 - 0.03, ratio5), fontsize=6.8, color=col, ha="right", va="center")
        else:             # the Qwen star sits below and left of the grid: label below it, and above the bar in (b)
            ax1.annotate(f"α = 5\n(ρ = {rho5:.2f})", (rho5, au5), xytext=(rho5 - 0.035, au5 + 0.035), fontsize=6.8, color=col, ha="left", va="bottom")
            ax2.annotate(f"α = 5 (ρ = {rho5:.2f})", (rho5, ratio5), xytext=(rho5 - 0.03, 1.36), fontsize=6.8, color=col, ha="left", va="bottom")
        V.set(f"f1_{tag}_a5_rho", C.f2(rho5))
    else:
        rho5 = 5 * 0.5 / c1["per_rho"]["0.5"]["alpha_equiv"]
        for ax in (ax1, ax2):
            ax.axvline(rho5, color=col, lw=0.9, ls=":")
        ax1.text(rho5 + 0.01, 0.41, f"α = 5 on {name.split(' (')[0]}\n(ρ ≈ {rho5:.2f}; not run)", color=col, fontsize=6.8, va="bottom")
        V.set(f"f1_{tag}_a5_rho", C.f2(rho5))
ax1.axhline(0.95, color=C.INK, lw=1, ls="--")
ax1.text(0.07, 0.95 + 0.012, "detectable: AUROC ≥ 0.95", color=C.INK, fontsize=7.2, ha="left", va="bottom")
ax1.set_ylabel("authors' MLP probe: AUROC\n(mean over 4 tuning keys)")
ax1.set_ylim(0.4, 1.03)
ax1.set_title("(a) detectability")
ax2.axhline(1.25, color=C.INK, lw=1, ls="--")
ax2.text(1.33, 1.25 * 1.03, "fluent: perplexity ratio ≤ 1.25", color=C.INK, fontsize=7.2, ha="right", va="bottom")

ax2.set_yscale("log")
ax2.set_yticks([1, 1.25, 1.5, 2, 3, 5], ["1", "1.25", "1.5", "2", "3", "5"])
from matplotlib.ticker import NullFormatter  # noqa: E402
ax2.yaxis.set_minor_formatter(NullFormatter())
ax2.set_yticks([], minor=True)
ax2.set_ylabel("perplexity ratio, steered / unsteered\n(medians; the same model, no steering)")
ax2.set_xlabel(C.XLAB_RHO)
ax2.set_title("(b) quality")
ax2.set_xlim(0.05, 1.36)
ax2.set_xticks([0.15, 0.25, 0.35, 0.5, 0.7, 1.0, 1.29], ["0.15", "0.25", "0.35", "0.50", "0.70", "1.00", "1.29"])
h, lab = ax1.get_legend_handles_labels()
ax2.legend(h, lab, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
fig.tight_layout()
C.save_fig(fig, "F1")
V.set("f1_n_models", len(MODELS))
p = V.save()
print("F1 written; values:", p.name, len(V.d))
