"""Build the Study 1 v0.4 report tables and figures from the locked outputs (numbers are never retyped).

Reads research/outputs/study1_v0.4/results.json, the per-key v0.4 outputs in research/study1_v04/data/, v0.3's in
research/study1_v03/data/ and v0.2's in research/study1_v02/data/ (all git-ignored). Re-computes every per-key FA and
acceptance rate and every median from the raw texts, scores and perplexities, with its own seq-rep-4 (the pinned Qwen
tokenizer), and asserts that they equal results.json before writing anything.
Writes to research/outputs/study1_v0.4/report/:
  tables.md          Tables 1-4 and the forged-text samples (protocol §8)
  fig1_fa.png, fig2_repetition_condition.png, fig3_repetition.png
Then assembles research/STUDY1_REPORT_v0.4.md from report_prose.md (placeholders <<TABLE1>>, <<TABLES234>>, <<SAMPLES>>).

Sample rule (protocol §8, fixed before the run): n = 256, per route, keys 1001-1003: at rho = 0.50 the first pool D text;
at rho = 0.70 the first accepted-and-fluent text in pool D order (none for a key with none). The first 80 words are quoted.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "study1_v04"))
import run_v04  # noqa: E402  (only for the pinned tokenizer loader)

RES = ROOT / "outputs" / "study1_v0.4" / "results.json"
D4, D3, D2 = ROOT / "study1_v04" / "data", ROOT / "study1_v03" / "data", ROOT / "study1_v02" / "data"
OUT = ROOT / "outputs" / "study1_v0.4" / "report"
KEYS = list(range(1001, 1009))
LEVELS = ["0.35", "0.5", "0.7"]
TAG = {"0.35": "035", "0.5": "050", "0.7": "070"}
FORGE_N = [64, 256]
ROUTES = "AB"
LAYER = 14
Q = 0.95
SAMPLE_WORDS = 80
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dc"
COL = {"A": "#2a78d6", "B": "#eb6834"}  # categorical slots 1-2 (as the v0.2 and v0.3 reports)

res = json.loads(RES.read_text())
tok = run_v04.load_tok()


def jl(p):
    return json.loads(p.read_text())


S2 = {(s, lv): jl(D2 / f"K_k{s}_r{TAG[lv]}_summary.json") for s in KEYS for lv in LEVELS}
S3 = {(s, lv): jl(D3 / f"K_k{s}_r{TAG[lv]}_v03.json") for s in KEYS for lv in LEVELS}
S4 = {(s, lv): jl(D4 / f"K_k{s}_r{TAG[lv]}_v04.json") for s in KEYS for lv in LEVELS}


def seqrep4(t):
    ids = tok(t, add_special_tokens=False)["input_ids"][:256]
    g = [tuple(ids[i:i + 4]) for i in range(len(ids) - 3)]
    return 1.0 - len(set(g)) / len(g) if g else 0.0


def rep3(t):
    w = t.lower().split()
    g = list(zip(w, w[1:], w[2:]))
    return 1 - len(set(g)) / len(g) if g else 0.0


def texts(s, lv, c):
    t = f"K_k{s}_r{TAG[lv]}"
    if c in ("oracle", "random"):
        return jl(D2 / f"{t}_{c}.json")
    v, r, n = c.split("_")
    return jl({"v02": D2 / f"{t}_forge_{r}_{n}.json", "v03": D3 / f"{t}_forge3_{r}_{n}.json",
               "v04": D4 / f"{t}_forge4_{r}_{n}.json"}[v])


def raw(s, lv, c):
    """(scores, ppl) of one condition at one key-level, from the raw per-key files."""
    x2 = S2[(s, lv)]
    if c in ("oracle", "random"):
        return np.asarray(x2[f"scores_{c}"]), np.asarray(x2[f"ppl_{c}"], dtype=np.float64)
    v, r, n = c.split("_")
    if v == "v02":
        return np.asarray(x2[f"scores_forge_{r}_{n}"]), np.asarray(x2[f"ppl_forge_{r}_{n}"], dtype=np.float64)
    a = (S3 if v == "v03" else S4)[(s, lv)]["attacks"][f"{r}_{n}"]
    return np.asarray(a["scores"]), np.asarray(a["ppl"], dtype=np.float64)


CONDS = ["oracle", "random"] + [f"{v}_{r}_n{n}" for v in ("v04", "v03", "v02") for r in ROUTES for n in FORGE_N]
REP = {(s, lv, c): np.array([seqrep4(x) for x in texts(s, lv, c)]) for s in KEYS for lv in LEVELS for c in CONDS}
R3 = {(s, lv, c): np.array([rep3(x) for x in texts(s, lv, c)]) for s in KEYS for lv in LEVELS for c in CONDS}
CUT = {(s, lv): {"ppl": float(np.quantile(raw(s, lv, "oracle")[1], Q)), "seqrep4": float(np.quantile(REP[(s, lv, "oracle")], Q)),
                 "rep3": float(np.quantile(R3[(s, lv, "oracle")], Q)), "thr": S2[(s, lv)]["threshold"]} for s in KEYS for lv in LEVELS}


def flags(s, lv, c):
    """(accepted, ppl ok, seq-rep-4 ok, rep3 ok) per text."""
    sc, pp = raw(s, lv, c)
    k = CUT[(s, lv)]
    return sc > k["thr"], pp <= k["ppl"], REP[(s, lv, c)] <= k["seqrep4"], R3[(s, lv, c)] <= k["rep3"]


def med(xs):
    return float(np.median(xs))


# ---- integrity: re-computed numbers equal the locked results
assert res["integrity"]["pass"] and len(res["integrity"]["rows"]) == 8 * 3
for lv in LEVELS:
    L = res["levels"][lv]
    for k in ("ppl", "seqrep4", "rep3"):
        assert L["cut_per_key"][k] == [CUT[(s, lv)][k] for s in KEYS], (lv, k)
    for c in CONDS:
        F = [flags(s, lv, c) for s in KEYS]
        assert all(len(f[0]) == 100 for f in F)
        fa = [float((a & p & r).mean()) for a, p, r, _ in F]
        ac = [float(a.mean()) for a, *_ in F]
        assert fa == L[c]["FA"]["per_key"] and med(fa) == L[c]["FA"]["median"], (lv, c)
        assert ac == L[c]["acceptance"]["per_key"] and med(ac) == L[c]["acceptance"]["median"], (lv, c)
        assert med([(a & p).mean() for a, p, _, _ in F]) == L[c]["FA_ppl_only_median"], (lv, c)
        assert med([(a & p & r3).mean() for a, p, _, r3 in F]) == L[c]["FA_rep3_median"], (lv, c)
        assert med([(~r).mean() for _, _, r, _ in F]) == L[c]["repetitive_share_median"], (lv, c)
    for c in [f"v03_{r}_n{n}" for r in ROUTES for n in FORGE_N] + ["oracle", "random"]:
        v3 = jl(ROOT / "outputs" / "study1_v0.3" / "results.json")["levels"][lv][c]["FA"]["median"]
        assert L[c]["FA_ppl_only_median"] == v3, (lv, c)  # v0.3's locked FA, reproduced
    for r in ROUTES:
        for n in FORGE_N:
            a = [S4[(s, lv)]["attacks"][f"{r}_n{n}"] for s in KEYS]
            d = L["attacks"][f"{r}_n{n}"]
            assert d["selected_layers"] == [x["selected_layer"] for x in a]
            assert d["none_passed"] == sum(not x["any_kept"] for x in a)
            assert d["layer_hits"] == sum(x["selected_layer"] == LAYER for x in a)
            assert d["m_selected"] == [x["m_selected"] for x in a]
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
T.append("\nEvaluation bars (median over the 8 keys of each key-level's oracle 95th percentile): " + "; ".join(
    f"ρ = {lv}: perplexity {med(res['levels'][lv]['cut_per_key']['ppl']):.1f}, seq-rep-4 "
    f"{med(res['levels'][lv]['cut_per_key']['seqrep4']):.3f}" for lv in LEVELS) + ".")
T.append("\nFA (v0.4): accepted at the owner's 1%-FPR threshold, perplexity ≤ the key-level oracle's 95th percentile, and "
         "seq-rep-4 ≤ the oracle's 95th percentile. F1 practical: at some n, median FA ≥ 50% of the oracle's median FA and its "
         "lower 95% bound > the random-key FA's upper 95% bound. Not practical: at both n, the upper 95% bound < 50% of the "
         "oracle's median FA. Otherwise inconclusive.\n")

# ---- Table 2: FA and acceptance for v0.4 forgeries and controls
T.append("## Table 2 — Fluent acceptance (FA, v0.4 definition) and its parts (median over 8 keys, % [95% cluster-bootstrap CI]); "
         "median perplexity ratio and seq-rep-4\n")
C2 = ["oracle", "random"] + [f"v04_{r}_n{n}" for r in ROUTES for n in FORGE_N]
T.append("| ρ | measure | Oracle | Random key | A n=64 | A n=256 | B n=64 | B n=256 |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    T.append(f"| {lv} | FA | " + " | ".join(f"{pct(L[c]['FA']['median'])} {ci(L[c]['FA']['ci95'])}" for c in C2) + " |")
    T.append("| | accepted | " + " | ".join(pct(L[c]["acceptance"]["median"]) for c in C2) + " |")
    T.append("| | fluent share | " + " | ".join(pct(L[c]["fluent_share_median"]) for c in C2) + " |")
    T.append("| | repetitive share | " + " | ".join(pct(L[c]["repetitive_share_median"]) for c in C2) + " |")
    T.append("| | ppl ratio | " + " | ".join(f"{L[c]['ppl_ratio_to_oracle_median']:.2f}" for c in C2) + " |")
    T.append("| | median seq-rep-4 | " + " | ".join(f"{L[c]['seqrep4_median']:.3f}" for c in C2) + " |")

# ---- Table 3: what the repetition term changes (v0.2, v0.3, v0.4 forgeries under three definitions)
T.append("\n## Table 3 — v0.2, v0.3 and v0.4 forgeries under three fluency definitions (median over 8 keys, %): "
         "perplexity only (v0.3's rule), perplexity and seq-rep-4 (v0.4's rule), perplexity and word rep3\n")
T.append("| ρ | Route | n | forgeries | accepted | FA ppl only | FA v0.4 | FA with rep3 |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    for r in ROUTES:
        for n in FORGE_N:
            for v in ("v02", "v03", "v04"):
                x = L[f"{v}_{r}_n{n}"]
                T.append(f"| {lv} | {r} | {n} | {v.replace('v0', 'v0.')} | {pct(x['acceptance']['median'])} | "
                         f"{pct(x['FA_ppl_only_median'])} | {pct(x['FA']['median'])} | {pct(x['FA_rep3_median'])} |")
T.append("\nv0.2 forgeries had no quality check; v0.3's attacker screened perplexity; v0.4's screened perplexity and repetition. "
         "The \"FA ppl only\" column for v0.3 forgeries equals v0.3's locked FA (asserted).\n")

# ---- Table 4: the attacker's own check (secondary, §8)
T.append("## Table 4 — The attacker's perplexity-and-repetition check and layer choice (secondary, descriptive; counts out of 8 keys)\n")
T.append("| ρ | Route | n | selected layers (keys 1001–1008) | layer = 14 | top candidate kept | no candidate passed | "
         "candidates passing (median of 5) | repetitive trials of the selected layer (of 16) | median cos(v̂, v) | check agrees with evaluation |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    for r in ROUTES:
        for n in FORGE_N:
            d = res["levels"][lv]["attacks"][f"{r}_n{n}"]
            T.append(f"| {lv} | {r} | {n} | {', '.join(map(str, d['selected_layers']))} | {d['layer_hits']} | "
                     f"{d['selected_is_top_candidate']} | {d['none_passed']} | {np.median(d['n_kept']):g} | "
                     f"{', '.join(map(str, d['m_selected']))} | {d['median_cos_true']:.3f} | {pct(d['check_vs_eval_agreement'])}% |")
T.append("\n*Check agrees with evaluation:* the share of keys where \"some candidate passed the attacker's check\" matches "
         "\"the forgery's median perplexity and median seq-rep-4 are both at or below the evaluation's bars\".\n")
# ---- Table 5: per-key FA (the spread behind the medians)
T.append("## Table 5 — Per-key FA (%, v0.4 definition), keys 1001–1008; n = 256 forgeries\n")
T.append("| ρ | condition | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | keys ≥ 50% of the oracle's median |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    bar = 0.5 * L["oracle"]["FA"]["median"]
    for c in ("oracle", "random", "v04_A_n256", "v04_B_n256"):
        pk = L[c]["FA"]["per_key"]
        T.append(f"| {lv} | {c} | " + " | ".join(f"{100 * x:.0f}" for x in pk) + f" | {sum(x >= bar for x in pk)} of 8 |")
T.append("")
tables_main = "\n".join(T) + "\n"

# ---- samples (protocol §8), taken from results.json and checked against the raw files
Sm = ["Rule (protocol §8, fixed before the run): n = 256, per route, keys 1001–1003; at ρ = 0.50 the first pool D text, at "
      f"ρ = 0.70 the first accepted-and-fluent text in pool D order. First {SAMPLE_WORDS} words quoted verbatim (\"…\" marks the cut).\n"]
for lv, what in (("0.5", "first pool D text"), ("0.7", "first accepted-and-fluent text")):
    Sm.append(f"### ρ = {lv}: {what}\n")
    for r in ROUTES:
        for row in res["levels"][lv]["samples"][f"v04_{r}_n256"]:
            s = row["key"]
            if row["index"] is None:
                Sm.append(f"**Route {r}, key {s}:** no accepted-and-fluent text among its 100.\n")
                continue
            i = row["index"]
            assert texts(s, lv, f"v04_{r}_n256")[i] == row["text"]
            a, p, rr, _ = (bool(x[i]) for x in flags(s, lv, f"v04_{r}_n256"))
            assert (a and p and rr) == row["fluent_accepted"] and a == row["accepted"]
            w = row["text"].split()
            q = " ".join(w[:SAMPLE_WORDS]) + (" …" if len(w) > SAMPLE_WORDS else "")
            k = CUT[(s, lv)]
            Sm.append(f"**Route {r}, key {s}, text {i}** (layer {S4[(s, lv)]['attacks'][f'{r}_n256']['selected_layer']}; "
                      f"accepted: {'yes' if a else 'no'}; perplexity {row['ppl']:.1f} vs bar {k['ppl']:.1f}; seq-rep-4 "
                      f"{row['seqrep4']:.3f} vs bar {k['seqrep4']:.3f})\n\n> " + q.replace("\n", " ") + "\n")
samples = "\n".join(Sm)
(OUT / "tables.md").write_text(tables_main + "\n## Samples\n\n" + samples)

# ---- figures
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
rho = [float(v) for v in LEVELS]

# Fig 1: FA vs strength (n = 256 solid with CI, n = 64 dotted)
fig, ax = plt.subplots(figsize=(6.4, 4.6))
series = [("oracle", "Oracle (true key): ceiling", INK, "-", "o"), ("random", "Random key (generic steering)", MUTED, "--", "s")]
for r, mk in (("A", "^"), ("B", "D")):
    series += [(f"v04_{r}_n256", f"Route {r} forgery, n = 256", COL[r], "-", mk), (f"v04_{r}_n64", f"Route {r} forgery, n = 64", COL[r], ":", mk)]
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
ax.set_ylabel("Accepted AND fluent AND not repetitive (%)")
ax.set_ylim(-2, 104)
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17), fontsize=7.5, ncol=3)
ax.set_title("Study 1 v0.4: fluent, non-repetitive acceptance at a 1% false-positive rate\n(median over 8 keys, 95% CI)",
             fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig1_fa.png", dpi=200)
plt.close(fig)

# Fig 2: what the repetition term changes, n = 256: v0.3 forgeries under v0.3's rule and v0.4's rule, v0.4 forgeries
fig, axs = plt.subplots(1, 2, figsize=(8.6, 4.0), sharey=True)
for ax, r in zip(axs, ROUTES):
    x = np.arange(len(LEVELS))
    w = 0.26
    bars = [(f"v03_{r}_n256", "FA_ppl_only_median", "v0.3 forgeries, perplexity-only FA (v0.3 rule)", "#c9c8c1"),
            (f"v03_{r}_n256", "FA", "v0.3 forgeries, v0.4 FA", MUTED),
            (f"v04_{r}_n256", "FA", "v0.4 forgeries, v0.4 FA (blue A, orange B)", COL[r])]
    for i, (c, m, lab, col) in enumerate(bars):
        vals = [100 * (res["levels"][lv][c][m] if m != "FA" else res["levels"][lv][c]["FA"]["median"]) for lv in LEVELS]
        ax.bar(x + (i - 1) * w, vals, w, color=col, label=lab, zorder=3)
    for j, lv in enumerate(LEVELS):
        ax.hlines(100 * res["levels"][lv]["oracle"]["FA"]["median"], j - 1.5 * w, j + 1.5 * w, color=INK, lw=1.2, zorder=4,
                  label="oracle v0.4 FA (ceiling)" if j == 0 else None)
    ax.set_xticks(x, [f"ρ = {lv}" for lv in LEVELS])
    ax.set_title(f"Route {r} (n = 256)", fontsize=9, color=INK)
    ax.set_ylim(0, 105)
axs[0].set_ylabel("median over 8 keys (%)")
h, lab = axs[0].get_legend_handles_labels()
fig.legend(h, lab, frameon=False, fontsize=7.5, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.0))
fig.suptitle("What the repetition term changes: v0.3 forgeries re-scored, and v0.4's repetition-screened forgeries", fontsize=9,
             color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.13, 1, 1))
fig.savefig(OUT / "fig2_repetition_condition.png", dpi=200)
plt.close(fig)

# Fig 3: per key, acceptance vs repetitive share (n = 256), v0.3 hollow vs v0.4 filled
fig, axs = plt.subplots(1, 3, figsize=(9.2, 3.1), sharey=True)
for ax, lv in zip(axs, LEVELS):
    for r, mk in (("A", "^"), ("B", "D")):
        for v, filled in (("v03", False), ("v04", True)):
            c = f"{v}_{r}_n256"
            xs = [100 * float((~flags(s, lv, c)[2]).mean()) for s in KEYS]
            ys = [100 * float(flags(s, lv, c)[0].mean()) for s in KEYS]
            ax.scatter(xs, ys, s=30, marker=mk, color=COL[r] if filled else "white", edgecolor=COL[r], linewidth=1,
                       label=f"Route {r} {v.replace('v0', 'v0.')}", zorder=3 if filled else 2)
    ax.axvline(5, color=MUTED, lw=1, ls=":")
    ax.set_xlim(-3, 103)
    ax.set_ylim(-5, 108)
    ax.set_title(f"ρ = {lv}", fontsize=9, color=INK)
    ax.set_xlabel("texts above the seq-rep-4 bar (%)")
axs[0].set_ylabel("Accepted (%)")
axs[0].legend(frameon=False, fontsize=7, loc="center right")
fig.suptitle("Forged texts per key (n = 256): filled = v0.4 (repetition-screened), hollow = v0.3; dotted line = the oracle's 5%",
             fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(OUT / "fig3_repetition.png", dpi=200)
plt.close(fig)
print("ok: integrity asserts passed; wrote", sorted(p.name for p in OUT.iterdir()))

# ---- assemble the report (only if the prose exists)
pf = Path(__file__).parent / "report_prose.md"
if not pf.exists():
    sys.exit("report_prose.md not written yet; assets only")
prose = pf.read_text()
for ph in ("<<TABLE1>>", "<<TABLES234>>", "<<SAMPLES>>"):
    assert prose.count(ph) == 1, ph
t1, rest = tables_main.split("## Table 2", 1)
report = (prose.replace("<<TABLE1>>", t1.replace("## Table 1", "### Table 1").strip())
          .replace("<<TABLES234>>", ("## Table 2" + rest).replace("## Table", "### Table").strip())
          .replace("<<SAMPLES>>", samples.replace("### ρ", "#### ρ").strip()))
(ROOT / "STUDY1_REPORT_v0.4.md").write_text(report)
print("wrote", ROOT / "STUDY1_REPORT_v0.4.md")
