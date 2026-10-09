"""Study 1 v0.2 runner (STUDY1_PROTOCOL_v0.2.md). Refuses to run unless PRE_RUN_LOCK.json matches the file hashes.

Phases, checkpointed under research/study1_v02/data/ (git-ignored):
  S  shared unwatermarked sets: A (A1 threshold, A2 check, A2 human), F (owner training), C (attacker reference)
  K  per key and level: observed texts (B), owner detector (E vs F, threshold on A1), oracle and random controls (D),
     attack estimates (routes A and B, all n; attack2.py sees features only), forgeries (D) scored by the owner
  R  gates, rules, bootstrap -> research/outputs/study1_v0.2/results.json
Run: .venv/bin/python research/study1_v02/run_v02.py [--phase S|K|R|all]
"""
import argparse
import hashlib
import json
import time

import numpy as np
import torch

import common as C  # first: puts research/study1 on sys.path
import attack2  # noqa: E402
import detect2
from common import core

DATA = C.HERE / "data"
LOCK_DIR = C.ROOT / "research" / "outputs" / "study1_v0.2"
PROTOCOL = C.ROOT / "research" / "STUDY1_PROTOCOL_v0.2.md"
CODE = [C.HERE / f for f in ("common.py", "detect2.py", "attack2.py", "run_v02.py", "validate_v02.py")] + [
    C.HERE.parent / "study1" / "core.py", C.HERE.parent / "study1" / "attack.py"]
BOOT_B, BOOT_SEED = 2000, 20260926


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_lock():
    lock = json.loads((LOCK_DIR / "PRE_RUN_LOCK.json").read_text())
    assert lock["protocol_sha256"] == sha(PROTOCOL), "protocol changed since lock"
    for p in CODE:
        assert lock["code_sha256"][p.name] == sha(p), f"{p.name} changed since lock"
    return lock


def tag(s, rho):
    return f"k{s}_r{int(round(rho * 100)):03d}"


def seed_base(s, li):
    return s * 1000 + li * 100


def npy(name):
    return DATA / f"{name}.npy"


def save_json(name, obj):
    (DATA / f"{name}.json").write_text(json.dumps(obj))


def load_json(name):
    return json.loads((DATA / f"{name}.json").read_text())


def have(name, ext="json"):
    return (DATA / f"{name}.{ext}").exists()


def gen(tok, model, name, prompt_list, vec, layer, seed):
    if not have(name):
        texts = core.generate(tok, model, prompt_list, key=vec, layer=layer, seed=seed)
        save_json(name, texts)
        torch.mps.empty_cache()
    return load_json(name)


def tokens_cached(tok, model, name, texts):
    if not npy(name + "_X").exists():
        X, lens = C.layer_tokens(tok, model, texts)
        np.save(npy(name + "_X"), X)
        np.save(npy(name + "_lens"), lens)
    return np.load(npy(name + "_X")), np.load(npy(name + "_lens"))


# ------------------------------------------------------------------ phase S
def phase_s(tok, model, P):
    a = gen(tok, model, "S_A_van", C.prompts(P["A1"]) + C.prompts(P["A2"]), None, C.LAYER, seed=11)
    tokens_cached(tok, model, "S_A_van", a)
    tokens_cached(tok, model, "S_A2_human", [u["human_continuation"] for u in P["A2"]])
    f = gen(tok, model, "S_F_van", C.prompts(P["F"]), None, C.LAYER, seed=17)
    tokens_cached(tok, model, "S_F_van", f)
    c = gen(tok, model, "S_C_ref", C.prompts(P["C"]), None, C.LAYER, seed=13)
    if not npy("S_C_ref_feats").exists():
        feats, norms = C.all_layer_means(tok, model, c, want_norms=True)
        np.save(npy("S_C_ref_feats"), feats)
        np.save(npy("S_C_ref_norms"), norms)
    print(f"phase S done", flush=True)


# ------------------------------------------------------------------ phase K
def phase_k_one(tok, model, P, s, li, rho, dev, refs):
    t = tag(s, rho)
    base = seed_base(s, li)
    v = C.key(s, rho)
    out = f"K_{t}_summary"
    if have(out):
        return
    # observed watermarked texts (attacker's sample) and their all-layer features
    obs = gen(tok, model, f"K_{t}_obs", C.prompts(P["B"]), v, C.LAYER, seed=base + 1)
    if not npy(f"K_{t}_obs_feats").exists():
        np.save(npy(f"K_{t}_obs_feats"), C.all_layer_means(tok, model, obs))
    # owner's detector
    e = gen(tok, model, f"K_{t}_E", C.prompts(P["E"]), v, C.LAYER, seed=base + 2)
    XE, lE = C.layer_tokens(tok, model, e)
    XF, lF = refs["F"]
    net = detect2.train(XE, lE, XF, lF, dev)
    del XE
    XA, lA = refs["A"]
    sA = detect2.score(net, XA, lA, dev)
    thr = detect2.threshold(sA[:500], C.FPR)
    sH = detect2.score(net, *refs["H"], dev)
    torch.save(net.state_dict(), DATA / f"K_{t}_mlp.pt")
    # controls on pool D
    ctrl = C.CONTROL_KEYS[C.STUDY_KEYS.index(s)]
    res = {"threshold": thr, "scores_A1": sA[:500].tolist(), "scores_A2": sA[500:].tolist(), "scores_A2_human": sH.tolist()}
    pD = C.prompts(P["D"])
    for name, vec, sd in (("oracle", v, base + 3), ("random", C.key(ctrl, rho), base + 4)):
        txt = gen(tok, model, f"K_{t}_{name}", pD, vec, C.LAYER, seed=sd)
        X, l = C.layer_tokens(tok, model, txt)
        res[f"scores_{name}"] = detect2.score(net, X, l, dev).tolist()
        res[f"ppl_{name}"] = C.perplexities(tok, model, pD, txt)
    # attack (features only), then compare with the truth outside the attack module
    obs_f = np.load(npy(f"K_{t}_obs_feats"))
    vt = v.numpy()
    est = {}
    for n in C.N_GRID:
        la, va, pa = attack2.route_a(obs_f[:n], refs["C"], C.K_SUPPORT, rho, refs["C_norms"])
        lb, vb, pb = attack2.route_b(obs_f[:n], refs["C"], rho, refs["C_norms"])
        cos = lambda x: float(x @ vt / (np.linalg.norm(x) * np.linalg.norm(vt)))  # noqa: E731
        est[n] = {"A": {"layer": la, "cos": cos(va), "support_hit": len(set(np.flatnonzero(va)) & set(np.flatnonzero(vt))) / C.K_SUPPORT,
                        "vhat": va.tolist(), "profile": pa.tolist()},
                  "B": {"layer": lb, "cos": cos(vb), "vhat": vb.tolist(), "profile": pb.tolist()}}
    np.save(npy(f"K_{t}_vhats"), np.stack([np.stack([est[n]["A"]["vhat"], est[n]["B"]["vhat"]]) for n in C.N_GRID]))
    res["estimates"] = {str(n): {r: {k: x for k, x in est[n][r].items() if k != "vhat"} for r in "AB"} for n in C.N_GRID}
    # forgeries, scored by the owner's detector
    for ni, n in enumerate(C.FORGE_N):
        for ri, r in enumerate("AB"):
            vh = torch.tensor(est[n][r]["vhat"])
            txt = gen(tok, model, f"K_{t}_forge_{r}_n{n}", pD, vh, est[n][r]["layer"], seed=base + 10 + ri * 3 + ni)
            X, l = C.layer_tokens(tok, model, txt)
            res[f"scores_forge_{r}_n{n}"] = detect2.score(net, X, l, dev).tolist()
            res[f"ppl_forge_{r}_n{n}"] = C.perplexities(tok, model, pD, txt)
    save_json(out, res)


def phase_k(tok, model, P):
    dev = core.device()
    refs = {"A": (np.load(npy("S_A_van_X")), np.load(npy("S_A_van_lens"))),
            "H": (np.load(npy("S_A2_human_X")), np.load(npy("S_A2_human_lens"))),
            "F": (np.load(npy("S_F_van_X")), np.load(npy("S_F_van_lens"))),
            "C": np.load(npy("S_C_ref_feats")), "C_norms": np.load(npy("S_C_ref_norms"))}
    t0 = time.time()
    for s in C.STUDY_KEYS:
        for li, rho in enumerate(C.LEVELS):
            phase_k_one(tok, model, P, s, li, rho, dev, refs)
            print(f"K {tag(s, rho)} done, {time.time() - t0:.0f}s", flush=True)


# ------------------------------------------------------------------ phase R
def boot_median(per_key, rng):
    K = len(per_key)
    meds = []
    for _ in range(BOOT_B):
        ks = rng.integers(0, K, K)
        meds.append(np.median([per_key[k][rng.integers(0, len(per_key[k]), len(per_key[k]))].mean() for k in ks]))
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def phase_r():
    rng = np.random.default_rng(BOOT_SEED)
    S = {(s, rho): load_json(f"K_{tag(s, rho)}_summary") for s in C.STUDY_KEYS for rho in C.LEVELS}
    res = {"levels": {}}
    fp_a2 = [detect2.accept(S[k]["scores_A2"], S[k]["threshold"]).mean() for k in S]
    res["G1_pooled_FPR_A2"] = float(np.mean(fp_a2))
    res["human_FPR_A2"] = float(np.mean([detect2.accept(S[k]["scores_A2_human"], S[k]["threshold"]).mean() for k in S]))
    g1 = 0.003 <= res["G1_pooled_FPR_A2"] <= 0.025
    need = int(np.ceil(0.875 * len(C.STUDY_KEYS)))
    for rho in C.LEVELS:
        L = {}
        acc = lambda name: [detect2.accept(S[(s, rho)][name], S[(s, rho)]["threshold"]) for s in C.STUDY_KEYS]  # noqa: E731
        conds = ["oracle", "random"] + [f"forge_{r}_n{n}" for r in "AB" for n in C.FORGE_N]
        for c in conds:
            pk = acc(f"scores_{c}")
            L[c] = {"per_key": [float(x.mean()) for x in pk], "median": float(np.median([x.mean() for x in pk])),
                    "ci95": boot_median(pk, rng),
                    "ppl_median": float(np.median(sum((S[(s, rho)][f"ppl_{c}"] for s in C.STUDY_KEYS), [])))}
        rec = {}
        for n in C.N_GRID:
            e = [S[(s, rho)]["estimates"][str(n)] for s in C.STUDY_KEYS]
            rec[n] = {"median_cos_A": float(np.median([x["A"]["cos"] for x in e])),
                      "median_cos_B": float(np.median([x["B"]["cos"] for x in e])),
                      "layer_hits_A": int(sum(x["A"]["layer"] == C.LAYER for x in e)),
                      "layer_hits_B": int(sum(x["B"]["layer"] == C.LAYER for x in e)),
                      "median_support_hit_A": float(np.median([x["A"]["support_hit"] for x in e]))}
        L["recovery"] = rec
        orc, rnd = L["oracle"], L["random"]
        l1 = orc["median"] >= 0.20
        n_star = next((n for n in C.N_GRID if rec[n]["median_cos_A"] >= 0.9 and rec[n]["layer_hits_A"] >= need), None)
        r1 = "succeeds" if n_star else ("partial" if rec[1024]["median_cos_A"] >= 0.5 else "fails at this budget")
        r2 = {}
        for r in "AB":
            verdict = "inconclusive"
            for n in [x for x in C.FORGE_N if x <= 256]:
                f = L[f"forge_{r}_n{n}"]
                if f["median"] >= 0.5 * orc["median"] and f["ci95"][0] > rnd["ci95"][1]:
                    verdict = f"practical (n={n})"
                    break
            if verdict == "inconclusive" and L[f"forge_{r}_n1024"]["median"] < max(2 * rnd["median"], 0.02):
                verdict = "not practical"
            r2[r] = verdict
        r3 = rnd["median"] >= 0.5 * orc["median"]
        L["rules"] = {"L1_working_watermark": l1, "R1": r1 if l1 else f"(descriptive) {r1}", "n_star": n_star,
                      "R2": r2 if l1 else {r: f"(descriptive) {v}" for r, v in r2.items()}, "R3_generic_steering_suffices": r3}
        res["levels"][str(rho)] = L
    res["gates"] = {"G1": g1, "G2": "asserted in code"}
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    (LOCK_DIR / "results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({"gates": res["gates"], "rules": {r: res["levels"][r]["rules"] for r in res["levels"]}}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all")
    a = ap.parse_args()
    lock = check_lock()
    DATA.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    phases = "SKR" if a.phase == "all" else a.phase
    if "S" in phases or "K" in phases:
        P = C.pools()
        tok, model = core.load_model()
        if "S" in phases:
            phase_s(tok, model, P)
        if "K" in phases:
            phase_k(tok, model, P)
        del model
    if "R" in phases:
        phase_r()
    (LOCK_DIR / f"RUN_MANIFEST_{phases}.json").write_text(json.dumps(
        {"lock": lock, "phases_run": phases, "seconds": round(time.time() - t0), "torch": torch.__version__}, indent=2))


if __name__ == "__main__":
    main()
