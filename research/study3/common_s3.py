"""Study 3 (STUDY3_PROTOCOL_v0.1.md): sources, the S4 exact key test, fluency, rules and secondaries.

Reused unchanged (hash-locked): the power pilot's power_pilot.py (text_features, transform, pvalues, null keys);
Study 1 v0.4's common4.py (seq-rep-4, the oracle 95th-percentile bar) and run_v04.py (the cluster bootstrap);
v0.2's common.py (keys, pools) and detect2.py (the probe's acceptance rule).

`analyse(src, tok)` works on any source object with the StudySrc interface, so that the input-validation smoke test can
run the whole analysis on tuning-key texts (SmokeSrc in validate_s3.py) before any study-key statistic exists.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "study1_v04"))
sys.path.insert(0, str(ROOT / "research" / "study3_pilot"))
import common4 as C4  # noqa: E402  (first: puts v0.3, v0.2 and v0.1 on sys.path)
from common4 import C2, core  # noqa: E402
import detect2  # noqa: E402  (v0.2)
import run_v04 as R4  # noqa: E402  (v0.4: boot_median, summarise)
import power_pilot as PP  # noqa: E402  (the pilot: text_features, transform, pvalues, null_matrix, unit)

V02, V03, V04 = C4.V02_DATA, C4.V03_DATA, ROOT / "research" / "study1_v04" / "data"
DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study3_v0.1"
PROTOCOL = ROOT / "research" / "STUDY3_PROTOCOL_v0.1.md"

KEYS = list(C2.STUDY_KEYS)            # 1001-1008
LEVELS = [0.25, 0.35, 0.50, 0.70]
LATE = [0.35, 0.50, 0.70]             # levels with v0.3 and v0.4 forgeries
ROUTES = ["A", "B"]
N02, N34 = [64, 256, 1024], [64, 256]
D = C2.D_MODEL                        # 1536
PRIMARY, SECONDARY = "S4", "S3"
ALPHA, ALPHA2, M2 = 0.01, 0.001, 9999
G1_RANGE, G2_MAX, MIN_CAL, P1_MIN = (0.3, 2.5), 3.0, 6, 20.0
BOOT_SEED = 20260930
POOL = 4                              # texts per pooled test (secondary)


def load(p):
    return json.loads(Path(p).read_text())


# ---------------------------------------------------------------- conditions and files
def cond_names(rho):
    names = ["oracle", "E", "random"] + [f"v02_{r}_n{n}" for r in ROUTES for n in N02]
    if rho in LATE:
        names += [f"v0{v}_{r}_n{n}" for v in (3, 4) for r in ROUTES for n in N34]
    return names


def is_forgery(c):
    return c.startswith("v0")


def text_file(s, rho, c):
    t = C4.tag(s, rho)
    if c in ("oracle", "E", "random"):
        return V02 / f"K_{t}_{c}.json"
    ver, r, n = c.split("_")
    return {"v02": V02 / f"K_{t}_forge_{r}_{n}.json", "v03": V03 / f"K_{t}_forge3_{r}_{n}.json",
            "v04": V04 / f"K_{t}_forge4_{r}_{n}.json"}[ver]


def reused_files():
    """Every Study 1 file this study reads (562): the shared sets, and per key-level the v0.2 summary, the texts, and
    the v0.3 / v0.4 per-key-level results (probe scores, perplexities, cos to the key)."""
    fs = [V02 / "S_F_van.json", V02 / "S_A_van.json"]
    for s in KEYS:
        for rho in LEVELS:
            t = C4.tag(s, rho)
            fs.append(V02 / f"K_{t}_summary.json")
            fs += [text_file(s, rho, c) for c in cond_names(rho)]
            if rho in LATE:
                fs += [V03 / f"K_{t}_v03.json", V04 / f"K_{t}_v04.json"]
    return fs


def human_texts():
    P = C2.pools()
    return [u["human_continuation"] for u in P["A1"] + P["A2"]]


def key_dir(s):
    return PP.unit(C2.key(s, 1.0).numpy().astype(np.float64))


def null_keys_big():
    """M2 = 9,999 null keys, seeds 77,700,000 + j; the first 999 are the primary set (core.null_keys)."""
    return PP.unit(np.stack([core.make_key(core.NULL_KEY_SEED * 100000 + j, D, 1.0).numpy()
                             for j in range(M2)]).astype(np.float64))


class StudySrc:
    """The study's data: features computed by run_s3.py phase F; texts, probe scores and perplexities from Study 1."""
    keys, levels = KEYS, LEVELS
    null_model, null_human, ref = "S_A_van", "S_A_human", "S_F_van"
    a2 = slice(500, 1000)             # pool A2 = the last 500 of pool A (v0.2: scores_A2 = sA[500:])

    def __init__(self, data=DATA):
        self.data = data

    def cond_names(self, rho):
        return cond_names(rho)

    def feats(self, name):
        z = np.load(self.data / f"{name}.npz")
        return z["A"].astype(np.float32), z["G"].astype(np.float32)

    def name(self, s, rho, c):
        return f"K_{C4.tag(s, rho)}_{c}"

    def key(self, s):
        return key_dir(s)

    def texts(self, s, rho, c):
        return load(text_file(s, rho, c))

    def probe(self, s, rho, c):
        """(scores, perplexities given the prompt, threshold) of the owner's probe; None for pool E (probe training)."""
        if c == "E":
            return None
        t = C4.tag(s, rho)
        S2 = load(V02 / f"K_{t}_summary.json")
        if c in ("oracle", "random"):
            return S2[f"scores_{c}"], S2[f"ppl_{c}"], S2["threshold"]
        ver, r, n = c.split("_")
        if ver == "v02":
            return S2[f"scores_forge_{r}_{n}"], S2[f"ppl_forge_{r}_{n}"], S2["threshold"]
        a = load((V03 / f"K_{t}_v03.json") if ver == "v03" else (V04 / f"K_{t}_v04.json"))["attacks"][f"{r}_{n}"]
        return a["scores"], a["ppl"], S2["threshold"]

    def cos(self, s, rho, c):
        """The attacker's cos(v_hat, v) for a forgery condition (Study 1's saved estimate)."""
        t = C4.tag(s, rho)
        ver, r, n = c.split("_")
        if ver == "v02":
            return load(V02 / f"K_{t}_summary.json")["estimates"][n[1:]][r]["cos"]
        return load((V03 / f"K_{t}_v03.json") if ver == "v03" else (V04 / f"K_{t}_v04.json"))["attacks"][f"{r}_{n}"][
            "cos_true"]

    def a2_probe(self, s, rho):
        S2 = load(V02 / f"K_{C4.tag(s, rho)}_summary.json")
        return S2["scores_A2"], S2["threshold"]


# ---------------------------------------------------------------- statistics
def reference(A, G):
    return {"mu_a": A.mean(0), "sd_a": np.maximum(A.std(0, ddof=1), 1e-12),
            "mu_g": G.mean(0), "sd_g": np.maximum(G.std(0, ddof=1), 1e-12)}


def pv(X, v, NM):
    return PP.pvalues(X @ v, X @ NM.T)


def pooled_pv(X, v, NM, n=POOL):
    nb = len(X) // n
    return PP.pvalues((X[:nb * n] @ v).reshape(nb, n).sum(1), (X[:nb * n] @ NM.T).reshape(nb, n, -1).sum(1))


def fluent_flags(ppl, rep, ppl_cut, rep_cut):
    """v0.4's fluency (protocol §5): perplexity and seq-rep-4 at most the key-level oracle's 95th percentiles."""
    return ((np.asarray(ppl, dtype=np.float64) <= ppl_cut) & (np.asarray(rep, dtype=np.float64) <= rep_cut)).astype(float)


def summ(per_key, rng):
    return R4.summarise([np.asarray(x, dtype=float) for x in per_key], rng)


def med(per_key):
    return float(np.median([np.mean(x) for x in per_key]))


def paired_boot(xs, ys, rng):
    """95% interval of the median over keys of mean(x) - mean(y), resampling keys, then texts (the same texts for x
    and y, which are two detectors on the same texts)."""
    K, meds = len(xs), []
    for _ in range(R4.BOOT_B):
        d = []
        for k in rng.integers(0, K, K):
            idx = rng.integers(0, len(xs[k]), len(xs[k]))
            d.append(xs[k][idx].mean() - ys[k][idx].mean())
        meds.append(np.median(d))
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def x1_verdict(L, prefix, orc, rnd):
    """v0.4's F1 logic on exact-FA: practical at some n in {64, 256}; not practical if both upper bounds < bar."""
    out = {}
    for r in ROUTES:
        v = "inconclusive"
        for n in N34:
            f = L[f"{prefix}_{r}_n{n}"]["exact_FA"]
            if f["median"] >= 0.5 * orc["median"] and f["ci95"][0] > rnd["ci95"][1]:
                v = f"practical (n={n})"
                break
        if v == "inconclusive" and all(L[f"{prefix}_{r}_n{n}"]["exact_FA"]["ci95"][1] < 0.5 * orc["median"]
                                       for n in N34):
            v = "not practical"
        out[r] = v
    return out


def analyse_stat(c, src, tok, ref, NM, NM2, seed):
    """All rules and secondaries for statistic c (S4 primary, S3 secondary). NM2 (9,999 keys) only for S4."""
    rng = np.random.default_rng(seed)
    keys = src.keys
    Xm = PP.transform(c, *src.feats(src.null_model), ref)
    Xh = PP.transform(c, *src.feats(src.null_human), ref)
    pm = {s: pv(Xm, src.key(s), NM) for s in keys}
    ph = {s: pv(Xh, src.key(s), NM) for s in keys}
    fpr_m = {s: 100 * float((pm[s] <= ALPHA).mean()) for s in keys}
    fpr_h = {s: 100 * float((ph[s] <= ALPHA).mean()) for s in keys}
    pooled_m = float(np.mean(list(fpr_m.values())))
    cal = [s for s in keys if fpr_m[s] <= G2_MAX]
    out = {"G1": {"pooled_fpr_pct": pooled_m, "range": list(G1_RANGE), "pass": G1_RANGE[0] <= pooled_m <= G1_RANGE[1]},
           "G2": {"per_key_fpr_pct": {str(s): fpr_m[s] for s in keys}, "max_pct": G2_MAX,
                  "calibrated_keys": cal, "n_calibrated": len(cal), "stop": len(cal) < MIN_CAL},
           "H1": {"per_key_fpr_pct": {str(s): fpr_h[s] for s in keys},
                  "n_keys_above_max": int(sum(fpr_h[s] > G2_MAX for s in keys)),
                  "pooled_fpr_pct": float(np.mean(list(fpr_h.values())))},
           "levels": {}}
    if not cal:  # G2 fails completely: nothing to summarise (protocol §9: stop)
        return out
    if NM2 is not None:
        out["alpha_0.001"] = {"pooled_fpr_model_pct": float(np.mean([100 * (pv(Xm, src.key(s), NM2) <= ALPHA2).mean()
                                                                     for s in keys])),
                              "pooled_fpr_human_pct": float(np.mean([100 * (pv(Xh, src.key(s), NM2) <= ALPHA2).mean()
                                                                     for s in keys]))}
    for rho in src.levels:
        L, per = {}, {}
        for s in keys:
            v = src.key(s)
            orc_txt = src.texts(s, rho, "oracle")
            _, orc_ppl, _ = src.probe(s, rho, "oracle")
            cut_ppl, cut_rep = C4.cut(orc_ppl), C4.cut(C4.seqrep4(tok, orc_txt))
            for cn in src.cond_names(rho):
                X = PP.transform(c, *src.feats(src.name(s, rho, cn)), ref)
                p = pv(X, v, NM)
                d = {"p": p, "acc": (p <= ALPHA).astype(float), "pool": (pooled_pv(X, v, NM) <= ALPHA).astype(float)}
                if NM2 is not None:
                    d["acc2"] = (pv(X, v, NM2) <= ALPHA2).astype(float)
                pr = src.probe(s, rho, cn)
                if pr is not None:
                    sc, ppl, thr = pr
                    rep = C4.seqrep4(tok, src.texts(s, rho, cn))
                    d["fluent"] = fluent_flags(ppl, rep, cut_ppl, cut_rep)
                    d["probe"] = detect2.accept(sc, thr)
                    d["probe_FA"] = d["probe"] * d["fluent"]
                    d["exact_FA"] = d["acc"] * d["fluent"]
                if is_forgery(cn):
                    d["cos"] = float(src.cos(s, rho, cn))
                per.setdefault(cn, {})[s] = d
            sa2, thr = src.a2_probe(s, rho)
            pa2 = detect2.accept(sa2, thr)
            ea2 = (pm[s][src.a2] <= ALPHA).astype(float)
            per.setdefault("_A2", {})[s] = {"both": pa2 * ea2, "either": np.maximum(pa2, ea2)}
        for cn in src.cond_names(rho):
            dd = [per[cn][s] for s in cal]
            e = {"acceptance": summ([x["acc"] for x in dd], rng),
                 "pooled4_detection_median": med([x["pool"] for x in dd]),
                 "p_le_0.05_median": med([(x["p"] <= 0.05).astype(float) for x in dd]),
                 "p_le_0.10_median": med([(x["p"] <= 0.10).astype(float) for x in dd])}
            if NM2 is not None:
                e["acceptance_0.001_median"] = med([x["acc2"] for x in dd])
            if "fluent" in dd[0]:
                e["exact_FA"] = summ([x["exact_FA"] for x in dd], rng)
                e["probe_acceptance_median"] = med([x["probe"] for x in dd])
                e["probe_FA_median"] = med([x["probe_FA"] for x in dd])
                e["both_acceptance_median"] = med([x["probe"] * x["acc"] for x in dd])
                e["either_acceptance_median"] = med([np.maximum(x["probe"], x["acc"]) for x in dd])
                e["fluent_share_median"] = med([x["fluent"] for x in dd])
            if is_forgery(cn):
                e["cos_to_key_per_key"] = [x["cos"] for x in dd]
                e["acceptance_per_key"] = [float(x["acc"].mean()) for x in dd]
            L[cn] = e
        L["A2_joint_fpr"] = {"both_median": med([per["_A2"][s]["both"] for s in cal]),
                             "either_median": med([per["_A2"][s]["either"] for s in cal])}
        tpr = L["oracle"]["acceptance"]["median"]
        L["P1"] = {"oracle_tpr_median": tpr, "min": P1_MIN / 100, "pass": tpr >= P1_MIN / 100}
        xs = [per["oracle"][s]["acc"] for s in cal]
        ys = [per["oracle"][s]["probe"] for s in cal]
        dmed = float(np.median([x.mean() - y.mean() for x, y in zip(xs, ys)]))
        ci = paired_boot(xs, ys, rng)
        L["E1"] = {"median_diff_exact_minus_probe": dmed, "ci95": ci,
                   "verdict": "exact test more powerful" if ci[0] > 0 else
                   ("exact test less powerful" if ci[1] < 0 else "no clear difference")}
        orc, rnd = L["oracle"]["exact_FA"], L["random"]["exact_FA"]
        L["X3_fluent_generic_steering_suffices"] = rnd["median"] >= 0.5 * orc["median"]
        L["X1_bar"] = 0.5 * orc["median"]
        if rho in LATE:
            L["X1"] = x1_verdict(L, "v04", orc, rnd) if L["P1"]["pass"] else "level fails P1 (descriptive only)"
            L["X1_form_v03"] = x1_verdict(L, "v03", orc, rnd)
        L["X1_form_v02"] = x1_verdict(L, "v02", orc, rnd)
        out["levels"][str(rho)] = L
    return out


def analyse(src, tok):
    Ff = src.feats(src.ref)
    ref = reference(*Ff)
    NM, NM2 = PP.null_matrix(), null_keys_big()
    return {"primary": PRIMARY, "M": int(NM.shape[0]), "M2": int(NM2.shape[0]), "alpha": ALPHA, "alpha2": ALPHA2,
            "boot_seed": BOOT_SEED, "boot_B": R4.BOOT_B,
            PRIMARY: analyse_stat(PRIMARY, src, tok, ref, NM, NM2, BOOT_SEED),
            SECONDARY: analyse_stat(SECONDARY, src, tok, ref, NM, None, BOOT_SEED)}


REQUIRED_LEVEL_FIELDS = ["oracle", "E", "random", "A2_joint_fpr", "P1", "E1", "X3_fluent_generic_steering_suffices",
                         "X1_bar", "X1_form_v02"]
REQUIRED_LATE_FIELDS = ["X1", "X1_form_v03"]
REQUIRED_COND_FIELDS = ["acceptance", "pooled4_detection_median", "p_le_0.05_median", "p_le_0.10_median"]
REQUIRED_PROBED_FIELDS = ["exact_FA", "probe_acceptance_median", "probe_FA_median", "both_acceptance_median",
                          "either_acceptance_median", "fluent_share_median"]


def missing_fields(res, levels, cond_fn):
    """Every result field that protocol §7 and §8 list (lesson from Study 1: assert secondaries too)."""
    miss = [k for k in ("primary", "M", "M2", PRIMARY, SECONDARY) if k not in res]
    for c in (PRIMARY, SECONDARY):
        R = res.get(c, {})
        miss += [f"{c}.{k}" for k in ("G1", "G2", "H1", "levels") if k not in R]
        if c == PRIMARY and "alpha_0.001" not in R:
            miss.append(f"{c}.alpha_0.001")
        for rho in levels:
            L = R.get("levels", {}).get(str(rho), {})
            need = REQUIRED_LEVEL_FIELDS + (REQUIRED_LATE_FIELDS if rho in LATE else [])
            miss += [f"{c}.{rho}.{k}" for k in need if k not in L]
            for cn in cond_fn(rho):
                e = L.get(cn, {})
                need = REQUIRED_COND_FIELDS + ([] if cn == "E" else REQUIRED_PROBED_FIELDS)
                need += ["acceptance_0.001_median"] if c == PRIMARY else []
                need += ["cos_to_key_per_key", "acceptance_per_key"] if is_forgery(cn) else []
                miss += [f"{c}.{rho}.{cn}.{k}" for k in need if k not in e]
    return miss
