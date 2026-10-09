"""Study 5 defence pilot v0.1 (DEFENCE_PILOT_SPEC_v0.1.md): the keyed scheme's machinery on the tuning keys.

Phases:
  validate  inputs only (unwatermarked texts, the validation secret, synthetic data); writes the reference statistics
  run       keyed generation, features, quality, the attacker, forgeries, controls, paraphrase, the rotation test
            (refuses unless the spec is FIXED and committed); checkpointed per file
  analyse   readings -> outputs/study5_pilot_v0.1/{results.json, REPORT.md}
Run: .venv/bin/python research/study5_pilot/defence_pilot.py --phase validate|run|analyse
"""
import argparse
import gc
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import keyed_core as KC  # noqa: E402
from keyed_core import PP, C2, S3, core  # noqa: E402
sys.path.insert(0, str(ROOT / "research" / "study2_pilot"))
sys.path.insert(0, str(ROOT / "research" / "study2"))
import scrub_core as SC  # noqa: E402

SPEC = HERE / "DEFENCE_PILOT_SPEC_v0.1.md"
DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study5_pilot_v0.1"
CAL = ROOT / "research" / "repro" / "data" / "qwen"
V02 = ROOT / "research" / "study1_v02" / "data"
S3DATA = ROOT / "research" / "study3" / "data"
BARS = ROOT / "research" / "study2" / "data" / "bars.json"
S2PILOT = ROOT / "research" / "outputs" / "study2_pilot_v0.1" / "results.json"
TUNING = [9001, 9002, 9003, 9004]
CONTROL = [5001, 5002, 5003, 5004]
ARMS = {"h1": 1, "h4": 4}
RHO, RHO2 = 0.50, 0.35
N_OBS, N_GEN, N_PARA, N_FORGE, PER_KEY = 100, 100, 50, 20, 100
C_MIN, N_GRID = 16, [16, 64, 100]
VAL_SECRET = core.VALIDATION_KEY_SEED            # 0: validation only
SEED0 = 7_000_000
ALPHA = 0.01
PARA_S = 4.2                                      # Study 2 v0.1: Qwen paraphrase with retries and checks, per original
BUDGET_H = 30.0
LAYER, D, T_MAX = KC.LAYER, KC.D, KC.T_MAX


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text())


def save(p, obj):
    Path(p).write_text(json.dumps(obj))


def tag(rho):
    return f"r{int(round(rho * 100)):03d}"


def seed(arm_i, key_i, off):
    return SEED0 + 10_000 * arm_i + 1_000 * key_i + off


def free():
    gc.collect()
    torch.mps.empty_cache()


def inputs():
    pools = core.assign_pools()
    P = C2.pools()
    return {"T": [[u["prompt"] for u in pools["T"][i * PER_KEY:(i + 1) * PER_KEY]] for i in range(len(TUNING))],
            "B": C2.prompts(P["B"])[:N_OBS], "D": C2.prompts(P["D"])[:N_FORGE],
            "F": load(V02 / "S_F_van.json"), "A": load(V02 / "S_A_van.json"), "C": load(V02 / "S_C_ref.json")[:200],
            "C_norm": float(np.load(V02 / "S_C_ref_norms.npy")[LAYER])}


def cal_file(kind, rho, s):
    return CAL / f"{kind}_calib_{tag(rho)}_k{s}.json"


# ---------------------------------------------------------------- features (padded storage)
def feats_of(tok, model, texts):
    G = np.zeros((len(texts), T_MAX, D), dtype=np.float16)
    ids = -np.ones((len(texts), T_MAX), dtype=np.int64)
    lens = np.zeros(len(texts), dtype=np.int64)
    for i, t in enumerate(texts):
        g, idv = KC.position_grads(tok, model, t)
        G[i, :len(g)], ids[i, :len(idv)], lens[i] = g, idv, len(g)
    return {"G": G, "ids": ids, "lens": lens}


def feats_cached(tok, model, name, texts):
    f = DATA / f"{name}.npz"
    if not f.exists():
        z = feats_of(tok, model, texts)
        np.savez(f, **z, sha=hashlib.sha256(json.dumps(texts).encode()).hexdigest())
    z = np.load(f)
    return {"G": z["G"], "ids": z["ids"], "lens": z["lens"]}


def each(z):
    for i in range(len(z["lens"])):
        n = int(z["lens"][i])
        yield z["G"][i, :n].astype(np.float32), z["ids"][i, :n]


def roundtrip_share(gen_ids, z):
    """Mean over texts of the share of positions (over the shorter length) where the generated token ids equal the
    detector's re-encoded ids; 1.0 means the tokenisation round trip is exact."""
    out = []
    for i in range(len(gen_ids)):
        n = int(z["lens"][i])
        g = np.asarray(gen_ids[i][:n]); d = z["ids"][i, :n]
        m = min(len(g), len(d))
        out.append(float(np.mean(g[:m] == d[:m])) if m else 0.0)
    return float(np.mean(out))


def load_ref(name):
    z = np.load(DATA / f"{name}.npz")
    return {"mu": z["mu"], "sd": z["sd"], "n_positions": int(z["n"])}


def pvals(owner, z, h, secret):
    return np.array([owner.pvalue(G, ids, h, secret)[0] for G, ids in each(z)])


def quality(tok, model, prompts, texts):
    return {"ppl": SC.perplexities(tok, model, prompts, texts), "rep": SC.C4.seqrep4(tok, texts),
            "len": SC.n_tokens(tok, texts).tolist()}


# ---------------------------------------------------------------- guard
def spec_guard():
    txt = SPEC.read_text()
    if "**Status:** FIXED" not in txt:
        sys.exit("refused: the spec is not marked FIXED (Yichen's approval comes first)")
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(SPEC), str(Path(__file__)), str(HERE / "keyed_core.py")],
                           cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        sys.exit(f"refused: the spec or the code has uncommitted changes:\n{dirty}")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"spec_sha256": sha(SPEC), "script_sha256": sha(Path(__file__)), "core_sha256": sha(HERE / "keyed_core.py"),
            "commit": commit}


# ---------------------------------------------------------------- validate
def validate():
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    t_start, checks = time.time(), {}
    I = inputs()
    files = {f"{k}_{tag(r)}_k{s}": cal_file(k, r, s) for k in ("texts", "ppl") for r in (RHO, RHO2) for s in TUNING}
    files.update({"S_F_van": V02 / "S_F_van.json", "S_A_van": V02 / "S_A_van.json", "S_C_ref": V02 / "S_C_ref.json",
                  "S_C_ref_norms": V02 / "S_C_ref_norms.npy", "bars": BARS, "S3_F": S3DATA / "S_F_van.npz",
                  "study2_pilot_results": S2PILOT})
    files.update({f"threat_feats_k{s}": DATA / f"feats_r050_k{s}.npz" for s in TUNING})
    files["threat_grads_C"] = DATA / "grads_C.npz"
    missing = [k for k, p in files.items() if not p.exists()]
    counts = {k: len(load(p)) for k, p in files.items() if p.suffix == ".json" and p.exists() and "bars" not in k
              and "results" not in k}
    ok = (not missing and all(len(t) == PER_KEY for t in I["T"]) and len(I["B"]) == N_OBS and len(I["D"]) == N_FORGE
          and counts["S_F_van"] == 200 and counts["S_A_van"] == 1000 and all(v == 100 for k, v in counts.items() if "calib" in k))
    checks["1_inputs"] = {"pass": bool(ok), "missing": missing, "counts": counts,
                          "sha256": {k: sha(p) for k, p in files.items() if p.exists() and p.stat().st_size < 50_000_000}}

    # 2. synthetic: the keyed test's null is uniform and a planted signal is detected
    from scipy.stats import kstest
    rng = np.random.default_rng(20261002)
    own0 = KC.KeyedOwner({"mu": np.zeros(D), "sd": np.ones(D)})
    p0, p1 = [], []
    for i in range(300):
        X = rng.normal(size=(T_MAX, D))
        ids = rng.integers(0, 150_000, T_MAX)
        sec = np.uint64(rng.integers(1, 2**62))
        p0.append(own0.pvalue(X, ids, 1, sec)[0])
        pos, ctx = KC.contexts(ids, 1)
        X[pos] += 2.0 * KC.dense_keys(sec, ctx)
        p1.append(own0.pvalue(X, ids, 1, sec)[0])
    p0, p1 = np.array(p0), np.array(p1)
    ks = kstest(p0, "uniform")
    checks["2_synthetic"] = {"pass": bool(ks.pvalue > 0.01 and np.allclose(p0 * 1000, np.round(p0 * 1000))
                                          and (p1 <= ALPHA).mean() > 0.9),
                             "ks_p": float(ks.pvalue), "null_rate_pct": 100 * float((p0 <= ALPHA).mean()),
                             "planted_detection": float((p1 <= ALPHA).mean())}

    tok, model = PP.load()
    dev = core.device()
    # 3. I1: fixed-mode reproduction of core.generate and of the stored calibration texts
    prompts16 = I["T"][0][:16]
    vec = torch.from_numpy(PP.tuning_key(TUNING[0], RHO))
    t0 = time.time()
    a, _, _ = KC.generate(tok, model, prompts16, "fixed", vec=vec, seed=TUNING[0])
    t_gen_fixed = (time.time() - t0) / 16
    b = core.generate(tok, model, prompts16, key=vec, layer=LAYER, seed=TUNING[0])
    stored = load(cal_file("texts", RHO, TUNING[0]))[:16]
    checks["3_I1_reproduction"] = {"pass": a == b, "equal_to_core_generate": int(sum(x == y for x, y in zip(a, b))),
                                   "equal_to_stored_calibration": int(sum(x == y for x, y in zip(a, stored)))}

    # 4. I2: keyed structure replay and the tokenisation round trip (validation secret)
    prompts8 = I["B"][:8]
    st = {}
    t_gen_keyed = {}
    for h in (1, 4):
        t0 = time.time()
        texts, ids, used = KC.generate(tok, model, prompts8, "keyed", h=h, secret=VAL_SECRET, rho=RHO, seed=seed(9, 9, h))
        t_gen_keyed[h] = (time.time() - t0) / 8
        eq, rt_len, rt_share, n_used = [], [], [], []
        for text, idv, us in zip(texts, ids, used):
            pos, ctx = KC.contexts(np.asarray(idv), h)
            idx, _ = KC.keys_from_hash(KC.context_hash([VAL_SECRET], ctx)[0])
            derived = [(int(p), tuple(int(i) for i in r)) for p, r in zip(pos, idx)]
            usedl = [(int(p), tuple(c)) for p, c in us]
            eq.append(derived[:len(usedl)] == usedl and len(derived) == len(usedl) + 1 and derived[-1][0] == T_MAX - 1)
            n_used.append(len(us))
            enc = core._encode(tok, [text])
            rid = enc["input_ids"][0][enc["content_mask"][0].bool()].tolist()
            m = min(len(rid), len(idv))
            rt_len.append(len(rid) == len(idv))
            rt_share.append(float(np.mean([rid[i] == idv[i] for i in range(m)])))
        st[str(h)] = {"all_equal": all(eq), "n_equal": int(sum(eq)), "keys_used_per_text": n_used,
                      "roundtrip_same_length": int(sum(rt_len)), "roundtrip_share_equal_mean": float(np.mean(rt_share))}
    checks["4_I2_structure"] = {"pass": all(v["all_equal"] for v in st.values()), **st}

    # 5. the hook acts only through its vectors and is removed
    prompts4 = I["B"][:4]
    u0 = core.generate(tok, model, prompts4, key=None, seed=seed(9, 9, 50))
    z0, _, _ = KC.generate(tok, model, prompts4, "keyed", h=1, secret=VAL_SECRET, rho=RHO, scale=0.0, seed=seed(9, 9, 50))
    k1, _, _ = KC.generate(tok, model, prompts4, "keyed", h=1, secret=VAL_SECRET, rho=RHO, seed=seed(9, 9, 50))
    u1 = core.generate(tok, model, prompts4, key=None, seed=seed(9, 9, 50))
    checks["5_hook_zero_and_removed"] = {"pass": bool(z0 == u0 and u1 == u0 and sum(x != y for x, y in zip(k1, u0)) >= 3),
                                         "zero_scale_equals_unsteered": z0 == u0, "steered_differ": int(sum(x != y for x, y in zip(k1, u0))),
                                         "after_removal_equals_unsteered": u1 == u0}

    # 6. reference statistics (owner: pool F; attacker: pool C)
    t_grad = []
    for name, texts in (("ref_owner", I["F"]), ("ref_attacker", I["C"])):
        f = DATA / f"{name}.npz"
        if not f.exists():
            ps = KC.PosStats()
            t0 = time.time()
            for t in texts:
                g, _ = KC.position_grads(tok, model, t)
                ps.add(g)
            t_grad.append((time.time() - t0) / len(texts))
            r = ps.ref()
            np.savez(f, mu=r["mu"], sd=r["sd"], n=r["n_positions"])
    own, att = load_ref("ref_owner"), load_ref("ref_attacker")
    checks["6_references"] = {"pass": bool(own["n_positions"] > 40_000 and att["n_positions"] > 40_000),
                              "owner_positions": own["n_positions"], "attacker_positions": att["n_positions"],
                              "sd_max_over_median_owner": float(own["sd"].max() / np.median(own["sd"]))}

    # 8. I3: calibration on 1,000 unwatermarked texts (and the summed gradients for the rotation test)
    owner = KC.KeyedOwner(own)
    fN = DATA / "null_A.npz"
    if not fN.exists():
        secrets = [VAL_SECRET] + TUNING
        P = {f"h{h}_s{sec}": [] for h in (1, 4) for sec in secrets}
        Pf = {f"h0_k{s}": [] for s in TUNING}
        Gsum = np.zeros((len(I["A"]), D), dtype=np.float32)
        t0 = time.time()
        for i, t in enumerate(I["A"]):
            g, idv = KC.position_grads(tok, model, t)
            Gsum[i] = g.sum(0)
            for h in (1, 4):
                for sec in secrets:
                    P[f"h{h}_s{sec}"].append(owner.pvalue(g, idv, h, sec)[0])
            for s in TUNING:
                Pf[f"h0_k{s}"].append(owner.pvalue_fixed(g, KC.fixed_dir(s))[0])
            if (i + 1) % 200 == 0:
                print(f"  null {i + 1}/1000, {time.time() - t0:.0f}s", flush=True)
        t_null = (time.time() - t0) / len(I["A"])
        np.savez(fN, Gsum=Gsum, t_per_text=t_null, **{k: np.array(v) for k, v in {**P, **Pf}.items()})
    zN = np.load(fN)
    fpr = {k: 100 * float((zN[k] <= ALPHA).mean()) for k in zN.files if k.startswith("h")}
    checks["8_I3_null_fpr"] = {"pass": all(0.3 <= v <= 2.5 for v in fpr.values()), "fpr_pct": fpr,
                               "s_per_text_incl_pvalues": float(zN["t_per_text"])}

    # 9. I5: timing projection for the study (decision 3's scope) and the pre-set fallbacks
    t_g = float(np.mean(list(t_gen_keyed.values())))
    t_f = float(np.mean(t_grad)) if t_grad else float(zN["t_per_text"]) / 3
    t_q = 0.15
    keylevels = 2 * 8
    def hours(obs_h4, n_para):
        gens = keylevels * ((1024 + 100 + 200 + 100) + (obs_h4 + 100 + 200 + 100)) + keylevels * 2 * 100 + 2 * 2 * 2 * 100
        feats = keylevels * ((1024 + 100 + 200 + 100) + (obs_h4 + 100 + 200 + 100)) + keylevels * 2 * n_para + keylevels * 1024 + keylevels * 200 + 800
        para = keylevels * 2 * n_para * PARA_S
        qual = (keylevels * 2 * (100 + 200 + 100 + n_para) + keylevels * 200 + 800) * t_q
        return (gens * t_g + feats * t_f + para + qual) / 3600
    proj = {"full": hours(1024, 100), "fallback1_h4_n256": hours(256, 100), "fallback2_plus_para50": hours(256, 50)}
    checks["9_I5_timing"] = {"pass": proj["full"] <= BUDGET_H, "projected_h": proj, "budget_h": BUDGET_H,
                             "s_per_keyed_generation": t_gen_keyed, "s_per_fixed_generation": t_gen_fixed,
                             "s_per_feature_text": t_f, "assumed_s_per_paraphrase": PARA_S, "assumed_s_per_quality": t_q}

    # 7. gradient agreement: bf16 cosine, then float32 relative difference
    cos_bf, rel32 = [], []
    for t in I["F"][:3]:
        g1 = PP.text_features(tok, model, t)[1].astype(np.float64)
        g, _ = KC.position_grads(tok, model, t)
        cos_bf.append(KC.PP.unit(g.sum(0).astype(np.float64)) @ KC.PP.unit(g1))
    del model
    free()
    tok32, model32 = core.load_model()
    model32.float()
    for prm in model32.parameters():
        prm.requires_grad_(False)
    for t in I["F"][:3]:
        g1 = PP.text_features(tok32, model32, t)[1].astype(np.float64)
        g, _ = KC.position_grads(tok32, model32, t)
        rel32.append(float(np.linalg.norm(g.sum(0) - g1) / np.linalg.norm(g1)))
    del model32
    free()
    checks["7_grad_agreement"] = {"pass": bool(max(rel32) <= 1e-3 and min(cos_bf) >= 0.99), "relative_diff_float32": rel32,
                                  "bf16_cos": [float(c) for c in cos_bf]}
    checks = {k: checks[k] for k in sorted(checks)}
    res = {"spec": SPEC.name, "spec_sha256": sha(SPEC), "script_sha256": sha(Path(__file__)), "core_sha256": sha(HERE / "keyed_core.py"),
           "date_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
           "note": "inputs only: unwatermarked texts, the validation secret 0, synthetic data; no statistic on any tuning-key or study-key text",
           "checks": checks, "all_pass": all(c["pass"] for c in checks.values()), "elapsed_s": time.time() - t_start}
    (OUT / "VALIDATION.json").write_text(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    for k, c in checks.items():
        print(k, "PASS" if c["pass"] else "FAIL", {x: y for x, y in c.items() if x not in ("sha256",)})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


# ---------------------------------------------------------------- run
def run():
    guard = spec_guard()
    DATA.mkdir(parents=True, exist_ok=True)
    I = inputs()
    bars = load(BARS)
    own, att = load_ref("ref_owner"), load_ref("ref_attacker")
    owner = KC.KeyedOwner(own)
    t_all = time.time()

    # ---- step A: generation, features, quality, attacker, forgeries, controls (base model)
    tok, model = PP.load()
    for ai, (arm, h) in enumerate(ARMS.items()):
        for ki, s in enumerate(TUNING):
            pre = f"{arm}_k{s}"
            fA = DATA / f"stepA_{pre}.json"
            if fA.exists():
                continue
            out = {"arm": arm, "h": h, "key": s}
            sets = {}
            for name, prompts, rho, off in (("gen050", I["T"][ki], RHO, 10), ("gen035", I["T"][ki], RHO2, 20), ("obs", I["B"], RHO, 30)):
                f = DATA / f"texts_{pre}_{name}.json"
                if not f.exists():
                    t0 = time.time()
                    texts, ids, used = KC.generate(tok, model, prompts, "keyed", h=h, secret=s, rho=rho, seed=seed(ai, ki, off))
                    save(f, {"texts": texts, "ids": ids, "n_keys_used": [len(u) for u in used], "gen_s": time.time() - t0})
                sets[name] = load(f)
            z = {name: feats_cached(tok, model, f"feats_{pre}_{name}", sets[name]["texts"]) for name in sets}
            out["gen_s_per_text"] = {name: sets[name]["gen_s"] / len(sets[name]["texts"]) for name in sets if "gen_s" in sets[name]}
            out["p"] = {name: pvals(owner, z[name], h, s).tolist() for name in ("gen050", "gen035")}
            out["roundtrip_share"] = {name: roundtrip_share(sets[name]["ids"], z[name]) for name in sets}
            # quality: the keyed genuine texts and the fixed-key calibration texts on the same prompts
            out["quality"] = {name: quality(tok, model, I["T"][ki], sets[name]["texts"]) for name in ("gen050", "gen035")}
            out["quality_fixed"] = {name: quality(tok, model, I["T"][ki], load(cal_file("texts", rho, s)))
                                    for name, rho in (("gen050", RHO), ("gen035", RHO2))}
            # the attacker (knows h and the layer; its own reference and scale)
            A = KC.ContextAttacker(att, h, C_MIN, RHO * I["C_norm"])
            obs_ids = [ids for _, ids in each(z["obs"])]
            A.eligible_from_ids(obs_ids)
            gen_ids = [ids for _, ids in each(z["gen050"])]
            out["attacker"] = {"n_eligible_contexts_at_100": len(A.eligible), "n_distinct_contexts_at_100": len(A.all_counts)}
            done = 0
            for n in N_GRID:
                for G, ids in list(each(z["obs"]))[done:n]:
                    A.observe(G, ids)
                done = n
                out["attacker"][str(n)] = {**A.score(s), "coverage_genuine": A.coverage(gen_ids)}
            table = A.table()
            np.savez(DATA / f"table_{pre}.npz", ctx=np.asarray(list(table.keys()), dtype=np.int64).reshape(len(table), h),
                     V=np.stack(list(table.values())) if table else np.zeros((0, D), dtype=np.float32))
            # forgeries (the attacker's table at n = 100) and the random-secret control
            fF = DATA / f"texts_{pre}_forge.json"
            if not fF.exists():
                texts, ids, used = KC.generate(tok, model, I["D"], "table", h=h, table=table, seed=seed(ai, ki, 40))
                save(fF, {"texts": texts, "ids": ids, "n_keys_used": [len(u) for u in used]})
            fC = DATA / f"texts_{pre}_control.json"
            if not fC.exists():
                texts, ids, used = KC.generate(tok, model, I["D"], "keyed", h=h, secret=CONTROL[ki], rho=RHO, seed=seed(ai, ki, 50))
                save(fC, {"texts": texts, "ids": ids})
            for name in ("forge", "control"):
                T_ = load(DATA / f"texts_{pre}_{name}.json")
                zz = feats_cached(tok, model, f"feats_{pre}_{name}", T_["texts"])
                out["p"][name] = pvals(owner, zz, h, s).tolist()
                out["quality"][name] = quality(tok, model, I["D"], T_["texts"])
                if name == "forge":
                    out["forge_steered_positions_per_text"] = T_["n_keys_used"]
            save(fA, out)
            print(f"A {pre} done, {time.time() - t_all:.0f}s", flush=True)
    del model, tok
    free()

    # ---- rotation code test (K = 4; summed gradients from the threat check and the validation's null set)
    fR = DATA / "rotation_test.json"
    if not fR.exists():
        refG = np.load(S3DATA / "S_F_van.npz")["G"].astype(np.float32)
        ref = S3.reference(refG, refG)
        Gk = {s: np.load(DATA / f"feats_{tag(RHO)}_k{s}.npz")["G"][:, LAYER].astype(np.float32) for s in TUNING}
        X = {s: PP.transform("S4", None, Gk[s], ref) for s in TUNING}
        Xn = PP.transform("S4", None, np.load(DATA / "null_A.npz")["Gsum"], ref)
        keys = np.stack([KC.fixed_dir(s) for s in TUNING])
        big = S3.null_keys_big()
        rot = {"union_detection_pct": {}, "single_detection_pct": {}}
        for s in TUNING:
            pu, _ = KC.union_pvalues(X[s], keys, big)
            rot["union_detection_pct"][str(s)] = 100 * float((pu <= ALPHA).mean())
            rot["single_detection_pct"][str(s)] = 100 * float((S3.pv(X[s], KC.fixed_dir(s), PP.null_matrix()) <= ALPHA).mean())
        pn, _ = KC.union_pvalues(Xn, keys, big)
        rot["union_fpr_pct"] = 100 * float((pn <= ALPHA).mean())
        # the mixture (interleaved) and the attackers
        mix = np.stack([Gk[s][j] for j in range(100) for s in TUNING])
        refC = np.load(DATA / "grads_C.npz")["G"][:, LAYER].astype(np.float32)
        rot["naive"], rot["cluster"] = {}, {}
        for n in (16, 64, 100, 400):
            v = KC.route_a_prime_fixed(mix[:n], refC, RHO)
            rot["naive"][str(n)] = {str(s): float(v @ KC.fixed_dir(s)) for s in TUNING}
            Xm = (mix[:n] - refC.mean(0)) / np.maximum(refC.std(0, ddof=1), 1e-12)
            lab = KC.cosine_kmeans(Xm, len(TUNING), seed=20261002 + n)
            per = {}
            for k in range(len(TUNING)):
                if (lab == k).sum() < 2:
                    continue
                vk = KC.route_a_prime_fixed(mix[:n][lab == k], refC, RHO)
                per[str(k)] = {"size": int((lab == k).sum()), "best_key": int(max(TUNING, key=lambda s: vk @ KC.fixed_dir(s))),
                               "best_cos": float(max(vk @ KC.fixed_dir(s) for s in TUNING))}
            rot["cluster"][str(n)] = {"clusters": per,
                                      "keys_recovered_ge_0.5": len({c["best_key"] for c in per.values() if c["best_cos"] >= 0.5})}
        save(fR, rot)
        print("rotation test done", flush=True)

    # ---- step B: paraphrase (P-Qwen with the attacker's self-check; Study 2's function; no base model held)
    import common_s2 as S2
    for ai, (arm, h) in enumerate(ARMS.items()):
        for ki, s in enumerate(TUNING):
            pre = f"{arm}_k{s}"
            fP = DATA / f"para_{pre}.json"
            if fP.exists():
                continue
            A_ = load(DATA / f"stepA_{pre}.json")
            texts = load(DATA / f"texts_{pre}_gen050.json")["texts"][:N_PARA]
            oq = {k: A_["quality"]["gen050"][k][:N_PARA] for k in ("ppl", "rep", "len")}
            res = S2.paraphrase_with_checks("qwen", texts, I["T"][ki][:N_PARA], oq, bars["C"], 5 + 4 * ai + ki, DATA,
                                            log=lambda m: print(m, flush=True))
            save(fP, {"kept": res["kept"], "texts": S2.kept_texts(res), "attempts": res["attempts"], "paraphrase_s": res["paraphrase_s"]})
            print(f"B {pre} done, {time.time() - t_all:.0f}s", flush=True)
    free()

    # ---- step C: score the paraphrases (base model and the embedder)
    tok, model = PP.load()
    E = SC.Embedder()
    for ai, (arm, h) in enumerate(ARMS.items()):
        for ki, s in enumerate(TUNING):
            pre = f"{arm}_k{s}"
            fS = DATA / f"parascore_{pre}.json"
            if fS.exists():
                continue
            A_ = load(DATA / f"stepA_{pre}.json")
            orig = load(DATA / f"texts_{pre}_gen050.json")["texts"][:N_PARA]
            kept = load(DATA / f"para_{pre}.json")["texts"]
            oq = {k: np.asarray(A_["quality"]["gen050"][k][:N_PARA]) for k in ("ppl", "rep", "len")}
            zq = SC.raw_quality(tok, model, E, I["T"][ki][:N_PARA], kept, orig)
            cond = SC.conditions(oq, zq, bars["A"])
            zz = feats_cached(tok, model, f"feats_{pre}_para", kept)
            p = pvals(owner, zz, h, s)
            save(fS, {"p": p.tolist(), "detected": (p <= ALPHA).tolist(), "quality_all": cond["all"].tolist(),
                      "quality": {k: cond[k].tolist() for k in ("ppl", "rep", "len", "cos")},
                      "success": ((p > ALPHA) & cond["all"]).tolist(), "zq": {k: np.asarray(v).tolist() for k, v in zq.items()}})
            print(f"C {pre} done, {time.time() - t_all:.0f}s", flush=True)
    del model, E, tok
    free()
    save(DATA / "run_guard.json", {**guard, "elapsed_s": time.time() - t_all})
    print("run complete", flush=True)


# ---------------------------------------------------------------- analyse
def med(xs):
    return float(np.median(xs))


def analyse():
    guard = spec_guard()
    V = load(OUT / "VALIDATION.json")
    res = {"guard": guard, "run_guard": load(DATA / "run_guard.json"), "validation_all_pass": V["all_pass"], "arms": {}}
    fixed_ref = {}
    for arm, h in ARMS.items():
        R = {"h": h, "per_key": {}}
        for ki, s in enumerate(TUNING):
            A_ = load(DATA / f"stepA_{arm}_k{s}.json")
            PS = load(DATA / f"parascore_{arm}_k{s}.json")
            PA = load(DATA / f"para_{arm}_k{s}.json")
            q, qf = A_["quality"], A_["quality_fixed"]
            fl_ppl, fl_rep = np.quantile(q["gen050"]["ppl"], 0.95), np.quantile(q["gen050"]["rep"], 0.95)
            acc_f = np.asarray(A_["p"]["forge"]) <= ALPHA
            fluent = (np.asarray(q["forge"]["ppl"]) <= fl_ppl) & (np.asarray(q["forge"]["rep"]) <= fl_rep)
            e = {"detect050_pct": 100 * float(np.mean(np.asarray(A_["p"]["gen050"]) <= ALPHA)),
                 "detect035_pct": 100 * float(np.mean(np.asarray(A_["p"]["gen035"]) <= ALPHA)),
                 "ppl_ratio_050": med(np.asarray(q["gen050"]["ppl"]) / np.asarray(qf["gen050"]["ppl"])),
                 "ppl_ratio_035": med(np.asarray(q["gen035"]["ppl"]) / np.asarray(qf["gen035"]["ppl"])),
                 "ppl_median_050": med(q["gen050"]["ppl"]), "ppl_fixed_median_050": med(qf["gen050"]["ppl"]),
                 "rep_median_050": med(q["gen050"]["rep"]), "rep_fixed_median_050": med(qf["gen050"]["rep"]),
                 "roundtrip_share": A_["roundtrip_share"], "attacker": A_["attacker"],
                 "forge_accept_pct": 100 * float(acc_f.mean()), "forge_FA_pct": 100 * float((acc_f & fluent).mean()),
                 "forge_fluent_pct": 100 * float(fluent.mean()),
                 "forge_steered_positions_median": med(A_["forge_steered_positions_per_text"]),
                 "control_accept_pct": 100 * float(np.mean(np.asarray(A_["p"]["control"]) <= ALPHA)),
                 "para_success_pct": 100 * float(np.mean(PS["success"])), "para_detected_pct": 100 * float(np.mean(PS["detected"])),
                 "para_quality_pass_pct": 100 * float(np.mean(PS["quality_all"])),
                 "para_s_per_original": PA["paraphrase_s"] / N_PARA, "gen_s_per_text": A_.get("gen_s_per_text", {})}
            R["per_key"][str(s)] = e
        keys = list(R["per_key"].values())
        R["median"] = {k: med([e[k] for e in keys]) for k in keys[0] if isinstance(keys[0][k], (int, float))}
        R["median"]["attacker"] = {str(n): {"cos_weighted": med([e["attacker"][str(n)]["cos_weighted"] for e in keys]),
                                            "coverage_genuine": med([e["attacker"][str(n)]["coverage_genuine"] for e in keys]),
                                            "n_contexts": med([e["attacker"][str(n)]["n_contexts"] for e in keys])} for n in N_GRID}
        res["arms"][arm] = R
    try:
        s2 = load(S2PILOT)["methods"]["P-qwen"]["0.5"]
        fixed_ref = {k: s2[k] for k in ("detected_before", "detected_after", "success")}
    except Exception as ex:  # noqa: BLE001
        fixed_ref = {"error": str(ex)}
    res["fixed_key_tuning_P_qwen_050_study2_pilot"] = fixed_ref
    res["rotation_test"] = load(DATA / "rotation_test.json")
    tm = V["checks"]["9_I5_timing"]
    para_meas = float(np.mean([res["arms"][a]["per_key"][str(s)]["para_s_per_original"] for a in ARMS for s in TUNING]))
    gen_meas = float(np.mean([v for a in ARMS for s in TUNING for v in res["arms"][a]["per_key"][str(s)]["gen_s_per_text"].values()]))
    res["timing"] = {"validation_projection": tm, "measured_para_s_per_original": para_meas, "measured_keyed_gen_s_per_text": gen_meas}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    L = ["# Study 5 defence pilot v0.1 — report (generated by defence_pilot.py from results.json)", "",
         f"Spec sha256 {guard['spec_sha256'][:12]}, commit {guard['commit'][:7]}; validation all pass: {V['all_pass']}. "
         "Tuning keys 9001–9004; medians over the 4 keys unless stated. No rule applies to these readings.", "",
         "## Keyed arms at ρ = 0.50 (and detection at 0.35)", "",
         "| arm | detect 0.50 % | detect 0.35 % | ppl ratio vs fixed (0.50) | ppl ratio (0.35) | rep keyed / fixed (0.50) | forge accept % | forge FA % | control accept % | para success % | para detected % | para quality pass % | roundtrip share |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm, R in res["arms"].items():
        m = R["median"]
        rt = med([e["roundtrip_share"]["gen050"] for e in R["per_key"].values()])
        L.append(f"| {arm} | {m['detect050_pct']:.1f} | {m['detect035_pct']:.1f} | {m['ppl_ratio_050']:.3f} | {m['ppl_ratio_035']:.3f} | "
                 f"{m['rep_median_050']:.3f} / {m['rep_fixed_median_050']:.3f} | {m['forge_accept_pct']:.1f} | {m['forge_FA_pct']:.1f} | "
                 f"{m['control_accept_pct']:.1f} | {m['para_success_pct']:.1f} | {m['para_detected_pct']:.1f} | {m['para_quality_pass_pct']:.1f} | {rt:.3f} |")
    L += ["", "## The per-context attacker (median over keys): count-weighted cosine, coverage of genuine positions, contexts estimated", "",
          "| arm | n | cos (weighted) | coverage | contexts |", "|---|---|---|---|---|"]
    for arm, R in res["arms"].items():
        for n in N_GRID:
            a = R["median"]["attacker"][str(n)]
            L.append(f"| {arm} | {n} | {a['cos_weighted']:.3f} | {a['coverage_genuine']:.3f} | {a['n_contexts']:.0f} |")
    L += ["", "## Per key", "", "| arm | key | detect 0.50 | ppl ratio | forge FA | para success | attacker cos at 100 | coverage at 100 |", "|---|---|---|---|---|---|---|---|"]
    for arm, R in res["arms"].items():
        for s, e in R["per_key"].items():
            L.append(f"| {arm} | {s} | {e['detect050_pct']:.0f} | {e['ppl_ratio_050']:.2f} | {e['forge_FA_pct']:.0f} | {e['para_success_pct']:.0f} | "
                     f"{e['attacker']['100']['cos_weighted']:.2f} | {e['attacker']['100']['coverage_genuine']:.2f} |")
    L += ["", f"Fixed key, P-Qwen at ρ = 0.50 on the tuning keys (Study 2 pilot v0.1): {json.dumps(fixed_ref)}", "",
          "## Rotation code test (K = 4 tuning keys at ρ = 0.50)", "", f"```\n{json.dumps(res['rotation_test'], indent=1)[:3000]}\n```", "",
          "## Timing", "", f"```\n{json.dumps(res['timing'], indent=1)}\n```"]
    (OUT / "REPORT.md").write_text("\n".join(L) + "\n")
    print(json.dumps({a: res["arms"][a]["median"] for a in ARMS}, indent=1)[:3000])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["validate", "run", "analyse"], required=True)
    {"validate": validate, "run": run, "analyse": analyse}[ap.parse_args().phase]()
