"""Build the Study 1 v0.2 report tables and figures from the locked outputs (numbers are never retyped).

Reads research/outputs/study1_v0.2/results.json and the per-key summaries in research/study1_v02/data/
(git-ignored), re-computes every per-key acceptance and median from the raw scores, and asserts that they equal
results.json before writing anything. Writes to research/outputs/study1_v0.2/report/:
  tables.md          Tables 1-4 (Table 4 and the fluent-forgery count are EXPLORATORY, added after the run)
  exploratory.json   the per-key quality breakdown behind Table 4
  fig1_acceptance.png, fig2_quality.png, fig3_recovery.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "outputs" / "study1_v0.2" / "results.json"
DATA = ROOT / "study1_v02" / "data"
OUT = ROOT / "outputs" / "study1_v0.2" / "report"
KEYS = list(range(1001, 1009))
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
TAG = {"0.25": "025", "0.35": "035", "0.5": "050", "0.7": "070"}
FORGE_N = [64, 256, 1024]
REC_N = [1, 4, 16, 64, 256, 1024]
CONDS = ["oracle", "random"] + [f"forge_{r}_n{n}" for r in "AB" for n in FORGE_N]
LAYER = 14
# Exploratory cut-off, chosen AFTER seeing the data (not pre-registered): a key-level forgery is "fluent" if its
# median perplexity is at most 1.5x that key-level's oracle (genuinely watermarked) median.
FLUENT_RATIO = 1.5
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dc"
COL = {"A": "#2a78d6", "B": "#eb6834"}  # categorical slots 1-2 (validated: ALL CHECKS PASS, light mode)

res = json.loads(RES.read_text())
S = {(s, lv): json.loads((DATA / f"K_k{s}_r{TAG[lv]}_summary.json").read_text()) for s in KEYS for lv in LEVELS}


def acc(s, lv, c):
    x = S[(s, lv)]
    return np.asarray(x[f"scores_{c}"]) > x["threshold"]


# ---- integrity: re-computed numbers equal the locked results
assert len(S) == 32
fpr = np.mean([np.mean(np.asarray(S[k]["scores_A2"]) > S[k]["threshold"]) for k in S])
assert abs(fpr - res["G1_pooled_FPR_A2"]) < 1e-12, (fpr, res["G1_pooled_FPR_A2"])
for lv in LEVELS:
    L = res["levels"][lv]
    for c in CONDS:
        pk = [float(acc(s, lv, c).mean()) for s in KEYS]
        assert all(len(acc(s, lv, c)) == 100 for s in KEYS)
        assert pk == L[c]["per_key"] and float(np.median(pk)) == L[c]["median"], (lv, c)
    for n in REC_N:
        e = [S[(s, lv)]["estimates"][str(n)] for s in KEYS]
        assert int(sum(x["A"]["layer"] == LAYER for x in e)) == L["recovery"][str(n)]["layer_hits_A"]
        assert float(np.median([x["A"]["cos"] for x in e])) == L["recovery"][str(n)]["median_cos_A"]
OUT.mkdir(parents=True, exist_ok=True)


def pct(x):
    return f"{100 * x:.1f}"


def ci(c):
    return f"[{pct(c[0])}, {pct(c[1])}]"


T = []
# ---- Table 1: pre-registered rules vs observed
T.append("## Table 1 — Pre-registered rules vs observed (protocol §10)\n")
T.append(f"G1 (pooled FPR on pool A2 within [0.3%, 2.5%]): observed **{pct(res['G1_pooled_FPR_A2'])}%** → "
         f"**{'PASS' if res['gates']['G1'] else 'FAIL'}**. G2 (attack isolation): {res['gates']['G2']}. "
         f"Descriptive: FPR on the human continuations of A2 = {pct(res['human_FPR_A2'])}%.\n")
T.append("| ρ | Oracle median acceptance (L1: ≥ 20%) | L1 | R1 key recovery (Route A) | R2 Route A | R2 Route B | "
         "Random-key median | R3 generic steering suffices (random ≥ 50% of oracle) |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    r = L["rules"]
    T.append(f"| {lv} | {pct(L['oracle']['median'])}% | {'pass' if r['L1_working_watermark'] else 'fail'} | {r['R1']} | "
             f"{r['R2']['A']} | {r['R2']['B']} | {pct(L['random']['median'])}% | {'yes' if r['R3_generic_steering_suffices'] else 'no'} |")
T.append("\nLevels failing L1 are descriptive only (protocol §10).\n")

# ---- Table 2: acceptance at 1% FPR
T.append("## Table 2 — Acceptance by the owner's detector at its 1%-FPR threshold (median over 8 keys, % [95% cluster-bootstrap CI]; "
         "median perplexity of the texts under the unsteered model)\n")
T.append("| ρ | Oracle (true key) | Random key | A n=64 | A n=256 | A n=1024 | B n=64 | B n=256 | B n=1024 |")
T.append("|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    T.append(f"| {lv} | " + " | ".join(f"{pct(L[c]['median'])} {ci(L[c]['ci95'])}" for c in CONDS) + " |")
    T.append("| ppl | " + " | ".join(f"{L[c]['ppl_median']:.1f}" for c in CONDS) + " |")


def auroc(pos, neg):
    """Mann-Whitney AUROC (ties count one half)."""
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


T.append("\nDescriptive (protocol §8, computed from the saved scores after the run): detector AUROC, oracle texts (pool D) vs the owner's "
         "unwatermarked check texts (pool A2), median over keys [min, max]:\n")
for lv in LEVELS:
    a = [auroc(S[(s, lv)]["scores_oracle"], S[(s, lv)]["scores_A2"]) for s in KEYS]
    T.append(f"- ρ = {lv}: {np.median(a):.3f} [{min(a):.3f}, {max(a):.3f}]")

# ---- Table 3: recovery
T.append("\n## Table 3 — Key recovery (median over 8 keys of cos(v̂, v); layer hits out of 8; Route A median support hit out of k = 4)\n")
T.append("| ρ | n | cos A | cos B | layer hits A | layer hits B | support hit A |")
T.append("|---|---|---|---|---|---|---|")
for lv in LEVELS:
    for n in REC_N:
        q = res["levels"][lv]["recovery"][str(n)]
        T.append(f"| {lv} | {n} | {q['median_cos_A']:.3f} | {q['median_cos_B']:.3f} | {q['layer_hits_A']} | {q['layer_hits_B']} | "
                 f"{q['median_support_hit_A']:.2f} |")

# ---- Table 4 (EXPLORATORY): quality of forgeries per key-level
expl = {"note": "EXPLORATORY, added after the run; the fluent cut-off was chosen after seeing the data", "fluent_ratio": FLUENT_RATIO,
        "rows": []}
for lv in LEVELS:
    for s in KEYS:
        x = S[(s, lv)]
        o_acc, o_ppl = float(acc(s, lv, "oracle").mean()), float(np.median(x["ppl_oracle"]))
        for r in "AB":
            for n in FORGE_N:
                c = f"forge_{r}_n{n}"
                a, p = float(acc(s, lv, c).mean()), float(np.median(x[f"ppl_{c}"]))
                expl["rows"].append({"rho": lv, "key": s, "route": r, "n": n, "layer": x["estimates"][str(n)][r]["layer"],
                                     "acceptance": a, "oracle_acceptance": o_acc, "ppl_median": p, "oracle_ppl_median": o_ppl,
                                     "ppl_ratio": p / o_ppl, "fluent": p / o_ppl <= FLUENT_RATIO,
                                     "forged": a >= 0.5 * o_acc})
rows = expl["rows"]
assert len(rows) == 4 * 8 * 2 * 3
T.append("\n## Table 4 — EXPLORATORY (added after the run): forgery quality per key-level\n")
T.append(f"A key-level forgery counts as *effective* if its acceptance is ≥ 50% of that key-level's oracle acceptance, and as *fluent* if its "
         f"median perplexity is ≤ {FLUENT_RATIO}× that key-level's oracle median (cut-off chosen after seeing the data). Counts are out of 8 keys.\n")
T.append("| ρ | Route | n | effective | effective and fluent | keys whose chosen layer is 0 or 1 | median ppl ratio to oracle |")
T.append("|---|---|---|---|---|---|---|")
summ = {}
for lv in LEVELS:
    for r in "AB":
        for n in FORGE_N:
            g = [x for x in rows if x["rho"] == lv and x["route"] == r and x["n"] == n]
            assert len(g) == 8
            eff = sum(x["forged"] for x in g)
            ef = sum(x["forged"] and x["fluent"] for x in g)
            low = sum(x["layer"] in (0, 1) for x in g)
            summ[(lv, r, n)] = (eff, ef)
            T.append(f"| {lv} | {r} | {n} | {eff} | {ef} | {low} | {np.median([x['ppl_ratio'] for x in g]):.2f} |")
# layer-choice effect on quality (Route B, all key-levels and n)
b = [x for x in rows if x["route"] == "B"]
lo = [x["ppl_ratio"] for x in b if x["layer"] in (0, 1)]
hi = [x["ppl_ratio"] for x in b if x["layer"] not in (0, 1)]
expl["route_B_layer01"] = {"count": len(lo), "median_ppl_ratio": float(np.median(lo)),
                           "median_acceptance": float(np.median([x["acceptance"] for x in b if x["layer"] in (0, 1)]))}
expl["route_B_other_layers"] = {"count": len(hi), "median_ppl_ratio": float(np.median(hi)),
                                "median_acceptance": float(np.median([x["acceptance"] for x in b if x["layer"] not in (0, 1)]))}
T.append(f"\nRoute B over all key-levels and n: chosen layer 0 or 1 in {len(lo)} of {len(b)} cases (median perplexity ratio "
         f"{expl['route_B_layer01']['median_ppl_ratio']:.1f}, median acceptance {pct(expl['route_B_layer01']['median_acceptance'])}%); other layers "
         f"in {len(hi)} cases (ratio {expl['route_B_other_layers']['median_ppl_ratio']:.2f}, acceptance "
         f"{pct(expl['route_B_other_layers']['median_acceptance'])}%).\n")
(OUT / "tables.md").write_text("\n".join(T) + "\n")
(OUT / "exploratory.json").write_text(json.dumps(expl, indent=1))

# ---- figures
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
rho = [float(v) for v in LEVELS]

# Fig 1: acceptance vs strength (n = 256, the largest n inside R2's practical window)
fig, ax = plt.subplots(figsize=(6.2, 3.8))
series = [("oracle", "Oracle (true key)", INK, "-", "o"), ("random", "Random key (generic steering)", MUTED, "--", "s"),
          ("forge_A_n256", "Route A forgery (n = 256)", COL["A"], "-", "^"), ("forge_B_n256", "Route B forgery (n = 256)", COL["B"], "-", "D")]
for c, lab, col, ls, mk in series:
    m = [res["levels"][lv][c]["median"] * 100 for lv in LEVELS]
    lo_ = [res["levels"][lv][c]["ci95"][0] * 100 for lv in LEVELS]
    hi_ = [res["levels"][lv][c]["ci95"][1] * 100 for lv in LEVELS]
    ax.fill_between(rho, lo_, hi_, color=col, alpha=0.10, linewidth=0)
    ax.plot(rho, m, ls, color=col, lw=2, marker=mk, ms=6, label=lab)
ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.text(0.705, 2.5, "nominal FPR 1%", color=MUTED, fontsize=8, ha="right")
ax.set_xticks(rho)
ax.set_xlabel("Watermark strength ρ = ‖v‖ / median activation norm")
ax.set_ylabel("Accepted by owner's detector (%)")
ax.set_ylim(-2, 104)
ax.legend(frameon=False, loc="upper left", fontsize=8)
ax.set_title("Study 1 v0.2: acceptance at a 1% false-positive rate (median over 8 keys, 95% CI)", fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig1_acceptance.png", dpi=200)
plt.close(fig)

# Fig 2 (EXPLORATORY): per key-level forgery acceptance vs perplexity ratio, n = 256
fig, axs = plt.subplots(1, 4, figsize=(10, 3.0), sharey=True)
for ax, lv in zip(axs, LEVELS):
    for r, mk in (("A", "^"), ("B", "D")):
        g = [x for x in rows if x["rho"] == lv and x["route"] == r and x["n"] == 256]
        ax.scatter([x["ppl_ratio"] for x in g], [100 * x["acceptance"] for x in g], s=34, marker=mk, color=COL[r],
                   edgecolor="white", linewidth=1, label=f"Route {r}", zorder=3)
    ax.axvline(FLUENT_RATIO, color=MUTED, lw=1, ls=":")
    ax.set_xscale("log")
    ax.set_xlim(0.3, 150)
    ax.set_ylim(-5, 108)
    ax.set_title(f"ρ = {lv}", fontsize=9, color=INK)
    ax.set_xlabel("ppl ratio to oracle (log)")
axs[0].set_ylabel("Accepted (%)")
axs[0].legend(frameon=False, fontsize=8, loc="center left")
fig.suptitle("Exploratory: forged texts per key (n = 256). Right of the dotted line = more than 1.5× the oracle's perplexity",
             fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(OUT / "fig2_quality.png", dpi=200)
plt.close(fig)

# Fig 3: recovery — Route A median cosine and layer hits vs n
fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.0))
shade = {"0.25": "#9ec5f4", "0.35": "#5598e7", "0.5": "#256abf", "0.7": "#0d366b"}  # one-hue ordinal ramp (blue)
for lv in LEVELS:
    q = res["levels"][lv]["recovery"]
    axs[0].plot(REC_N, [q[str(n)]["median_cos_A"] for n in REC_N], "-o", color=shade[lv], lw=2, ms=5, label=f"ρ = {lv}")
    axs[1].plot(REC_N, [q[str(n)]["layer_hits_A"] for n in REC_N], "-o", color=shade[lv], lw=2, ms=5, label=f"ρ = {lv}")
axs[0].axhline(0.9, color=MUTED, lw=1, ls=":")
axs[0].text(1, 0.86, "R1 threshold 0.9", color=MUTED, fontsize=8, va="top")
axs[0].set_ylim(-0.05, 1)
axs[0].set_ylabel("median cos(v̂, v), Route A")
axs[1].axhline(7, color=MUTED, lw=1, ls=":")
axs[1].text(1, 6.8, "R1 needs ≥ 7 of 8", color=MUTED, fontsize=8, va="top")
axs[1].set_ylim(-0.3, 8.3)
axs[1].set_ylabel("keys with layer found (of 8)")
for ax in axs:
    ax.set_xscale("log", base=4)
    ax.set_xticks(REC_N, [str(n) for n in REC_N])
    ax.set_xlabel("observed watermarked texts n")
axs[0].legend(frameon=False, fontsize=8, loc="center right")
fig.suptitle("Study 1 v0.2: key recovery does not converge within 1,024 texts", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(OUT / "fig3_recovery.png", dpi=200)
plt.close(fig)
print("ok: integrity asserts passed; wrote", sorted(p.name for p in OUT.iterdir()))
for k, v in summ.items():
    if k[2] == 256:
        print(k, "effective, effective+fluent:", v)

# ---- assemble the report: prose + generated tables (Table 1 in §2, Tables 2-4 in §3)
tables = (OUT / "tables.md").read_text()
t1, rest = tables.split("## Table 2", 1)
prose = (Path(__file__).parent / "report_prose.md").read_text()
assert prose.count("<<TABLE1>>") == 1 and prose.count("<<TABLES234>>") == 1
report = prose.replace("<<TABLE1>>", t1.replace("## Table 1", "### Table 1").strip()).replace(
    "<<TABLES234>>", ("## Table 2" + rest).replace("## Table", "### Table").strip())
(ROOT / "STUDY1_REPORT_v0.2.md").write_text(report)
print("wrote", ROOT / "STUDY1_REPORT_v0.2.md")
