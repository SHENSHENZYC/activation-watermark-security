"""Study 1 v0.4 runner (STUDY1_PROTOCOL_v0.4.md). Refuses to run unless PRE_RUN_LOCK.json matches the hashes of the
protocol, the code, the 243 reused v0.2 files and the 120 reused v0.3 files.

Phases, checkpointed under research/study1_v04/data/ (git-ignored):
  I  integrity: the reloaded v0.2 probes re-score v0.2's oracle texts within 1e-4 (else stop, protocol §9)
  K  per key and level: continuation-only perplexity and seq-rep-4 of the observed texts; per n and route: candidates
     (attack3, unchanged), trials, the repetition-aware selection (attack4 sees its own numbers only), 100 forgeries on
     pool D scored by the owner
  R  rules, bootstrap, secondaries, samples -> research/outputs/study1_v0.4/results.json
Run: .venv/bin/python research/study1_v04/run_v04.py [--phase I|K|R|all]
"""
import argparse
import hashlib
import json
import time

import numpy as np
import torch

import common4 as C4  # first: sets up the v0.3 / v0.2 / v0.1 import paths
import attack3  # noqa: E402  (v0.3, unchanged)
import attack4  # noqa: E402
import detect2  # noqa: E402  (v0.2)
from common4 import C2, C3, core

DATA = C4.HERE / "data"
V02, V03 = C4.V02_DATA, C4.V03_DATA
LOCK_DIR = C2.ROOT / "research" / "outputs" / "study1_v0.4"
V03_RESULTS = C2.ROOT / "research" / "outputs" / "study1_v0.3" / "results.json"
PROTOCOL = C2.ROOT / "research" / "STUDY1_PROTOCOL_v0.4.md"
CODE = [C4.HERE / f for f in ("common4.py", "attack4.py", "run_v04.py", "validate_v04.py")] + [
    C3.HERE / f for f in ("common3.py", "attack3.py")] + [
    C2.HERE / f for f in ("common.py", "detect2.py", "attack2.py")] + [
    C2.HERE.parent / "study1" / f for f in ("core.py", "attack.py")]
KEYS = list(C2.STUDY_KEYS)
LEVELS = list(C4.LEVELS)
INTEGRITY_TOL = 1e-4
BOOT_B, BOOT_SEED = 2000, 20260928
SAMPLE_KEYS = 3   # §8: the first three study keys (1001-1003)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def reused_v02_files():
    """The same 243 v0.2 files as the v0.3 lock."""
    fs = [V02 / f"S_C_ref{x}" for x in (".json", "_feats.npy", "_norms.npy")]
    for s in KEYS:
        for rho in LEVELS:
            t = C4.tag(s, rho)
            fs += [V02 / f"K_{t}_{x}" for x in ("summary.json", "mlp.pt", "obs.json", "obs_feats.npy", "oracle.json",
                                               "random.json", "forge_A_n64.json", "forge_A_n256.json",
                                               "forge_B_n64.json", "forge_B_n256.json")]
    return fs


def reused_v03_files():
    """120 v0.3 files: per key-level, K_*_v03.json and the four forged-text files."""
    fs = []
    for s in KEYS:
        for rho in LEVELS:
            t = C4.tag(s, rho)
            fs += [V03 / f"K_{t}_v03.json"] + [V03 / f"K_{t}_forge3_{r}_n{n}.json" for r in C4.ROUTES for n in C4.FORGE_N]
    return fs


def check_lock():
    lock = json.loads((LOCK_DIR / "PRE_RUN_LOCK.json").read_text())
    assert lock["protocol_sha256"] == sha(PROTOCOL), "protocol changed since lock"
    for p in CODE:
        assert lock["code_sha256"][p.name] == sha(p), f"{p.name} changed since lock"
    for key, fs in (("reused_v02_sha256", reused_v02_files()), ("reused_v03_sha256", reused_v03_files())):
        for p in fs:
            assert lock[key][p.name] == sha(p), f"reused file {p.name} changed since lock"
    return lock


def save_json(name, obj):
    (DATA / f"{name}.json").write_text(json.dumps(obj))


def load_json(name, folder=None):
    return json.loads(((folder or DATA) / f"{name}.json").read_text())


def have(name):
    return (DATA / f"{name}.json").exists()


def gen(tok, model, name, prompt_list, vec, layer, seed):
    if not have(name):
        texts = core.generate(tok, model, prompt_list, key=vec, layer=layer, seed=seed)
        save_json(name, texts)
        torch.mps.empty_cache()
    return load_json(name)


def load_net(t, dev):
    net = detect2.SimpleMLP(C2.D_MODEL).to(dev)
    net.load_state_dict(torch.load(V02 / f"K_{t}_mlp.pt", map_location=dev))
    net.eval()
    return net


def load_tok():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(core.MODEL_ID, revision=core.REVISION)


# ------------------------------------------------------------------ phase I
def phase_i(tok, model, keys=None, levels=None):
    dev, rows = core.device(), []
    for s in keys or KEYS:
        for rho in levels or LEVELS:
            t = C4.tag(s, rho)
            S2 = load_json(f"K_{t}_summary", V02)
            X, lens = C2.layer_tokens(tok, model, load_json(f"K_{t}_oracle", V02))
            sc = detect2.score(load_net(t, dev), X, lens, dev)
            rows.append({"tag": t, "max_abs_diff": float(np.max(np.abs(sc - np.asarray(S2["scores_oracle"]))))})
    ok = all(r["max_abs_diff"] <= INTEGRITY_TOL for r in rows)
    return {"pass": ok, "tol": INTEGRITY_TOL, "rows": rows}


# ------------------------------------------------------------------ phase K
def phase_k_one(tok, model, P, s, rho, dev, refs):
    t = C4.tag(s, rho)
    out = f"K_{t}_v04"
    if have(out):
        return
    base = C4.seed_base(s, rho)
    S2 = load_json(f"K_{t}_summary", V02)
    net = load_net(t, dev)
    obs = load_json(f"K_{t}_obs", V02)
    obs_f = np.load(V02 / f"K_{t}_obs_feats.npy")
    nmax = max(C4.FORGE_N)
    if not have(f"K_{t}_qobs4"):
        save_json(f"K_{t}_qobs4", C4.ppl_cont_only(tok, model, obs[:nmax]))
    q_obs_all = load_json(f"K_{t}_qobs4")
    rep_obs_all = C4.seqrep4(tok, obs[:nmax])
    trial_prompts = C2.prompts(P["C"])[:C4.N_TRIAL]
    pD = C2.prompts(P["D"])[:C4.N_FORGE]
    vt = C2.key(s, rho).numpy()
    res = {"threshold": S2["threshold"], "q_obs_all": q_obs_all, "rep_obs_all": rep_obs_all, "attacks": {}}
    for ni, n in enumerate(C4.FORGE_N):
        q_obs = float(np.median(q_obs_all[:n]))
        r_obs = attack4.rep_threshold(rep_obs_all[:n], C4.OBS_REP_Q)
        for ri, r in enumerate(C4.ROUTES):
            cands, _ = attack3.candidates(r, obs_f[:n], refs["C"], C2.K_SUPPORT, rho, refs["C_norms"], C4.N_CAND)
            q_tr, rep_tr, m_tr = [], [], []
            for c in cands:
                txt = gen(tok, model, f"K_{t}_trial4_{r}_n{n}_L{c['layer']}", trial_prompts,
                          torch.from_numpy(c["vec"]), c["layer"], seed=base + C4.SEED_TRIAL)
                q_tr.append(float(np.median(C4.ppl_cont_only(tok, model, txt))))
                rep_tr.append(C4.seqrep4(tok, txt))
                m_tr.append(attack4.n_repetitive(rep_tr[-1], r_obs))
            i, any_kept, kept = attack4.select(cands, q_obs, q_tr, m_tr, C4.TOL, C4.MAX_REP_TRIALS)
            c = cands[i]
            ftxt = gen(tok, model, f"K_{t}_forge4_{r}_n{n}", pD, torch.from_numpy(c["vec"]), c["layer"],
                       seed=base + C4.SEED_FORGE + 3 * ri + ni)
            X, lens = C2.layer_tokens(tok, model, ftxt)
            v = c["vec"]
            res["attacks"][f"{r}_n{n}"] = {
                "q_obs": q_obs, "r_obs": r_obs,
                "candidates": [{"layer": x["layer"], "profile": x["profile"], "q_trial": q, "m_trial": m,
                                "rep_trial": rr} for x, q, m, rr in zip(cands, q_tr, m_tr, rep_tr)],
                "selected": i, "selected_layer": c["layer"], "any_kept": any_kept, "n_kept": len(kept),
                "m_selected": m_tr[i],
                "cos_true": float(v @ vt / (np.linalg.norm(v) * np.linalg.norm(vt))),
                "scores": detect2.score(net, X, lens, dev).tolist(),
                "ppl": C2.perplexities(tok, model, pD, ftxt)}
    save_json(out, res)


def phase_k(tok, model, P):
    dev = core.device()
    assert load_json("I_integrity")["pass"], "integrity check has not passed (protocol §9)"
    refs = {"C": np.load(V02 / "S_C_ref_feats.npy"), "C_norms": np.load(V02 / "S_C_ref_norms.npy")}
    t0 = time.time()
    for s in KEYS:
        for rho in LEVELS:
            phase_k_one(tok, model, P, s, rho, dev, refs)
            print(f"K {C4.tag(s, rho)} done, {time.time() - t0:.0f}s", flush=True)


# ------------------------------------------------------------------ phase R
def boot_median(per_key, rng):
    K = len(per_key)
    meds = []
    for _ in range(BOOT_B):
        ks = rng.integers(0, K, K)
        meds.append(np.median([per_key[k][rng.integers(0, len(per_key[k]), len(per_key[k]))].mean() for k in ks]))
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def summarise(per_key, rng):
    return {"per_key": [float(x.mean()) for x in per_key], "median": float(np.median([x.mean() for x in per_key])),
            "ci95": boot_median(per_key, rng)}


def med_of_meds(per_key):
    return float(np.median([x.mean() for x in per_key]))


def conditions(rho, include_v04=True):
    """name -> per key (texts, scores, perplexities given the prompt): v0.2's oracle and random-key controls, v0.2's and
    v0.3's forgeries (secondary), and v0.4's forgeries (primary)."""
    src = {"oracle": {}, "random": {}}
    for s in KEYS:
        t = C4.tag(s, rho)
        S2 = load_json(f"K_{t}_summary", V02)
        for c in ("oracle", "random"):
            src[c][s] = (load_json(f"K_{t}_{c}", V02), S2[f"scores_{c}"], S2[f"ppl_{c}"])
        S3 = load_json(f"K_{t}_v03", V03)
        S4 = load_json(f"K_{t}_v04") if include_v04 else None
        for r in C4.ROUTES:
            for n in C4.FORGE_N:
                a3 = S3["attacks"][f"{r}_n{n}"]
                src.setdefault(f"v02_{r}_n{n}", {})[s] = (load_json(f"K_{t}_forge_{r}_n{n}", V02),
                                                          S2[f"scores_forge_{r}_n{n}"], S2[f"ppl_forge_{r}_n{n}"])
                src.setdefault(f"v03_{r}_n{n}", {})[s] = (load_json(f"K_{t}_forge3_{r}_n{n}", V03), a3["scores"], a3["ppl"])
                if include_v04:
                    a4 = S4["attacks"][f"{r}_n{n}"]
                    src.setdefault(f"v04_{r}_n{n}", {})[s] = (load_json(f"K_{t}_forge4_{r}_n{n}"), a4["scores"], a4["ppl"])
    return src


def cuts(tok, rho, src):
    """Per key: threshold; the oracle's 95th percentiles of perplexity, seq-rep-4 and word rep3 (§5, §8)."""
    out = {}
    for s in KEYS:
        txt, _, ppl = src["oracle"][s]
        out[s] = {"thr": load_json(f"K_{C4.tag(s, rho)}_summary", V02)["threshold"], "ppl": C4.cut(ppl),
                  "seqrep4": C4.cut(C4.seqrep4(tok, txt)), "rep3": C4.cut([C4.rep3(x) for x in txt])}
    return out


def fa_per_key(src_c, cut, rep_vals, rep_name):
    """FA per key for one condition; rep_name None switches the repetition term off (v0.3's definition)."""
    return [C4.fluent_accept(src_c[s][1], src_c[s][2], rep_vals[s], cut[s]["thr"], cut[s]["ppl"],
                             np.inf if rep_name is None else cut[s][rep_name]) for s in KEYS]


def phase_r(out_dir=None, tok=None):
    tok = tok or load_tok()
    rng = np.random.default_rng(BOOT_SEED)
    res = {"levels": {}, "integrity": load_json("I_integrity")}
    for rho in LEVELS:
        src = conditions(rho)
        cut = cuts(tok, rho, src)
        L = {"cut_per_key": {k: [cut[s][k] for s in KEYS] for k in ("ppl", "seqrep4", "rep3")}}
        seqrep = {}
        for name, d in src.items():
            sr = {s: np.asarray(C4.seqrep4(tok, d[s][0])) for s in KEYS}
            r3 = {s: np.asarray([C4.rep3(x) for x in d[s][0]]) for s in KEYS}
            seqrep[name] = sr
            fa = fa_per_key(d, cut, sr, "seqrep4")
            acc = [detect2.accept(d[s][1], cut[s]["thr"]) for s in KEYS]
            flu = [((np.asarray(d[s][2], dtype=np.float64) <= cut[s]["ppl"]) & (sr[s] <= cut[s]["seqrep4"])).astype(float)
                   for s in KEYS]
            orc_ppl = {s: np.median(src["oracle"][s][2]) for s in KEYS}
            L[name] = {"FA": summarise(fa, rng), "acceptance": summarise(acc, rng),
                       "FA_ppl_only_median": med_of_meds(fa_per_key(d, cut, sr, None)),
                       "FA_rep3_median": med_of_meds(fa_per_key(d, cut, r3, "rep3")),
                       "fluent_share_median": med_of_meds(flu),
                       "repetitive_share_median": med_of_meds([(sr[s] > cut[s]["seqrep4"]).astype(float) for s in KEYS]),
                       "ppl_ratio_to_oracle_median": float(np.median([np.median(d[s][2]) / orc_ppl[s] for s in KEYS])),
                       "seqrep4_median": float(np.median([np.median(sr[s]) for s in KEYS]))}
        att = {}
        for r in C4.ROUTES:
            for n in C4.FORGE_N:
                a = [load_json(f"K_{C4.tag(s, rho)}_v04")["attacks"][f"{r}_n{n}"] for s in KEYS]
                d, sr = src[f"v04_{r}_n{n}"], seqrep[f"v04_{r}_n{n}"]
                ev = [float(np.median(d[s][2]) <= cut[s]["ppl"] and np.median(sr[s]) <= cut[s]["seqrep4"]) for s in KEYS]
                att[f"{r}_n{n}"] = {"selected_layers": [x["selected_layer"] for x in a],
                                    "layer_hits": int(sum(x["selected_layer"] == C2.LAYER for x in a)),
                                    "selected_is_top_candidate": int(sum(x["selected"] == 0 for x in a)),
                                    "none_passed": int(sum(not x["any_kept"] for x in a)),
                                    "n_kept": [x["n_kept"] for x in a],
                                    "m_selected": [x["m_selected"] for x in a],
                                    "median_cos_true": float(np.median([x["cos_true"] for x in a])),
                                    "check_vs_eval_agreement": float(np.mean([float(x["any_kept"]) == e
                                                                              for x, e in zip(a, ev)]))}
        L["attacks"] = att
        orc, rnd = L["oracle"]["FA"], L["random"]["FA"]
        f1 = {}
        for r in C4.ROUTES:
            verdict = "inconclusive"
            for n in C4.FORGE_N:
                f = L[f"v04_{r}_n{n}"]["FA"]
                if f["median"] >= 0.5 * orc["median"] and f["ci95"][0] > rnd["ci95"][1]:
                    verdict = f"practical (n={n})"
                    break
            if verdict == "inconclusive" and all(L[f"v04_{r}_n{n}"]["FA"]["ci95"][1] < 0.5 * orc["median"]
                                                 for n in C4.FORGE_N):
                verdict = "not practical"
            f1[r] = verdict
        L["rules"] = {"F1": f1, "F3_fluent_generic_steering_suffices": rnd["median"] >= 0.5 * orc["median"]}
        L["samples"] = samples(rho, src, seqrep, cut)
        res["levels"][str(rho)] = L
    d = out_dir or LOCK_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / "results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({r: res["levels"][r]["rules"] for r in res["levels"]}, indent=2))
    return res


def samples(rho, src, seqrep, cut):
    """§8 samples, fixed by rule, n = the largest n: at rho = 0.50 the first pool D text of each of the first three keys;
    at rho = 0.70 the first accepted-and-fluent text of each of the first three keys (None if the key has none)."""
    if rho not in (0.50, 0.70):
        return {}
    n, pD = max(C4.FORGE_N), C2.prompts(C2.pools()["D"])
    out = {}
    for r in C4.ROUTES:
        c = f"v04_{r}_n{n}"
        rows = []
        for s in KEYS[:SAMPLE_KEYS]:
            txt, sc, ppl = src[c][s]
            fa = C4.fluent_accept(sc, ppl, seqrep[c][s], cut[s]["thr"], cut[s]["ppl"], cut[s]["seqrep4"])
            hits = [0] if rho == 0.50 else [int(i) for i in np.flatnonzero(fa)[:1]]
            for i in hits:
                rows.append({"key": s, "index": i, "prompt": pD[i], "text": txt[i], "accepted": bool(sc[i] > cut[s]["thr"]),
                             "fluent_accepted": bool(fa[i]), "ppl": ppl[i], "seqrep4": float(seqrep[c][s][i])})
            if not hits:
                rows.append({"key": s, "index": None, "note": "no accepted-and-fluent text"})
        out[c] = rows
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all")
    a = ap.parse_args()
    lock = check_lock()
    DATA.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    phases = "IKR" if a.phase == "all" else a.phase
    tok = None
    if "I" in phases or "K" in phases:
        tok, model = core.load_model()
        if "I" in phases and not have("I_integrity"):
            save_json("I_integrity", phase_i(tok, model))
            print(f"phase I done: pass = {load_json('I_integrity')['pass']}", flush=True)
            if not load_json("I_integrity")["pass"]:
                raise SystemExit("STOP: integrity check failed (protocol §9)")
        if "K" in phases:
            phase_k(tok, model, C2.pools())
        del model
    if "R" in phases:
        phase_r(tok=tok)
    (LOCK_DIR / f"RUN_MANIFEST_{phases}.json").write_text(json.dumps(
        {"lock": lock, "phases_run": phases, "seconds": round(time.time() - t0), "torch": torch.__version__}, indent=2))


if __name__ == "__main__":
    main()
