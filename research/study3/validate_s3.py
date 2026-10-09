"""Study 3 input validation (STUDY3_PROTOCOL_v0.1.md §10). Inputs only: no Study 3 feature or statistic on any
study-key text. The smoke test runs the whole analysis on tuning-key texts (the pilot's features) with synthetic probe
scores and perplexities, to assert that every §7 and §8 field is produced.
Output: research/outputs/study3_v0.1/INPUT_VALIDATION.json
Run: .venv/bin/python research/study3/validate_s3.py
"""
import json
import shutil
import subprocess
import time
import zlib

import numpy as np
from scipy.stats import kstest

import common_s3 as S
import run_s3
from common_s3 import C4, PP, core, detect2

SYNTH_SEED0, FRESH_SEED0 = 88_800_000, 66_600_000   # the pilot's synthetic and diagnostic key seeds


def check_reused():
    fs = S.reused_files()
    missing = [str(p) for p in fs if not p.exists()]
    lock04 = json.loads((S.ROOT / "research/outputs/study1_v0.4/PRE_RUN_LOCK.json").read_text())
    known = {**lock04["reused_v02_sha256"], **lock04["reused_v03_sha256"]}
    over = [p for p in fs if p.name in known and not missing]
    equal = all(run_s3.sha(p) == known[p.name] for p in over)
    return {"pass": not missing and len(fs) == 562 and equal, "n_files": len(fs), "missing": missing[:5],
            "n_overlap_with_study1_locks": len(over), "overlap_with_study1_locks_equal": equal}


def check_null_keys():
    NM, NM2 = PP.null_matrix(), S.null_keys_big()
    null_seeds = {core.NULL_KEY_SEED * 100000 + j for j in range(S.M2)}
    other = PP.OTHER_SEEDS | {SYNTH_SEED0 + i for i in range(10000)} | {FRESH_SEED0 + i for i in range(1000)}
    same = bool(np.array_equal(NM2[:999], NM))
    return {"pass": same and not (null_seeds & other) and NM2.shape == (S.M2, S.D), "first_999_equal_primary": same,
            "seed_range": [min(null_seeds), max(null_seeds)]}, NM, NM2


def check_pvalues(NM, NM2):
    rng = np.random.default_rng(20260930)
    scales = np.exp(rng.normal(0, 1.5, S.D))
    true = PP.unit(np.stack([core.make_key(SYNTH_SEED0 + i, S.D, 1.0).numpy() for i in range(10000)]).astype(np.float64))
    out = {}
    for name, M, n_sim in (("M999", NM, 10000), ("M9999", NM2, 3000)):
        X0 = PP.unit(rng.normal(size=(n_sim, S.D)) * scales)
        p0 = PP.pvalues((X0 * true[:n_sim]).sum(1), X0 @ M.T)
        X1 = PP.unit(rng.normal(size=(1000, S.D)) + 5.0 * true[:1000])
        p1 = PP.pvalues((X1 * true[:1000]).sum(1), X1 @ M.T)
        grid = bool(np.allclose(p0 * (M.shape[0] + 1), np.round(p0 * (M.shape[0] + 1))))
        a = S.ALPHA if name == "M999" else S.ALPHA2
        ks = kstest(p0, "uniform").pvalue
        out[name] = {"ks_p": float(ks), "null_rate_at_alpha": float((p0 <= a).mean()), "alpha": a, "on_grid": grid,
                     "planted_detection": float((p1 <= a).mean()),
                     "pass": bool(ks > 0.01 and grid and (p1 <= a).mean() > 0.9)}
    return {"pass": all(v["pass"] for v in out.values()), **out}


def check_fluency_and_probe(tok):
    """v0.4's bars and the probe's acceptance and FA medians, reproduced exactly from the saved texts and scores."""
    R04 = json.loads((S.ROOT / "research/outputs/study1_v0.4/results.json").read_text())["levels"]
    src, bars_ok, rows = S.StudySrc(), True, []
    for rho in S.LATE:
        L = R04[str(rho)]
        cut = {}
        for i, s in enumerate(S.KEYS):
            _, ppl, _ = src.probe(s, rho, "oracle")
            cut[s] = (C4.cut(ppl), C4.cut(C4.seqrep4(tok, src.texts(s, rho, "oracle"))))
            bars_ok &= cut[s][0] == L["cut_per_key"]["ppl"][i] and cut[s][1] == L["cut_per_key"]["seqrep4"][i]
        for c in ["oracle", "random"] + [f"v0{v}_{r}_n{n}" for v in (2, 3, 4) for r in S.ROUTES for n in S.N34]:
            acc, fa = [], []
            for s in S.KEYS:
                sc, ppl, thr = src.probe(s, rho, c)
                a = detect2.accept(sc, thr)
                f = S.fluent_flags(ppl, C4.seqrep4(tok, src.texts(s, rho, c)), *cut[s])
                acc.append(a.mean())
                fa.append((a * f).mean())
            d_acc = abs(float(np.median(acc)) - L[c]["acceptance"]["median"])
            d_fa = abs(float(np.median(fa)) - L[c]["FA"]["median"])
            rows.append({"rho": rho, "cond": c, "d_acceptance": d_acc, "d_FA": d_fa})
    ok = bars_ok and all(r["d_acceptance"] < 1e-12 and r["d_FA"] < 1e-12 for r in rows)
    return {"pass": bool(ok), "bars_equal": bool(bars_ok), "n_conditions": len(rows),
            "max_abs_diff": max(max(r["d_acceptance"], r["d_FA"]) for r in rows)}


def check_texts(tok):
    h = S.human_texts()
    lens = [len(tok(x, add_special_tokens=False)["input_ids"]) for x in h]
    F = S.load(S.V02 / "S_F_van.json")
    P = S.C2.pools()
    ids_eval = {u["id"] for k in ("A1", "A2", "D", "E") for u in P[k]}
    return {"pass": len(h) == 1000 and min(lens) >= 4 and len(F) == 200 and not ({u["id"] for u in P["F"]} & ids_eval),
            "n_human": len(h), "human_min_tokens": int(min(lens)), "human_median_tokens": float(np.median(lens)),
            "F_disjoint_from_A_D_E": not ({u["id"] for u in P["F"]} & ids_eval)}


class SmokeSrc(S.StudySrc):
    """Tuning-key stand-in: every condition of key s is its own watermarked texts (the pilot's), 'random' is the next
    tuning key's texts, the nulls are the 400 unwatermarked tuning texts; probe scores and perplexities are synthetic."""
    keys = list(PP.TUNING)
    null_model, null_human, ref = "van", "van", "F"
    a2 = slice(200, 400)

    def __init__(self):
        self.src_key = {s: (PP.TUNING[(i + 1) % 4]) for i, s in enumerate(PP.TUNING)}

    def _rng(self, *a):
        return np.random.default_rng(zlib.crc32(repr(a).encode()))

    def _owner(self, s, c):
        return self.src_key[s] if c == "random" else s

    def feats(self, name):
        if name == "van":
            z = [np.load(PP.DATA / f"feats_van_k{s}.npz") for s in PP.TUNING]
            return np.concatenate([x["A"] for x in z]).astype(np.float32), np.concatenate([x["G"] for x in z])
        if name == "F":
            z = np.load(PP.DATA / "feats_F.npz")
            return z["A"].astype(np.float32), z["G"]
        s, rho, c = name.split("|")
        z = np.load(PP.DATA / f"feats_{PP.tag(float(rho))}_k{self._owner(int(s), c)}.npz")
        return z["A"].astype(np.float32), z["G"]

    def name(self, s, rho, c):
        return f"{s}|{rho}|{c}"

    def key(self, s):
        return PP.unit(PP.tuning_key(s, 1.0).astype(np.float64))

    def texts(self, s, rho, c):
        return S.load(PP.CAL / f"texts_calib_{PP.tag(rho)}_k{self._owner(s, c)}.json")

    def probe(self, s, rho, c):
        if c == "E":
            return None
        r = self._rng(s, rho, c)
        return list(r.uniform(size=100)), list(r.lognormal(2.0, 0.3, 100)), 0.5

    def cos(self, s, rho, c):
        return float(self._rng(s, rho, c, "cos").uniform(-0.1, 0.3))

    def a2_probe(self, s, rho):
        return list(self._rng(s, rho, "a2").uniform(size=200)), 0.99


def check_smoke(tok):
    t0 = time.time()
    res = S.analyse(SmokeSrc(), tok)
    miss = S.missing_fields(res, S.LEVELS, S.cond_names)
    scratch = S.HERE / "smoke_scratch"
    scratch.mkdir(exist_ok=True)
    (scratch / "results.json").write_text(json.dumps(res))
    shutil.rmtree(scratch)
    P = res[S.PRIMARY]
    return {"pass": not miss, "missing": miss[:10], "seconds": time.time() - t0, "scratch_deleted": not scratch.exists(),
            "note": "tuning texts with synthetic probe scores and perplexities; its verdicts carry no information",
            "smoke_G1_pooled_fpr_pct": P["G1"]["pooled_fpr_pct"],
            "smoke_oracle_tpr_median": {r: P["levels"][r]["P1"]["oracle_tpr_median"] for r in P["levels"]}}


def check_refusal():
    moved = run_s3.LOCK.exists()
    assert not moved, "a lock already exists; validation runs before the lock"
    r = subprocess.run([str(S.ROOT / ".venv/bin/python"), str(S.HERE / "run_s3.py"), "--phase", "R"], cwd=S.ROOT,
                       capture_output=True, text=True)
    return {"pass": r.returncode != 0 and "refused" in (r.stdout + r.stderr), "returncode": r.returncode}


def check_features_and_timing():
    tok, model = PP.load()
    Ftexts = S.load(S.V02 / "S_F_van.json")
    A, G, _ = zip(*(PP.text_features(tok, model, t) for t in Ftexts))
    z = np.load(PP.DATA / "feats_F.npz")
    dG = float(np.max(np.abs(np.stack(G) - z["G"])))
    dA = float(np.max(np.abs(np.stack(A) - z["A"])))
    t0 = time.time()
    for t in S.load(S.V02 / "S_A_van.json")[:10] + S.human_texts()[:10]:
        PP.text_features(tok, model, t)
    per = (time.time() - t0) / 20
    n = sum(len(t) for _, t in run_s3.feature_jobs())
    return ({"pass": dG == 0.0 and dA == 0.0, "max_abs_diff_G": dG, "max_abs_diff_A": dA},
            {"pass": per * n / 3600 <= 5.0, "s_per_text": per, "n_texts": n, "projected_h": per * n / 3600,
             "budget_h": 5.0})


def main():
    t_start = time.time()
    no_outcomes = (not S.DATA.exists() or not any(S.DATA.glob("*.npz"))) and not (S.OUT / "results.json").exists()
    assert no_outcomes, "outcomes exist"
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(core.MODEL_ID, revision=core.REVISION)
    checks = {"1_reused_files": check_reused()}
    nk, NM, NM2 = check_null_keys()
    checks["2_null_keys"] = nk
    checks["3_pvalues_synthetic"] = check_pvalues(NM, NM2)
    checks["4_fluency_bars_and_probe_reproduced"] = check_fluency_and_probe(tok)
    checks["5_texts_and_pools"] = check_texts(tok)
    checks["6_runner_refuses_without_lock"] = check_refusal()
    checks["7_smoke_test_tuning_texts"] = check_smoke(tok)
    checks["8_reference_features_equal_pilot"], checks["9_timing"] = check_features_and_timing()
    checks["10_no_outcomes"] = {"pass": (not S.DATA.exists() or not any(S.DATA.glob("*.npz")))
                                and not (S.OUT / "results.json").exists()}
    res = {"protocol": S.PROTOCOL.name, "protocol_sha256": run_s3.sha(S.PROTOCOL),
           "date_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
           "note": "inputs only; no Study 3 feature or statistic on any study-key text",
           "checks": checks, "all_pass": all(c["pass"] for c in checks.values()), "elapsed_s": time.time() - t_start}
    S.OUT.mkdir(parents=True, exist_ok=True)
    (S.OUT / "INPUT_VALIDATION.json").write_text(json.dumps(res, indent=2))
    for k, c in checks.items():
        print(k, "PASS" if c["pass"] else "FAIL", {x: y for x, y in c.items() if x not in ("pass",)})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


if __name__ == "__main__":
    main()
