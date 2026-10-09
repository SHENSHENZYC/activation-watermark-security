"""Study 2 runner (STUDY2_PROTOCOL_v0.1.md). Refuses to run unless outputs/study2_v0.1/PRE_RUN_LOCK.json matches the
protocol, the code and every reused file (except in --dry mode, which uses tuning-key stand-ins in a scratch folder).

Phases (each checkpointed; re-running resumes):
  para     bars; Qwen paraphrases (3,200 genuine + 1,000 null); Phi paraphrases (1,600 genuine + 1,000 null)
           -- needs a freshly restarted Mac with other apps closed (Phi)
  edits    the attacker's gradient scale at every needed layer; E-true, E-est, E-rand (float32 editor)
  score    S4 gradients, quality and probe scores for every scrubbed set; length-matched controls
  analyse  gates, rules and secondaries -> outputs/study2_v0.1/results.json
Run: .venv/bin/python -u research/study2/run_s2.py --phase para|edits|score|analyse [--dry SCRATCH]
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common_s2 as S  # noqa: E402
from common_s2 import SC, PP, C2, core  # noqa: E402

ROOT = S.ROOT
LOCK = S.OUT / "PRE_RUN_LOCK.json"
CODE = [HERE / "common_s2.py", HERE / "run_s2.py", HERE / "validate_s2.py", ROOT / "research/study2_pilot/scrub_core.py",
        ROOT / "research/study3/common_s3.py", ROOT / "research/study3_pilot/power_pilot.py",
        ROOT / "research/study1_v04/common4.py", ROOT / "research/study1_v04/attack4.py",
        ROOT / "research/study1_v04/run_v04.py", ROOT / "research/study1_v03/common3.py",
        ROOT / "research/study1_v02/common.py", ROOT / "research/study1_v02/detect2.py", ROOT / "research/study1/core.py"]
DATA, OUT, SRC = S.DATA, S.OUT, None


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def log(msg):
    print(f"{msg} ({now()})", flush=True)


def check_lock():
    if not LOCK.exists():
        sys.exit("refused: no PRE_RUN_LOCK.json (the protocol must be locked before outcomes)")
    L = json.loads(LOCK.read_text())
    bad = [] if sha(S.PROTOCOL) == L["protocol_sha256"] else ["protocol"]
    bad += [p.name for p in CODE if L["code_sha256"].get(p.name) != sha(p)]
    bad += [str(p) for p in S.Src().reused_files() if L["reused_sha256"].get(str(p.relative_to(ROOT))) != sha(p)]
    if bad:
        sys.exit(f"refused: hashes differ from the lock: {bad[:10]}")
    return L


def T(path):
    return DATA / path


# ---------------------------------------------------------------- phase para
def bars_step(src):
    f = T("bars.json")
    if f.exists():
        return S.load(f)
    SC.free()
    tok, model = SC.load_base()
    E = SC.Embedder()
    nt, npr, nh = src.null()
    ct, cp, ch = src.attacker()
    qh, qm = SC.raw_quality(tok, model, E, npr, nh), SC.raw_quality(tok, model, E, npr, nt)
    pairs = SC.cosines(E, nt, nh)
    qch, cpairs = SC.raw_quality(tok, model, E, cp, ch), SC.cosines(E, ct, ch)
    out = {"A": SC.bars(qh, pairs), "C": SC.bars(qch, cpairs), "A_model_p95": SC.bars(qm, pairs),
           "A_human_median": SC.bars(qh, pairs, q=0.5), "orig": {}, "null_orig": {k: np.asarray(v).tolist() for k, v in qm.items()}}
    for s in src.keys:
        for rho in src.levels:
            q = SC.raw_quality(tok, model, E, src.prompts(s, rho), src.genuine(s, rho))
            out["orig"][S.tag(s, rho)] = {k: np.asarray(v).tolist() for k, v in q.items()}
    S.save(f, out)
    del model, E, tok
    SC.free()
    log("bars done")
    return out


def gen_set(src, m):
    """The genuine texts a paraphraser scrubs, in a fixed order, with (key, level, index) labels."""
    n = S.N_GEN if m == "qwen" else S.N_PHI
    items = []
    for s in src.keys:
        for rho in src.levels:
            g, pr = src.genuine(s, rho), src.prompts(s, rho)
            items += [(s, rho, j, g[j], pr[j]) for j in range(min(n, len(g)))]
    return items


def para_phase(src):
    bars = bars_step(src)
    for m in S.MODELS:
        for si, name in ((0, "gen"), (1, "null")):
            f = T(f"para_{m}_{name}.json")
            if f.exists():
                continue
            if name == "gen":
                items = gen_set(src, m)
                texts, prompts = [x[3] for x in items], [x[4] for x in items]
                oq = {k: [bars["orig"][S.tag(x[0], x[1])][k][x[2]] for x in items] for k in ("ppl", "rep", "len")}
                labels = [[x[0], x[1], x[2]] for x in items]
            else:
                texts, prompts, _ = src.null()
                oq = {k: bars["null_orig"][k] for k in ("ppl", "rep", "len")}
                labels = None
            res = S.paraphrase_with_checks(m, texts, prompts, oq, bars["C"], si, DATA, log=log)
            res["labels"] = labels
            S.save(f, res)
            log(f"para {m} {name} done")
    log("phase para complete")


# ---------------------------------------------------------------- phase edits
def edits_phase(src):
    ct, _, _ = src.attacker()
    layers = sorted({14} | {src.estimate(s, rho)[0] for s in src.keys for rho in src.levels})
    SC.free()
    tok, m16 = SC.load_base()
    for l in layers:
        f = T(f"att_sd_l{l}.npy")
        if not f.exists():
            G = np.stack([SC.grad_at_layer(tok, m16, t, l) for t in ct])
            np.save(f, np.maximum(G.std(0, ddof=1), 1e-12))
            log(f"attacker scale at layer {l} done")
    del m16, tok
    SC.free()
    tok, m32 = SC.load_base_fp32()
    ed = SC.Editor(tok, m32)
    for arm in S.ARMS:
        for s in src.keys:
            for rho in src.levels:
                f = T(f"edits_{arm}_{S.tag(s, rho)}.json")
                if f.exists():
                    continue
                texts = src.genuine(s, rho)
                t0 = time.time()
                if arm == "rand":
                    rng = np.random.default_rng(S.SEED_RAND + 7919 * src.keys.index(s) + 104729 * src.levels.index(rho))
                    out = ed.run(texts, "random", rng=rng, round_frac=S.ROUND, budgets=S.BUDGETS)
                    meta = {}
                else:
                    l, v = (14, src.key(s, rho)) if arm == "true" else src.estimate(s, rho)[:2]
                    out = ed.run(texts, "guided", direction=v / np.load(T(f"att_sd_l{l}.npy")), layer=l,
                                 round_frac=S.ROUND, budgets=S.BUDGETS)
                    meta = {"layer": l}
                S.save(f, {"recs": out, "edit_s": time.time() - t0, "n": len(texts), **meta})
            log(f"edits {arm} key {s} done")
    del ed, m32, tok
    SC.free()
    log("phase edits complete")


# ---------------------------------------------------------------- phase score
def score_sets(src):
    """name -> (texts, prompts, originals or None, labels [(key, level, index)], probe True/False)."""
    sets = {}
    for m in S.MODELS:
        P = S.load(T(f"para_{m}_gen.json"))
        items = gen_set(src, m)
        lab = [(x[0], x[1], x[2]) for x in items]
        o, pr = [x[3] for x in items], [x[4] for x in items]
        sets[f"para_{m}_gen"] = (S.kept_texts(P), pr, o, lab, True)
        diff = [i for i, a in enumerate(P["kept"]) if a != 0]
        sets[f"para1_{m}_gen"] = ([S.first_texts(P)[i] for i in diff], [pr[i] for i in diff], [o[i] for i in diff],
                                  [lab[i] for i in diff], False)
        kt = S.kept_texts(P)
        nz = [len(SC_tok_ids(z)) for z in kt]
        trunc = [SC_decode(SC_tok_ids(x)[:n]) for x, n in zip(o, nz)]
        sets[f"lm_{m}_gen"] = (trunc, None, None, lab, False)
        Pn = S.load(T(f"para_{m}_null.json"))
        nt, npr, _ = src.null()
        sets[f"para_{m}_null"] = (S.kept_texts(Pn), npr, nt, [(None, None, j) for j in range(len(nt))], "all")
    for arm in S.ARMS:
        for f in S.BUDGETS:
            texts, pr, o, lab = [], [], [], []
            for s in src.keys:
                for rho in src.levels:
                    E = S.load(T(f"edits_{arm}_{S.tag(s, rho)}.json"))["recs"]
                    g, p_ = src.genuine(s, rho), src.prompts(s, rho)
                    texts += [r["texts"][str(f)] for r in E]
                    pr += p_[:len(E)]
                    o += g[:len(E)]
                    lab += [(s, rho, j) for j in range(len(E))]
            sets[f"edit_{arm}_{f}"] = (texts, pr, o, lab, True)
    return sets


_TOK = None


def SC_tok_ids(text):
    return _TOK(text, add_special_tokens=False)["input_ids"][:core.NEW_TOKENS]


def SC_decode(ids):
    return _TOK.decode(ids, skip_special_tokens=True)


def score_phase(src):
    global _TOK
    SC.free()
    tok, model = SC.load_base()
    _TOK = tok
    E = SC.Embedder()
    dev = SC.dev()
    sets = score_sets(src)
    rates = {"s4": [0.0, 0], "q": [0.0, 0], "probe": [0.0, 0]}
    probes = {}
    for name, (texts, prompts, origs, lab, probe) in sets.items():
        fg, fq, fp = T(f"G_{name}.npy"), T(f"Q_{name}.json"), T(f"probe_{name}.json")
        if not fg.exists():
            t0 = time.time()
            np.save(fg, SC.Owner.grads(tok, model, texts) if texts else np.zeros((0, SC.D)))
            rates["s4"][0] += time.time() - t0
            rates["s4"][1] += len(texts)
        if origs is not None and not fq.exists():
            t0 = time.time()
            q = SC.raw_quality(tok, model, E, prompts, texts, origs) if texts else {}
            rates["q"][0] += time.time() - t0
            rates["q"][1] += len(texts)
            S.save(fq, {k: np.asarray(v).tolist() for k, v in q.items()})
        if probe and not fp.exists():
            t0 = time.time()
            out = {}
            pairs = [(s_, r_) for s_ in src.keys for r_ in src.levels]
            if probe == "all":
                X, lens = C2.layer_tokens(tok, model, texts)
                for s_, r_ in pairs:
                    if (s_, r_) not in probes:
                        probes[(s_, r_)] = src.probe(s_, r_, dev)[:2]
                    net, thr = probes[(s_, r_)]
                    out[S.tag(s_, r_)] = {"scores": S.detect2.score(net, X, lens, dev).tolist(), "threshold": thr}
                del X
            else:
                for s_, r_ in pairs:
                    idx = [i for i, x in enumerate(lab) if x[0] == s_ and x[1] == r_]
                    if not idx:
                        continue
                    if (s_, r_) not in probes:
                        probes[(s_, r_)] = src.probe(s_, r_, dev)[:2]
                    net, thr = probes[(s_, r_)]
                    X, lens = C2.layer_tokens(tok, model, [texts[i] for i in idx])
                    out[S.tag(s_, r_)] = {"idx": idx, "scores": S.detect2.score(net, X, lens, dev).tolist(), "threshold": thr}
                    del X
            S.save(fp, out)
            rates["probe"][0] += time.time() - t0
            rates["probe"][1] += len(texts)
        log(f"scored {name}: {len(texts)} texts")
    S.save(T("score_rates.json"), {k: (v[0] / v[1] if v[1] else None) for k, v in rates.items()})
    del model, E, tok
    SC.free()
    log("phase score complete")


# ---------------------------------------------------------------- analysis
def analyse(src):
    rng = np.random.default_rng(S.BOOT_SEED)
    own = S.Owner(src)
    bars = S.load(T("bars.json"))
    keys, levels = src.keys, src.levels
    kd = {s: src.key_dir(s) for s in keys}
    res = {"protocol_sha256": sha(S.PROTOCOL), "dry": src.dry, "bars": {k: bars[k] for k in ("A", "C", "A_model_p95", "A_human_median")}}

    # detection before (Study 3's features); P1
    p0 = {(s, rho): own.p(src.orig_G(s, rho), kd[s]) for s in keys for rho in levels}
    oq = {S.tag(s, rho): {k: np.asarray(v) for k, v in bars["orig"][S.tag(s, rho)].items()} for s in keys for rho in levels}

    # calibration after paraphrase (G1, G2) and its secondaries
    cal, res["calibration"] = {}, {}
    fresh = SC.unit(np.stack([core.make_key(S.FRESH0 + j, SC.D, 1.0).numpy() for j in range(S.N_FRESH)]))
    for m in S.MODELS:
        G = np.load(T(f"G_para_{m}_null.npy"))
        X = own.X(G)
        N = X @ own.nm.T
        fpr = {s: 100 * float((PP.pvalues(X @ kd[s], N) <= S.ALPHA).mean()) for s in keys}
        pooled = float(np.mean(list(fpr.values())))
        ok = [s for s in keys if fpr[s] <= S.G2_MAX]
        cal[m] = ok
        fk = np.array([100 * float((PP.pvalues(X @ fresh[j], N) <= S.ALPHA).mean()) for j in range(S.N_FRESH)])
        pr = S.load(T(f"probe_para_{m}_null.json"))
        a2 = slice(len(G) // 2, len(G))
        probe_fpr = {t: 100 * float((np.asarray(v["scores"])[a2] > v["threshold"]).mean()) for t, v in pr.items()}
        res["calibration"][m] = {
            "G1": {"pooled_fpr_pct": pooled, "range": list(S.G1_RANGE), "pass": S.G1_RANGE[0] <= pooled <= S.G1_RANGE[1]},
            "G2": {"per_key_fpr_pct": {str(s): fpr[s] for s in keys}, "calibrated": ok, "n_calibrated": len(ok),
                   "verdicts_made": len(ok) >= S.MIN_CAL},
            "fresh_keys": {"mean_fpr_pct": float(fk.mean()), "share_above_3pct": float((fk > 3).mean()),
                           "max_fpr_pct": float(fk.max())},
            "probe_fpr_on_paraphrased_A2_pct": {"median": float(np.median(list(probe_fpr.values()))), "per_key_level": probe_fpr}}

    def method_rows(name, scope_keys, comp=None):
        """Per text: p, success flags under the three bars, quality conditions; grouped by (key, level)."""
        G, Q = np.load(T(f"G_{name}.npy")), {k: np.asarray(v) for k, v in S.load(T(f"Q_{name}.json")).items()}
        lab = sets_lab[name]
        p = np.array([own.p(G[i:i + 1], kd[l[0]])[0] for i, l in enumerate(lab)])
        o = {k: np.array([oq[S.tag(l[0], l[1])][k][l[2]] for l in lab]) for k in ("ppl", "rep", "len")}
        conds = {b: SC.conditions(o, Q, bars[b]) for b in ("A", "A_model_p95", "A_human_median")}
        return {"p": p, "c": conds["A"], "succ": {b: (p > S.ALPHA) & conds[b]["all"] for b in conds}, "lab": lab, "Q": Q, "o": o}

    meta = score_sets_meta(src)
    sets_lab = {name: v[3] for name, v in meta.items()}

    res["levels"] = {}
    rows = {}
    for name in [f"para_{m}_gen" for m in S.MODELS] + [f"edit_{a}_{f}" for a in S.ARMS for f in S.BUDGETS]:
        rows[name] = method_rows(name, keys)
    for m in S.MODELS:                       # first attempts: the kept rows, with the retried texts replaced
        k, d = rows[f"para_{m}_gen"], f"para1_{m}_gen"
        P = S.load(T(f"para_{m}_gen.json"))
        diff = [i for i, a in enumerate(P["kept"]) if a != 0]
        r1 = {"p": k["p"].copy(), "c": {c: v.copy() for c, v in k["c"].items()},
              "succ": {b: v.copy() for b, v in k["succ"].items()}, "lab": k["lab"],
              "Q": {q: v.astype(float).copy() for q, v in k["Q"].items()}, "o": k["o"]}
        if diff:
            dr = method_rows(d, keys)
            for j, i in enumerate(diff):
                r1["p"][i] = dr["p"][j]
                for c in r1["c"]:
                    r1["c"][c][i] = dr["c"][c][j]
                for b in r1["succ"]:
                    r1["succ"][b][i] = dr["succ"][b][j]
                for q in r1["Q"]:
                    r1["Q"][q][i] = dr["Q"][q][j]
        rows[d] = r1
    for rho in levels:
        L = {}
        sel_keys = keys
        before = {s: p0[(s, rho)] <= S.ALPHA for s in keys}
        d0 = S.summ({s: before[s] for s in keys}, keys, rng)
        L["P1"] = {"detected_before": d0, "pass": d0["median"] >= S.P1_MIN}

        def grp(name, flag, ks):
            r = rows[name]
            return {s: np.asarray([f for f, l in zip(flag, r["lab"]) if l[0] == s and l[1] == rho], dtype=float) for s in ks}

        def describe(name, ks):
            r = rows[name]
            out = {"success": S.summ(grp(name, r["succ"]["A"], ks), ks, rng),
                   "detected_after": S.summ(grp(name, r["p"] <= S.ALPHA, ks), ks, rng),
                   "success_stricter": {b: S.summ(grp(name, r["succ"][b], ks), ks, rng)["median"] for b in ("A_model_p95", "A_human_median")},
                   "pass": {c: S.summ(grp(name, r["c"][c], ks), ks, rng)["median"] for c in ("ppl", "rep", "len", "cos", "all")}}
            sel = [i for i, l in enumerate(r["lab"]) if l[1] == rho and l[0] in ks]
            if sel:
                out["median_ppl_ratio"] = float(np.median(r["Q"]["ppl"][sel] / r["o"]["ppl"][sel]))
                out["median_len_ratio"] = float(np.median(r["Q"]["len"][sel] / np.minimum(r["o"]["len"][sel], core.NEW_TOKENS)))
                out["median_cos"] = float(np.median(r["Q"]["cos"][sel]))
            return out

        # S1: paraphrase vs the originals' miss rate (same texts)
        for m in S.MODELS:
            ks = cal[m]
            name = f"para_{m}_gen"
            n = S.N_GEN if m == "qwen" else S.N_PHI
            miss = {s: (p0[(s, rho)][:n] > S.ALPHA).astype(float) for s in ks}
            comp = S.summ(miss, ks, rng)
            d = describe(name, ks)
            d["first_attempt"] = describe(f"para1_{m}_gen", ks)
            v = S.verdict(d["success"], comp) if (L["P1"]["pass"] and len(ks) >= S.MIN_CAL) else "not made"
            L[f"S1_{m}"] = {"verdict": v, "keys_success_ge_50": d["success"]["keys_ge_50"], "originals_miss": comp, **d}
        # S2 and C1: edits at 5% vs E-rand at 5%; curves at 2% and 10%
        for f in S.BUDGETS:
            for a in S.ARMS:
                L[f"E-{a} {f}"] = describe(f"edit_{a}_{f}", keys)
        rand5 = L[f"E-rand {S.PRIMARY}"]["success"]
        for a in ("true", "est"):
            d = L[f"E-{a} {S.PRIMARY}"]
            L[f"S2_{a}"] = {"verdict": S.verdict(d["success"], rand5) if L["P1"]["pass"] else "not made",
                            "keys_success_ge_50": d["success"]["keys_ge_50"]}
        pe = grp(f"edit_est_{S.PRIMARY}", rows[f"edit_est_{S.PRIMARY}"]["succ"]["A"], keys)
        pr_ = grp(f"edit_rand_{S.PRIMARY}", rows[f"edit_rand_{S.PRIMARY}"]["succ"]["A"], keys)
        c1 = S.boot_paired_diff(pe, pr_, keys, rng)
        L["C1"] = {**c1, "verdict": S.c1_verdict(c1) if L["P1"]["pass"] else "not made"}
        res["levels"][str(rho)] = L

    # secondaries needing per-set data
    sec = {"length_matched": {}, "probe": {}, "alpha_0.001": {}, "pooled_4": {}, "key_leakage": {}}
    for m in S.MODELS:
        Glm = np.load(T(f"G_lm_{m}_gen.npy"))
        lab = sets_lab[f"lm_{m}_gen"]
        plm = np.array([own.p(Glm[i:i + 1], kd[l[0]])[0] for i, l in enumerate(lab)])
        sec["length_matched"][m] = {str(rho): float(100 * np.mean([pp <= S.ALPHA for pp, l in zip(plm, lab) if l[1] == rho]))
                                    for rho in levels}
    for name in [f"para_{m}_gen" for m in S.MODELS] + [f"edit_{a}_{f}" for a in S.ARMS for f in S.BUDGETS]:
        pr = S.load(T(f"probe_{name}.json"))
        acc = {t: float(100 * np.mean(np.asarray(v["scores"]) > v["threshold"])) for t, v in pr.items()}
        sec["probe"][name] = {str(rho): float(np.median([acc[S.tag(s, rho)] for s in keys if S.tag(s, rho) in acc])) for rho in levels}
    for name in [f"para_{m}_gen" for m in S.MODELS] + [f"edit_{a}_{S.PRIMARY}" for a in S.ARMS]:
        G = np.load(T(f"G_{name}.npy"))
        lab = sets_lab[name]
        det = {}
        pooled = {}
        for rho in levels:
            per, perp = [], []
            for s in keys:
                idx = [i for i, l in enumerate(lab) if l[0] == s and l[1] == rho]
                if not idx:
                    continue
                per.append(100 * float((own.p_big(G[idx], kd[s]) <= S.ALPHA2).mean()))
                if len(idx) >= S.POOL:
                    perp.append(100 * float((S.S3.pooled_pv(own.X(G[idx]), kd[s], own.nm) <= S.ALPHA).mean()))
            det[str(rho)] = float(np.median(per))
            pooled[str(rho)] = float(np.median(perp)) if perp else None
        sec["alpha_0.001"][name], sec["pooled_4"][name] = det, pooled
    xs, ys = [], []
    for s in keys:
        for rho in levels:
            r = rows[f"edit_est_{S.PRIMARY}"]
            v = [f for f, l in zip(r["succ"]["A"], r["lab"]) if l[0] == s and l[1] == rho]
            xs.append(src.estimate(s, rho)[2])
            ys.append(float(np.mean(v)))
    from scipy.stats import spearmanr
    sec["key_leakage"] = {"spearman_success_vs_cos": float(spearmanr(xs, ys).statistic) if len(set(xs)) > 1 else None,
                          "per_key_level": [{"cos": x, "success": y} for x, y in zip(xs, ys)]}
    sec["paraphrase_attempts"] = {}
    for m in S.MODELS:
        P = S.load(T(f"para_{m}_gen.json"))
        sec["paraphrase_attempts"][m] = {"used": {str(a + 1): int(sum(k == a for k in P["kept"])) for a in range(SC.MAX_ATTEMPTS)},
                                         "kept_failing_attacker_check": int(sum(P["attempts"][a][i]["n_fail_attacker"] > 0
                                                                                for i, a in enumerate(P["kept"])))}
    sec["edits"] = {}
    for a in S.ARMS:
        recs = [r for s in keys for rho in levels for r in S.load(T(f"edits_{a}_{S.tag(s, rho)}.json"))["recs"]]
        sec["edits"][a] = {"stalled": int(sum(r["stalled_at"] is not None for r in recs)),
                           "median_drift": {str(f): float(np.median([r["drift"][str(f)] for r in recs])) for f in S.BUDGETS}}
        if a != "rand":
            sec["edits"][a]["median_objective"] = {k: float(np.median([r["obj"][k] for r in recs])) for k in ["0"] + [str(f) for f in S.BUDGETS]}
    res["secondary"] = sec
    # samples
    res["samples"] = []
    for s in keys[:2]:
        rho = 0.5 if 0.5 in levels else levels[0]
        smp = {"key": s, "rho": rho, "original": src.genuine(s, rho)[0], "p_original": float(p0[(s, rho)][0])}
        for name in [f"para_{m}_gen" for m in S.MODELS] + [f"edit_{a}_{f}" for a in S.ARMS for f in (0.05, 0.10)]:
            r = rows[name]
            i = next((i for i, l in enumerate(r["lab"]) if l[0] == s and l[1] == rho and l[2] == 0), None)
            if i is not None:
                smp[name] = meta[name][0][i]
                smp["p_" + name] = float(r["p"][i])
        res["samples"].append(smp)
    OUT.mkdir(parents=True, exist_ok=True)
    S.save(OUT / "results.json", res)
    print(json.dumps({rho: {k: (v["verdict"] if isinstance(v, dict) and "verdict" in v else None)
                            for k, v in L.items() if k.startswith(("S1", "S2", "C1"))} for rho, L in res["levels"].items()},
                     indent=1))
    print("G1/G2:", {m: (c["G1"]["pass"], c["G2"]["n_calibrated"]) for m, c in res["calibration"].items()})


def score_sets_meta(src):
    global _TOK
    if _TOK is None:
        from transformers import AutoTokenizer
        _TOK = AutoTokenizer.from_pretrained(core.MODEL_ID, revision=core.REVISION)
    return score_sets(src)


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["para", "edits", "score", "analyse"], required=True)
    ap.add_argument("--dry", metavar="SCRATCH", help="tuning-key stand-ins in a scratch folder (no lock needed)")
    a = ap.parse_args()
    if a.dry:
        import validate_s2 as V
        SRC = V.DrySrc()
        DATA = Path(a.dry) / "data"
        OUT = Path(a.dry) / "out"
        S.DATA, S.OUT = DATA, OUT
        S.MODELS = V.DRY_MODELS
        S.N_GEN, S.N_PHI, S.N_NULL, S.N_REF_C = V.DRY_N
        S.MIN_CAL = 2                       # 4 tuning keys only: lets the S1 verdict path run in the smoke test
    else:
        check_lock()
        SRC = S.Src()
        assert not (OUT / "results.json").exists() or a.phase == "analyse", "outcomes exist"
    DATA.mkdir(parents=True, exist_ok=True)
    {"para": para_phase, "edits": edits_phase, "score": score_phase, "analyse": analyse}[a.phase](SRC)
