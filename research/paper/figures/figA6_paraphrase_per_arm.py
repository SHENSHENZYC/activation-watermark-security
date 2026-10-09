"""FA6 — paraphrase per arm beside the fixed key (Appendix G): at ρ = 0.35 and 0.50, scrub success by P-Qwen (top) and
detection after paraphrase (bottom) for the fixed key (Study 2), the context-hashed arms h = 1 and h = 4 and rotation
(the union test on Study 2's paraphrases), with 95% intervals where the locked file holds them and the D2 difference d
from the fixed key. Reads study5_v0.1/results.json and study2_v0.1/results.json; asserts medians; writes build/FA6.png
and build/values_figA6.json. Rotation's detection after paraphrase is not in the locked results file and is not drawn.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("figA6")
r5 = C.load(C.OUT / "study5_v0.1" / "results.json")
r2 = C.load(C.OUT / "study2_v0.1" / "results.json")
K = [str(k) for k in C.KEYS]
ORDER = ["fixed", "h1", "h4", "rot"]
SHORT = {"fixed": "fixed key\n(h = 0)", "h1": "context-hashed\nh = 1", "h4": "context-hashed\nh = 4", "rot": "rotation\n(K = 8)"}
plt = C.fig_style()
fig, axs = plt.subplots(2, 2, figsize=(9.2, 6.8), sharex=True)
for j, rho in enumerate(C.LEVELS2):
    t = C.tag(rho)
    S1 = r2["levels"][rho]["S1_qwen"]
    C.chk(S1["success"])
    C.chk(S1["detected_after"])
    assert np.allclose([S1["success"]["per_key"][k] for k in K], [100 * v for v in r5["fixed"][rho]["s2_success"]["per_key"]])
    succ = {"fixed": {"median": S1["success"]["median"], "ci95": S1["success"]["ci95"]}}
    det = {"fixed": {"median": S1["detected_after"]["median"], "ci95": S1["detected_after"]["ci95"]}}
    for a in ("h1", "h4"):
        L = r5["arms"][a]["levels"][rho]
        C.chk(L["para_success"])
        C.chk(L["para_detected"])
        succ[a] = {"median": 100 * L["para_success"]["median"], "ci95": [100 * c for c in L["para_success"]["ci95"]]}
        det[a] = {"median": 100 * L["para_detected"]["median"], "ci95": [100 * c for c in L["para_detected"]["ci95"]]}
    R = r5["rotation"][rho]
    us = [R["per_key"][k]["union_success"] for k in K]
    succ["rot"] = {"median": 100 * float(np.median(us)), "ci95": None}
    det["rot"] = None
    for i, (blk, ylab) in enumerate(((succ, "scrub success (%): not attributed and\nall four quality conditions pass"), (det, "attributed after paraphrase (%)"))):
        ax = axs[i, j]
        for k, arm in enumerate(ORDER):
            v = blk[arm]
            if v is None:
                ax.text(k, 3, "not in the\nlocked file", ha="center", va="bottom", fontsize=7, color=C.MUTED)
                continue
            ax.bar(k, v["median"], width=0.62, color=C.PAL[arm], edgecolor="white", linewidth=1.2, zorder=2)
            if v["ci95"] is not None:
                ax.errorbar(k, v["median"], yerr=[[v["median"] - v["ci95"][0]], [v["ci95"][1] - v["median"]]], fmt="none", ecolor=C.INK, elinewidth=1.1, capsize=3, zorder=3)
                top = v["ci95"][1] + 2
            else:
                top = v["median"] + 2
            ax.text(k, top, f"{v['median']:.0f}", ha="center", va="bottom", fontsize=8, color=C.INK)
        if i == 0:
            ax.axhline(50, color=C.INK, lw=1, ls="--", label="50%: paraphrase effective (Study 2's absolute reading)")
            for k, a in enumerate(("h1", "h4"), start=1):
                D2 = r5["arms"][a]["levels"][rho]["D2"]
                ax.text(k, -9, f"d = {D2['median_diff_points']:+.0f}\n[{D2['ci95'][0]:+.0f}, {D2['ci95'][1]:+.0f}]", ha="center", va="top", fontsize=7, color=C.PAL[a])
                V.set(f"fa6_{a}_{t}_d", f"{D2['median_diff_points']:+.0f} [{D2['ci95'][0]:+.0f}, {D2['ci95'][1]:+.0f}]")
            ax.text(3, -9, f"d = {R['D2']['median_diff_points']:+.0f}\n[{R['D2']['ci95'][0]:+.0f}, {R['D2']['ci95'][1]:+.0f}]", ha="center", va="top", fontsize=7, color=C.PAL["rot"])
            ax.set_ylim(-34, 110)
            ax.set_title(f"ρ = {C.rho_lab(rho)}")
        else:
            ax.set_ylim(0, 110)
        ax.set_xticks(range(4), [SHORT[a] for a in ORDER], fontsize=8)
        if j == 0:
            ax.set_ylabel(ylab)
    V.set(f"fa6_fixed_{t}_success", C.f1(succ["fixed"]["median"]))
    V.set(f"fa6_fixed_{t}_detected", C.f1(det["fixed"]["median"]))
    V.set(f"fa6_rot_{t}_success", C.f1(succ["rot"]["median"]))
    for a in ("h1", "h4"):
        V.set(f"fa6_{a}_{t}_success", C.f1(succ[a]["median"]))
        V.set(f"fa6_{a}_{t}_detected", C.f1(det[a]["median"]))
h, lab = axs[0, 0].get_legend_handles_labels()
fig.legend(h, lab, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, -0.005))
fig.tight_layout(rect=(0, 0.03, 1, 1))
C.save_fig(fig, "FA6")
p = V.save()
print("FA6 written; values:", p.name, len(V.d))
