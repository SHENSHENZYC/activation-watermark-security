"""Study 5 input validation (STUDY5_PROTOCOL_v0.1.md §12) and the tuning-key stand-in source for the smoke test.

Run: .venv/bin/python research/study5/validate_s5.py  -> outputs/study5_v0.1/INPUT_VALIDATION.json
(the smoke test runs `run_s5.py --dry --phase all` on DrySrc; about 20 minutes; it writes only under data/dry and
outputs/study5_v0.1/dry). No study-key text is generated, attacked or paraphrased.
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common_s5 as S  # noqa: E402
from common_s5 import KC, PP, SC, C2, core, ROOT  # noqa: E402
import run_s5 as R  # noqa: E402

CAL = ROOT / "research" / "repro" / "data" / "qwen"
PILOT = ROOT / "research" / "outputs" / "study5_pilot_v0.1"
THREAT = ROOT / "research" / "outputs" / "study5_threat_v0.1"
BUDGET_H = 30.0
VAL_SECRET = core.VALIDATION_KEY_SEED


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class DrySrc(S.Src):
    """Tuning-key stand-ins for the smoke test: keys 9001 and 9002 at rho = 0.50; the calibration texts play Study 1's
    observed and oracle texts and the van texts the random-key control; S4 features and a crude paraphrase stand-in are
    computed in prepare() (called from phase F, where the model is loaded). The scope is shrunk and every path moves
    under data/dry and outputs/study5_v0.1/dry. The numbers carry no information; only the fields matter."""
    dry = True
    keys, levels = [9001, 9002], [0.50]

    def __init__(self):
        S.DATA = S.HERE / "data" / "dry"
        S.OUT = S.OUT / "dry"
        S.KEYS, S.LEVELS = list(self.keys), list(self.levels)
        S.N_OBS = {"h1": 32, "h4": 32}
        S.N_GEN, S.N_FORGE, S.N_PARA = 8, 4, 4
        S.N_GRID, S.FORGE_N = [16, 32], [16, 32]
        S.CONTROL = {9001: 5001, 9002: 5002}
        super().__init__(data=S.DATA)
        self.prompts_D = [u["prompt"] for u in core.assign_pools()["T"][:S.N_GEN]]

    def _cal(self, s):
        return S.load(CAL / f"texts_calib_r050_k{s}.json")

    def fixed_texts(self, s, rho, c):
        if c == "obs":
            return self._cal(s)[8:40]
        if c == "oracle":
            return self._cal(s)[:8]
        return S.load(CAL / f"texts_van_k{s}.json")[:8]

    def obs_texts(self, s, rho):
        return self.fixed_texts(s, rho, "obs")

    def fixed_G(self, s, rho, c):
        return np.load(S.DATA / f"dry_G_{s}_{c}.npy")

    def fixed_ppl(self, s, rho, c):
        return S.load(S.DATA / f"dry_q_{s}_{c}.json")["ppl"]

    def orig_quality(self, s, rho):
        q = S.load(S.DATA / f"dry_q_{s}_oracle.json")
        return {k: np.asarray(q[k]) for k in ("ppl", "rep", "len")}

    def s2_para(self, s, rho):
        z = S.load(S.DATA / f"dry_para_{s}.json")
        return z["texts"], np.load(S.DATA / f"dry_G_{s}_para.npy"), {k: np.asarray(z["q"][k]) for k in ("ppl", "rep", "len", "cos")}

    def null_texts(self):
        return super().null_texts()[:40]

    def owner_ref_texts(self):
        return super().owner_ref_texts()[:20]

    def attacker_texts(self):
        return super().attacker_texts()[:20]

    def prepare(self, tok, model):
        if (S.DATA / "dry_prepared.json").exists():
            return
        E = SC.Embedder()
        for s in self.keys:
            for c in ("oracle", "random"):
                texts = self.fixed_texts(s, 0.50, c)
                np.save(S.DATA / f"dry_G_{s}_{c}.npy", R.s4_feats(tok, model, texts))
                S.save(S.DATA / f"dry_q_{s}_{c}.json", R.quality(tok, model, self.prompts_D, texts))
            orig = self.fixed_texts(s, 0.50, "oracle")
            para = [t.split(". ", 1)[-1] for t in orig]            # a crude stand-in for Study 2's paraphrases
            np.save(S.DATA / f"dry_G_{s}_para.npy", R.s4_feats(tok, model, para))
            q = SC.raw_quality(tok, model, E, self.prompts_D, para, orig)
            S.save(S.DATA / f"dry_para_{s}.json", {"texts": para, "q": {k: np.asarray(v).tolist() for k, v in q.items()}})
        del E
        S.save(S.DATA / "dry_prepared.json", {"ok": True})


def study_seeds():
    seeds = set()
    for ai in range(2):
        for li in range(2):
            for ki in range(8):
                for off in (10, 20, 30, 40, 41, 42):
                    seeds.add(S.seed(ai, li, ki, off))
    for li in range(2):
        for ki in range(8):
            for off in (40, 41, 42, 49):
                seeds.add(S.seed(9, li, ki, off))
        for off in range(12):
            seeds.add(S.seed(9, li, 95, off))
    return seeds


def main():
    t_start, checks = time.time(), {}
    out_real = ROOT / "research" / "outputs" / "study5_v0.1"
    out_real.mkdir(parents=True, exist_ok=True)
    src = S.Src()
    # 1. reused files present and hashed; equal to the Study 2 and Study 3 locks where recorded
    files = src.reused_files() + [PILOT / "VALIDATION.json", PILOT / "results.json", THREAT / "VALIDATION.json", THREAT / "results.json"]
    missing = [str(p) for p in files if not p.exists()]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in files if p.exists()}
    mism = []
    for lockf in (ROOT / "research/outputs/study2_v0.1/PRE_RUN_LOCK.json", ROOT / "research/outputs/study3_v0.1/PRE_RUN_LOCK.json"):
        rec = json.loads(lockf.read_text()).get("reused_sha256", {})
        mism += [k for k, h in rec.items() if k in hashes and hashes[k] != h]
    checks["1_reused_files"] = {"pass": not missing and not mism, "n_files": len(files), "missing": missing, "hash_mismatch_vs_locks": mism}

    # 2. the keyed hook with the code to be locked: I1 reproduction and I2 replay
    tok, model = PP.load()
    pools = core.assign_pools()
    prompts16 = [u["prompt"] for u in pools["T"][:16]]
    vec = __import__("torch").from_numpy(PP.tuning_key(9001, 0.50))
    a, _, _ = KC.generate(tok, model, prompts16, "fixed", vec=vec, seed=9001)
    b = core.generate(tok, model, prompts16, key=vec, layer=S.LAYER, seed=9001)
    stored = S.load(CAL / "texts_calib_r050_k9001.json")[:16]
    rep = {}
    for h in (1, 4):
        texts, ids, used = KC.generate(tok, model, src.prompts_B[:8], "keyed", h=h, secret=VAL_SECRET, rho=0.50, seed=S.seed(9, 9, 9, h))
        eq = []
        for idv, us in zip(ids, used):
            pos, ctx = KC.contexts(np.asarray(idv), h)
            idx, _ = KC.keys_from_hash(KC.context_hash([VAL_SECRET], ctx)[0])
            derived = [(int(p), tuple(int(i) for i in r)) for p, r in zip(pos, idx)]
            usedl = [(int(p), tuple(c)) for p, c in us]
            eq.append(derived[:len(usedl)] == usedl and len(derived) == len(usedl) + 1)
        rep[str(h)] = int(sum(eq))
    checks["2_hook_I1_I2"] = {"pass": a == b and a == stored and all(v == 8 for v in rep.values()),
                             "I1_equal_core_generate": int(sum(x == y for x, y in zip(a, b))), "I1_equal_stored": int(sum(x == y for x, y in zip(a, stored))),
                             "I2_replay_equal_of_8": rep}
    # 3. the keyed test's calibration with the validation secret on 100 pool A texts (the pilot's I3 covered 1,000 and 5 secrets)
    ro = np.load(PILOT.parent.parent / "study5_pilot" / "data" / "ref_owner.npz") if (ROOT / "research/study5_pilot/data/ref_owner.npz").exists() else None
    fpr = {}
    if ro is not None:
        owner = KC.KeyedOwner({"mu": ro["mu"], "sd": ro["sd"], "n_positions": int(ro["n"])})
        nt = src.null_texts()[:100]
        P = {1: [], 4: []}
        for t in nt:
            g, ids = KC.position_grads(tok, model, t)
            for h in (1, 4):
                P[h].append(owner.pvalue(g, ids, h, VAL_SECRET)[0])
        fpr = {str(h): 100 * float((np.array(P[h]) <= S.ALPHA).mean()) for h in (1, 4)}
    pil = json.loads((PILOT / "VALIDATION.json").read_text())["checks"]["8_I3_null_fpr"]
    checks["3_calibration"] = {"pass": pil["pass"] and all(v <= 5.0 for v in fpr.values()), "pilot_I3_fpr_pct": pil["fpr_pct"],
                               "validation_secret_100_texts_fpr_pct": fpr}
    del model, tok
    R.free()

    # 4. seeds disjoint from every earlier study (generation seeds in [8,000,000, 9,099,999]; earlier studies: Study 1 < 1.1M and 11/13/17,
    #    the calibration 9001-9004, the pilot 7,000,000+; paraphrase seed sets 20-21 against Study 2's 0-1 and the pilot's 5-12);
    #    the rotation forgeries use key index 95, so the range reaches 9,005,0xx
    seeds = study_seeds()
    checks["4_seeds"] = {"pass": min(seeds) >= 8_000_000 and max(seeds) < 9_100_000 and S.SET_IDX0 >= 20, "n_generation_seeds": len(seeds),
                         "range": [min(seeds), max(seeds)], "paraphrase_set_idx": [S.SET_IDX0, S.SET_IDX0 + 1]}

    # 5. the runner refuses without a lock
    refused = False
    try:
        R.check_lock()
    except (FileNotFoundError, AssertionError, KeyError):
        refused = True
    checks["5_refuses_without_lock"] = {"pass": refused or R.LOCK.exists(), "lock_exists": R.LOCK.exists()}

    # 6. no study-key outcome exists
    k_files = sorted(p.name for p in S.DATA.glob("K_*")) if S.DATA.exists() else []
    checks["6_no_outcomes"] = {"pass": not k_files and not (out_real / "results.json").exists(), "k_files": k_files[:5]}

    # 7. timing projection from the pilot's measured rates and this study's scope (decision 3; the fallbacks pre-set)
    pr = json.loads((PILOT / "results.json").read_text())["timing"]
    t_g, t_para = pr["measured_keyed_gen_s_per_text"], pr["measured_para_s_per_original"]
    t_f = pr["validation_projection"]["s_per_feature_text"]
    t_q, t_fix = 0.15, pr["validation_projection"]["s_per_fixed_generation"]

    def hours(obs_h4, n_para):
        kl = 16
        gens_keyed = kl * ((1024 + 100 + 300 + 100) + (obs_h4 + 100 + 300 + 100))
        gens_fixed = kl * 4 * 100 + 2 * 2 * 3 * 100
        feats = gens_keyed + kl * 2 * n_para + kl * 1024 + gens_fixed + 2200
        para = kl * 2 * n_para * t_para
        qual = (gens_keyed + gens_fixed + kl * 2 * n_para) * t_q
        return (gens_keyed * t_g + gens_fixed * t_fix + feats * t_f + para + qual) / 3600
    proj = {"full": hours(1024, 100), "fallback1_h4_n256": hours(256, 100), "fallback2_plus_para50": hours(256, 50),
            "chosen": hours(S.N_OBS["h4"], S.N_PARA)}
    checks["7_timing"] = {"pass": proj["chosen"] <= BUDGET_H, "projected_h": proj, "scope": {"N_OBS": S.N_OBS, "N_PARA": S.N_PARA},
                          "rates": {"keyed_gen_s": t_g, "fixed_gen_s": t_fix, "feature_s": t_f, "para_s": t_para, "quality_s": t_q}}

    # 8. the smoke test on tuning-key stand-ins: every phase runs and every field of §7-§10 is produced
    t0 = time.time()
    r = subprocess.run([sys.executable, "-u", str(HERE / "run_s5.py"), "--dry", "--phase", "all"], cwd=ROOT, capture_output=True, text=True)
    dry_res = out_real / "dry" / "results.json"
    miss = S.missing_fields(json.loads(dry_res.read_text()), [0.50], ["h1", "h4"]) if dry_res.exists() else ["results.json missing"]
    checks["8_smoke_test"] = {"pass": r.returncode == 0 and not miss, "returncode": r.returncode, "missing_fields": miss[:12],
                              "elapsed_s": time.time() - t0, "stderr_tail": r.stderr[-1500:] if r.returncode else ""}

    res = {"protocol_sha256": sha(S.PROTOCOL), "code_sha256": {p.name: sha(p) for p in R.CODE}, "reused_sha256": hashes,
           "date_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
           "note": "inputs only: unwatermarked texts, the validation secret, tuning-key stand-ins; no study-key text generated, attacked or paraphrased",
           "checks": checks, "all_pass": all(c["pass"] for c in checks.values()), "elapsed_s": time.time() - t_start}
    (out_real / "INPUT_VALIDATION.json").write_text(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    for k, c in checks.items():
        print(k, "PASS" if c["pass"] else "FAIL", {x: y for x, y in c.items() if x not in ("stderr_tail",)})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


if __name__ == "__main__":
    main()
