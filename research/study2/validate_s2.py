"""Study 2 input validation (STUDY2_PROTOCOL_v0.1.md §10), inputs only, and the tuning-key stand-in source for the
pipeline smoke test (run_s2.py --dry). No study-key text is paraphrased or edited, and no new statistic is computed
on any study-key text (check 3 reproduces Study 3's already-reported features).
Run: .venv/bin/python -u research/study2/validate_s2.py [--smoke-results SCRATCH/out/results.json]
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common_s2 as S  # noqa: E402
from common_s2 import SC, PP, C2, core  # noqa: E402

ROOT = S.ROOT
sys.path.insert(0, str(ROOT / "research" / "study2_pilot"))
sys.path.insert(0, str(ROOT / "research" / "repro"))
DRY_MODELS = ["qwen", "phi"]
DRY_N = (4, 2, 20, 20)                      # N_GEN, N_PHI, N_NULL, N_REF_C in the smoke test
CAL = ROOT / "research" / "repro" / "data" / "qwen"
TUNING = [9001, 9002, 9003, 9004]


class DrySrc(S.Src):
    """Tuning-key stand-ins for every study input (calibration v0.1 texts on pool T; their unwatermarked texts as the
    null set; stand-in estimates as in pilot v0.1, one at layer 10). Study probes of key 1001 stand in for the probe;
    their numbers carry no information."""
    dry = True
    keys, levels = TUNING, S.LEVELS

    def __init__(self):
        super().__init__()
        import repro_pilot as rp
        base = core.assign_pools()
        self._pT = {s: [u for u in rp.key_prompts(base, i)] for i, s in enumerate(TUNING)}
        self._G = {}

    def genuine(self, s, rho):
        return S.load(CAL / f"texts_calib_r{int(round(rho * 100)):03d}_k{s}.json")[:S.N_GEN]

    def prompts(self, s, rho):
        return [u["prompt"] for u in self._pT[s]][:S.N_GEN]

    def null(self):
        t, p, h = [], [], []
        for s in TUNING:
            k = S.N_NULL // len(TUNING)
            t += S.load(CAL / f"texts_van_k{s}.json")[:k]
            p += [u["prompt"] for u in self._pT[s]][:k]
            h += [u["human_continuation"] for u in self._pT[s]][:k]
        return t, p, h

    def key(self, s, rho):
        return PP.tuning_key(s, rho).astype(np.float64)

    def key_dir(self, s):
        return SC.unit(PP.tuning_key(s, 1.0).astype(np.float64))

    def estimate(self, s, rho):
        import scrub_pilot as P1
        v = P1.standin(s)
        return (10 if s == 9004 else 14), v, float(SC.unit(v) @ self.key_dir(s))

    def orig_G(self, s, rho):
        f = S.DATA / f"origG_{S.tag(s, rho)}.npy"
        if not f.exists():
            tok, model = SC.load_base()
            np.save(f, SC.Owner.grads(tok, model, self.genuine(s, rho)).astype(np.float32))
            del model, tok
            SC.free()
        return np.load(f)

    def probe(self, s, rho, dev):
        return super().probe(1001, rho, dev)

    def reused_files(self):
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke-results", help="results.json of the run_s2.py --dry smoke test")
    a = ap.parse_args()
    S.OUT.mkdir(parents=True, exist_ok=True)
    checks, t0 = {}, time.time()
    src = S.Src()
    files = src.reused_files()
    missing = [str(p) for p in files if not p.exists()]
    s3lock = json.loads((ROOT / "research/outputs/study3_v0.1/PRE_RUN_LOCK.json").read_text())
    s3hash = {}
    for k in ("reused_sha256", "reused_files_sha256", "study1_files_sha256"):
        s3hash.update(s3lock.get(k, {}) or {})
    sh = {str(p.relative_to(ROOT)): S.hashlib_sha(p) for p in files if p.exists()}
    agree = [k for k in sh if k in s3hash and s3hash[k] == sh[k]]
    disagree = [k for k in sh if k in s3hash and s3hash[k] != sh[k]]
    checks["1_reused_files"] = {"pass": not missing and not disagree and len(files) == 4 + 5 * 32,
                                "n_files": len(files), "missing": missing[:5], "agree_with_study3_lock": len(agree),
                                "disagree_with_study3_lock": disagree[:5]}

    # 2. bars recomputed with the Study 2 code equal the pilot's
    tok, model = SC.load_base()
    E = SC.Embedder()
    nt, npr, nh = src.null()
    ct, cp, ch = src.attacker()
    qh, qm = SC.raw_quality(tok, model, E, npr, nh), SC.raw_quality(tok, model, E, npr, nt)
    pairs = SC.cosines(E, nt, nh)
    qch, cpairs = SC.raw_quality(tok, model, E, cp, ch), SC.cosines(E, ct, ch)
    mine = {"A": SC.bars(qh, pairs), "C": SC.bars(qch, cpairs), "A_model_p95": SC.bars(qm, pairs),
            "A_human_median": SC.bars(qh, pairs, q=0.5)}
    pilot = json.loads((ROOT / "research/study2_pilot/data/bars.json").read_text())
    diff = max(abs(mine[b][k] - pilot[b][k]) for b in mine for k in mine[b])
    checks["2_bars_equal_pilot"] = {"pass": diff < 1e-9, "max_abs_diff": diff, "bars": mine}

    # 3. the S4 path reproduces Study 3's features and p-values (already-reported outcomes; no new statistic)
    own = S.Owner(src)
    rep = {}
    for s, rho in ((1001, 0.25), (1008, 0.70)):
        texts = src.genuine(s, rho)
        G = np.stack([PP.text_features(tok, model, t)[1] for t in texts]).astype(np.float32)
        G3 = src.orig_G(s, rho)
        p_new, p_old = own.p(G, src.key_dir(s)), own.p(G3, src.key_dir(s))
        rep[S.tag(s, rho)] = {"max_abs_G_diff": float(np.abs(G - G3).max()), "p_equal": bool(np.array_equal(p_new, p_old))}
    checks["3_s4_reproduces_study3"] = {"pass": all(v["max_abs_G_diff"] == 0.0 and v["p_equal"] for v in rep.values()),
                                        "per_key_level": rep}

    # 4. the attacker's estimates (E-est)
    est, ok = {}, True
    for s in src.keys:
        for rho in src.levels:
            l, v, c = src.estimate(s, rho)
            cc = float(SC.unit(v) @ SC.unit(src.key(s, rho)))
            nz = int((v != 0).sum())
            ok &= abs(cc - c) < 1e-5 and nz <= 4 and 0 <= l < 28
            est[S.tag(s, rho)] = {"layer": l, "cos": c, "nonzero": nz}
    checks["4_estimates"] = {"pass": bool(ok), "layers": sorted({e["layer"] for e in est.values()}),
                             "median_cos": float(np.median([e["cos"] for e in est.values()])), "per_key_level": est}
    del model, E, tok
    SC.free()

    # 5. the float32 editor against float32 autograd (an unwatermarked tuning text outside the pilot set)
    tok, m32 = SC.load_base_fp32()
    ed = SC.Editor(tok, m32)
    t = S.load(CAL / "texts_van_k9002.json")[30]
    enc = core._encode(tok, [t]).to(SC.dev())
    cm = enc.pop("content_mask")
    b = torch.zeros(1, 1, SC.D, device=SC.dev(), dtype=torch.float32, requires_grad=True)
    hd = m32.model.layers[SC.LAYER].register_forward_hook(PP._hook(b))
    try:
        ll = PP._loglik(m32, enc, cm)
        ll.backward()
    finally:
        hd.remove()
    g = b.grad[0, 0].detach().cpu().numpy().astype(np.float64)
    ids = tok(t, add_special_tokens=False)["input_ids"][:SC.NEW_TOKENS]
    rng = np.random.default_rng(5)
    fd, au = [], []
    for _ in range(8):
        u = rng.normal(size=SC.D)
        u /= np.linalg.norm(u)
        w = torch.tensor(u, dtype=torch.float32)
        H = ed._passes([ids, ids], [SC.S_FD * w, -SC.S_FD * w], SC.LAYER)
        fd.append(float(((ed._gather(H[0], ids)[0] - ed._gather(H[1], ids)[0]) / (2 * SC.S_FD)).sum()))
        au.append(float(g @ u))
    r = float(np.corrcoef(fd, au)[0, 1])
    checks["5_float32_editor"] = {"pass": r >= 0.999, "r": r}
    del ed, m32, tok
    SC.free()

    # 6. seeds disjoint from every earlier seed
    key_seeds_in_use = ({0, 1} | set(range(1001, 1017)) | set(range(5001, 5017)) | set(range(9001, 9005))
                        | {77_700_000 + j for j in range(9999)} | {88_800_000 + j for j in range(10000)}
                        | {66_600_000 + j for j in range(1000)} | {55_500_000 + j for j in range(1000)})
    fresh = {S.FRESH0 + j for j in range(S.N_FRESH)}
    sampling = {S.SEED_PARA, S.SEED_RAND}
    pilot_sampling = {20261000, 20261001, 20261002, 20261003, 20261011, 20261013}
    checks["6_seeds"] = {"pass": not (fresh & key_seeds_in_use) and not (sampling & pilot_sampling),
                         "fresh_key_seeds": [S.FRESH0, S.FRESH0 + S.N_FRESH - 1], "sampling": sorted(sampling)}

    # 7. the runner refuses without a lock
    import run_s2
    refused = False
    if not run_s2.LOCK.exists():
        try:
            run_s2.check_lock()
        except SystemExit:
            refused = True
    checks["7_refuses_without_lock"] = {"pass": refused}

    # 8. pipeline smoke test (run_s2.py --dry): every §7 and §8 field present
    if a.smoke_results:
        R = json.loads(Path(a.smoke_results).read_text())
        need_level = ["P1", "S1_qwen", "S1_phi", "S2_true", "S2_est", "C1"] + [f"E-{x} {f}" for x in S.ARMS for f in S.BUDGETS]
        need_sec = ["length_matched", "probe", "alpha_0.001", "pooled_4", "key_leakage", "paraphrase_attempts", "edits"]
        miss = [f"level {rho}: {k}" for rho, L in R["levels"].items() for k in need_level if k not in L]
        miss += [f"secondary: {k}" for k in need_sec if k not in R["secondary"]]
        miss += [f"calibration: {m}" for m in S.MODELS if m not in R["calibration"]]
        miss += [] if R["samples"] and all(f"para_{m}_gen" in R["samples"][0] for m in S.MODELS) else ["samples"]
        first = [rho for rho, L in R["levels"].items() if L["S1_qwen"].get("first_attempt") is None]
        checks["8_smoke_fields"] = {"pass": not miss, "missing": miss, "levels_without_first_attempt_rows": first,
                                    "note": "tuning-key stand-ins; numbers carry no information"}
    else:
        checks["8_smoke_fields"] = {"pass": False, "note": "run run_s2.py --dry first and pass --smoke-results"}

    # 9. timing (pilot v0.2's projection for the revised scope)
    proj = json.loads((ROOT / "research/outputs/study2_pilot_v0.2/results.json").read_text())["checks"]["I5prime"]
    checks["9_timing"] = {"pass": proj["projection"]["total_h"] <= 30.0, "projected_h": proj["projection"]["total_h"],
                          "budget_h": 30.0, "source": "outputs/study2_pilot_v0.2/results.json (I5′)"}
    res = {"protocol_sha256": S.hashlib_sha(S.PROTOCOL), "date_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
           "checks": checks, "all_pass": all(c["pass"] for c in checks.values()), "elapsed_s": time.time() - t0,
           "note": "inputs only; no study-key text paraphrased or edited; check 3 reproduces Study 3's features"}
    (S.OUT / "INPUT_VALIDATION.json").write_text(json.dumps(res, indent=2))
    for k, c in checks.items():
        print(k, "PASS" if c["pass"] else "FAIL", {x: y for x, y in c.items() if x not in ("per_key_level", "bars")})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


if __name__ == "__main__":
    main()
