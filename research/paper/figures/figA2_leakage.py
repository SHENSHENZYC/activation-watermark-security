"""FA2 — key leakage (Appendix D): (a) Study 3: each forgery set's exact acceptance per key against the attacker's recovered
cosine with that key (one point per key, strength and forgery set; Routes A and B; attacker versions v0.2–v0.4), with
the nominal 1%; (b) Study 2: E-est's scrub success at 5% against the same cosine (Route A, n = 1,024; one point per key
and strength) with the 50% bar. Reads study3_v0.1 and study2_v0.1 results.json; re-computes the Spearman correlations
and the ≥ 50% cell count; writes build/FA2.png and build/values_figA2.json.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("figA2")
r3 = C.load(C.OUT / "study3_v0.1" / "results.json")
r2 = C.load(C.OUT / "study2_v0.1" / "results.json")
P = r3["S4"]["levels"]
pts = {"A": [], "B": []}
MK = {"v02": "o", "v03": "s", "v04": "D"}
for rho in C.LEVELS4:
    sets = [f"v02_{r}_n{n}" for r in "AB" for n in (64, 256, 1024)]
    if rho != "0.25":
        sets += [f"{v}_{r}_n{n}" for v in ("v03", "v04") for r in "AB" for n in (64, 256)]
    for s in sets:
        d = P[rho][s]
        assert len(d["cos_to_key_per_key"]) == 8 and np.allclose(d["acceptance_per_key"], d["acceptance"]["per_key"])
        route, ver = s.split("_")[1], s.split("_")[0]
        pts[route] += [(ver, c, a) for c, a in zip(d["cos_to_key_per_key"], d["acceptance_per_key"])]
assert len(pts["A"]) == 192 and len(pts["B"]) == 192
plt = C.fig_style()
fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.0))
ax = axs[0]
for r in "AB":
    for ver in MK:
        sel = [(c, a) for v, c, a in pts[r] if v == ver]
        ax.scatter([c for c, _ in sel], [100 * a for _, a in sel], s=24, marker=MK[ver], color=C.PAL[r], alpha=0.75, edgecolor="white", linewidth=0.5,
                   label=f"Route {r}, {ver.replace('v0', 'v0.')}")
ax.axhline(1, color=C.MUTED, lw=1, ls=":")
ax.text(0.99, 2, "nominal 1%", color=C.MUTED, fontsize=7.5, ha="right", va="bottom")
ax.set_xlabel("attacker's recovered cosine cos(v̂, v) with the key")
ax.set_ylabel("forgeries attributed by the exact test (%)")
ax.set_title("(a) Study 3: one point per key, strength and forgery set")
ax.legend(fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18))
ax.set_xlim(-0.05, 1.02)
ax.set_ylim(-3, 104)
for r in "AB":
    rho_s, _ = spearmanr([c for _, c, _ in pts[r]], [a for _, _, a in pts[r]])
    V.set(f"fa2_spearman_{r}", C.f2(rho_s))
cells = sum(a >= 0.5 for r in "AB" for _, _, a in pts[r])
V.set("fa2_cells_ge50", cells)
V.set("fa2_cells_total", 384)
V.set("fa2_B_low_cos_ge50", sum(a >= 0.5 and c < 0.2 for _, c, a in pts["B"]))
V.set("fa2_A_low_cos_ge50", sum(a >= 0.5 and c < 0.2 for _, c, a in pts["A"]))
V.set("fa2_A_hi_cos_ge50", sum(a >= 0.5 and c >= 0.5 for _, c, a in pts["A"]))
V.set("fa2_A_hi_cos_total", sum(c >= 0.5 for _, c, _ in pts["A"]))
ax = axs[1]
kl = r2["secondary"]["key_leakage"]["per_key_level"]
assert len(kl) == 32
LMK = {"0.25": "o", "0.35": "s", "0.5": "D", "0.7": "^"}
ALP = {"0.25": 0.35, "0.35": 0.55, "0.5": 0.75, "0.7": 1.0}
for i, rho in enumerate(C.LEVELS4):
    sel = [kl[k * 4 + i] for k in range(8)]
    ax.scatter([q["cos"] for q in sel], [100 * q["success"] for q in sel], s=34, marker=LMK[rho], color=C.PAL["est"], alpha=ALP[rho], edgecolor="white", linewidth=0.5,
               label=f"ρ = {C.rho_lab(rho)}")
ax.axhline(50, color=C.INK, lw=1, ls="--")
ax.text(0.99, 51.5, "50% bar", color=C.INK, fontsize=7.5, ha="right", va="bottom")
ax.set_xlabel("attacker's recovered cosine cos(v̂, v) (Study 1 v0.2, Route A, n = 1,024)")
ax.set_ylabel("E-est scrub success at 5% of the tokens (%)")
ax.set_title("(b) Study 2: one point per key and strength")
ax.legend(fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18))
ax.set_xlim(-0.05, 1.02)
ax.set_ylim(-3, 104)
rs, _ = spearmanr([q["cos"] for q in kl], [q["success"] for q in kl])
assert abs(rs - kl_sp) < 1e-9 if (kl_sp := r2["secondary"]["key_leakage"]["spearman_success_vs_cos"]) is not None else True
V.set("fa2_s2_spearman", C.f2(kl_sp))
V.set("fa2_s2_cos_max", C.f2(max(q["cos"] for q in kl)))
V.set("fa2_s2_ge50", sum(q["success"] >= 0.5 for q in kl))
fig.tight_layout()
C.save_fig(fig, "FA2")
p = V.save()
print("FA2 written; values:", p.name, len(V.d))
