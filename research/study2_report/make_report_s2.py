"""Build the Study 2 v0.1 report tables, figures and samples from the locked outputs (numbers are never retyped).

Written during the run (phase 1), before any Study 2 outcome was read (2026-10-01, Milestone 7).
Reads research/outputs/study2_v0.1/results.json, the per-text features, quality and probe scores in research/study2/data/
(git-ignored), and Study 3's features and results. Before writing anything it re-computes, with its own implementation of
the S4 test and of the quality conditions (not common_s2 / scrub_core / common_s3):
  - G1 and G2 (each key's FPR on the paraphrased null texts), P1 (detection before scrubbing);
  - for every method and level: each key's detection after scrubbing, success and originals' miss rate;
  - the first-attempt-only success, the length-matched control and the probe's acceptance;
  - every S1, S2 and C1 verdict, from the summaries, with the protocol's §7 rule written out again here;
and asserts that they equal results.json.
Writes research/outputs/study2_v0.1/report/: tables.md, samples.md, prose_values.json and fig1-fig5 (.png). Then assembles
research/STUDY2_REPORT_v0.1.md from report_prose.md (placeholders <<TABLE1>>, <<TABLES>>, <<SAMPLES>>, [[name]]) if the
prose exists.
Run: .venv/bin/python research/study2_report/make_report_s2.py
"""
import difflib
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "study1"))
import core  # noqa: E402  (keys only: make_key, the null-key seeds)

RES = ROOT / "outputs" / "study2_v0.1" / "results.json"
D2S, D3S = ROOT / "study2" / "data", ROOT / "study3" / "data"
OUT = ROOT / "outputs" / "study2_v0.1" / "report"
REPORT = ROOT / "STUDY2_REPORT_v0.1.md"
TEST = len(sys.argv) > 2 and sys.argv[1] == "--fixture"      # builder test on a synthetic fixture (no outcomes)
if TEST:
    FX = Path(sys.argv[2])
    RES, D2S, OUT, REPORT = FX / "out" / "results.json", FX / "data", FX / "report", FX / "STUDY2_REPORT_fixture.md"
R3 = json.loads((ROOT / "outputs" / "study3_v0.1" / "results.json").read_text())["S4"]
KEYS = list(range(1001, 1009))
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
TAG = {"0.25": "025", "0.35": "035", "0.5": "050", "0.7": "070"}
LV = {"0.25": "25", "0.35": "35", "0.5": "50", "0.7": "70"}
MODELS = ["qwen", "phi"]
N_GEN = {"qwen": 100, "phi": 50}
ARMS = ["true", "est", "rand"]
BUDGETS = ["0.02", "0.05", "0.1"]
PRIMARY = "0.05"
ALPHA, BAR, NEW_TOKENS, D = 0.01, 50.0, 256, 1536
G1_RANGE, G2_MAX, MIN_CAL, P1_MIN = (0.3, 2.5), 3.0, 6, 20.0
MNAME = {"qwen": "P-Qwen (Qwen2.5-1.5B-Instruct)", "phi": "P-Phi (Phi-3.5-mini-instruct)",
         "true": "E-true (true key)", "est": "E-est (attacker's estimate)", "rand": "E-rand (random edits)"}
SHORT = {"qwen": "P-Qwen", "phi": "P-Phi", "true": "E-true", "est": "E-est", "rand": "E-rand"}
# palette: categorical slots 1, 2, 3, 7 (validated all-pairs, light); controls in recessive gray
INK, MUTED, GRID, CTRL = "#1f1f1e", "#6b6a64", "#e4e3dc", "#52514e"
COL = {"qwen": "#2a78d6", "phi": "#eb6834", "true": "#1baf7a", "est": "#4a3aa7", "rand": CTRL}
MK = {"qwen": "o", "phi": "s", "true": "D", "est": "^", "rand": "v"}

res = json.loads(RES.read_text())
assert res["dry"] is False or TEST, "results.json comes from the dry smoke test"
bars = json.loads((D2S / "bars.json").read_text())
CAL = {m: [int(s) for s in res["calibration"][m]["G2"]["calibrated"]] for m in MODELS}


def jl(p):
    return json.loads(Path(p).read_text())


def tg(s, lv):
    return f"k{s}_r{TAG[lv]}"


# ---------------------------------------------------------------- independent S4 (Study 3's definition, re-written)
def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def key_unit(seed):
    return unit(core.make_key(seed, D, 1.0).numpy().astype(np.float64))


NULL = np.stack([key_unit(core.NULL_KEY_SEED * 100000 + j) for j in range(999)])
Gf = np.load(D3S / "S_F_van.npz")["G"].astype(np.float64)
MU, SD = Gf.mean(0), np.maximum(Gf.std(0, ddof=1), 1e-12)
KU = {s: key_unit(s) for s in KEYS}


def pvals(G, s):
    X = unit((np.asarray(G, dtype=np.float64) - MU) / SD)
    return (1 + ((X @ NULL.T) >= (X @ KU[s])[:, None]).sum(1)) / 1000


def pvals_lab(G, lab):
    p = np.empty(len(lab))
    for s in KEYS:
        idx = [i for i, l in enumerate(lab) if l[0] == s]
        if idx:
            p[idx] = pvals(G[idx], s)
    return p


# ---------------------------------------------------------------- independent quality conditions (protocol §5)
def conds(o, z, b):
    olen = np.minimum(o["len"], NEW_TOKENS)
    c = {"ppl": z["ppl"] <= np.maximum(1.25 * o["ppl"], b["ppl"]), "rep": z["rep"] <= np.maximum(o["rep"], b["rep"]),
         "len": z["len"] >= 0.8 * olen, "cos": z["cos"] > b["cos"]}
    c["all"] = c["ppl"] & c["rep"] & c["len"] & c["cos"]
    return c


# ---------------------------------------------------------------- per-text rows for every scrubbed set
def labels(name):
    """(key, level, index) per text, rebuilt from the protocol's order (keys, then levels, then pool D order)."""
    if name.startswith(("para_", "para1_", "lm_")):
        m = name.split("_")[1]
        return [(s, lv, j) for s in KEYS for lv in LEVELS for j in range(N_GEN[m])]
    return [(s, lv, j) for s in KEYS for lv in LEVELS for j in range(len(jl(D2S / f"edits_{name.split('_')[1]}_{tg(s, lv)}.json")["recs"]))]


OQ = {tg(s, lv): {k: np.asarray(v, dtype=np.float64) for k, v in bars["orig"][tg(s, lv)].items()} for s in KEYS for lv in LEVELS}


def rows(name, lab=None):
    lab = labels(name) if lab is None else lab
    G = np.load(D2S / f"G_{name}.npy")
    assert len(G) == len(lab), (name, len(G), len(lab))
    Q = {k: np.asarray(v, dtype=np.float64) for k, v in jl(D2S / f"Q_{name}.json").items()}
    o = {k: np.array([OQ[tg(l[0], l[1])][k][l[2]] for l in lab]) for k in ("ppl", "rep", "len")}
    p = pvals_lab(G, lab)
    c = {b: conds(o, Q, bars[b]) for b in ("A", "A_model_p95", "A_human_median")}
    return {"p": p, "c": c["A"], "succ": {b: (p > ALPHA) & c[b]["all"] for b in c}, "lab": lab, "Q": Q, "o": o}


SETS = [f"para_{m}_gen" for m in MODELS] + [f"edit_{a}_{f}" for a in ARMS for f in BUDGETS]
ROWS = {n: rows(n) for n in SETS}
for m in MODELS:
    P = jl(D2S / f"para_{m}_gen.json")
    assert [tuple(x) for x in P["labels"]] == [(s, float(lv), j) for s, lv, j in labels(f"para_{m}_gen")], m
    diff = [i for i, a in enumerate(P["kept"]) if a != 0]
    k = ROWS[f"para_{m}_gen"]
    r1 = {"p": k["p"].copy(), "c": {c: v.copy() for c, v in k["c"].items()}, "succ": {b: v.copy() for b, v in k["succ"].items()},
          "lab": k["lab"], "Q": {q: v.copy() for q, v in k["Q"].items()}, "o": k["o"]}
    if diff:
        d = rows(f"para1_{m}_gen", [k["lab"][i] for i in diff])
        for j, i in enumerate(diff):
            r1["p"][i] = d["p"][j]
            for c in r1["c"]:
                r1["c"][c][i] = d["c"][c][j]
            for b in r1["succ"]:
                r1["succ"][b][i] = d["succ"][b][j]
            for q in r1["Q"]:
                r1["Q"][q][i] = d["Q"][q][j]
    ROWS[f"para1_{m}_gen"] = r1


def per_key(name, flag, lv, ks):
    r = ROWS[name]
    return {s: 100 * float(np.mean([f for f, l in zip(flag, r["lab"]) if l[0] == s and l[1] == lv])) for s in ks}


def close(a, b, what):
    assert set(map(str, a)) == set(b), (what, sorted(a), sorted(b))
    for s, v in a.items():
        assert abs(v - b[str(s)]) < 1e-9, (what, s, v, b[str(s)])


# ---------------------------------------------------------------- integrity: re-compute and assert
P0 = {(s, lv): pvals(np.load(D3S / f"K_{tg(s, lv)}_oracle.npz")["G"][:100], s) for s in KEYS for lv in LEVELS}
for m in MODELS:
    Gn = np.load(D2S / f"G_para_{m}_null.npy")
    assert len(Gn) == 1000, m
    fpr = {s: 100 * float((pvals(Gn, s) <= ALPHA).mean()) for s in KEYS}
    C = res["calibration"][m]
    close(fpr, C["G2"]["per_key_fpr_pct"], f"G2 {m}")
    assert abs(np.mean(list(fpr.values())) - C["G1"]["pooled_fpr_pct"]) < 1e-9, m
    assert C["G1"]["pass"] == (G1_RANGE[0] <= C["G1"]["pooled_fpr_pct"] <= G1_RANGE[1]), m
    assert sorted(CAL[m]) == sorted(s for s in KEYS if fpr[s] <= G2_MAX), m
    assert C["G2"]["verdicts_made"] == (len(CAL[m]) >= MIN_CAL), m


def rule(method, comp):
    """§7, re-written: effective if median >= 50 and lower bound > the comparison's upper bound; not effective if the
    upper bound < 50; otherwise inconclusive."""
    if method["median"] >= BAR and method["ci95"][0] > comp["ci95"][1]:
        return "effective"
    return "not effective" if method["ci95"][1] < BAR else "inconclusive"


for lv in LEVELS:
    L = res["levels"][lv]
    close({s: 100 * float((P0[(s, lv)] <= ALPHA).mean()) for s in KEYS}, L["P1"]["detected_before"]["per_key"], f"P1 {lv}")
    assert L["P1"]["pass"] == (L["P1"]["detected_before"]["median"] >= P1_MIN)
    assert abs(np.median(list(L["P1"]["detected_before"]["per_key"].values())) - L["P1"]["detected_before"]["median"]) < 1e-9
    for m in MODELS:
        ks, n, S1 = CAL[m], N_GEN[m], L[f"S1_{m}"]
        close({s: 100 * float((P0[(s, lv)][:n] > ALPHA).mean()) for s in ks}, S1["originals_miss"]["per_key"], f"miss {m} {lv}")
        for nm, blk in ((f"para_{m}_gen", S1), (f"para1_{m}_gen", S1["first_attempt"])):
            r = ROWS[nm]
            close(per_key(nm, r["succ"]["A"], lv, ks), blk["success"]["per_key"], f"success {nm} {lv}")
            close(per_key(nm, r["p"] <= ALPHA, lv, ks), blk["detected_after"]["per_key"], f"detected {nm} {lv}")
            for b in ("A_model_p95", "A_human_median"):
                assert abs(np.median(list(per_key(nm, r["succ"][b], lv, ks).values())) - blk["success_stricter"][b]) < 1e-9
        made = L["P1"]["pass"] and len(ks) >= MIN_CAL
        assert S1["verdict"] == (rule(S1["success"], S1["originals_miss"]) if made else "not made"), (m, lv)
        assert S1["keys_success_ge_50"] == sum(v >= BAR for v in S1["success"]["per_key"].values())
    for a in ARMS:
        for f in BUDGETS:
            r, blk = ROWS[f"edit_{a}_{f}"], L[f"E-{a} {f}"]
            close(per_key(f"edit_{a}_{f}", r["succ"]["A"], lv, KEYS), blk["success"]["per_key"], f"success {a} {f} {lv}")
            close(per_key(f"edit_{a}_{f}", r["p"] <= ALPHA, lv, KEYS), blk["detected_after"]["per_key"], f"det {a} {f} {lv}")
    for a in ("true", "est"):
        assert L[f"S2_{a}"]["verdict"] == (rule(L[f"E-{a} {PRIMARY}"]["success"], L[f"E-rand {PRIMARY}"]["success"])
                                           if L["P1"]["pass"] else "not made"), (a, lv)
    d = [L[f"E-est {PRIMARY}"]["success"]["per_key"][str(s)] - L[f"E-rand {PRIMARY}"]["success"]["per_key"][str(s)] for s in KEYS]
    assert abs(np.median(d) - L["C1"]["median"]) < 1e-9, lv
    c1 = L["C1"]["ci95"]
    want = "the estimate helps" if c1[0] > 0 else ("the estimate hurts" if c1[1] < 0 else "no clear difference")
    assert L["C1"]["verdict"] == (want if L["P1"]["pass"] else "not made"), lv

LMMED = {}
for m in MODELS:
    lab = labels(f"lm_{m}_gen")
    plm = pvals_lab(np.load(D2S / f"G_lm_{m}_gen.npy"), lab)
    for lv in LEVELS:
        got = 100 * float(np.mean([p <= ALPHA for p, l in zip(plm, lab) if l[1] == lv]))
        assert abs(got - res["secondary"]["length_matched"][m][lv]) < 1e-9, (m, lv)
        # builder-side descriptive: the same control as a median over the paraphraser's calibrated keys (Fig. 1)
        LMMED[(m, lv)] = float(np.median([100 * np.mean([p <= ALPHA for p, l in zip(plm, lab) if l[0] == s and l[1] == lv])
                                          for s in CAL[m]]))
for name in SETS:
    pr = jl(D2S / f"probe_{name}.json")
    for lv in LEVELS:
        acc = [100 * float(np.mean(np.asarray(pr[tg(s, lv)]["scores"]) > pr[tg(s, lv)]["threshold"])) for s in KEYS]
        assert abs(float(np.median(acc)) - res["secondary"]["probe"][name][lv]) < 1e-9, (name, lv)
OUT.mkdir(parents=True, exist_ok=True)
print("ok: integrity asserts passed (S4 p-values, quality conditions, rules, controls and probe re-computed)")


# ---------------------------------------------------------------- tables
def f1(x):
    return "—" if x is None else f"{x:.1f}"


def cis(c):
    return f"[{c[0]:.1f}, {c[1]:.1f}]"


def mc(s):
    return f"{s['median']:.1f} {cis(s['ci95'])}"


def rand_flag(lv):
    return res["levels"][lv][f"E-rand {PRIMARY}"]["success"]["median"] >= BAR


T = ["## Table 1 — Pre-registered rules vs observed (protocol §7)\n"]
for m in MODELS:
    C = res["calibration"][m]
    T.append(f"**{MNAME[m]}.** G1 (pooled FPR over 8 keys × 1,000 paraphrased pool A texts, pass if {G1_RANGE[0]}–{G1_RANGE[1]}%): "
             f"{C['G1']['pooled_fpr_pct']:.2f}% → **{'PASS' if C['G1']['pass'] else 'FAIL'}**. G2 (a key is calibrated if its "
             f"FPR ≤ {G2_MAX}%): {C['G2']['n_calibrated']} of 8 calibrated → verdicts **{'made' if C['G2']['verdicts_made'] else 'not made'}**"
             + (f" (excluded: {', '.join(str(s) for s in KEYS if s not in CAL[m])})" if len(CAL[m]) < 8 else "") + ".\n")
T.append("| ρ | P1: detected before, median (≥ 20%) | S1 P-Qwen: success [95% CI] vs originals' miss [95% CI]; keys ≥ 50% | "
         "S1 P-Phi: same | S2 E-true 5%: success [95% CI]; keys ≥ 50% | S2 E-est 5%: same | E-rand 5%: success [95% CI] | "
         "C1: E-est − E-rand, median [95% CI] |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    s1 = [f"**{L[f'S1_{m}']['verdict']}**: {mc(L[f'S1_{m}']['success'])} vs {mc(L[f'S1_{m}']['originals_miss'])}; "
          f"{L[f'S1_{m}']['keys_success_ge_50']} of {len(CAL[m])}" for m in MODELS]
    s2 = [f"**{L[f'S2_{a}']['verdict']}**: {mc(L[f'E-{a} {PRIMARY}']['success'])}; {L[f'S2_{a}']['keys_success_ge_50']} of 8"
          for a in ("true", "est")]
    rf = " (**random edits suffice**)" if rand_flag(lv) else ""
    T.append(f"| {float(lv):.2f} | {L['P1']['detected_before']['median']:.1f}% ({'pass' if L['P1']['pass'] else 'fail'}) | {s1[0]} | {s1[1]} | "
             f"{s2[0]} | {s2[1]} | {mc(L[f'E-rand {PRIMARY}']['success'])}{rf} | **{L['C1']['verdict']}**: "
             f"{L['C1']['median']:+.1f} {cis(L['C1']['ci95'])} |")
T.append("\nSuccess = not detected by S4 at p ≤ 0.01 **and** all four quality conditions pass (fluency, repetition, length, meaning; "
         "protocol §5, normal range at the human 95th percentile). Medians over the calibrated keys (paraphrase: G2 per "
         "paraphraser; edits: all 8 keys, Study 3's calibration), with 95% cluster-bootstrap intervals (keys, then texts). P-Phi "
         "scrubs the first 50 genuine texts per key-level, the others all 100. \"Random edits suffice\" marks a level where "
         "E-rand's own median success at 5% reaches 50% (protocol §7, bounds).\n")

T.append("## Table 2 — Calibration after paraphrase: each key's FPR at p ≤ 0.01 (%) on 1,000 pool A texts\n")
T.append("| null texts | " + " | ".join(str(s) for s in KEYS) + " | pooled | keys > 3% | fresh keys: mean FPR | fresh keys > 3% | "
         "probe FPR on pool A2 (median) |")
T.append("|---|" + "---|" * (len(KEYS) + 5))
v3 = R3["G2"]["per_key_fpr_pct"]
T.append("| unparaphrased (Study 3) | " + " | ".join(f"{v3[str(s)]:.1f}" for s in KEYS) +
         f" | {R3['G1']['pooled_fpr_pct']:.2f} | {sum(v3[str(s)] > 3 for s in KEYS)} | — | — | — |")
for m in MODELS:
    C = res["calibration"][m]
    v = C["G2"]["per_key_fpr_pct"]
    T.append(f"| paraphrased by {SHORT[m]} | " + " | ".join(f"{v[str(s)]:.1f}" for s in KEYS) +
             f" | {C['G1']['pooled_fpr_pct']:.2f} | {sum(v[str(s)] > G2_MAX for s in KEYS)} | {C['fresh_keys']['mean_fpr_pct']:.2f} | "
             f"{100 * C['fresh_keys']['share_above_3pct']:.1f}% (max {C['fresh_keys']['max_fpr_pct']:.1f}) | "
             f"{C['probe_fpr_on_paraphrased_A2_pct']['median']:.1f} |")
T.append("\nFresh keys: 1,000 public-distribution keys never used by the owner (seeds 44,400,000 + j), each tested on the same "
         "paraphrased texts; the share above 3% estimates how often a newly drawn key would fail G2 after paraphrase. The probe "
         "row is the owner's trained probe (Study 1) at its own 1% threshold on the paraphrased pool A2 texts (secondary).\n")

T.append("## Table 3 — Detection, quality and success per method (median over keys, %; ρ by row)\n")
T.append("| ρ | method | detected after | success [95% CI] | keys ≥ 50% | passes fluency | repetition | length | meaning | all four | "
         "median ppl ratio | median length ratio | median cosine | success, model-text bar | success, human-median bar |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    items = [(SHORT[m], L[f"S1_{m}"]) for m in MODELS] + [(f"{SHORT[a]} {100 * float(f):.0f}%", L[f"E-{a} {f}"])
                                                           for f in BUDGETS for a in ARMS]
    for nm, d in items:
        T.append(f"| {float(lv):.2f} | {nm} | {d['detected_after']['median']:.1f} | {mc(d['success'])} | {d['success']['keys_ge_50']} | "
                 + " | ".join(f"{d['pass'][c]:.1f}" for c in ("ppl", "rep", "len", "cos", "all")) +
                 f" | {d.get('median_ppl_ratio', float('nan')):.2f} | {d.get('median_len_ratio', float('nan')):.2f} | "
                 f"{d.get('median_cos', float('nan')):.3f} | {d['success_stricter']['A_model_p95']:.1f} | "
                 f"{d['success_stricter']['A_human_median']:.1f} |")
b = res["bars"]
T.append(f"\nNormal range (pool A's human continuations, 95th percentile): perplexity {b['A']['ppl']:.2f}, seq-rep-4 "
         f"{b['A']['rep']:.4f}; meaning bar (cosine, 95th percentile of same-prompt pairs) {b['A']['cos']:.3f}. Stricter readings "
         f"(secondary): model-text 95th percentile (perplexity {b['A_model_p95']['ppl']:.2f}, seq-rep-4 {b['A_model_p95']['rep']:.4f}) "
         f"and human median (perplexity {b['A_human_median']['ppl']:.2f}, seq-rep-4 {b['A_human_median']['rep']:.4f}). The "
         f"attacker's own bars (pool C): perplexity {b['C']['ppl']:.2f}, seq-rep-4 {b['C']['rep']:.4f}, cosine {b['C']['cos']:.3f}. "
         "Ratios are scrub / original (length: original counted up to 256 tokens).\n")

T.append("## Table 4 — Per-key success (%), the per-unit view behind every median (keys excluded by G2 shown as —)\n")
T.append("| ρ | method | " + " | ".join(str(s) for s in KEYS) + " | median | keys ≥ 50% |")
T.append("|---|---|" + "---|" * (len(KEYS) + 2))
for lv in LEVELS:
    L = res["levels"][lv]
    items = [(SHORT[m], L[f"S1_{m}"]["success"]) for m in MODELS] + \
            [(f"{SHORT[a]} {100 * float(f):.0f}%", L[f"E-{a} {f}"]["success"]) for f in (PRIMARY, "0.1") for a in ARMS]
    for nm, s_ in items:
        pk = s_["per_key"]
        T.append(f"| {float(lv):.2f} | {nm} | " + " | ".join(f"{pk[str(s)]:.0f}" if str(s) in pk else "—" for s in KEYS) +
                 f" | {s_['median']:.1f} | {s_['keys_ge_50']} |")
T.append("")

SEC = res["secondary"]
T.append("## Table 5 — Secondary readings (median over keys unless stated, %)\n")
T.append("| ρ | method | detected after (p ≤ 0.01) | at p ≤ 0.001 (9,999 null keys) | 4 texts pooled: detected | "
         "length-matched originals: detected (pooled; median over keys) | owner's probe accepts | first attempt only: success |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = res["levels"][lv]
    T.append(f"| {float(lv):.2f} | unscrubbed | {L['P1']['detected_before']['median']:.1f} | {100 * R3['levels'][lv]['oracle']['acceptance_0.001_median']:.1f} "
             f"(Study 3) | {100 * R3['levels'][lv]['oracle']['pooled4_detection_median']:.1f} (Study 3) | — | "
             f"{100 * R3['levels'][lv]['oracle']['probe_acceptance_median']:.1f} (Study 3) | — |")
    for m in MODELS:
        nm = f"para_{m}_gen"
        T.append(f"| {float(lv):.2f} | {SHORT[m]} | {L[f'S1_{m}']['detected_after']['median']:.1f} | {f1(SEC['alpha_0.001'][nm][lv])} | "
                 f"{f1(SEC['pooled_4'][nm][lv])} | {SEC['length_matched'][m][lv]:.1f}; {LMMED[(m, lv)]:.1f} | "
                 f"{SEC['probe'][nm][lv]:.1f} | {L[f'S1_{m}']['first_attempt']['success']['median']:.1f} |")
    for a in ARMS:
        nm = f"edit_{a}_{PRIMARY}"
        T.append(f"| {float(lv):.2f} | {SHORT[a]} 5% | {L[f'E-{a} {PRIMARY}']['detected_after']['median']:.1f} | {f1(SEC['alpha_0.001'][nm][lv])} | "
                 f"{f1(SEC['pooled_4'][nm][lv])} | — | {SEC['probe'][nm][lv]:.1f} | — |")
T.append("\nThe 0.001 and pooled readings use all 8 keys (median). The length-matched control truncates each original to its "
         "paraphrase's token count and scores it with S4: it separates \"less text\" from \"evidence removed\". The probe "
         "column is the share of scrubbed texts the owner's trained probe still accepts at its 1% threshold.\n")
pa = SEC["paraphrase_attempts"]
T.append("Paraphrase attempts kept (genuine texts): " + "; ".join(
    f"{SHORT[m]}: " + ", ".join(f"attempt {a} {pa[m]['used'][a]}" for a in ("1", "2", "3")) +
    f"; kept but still failing the attacker's own check {pa[m]['kept_failing_attacker_check']} of {8 * 4 * N_GEN[m]}"
    for m in MODELS) + ".\n")
ed = SEC["edits"]
T.append("Edits: " + "; ".join(
    f"{SHORT[a]}: stalled before 10% in {ed[a]['stalled']} texts, median re-tokenisation drift "
    + ", ".join(f"{float(f) * 100:.0f}% {ed[a]['median_drift'][f]:.3f}" for f in BUDGETS)
    + (", attacker's objective (median) " + " → ".join(f"{ed[a]['median_objective'][k]:.2f}" for k in ["0"] + BUDGETS)
       if "median_objective" in ed[a] else "") for a in ARMS) + ".\n")

T.append("## Table 6 — The edit curve: success, detection and quality by budget (median over all 8 keys, %)\n")
T.append("| ρ | arm | success 0% (originals' miss) | success 2% | 5% | 10% | detected 2% | 5% | 10% | all four quality 2% | 5% | 10% |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
MISS0 = {lv: float(np.median([100 - v for v in res["levels"][lv]["P1"]["detected_before"]["per_key"].values()])) for lv in LEVELS}
for lv in LEVELS:
    L = res["levels"][lv]
    for a in ARMS:
        T.append(f"| {float(lv):.2f} | {SHORT[a]} | {MISS0[lv]:.1f} | " + " | ".join(f"{L[f'E-{a} {f}']['success']['median']:.1f}" for f in BUDGETS) +
                 " | " + " | ".join(f"{L[f'E-{a} {f}']['detected_after']['median']:.1f}" for f in BUDGETS) + " | " +
                 " | ".join(f"{L[f'E-{a} {f}']['pass']['all']:.1f}" for f in BUDGETS) + " |")
T.append("")
kl = SEC["key_leakage"]
T.append(f"Key leakage (secondary): Spearman correlation between the attacker's recovered cosine cos(v̂, v) and E-est's success at "
         f"5%, over the 32 key-levels: {kl['spearman_success_vs_cos']:.2f} (descriptive; Fig. 4).\n")
tables = "\n".join(T) + "\n"
(OUT / "tables.md").write_text(tables)

# ---------------------------------------------------------------- samples (protocol §8: read and quoted)


def marked(orig, new):
    """The edited text with each replaced word in bold and the original word after it in parentheses."""
    a, b = orig.split(), new.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out += b[j1:j2]
        elif op == "replace":
            out.append("**" + " ".join(b[j1:j2]) + "** (was: " + " ".join(a[i1:i2]) + ")")
        elif op == "insert":
            out.append("**" + " ".join(b[j1:j2]) + "** (inserted)")
        elif op == "delete" and i2 < len(a) and j1 < len(b):
            out.append("(deleted: " + " ".join(a[i1:i2]) + ")")
    return " ".join(out)


def bq(text):
    return text.strip().replace("\n", "\n> ")


def qline(name, s, lv, j):
    r = ROWS[name]
    i = next(i for i, l in enumerate(r["lab"]) if l == (s, lv, j))
    c = r["c"]
    return (f"S4 p = {r['p'][i]:.3f} ({'detected' if r['p'][i] <= ALPHA else 'not detected'}); perplexity {r['Q']['ppl'][i]:.1f} "
            f"(original {r['o']['ppl'][i]:.1f}), seq-rep-4 {r['Q']['rep'][i]:.3f}, {int(r['Q']['len'][i])} tokens (original "
            f"{int(min(r['o']['len'][i], NEW_TOKENS))}), cosine {r['Q']['cos'][i]:.3f}; conditions: "
            + ", ".join(f"{k} {'pass' if c[k][i] else 'FAIL'}" for k in ("ppl", "rep", "len", "cos"))
            + f" → **{'success' if r['succ']['A'][i] else 'no success'}**")


SM = ["Each sample is the first pool D text of the key-level, as the protocol fixes (§8). Edited words are in **bold**, with "
      "the original word in parentheses. Texts are quoted in full as scored (edits: the first 256 tokens).\n"]
for smp in res["samples"]:
    s, lv = smp["key"], str(smp["rho"])
    assert lv in LEVELS, lv
    assert abs(smp["p_original"] - P0[(s, lv)][0]) < 1e-12, s
    SM.append(f"### Key {s}, ρ = {float(lv):.2f}\n")
    SM.append(f"**Original** (S4 p = {smp['p_original']:.3f}):\n\n> {bq(smp['original'])}\n")
    for m in MODELS:
        nm = f"para_{m}_gen"
        assert abs(smp[f"p_{nm}"] - ROWS[nm]["p"][ROWS[nm]["lab"].index((s, lv, 0))]) < 1e-12
        SM.append(f"**{MNAME[m]}** — {qline(nm, s, lv, 0)}:\n\n> {bq(smp[nm])}\n")
    for f, fs in (("0.05", "0.05"), ("0.1", "0.1")):
        for a in ARMS:
            nm = f"edit_{a}_{f}"
            SM.append(f"**{MNAME[a]}, {100 * float(f):.0f}% of tokens** — {qline(nm, s, lv, 0)}:\n\n> {bq(marked(smp['original'], smp[nm]))}\n")
samples = "\n".join(SM) + "\n"
(OUT / "samples.md").write_text(samples)

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6})
RHO = [float(v) for v in LEVELS]
XLAB = "Watermark strength ρ = ‖v‖ / median activation norm"


def band(ax, ys, col, lab, mk, ls="-", hollow=False, ci=None):
    if ci is not None:
        ax.fill_between(RHO, [c[0] for c in ci], [c[1] for c in ci], color=col, alpha=0.12, linewidth=0)
    ax.plot(RHO, ys, ls, color=col, lw=2 if not hollow else 1.4, marker=mk, ms=7, mfc="white" if hollow else col,
            mec=col, label=lab)


# Fig 1: detection after and success, paraphrase (left) and edits at 5% (right)
fig, axs = plt.subplots(2, 2, figsize=(9.6, 8.4), sharex=True)
before = [res["levels"][lv]["P1"]["detected_before"]["median"] for lv in LEVELS]
bci = [res["levels"][lv]["P1"]["detected_before"]["ci95"] for lv in LEVELS]
for ax in axs[0]:
    band(ax, before, INK, "unscrubbed (Study 3's features)", "o", ci=bci)
for m in MODELS:
    d = [res["levels"][lv][f"S1_{m}"]["detected_after"] for lv in LEVELS]
    band(axs[0, 0], [x["median"] for x in d], COL[m], f"{SHORT[m]}", MK[m], ci=[x["ci95"] for x in d])
    band(axs[0, 0], [LMMED[(m, lv)] for lv in LEVELS], COL[m], f"{SHORT[m]}: originals cut to the paraphrase's length",
         MK[m], ls="--", hollow=True)
    s_ = [res["levels"][lv][f"S1_{m}"]["success"] for lv in LEVELS]
    band(axs[1, 0], [x["median"] for x in s_], COL[m], SHORT[m], MK[m], ci=[x["ci95"] for x in s_])
miss = [res["levels"][lv]["S1_qwen"]["originals_miss"]["median"] for lv in LEVELS]
band(axs[1, 0], miss, CTRL, "originals' miss rate (P-Qwen's keys)", "o", ls=":", hollow=True)
for a in ARMS:
    d = [res["levels"][lv][f"E-{a} {PRIMARY}"]["detected_after"] for lv in LEVELS]
    s_ = [res["levels"][lv][f"E-{a} {PRIMARY}"]["success"] for lv in LEVELS]
    ls = "--" if a == "rand" else "-"
    band(axs[0, 1], [x["median"] for x in d], COL[a], SHORT[a], MK[a], ls=ls, ci=[x["ci95"] for x in d])
    band(axs[1, 1], [x["median"] for x in s_], COL[a], SHORT[a], MK[a], ls=ls, ci=[x["ci95"] for x in s_])
for ax in axs[1]:
    ax.axhline(BAR, color=INK, lw=1, ls="--")
    ax.text(0.775, BAR + 1.5, "50% materiality bar", color=INK, fontsize=7.5, ha="right", va="bottom")
    ax.set_xlabel(XLAB)
for ax in axs.flat:
    ax.set_xticks(RHO)
    ax.set_xlim(0.22, 0.78)
    ax.set_ylim(-3, 104)
axs[0, 0].set_ylabel("detected by S4 at p ≤ 0.01 (%)")
axs[1, 0].set_ylabel("scrub success (%)\nnot detected and all quality conditions pass")
axs[0, 0].set_title("Paraphrase (no key)", fontsize=9, color=INK, loc="left")
axs[0, 1].set_title("Word edits at 5% of tokens", fontsize=9, color=INK, loc="left")
for j in range(2):                     # one legend per column, below the figure (never over the data)
    h, lab = axs[0, j].get_legend_handles_labels()
    h2, lab2 = axs[1, j].get_legend_handles_labels()
    extra = [(a, b) for a, b in zip(h2, lab2) if b not in lab]
    axs[1, j].legend(h + [a for a, _ in extra], lab + [b for _, b in extra], frameon=False, fontsize=7, loc="upper center",
                     bbox_to_anchor=(0.5, -0.2), ncol=2)
fig.suptitle("Study 2: S4 detection and scrub success after each method (median over calibrated keys, 95% CI)",
             fontsize=9.5, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(OUT / "fig1_scrubbing.png", dpi=200)
plt.close(fig)

# Fig 2: success against the edit budget, per arm, one panel per level
fig, axs = plt.subplots(1, 4, figsize=(10.5, 3.6), sharey=True)
XB = [0, 2, 5, 10]
for ax, lv in zip(axs, LEVELS):
    L = res["levels"][lv]
    for a in ARMS:
        y = [MISS0[lv]] + [L[f"E-{a} {f}"]["success"]["median"] for f in BUDGETS]
        lo = [MISS0[lv]] + [L[f"E-{a} {f}"]["success"]["ci95"][0] for f in BUDGETS]
        hi = [MISS0[lv]] + [L[f"E-{a} {f}"]["success"]["ci95"][1] for f in BUDGETS]
        ax.fill_between(XB, lo, hi, color=COL[a], alpha=0.12, linewidth=0)
        ax.plot(XB, y, "--" if a == "rand" else "-", color=COL[a], lw=2, marker=MK[a], ms=7, label=SHORT[a])
    ax.axhline(BAR, color=INK, lw=1, ls="--")
    ax.axvline(5, color=MUTED, lw=1, ls=":")
    ax.set_xticks(XB)
    ax.set_xlim(-0.6, 10.6)
    ax.set_ylim(-3, 104)
    ax.set_title(f"ρ = {float(lv):.2f}", fontsize=9, color=INK)
    ax.set_xlabel("edited tokens (%)")
axs[0].set_ylabel("scrub success (%)")
axs[0].text(5.3, 97, "judged\nat 5%", color=MUTED, fontsize=7, va="top", ha="left")
h, lab = axs[0].get_legend_handles_labels()
fig.legend(h, lab, frameon=False, fontsize=8, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0))
fig.suptitle("Study 2: scrub success against the edit budget (median over 8 keys, 95% CI; 0% = the originals' miss rate; "
             "dashed line = 50%)", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(OUT / "fig2_edit_budget.png", dpi=200)
plt.close(fig)

# Fig 3: per-key calibration after paraphrase
fig, ax = plt.subplots(figsize=(6.4, 3.6))
x = np.arange(len(KEYS))
ax.scatter(x - 0.16, [v3[str(s)] for s in KEYS], s=40, marker="o", color="white", edgecolor=INK, linewidth=1.3, zorder=3,
           label="unparaphrased (Study 3)")
for m, off in (("qwen", 0.0), ("phi", 0.16)):
    v = res["calibration"][m]["G2"]["per_key_fpr_pct"]
    ax.scatter(x + off, [v[str(s)] for s in KEYS], s=40, marker=MK[m], color=COL[m], edgecolor="white", linewidth=0.8, zorder=3,
               label=f"paraphrased by {SHORT[m]}")
ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.axhline(G2_MAX, color=INK, lw=1, ls="--")
ax.text(len(KEYS) - 0.45, G2_MAX, "G2 bar 3%", color=INK, fontsize=7.5, va="bottom", ha="right")
ax.text(len(KEYS) - 0.45, 1, "nominal 1%", color=MUTED, fontsize=7.5, va="bottom", ha="right")
ax.set_xticks(x, [str(s) for s in KEYS])
ax.set_xlabel("study key")
ax.set_ylabel("FPR at p ≤ 0.01 (%)")
ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
ax.set_title("Per-key calibration on 1,000 pool A texts, before and after paraphrase", fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig3_calibration.png", dpi=200)
plt.close(fig)

# Fig 4: key leakage, E-est success at 5% against the attacker's recovered cosine
fig, ax = plt.subplots(figsize=(6.4, 4.2))
pts = kl["per_key_level"]
assert len(pts) == 32
LMK = {"0.25": "o", "0.35": "s", "0.5": "D", "0.7": "^"}
LSH = {"0.25": 0.35, "0.35": 0.55, "0.5": 0.75, "0.7": 1.0}
for i, lv in enumerate(LEVELS):
    sel = [pts[k * 4 + i] for k in range(8)]
    ax.scatter([q["cos"] for q in sel], [100 * q["success"] for q in sel], s=34, marker=LMK[lv], color=COL["est"],
               alpha=LSH[lv], edgecolor="white", linewidth=0.6, label=f"ρ = {float(lv):.2f}")
ax.axhline(BAR, color=INK, lw=1, ls="--")
ax.set_xlabel("attacker's recovered cosine cos(v̂, v) (Study 1, Route A, n = 1,024)")
ax.set_ylabel("E-est success at 5% (%)")
ax.legend(frameon=False, fontsize=7.5, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.16))
ax.set_title(f"Key leakage: edits guided by the attacker's estimate vs its accuracy\n(one point per key-level; "
             f"Spearman {kl['spearman_success_vs_cos']:.2f}; dashed line = 50%)", fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig4_leakage.png", dpi=200)
plt.close(fig)

# Fig 5: the owner's probe vs S4 on the same scrubbed texts (dumbbell), one panel per level
RW = [("unscrubbed", None)] + [(SHORT[m], f"para_{m}_gen") for m in MODELS] + [(f"{SHORT[a]} 5%", f"edit_{a}_{PRIMARY}") for a in ARMS]
fig, axs = plt.subplots(1, 4, figsize=(10.5, 3.4), sharey=True)
for ax, lv in zip(axs, LEVELS):
    L = res["levels"][lv]
    for i, (lab, nm) in enumerate(RW):
        if nm is None:
            p, e = 100 * R3["levels"][lv]["oracle"]["probe_acceptance_median"], L["P1"]["detected_before"]["median"]
        else:
            p = SEC["probe"][nm][lv]
            e = (L[f"S1_{nm.split('_')[1]}"] if nm.startswith("para") else L[f"E-{nm.split('_')[1]} {PRIMARY}"])["detected_after"]["median"]
        ax.plot([p, e], [i, i], color=GRID, lw=2.4, zorder=1)
        ax.scatter([p], [i], s=46, color="white", edgecolor=CTRL, linewidth=1.4, zorder=2, label="owner's probe" if i == 0 else None)
        ax.scatter([e], [i], s=46, color=INK, edgecolor="white", linewidth=1.0, zorder=3, label="S4 (exact test)" if i == 0 else None)
    ax.axvline(1, color=MUTED, lw=1, ls=":")
    ax.set_xlim(-4, 104)
    ax.set_title(f"ρ = {float(lv):.2f}", fontsize=9, color=INK)
    ax.set_xlabel("detected / accepted (%)")
axs[0].set_yticks(range(len(RW)), [r[0] for r in RW], fontsize=8)
axs[0].invert_yaxis()
h, lab = axs[0].get_legend_handles_labels()
fig.legend(h, lab, frameon=False, fontsize=8, loc="lower center", ncol=2, bbox_to_anchor=(0.55, 0.0))
fig.suptitle("Scrubbed texts still attributed to the key: the owner's probe (hollow) vs S4 (filled); median over keys; "
             "dotted line = 1%", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(OUT / "fig5_probe_vs_s4.png", dpi=200)
plt.close(fig)
print("wrote", sorted(p.name for p in OUT.iterdir()))

# ---------------------------------------------------------------- values quoted in the prose ([[name]] placeholders)
V = {}
for m in MODELS:
    C = res["calibration"][m]
    V[f"g1_{m}"] = f"{C['G1']['pooled_fpr_pct']:.2f}"
    V[f"ncal_{m}"] = str(C["G2"]["n_calibrated"])
    v = C["G2"]["per_key_fpr_pct"]
    V[f"g2min_{m}"], V[f"g2max_{m}"] = f"{min(v.values()):.1f}", f"{max(v.values()):.1f}"
    V[f"fresh3_{m}"] = f"{100 * C['fresh_keys']['share_above_3pct']:.1f}"
    V[f"freshmean_{m}"] = f"{C['fresh_keys']['mean_fpr_pct']:.2f}"
    V[f"probefpr_{m}"] = f"{C['probe_fpr_on_paraphrased_A2_pct']['median']:.1f}"
    for a in ("1", "2", "3"):
        V[f"att{a}_{m}"] = str(pa[m]["used"][a])
    V[f"keptfail_{m}"] = str(pa[m]["kept_failing_attacker_check"])
for lv, k in LV.items():
    L = res["levels"][lv]
    V[f"before_{k}"] = f"{L['P1']['detected_before']['median']:.1f}"
    V[f"miss0_{k}"] = f"{MISS0[lv]:.1f}"
    for m in MODELS:
        S1 = L[f"S1_{m}"]
        V.update({f"s1_{m}_{k}": f"{S1['success']['median']:.1f}", f"s1ci_{m}_{k}": cis(S1["success"]["ci95"]),
                  f"s1v_{m}_{k}": S1["verdict"], f"s1n_{m}_{k}": str(S1["keys_success_ge_50"]),
                  f"det_{m}_{k}": f"{S1['detected_after']['median']:.1f}", f"miss_{m}_{k}": f"{S1['originals_miss']['median']:.1f}",
                  f"all_{m}_{k}": f"{S1['pass']['all']:.1f}", f"cospass_{m}_{k}": f"{S1['pass']['cos']:.1f}",
                  f"pplpass_{m}_{k}": f"{S1['pass']['ppl']:.1f}", f"lenpass_{m}_{k}": f"{S1['pass']['len']:.1f}",
                  f"s1first_{m}_{k}": f"{S1['first_attempt']['success']['median']:.1f}",
                  f"lm_{m}_{k}": f"{SEC['length_matched'][m][lv]:.1f}", f"lmmed_{m}_{k}": f"{LMMED[(m, lv)]:.1f}",
                  f"probe_{m}_{k}": f"{SEC['probe'][f'para_{m}_gen'][lv]:.1f}",
                  f"strict_{m}_{k}": f"{S1['success_stricter']['A_model_p95']:.1f}",
                  f"strictmed_{m}_{k}": f"{S1['success_stricter']['A_human_median']:.1f}"})
    for a in ARMS:
        for f in BUDGETS:
            E = L[f"E-{a} {f}"]
            fk = f"{a}{int(round(100 * float(f)))}_{k}"
            V.update({f"e_{fk}": f"{E['success']['median']:.1f}", f"eci_{fk}": cis(E["success"]["ci95"]),
                      f"en_{fk}": str(E["success"]["keys_ge_50"]), f"edet_{fk}": f"{E['detected_after']['median']:.1f}",
                      f"eall_{fk}": f"{E['pass']['all']:.1f}", f"eppl_{fk}": f"{E['pass']['ppl']:.1f}"})
        V[f"eprobe_{a}_{k}"] = f"{SEC['probe'][f'edit_{a}_{PRIMARY}'][lv]:.1f}"
    for a in ("true", "est"):
        V[f"s2v_{a}_{k}"] = L[f"S2_{a}"]["verdict"]
    V[f"c1_{k}"] = f"{L['C1']['median']:+.1f}"
    V[f"c1ci_{k}"] = cis(L["C1"]["ci95"])
    V[f"c1v_{k}"] = L["C1"]["verdict"]
V["leak_spear"] = f"{kl['spearman_success_vs_cos']:.2f}"
for k, v in res["bars"]["A"].items():
    V[f"barA_{k}"] = f"{v:.3f}" if k != "ppl" else f"{v:.1f}"
# extra values for the in-words section (report_inwords.md)
V["s3_g1"] = f"{R3['G1']['pooled_fpr_pct']:.2f}"
V["s3_fpr_1002"] = f"{R3['G2']['per_key_fpr_pct']['1002']:.1f}"
for m in MODELS:
    C = res["calibration"][m]
    V[f"freshmax_{m}"] = f"{C['fresh_keys']['max_fpr_pct']:.1f}"
    V[f"keptfailpct_{m}"] = f"{100 * pa[m]['kept_failing_attacker_check'] / (8 * 4 * N_GEN[m]):.1f}"
    lm = [LMMED[(m, lv)] for lv in LEVELS]
    V[f"lmmed_min_{m}"], V[f"lmmed_max_{m}"] = f"{min(lm):.1f}", f"{max(lm):.1f}"
for a in ARMS:
    if "median_objective" in ed[a]:
        for k_, lab_ in (("0", "0"), (PRIMARY, "5"), ("0.1", "10")):
            V[f"obj_{a}_{lab_}"] = f"{ed[a]['median_objective'][k_]:.2f}"
NAMES = {"qwen": lambda L: L["S1_qwen"], "phi": lambda L: L["S1_phi"]}
for a in ARMS:
    for f, lab_ in (("0.02", "2"), (PRIMARY, "5"), ("0.1", "10")):
        NAMES[f"{a}{lab_}"] = (lambda L, a=a, f=f: L[f"E-{a} {f}"])
for lv, k in LV.items():
    L = res["levels"][lv]
    p1 = L["P1"]["detected_before"]["per_key"]
    for s in KEYS:
        V[f"p1_{s}_{k}"] = f"{p1[str(s)]:.0f}"
    V[f"p1minother1002_{k}"] = f"{min(v for s, v in p1.items() if s != '1002'):.0f}"
    for m in MODELS:
        S1 = L[f"S1_{m}"]
        ev = 100 - S1["detected_after"]["median"]
        V[f"evade_{m}_{k}"] = f"{ev:.1f}"
        V[f"passgiven_{m}_{k}"] = f"{100 * S1['success']['median'] / ev:.0f}" if ev > 0 else "—"
        V[f"pool4_{m}_{k}"] = f1(SEC["pooled_4"][f"para_{m}_gen"][lv])
        V[f"a001_{m}_{k}"] = f1(SEC["alpha_0.001"][f"para_{m}_gen"][lv])
    for a in ARMS:
        V[f"pool4_{a}5_{k}"] = f1(SEC["pooled_4"][f"edit_{a}_{PRIMARY}"][lv])
        V[f"a001_{a}5_{k}"] = f1(SEC["alpha_0.001"][f"edit_{a}_{PRIMARY}"][lv])
        for f, lab_ in (("0.02", "2"), (PRIMARY, "5"), ("0.1", "10")):
            V[f"epplratio_{a}{lab_}_{k}"] = f"{L[f'E-{a} {f}'].get('median_ppl_ratio', float('nan')):.2f}"
    for nm, get in NAMES.items():
        pk = get(L)["success"]["per_key"]
        for s in KEYS:
            V[f"pk_{nm}_{s}_{k}"] = f"{pk[str(s)]:.0f}" if str(s) in pk else "—"
        oth = [v for s, v in pk.items() if s != "1002"]
        V[f"pkmaxother1002_{nm}_{k}"] = f"{max(oth):.0f}" if oth else "—"
(OUT / "prose_values.json").write_text(json.dumps(V, indent=2, ensure_ascii=False))

# ---------------------------------------------------------------- assemble the report (only if the prose exists)
pf = Path(__file__).parent / "report_prose.md"
if not pf.exists():
    sys.exit("report_prose.md not written yet; assets only")
MANF = ROOT / "outputs" / "study2_v0.1" / "RUN_MANIFEST.json"
if MANF.exists():
    MAN = jl(MANF)
    for ph, d in MAN["phases"].items():
        V[f"{ph}_start_utc"], V[f"{ph}_end_utc"] = d["start_utc"][11:16], d["end_utc"][11:16]
        V[f"{ph}_start_ct"], V[f"{ph}_end_ct"] = d["start_ct"][11:16], d["end_ct"][11:16]
        V[f"{ph}_hours"] = f"{d['seconds'] / 3600:.1f}"
        V[f"{ph}_start_date"], V[f"{ph}_end_date"] = d["start_utc"][:10], d["end_utc"][:10]
    V["total_hours"] = f"{MAN['total_seconds'] / 3600:.1f}"
    V["report_date"] = MAN["phases"]["analyse"]["end_utc"][:10]
    V["ct"] = "/".join(sorted({d["ct_label"] for d in MAN["phases"].values()}))       # CDT (UTC-5) until 1 November
    V["deviations"] = "; ".join(MAN["deviations"])
elif TEST:
    for ph in ("para", "edits", "score", "analyse"):
        V.update({f"{ph}_{x}": "00:00" for x in ("start_utc", "end_utc", "start_ct", "end_ct")} | {f"{ph}_hours": "0.0"}
                 | {f"{ph}_start_date": "fixture", f"{ph}_end_date": "fixture"})
    V.update({"total_hours": "0.0", "report_date": "fixture", "deviations": "fixture", "ct": "CDT"})
prose = pf.read_text()
pi = Path(__file__).parent / "report_inwords.md"          # the in-words section, written after the results were read
if pi.exists():
    prose = prose.replace("<<IN_WORDS>>", pi.read_text().strip())
if TEST:
    prose = prose.replace("<<IN_WORDS>>", "(fixture: the in-words section is written after the results)")
for ph in ("<<TABLE1>>", "<<TABLES>>", "<<SAMPLES>>"):
    assert prose.count(ph) == 1, ph
missing = sorted(set(re.findall(r"\[\[(\w+)\]\]", prose)) - set(V))
assert not missing, f"unknown placeholders: {missing}"
prose = re.sub(r"\[\[(\w+)\]\]", lambda m: V[m.group(1)], prose)
t1, rest = tables.split("## Table 2", 1)
report = (prose.replace("<<TABLE1>>", t1.replace("## Table 1", "### Table 1").strip())
          .replace("<<TABLES>>", ("## Table 2" + rest).replace("## Table", "### Table").strip())
          .replace("<<SAMPLES>>", samples.strip()))
assert "[[" not in report and "<<" not in report
REPORT.write_text(report)
print("wrote", REPORT)
