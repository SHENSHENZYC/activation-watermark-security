"""FA4 — the per-context attacker's mechanics on the context-hashed arms (Appendix C): against the budget n, (a) the
coverage of a genuine text's positions by estimated contexts, (b) the number of contexts estimated (seen at least 16
times), and (c) at n = 1,024 the cosine of the per-context estimates with the true per-context keys by how often the
context was seen (median over keys). Reads study5_v0.1/results.json; asserts the medians against the per-key records;
writes build/FA4.png and build/values_figA4.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("figA4")
r5 = C.load(C.OUT / "study5_v0.1" / "results.json")
K = [str(k) for k in C.KEYS]
NS = ["64", "256", "1024"]
BINS, BLAB = ["16", "32", "128", "512"], ["16–31", "32–127", "128–511", "≥ 512"]
plt = C.fig_style()
fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.7))
for a in ("h1", "h4"):
    h = r5["arms"][a]["h"]
    for rho in C.LEVELS2:
        L = r5["arms"][a]["levels"][rho]
        cov = [L["recovery"][n]["coverage"] for n in NS]
        ctx = [L["recovery"][n]["n_contexts"] for n in NS]
        for n in NS:
            assert abs(np.median([L["per_key"][k]["attacker"][n]["coverage_genuine"] for k in K]) - L["recovery"][n]["coverage"]) < 1e-9
            assert abs(np.median([L["per_key"][k]["attacker"][n]["n_contexts"] for k in K]) - L["recovery"][n]["n_contexts"]) < 1e-9
        ls, hol = ("-", False) if rho == "0.5" else ("--", True)
        x = np.log2([float(n) for n in NS])
        lab = f"h = {h}, ρ = {C.rho_lab(rho)}"
        for ax, y in ((axs[0], cov), (axs[1], ctx)):
            ax.plot(x, y, ls, color=C.PAL[a], lw=1.8, marker="^" if a == "h1" else "v", ms=6.5, mfc="white" if hol else C.PAL[a], mec=C.PAL[a], label=lab)
        t = C.tag(rho)
        V.set(f"fa4_{a}_{t}_cov_n1024", C.f3(cov[-1]))
        V.set(f"fa4_{a}_{t}_ctx_n1024", f"{ctx[-1]:,.0f}")
        V.set(f"fa4_{a}_{t}_cov_n64", C.f3(cov[0]))
        V.set(f"fa4_{a}_{t}_ctx_n64", f"{ctx[0]:,.0f}")
        V.set(f"fa4_{a}_{t}_cosw_n1024", C.f3(L["recovery"]["1024"]["cos_weighted"]))
for ai, a in enumerate(("h1", "h4")):
    for li, rho in enumerate(C.LEVELS2):
        L = r5["arms"][a]["levels"][rho]
        vals = []
        for b in BINS:
            xs = [L["per_key"][k]["attacker"]["1024"]["cos_by_count"].get(b) for k in K]
            xs = [x for x in xs if x is not None]
            vals.append(float(np.median(xs)) if xs else np.nan)
            V.set(f"fa4_{a}_{C.tag(rho)}_cosbin_{b}", C.f3(vals[-1]) if xs else "—")
        xpos = np.arange(4) + (-0.3 + 0.2 * (2 * ai + li))
        axs[2].bar(xpos, vals, width=0.18, color=C.PAL[a], alpha=0.55 if rho == "0.35" else 1.0, edgecolor="white", linewidth=0.8, label=f"h = {r5['arms'][a]['h']}, ρ = {C.rho_lab(rho)}")
axs[2].set_xticks(range(4), BLAB)
axs[2].set_xlabel("times the context was seen among the n = 1,024 observed texts")
axs[2].set_ylabel("cos with the true per-context key\n(median over keys)")
axs[2].axhline(0, color=C.MUTED, lw=0.8)
axs[2].set_title("(c) accuracy by context count, n = 1,024")
for ax, ttl in ((axs[0], "(a) coverage of a genuine text's positions"), (axs[1], "(b) contexts estimated (seen ≥ 16 times)")):
    ax.set_xticks(np.log2([64, 256, 1024]), ["64", "256", "1,024"])
    ax.set_xlabel("observed watermarked texts n")
    ax.set_title(ttl)
axs[0].set_ylabel("share of a genuine text's positions covered")
axs[0].set_ylim(-0.03, 1.03)
axs[1].set_yscale("symlog", linthresh=10)
axs[1].set_ylim(0, 3000)
axs[1].set_ylabel("contexts with an estimate")
axs[0].legend(fontsize=7, loc="upper left")
axs[2].legend(fontsize=7, loc="upper left")
fig.tight_layout()
C.save_fig(fig, "FA4")
p = V.save()
print("FA4 written; values:", p.name, len(V.d))
