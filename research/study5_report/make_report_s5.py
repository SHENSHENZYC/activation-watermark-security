"""Build the Study 5 v0.1 report tables, figures, samples and prose values from the locked outputs (numbers are never retyped).

Written during the run (phases S and K), before any Study 5 outcome was read (2026-10-02/03, Milestone 9), and tested on a
synthetic fixture (fixture_s5.py; `--fixture DIR`). Reads research/outputs/study5_v0.1/results.json and the per-text
statistics, quality and texts in research/study5/data/ (git-ignored), plus the locked inputs it shares with the run
(Study 1's texts and prompts, Study 2's paraphrases, quality and bars, Study 3's features). Before writing anything it
re-computes, with its own implementation (not common_s5 / keyed_core / common_s3 / scrub_core):
  - S4 and the union test on Study 3's locked features (the fixed arm's and rotation's detection, FA and controls) and on
    Study 2's paraphrase features (the fixed key's scrub success, the D2 comparator; cross-checked against Study 2's report);
  - from the run's per-text keyed statistics (the per-position test's gradients are not stored): every p-value, fluency
    flag, acceptance, scrub success, quality condition and perplexity ratio, per key;
  - G1, G2, P0, P1 and every D1, D2 and D3 verdict from the summaries, with the protocol's §9 rules written out again here;
and asserts that all of these equal results.json. Builder-side descriptive readings (protocol §10): detection at p <= 0.05
and 0.10, four texts pooled, stricter quality bars, the tokenisation round trip, paraphrase attempts, timing.
Writes research/outputs/study5_v0.1/report/: tables.md, samples.md, prose_values.json, fig1-fig5 (.png). Then assembles
research/STUDY5_REPORT_v0.1.md from report_prose.md (<<TABLE1>>, <<IN_WORDS>>, <<TABLES>>, <<SAMPLES>>, [[name]]) if it exists.
Run: .venv/bin/python research/study5_report/make_report_s5.py [--fixture DIR]
"""
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]                     # research/
sys.path.insert(0, str(ROOT / "study1"))
import core  # noqa: E402  (keys only: make_key and the null-key seeds; the tokenizer id)

RES = ROOT / "outputs" / "study5_v0.1" / "results.json"
D5 = ROOT / "study5" / "data"
OUT = ROOT / "outputs" / "study5_v0.1" / "report"
REPORT = ROOT / "STUDY5_REPORT_v0.1.md"
MANF = ROOT / "outputs" / "study5_v0.1" / "RUN_MANIFEST.json"
TEST = len(sys.argv) > 2 and sys.argv[1] == "--fixture"       # builder test on a synthetic fixture (no outcomes)
REAL = not TEST   # on the fixture the run's statistics are planted noise, so the re-computation from the locked features is
                  # exercised but compared with the run only on the real data; the fixture then uses the run's statistics
if TEST:
    FX = Path(sys.argv[2])
    RES, D5, OUT, REPORT, MANF = FX / "out" / "results.json", FX / "data", FX / "report", FX / "STUDY5_REPORT_fixture.md", FX / "RUN_MANIFEST.json"
V02, S3D, S2D = ROOT / "study1_v02" / "data", ROOT / "study3" / "data", ROOT / "study2" / "data"
R2 = json.loads((ROOT / "outputs" / "study2_v0.1" / "results.json").read_text())
R3 = json.loads((ROOT / "outputs" / "study3_v0.1" / "results.json").read_text())["S4"]
KEYS = list(range(1001, 1009))
LEVELS = ["0.35", "0.5"]
TAG = {"0.35": "035", "0.5": "050"}
LV = {"0.35": "35", "0.5": "50"}
ARMS = ["h1", "h4"]
HH = {"h1": 1, "h4": 4}
NG = [64, 256, 1024]
ALPHA, D, NEW_TOKENS, M = 0.01, 1536, 256, 999
G1_RANGE, G2_MAX, MIN_CAL, P1_MIN, D2_POINTS, D3_RATIO = (0.3, 2.5), 3.0, 6, 50.0, 20.0, 1.10
NAME = {"fixed": "fixed key (h = 0)", "h1": "context-hashed, h = 1", "h4": "context-hashed, h = 4", "rot": "rotation (K = 8)"}
SHORT = {"fixed": "fixed", "h1": "h = 1", "h4": "h = 4", "rot": "rotation", "naive": "rotation, naive attacker", "cluster": "rotation, clustering attacker"}
# palette: the fixed key in ink; categorical slots 1, 2, 7 for the three defences (validated, light); controls in recessive gray
INK, MUTED, GRID, CTRL = "#1f1f1e", "#6b6a64", "#e4e3dc", "#52514e"
COL = {"fixed": INK, "h1": "#2a78d6", "h4": "#eb6834", "rot": "#4a3aa7", "ctrl": CTRL}
MK = {"fixed": "o", "h1": "s", "h4": "^", "rot": "D"}

res = json.loads(RES.read_text())
if not TEST:
    assert "dry" not in str(RES) and "dry" not in str(D5), "the dry smoke test's files are not the study"
bars = json.loads((S2D / "bars.json").read_text())
CAL = {a: [int(s) for s in res["arms"][a]["calibration"]["G2"]["calibrated_keys"]] for a in ARMS}


def jl(p):
    return json.loads(Path(p).read_text())


def tg(s, lv):
    return f"k{s}_r{TAG[lv]}"


def ld(name):
    """(S_true, S_null, npos) of a run file."""
    z = np.load(D5 / f"{name}.npz")
    return z["S_true"].astype(np.float64), z["S_null"].astype(np.float64), z["npos"]


def pv_of(name):
    St, Sn, _ = ld(name)
    return (1 + (Sn >= St[:, None]).sum(1)) / (1 + Sn.shape[1])


def pooled_pv(name, n=4):
    St, Sn, _ = ld(name)
    nb = len(St) // n
    T, Tn = St[:nb * n].reshape(nb, n).sum(1), Sn[:nb * n].reshape(nb, n, -1).sum(1)
    return (1 + (Tn >= T[:, None]).sum(1)) / (1 + Tn.shape[1])


def cut95(x):
    return float(np.quantile(np.asarray(x, dtype=np.float64), 0.95))


def fl(ppl, rep, cp, cr):
    return (np.asarray(ppl, dtype=np.float64) <= cp) & (np.asarray(rep, dtype=np.float64) <= cr)


def conds(o, z, b):
    """Protocol §7 / Study 2 §5, re-written: the four quality conditions of a paraphrase z of its original o."""
    olen = np.minimum(np.asarray(o["len"], dtype=np.float64), NEW_TOKENS)
    c = {"ppl": z["ppl"] <= np.maximum(1.25 * np.asarray(o["ppl"], dtype=np.float64), b["ppl"]),
         "rep": z["rep"] <= np.maximum(np.asarray(o["rep"], dtype=np.float64), b["rep"]),
         "len": z["len"] >= 0.8 * olen, "cos": z["cos"] > b["cos"]}
    c["all"] = c["ppl"] & c["rep"] & c["len"] & c["cos"]
    return c


def close(a, b, what, tol=1e-9):
    assert abs(float(a) - float(b)) < tol, (what, a, b)


def close_list(a, b, what):
    assert len(a) == len(b), (what, len(a), len(b))
    for x, y in zip(a, b):
        close(x, y, what)


# ---------------------------------------------------------------- independent S4 and union test (Study 3's and §5's definitions, re-written)
def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def key_unit(seed):
    return unit(core.make_key(seed, D, 1.0).numpy().astype(np.float64))


NULL = np.stack([key_unit(core.NULL_KEY_SEED * 100000 + j) for j in range(M)])
NULLBIG = np.stack([key_unit(core.NULL_KEY_SEED * 100000 + j) for j in range(M * len(KEYS) + 1 + M * 2)])  # >= 999 groups of 8
GROUPS = NULLBIG[:M * len(KEYS)].reshape(M, len(KEYS), D)
KU = {s: key_unit(s) for s in KEYS}
KUM = np.stack([KU[s] for s in KEYS])
Gf = np.load(S3D / "S_F_van.npz")["G"].astype(np.float32)
MU, SD = Gf.mean(0), np.maximum(Gf.std(0, ddof=1), 1e-12)


def s4_X(G):
    return unit(((np.asarray(G, dtype=np.float32) - MU) / SD).astype(np.float64))


def pvals(G, s):
    X = s4_X(G)
    return (1 + ((X @ NULL.T) >= (X @ KU[s])[:, None]).sum(1)) / (1 + M)


def pvals_union(G):
    X = s4_X(G)
    U = (X @ KUM.T).max(1)
    Un = np.stack([(X @ GROUPS[j].T).max(1) for j in range(M)], 1)
    return (1 + (Un >= U[:, None]).sum(1)) / (1 + M)


OQ = {tg(s, lv): {k: np.asarray(v, dtype=np.float64) for k, v in bars["orig"][tg(s, lv)].items()} for s in KEYS for lv in LEVELS}
P2 = jl(S2D / "para_qwen_gen.json")
Q2 = {k: np.asarray(v, dtype=np.float64) for k, v in jl(S2D / "Q_para_qwen_gen.json").items()}
G2 = np.load(S2D / "G_para_qwen_gen.npy", mmap_mode="r")


def s2_rows(s, lv):
    """Study 2's kept P-Qwen paraphrases of (s, lv): indices in pool D order, their features, raw quality and texts."""
    idx = [i for i, l in enumerate(P2["labels"]) if l[0] == s and abs(l[1] - float(lv)) < 1e-9]
    texts = [P2["attempts"][P2["kept"][i]][i]["text"] for i in idx]
    return idx, np.asarray(G2[idx], dtype=np.float32), {k: Q2[k][idx] for k in ("ppl", "rep", "len", "cos")}, texts


# ---------------------------------------------------------------- rules (protocol §9), re-written
def rule_d1(forge, gen_median, ctrl):
    bar = 0.5 * gen_median
    if ctrl["median"] >= bar:
        return "generic steering suffices"
    for n in sorted(forge, key=int):
        if forge[n]["median"] >= bar and forge[n]["ci95"][0] > ctrl["ci95"][1]:
            return f"practical (n={n})"
    if all(forge[n]["ci95"][1] < bar for n in forge):
        return "stealing blocked at n <= 1024"
    return "inconclusive"


def rule_d2(dmed, ci):
    if ci[0] > 0 and dmed >= D2_POINTS:
        return "material robustness cost"
    return "immaterial" if ci[1] < D2_POINTS else "inconclusive"


def rule_d3(ci):
    if ci[0] > D3_RATIO:
        return "material quality cost"
    return "immaterial" if ci[1] <= D3_RATIO else "inconclusive"


def rule_abs(success):
    if success["median"] >= 0.5:
        return "paraphrase effective (>= 50%)"
    return "not effective" if success["ci95"][1] < 0.5 else "inconclusive"


# ---------------------------------------------------------------- integrity: re-compute and assert
PK = {}          # (arm, lv, s) -> per-key dict of builder values (fractions), also used by the tables
FIXED = {}       # (lv, s) -> builder values for the fixed arm
ROT = {}         # (lv, s)
FXS2 = {}        # (lv, s) -> the fixed key's Study 2 scrub success per text (own S4 + own conditions)
SEC = {"alpha": {}, "pooled": {}, "strict": {}, "para_pooled": {}, "det_after_fixed": {}}
for a in ARMS:
    C = res["arms"][a]["calibration"]
    fp = {s: 100 * float((pv_of(f"S_null_{a}_k{s}") <= ALPHA).mean()) for s in KEYS}
    for s in KEYS:
        close(fp[s], C["G2"]["per_key_fpr_pct"][str(s)], f"G2 {a} {s}")
    close(np.mean(list(fp.values())), C["G1"]["pooled_fpr_pct"], f"G1 {a}")
    assert C["G1"]["pass"] == (G1_RANGE[0] <= C["G1"]["pooled_fpr_pct"] <= G1_RANGE[1]), a
    assert sorted(CAL[a]) == sorted(s for s in KEYS if fp[s] <= G2_MAX), a
    assert C["G2"]["stop"] == (len(CAL[a]) < MIN_CAL), a
pu_run = pv_of("S_null_union")
close(100 * float((pu_run <= ALPHA).mean()), res["rotation"]["G1"]["pooled_fpr_pct"], "union G1 (run stats)")
pu_own = pvals_union(np.load(S3D / "S_A_van.npz")["G"])
if REAL:
    close(100 * float((pu_own <= ALPHA).mean()), res["rotation"]["G1"]["pooled_fpr_pct"], "union G1 (own union test on pool A)")
assert res["rotation"]["G1"]["pass"] == (G1_RANGE[0] <= res["rotation"]["G1"]["pooled_fpr_pct"] <= G1_RANGE[1])

for lv in LEVELS:
    F = res["fixed"][lv]
    for s in KEYS:
        t = tg(s, lv)
        Go = np.load(S3D / f"K_{t}_oracle.npz")["G"]
        p_own, p_run = pvals(Go, s), pv_of(f"F_{t}_oracle")
        assert len(p_own) == len(p_run) == 100, (t, len(p_own), len(p_run))
        if REAL:
            close_list(p_own, p_run, f"fixed oracle p-values {t}")
        p_own = p_own if REAL else p_run
        o = OQ[t]
        cp, cr = cut95(o["ppl"]), cut95(o["rep"])
        acc = p_own <= ALPHA
        pr_own, pr_run = pvals(np.load(S3D / f"K_{t}_random.npz")["G"], s), pv_of(f"F_{t}_random")
        if REAL:
            close_list(pr_own, pr_run, f"fixed random p-values {t}")
        pr_own = pr_own if REAL else pr_run
        rq = jl(D5 / f"F_{t}_random_quality.json")
        est = jl(D5 / f"F_{t}_est.json")
        fa_f = {n: (pv_of(f"F_{t}_forge_n{n}") <= ALPHA) & fl(*(jl(D5 / f"F_{t}_forge_n{n}_quality.json")[k] for k in ("ppl", "rep")), cp, cr) for n in NG}
        fa_s = (pv_of(f"F_{t}_forge_search_n256") <= ALPHA) & fl(*(jl(D5 / f"F_{t}_forge_search_n256_quality.json")[k] for k in ("ppl", "rep")), cp, cr)
        d = {"detect": acc.mean(), "oracle_FA": (acc & fl(o["ppl"], o["rep"], cp, cr)).mean(), "random_FA": ((pr_own <= ALPHA) & fl(rq["ppl"], rq["rep"], cp, cr)).mean(),
             "forge_FA": {n: fa_f[n].mean() for n in NG}, "forge_search_FA": fa_s.mean(), "cut_ppl": cp, "cut_rep": cr,
             "cos_known": {n: est[str(n)]["known"]["cos"] for n in NG}, "cos_search": {n: est[str(n)]["search"]["cos"] for n in NG},
             "layer_search": {n: est[str(n)]["search"]["layer"] for n in NG},
             "det_alpha": {al: (p_own <= al).mean() for al in (0.05, 0.10)}, "pooled4": (pooled_pv(f"F_{t}_oracle") <= ALPHA).mean(), "p_oracle": p_own}
        pk = F["per_key"][str(s)]
        close(d["detect"], pk["detect"], f"fixed detect {t}")
        close(d["oracle_FA"], pk["oracle_FA"], f"fixed oracle FA {t}")
        for n in NG:
            close(d["forge_FA"][n], pk["forge_FA"][str(n)], f"fixed forge FA {t} {n}")
            close(d["cos_known"][n], pk["cos_known"][str(n)], f"cos known {t}")
            close(d["cos_search"][n], pk["cos_search"][str(n)], f"cos search {t}")
        # the fixed key's Study 2 scrub success (the D2 comparator): own S4 on Study 2's paraphrase features, own conditions
        idx, Gp, q, _ = s2_rows(s, lv)
        pp = pvals(Gp, s)
        c = conds(o, q, bars["A"])
        FXS2[(lv, s)] = ((pp > ALPHA) & c["all"]).astype(float)
        d["s2_success"], d["s2_detected_after"], d["s2_quality_pass"] = FXS2[(lv, s)].mean(), (pp <= ALPHA).mean(), c["all"].mean()
        d["s2_strict"] = {b: ((pp > ALPHA) & conds(o, q, bars[b])["all"]).mean() for b in ("A_model_p95", "A_human_median")}
        close(100 * d["s2_success"], R2["levels"][lv]["S1_qwen"]["success"]["per_key"][str(s)], f"Study 2's S1 success {t}")
        close(100 * d["s2_detected_after"], R2["levels"][lv]["S1_qwen"]["detected_after"]["per_key"][str(s)], f"Study 2's detection after {t}")
        FIXED[(lv, s)] = d
    close_list([FIXED[(lv, s)]["oracle_FA"] for s in KEYS], F["oracle_FA"]["per_key"], f"fixed oracle FA list {lv}")
    close_list([FIXED[(lv, s)]["random_FA"] for s in KEYS], F["random_FA"]["per_key"], f"fixed random FA list {lv}")
    close_list([FIXED[(lv, s)]["forge_search_FA"] for s in KEYS], F["forge_search_FA"]["per_key"], f"fixed search FA list {lv}")
    close_list([FIXED[(lv, s)]["s2_success"] for s in KEYS], F["s2_success"]["per_key"], f"fixed s2 success list {lv}")
    for n in NG:
        close_list([FIXED[(lv, s)]["forge_FA"][n] for s in KEYS], F["forge_FA"][str(n)]["per_key"], f"fixed forge FA list {lv} {n}")
        close(np.median([FIXED[(lv, s)]["cos_known"][n] for s in KEYS]), F["recovery"][str(n)]["median_cos_known"], f"median cos known {lv} {n}")
        close(np.median([FIXED[(lv, s)]["cos_search"][n] for s in KEYS]), F["recovery"][str(n)]["median_cos_search"], f"median cos search {lv} {n}")
        assert F["recovery"][str(n)]["layer_hits_search"] == sum(FIXED[(lv, s)]["layer_search"][n] == 14 for s in KEYS), (lv, n)
    for blk in (F["oracle_FA"], F["random_FA"], F["forge_search_FA"], F["s2_success"], *F["forge_FA"].values()):
        close(np.median(blk["per_key"]), blk["median"], f"median {lv}")
    assert F["P0"]["verdict"] == rule_d1(F["forge_FA"], F["oracle_FA"]["median"], F["random_FA"]), lv
    assert F["P0"]["pass"] == F["P0"]["verdict"].startswith("practical"), lv
    close(F["P0"]["bar"], 0.5 * F["oracle_FA"]["median"], f"P0 bar {lv}")

    # ---- the keyed arms
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        cal = CAL[a]
        for s in cal:
            t = f"{a}_{tg(s, lv)}"
            gq = jl(D5 / f"K_{t}_genuine_quality.json")
            cp, cr = cut95(gq["ppl"]), cut95(gq["rep"])
            pg = pv_of(f"K_{t}_genuine")
            acc = pg <= ALPHA
            cq = jl(D5 / f"K_{t}_control_quality.json")
            ak = jl(D5 / f"K_{t}_attacker.json")
            pq = jl(D5 / f"P_{t}_quality.json")
            raw = {k: np.asarray(v, dtype=np.float64) for k, v in pq["raw"].items()}
            own_c = conds({k: np.asarray(gq[k])[:len(raw["ppl"])] for k in ("ppl", "rep", "len")}, raw, bars["A"])
            assert own_c["all"].tolist() == [bool(x) for x in pq["all"]], f"quality conditions {t}"
            for k in ("ppl", "rep", "len", "cos"):
                assert own_c[k].tolist() == [bool(x) for x in pq[k]], f"quality condition {k} {t}"
            pp = pv_of(f"P_{t}")
            assert len(pp) == len(own_c["all"]), t
            sc = (pp > ALPHA) & own_c["all"]
            fx = FXS2[(lv, s)][:len(sc)]
            o = OQ[tg(s, lv)]
            ratio = np.asarray(gq["ppl"], dtype=np.float64) / o["ppl"][:len(gq["ppl"])]
            d = {"detect": acc.mean(), "genuine_FA": (acc & fl(gq["ppl"], gq["rep"], cp, cr)).mean(),
                 "control_FA": ((pv_of(f"K_{t}_control") <= ALPHA) & fl(cq["ppl"], cq["rep"], cp, cr)).mean(),
                 "forge_FA": {n: ((pv_of(f"K_{t}_forge_n{n}") <= ALPHA) & fl(*(jl(D5 / f"K_{t}_forge_n{n}_quality.json")[k] for k in ("ppl", "rep")), cp, cr)).mean()
                              for n in NG if n <= res["scope"]["N_OBS"][a]},
                 "attacker": {n: ak[str(n)] for n in NG if str(n) in ak}, "n_distinct_contexts": ak["n_distinct_contexts"], "n_eligible_contexts": ak["n_eligible_contexts"],
                 "para_success": sc.mean(), "para_detected": (pp <= ALPHA).mean(), "para_quality_pass": own_c["all"].mean(),
                 "para_cond_pass": {k: own_c[k].mean() for k in ("ppl", "rep", "len", "cos")},
                 "d_points": 100 * (sc.mean() - fx.mean()), "fixed_s2_success": fx.mean(),
                 "ppl_ratio_median": float(np.median(ratio)), "rep_keyed": float(np.median(gq["rep"])), "rep_fixed": float(np.median(o["rep"])),
                 "cut_ppl": cp, "cut_rep": cr, "ppl_median_keyed": float(np.median(gq["ppl"])), "ppl_median_fixed": float(np.median(o["ppl"][:len(gq["ppl"])])),
                 "det_alpha": {al: (pg <= al).mean() for al in (0.05, 0.10)}, "pooled4": (pooled_pv(f"K_{t}_genuine") <= ALPHA).mean(),
                 "para_pooled4_detected": (pooled_pv(f"P_{t}") <= ALPHA).mean(),
                 "para_strict": {b: ((pp > ALPHA) & conds({k: np.asarray(gq[k])[:len(pp)] for k in ("ppl", "rep", "len")}, raw, bars[b])["all"]).mean()
                                 for b in ("A_model_p95", "A_human_median")},
                 "para_raw_medians": {k: float(np.median(raw[k])) for k in raw}}
            pk = L["per_key"][str(s)]
            for k in ("detect", "genuine_FA", "control_FA", "para_success", "fixed_s2_success", "ppl_ratio_median"):
                close(d[k], pk[k], f"{a} {t} {k}")
            for n in d["forge_FA"]:
                close(d["forge_FA"][n], pk["forge_FA"][str(n)], f"{a} {t} forge FA {n}")
            for n in d["attacker"]:
                for k in ("cos_weighted", "coverage_genuine", "n_contexts"):
                    close(d["attacker"][n][k], pk["attacker"][str(n)][k], f"{a} {t} attacker {n} {k}")
            PK[(a, lv, s)] = d
        rows = [PK[(a, lv, s)] for s in cal]
        for key, blk in (("detect", L["detection"]), ("genuine_FA", L["genuine_FA"]), ("control_FA", L["control_FA"]), ("para_success", L["para_success"]),
                         ("para_detected", L["para_detected"]), ("para_quality_pass", L["para_quality_pass"])):
            close_list([r[key] for r in rows], blk["per_key"], f"{a} {lv} {key} list")
            close(np.median(blk["per_key"]), blk["median"], f"{a} {lv} {key} median")
        for n in L["forge_FA"]:
            close_list([r["forge_FA"][int(n)] for r in rows], L["forge_FA"][n]["per_key"], f"{a} {lv} forge FA list {n}")
        for n in L["recovery"]:
            for k, kk in (("cos_weighted", "cos_weighted"), ("coverage", "coverage_genuine"), ("n_contexts", "n_contexts")):
                close(np.median([r["attacker"][int(n)][kk] for r in rows]), L["recovery"][n][k], f"{a} {lv} recovery {n} {k}")
        close(L["P1"]["median_pct"], 100 * L["detection"]["median"], f"P1 {a} {lv}")
        assert L["P1"]["pass"] == (L["P1"]["median_pct"] >= P1_MIN), (a, lv)
        assert L["D1"]["verdict"] == rule_d1(L["forge_FA"], L["genuine_FA"]["median"], L["control_FA"]), (a, lv)
        close(L["D1"]["bar"], 0.5 * L["genuine_FA"]["median"], f"D1 bar {a} {lv}")
        close(np.median([r["d_points"] for r in rows]), L["D2"]["median_diff_points"], f"D2 median {a} {lv}")
        assert L["D2"]["n_keys_ge_20_points"] == sum(r["d_points"] >= D2_POINTS for r in rows), (a, lv)
        assert L["D2"]["verdict"] == rule_d2(L["D2"]["median_diff_points"], L["D2"]["ci95"]), (a, lv)
        assert L["D2"]["absolute"] == rule_abs(L["para_success"]), (a, lv)
        close(np.median([r["ppl_ratio_median"] for r in rows]), L["D3"]["median_ratio"], f"D3 median {a} {lv}")
        assert L["D3"]["n_keys_above_1.10"] == sum(r["ppl_ratio_median"] > D3_RATIO for r in rows), (a, lv)
        assert L["D3"]["verdict"] == rule_d3(L["D3"]["ci95"]), (a, lv)
        close(np.median([r["rep_keyed"] for r in rows]), L["D3"]["rep_median_keyed"], f"rep keyed {a} {lv}")
        close(np.median([r["rep_fixed"] for r in rows]), L["D3"]["rep_median_fixed"], f"rep fixed {a} {lv}")
        assert L["gates"] == {"P0": F["P0"]["pass"], "P1": L["P1"]["pass"], "descriptive_only": not (F["P0"]["pass"] and L["P1"]["pass"])}, (a, lv)

    # ---- rotation
    R = res["rotation"][lv]
    allo_p = np.concatenate([OQ[tg(s, lv)]["ppl"] for s in KEYS])
    allo_r = np.concatenate([OQ[tg(s, lv)]["rep"] for s in KEYS])
    cpp, crp = cut95(allo_p), cut95(allo_r)
    for s in KEYS:
        t = tg(s, lv)
        pu_own, pu_run = pvals_union(np.load(S3D / f"K_{t}_oracle.npz")["G"]), pv_of(f"R_{t}_oracle_union")
        if REAL:
            close_list(pu_own, pu_run, f"union p-values {t}")
        pu_own = pu_own if REAL else pu_run
        idx, Gp, q, _ = s2_rows(s, lv)
        pup_own, pup_run = pvals_union(Gp), pv_of(f"R_{t}_para_union")
        if REAL:
            close_list(pup_own, pup_run, f"union paraphrase p-values {t}")
        pup_own = pup_own if REAL else pup_run
        c = conds(OQ[t], q, bars["A"])
        d = {"union_detect": (pu_own <= ALPHA).mean(), "single_detect": FIXED[(lv, s)]["detect"], "union_success": ((pup_own > ALPHA) & c["all"]).mean(),
             "union_detected_after": (pup_own <= ALPHA).mean(), "union_d_points": 100 * (((pup_own > ALPHA) & c["all"]).mean() - FXS2[(lv, s)].mean())}
        pk = R["per_key"][str(s)]
        for k in ("union_detect", "single_detect", "union_success"):
            close(d[k], pk[k], f"rotation {t} {k}")
        ROT[(lv, s)] = d
    for key, blk in (("union_detect", R["union_detection"]), ("single_detect", R["single_detection"])):
        close_list([ROT[(lv, s)][key] for s in KEYS], blk["per_key"], f"rotation {lv} {key} list")
        close(np.median(blk["per_key"]), blk["median"], f"rotation {lv} {key} median")
    close(R["P1"]["median_pct"], 100 * R["union_detection"]["median"], f"rotation P1 {lv}")
    assert R["P1"]["pass"] == (R["P1"]["median_pct"] >= P1_MIN), lv
    rt = f"r{TAG[lv]}"
    for who in ("naive", "cluster"):
        for n in NG:
            fa = (pv_of(f"R_{rt}_forge_{who}_n{n}_union") <= ALPHA) & fl(*(jl(D5 / f"R_{rt}_forge_{who}_n{n}_quality.json")[k] for k in ("ppl", "rep")), cpp, crp)
            close(fa.mean(), R["forge_FA"][who][str(n)]["mean"], f"rotation forge FA {lv} {who} {n}")
        assert R["D1"][who]["verdict"] == rule_d1({n: {"median": v["mean"], "ci95": v["ci95"]} for n, v in R["forge_FA"][who].items()},
                                                   F["oracle_FA"]["median"], F["random_FA"]), (lv, who)
    close(np.median([ROT[(lv, s)]["union_d_points"] for s in KEYS]), R["D2"]["median_diff_points"], f"rotation D2 {lv}")
    assert R["D2"]["verdict"] == rule_d2(R["D2"]["median_diff_points"], R["D2"]["ci95"]), lv
    ro = jl(D5 / f"R_{rt}_attack.json")
    assert ro["naive"] == R["naive"] and ro["cluster"] == R["cluster"], lv
OUT.mkdir(parents=True, exist_ok=True)
print("ok: integrity asserts passed (S4, the union test, the quality conditions, every per-key value and every rule re-computed"
      + ("; fixture: the run's planted statistics stand in for the locked features)" if TEST else ")"))

# ---------------------------------------------------------------- builder-side descriptive readings (protocol §10)
def rt_share():
    """Tokenisation round trip: the share of continuation positions whose token id is recovered by re-tokenising the
    decoded text (median over keys of the per-key mean), per arm at rho = 0.50."""
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(core.MODEL_ID, revision=core.REVISION)
    except Exception as e:  # noqa: BLE001
        return {a: None for a in ARMS}, f"tokenizer not loaded ({type(e).__name__})"
    out = {}
    for a in ARMS:
        per = []
        for s in CAL[a]:
            g = jl(D5 / f"K_{a}_{tg(s, '0.5')}_genuine.json")
            sh = []
            for text, ids in zip(g["texts"][:20], g["ids"][:20]):
                re_ids = tok(text, add_special_tokens=False)["input_ids"]
                n = min(len(ids), len(re_ids))
                sh.append(sum(int(x == y) for x, y in zip(ids[:n], re_ids[:n])) / len(ids))
            per.append(float(np.mean(sh)))
        out[a] = float(np.median(per))
    return out, "first 20 genuine texts per key"


RT, RT_NOTE = rt_share()
ATT = {}
for a in ARMS:
    P = jl(D5 / f"P_{a}_all.json")
    kept = P["kept"]
    used = {k: int(sum(1 for x in kept if x == k - 1)) for k in (1, 2, 3)}
    fail = int(sum(1 for i, k in enumerate(kept) if P["attempts"][k][i]["n_fail_attacker"] > 0))
    ATT[a] = {"used": used, "kept_failing": fail, "n": len(kept), "paraphrase_s": P["paraphrase_s"]}
TIM = {}
for a in ARMS:
    gs = {"genuine": [], "control": [], "obs": []}
    for lv in LEVELS:
        for s in KEYS:
            dn = D5 / f"K_{a}_{tg(s, lv)}_done.json"
            if dn.exists():
                for k, v in jl(dn)["gen_s"].items():
                    if v is not None:
                        gs[k].append(v)
    TIM[a] = {k: (float(np.sum(v)) if v else None) for k, v in gs.items()}

# ---------------------------------------------------------------- tables
def pc(x):
    return f"{100 * x:.1f}"


def ci(c, scale=100):
    return f"[{scale * c[0]:.1f}, {scale * c[1]:.1f}]"


def mc(s, scale=100):
    return f"{scale * s['median']:.1f} {ci(s['ci95'], scale)}"


def cif(c, fmt):
    return "[" + format(c[0], fmt) + ", " + format(c[1], fmt) + "]"


def med(vals):
    return float(np.median(vals))


T = ["## Table 1 — Pre-registered rules vs observed (protocol §9)\n"]
g = []
for a in ARMS:
    C = res["arms"][a]["calibration"]
    g.append(f"**{NAME[a]}:** G1 pooled FPR over 8 secrets × 1,000 pool A texts {C['G1']['pooled_fpr_pct']:.2f}% (pass if {G1_RANGE[0]}–{G1_RANGE[1]}%) → "
             f"**{'PASS' if C['G1']['pass'] else 'FAIL'}**; G2 {C['G2']['n_calibrated']} of 8 keys calibrated (FPR ≤ {G2_MAX}%)"
             + (f", excluded {', '.join(str(s) for s in KEYS if s not in CAL[a])}" if len(CAL[a]) < 8 else "") + f" → verdicts **{'not made' if C['G2']['stop'] else 'made'}**.")
GU = res["rotation"]["G1"]
g.append(f"**Union test (rotation):** G1 pooled FPR {GU['pooled_fpr_pct']:.2f}% → **{'PASS' if GU['pass'] else 'FAIL'}**.")
for lv in LEVELS:
    F = res["fixed"][lv]
    g.append(f"**P0, the threat at ρ = {float(lv):.2f}:** the fixed key under Route A′ is **{F['P0']['verdict']}** (forgery FA at n = 64 / 256 / 1,024: "
             + " / ".join(mc(F["forge_FA"][str(n)]) for n in NG) + f"%, bar {pc(F['P0']['bar'])}% = half the genuine FA {pc(F['oracle_FA']['median'])}%, "
             f"random-key control {mc(F['random_FA'])}%) → defence verdicts at this strength are **{'made' if F['P0']['pass'] else 'descriptive'}**.")
T.append("\n".join("- " + x for x in g) + "\n")
T.append("| arm | ρ | P1: genuine detection, median [95% CI] (≥ 50%) | D1 stealing: forgery FA at n = 64 / 256 / 1,024 [95% CI]; bar; control → verdict | "
         "D2 robustness cost: scrub success [95% CI] vs the fixed key's; d = median difference [95% CI]; keys ≥ 20 pts → verdict (absolute reading) | "
         "D3 quality cost: perplexity ratio arm/fixed, median [95% CI]; keys > 1.10 → verdict |")
T.append("|---|---|---|---|---|---|")
for a in ARMS:
    for lv in LEVELS:
        L = res["arms"][a]["levels"][lv]
        F = res["fixed"][lv]
        desc = " (descriptive: " + ", ".join(x for x, ok in (("P0 fails", not L["gates"]["P0"]), ("P1 fails", not L["gates"]["P1"])) if ok) + ")" if L["gates"]["descriptive_only"] else ""
        T.append(f"| {NAME[a]} | {float(lv):.2f} | {mc(L['detection'])}% ({'pass' if L['P1']['pass'] else 'fail'}) | "
                 + " / ".join(mc(L["forge_FA"][str(n)]) for n in NG if str(n) in L["forge_FA"]) + f"%; bar {pc(L['D1']['bar'])}% (genuine FA {pc(L['genuine_FA']['median'])}%); "
                 f"control {mc(L['control_FA'])}% → **{L['D1']['verdict']}**{desc} | {mc(L['para_success'])}% vs {mc(F['s2_success'])}%; d = {L['D2']['median_diff_points']:+.1f} "
                 f"{ci(L['D2']['ci95'], 1)}; {L['D2']['n_keys_ge_20_points']} of {len(CAL[a])} → **{L['D2']['verdict']}** ({L['D2']['absolute']}) | "
                 f"{L['D3']['median_ratio']:.3f} {cif(L['D3']['ci95'], '.3f')}; {L['D3']['n_keys_above_1.10']} of {len(CAL[a])} → **{L['D3']['verdict']}** |")
for lv in LEVELS:
    R, F = res["rotation"][lv], res["fixed"][lv]
    d1 = "; ".join(f"{who}: " + " / ".join(f"{100 * R['forge_FA'][who][str(n)]['mean']:.1f} {ci(R['forge_FA'][who][str(n)]['ci95'])}" for n in NG) + f"% → **{R['D1'][who]['verdict']}**"
                   for who in ("naive", "cluster"))
    T.append(f"| {NAME['rot']} | {float(lv):.2f} | union test {mc(R['union_detection'])}% ({'pass' if R['P1']['pass'] else 'fail'}; told which key: {mc(R['single_detection'])}%) | "
             f"{d1}; bar {pc(R['D1']['naive']['bar'])}% (the fixed oracle FA {pc(F['oracle_FA']['median'])}%); control {mc(F['random_FA'])}%"
             + (" (descriptive: P0 fails)" if not F["P0"]["pass"] else "") + f" | union-test success on Study 2's paraphrases {med([100 * ROT[(lv, s)]['union_success'] for s in KEYS]):.1f}% vs "
             f"{mc(F['s2_success'])}%; d = {R['D2']['median_diff_points']:+.1f} {ci(R['D2']['ci95'], 1)} → **{R['D2']['verdict']}** | unchanged by construction (not tested) |")
T.append("\nFA = accepted at p ≤ 0.01 **and** fluent (perplexity and seq-rep-4 at most the arm's own genuine texts' 95th percentiles at that key-level; "
         "rotation: the level's pooled oracle percentiles). Scrub success = not detected at p ≤ 0.01 **and** Study 2's four quality conditions "
         "(fluency, repetition, length, meaning; the owner's bars). Medians over calibrated keys with 95% cluster-bootstrap intervals (keys, then texts); "
         "D2's interval is paired (the same keys and prompts). The fixed key's scrub success is Study 2's P-Qwen result on the same prompts and keys, "
         "re-computed here from Study 2's locked paraphrases.\n")

T.append("## Table 2 — Detection, quality and power per arm (median over calibrated keys; ρ by row)\n")
T.append("| arm | ρ | genuine detection % [95% CI] | at p ≤ 0.05 / 0.10 | 4 texts pooled | genuine FA % | control FA % | perplexity: median keyed / median fixed; ratio | "
         "seq-rep-4 keyed / fixed | tokenisation round trip (ρ = 0.50) |")
T.append("|---|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    F = res["fixed"][lv]
    rows = [FIXED[(lv, s)] for s in KEYS]
    T.append(f"| {NAME['fixed']} (S4, Study 3's features) | {float(lv):.2f} | {pc(med([r['detect'] for r in rows]))} | "
             f"{pc(med([r['det_alpha'][0.05] for r in rows]))} / {pc(med([r['det_alpha'][0.10] for r in rows]))} | {pc(med([r['pooled4'] for r in rows]))} | "
             f"{mc(F['oracle_FA'])} | {mc(F['random_FA'])} | {med([np.median(OQ[tg(s, lv)]['ppl']) for s in KEYS]):.2f} (reference; ratio 1) | "
             f"{med([np.median(OQ[tg(s, lv)]['rep']) for s in KEYS]):.4f} (reference) | — |")
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        rows = [PK[(a, lv, s)] for s in CAL[a]]
        T.append(f"| {NAME[a]} | {float(lv):.2f} | {mc(L['detection'])} | {pc(med([r['det_alpha'][0.05] for r in rows]))} / {pc(med([r['det_alpha'][0.10] for r in rows]))} | "
                 f"{pc(med([r['pooled4'] for r in rows]))} | {mc(L['genuine_FA'])} | {mc(L['control_FA'])} | {med([r['ppl_median_keyed'] for r in rows]):.2f} / "
                 f"{med([r['ppl_median_fixed'] for r in rows]):.2f}; {L['D3']['median_ratio']:.3f} {cif(L['D3']['ci95'], '.3f')} | {L['D3']['rep_median_keyed']:.4f} / {L['D3']['rep_median_fixed']:.4f} | "
                 + (f"{RT[a]:.3f}" if RT[a] is not None else "—") + " |")
    R = res["rotation"][lv]
    T.append(f"| {NAME['rot']} (union test) | {float(lv):.2f} | {mc(R['union_detection'])} (told which key: {mc(R['single_detection'])}) | — | — | — | — | unchanged | unchanged | — |")
T.append(f"\nThe keyed arms' texts are new generations on Study 1's oracle prompts (pool D, 100 per key-level); the fixed key's are Study 1's oracle texts on the "
         f"same prompts, so the perplexity ratio is paired by prompt and key. Round trip: {RT_NOTE}. Pooled: four consecutive genuine texts' statistics summed "
         "before the null comparison (25 tests per key-level).\n")

T.append("## Table 3 — Key recovery and forgery acceptance against the attacker's budget n (median over keys)\n")
T.append("| arm | ρ | n | recovery | forgery FA % [95% CI] |")
T.append("|---|---|---|---|---|")
for lv in LEVELS:
    F = res["fixed"][lv]
    for n in NG:
        rc = F["recovery"][str(n)]
        T.append(f"| {NAME['fixed']}, Route A′ | {float(lv):.2f} | {n} | cos(v̂, v) known layer {rc['median_cos_known']:.2f}; layer search {rc['median_cos_search']:.2f} "
                 f"(layer 14 found for {rc['layer_hits_search']} of 8 keys) | {mc(F['forge_FA'][str(n)])}" + (f"; layer-search forgery {mc(F['forge_search_FA'])}" if n == F["forge_search_FA"]["n"] else "") + " |")
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        for n in NG:
            if str(n) not in L["recovery"]:
                continue
            rc = L["recovery"][str(n)]
            T.append(f"| {NAME[a]}, per-context attacker (layer given) | {float(lv):.2f} | {n} | count-weighted cos {rc['cos_weighted']:.3f}; coverage of genuine positions "
                     f"{rc['coverage']:.3f}; contexts estimated {rc['n_contexts']:.0f} | {mc(L['forge_FA'][str(n)]) if str(n) in L['forge_FA'] else '—'} |")
    R = res["rotation"][lv]
    for n in NG:
        nv = R["naive"][str(n)]
        cl = R["cluster"][str(n)]["clusters"]
        T.append(f"| {NAME['rot']}, naive Route A′ on the mixture | {float(lv):.2f} | {n} | best cos with any key {max(nv.values()):.2f} (key {max(nv, key=nv.get)}) | "
                 f"{100 * R['forge_FA']['naive'][str(n)]['mean']:.1f} {ci(R['forge_FA']['naive'][str(n)]['ci95'])} |")
        ch = cl[str(R['cluster'][str(n)]['chosen_cluster'])]
        T.append(f"| {NAME['rot']}, clustering attacker | {float(lv):.2f} | {n} | keys recovered at cos ≥ 0.5: {R['cluster'][str(n)]['keys_recovered_ge_0.5']} of 8; "
                 f"median best cos over clusters {med([c['best_cos'] for c in cl.values()]):.2f}; the forging cluster (largest z-profile): cos {ch['best_cos']:.2f} with key {ch['best_key']}, "
                 f"{ch['size']} texts | {100 * R['forge_FA']['cluster'][str(n)]['mean']:.1f} {ci(R['forge_FA']['cluster'][str(n)]['ci95'])} |")
T.append("\nRecovery for the fixed key: the cosine between the attacker's 4-sparse estimate and the true key (Study 1's Route A rule on the exact test's gradient "
         "statistic). For the hashed arms: the mean cosine over estimated contexts with the true per-context keys, weighted by context count; coverage = the "
         "share of a genuine text's scored positions whose context has an estimate. Rotation's forgeries use the cluster with the largest z-profile.\n")

T.append("## Table 4 — Paraphrase (P-Qwen with the attacker's self-check) per arm beside the fixed key (median over calibrated keys, %)\n")
T.append("| arm | ρ | scrub success [95% CI] | detected after | 4 paraphrases pooled: detected | quality: all four pass | fluency / repetition / length / meaning pass | "
         "success, model-text bar | success, human-median bar | d vs the fixed key [95% CI]; keys ≥ 20 pts | verdict |")
T.append("|---|---|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    F = res["fixed"][lv]
    rows = [FIXED[(lv, s)] for s in KEYS]
    T.append(f"| {NAME['fixed']} (Study 2) | {float(lv):.2f} | {mc(F['s2_success'])} | {pc(med([r['s2_detected_after'] for r in rows]))} | "
             f"{R2['secondary']['pooled_4']['para_qwen_gen'][lv]:.1f} (Study 2) | {pc(med([r['s2_quality_pass'] for r in rows]))} | — | "
             f"{pc(med([r['s2_strict']['A_model_p95'] for r in rows]))} | {pc(med([r['s2_strict']['A_human_median'] for r in rows]))} | — | {R2['levels'][lv]['S1_qwen']['verdict']} (Study 2's S1) |")
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        rows = [PK[(a, lv, s)] for s in CAL[a]]
        T.append(f"| {NAME[a]} | {float(lv):.2f} | {mc(L['para_success'])} | {mc(L['para_detected'])} | {pc(med([r['para_pooled4_detected'] for r in rows]))} | "
                 f"{mc(L['para_quality_pass'])} | " + " / ".join(pc(med([r["para_cond_pass"][k] for r in rows])) for k in ("ppl", "rep", "len", "cos")) +
                 f" | {pc(med([r['para_strict']['A_model_p95'] for r in rows]))} | {pc(med([r['para_strict']['A_human_median'] for r in rows]))} | "
                 f"{L['D2']['median_diff_points']:+.1f} {ci(L['D2']['ci95'], 1)}; {L['D2']['n_keys_ge_20_points']} of {len(CAL[a])} | **{L['D2']['verdict']}** ({L['D2']['absolute']}) |")
    R = res["rotation"][lv]
    T.append(f"| {NAME['rot']} (union test on Study 2's paraphrases) | {float(lv):.2f} | {med([100 * ROT[(lv, s)]['union_success'] for s in KEYS]):.1f} | "
             f"{med([100 * ROT[(lv, s)]['union_detected_after'] for s in KEYS]):.1f} | — | as the fixed key | — | — | — | {R['D2']['median_diff_points']:+.1f} {ci(R['D2']['ci95'], 1)} | **{R['D2']['verdict']}** |")
b = bars
T.append(f"\nThe owner's bars (pool A's human continuations, 95th percentile): perplexity {b['A']['ppl']:.2f}, seq-rep-4 {b['A']['rep']:.4f}; meaning (cosine) {b['A']['cos']:.3f}; "
         f"the attacker's self-check uses pool C's ({b['C']['ppl']:.2f}, {b['C']['rep']:.4f}, {b['C']['cos']:.3f}). Stricter readings (descriptive): the model-text 95th "
         f"percentile (perplexity {b['A_model_p95']['ppl']:.2f}) and the human median ({b['A_human_median']['ppl']:.2f}). Paraphrase attempts kept: "
         + "; ".join(f"{SHORT[a]}: attempt 1 {ATT[a]['used'][1]}, 2 {ATT[a]['used'][2]}, 3 {ATT[a]['used'][3]} of {ATT[a]['n']}; kept but still failing the attacker's check {ATT[a]['kept_failing']}"
                     for a in ARMS) + ".\n")

T.append("## Table 5 — Per key: the per-unit view behind every median (keys excluded by G2 shown as —)\n")
T.append("| arm | ρ | reading | " + " | ".join(str(s) for s in KEYS) + " | median |")
T.append("|---|---|---|" + "---|" * (len(KEYS) + 1))
for a in ARMS:
    v = res["arms"][a]["calibration"]["G2"]["per_key_fpr_pct"]
    T.append(f"| {NAME[a]} | — | FPR on pool A, % (G2 ≤ 3) | " + " | ".join(f"{v[str(s)]:.1f}" for s in KEYS) + f" | {med([v[str(s)] for s in KEYS]):.1f} |")
v3 = R3["G2"]["per_key_fpr_pct"]
T.append(f"| {NAME['fixed']} (S4, Study 3) | — | FPR on pool A, % | " + " | ".join(f"{v3[str(s)]:.1f}" for s in KEYS) + f" | {med([v3[str(s)] for s in KEYS]):.1f} |")


def row(label, lv, name, vals, fmt):
    T.append(f"| {label} | {float(lv):.2f} | {name} | " + " | ".join(fmt(x) if x is not None else "—" for x in vals) + f" | {fmt(med([x for x in vals if x is not None]))} |")


p0 = lambda x: f"{100 * x:.0f}"  # noqa: E731
for lv in LEVELS:
    for s_ in ("detect", "oracle_FA"):
        row(NAME["fixed"], lv, {"detect": "S4 detection %", "oracle_FA": "genuine FA %"}[s_], [FIXED[(lv, s)][s_] for s in KEYS], p0)
    for n in NG:
        row(NAME["fixed"], lv, f"cos known layer, n = {n}", [FIXED[(lv, s)]["cos_known"][n] for s in KEYS], lambda x: f"{x:.2f}")
        row(NAME["fixed"], lv, f"forgery FA %, n = {n}", [FIXED[(lv, s)]["forge_FA"][n] for s in KEYS], p0)
    row(NAME["fixed"], lv, "Study 2 scrub success %", [FIXED[(lv, s)]["s2_success"] for s in KEYS], p0)
    for a in ARMS:
        get = lambda s, f: f(PK[(a, lv, s)]) if (a, lv, s) in PK else None  # noqa: E731
        row(NAME[a], lv, "detection %", [get(s, lambda r: r["detect"]) for s in KEYS], p0)
        row(NAME[a], lv, "genuine FA %", [get(s, lambda r: r["genuine_FA"]) for s in KEYS], p0)
        row(NAME[a], lv, "control FA %", [get(s, lambda r: r["control_FA"]) for s in KEYS], p0)
        for n in NG:
            if any((a, lv, s) in PK and n in PK[(a, lv, s)]["forge_FA"] for s in KEYS):
                row(NAME[a], lv, f"forgery FA %, n = {n}", [get(s, lambda r, n=n: r["forge_FA"].get(n)) for s in KEYS], p0)
        row(NAME[a], lv, "attacker cos (weighted), n = 1,024", [get(s, lambda r: r["attacker"][1024]["cos_weighted"] if 1024 in r["attacker"] else None) for s in KEYS], lambda x: f"{x:.3f}")
        row(NAME[a], lv, "coverage, n = 1,024", [get(s, lambda r: r["attacker"][1024]["coverage_genuine"] if 1024 in r["attacker"] else None) for s in KEYS], lambda x: f"{x:.3f}")
        row(NAME[a], lv, "scrub success %", [get(s, lambda r: r["para_success"]) for s in KEYS], p0)
        row(NAME[a], lv, "d vs fixed, points", [get(s, lambda r: r["d_points"] / 100) for s in KEYS], lambda x: f"{100 * x:+.0f}")
        row(NAME[a], lv, "perplexity ratio (median)", [get(s, lambda r: r["ppl_ratio_median"]) for s in KEYS], lambda x: f"{x:.2f}")
    row(NAME["rot"], lv, "union-test detection %", [ROT[(lv, s)]["union_detect"] for s in KEYS], p0)
    row(NAME["rot"], lv, "union-test scrub success %", [ROT[(lv, s)]["union_success"] for s in KEYS], p0)
T.append("")

T.append("## Table 6 — The per-context attacker's mechanics and the run's timing (descriptive)\n")
T.append("| arm | ρ | distinct contexts in the observed set | eligible (≥ 16 occurrences) | n | contexts estimated | coverage | cos by context count: 16–31 / 32–127 / 128–511 / ≥ 512 |")
T.append("|---|---|---|---|---|---|---|---|")
for a in ARMS:
    for lv in LEVELS:
        rows = [PK[(a, lv, s)] for s in CAL[a]]
        for n in NG:
            if not all(n in r["attacker"] for r in rows):
                continue
            cb = {k: [r["attacker"][n].get("cos_by_count", {}).get(k) for r in rows] for k in ("16", "32", "128", "512")}
            cbs = " / ".join((f"{med([x for x in v if x is not None]):.3f}" if any(x is not None for x in v) else "—") for v in cb.values())
            T.append(f"| {NAME[a]} | {float(lv):.2f} | {med([r['n_distinct_contexts'] for r in rows]):.0f} | {med([r['n_eligible_contexts'] for r in rows]):.0f} | {n} | "
                     f"{med([r['attacker'][n]['n_contexts'] for r in rows]):.0f} | {med([r['attacker'][n]['coverage_genuine'] for r in rows]):.3f} | {cbs} |")
T.append("")
tim = []
for a in ARMS:
    n_kl = sum(1 for lv in LEVELS for s in KEYS if (D5 / f"K_{a}_{tg(s, lv)}_done.json").exists())
    parts = [f"{k} {v / 3600:.2f} h" for k, v in TIM[a].items() if v is not None]
    tim.append(f"{SHORT[a]}: generation over {n_kl} key-levels: " + ", ".join(parts) + f"; paraphrase {ATT[a]['paraphrase_s'] / 3600:.2f} h for {ATT[a]['n']} originals "
               f"({ATT[a]['paraphrase_s'] / max(ATT[a]['n'], 1):.2f} s each)")
T.append("Timing (from the run's per-step records): " + "; ".join(tim) + ". Phase durations are in the run manifest.\n")
tables = "\n".join(T) + "\n"
(OUT / "tables.md").write_text(tables)


# ---------------------------------------------------------------- samples (protocol §10: keys 1001 and 1002 at rho = 0.50, read and quoted)
def bq(text):
    return text.strip().replace("\n", "\n> ")


SM = ["Keys 1001 and 1002 at ρ = 0.50, as the protocol fixes (§10): for each arm the first genuine text (pool D's first prompt), the forgery of that "
      "prompt at n = 1,024, and the paraphrase of the genuine text. Each is quoted in full as scored, with its p-value and quality readings.\n"]
lv = "0.5"
for s in (1001, 1002):
    t = tg(s, lv)
    SM.append(f"### Key {s}, ρ = 0.50\n")
    o = OQ[t]
    po = FIXED[(lv, s)]["p_oracle"][0]
    SM.append(f"**Fixed key — genuine (Study 1's oracle text)** — S4 p = {po:.3f} ({'detected' if po <= ALPHA else 'not detected'}); perplexity {o['ppl'][0]:.1f}, "
              f"seq-rep-4 {o['rep'][0]:.3f}:\n\n> {bq(jl(V02 / f'K_{t}_oracle.json')[0])}\n")
    pf_ = pv_of(f"F_{t}_forge_n1024")[0]
    fq = jl(D5 / f"F_{t}_forge_n1024_quality.json")
    fd = FIXED[(lv, s)]
    SM.append(f"**Fixed key — Route A′ forgery at n = 1,024 (known layer; cos {fd['cos_known'][1024]:.2f})** — S4 p = {pf_:.3f} ({'accepted' if pf_ <= ALPHA else 'rejected'}); "
              f"perplexity {fq['ppl'][0]:.1f} (bar {fd['cut_ppl']:.1f}), seq-rep-4 {fq['rep'][0]:.3f} (bar {fd['cut_rep']:.3f}) → "
              f"**{'accepted and fluent' if (pf_ <= ALPHA and fq['ppl'][0] <= fd['cut_ppl'] and fq['rep'][0] <= fd['cut_rep']) else 'no'}**:\n\n> {bq(jl(D5 / f'F_{t}_forge_n1024.json')[0])}\n")
    idx, Gp, q, texts = s2_rows(s, lv)
    pp0 = pvals(Gp[:1], s)[0]
    c0 = {k: bool(v[0]) for k, v in conds(o, q, bars["A"]).items()}
    SM.append(f"**Fixed key — Study 2's P-Qwen paraphrase** — S4 p = {pp0:.3f} ({'detected' if pp0 <= ALPHA else 'not detected'}); perplexity {q['ppl'][0]:.1f}, "
              f"seq-rep-4 {q['rep'][0]:.3f}, {int(q['len'][0])} tokens, cosine {q['cos'][0]:.3f}; conditions "
              + ", ".join(f"{k} {'pass' if c0[k] else 'FAIL'}" for k in ("ppl", "rep", "len", "cos")) + f" → **{'success' if FXS2[(lv, s)][0] else 'no success'}**:\n\n> {bq(texts[0])}\n")
    for a in ARMS:
        if s not in CAL[a]:
            SM.append(f"**{NAME[a]}:** key {s} is excluded by G2.\n")
            continue
        ta = f"{a}_{t}"
        g = jl(D5 / f"K_{ta}_genuine.json")
        gq = jl(D5 / f"K_{ta}_genuine_quality.json")
        pg = pv_of(f"K_{ta}_genuine")[0]
        SM.append(f"**{NAME[a]} — genuine** — keyed test p = {pg:.3f} ({'detected' if pg <= ALPHA else 'not detected'}); perplexity {gq['ppl'][0]:.1f} "
                  f"(fixed key's text on the same prompt {o['ppl'][0]:.1f}), seq-rep-4 {gq['rep'][0]:.3f}:\n\n> {bq(g['texts'][0])}\n")
        if 1024 in PK[(a, lv, s)]["forge_FA"]:
            f_ = jl(D5 / f"K_{ta}_forge_n1024.json")
            fq = jl(D5 / f"K_{ta}_forge_n1024_quality.json")
            pf_ = pv_of(f"K_{ta}_forge_n1024")[0]
            d = PK[(a, lv, s)]
            SM.append(f"**{NAME[a]} — per-context forgery at n = 1,024** ({f_['steered_positions'][0]} of 256 positions steered; the attacker's weighted cos "
                      f"{d['attacker'][1024]['cos_weighted']:.3f}) — p = {pf_:.3f} ({'accepted' if pf_ <= ALPHA else 'rejected'}); perplexity {fq['ppl'][0]:.1f} (bar {d['cut_ppl']:.1f}), "
                      f"seq-rep-4 {fq['rep'][0]:.3f} (bar {d['cut_rep']:.3f}) → **{'accepted and fluent' if (pf_ <= ALPHA and fq['ppl'][0] <= d['cut_ppl'] and fq['rep'][0] <= d['cut_rep']) else 'no'}**:\n\n> {bq(f_['texts'][0])}\n")
        P = jl(D5 / f"P_{a}_all.json")
        i = next(i for i, it in enumerate(P["items"]) if it[0] == s and abs(it[1] - 0.5) < 1e-9 and it[2] == 0)
        pq = jl(D5 / f"P_{ta}_quality.json")
        ppp = pv_of(f"P_{ta}")[0]
        SM.append(f"**{NAME[a]} — P-Qwen paraphrase (attempt {P['kept'][i] + 1} kept)** — p = {ppp:.3f} ({'detected' if ppp <= ALPHA else 'not detected'}); perplexity "
                  f"{pq['raw']['ppl'][0]:.1f}, seq-rep-4 {pq['raw']['rep'][0]:.3f}, {int(pq['raw']['len'][0])} tokens, cosine {pq['raw']['cos'][0]:.3f}; conditions "
                  + ", ".join(f"{k} {'pass' if pq[k][0] else 'FAIL'}" for k in ("ppl", "rep", "len", "cos"))
                  + f" → **{'success' if (ppp > ALPHA and pq['all'][0]) else 'no success'}**:\n\n> {bq(P['texts'][i])}\n")
    if s == 1001:
        rt = f"r{TAG[lv]}"
        rf = jl(D5 / f"R_{rt}_forge_cluster_n1024.json")
        rq = jl(D5 / f"R_{rt}_forge_cluster_n1024_quality.json")
        pr_ = pv_of(f"R_{rt}_forge_cluster_n1024_union")[0]
        SM.append(f"**Rotation — the clustering attacker's forgery at n = 1,024 (one corpus per strength)** — union-test p = {pr_:.3f} "
                  f"({'accepted' if pr_ <= ALPHA else 'rejected'}); perplexity {rq['ppl'][0]:.1f}, seq-rep-4 {rq['rep'][0]:.3f}:\n\n> {bq(rf[0])}\n")
samples = "\n".join(SM) + "\n"
(OUT / "samples.md").write_text(samples)

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6})
X = np.log2(np.array(NG, dtype=float))


def line(ax, ys, col, lab, mk, ls="-", hollow=False, ci_=None, x=X):
    if ci_ is not None:
        ax.fill_between(x, [c[0] for c in ci_], [c[1] for c in ci_], color=col, alpha=0.12, linewidth=0)
    ax.plot(x, ys, ls, color=col, lw=2 if not hollow else 1.4, marker=mk, ms=7, mfc="white" if hollow else col, mec=col, label=lab)


def nx(ax):
    ax.set_xticks(X, [f"{n:,}" for n in NG])
    ax.set_xlim(X[0] - 0.4, X[-1] + 0.4)
    ax.set_xlabel("observed watermarked texts n")


# Fig 1: recovery (top) and forgery acceptance (bottom) against n, one column per strength
fig, axs = plt.subplots(2, 2, figsize=(9.8, 8.2))
for j, lv in enumerate(LEVELS):
    F, R = res["fixed"][lv], res["rotation"][lv]
    ax = axs[0, j]
    line(ax, [F["recovery"][str(n)]["median_cos_known"] for n in NG], COL["fixed"], "fixed key, Route A′ (known layer)", MK["fixed"])
    line(ax, [F["recovery"][str(n)]["median_cos_search"] for n in NG], COL["fixed"], "fixed key, Route A′ (layer search)", MK["fixed"], ls="--", hollow=True)
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        ns = [n for n in NG if str(n) in L["recovery"]]
        line(ax, [L["recovery"][str(n)]["cos_weighted"] for n in ns], COL[a], f"{NAME[a]}: count-weighted cos", MK[a], x=np.log2(np.array(ns, dtype=float)))
    line(ax, [med([c["best_cos"] for c in R["cluster"][str(n)]["clusters"].values()]) for n in NG], COL["rot"], "rotation: clustering attacker (median cluster)", MK["rot"])
    line(ax, [max(R["naive"][str(n)].values()) for n in NG], COL["rot"], "rotation: naive attacker (best key)", MK["rot"], ls="--", hollow=True)
    ax.set_ylim(-0.03, 1.03)
    ax.set_title(f"ρ = {float(lv):.2f}", fontsize=9, color=INK, loc="left")
    nx(ax)
    ax = axs[1, j]
    line(ax, [100 * F["forge_FA"][str(n)]["median"] for n in NG], COL["fixed"], "fixed key", MK["fixed"], ci_=[[100 * c for c in F["forge_FA"][str(n)]["ci95"]] for n in NG])
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        ns = [n for n in NG if str(n) in L["forge_FA"]]
        line(ax, [100 * L["forge_FA"][str(n)]["median"] for n in ns], COL[a], NAME[a], MK[a], ci_=[[100 * c for c in L["forge_FA"][str(n)]["ci95"]] for n in ns],
             x=np.log2(np.array(ns, dtype=float)))
    for who, ls, hol in (("cluster", "-", False), ("naive", "--", True)):
        line(ax, [100 * R["forge_FA"][who][str(n)]["mean"] for n in NG], COL["rot"], SHORT[who], MK["rot"], ls=ls, hollow=hol,
             ci_=[[100 * c for c in R["forge_FA"][who][str(n)]["ci95"]] for n in NG])
    bars_ = [100 * F["P0"]["bar"]] + [100 * res["arms"][a]["levels"][lv]["D1"]["bar"] for a in ARMS]
    ax.axhspan(min(bars_), max(bars_), color=GRID, alpha=0.8, zorder=0, label=f"D1 bar: half of each arm's genuine FA ({min(bars_):.0f}–{max(bars_):.0f}%)")
    ctrl = [100 * F["random_FA"]["median"]] + [100 * res["arms"][a]["levels"][lv]["control_FA"]["median"] for a in ARMS]
    ax.axhline(max(ctrl), color=CTRL, lw=1, ls=":", label=f"random-key / random-secret controls (max over arms {max(ctrl):.0f}%)")
    ax.set_ylim(-3, 104)
    nx(ax)
axs[0, 0].set_ylabel("key recovery: cosine with the true key")
axs[1, 0].set_ylabel("forgery acceptance FA (%)\naccepted at p ≤ 0.01 and fluent")
for i in range(2):
    h, lab = axs[i, 0].get_legend_handles_labels()
    axs[i, 1].legend(h, lab, frameon=False, fontsize=7, loc="upper left", bbox_to_anchor=(1.02, 1.0))
fig.suptitle("Study 5: key recovery and forgery acceptance against the attacker's budget (median over calibrated keys; bands = 95% CI)",
             fontsize=9.5, color=INK, x=0.01, ha="left")
fig.tight_layout()
fig.savefig(OUT / "fig1_recovery_forgery.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Fig 2: scrub success (top) and detection after paraphrase (bottom) per arm beside the fixed key
fig, axs = plt.subplots(2, 2, figsize=(9.2, 7.2), sharex=True)
ORDER = ["fixed", "h1", "h4", "rot"]
for j, lv in enumerate(LEVELS):
    F, R = res["fixed"][lv], res["rotation"][lv]
    succ = {"fixed": F["s2_success"], "rot": {"median": med([ROT[(lv, s)]["union_success"] for s in KEYS]), "ci95": None}}
    det = {"fixed": {"median": med([FIXED[(lv, s)]["s2_detected_after"] for s in KEYS]), "ci95": None},
           "rot": {"median": med([ROT[(lv, s)]["union_detected_after"] for s in KEYS]), "ci95": None}}
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        succ[a], det[a] = L["para_success"], L["para_detected"]
    for i, (blk, ylab) in enumerate(((succ, "scrub success (%)\nnot detected and all four quality conditions pass"), (det, "detected after paraphrase (%)"))):
        ax = axs[i, j]
        for k, arm in enumerate(ORDER):
            v = blk[arm]
            ax.bar(k, 100 * v["median"], width=0.62, color=COL[arm], edgecolor="white", linewidth=1.2, zorder=2)
            if v["ci95"] is not None:
                ax.errorbar(k, 100 * v["median"], yerr=[[100 * (v["median"] - v["ci95"][0])], [100 * (v["ci95"][1] - v["median"])]], fmt="none", ecolor=INK, elinewidth=1.2, capsize=3, zorder=3)
            ax.text(k, 100 * v["median"] + (6 if v["ci95"] is None else 100 * (v["ci95"][1] - v["median"]) + 2), f"{100 * v['median']:.0f}", ha="center", va="bottom", fontsize=8, color=INK)
        if i == 0:
            ax.axhline(50, color=INK, lw=1, ls="--", label="50%: paraphrase effective (Study 2's absolute reading)")
            for k, a in enumerate(ARMS, start=1):
                L = res["arms"][a]["levels"][lv]
                ax.text(k, -9, f"d = {L['D2']['median_diff_points']:+.0f} {cif(L['D2']['ci95'], '+.0f')}", ha="center", va="top", fontsize=6.5, color=COL[a])
            ax.text(3, -9, f"d = {R['D2']['median_diff_points']:+.0f} {cif(R['D2']['ci95'], '+.0f')}", ha="center", va="top", fontsize=6.5, color=COL["rot"])
            ax.set_ylim(-22, 108)
        else:
            ax.set_ylim(0, 108)
        ax.set_xticks(range(4), [SHORT[a] for a in ORDER])
        ax.set_ylabel(ylab if j == 0 else "")
        if i == 0:
            ax.set_title(f"ρ = {float(lv):.2f}", fontsize=9, color=INK, loc="left")
h2, l2 = axs[0, 0].get_legend_handles_labels()
fig.legend(h2, l2, frameon=False, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, -0.01))
fig.suptitle("Study 5: P-Qwen paraphrase per arm beside the fixed key (median over calibrated keys; whiskers = 95% CI; d = median difference "
             "from the fixed key, points)", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "fig2_paraphrase.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Fig 3: the stealability-robustness-quality frontier (three one-axis panels, rows = arms, markers = strength)
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.9), sharey=True)
ROWS = [("fixed", "fixed key"), ("h1", NAME["h1"]), ("h4", NAME["h4"]), ("naive", SHORT["naive"]), ("cluster", SHORT["cluster"])]
LMK = {"0.35": "o", "0.5": "s"}
for i, (arm, lab) in enumerate(ROWS):
    for lv in LEVELS:
        F, R = res["fixed"][lv], res["rotation"][lv]
        off = -0.15 if lv == "0.35" else 0.15
        col = COL["rot"] if arm in ("naive", "cluster") else COL[arm]
        if arm == "fixed":
            st, rb, qu = F["forge_FA"]["1024"], F["s2_success"], None
        elif arm in ARMS:
            L = res["arms"][arm]["levels"][lv]
            st, rb, qu = L["forge_FA"].get("1024"), L["para_success"], L["D3"]
        else:
            v = R["forge_FA"][arm]["1024"]
            st = {"median": v["mean"], "ci95": v["ci95"]}
            rb = {"median": med([ROT[(lv, s)]["union_success"] for s in KEYS]), "ci95": None}
            qu = None
        for ax, blk, scale in ((axs[0], st, 100), (axs[1], rb, 100)):
            if blk is None:
                continue
            if blk["ci95"] is not None:
                ax.plot([scale * blk["ci95"][0], scale * blk["ci95"][1]], [i + off, i + off], color=col, lw=1.2, alpha=0.6)
            ax.scatter([scale * blk["median"]], [i + off], s=44, marker=LMK[lv], color=col, edgecolor="white", linewidth=0.8, zorder=3)
        if qu is not None:
            axs[2].plot(qu["ci95"], [i + off, i + off], color=col, lw=1.2, alpha=0.6)
            axs[2].scatter([qu["median_ratio"]], [i + off], s=44, marker=LMK[lv], color=col, edgecolor="white", linewidth=0.8, zorder=3)
        elif arm == "fixed":
            axs[2].scatter([1.0], [i + off], s=44, marker=LMK[lv], color=col, edgecolor="white", linewidth=0.8, zorder=3)
        else:
            axs[2].scatter([1.0], [i + off], s=44, marker=LMK[lv], facecolor="white", edgecolor=col, linewidth=1.2, zorder=3)
axs[0].set_yticks(range(len(ROWS)), [r[1] for r in ROWS], fontsize=8)
axs[0].invert_yaxis()
axs[0].set_xlabel("forgery FA at n = 1,024 (%)")
axs[1].set_xlabel("scrub success after P-Qwen (%)")
axs[2].set_xlabel("perplexity ratio to the fixed key")
axs[2].axvline(1.0, color=MUTED, lw=1, ls=":")
axs[2].axvline(D3_RATIO, color=INK, lw=1, ls="--")
axs[2].text(D3_RATIO, -0.45, "D3 bar 1.10", color=INK, fontsize=7, ha="left", va="top")
axs[1].axvline(50, color=INK, lw=1, ls="--")
for ax in axs[:2]:
    ax.set_xlim(-4, 104)
axs[2].set_xlim(0.5, 1.6)
from matplotlib.lines import Line2D  # noqa: E402
hs = [Line2D([], [], marker=LMK[lv], color=MUTED, ls="", ms=7, label=f"ρ = {float(lv):.2f}") for lv in LEVELS] + \
     [Line2D([], [], marker="s", color=MUTED, mfc="white", ls="", ms=7, label="rotation: unchanged by construction (hollow)")]
fig.legend(handles=hs, frameon=False, fontsize=7.5, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Study 5: the frontier per arm: stealability (left), robustness lost (middle), quality (right); median over calibrated keys; "
             "lines = 95% CI; dashed = materiality bars", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(OUT / "fig3_frontier.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Fig 4: per key: calibration (left) and forgery FA at n = 1,024 against genuine detection (right), by arm
fig, axs = plt.subplots(1, 2, figsize=(10.2, 3.9))
ax = axs[0]
xk = np.arange(len(KEYS))
ax.scatter(xk - 0.2, [v3[str(s)] for s in KEYS], s=40, marker=MK["fixed"], color="white", edgecolor=INK, linewidth=1.3, zorder=3, label="fixed key, S4 (Study 3)")
for a, off in (("h1", 0.0), ("h4", 0.2)):
    v = res["arms"][a]["calibration"]["G2"]["per_key_fpr_pct"]
    ax.scatter(xk + off, [v[str(s)] for s in KEYS], s=40, marker=MK[a], color=COL[a], edgecolor="white", linewidth=0.8, zorder=3, label=f"{NAME[a]}, keyed test")
ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.axhline(G2_MAX, color=INK, lw=1, ls="--")
ax.text(len(KEYS) - 0.5, G2_MAX, "G2 bar 3%", color=INK, fontsize=7.5, va="bottom", ha="right")
ax.text(len(KEYS) - 0.5, 1, "nominal 1%", color=MUTED, fontsize=7.5, va="bottom", ha="right")
ax.set_xticks(xk, [str(s) for s in KEYS])
ax.set_xlabel("study key")
ax.set_ylabel("FPR at p ≤ 0.01 on 1,000 pool A texts (%)")
ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
ax.set_title("Per-key calibration", fontsize=9, color=INK, loc="left")
ax = axs[1]
for lv in LEVELS:
    for arm in ("fixed", "h1", "h4"):
        if arm == "fixed":
            pts = [(100 * FIXED[(lv, s)]["detect"], 100 * FIXED[(lv, s)]["forge_FA"][1024]) for s in KEYS]
        else:
            pts = [(100 * PK[(arm, lv, s)]["detect"], 100 * PK[(arm, lv, s)]["forge_FA"][1024]) for s in CAL[arm] if 1024 in PK[(arm, lv, s)]["forge_FA"]]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=36, marker=MK[arm], color=COL[arm], alpha=0.55 if lv == "0.35" else 1.0, edgecolor="white", linewidth=0.6,
                   label=f"{SHORT[arm]}, ρ = {float(lv):.2f}")
ax.set_xlabel("genuine detection per key (%)")
ax.set_ylabel("forgery FA at n = 1,024 per key (%)")
xmin = min([100 * FIXED[(lv, s)]["detect"] for lv in LEVELS for s in KEYS] + [100 * PK[k]["detect"] for k in PK])
ax.set_xlim(max(-4, xmin - 6), 101.5)
ax.set_ylim(-4, 104)
ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3)
ax.set_title("Per-key stealing: one point per key (lighter = ρ 0.35)", fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig4_per_key.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# Fig 5: the per-context attacker's mechanics on the hashed arms
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.6))
for a in ARMS:
    for lv in LEVELS:
        L = res["arms"][a]["levels"][lv]
        ns = [n for n in NG if str(n) in L["recovery"]]
        xx = np.log2(np.array(ns, dtype=float))
        ls, hol = ("-", False) if lv == "0.5" else ("--", True)
        line(axs[0], [L["recovery"][str(n)]["coverage"] for n in ns], COL[a], f"{NAME[a]}, ρ = {float(lv):.2f}", MK[a], ls=ls, hollow=hol, x=xx)
        line(axs[1], [L["recovery"][str(n)]["n_contexts"] for n in ns], COL[a], f"{NAME[a]}, ρ = {float(lv):.2f}", MK[a], ls=ls, hollow=hol, x=xx)
rows_cb = {a: {lv: {k: [PK[(a, lv, s)]["attacker"][1024].get("cos_by_count", {}).get(k) for s in CAL[a] if 1024 in PK[(a, lv, s)]["attacker"]] for k in ("16", "32", "128", "512")}
               for lv in LEVELS} for a in ARMS}
BINS = ["16–31", "32–127", "128–511", "≥ 512"]
for ai, a in enumerate(ARMS):
    for li, lv in enumerate(LEVELS):
        vals = [med([x for x in v if x is not None]) if any(x is not None for x in v) else np.nan for v in rows_cb[a][lv].values()]
        xs = np.arange(4) + (-0.3 + 0.2 * (2 * ai + li))
        axs[2].bar(xs, vals, width=0.18, color=COL[a], alpha=0.55 if lv == "0.35" else 1.0, edgecolor="white", linewidth=0.8, label=f"{NAME[a]}, ρ = {float(lv):.2f}")
axs[2].set_xticks(range(4), BINS)
axs[2].set_xlabel("context count among the n = 1,024 observed texts")
axs[2].set_ylabel("cosine with the true per-context key (median over keys)")
axs[2].axhline(0, color=MUTED, lw=0.8)
axs[0].set_ylabel("coverage of a genuine text's positions")
axs[1].set_ylabel("contexts estimated (≥ 16 occurrences)")
axs[1].set_yscale("symlog", linthresh=10)
for ax in axs[:2]:
    nx(ax)
axs[0].set_ylim(-0.03, 1.03)
h, lab = axs[0].get_legend_handles_labels()
fig.legend(h, lab, frameon=False, fontsize=7.5, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Study 5: what the per-context attacker gets from n texts (hashed arms; median over calibrated keys)", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(OUT / "fig5_attacker.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("wrote", sorted(p.name for p in OUT.iterdir()))

# ---------------------------------------------------------------- values quoted in the prose ([[name]] placeholders)
V = {}
for a in ARMS:
    C = res["arms"][a]["calibration"]
    v = C["G2"]["per_key_fpr_pct"]
    V.update({f"g1_{a}": f"{C['G1']['pooled_fpr_pct']:.2f}", f"g1pass_{a}": "PASS" if C["G1"]["pass"] else "FAIL", f"ncal_{a}": str(C["G2"]["n_calibrated"]),
              f"g2min_{a}": f"{min(v.values()):.1f}", f"g2max_{a}": f"{max(v.values()):.1f}", f"rt_{a}": (f"{RT[a]:.3f}" if RT[a] is not None else "—"),
              f"att1_{a}": str(ATT[a]["used"][1]), f"att2_{a}": str(ATT[a]["used"][2]), f"att3_{a}": str(ATT[a]["used"][3]), f"keptfail_{a}": str(ATT[a]["kept_failing"]),
              f"keptfailpct_{a}": f"{100 * ATT[a]['kept_failing'] / max(ATT[a]['n'], 1):.1f}", f"paras_{a}": f"{ATT[a]['paraphrase_s'] / max(ATT[a]['n'], 1):.2f}"})
V.update({"g1_union": f"{GU['pooled_fpr_pct']:.2f}", "g1pass_union": "PASS" if GU["pass"] else "FAIL"})
for lv, k in LV.items():
    F, R = res["fixed"][lv], res["rotation"][lv]
    rows = [FIXED[(lv, s)] for s in KEYS]
    V.update({f"p0v_{k}": F["P0"]["verdict"], f"p0bar_{k}": pc(F["P0"]["bar"]), f"fx_det_{k}": pc(med([r["detect"] for r in rows])), f"fx_fa_{k}": mc(F["oracle_FA"]),
              f"fx_ctrl_{k}": mc(F["random_FA"]), f"fx_s2_{k}": mc(F["s2_success"]), f"fx_s2det_{k}": pc(med([r["s2_detected_after"] for r in rows])),
              f"fx_search_{k}": mc(F["forge_search_FA"]), f"fx_det05_{k}": pc(med([r["det_alpha"][0.05] for r in rows])), f"fx_pool4_{k}": pc(med([r["pooled4"] for r in rows])),
              f"fx_famed_{k}": pc(F["oracle_FA"]["median"]), f"fx_s2med_{k}": pc(F["s2_success"]["median"])})
    for n in NG:
        rc = F["recovery"][str(n)]
        V.update({f"fx_fa{n}_{k}": mc(F["forge_FA"][str(n)]), f"fx_fa{n}med_{k}": pc(F["forge_FA"][str(n)]["median"]), f"fx_cos{n}_{k}": f"{rc['median_cos_known']:.2f}",
                  f"fx_coss{n}_{k}": f"{rc['median_cos_search']:.2f}", f"fx_hits{n}_{k}": str(rc["layer_hits_search"]),
                  f"fx_nfa{n}_{k}": str(sum(FIXED[(lv, s)]["forge_FA"][n] >= F["P0"]["bar"] for s in KEYS))})
    for a in ARMS:
        L = res["arms"][a]["levels"][lv]
        rows = [PK[(a, lv, s)] for s in CAL[a]]
        V.update({f"det_{a}_{k}": mc(L["detection"]), f"detmed_{a}_{k}": pc(L["detection"]["median"]), f"p1_{a}_{k}": "pass" if L["P1"]["pass"] else "fail",
                  f"fa_{a}_{k}": mc(L["genuine_FA"]), f"ctrl_{a}_{k}": mc(L["control_FA"]), f"d1v_{a}_{k}": L["D1"]["verdict"], f"d1bar_{a}_{k}": pc(L["D1"]["bar"]),
                  f"succ_{a}_{k}": mc(L["para_success"]), f"succmed_{a}_{k}": pc(L["para_success"]["median"]), f"pdet_{a}_{k}": mc(L["para_detected"]),
                  f"pdetmed_{a}_{k}": pc(L["para_detected"]["median"]), f"pq_{a}_{k}": mc(L["para_quality_pass"]),
                  f"d2_{a}_{k}": f"{L['D2']['median_diff_points']:+.1f}", f"d2ci_{a}_{k}": ci(L["D2"]["ci95"], 1), f"d2v_{a}_{k}": L["D2"]["verdict"],
                  f"d2lo_{a}_{k}": f"{L['D2']['ci95'][0]:+.1f}", f"famed_{a}_{k}": pc(L["genuine_FA"]["median"]), f"pqmed_{a}_{k}": pc(L["para_quality_pass"]["median"]),
                  f"d2n_{a}_{k}": str(L["D2"]["n_keys_ge_20_points"]), f"d2abs_{a}_{k}": L["D2"]["absolute"],
                  f"d3_{a}_{k}": f"{L['D3']['median_ratio']:.3f}", f"d3ci_{a}_{k}": f"[{L['D3']['ci95'][0]:.3f}, {L['D3']['ci95'][1]:.3f}]", f"d3v_{a}_{k}": L["D3"]["verdict"],
                  f"d3n_{a}_{k}": str(L["D3"]["n_keys_above_1.10"]), f"rep_{a}_{k}": f"{L['D3']['rep_median_keyed']:.4f}", f"repfx_{a}_{k}": f"{L['D3']['rep_median_fixed']:.4f}",
                  f"gates_{a}_{k}": "descriptive" if L["gates"]["descriptive_only"] else "made",
                  f"det05_{a}_{k}": pc(med([r["det_alpha"][0.05] for r in rows])), f"pool4_{a}_{k}": pc(med([r["pooled4"] for r in rows])),
                  f"ppool4_{a}_{k}": pc(med([r["para_pooled4_detected"] for r in rows])),
                  f"strict_{a}_{k}": pc(med([r["para_strict"]["A_model_p95"] for r in rows])), f"strictmed_{a}_{k}": pc(med([r["para_strict"]["A_human_median"] for r in rows])),
                  f"ncon_{a}_{k}": f"{med([r['n_distinct_contexts'] for r in rows]):,.0f}", f"nelig_{a}_{k}": f"{med([r['n_eligible_contexts'] for r in rows]):,.0f}",
                  f"pplk_{a}_{k}": f"{med([r['ppl_median_keyed'] for r in rows]):.2f}", f"pplf_{a}_{k}": f"{med([r['ppl_median_fixed'] for r in rows]):.2f}",
                  f"nsucc50_{a}_{k}": str(sum(r["para_success"] >= 0.5 for r in rows)), f"ratmin_{a}_{k}": f"{min(r['ppl_ratio_median'] for r in rows):.2f}",
                  f"ratmax_{a}_{k}": f"{max(r['ppl_ratio_median'] for r in rows):.2f}"})
        for c in ("ppl", "rep", "len", "cos"):
            V[f"pc_{c}_{a}_{k}"] = pc(med([r["para_cond_pass"][c] for r in rows]))
        for n in NG:
            if str(n) in L["forge_FA"]:
                V.update({f"fa{n}_{a}_{k}": mc(L["forge_FA"][str(n)]), f"fa{n}med_{a}_{k}": pc(L["forge_FA"][str(n)]["median"]),
                          f"nfa{n}_{a}_{k}": str(sum(r["forge_FA"][n] >= L["D1"]["bar"] for r in rows))})
            if str(n) in L["recovery"]:
                rc = L["recovery"][str(n)]
                V.update({f"cos{n}_{a}_{k}": f"{rc['cos_weighted']:.3f}", f"cov{n}_{a}_{k}": f"{rc['coverage']:.3f}", f"nctx{n}_{a}_{k}": f"{rc['n_contexts']:,.0f}"})
        for s in KEYS:
            if (a, lv, s) in PK:
                r = PK[(a, lv, s)]
                V.update({f"pk_det_{a}_{s}_{k}": p0(r["detect"]), f"pk_fa1024_{a}_{s}_{k}": p0(r["forge_FA"].get(1024, float("nan"))) if 1024 in r["forge_FA"] else "—",
                          f"pk_succ_{a}_{s}_{k}": p0(r["para_success"]), f"pk_rat_{a}_{s}_{k}": f"{r['ppl_ratio_median']:.2f}"})
    V.update({f"ru_det_{k}": mc(R["union_detection"]), f"rs_det_{k}": mc(R["single_detection"]), f"r_p1_{k}": "pass" if R["P1"]["pass"] else "fail",
              f"r_succ_{k}": f"{med([100 * ROT[(lv, s)]['union_success'] for s in KEYS]):.1f}", f"r_pdet_{k}": f"{med([100 * ROT[(lv, s)]['union_detected_after'] for s in KEYS]):.1f}",
              f"r_d2_{k}": f"{R['D2']['median_diff_points']:+.1f}", f"r_d2ci_{k}": ci(R["D2"]["ci95"], 1), f"r_d2v_{k}": R["D2"]["verdict"],
              f"r_d2hi_{k}": f"{R['D2']['ci95'][1]:.1f}"})
    for who in ("naive", "cluster"):
        V[f"r_d1v_{who}_{k}"] = R["D1"][who]["verdict"]
        for n in NG:
            V[f"r_fa{n}_{who}_{k}"] = f"{100 * R['forge_FA'][who][str(n)]['mean']:.1f} {ci(R['forge_FA'][who][str(n)]['ci95'])}"
            V[f"r_fa{n}med_{who}_{k}"] = f"{100 * R['forge_FA'][who][str(n)]['mean']:.1f}"
    for n in NG:
        V[f"r_naive{n}_{k}"] = f"{max(R['naive'][str(n)].values()):.2f}"
        V[f"r_keys{n}_{k}"] = str(R["cluster"][str(n)]["keys_recovered_ge_0.5"])
        V[f"r_clcos{n}_{k}"] = f"{med([c['best_cos'] for c in R['cluster'][str(n)]['clusters'].values()]):.2f}"
        ch = R['cluster'][str(n)]['clusters'][str(R['cluster'][str(n)]['chosen_cluster'])]
        V[f"r_chcos{n}_{k}"], V[f"r_chkey{n}_{k}"] = f"{ch['best_cos']:.2f}", str(ch['best_key'])
for lv, k in LV.items():
    fr = [FIXED[(lv, s)] for s in KEYS]
    V.update({f"fx_fa1024min_{k}": p0(min(r['forge_FA'][1024] for r in fr)), f"fx_fa1024max_{k}": p0(max(r['forge_FA'][1024] for r in fr)),
              f"fx_s2min_{k}": p0(min(r['s2_success'] for r in fr)), f"fx_s2max_{k}": p0(max(r['s2_success'] for r in fr)),
              f"fx_detmin_{k}": p0(min(r['detect'] for r in fr)), f"fx_cos64min_{k}": f"{min(r['cos_known'][64] for r in fr):.2f}"})
    for a in ARMS:
        rows = [PK[(a, lv, s)] for s in CAL[a]]
        V.update({f"succmin_{a}_{k}": p0(min(r['para_success'] for r in rows)), f"succmax_{a}_{k}": p0(max(r['para_success'] for r in rows)),
                  f"detmin_{a}_{k}": p0(min(r['detect'] for r in rows)), f"detmax_{a}_{k}": p0(max(r['detect'] for r in rows)),
                  f"pdetmax_{a}_{k}": p0(max(r['para_detected'] for r in rows))})
        if all(1024 in r['forge_FA'] for r in rows):
            V.update({f"fa1024min_{a}_{k}": p0(min(r['forge_FA'][1024] for r in rows)), f"fa1024max_{a}_{k}": p0(max(r['forge_FA'][1024] for r in rows))})
    R = res["rotation"][lv]
    V.update({f"r_succmin_{k}": p0(min(ROT[(lv, s)]['union_success'] for s in KEYS)), f"r_succmax_{k}": p0(max(ROT[(lv, s)]['union_success'] for s in KEYS)),
              f"r_udetmin_{k}": p0(min(ROT[(lv, s)]['union_detect'] for s in KEYS))})
V["fa_upper_max"] = pc(max(res["arms"][a]["levels"][lv]["forge_FA"][n]["ci95"][1] for a in ARMS for lv in LEVELS for n in res["arms"][a]["levels"][lv]["forge_FA"]))
for s in KEYS:
    V[f"fpr3_{s}"] = f"{v3[str(s)]:.1f}"
    for a in ARMS:
        V[f"fpr_{a}_{s}"] = f"{res['arms'][a]['calibration']['G2']['per_key_fpr_pct'][str(s)]:.1f}"
for kk, vv in bars["A"].items():
    V[f"barA_{kk}"] = f"{vv:.3f}" if kk != "ppl" else f"{vv:.1f}"
(OUT / "prose_values.json").write_text(json.dumps(V, indent=2, ensure_ascii=False))

# ---------------------------------------------------------------- assemble the report (only if the prose exists)
pf = Path(__file__).parent / "report_prose.md"
if not pf.exists():
    sys.exit("report_prose.md not written yet; assets only")
if MANF.exists():
    MAN = jl(MANF)
    for ph, d in MAN["phases"].items():
        V[f"{ph}_start_utc"], V[f"{ph}_end_utc"] = d["start_utc"][11:16], d["end_utc"][11:16]
        V[f"{ph}_start_ct"], V[f"{ph}_end_ct"] = d["start_ct"][11:16], d["end_ct"][11:16]
        V[f"{ph}_hours"] = f"{d['seconds'] / 3600:.1f}"
        V[f"{ph}_start_date"], V[f"{ph}_end_date"] = d["start_utc"][:10], d["end_utc"][:10]
    V["total_hours"] = f"{MAN['total_seconds'] / 3600:.1f}"
    V["projected_hours"] = f"{MAN['projected_hours']:.1f}"
    V["report_date"] = MAN["phases"]["A"]["end_utc"][:10]
    V["ct"] = "/".join(sorted({d["ct_label"] for d in MAN["phases"].values()}))       # CDT (UTC-5) until 1 November
    V["deviations"] = "; ".join(MAN["deviations"])
elif TEST:
    for ph in "SKPFRA":
        V.update({f"{ph}_{x}": "00:00" for x in ("start_utc", "end_utc", "start_ct", "end_ct")} | {f"{ph}_hours": "0.0", f"{ph}_start_date": "fixture", f"{ph}_end_date": "fixture"})
    V.update({"total_hours": "0.0", "projected_hours": "26.6", "report_date": "fixture", "deviations": "fixture", "ct": "CDT"})
prose = pf.read_text()
pi = Path(__file__).parent / "report_inwords.md"          # the in-words section, written after the results were read
if not pi.exists() and not TEST:
    sys.exit("report_inwords.md not written yet; assets and prose_values.json only")
if pi.exists() and not TEST:
    prose = prose.replace("<<IN_WORDS>>", pi.read_text().strip())
if TEST:
    prose = prose.replace("<<IN_WORDS>>", "(fixture: the in-words section is written after the results)")
ADD = OUT.parent / "ADDENDUM_ROTATION.md"          # written by study5_addendum/rotation_addendum.py (decision 10; post hoc)
ADDJ = OUT.parent / "ADDENDUM_ROTATION.json"
for n_ in ("256", "1024"):
    V.update({f"add_every_{n_}": "—", f"add_largest_{n_}": "—", f"add_study_{n_}": "—", f"add_good_{n_}": "—", f"add_goodbar_{n_}": "—"})
if ADDJ.exists() and not TEST:
    for n_, d_ in jl(ADDJ)["n"].items():
        V.update({f"add_every_{n_}": f"{100 * d_['every_cluster']['FA']:.0f}", f"add_largest_{n_}": f"{100 * d_['largest_cluster_rule']['FA']:.0f}",
                  f"add_study_{n_}": f"{100 * d_['study_rule']['FA']:.0f}", f"add_good_{n_}": str(d_["clusters_cos_ge_0.5"]), f"add_goodbar_{n_}": str(d_["clusters_cos_ge_0.5_reaching_bar"])})
prose = prose.replace("<<ADDENDUM>>", ADD.read_text().strip() if (ADD.exists() and not TEST) else "(not run yet)")
for ph in ("<<TABLE1>>", "<<TABLES>>", "<<SAMPLES>>"):
    assert prose.count(ph) == 1, ph
missing = sorted(set(re.findall(r"\[\[([\w.]+)\]\]", prose)) - set(V))
assert not missing, f"unknown placeholders: {missing}"
prose = re.sub(r"\[\[([\w.]+)\]\]", lambda m_: V[m_.group(1)], prose)
t1, rest = tables.split("## Table 2", 1)
report = (prose.replace("<<TABLE1>>", t1.replace("## Table 1", "### Table 1").strip())
          .replace("<<TABLES>>", ("## Table 2" + rest).replace("## Table", "### Table").strip())
          .replace("<<SAMPLES>>", samples.strip()))
assert "[[" not in report and "<<" not in report
REPORT.write_text(report)
print("wrote", REPORT)
