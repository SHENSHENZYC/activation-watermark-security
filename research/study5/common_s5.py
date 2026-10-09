"""Study 5 (STUDY5_PROTOCOL_v0.1.md): sources, the owner's tests, the attackers, rules and summaries.

Reused unchanged (hash-locked at the lock): study5_pilot/keyed_core.py (the keyed scheme, its exact test, the
per-context attacker, the union test, clustering), study5_pilot/threat_check.py (all-layer gradients, Route A'),
study2/common_s2.py and study2_pilot/scrub_core.py (paraphrase with the attacker's self-check, quality conditions),
study3/common_s3.py and study3_pilot/power_pilot.py (S4, p-values, null keys), study1_v04/run_v04.py (the bootstrap),
study1_v02/common.py and attack2.py (pools, keys, Route A), study1/core.py (model, generation).

`analyse(src)` works on any source with the Src interface so that the smoke test can run the whole analysis on
tuning-key stand-ins before any study-key statistic exists.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in ("study5_pilot", "study2", "study2_pilot", "study3", "study3_pilot", "study1_v04", "study1_v03", "study1_v02", "study1"):
    sys.path.insert(0, str(ROOT / "research" / p))
import keyed_core as KC  # noqa: E402
import threat_check as TC  # noqa: E402  (all_layer_grads, route_a_prime)
import common_s3 as S3  # noqa: E402
import power_pilot as PP  # noqa: E402
import run_v04 as R4  # noqa: E402  (boot_median, summarise, BOOT_B)
import scrub_core as SC  # noqa: E402
import common as C2  # noqa: E402
from common import core  # noqa: E402

DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study5_v0.1"
PROTOCOL = ROOT / "research" / "STUDY5_PROTOCOL_v0.1.md"
V02 = ROOT / "research" / "study1_v02" / "data"
S3DATA = ROOT / "research" / "study3" / "data"
S2DATA = ROOT / "research" / "study2" / "data"
KEYS = list(S3.KEYS)                                  # 1001-1008
LEVELS = [0.35, 0.50]
ARMS = {"h1": 1, "h4": 4}
N_GRID = [64, 256, 1024]
FORGE_N = [64, 256, 1024]
N_GEN, N_FORGE, N_REF_C = 100, 100, 200
C_MIN = 16
CONTROL = {s: 5000 + (s - 1000) for s in KEYS}       # random-secret controls 5001-5008 (Study 1's control seeds)
ALPHA = 0.01
G1_RANGE, G2_MAX, MIN_CAL, P1_MIN = (0.3, 2.5), 3.0, 6, 50.0
D2_POINTS, D3_RATIO = 20.0, 1.10
BOOT_SEED = 20261003
POOL = 4
SEED0 = 8_000_000
SET_IDX0 = 20                                         # paraphrase seed sets: 20 + 16*arm + 8*level + key (Study 2: 0, 1; pilot: 5-12)
# scope knobs (decision 3's pre-set fallbacks; fixed at the lock from the pilot's projection)
N_OBS = {"h1": 1024, "h4": 1024}
N_PARA = 100
LAYER, D, T_MAX = KC.LAYER, KC.D, KC.T_MAX


def load(p):
    return json.loads(Path(p).read_text())


def save(p, obj):
    Path(p).write_text(json.dumps(obj, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def tag(s, rho):
    return f"k{s}_r{int(round(rho * 100)):03d}"


def seed(arm_i, level_i, key_i, off):
    return SEED0 + 100_000 * arm_i + 10_000 * level_i + 1_000 * key_i + off


def pv_from_stats(S_true, S_null):
    return (1 + (S_null >= S_true[:, None]).sum(1)) / (1 + S_null.shape[1])


def pooled_pv(S_true, S_null, n=POOL):
    nb = len(S_true) // n
    return pv_from_stats(S_true[:nb * n].reshape(nb, n).sum(1), S_null[:nb * n].reshape(nb, n, -1).sum(1))


# ---------------------------------------------------------------- sources
class Src:
    """The study's data. New texts and statistics come from run_s5 (DATA); the fixed arm and rotation reuse Study 1's
    texts, Study 3's features and Study 2's paraphrases."""
    dry = False
    keys, levels, arms = KEYS, LEVELS, ARMS

    def __init__(self, data=DATA):
        self.data = data
        P = C2.pools()
        self.P = P
        self.prompts_B = C2.prompts(P["B"])
        self.prompts_D = C2.prompts(P["D"])[:N_GEN]
        self.bars = load(S2DATA / "bars.json")

    # fixed arm (Study 1 texts, Study 3 features, Study 2 paraphrases)
    def fixed_texts(self, s, rho, c):
        return load(V02 / f"K_{tag(s, rho)}_{c}.json")

    def fixed_G(self, s, rho, c):
        return np.load(S3DATA / f"K_{tag(s, rho)}_{c}.npz")["G"].astype(np.float32)

    def fixed_ppl(self, s, rho, c):
        return load(V02 / f"K_{tag(s, rho)}_summary.json")[f"ppl_{c}"]

    def ref_G(self):
        return np.load(S3DATA / "S_F_van.npz")["G"].astype(np.float32)

    def null_G(self):
        return np.load(S3DATA / "S_A_van.npz")["G"].astype(np.float32)

    def s2_para(self, s, rho):
        """Study 2's kept P-Qwen paraphrases of the oracle texts of (s, rho): (texts, G, quality raw dict), in pool D order."""
        P = load(S2DATA / "para_qwen_gen.json")
        idx = [i for i, l in enumerate(P["labels"]) if l[0] == s and abs(l[1] - rho) < 1e-9]
        texts = [P["attempts"][P["kept"][i]][i]["text"] for i in idx]
        G = np.load(S2DATA / "G_para_qwen_gen.npy", mmap_mode="r")[idx].astype(np.float32)
        Q = load(S2DATA / "Q_para_qwen_gen.json")
        q = {k: np.asarray(Q[k])[idx] for k in ("ppl", "rep", "len", "cos")}
        return texts, G, q

    def orig_quality(self, s, rho):
        o = self.bars["orig"][tag(s, rho)]
        return {k: np.asarray(o[k]) for k in ("ppl", "rep", "len")}

    def key_dir(self, s):
        return KC.fixed_dir(s)

    def key_vec(self, s, rho):
        return C2.key(s, rho)

    # keyed arms (run_s5 outputs)
    def T(self, name):
        return self.data / name

    def stats(self, name):
        z = np.load(self.T(f"{name}.npz"))
        return z["S_true"].astype(np.float64), z["S_null"].astype(np.float64), z["npos"]

    def texts(self, name):
        return load(self.T(f"{name}.json"))


    # shared unwatermarked texts (Study 1 v0.2)
    def null_texts(self):
        return load(V02 / "S_A_van.json")

    def owner_ref_texts(self):
        return load(V02 / "S_F_van.json")

    def attacker_texts(self):
        return load(V02 / "S_C_ref.json")[:N_REF_C]

    def attacker_norms(self):
        """The attacker's own strength scale per layer (median token norm over its references; Study 1 v0.2)."""
        return np.load(V02 / "S_C_ref_norms.npy")

    def obs_texts(self, s, rho):
        return self.fixed_texts(s, rho, "obs")

    def reused_files(self):
        fs = [V02 / "S_A_van.json", V02 / "S_F_van.json", V02 / "S_C_ref.json", V02 / "S_C_ref_norms.npy",
              S3DATA / "S_F_van.npz", S3DATA / "S_A_van.npz", S2DATA / "bars.json", S2DATA / "para_qwen_gen.json",
              S2DATA / "Q_para_qwen_gen.json", S2DATA / "G_para_qwen_gen.npy"]
        for s in KEYS:
            for rho in LEVELS:
                t = tag(s, rho)
                fs += [V02 / f"K_{t}_{c}.json" for c in ("obs", "oracle", "random")] + [V02 / f"K_{t}_summary.json"]
                fs += [S3DATA / f"K_{t}_{c}.npz" for c in ("oracle", "random")]
        return fs


# ---------------------------------------------------------------- the owner's tests
class Owner:
    """The keyed per-position test (hashed arms), S4 (fixed arm) and the union test (rotation)."""

    def __init__(self, ref_pos, ref_G):
        self.keyed = KC.KeyedOwner(ref_pos)
        self.ref_s4 = S3.reference(ref_G, ref_G)
        self.nm = PP.null_matrix()
        self.nm_big = S3.null_keys_big()

    def keyed_stats(self, G, ids, h, secret):
        """(S_true, S_null [999], n positions) for one text's per-position gradients."""
        X = KC.standardise(G, self.keyed.ref)
        pos, ctx = KC.contexts(ids, h)
        if len(pos) == 0:
            return 0.0, np.zeros(KC.M_NULL), 0
        allS = self.keyed.stats(X, pos, ctx, np.concatenate([[np.uint64(secret)], self.keyed.secrets_null]))
        return float(allS[0]), allS[1:], int(len(pos))

    def s4_stats(self, G, vdir):
        X = PP.transform("S4", None, np.asarray(G, dtype=np.float32), self.ref_s4)
        return X @ vdir, X @ self.nm.T

    def union_stats(self, G, keys_unit):
        X = PP.transform("S4", None, np.asarray(G, dtype=np.float32), self.ref_s4)
        Kk = keys_unit.shape[0]
        U = (X @ keys_unit.T).max(1)
        groups = self.nm_big[:KC.M_NULL * Kk].reshape(KC.M_NULL, Kk, -1)
        Un = np.stack([(X @ groups[j].T).max(1) for j in range(KC.M_NULL)], 1)
        return U, Un


def fluent_flags(ppl, rep, ppl_cut, rep_cut):
    return S3.fluent_flags(ppl, rep, ppl_cut, rep_cut)


def cut95(values):
    return float(np.quantile(np.asarray(values, dtype=np.float64), 0.95))


# ---------------------------------------------------------------- summaries and rules
def summ(per_key, rng):
    return R4.summarise([np.asarray(x, dtype=float) for x in per_key], rng)


def paired_boot(xs, ys, rng, stat=np.mean):
    """95% interval of the median over keys of stat(x) - stat(y), resampling keys then the paired texts."""
    K_ = len(xs)
    meds = []
    for _ in range(R4.BOOT_B):
        d = []
        for k in rng.integers(0, K_, K_):
            idx = rng.integers(0, len(xs[k]), len(xs[k]))
            d.append(stat(xs[k][idx]) - stat(ys[k][idx]))
        meds.append(np.median(d))
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def ratio_boot(per_key_ratios, rng):
    """95% interval of the median over keys of the per-key median ratio (keys, then texts)."""
    K_ = len(per_key_ratios)
    meds = []
    for _ in range(R4.BOOT_B):
        m = []
        for k in rng.integers(0, K_, K_):
            r = per_key_ratios[k]
            m.append(np.median(r[rng.integers(0, len(r), len(r))]))
        meds.append(np.median(m))
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def d1_verdict(forge, genuine, control):
    """forge: {n: summary of FA}, genuine and control: summaries of FA. Study 3's X1 form (protocol §9)."""
    bar = 0.5 * genuine["median"]
    if control["median"] >= bar:
        return {"verdict": "generic steering suffices", "bar": bar}
    for n in sorted(forge, key=int):
        f = forge[n]
        if f["median"] >= bar and f["ci95"][0] > control["ci95"][1]:
            return {"verdict": f"practical (n={n})", "bar": bar, "practical_n": int(n)}
    if all(forge[n]["ci95"][1] < bar for n in forge):
        return {"verdict": "stealing blocked at n <= 1024", "bar": bar}
    return {"verdict": "inconclusive", "bar": bar}


def d2_verdict(dmed, ci):
    if ci[0] > 0 and dmed >= D2_POINTS:
        return "material robustness cost"
    if ci[1] < D2_POINTS:
        return "immaterial"
    return "inconclusive"


def d3_verdict(ci):
    if ci[0] > D3_RATIO:
        return "material quality cost"
    if ci[1] <= D3_RATIO:
        return "immaterial"
    return "inconclusive"


def s1_absolute(success):
    """Study 2's absolute reading of a scrub-success summary: effective at the 50% bar (lower bound above the originals'
    miss rate is not re-checked here; the originals' miss rate is 0-4%)."""
    if success["median"] >= 0.5:
        return "paraphrase effective (>= 50%)"
    if success["ci95"][1] < 0.5:
        return "not effective"
    return "inconclusive"


# ---------------------------------------------------------------- the analysis
def analyse(src):
    rng = np.random.default_rng(BOOT_SEED)
    res = {"alpha": ALPHA, "boot_seed": BOOT_SEED, "boot_B": R4.BOOT_B, "scope": {"N_OBS": N_OBS, "N_PARA": N_PARA},
           "arms": {}, "fixed": {}, "rotation": {}}
    keys = src.keys
    # ---- calibration of the keyed arms (G1, G2) and of the union test on pool A
    for arm, h in src.arms.items():
        A = {"G2": {"per_key_fpr_pct": {}}}
        fp = {}
        for s in keys:
            St, Sn, _ = src.stats(f"S_null_{arm}_k{s}")
            fp[s] = 100 * float((pv_from_stats(St, Sn) <= ALPHA).mean())
        pooled = float(np.mean(list(fp.values())))
        cal = [s for s in keys if fp[s] <= G2_MAX]
        A["G1"] = {"pooled_fpr_pct": pooled, "range": list(G1_RANGE), "pass": G1_RANGE[0] <= pooled <= G1_RANGE[1]}
        A["G2"] = {"per_key_fpr_pct": {str(s): fp[s] for s in keys}, "max_pct": G2_MAX, "calibrated_keys": cal,
                   "n_calibrated": len(cal), "stop": len(cal) < MIN_CAL}
        res["arms"][arm] = {"h": h, "calibration": A, "levels": {}}
    Ut, Un = src.stats("S_null_union")[:2]
    pooled_u = 100 * float((pv_from_stats(Ut, Un) <= ALPHA).mean())
    res["rotation"]["G1"] = {"pooled_fpr_pct": pooled_u, "range": list(G1_RANGE), "pass": G1_RANGE[0] <= pooled_u <= G1_RANGE[1]}

    for rho in src.levels:
        # ---- the fixed arm: Study 3's S4 on the oracle, the random-key control and the Route A' forgeries (P0)
        F = {"per_key": {}}
        fa = {"oracle": [], "random": [], "forge": {n: [] for n in FORGE_N}, "forge_search": []}
        cos_known, cos_search, layer_hits = {n: [] for n in N_GRID}, {n: [] for n in N_GRID}, {n: 0 for n in N_GRID}
        for s in keys:
            St, Sn, _ = src.stats(f"F_{tag(s, rho)}_oracle")
            St_r, Sn_r, _ = src.stats(f"F_{tag(s, rho)}_random")
            oq = src.orig_quality(s, rho)
            cut_p, cut_r = cut95(oq["ppl"]), cut95(oq["rep"])
            acc_o = (pv_from_stats(St, Sn) <= ALPHA).astype(float)
            fl_o = fluent_flags(oq["ppl"], oq["rep"], cut_p, cut_r)
            rq = src.texts(f"F_{tag(s, rho)}_random_quality")
            acc_r = (pv_from_stats(St_r, Sn_r) <= ALPHA).astype(float)
            fl_r = fluent_flags(rq["ppl"], rq["rep"], cut_p, cut_r)
            fa["oracle"].append(acc_o * fl_o)
            fa["random"].append(acc_r * fl_r)
            est = src.texts(f"F_{tag(s, rho)}_est")
            for n in N_GRID:
                cos_known[n].append(est[str(n)]["known"]["cos"])
                cos_search[n].append(est[str(n)]["search"]["cos"])
                layer_hits[n] += int(est[str(n)]["search"]["layer"] == LAYER)
            for n in FORGE_N:
                St_f, Sn_f, _ = src.stats(f"F_{tag(s, rho)}_forge_n{n}")
                fq = src.texts(f"F_{tag(s, rho)}_forge_n{n}_quality")
                fa["forge"][n].append((pv_from_stats(St_f, Sn_f) <= ALPHA) * fluent_flags(fq["ppl"], fq["rep"], cut_p, cut_r))
            n_mid = N_GRID[len(N_GRID) // 2]
            St_f, Sn_f, _ = src.stats(f"F_{tag(s, rho)}_forge_search_n{n_mid}")
            fq = src.texts(f"F_{tag(s, rho)}_forge_search_n{n_mid}_quality")
            fa["forge_search"].append((pv_from_stats(St_f, Sn_f) <= ALPHA) * fluent_flags(fq["ppl"], fq["rep"], cut_p, cut_r))
            F["per_key"][str(s)] = {"oracle_FA": float((acc_o * fl_o).mean()), "detect": float(acc_o.mean()),
                                    "cos_known": {str(n): est[str(n)]["known"]["cos"] for n in N_GRID},
                                    "cos_search": {str(n): est[str(n)]["search"]["cos"] for n in N_GRID},
                                    "forge_FA": {str(n): float(fa["forge"][n][-1].mean()) for n in FORGE_N}}
        F["oracle_FA"], F["random_FA"] = summ(fa["oracle"], rng), summ(fa["random"], rng)
        F["forge_FA"] = {str(n): summ(fa["forge"][n], rng) for n in FORGE_N}
        F["forge_search_FA"] = {"n": N_GRID[len(N_GRID) // 2], **summ(fa["forge_search"], rng)}
        F["recovery"] = {str(n): {"median_cos_known": float(np.median(cos_known[n])), "median_cos_search": float(np.median(cos_search[n])),
                                  "layer_hits_search": layer_hits[n]} for n in N_GRID}
        F["P0"] = d1_verdict({str(n): F["forge_FA"][str(n)] for n in FORGE_N}, F["oracle_FA"], F["random_FA"])
        F["P0"]["pass"] = F["P0"]["verdict"].startswith("practical")
        res["fixed"][str(rho)] = F
        # the fixed key's Study 2 scrub success per key (the D2 comparator), recomputed from Study 2's locked data
        fixed_success = {}
        for s in keys:
            texts, G, q = src.s2_para(s, rho)
            Tt, Tn = src.owner.s4_stats(G, src.key_dir(s))
            det = pv_from_stats(Tt, Tn) <= ALPHA
            cond = SC.conditions(src.orig_quality(s, rho), q, src.bars["A"])
            fixed_success[s] = ((~det) & cond["all"]).astype(float)
        F["s2_success"] = summ([fixed_success[s] for s in keys], rng)

        # ---- the keyed arms
        for arm, h in src.arms.items():
            A = res["arms"][arm]
            cal = A["calibration"]["G2"]["calibrated_keys"]
            L = {"per_key": {}}
            det, fa_g, fa_c, fa_f = [], [], [], {n: [] for n in FORGE_N}
            succ, det_after, qpass, dsucc, ratios, reps = [], [], [], [], [], []
            att = {n: {"cos_weighted": [], "coverage": [], "n_contexts": []} for n in N_GRID}
            for s in cal:
                t = f"{arm}_{tag(s, rho)}"
                St, Sn, _ = src.stats(f"K_{t}_genuine")
                gq = src.texts(f"K_{t}_genuine_quality")
                acc = (pv_from_stats(St, Sn) <= ALPHA).astype(float)
                cut_p, cut_r = cut95(gq["ppl"]), cut95(gq["rep"])
                det.append(acc)
                fa_g.append(acc * fluent_flags(gq["ppl"], gq["rep"], cut_p, cut_r))
                St_c, Sn_c, _ = src.stats(f"K_{t}_control")
                cq = src.texts(f"K_{t}_control_quality")
                fa_c.append((pv_from_stats(St_c, Sn_c) <= ALPHA) * fluent_flags(cq["ppl"], cq["rep"], cut_p, cut_r))
                for n in FORGE_N:
                    if n > N_OBS[arm]:
                        continue
                    St_f, Sn_f, _ = src.stats(f"K_{t}_forge_n{n}")
                    fq = src.texts(f"K_{t}_forge_n{n}_quality")
                    fa_f[n].append((pv_from_stats(St_f, Sn_f) <= ALPHA) * fluent_flags(fq["ppl"], fq["rep"], cut_p, cut_r))
                ak = src.texts(f"K_{t}_attacker")
                for n in N_GRID:
                    if str(n) in ak:
                        att[n]["cos_weighted"].append(ak[str(n)]["cos_weighted"])
                        att[n]["coverage"].append(ak[str(n)]["coverage_genuine"])
                        att[n]["n_contexts"].append(ak[str(n)]["n_contexts"])
                # paraphrase: success under the keyed test and Study 2's conditions; paired with the fixed key's Study 2 success
                St_p, Sn_p, _ = src.stats(f"P_{t}")
                pq = src.texts(f"P_{t}_quality")
                detp = pv_from_stats(St_p, Sn_p) <= ALPHA
                allq = np.asarray(pq["all"], dtype=bool)
                sc = ((~detp) & allq).astype(float)
                succ.append(sc)
                det_after.append(detp.astype(float))
                qpass.append(allq.astype(float))
                dsucc.append((sc, fixed_success[s][:len(sc)]))
                # quality: the perplexity ratio keyed/fixed on the same prompts
                oq = src.orig_quality(s, rho)
                ratios.append(np.asarray(gq["ppl"], dtype=float) / np.asarray(oq["ppl"], dtype=float)[:len(gq["ppl"])])
                reps.append((float(np.median(gq["rep"])), float(np.median(oq["rep"]))))
                L["per_key"][str(s)] = {"detect": float(acc.mean()), "genuine_FA": float(fa_g[-1].mean()), "control_FA": float(fa_c[-1].mean()),
                                        "forge_FA": {str(n): float(fa_f[n][-1].mean()) for n in FORGE_N if n <= N_OBS[arm]},
                                        "para_success": float(sc.mean()), "fixed_s2_success": float(fixed_success[s].mean()),
                                        "ppl_ratio_median": float(np.median(ratios[-1])), "attacker": {str(n): ak.get(str(n)) for n in N_GRID}}
            L["detection"] = summ(det, rng)
            L["P1"] = {"median_pct": 100 * L["detection"]["median"], "min_pct": P1_MIN, "pass": 100 * L["detection"]["median"] >= P1_MIN}
            L["genuine_FA"], L["control_FA"] = summ(fa_g, rng), summ(fa_c, rng)
            L["forge_FA"] = {str(n): summ(fa_f[n], rng) for n in FORGE_N if fa_f[n]}
            L["recovery"] = {str(n): {k: float(np.median(v)) for k, v in att[n].items()} for n in N_GRID if att[n]["cos_weighted"]}
            L["D1"] = d1_verdict(L["forge_FA"], L["genuine_FA"], L["control_FA"])
            L["para_success"], L["para_detected"], L["para_quality_pass"] = summ(succ, rng), summ(det_after, rng), summ(qpass, rng)
            dmed = float(np.median([x.mean() - y.mean() for x, y in dsucc])) * 100
            ci = [100 * c for c in paired_boot([x for x, _ in dsucc], [y for _, y in dsucc], rng)]
            L["D2"] = {"median_diff_points": dmed, "ci95": ci, "verdict": d2_verdict(dmed, ci), "absolute": s1_absolute(L["para_success"]),
                       "n_keys_ge_20_points": int(sum((x.mean() - y.mean()) * 100 >= D2_POINTS for x, y in dsucc))}
            rmed = float(np.median([np.median(r) for r in ratios]))
            rci = ratio_boot(ratios, rng)
            L["D3"] = {"median_ratio": rmed, "ci95": rci, "verdict": d3_verdict(rci), "n_keys_above_1.10": int(sum(np.median(r) > D3_RATIO for r in ratios)),
                       "rep_median_keyed": float(np.median([a for a, _ in reps])), "rep_median_fixed": float(np.median([b for _, b in reps]))}
            L["gates"] = {"P0": F["P0"]["pass"], "P1": L["P1"]["pass"], "descriptive_only": not (F["P0"]["pass"] and L["P1"]["pass"])}
            A["levels"][str(rho)] = L

        # ---- rotation (K = 8 on the existing texts): union-test detection, attackers, forgeries, the union's loss on Study 2's paraphrases
        R = {"per_key": {}}
        det_u, det_s, loss = [], [], []
        for s in keys:
            Ut, Un, _ = src.stats(f"R_{tag(s, rho)}_oracle_union")
            St, Sn, _ = src.stats(f"F_{tag(s, rho)}_oracle")
            du, ds = (pv_from_stats(Ut, Un) <= ALPHA).astype(float), (pv_from_stats(St, Sn) <= ALPHA).astype(float)
            det_u.append(du)
            det_s.append(ds)
            Up, Unp, _ = src.stats(f"R_{tag(s, rho)}_para_union")
            texts, G, q = src.s2_para(s, rho)
            cond = SC.conditions(src.orig_quality(s, rho), q, src.bars["A"])
            su = ((pv_from_stats(Up, Unp) > ALPHA) & cond["all"]).astype(float)
            loss.append((su, fixed_success[s]))
            R["per_key"][str(s)] = {"union_detect": float(du.mean()), "single_detect": float(ds.mean()), "union_success": float(su.mean())}
        R["union_detection"], R["single_detection"] = summ(det_u, rng), summ(det_s, rng)
        R["P1"] = {"median_pct": 100 * R["union_detection"]["median"], "pass": 100 * R["union_detection"]["median"] >= P1_MIN}
        ro = src.texts(f"R_r{int(round(rho * 100)):03d}_attack")
        R["naive"], R["cluster"] = ro["naive"], ro["cluster"]
        fa_f = {}
        for who in ("naive", "cluster"):
            fa_f[who] = {}
            for n in FORGE_N:
                Ut, Un, _ = src.stats(f"R_r{int(round(rho * 100)):03d}_forge_{who}_n{n}_union")
                fq = src.texts(f"R_r{int(round(rho * 100)):03d}_forge_{who}_n{n}_quality")
                # fluency against the pooled oracle bars of the level (the rotating corpus has no single key)
                allo = np.concatenate([src.orig_quality(s, rho)["ppl"] for s in keys]), np.concatenate([src.orig_quality(s, rho)["rep"] for s in keys])
                fa_f[who][str(n)] = (pv_from_stats(Ut, Un) <= ALPHA) * fluent_flags(fq["ppl"], fq["rep"], cut95(allo[0]), cut95(allo[1]))
        gen_fa = summ(fa["oracle"], rng)
        R["forge_FA"] = {who: {n: {"mean": float(v.mean()), "ci95": [float(np.quantile([np.mean(rng.choice(v, len(v))) for _ in range(R4.BOOT_B)], q)) for q in (0.025, 0.975)]}
                               for n, v in d.items()} for who, d in fa_f.items()}
        R["D1"] = {who: d1_verdict({n: {"median": v["mean"], "ci95": v["ci95"]} for n, v in R["forge_FA"][who].items()}, gen_fa, F["random_FA"])
                   for who in fa_f}
        dmed = float(np.median([x.mean() - y.mean() for x, y in loss])) * 100
        ci = [100 * c for c in paired_boot([x for x, _ in loss], [y for _, y in loss], rng)]
        R["D2"] = {"median_diff_points": dmed, "ci95": ci, "verdict": d2_verdict(dmed, ci)}
        res["rotation"][str(rho)] = R
    return res


REQUIRED = {"arm_level": ["detection", "P1", "genuine_FA", "control_FA", "forge_FA", "recovery", "D1", "para_success", "para_detected",
                          "para_quality_pass", "D2", "D3", "gates", "per_key"],
            "fixed_level": ["oracle_FA", "random_FA", "forge_FA", "forge_search_FA", "recovery", "P0", "s2_success", "per_key"],
            "rot_level": ["union_detection", "single_detection", "P1", "naive", "cluster", "forge_FA", "D1", "D2", "per_key"]}


def missing_fields(res, levels, arms):
    miss = [k for k in ("arms", "fixed", "rotation", "scope") if k not in res]
    for arm in arms:
        A = res.get("arms", {}).get(arm, {})
        miss += [f"{arm}.calibration.{k}" for k in ("G1", "G2") if k not in A.get("calibration", {})]
        for rho in levels:
            L = A.get("levels", {}).get(str(rho), {})
            miss += [f"{arm}.{rho}.{k}" for k in REQUIRED["arm_level"] if k not in L]
    for rho in levels:
        miss += [f"fixed.{rho}.{k}" for k in REQUIRED["fixed_level"] if k not in res.get("fixed", {}).get(str(rho), {})]
        miss += [f"rotation.{rho}.{k}" for k in REQUIRED["rot_level"] if k not in res.get("rotation", {}).get(str(rho), {})]
    if "G1" not in res.get("rotation", {}):
        miss.append("rotation.G1")
    return miss
