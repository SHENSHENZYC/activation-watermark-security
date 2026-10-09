"""Build the Study 1 v0.3 report tables and figures from the locked outputs (numbers are never retyped).

Reads research/outputs/study1_v0.3/results.json, the per-key v0.3 outputs in research/study1_v03/data/ and v0.2's
per-key summaries in research/study1_v02/data/ (both git-ignored). Re-computes every per-key FA and acceptance rate and
every median from the raw scores and perplexities, and asserts that they equal results.json before writing anything.
Writes to research/outputs/study1_v0.3/report/:
  tables.md          Tables 1-4 and the forged-text samples (protocol §8: 3 per route at rho = 0.50)
  fig1_fa.png, fig2_quality_condition.png, fig3_quality.png
Then assembles research/STUDY1_REPORT_v0.3.md from report_prose.md (placeholders <<TABLE1>>, <<TABLES234>>, <<SAMPLES>>,
<<EXPLORATORY>>; the last is the table written by exploratory_repetition.py, run first).

Sample rule (fixed before the run's outcomes were read): at rho = 0.50 and n = 256, for each route, the first pool D text
of keys 1001, 1002 and 1003, shown with its accepted and fluent flags; the first 80 words are quoted.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "outputs" / "study1_v0.3" / "results.json"
D3 = ROOT / "study1_v03" / "data"
D2 = ROOT / "study1_v02" / "data"
OUT = ROOT / "outputs" / "study1_v0.3" / "report"
KEYS = list(range(1001, 1009))
LEVELS = ["0.35", "0.5", "0.7"]
TAG = {"0.35": "035", "0.5": "050", "0.7": "070"}
FORGE_N = [64, 256]
ROUTES = "AB"
LAYER = 14
FLUENT_Q = 0.95
SAMPLE_KEYS, SAMPLE_LEVEL, SAMPLE_N, SAMPLE_WORDS = [1001, 1002, 1003], "0.5", 256, 80
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dc"
COL = {"A": "#2a78d6", "B": "#eb6834"}  # categorical slots 1-2 (as the v0.2 report; validated, light mode)

res = json.loads(RES.read_text())
S2 = {(s, lv): json.loads((D2 / f"K_k{s}_r{TAG[lv]}_summary.json").read_text()) for s in KEYS for lv in LEVELS}
S3 = {(s, lv): json.loads((D3 / f"K_k{s}_r{TAG[lv]}_v03.json").read_text()) for s in KEYS for lv in LEVELS}


def cut(s, lv):
    return float(np.quantile(np.asarray(S2[(s, lv)]["ppl_oracle"], dtype=np.float64), FLUENT_Q))


def raw(s, lv, c):
    """(scores, ppl) of one condition at one key-level, from the raw per-key files."""
    x2, x3 = S2[(s, lv)], S3[(s, lv)]
    if c in ("oracle", "random"):
        return np.asarray(x2[f"scores_{c}"]), np.asarray(x2[f"ppl_{c}"], dtype=np.float64)
    ver, r, n = c.split("_")
    if ver == "v03":
        a = x3["attacks"][f"{r}_{n}"]
        return np.asarray(a["scores"]), np.asarray(a["ppl"], dtype=np.float64)
    return np.asarray(x2[f"scores_forge_{r}_{n}"]), np.asarray(x2[f"ppl_forge_{r}_{n}"], dtype=np.float64)


def flags(s, lv, c):
    sc, pp = raw(s, lv, c)
    thr = S2[(s, lv)]["threshold"]
    assert S3[(s, lv)]["threshold"] == thr
    return sc > thr, pp <= cut(s, lv)


CONDS = ["oracle", "random"] + [f"{v}_{r}_n{n}" for v in ("v03", "v02") for r in ROUTES for n in FORGE_N]

# ---- integrity: re-computed numbers equal the locked results
assert res["integrity"]["pass"] and len(res["integrity"]["rows"]) == 8 * 3
for lv in LEVELS:
    L = res["levels"][lv]
    assert L["fluent_cut_per_key"] == [cut(s, lv) for s in KEYS]
    for c in CONDS:
        fa = [float((a & f).mean()) for a, f in (flags(s, lv, c) for s in KEYS)]
        ac = [float(flags(s, lv, c)[0].mean()) for s in KEYS]
        assert all(len(flags(s, lv, c)[0]) == 100 for s in KEYS)
        assert fa == L[c]["FA"]["per_key"] and float(np.median(fa)) == L[c]["FA"]["median"], (lv, c)
        assert ac == L[c]["acceptance"]["per_key"] and float(np.median(ac)) == L[c]["acceptance"]["median"], (lv, c)
    for r in ROUTES:
        for n in FORGE_N:
            a = [S3[(s, lv)]["attacks"][f"{r}_n{n}"] for s in KEYS]
            d = L["attacks"][f"{r}_n{n}"]
            assert d["selected_layers"] == [x["selected_layer"] for x in a]
            assert d["none_passed"] == sum(not x["any_kept"] for x in a)
            assert d["layer_hits"] == sum(x["selected_layer"] == LAYER for x in a)
OUT.mkdir(parents=True, exist_ok=True)


def pct(x):
    return f"{100 * x:.1f}"


def ci(c):
    return f"[{pct(c[0])}, {pct(c[1])}]"


T = []
# ---- Table 1: pre-registered rules vs observed
T.append("## Table 1 — Pre-registered rules vs observed (protocol §7)\n")
ig = res["integrity"]
T.append(f"Integrity check (§3; reloaded v0.2 probes re-score v0.2's oracle texts within {ig['tol']}): "
         f"**{'PASS' if ig['pass'] else 'FAIL'}** (largest difference {max(r['max_abs_diff'] for r in ig['rows']):.2g}, "
         f"{len(ig['rows'])} key-levels).\n")
T.append("| ρ | Oracle FA (ceiling) | 50% of oracle | Random-key FA [95% CI] | F1 Route A | F1 Route B | F3 fluent generic steering suffices |")
T.append("|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    o, rd, ru = L["oracle"]["FA"], L["random"]["FA"], L["rules"]
    T.append(f"| {lv} | {pct(o['median'])}% | {pct(0.5 * o['median'])}% | {pct(rd['median'])}% {ci(rd['ci95'])} | "
             f"{ru['F1']['A']} | {ru['F1']['B']} | {'yes' if ru['F3_fluent_generic_steering_suffices'] else 'no'} |")
T.append("\nF1 practical: at some n, median FA ≥ 50% of the oracle's median FA and its lower 95% bound > the random-key FA's upper "
         "95% bound. Not practical: at both n, the upper 95% bound < 50% of the oracle's median FA. Otherwise inconclusive.\n")

# ---- Table 2: FA and acceptance for v0.3 forgeries and controls
T.append("## Table 2 — Fluent acceptance (FA) and plain acceptance at the owner's 1%-FPR threshold (median over 8 keys, % "
         "[95% cluster-bootstrap CI]); median perplexity ratio to the key-level's oracle texts\n")
C2 = ["oracle", "random"] + [f"v03_{r}_n{n}" for r in ROUTES for n in FORGE_N]
T.append("| ρ | measure | Oracle | Random key | A n=64 | A n=256 | B n=64 | B n=256 |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    T.append(f"| {lv} | FA | " + " | ".join(f"{pct(L[c]['FA']['median'])} {ci(L[c]['FA']['ci95'])}" for c in C2) + " |")
    T.append(f"| | accepted | " + " | ".join(f"{pct(L[c]['acceptance']['median'])}" for c in C2) + " |")
    T.append(f"| | fluent share | " + " | ".join(f"{pct(L[c]['fluent_share_median'])}" for c in C2) + " |")
    T.append(f"| | ppl ratio | " + " | ".join(f"{L[c]['ppl_ratio_to_oracle_median']:.2f}" for c in C2) + " |")

# ---- Table 3: what the quality condition changes (v0.2 forgeries re-scored under FA vs v0.3)
T.append("\n## Table 3 — v0.2's forgeries (no fluency check) re-scored under FA, beside v0.3's (median over 8 keys, %)\n")
T.append("| ρ | Route | n | v0.2 accepted | v0.2 FA | v0.3 accepted | v0.3 FA |")
T.append("|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    for r in ROUTES:
        for n in FORGE_N:
            a, b = L[f"v02_{r}_n{n}"], L[f"v03_{r}_n{n}"]
            T.append(f"| {lv} | {r} | {n} | {pct(a['acceptance']['median'])} | {pct(a['FA']['median'])} | "
                     f"{pct(b['acceptance']['median'])} | {pct(b['FA']['median'])} |")

# ---- Table 4: the attacker's own check (secondary, §8)
T.append("\n## Table 4 — The attacker's fluency check and layer choice (secondary, descriptive; counts out of 8 keys)\n")
T.append("| ρ | Route | n | selected layers (keys 1001–1008) | layer = 14 | top candidate kept | no candidate passed | "
         "candidates passing (median of 5) | median cos(v̂, v) | check agrees with evaluation |")
T.append("|---|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    for r in ROUTES:
        for n in FORGE_N:
            d = res["levels"][lv]["attacks"][f"{r}_n{n}"]
            T.append(f"| {lv} | {r} | {n} | {', '.join(map(str, d['selected_layers']))} | {d['layer_hits']} | "
                     f"{d['selected_is_top_candidate']} | {d['none_passed']} | {np.median(d['n_kept']):g} | "
                     f"{d['median_cos_true']:.3f} | {pct(d['check_vs_eval_agreement'])}% |")
T.append("\n*Check agrees with evaluation:* the share of keys where \"some candidate passed the attacker's check\" matches "
         "\"the forgery's median perplexity is at or below the evaluation's fluency bar\".\n")
tables_main = "\n".join(T) + "\n"

# ---- samples (protocol §8; rule fixed in the docstring)
Sm = [f"Rule (fixed before outcomes were read): ρ = {SAMPLE_LEVEL}, n = {SAMPLE_N}, the first pool D text of keys "
      f"{', '.join(map(str, SAMPLE_KEYS))}, per route; first {SAMPLE_WORDS} words quoted verbatim (\"…\" marks the cut).\n"]
for r in ROUTES:
    for s in SAMPLE_KEYS:
        txt = json.loads((D3 / f"K_k{s}_r{TAG[SAMPLE_LEVEL]}_forge3_{r}_n{SAMPLE_N}.json").read_text())[0]
        acc_, flu_ = (bool(x[0]) for x in flags(s, SAMPLE_LEVEL, f"v03_{r}_n{SAMPLE_N}"))
        w = txt.split()
        q = " ".join(w[:SAMPLE_WORDS]) + (" …" if len(w) > SAMPLE_WORDS else "")
        pp = raw(s, SAMPLE_LEVEL, f"v03_{r}_n{SAMPLE_N}")[1][0]
        Sm.append(f"**Route {r}, key {s}** (layer {S3[(s, SAMPLE_LEVEL)]['attacks'][f'{r}_n{SAMPLE_N}']['selected_layer']}; "
                  f"accepted: {'yes' if acc_ else 'no'}; fluent: {'yes' if flu_ else 'no'}; perplexity {pp:.1f} vs bar "
                  f"{cut(s, SAMPLE_LEVEL):.1f})\n\n> " + q.replace("\n", " ") + "\n")
samples = "\n".join(Sm)
(OUT / "tables.md").write_text(tables_main + "\n## Samples\n\n" + samples)

# ---- figures
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
rho = [float(v) for v in LEVELS]

# Fig 1: FA vs strength (both n; n = 256 solid, n = 64 dashed)
fig, ax = plt.subplots(figsize=(6.4, 4.6))
series = [("oracle", "Oracle (true key): ceiling", INK, "-", "o"), ("random", "Random key (generic steering)", MUTED, "--", "s")]
for r, mk in (("A", "^"), ("B", "D")):
    series += [(f"v03_{r}_n256", f"Route {r} forgery, n = 256", COL[r], "-", mk), (f"v03_{r}_n64", f"Route {r} forgery, n = 64", COL[r], ":", mk)]
for c, lab, col, ls, mk in series:
    m = [res["levels"][lv][c]["FA"]["median"] * 100 for lv in LEVELS]
    if ls != ":":
        ax.fill_between(rho, [res["levels"][lv][c]["FA"]["ci95"][0] * 100 for lv in LEVELS],
                        [res["levels"][lv][c]["FA"]["ci95"][1] * 100 for lv in LEVELS], color=col, alpha=0.10, linewidth=0)
    ax.plot(rho, m, ls, color=col, lw=2 if ls != ":" else 1.4, marker=mk, ms=6 if ls != ":" else 4,
            mfc=col if ls != ":" else "white", label=lab)
ax.plot(rho, [50 * res["levels"][lv]["oracle"]["FA"]["median"] for lv in LEVELS], color=MUTED, lw=1, ls=(0, (1, 2)))
ax.text(rho[-1] + 0.005, 50 * res["levels"][LEVELS[-1]]["oracle"]["FA"]["median"], "50% of oracle\n(F1 bar)", color=MUTED,
        fontsize=7.5, va="center")
ax.set_xticks(rho)
ax.set_xlim(0.33, 0.78)
ax.set_xlabel("Watermark strength ρ = ‖v‖ / median activation norm")
ax.set_ylabel("Accepted AND fluent (%)")
ax.set_ylim(-2, 104)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17), fontsize=7.5, ncol=3)
ax.set_title("Study 1 v0.3: fluent acceptance at a 1% false-positive rate (median over 8 keys, 95% CI)", fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig1_fa.png", dpi=200)
plt.close(fig)

# Fig 2: what the quality condition changes — accepted vs FA, v0.2 vs v0.3, n = 256
fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.2), sharey=True)
for ax, r in zip(axs, ROUTES):
    x = np.arange(len(LEVELS))
    w = 0.2
    bars = [(f"v02_{r}_n256", "acceptance", "v0.2 accepted", "#c9c8c1"), (f"v02_{r}_n256", "FA", "v0.2 accepted and fluent", MUTED),
            (f"v03_{r}_n256", "acceptance", "v0.3 accepted", "#f5b596" if r == "B" else "#9ec5f4"),
            (f"v03_{r}_n256", "FA", "v0.3 accepted and fluent", COL[r])]
    for i, (c, m, lab, col) in enumerate(bars):
        ax.bar(x + (i - 1.5) * w, [100 * res["levels"][lv][c][m]["median"] for lv in LEVELS], w, color=col, label=lab, zorder=3)
    ax.set_xticks(x, [f"ρ = {lv}" for lv in LEVELS])
    ax.set_title(f"Route {r} (n = 256)", fontsize=9, color=INK)
    ax.set_ylim(0, 105)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
axs[0].set_ylabel("median over 8 keys (%)")
fig.suptitle("What the fluency condition removes: v0.2 forgeries (no check) vs v0.3 (attacker's check)", fontsize=9, color=INK,
             x=0.01, ha="left")
fig.tight_layout()
fig.savefig(OUT / "fig2_quality_condition.png", dpi=200)
plt.close(fig)

# Fig 3: per key-level, acceptance vs perplexity ratio (v0.3 forgeries, n = 256), with v0.2's for comparison
fig, axs = plt.subplots(1, 3, figsize=(9.2, 3.1), sharey=True)
for ax, lv in zip(axs, LEVELS):
    for r, mk in (("A", "^"), ("B", "D")):
        for v, filled in (("v02", False), ("v03", True)):
            c = f"{v}_{r}_n256"
            xs = [float(np.median(raw(s, lv, c)[1]) / np.median(S2[(s, lv)]["ppl_oracle"])) for s in KEYS]
            ys = [100 * float(flags(s, lv, c)[0].mean()) for s in KEYS]
            ax.scatter(xs, ys, s=30, marker=mk, color=COL[r] if filled else "white", edgecolor=COL[r], linewidth=1,
                       label=f"Route {r} {v.replace('v0', 'v0.')}", zorder=3 if filled else 2)
    ax.axvline(1, color=MUTED, lw=1, ls=":")
    ax.set_xscale("log")
    ax.set_xlim(0.3, 150)
    ax.set_ylim(-5, 108)
    ax.set_title(f"ρ = {lv}", fontsize=9, color=INK)
    ax.set_xlabel("median ppl ratio to oracle (log)")
axs[0].set_ylabel("Accepted (%)")
axs[0].legend(frameon=False, fontsize=7, loc="center left")
fig.suptitle("Forged texts per key (n = 256): filled = v0.3 (fluency-checked), hollow = v0.2", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(OUT / "fig3_quality.png", dpi=200)
plt.close(fig)
print("ok: integrity asserts passed; wrote", sorted(p.name for p in OUT.iterdir()))

# ---- assemble the report (only if the prose exists)
pf = Path(__file__).parent / "report_prose.md"
if not pf.exists():
    sys.exit("report_prose.md not written yet; assets only")
prose = pf.read_text()
ex = OUT / "exploratory_repetition.md"
assert ex.exists(), "run exploratory_repetition.py first"
for ph in ("<<TABLE1>>", "<<TABLES234>>", "<<SAMPLES>>", "<<EXPLORATORY>>"):
    assert prose.count(ph) == 1, ph
t1, rest = tables_main.split("## Table 2", 1)
report = (prose.replace("<<TABLE1>>", t1.replace("## Table 1", "### Table 1").strip())
          .replace("<<TABLES234>>", ("## Table 2" + rest).replace("## Table", "### Table").strip())
          .replace("<<SAMPLES>>", samples.strip()).replace("<<EXPLORATORY>>", ex.read_text().strip()))
(ROOT / "STUDY1_REPORT_v0.3.md").write_text(report)
print("wrote", ROOT / "STUDY1_REPORT_v0.3.md")
