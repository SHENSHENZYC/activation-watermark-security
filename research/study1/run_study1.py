"""Study 1 runner (STUDY1_PROTOCOL_v0.1). Refuses to run unless PRE_RUN_LOCK.json matches the current file hashes.

Phases (each checkpointed under research/study1/data/v0.1/, git-ignored):
  A  reproduction gate G1 on tuning keys (pool T)          -> may switch alpha 5 -> 10 once
  B  null sets: pool A unwatermarked + human texts; pool C attacker reference
  C  observed watermarked texts (pool B) and evaluation texts (pool E), per study key
  D  attack: key estimates for every n in N_GRID (attack.py sees features only)
  E  spoof, oracle and random-key control generations on pool D
  F  detection, gates, rules, bootstrap -> outputs/study1_v0.1/results.json
  G  secondary: spoof-text perplexity under Phi-3.5-mini
Run: .venv/bin/python research/study1/run_study1.py --model qwen|llama [--phase A|B|C|D|E|F|G|all]
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch

import attack
import core
import detect

HERE = Path(__file__).parent
LOCK_DIR = core.ROOT / "research" / "outputs" / "study1_v0.1"
DATA = HERE / "data" / "v0.1" / core.MODEL_NAME  # reset by set_model()
OUT = LOCK_DIR / core.MODEL_NAME


def set_model(name):
    global DATA, OUT
    core.configure(name)
    DATA = HERE / "data" / "v0.1" / name
    OUT = LOCK_DIR / name
PROTOCOL = core.ROOT / "research" / "STUDY1_PROTOCOL_v0.1.md"
CODE = [HERE / f for f in ("core.py", "detect.py", "attack.py", "run_study1.py")]
BOOT_B, BOOT_SEED = 2000, 20260925


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_lock():
    lock = json.loads((LOCK_DIR / "PRE_RUN_LOCK.json").read_text())
    assert lock["protocol_sha256"] == sha(PROTOCOL), "protocol changed since lock"
    for p in CODE:
        assert lock["script_sha256"][p.name] == sha(p), f"{p.name} changed since lock"
    return lock


def save(name, **arrays):
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DATA / f"{name}.npz", **arrays)


def load(name):
    return dict(np.load(DATA / f"{name}.npz", allow_pickle=False))


def done(name):
    return (DATA / f"{name}.npz").exists()


def save_texts(name, texts):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / f"{name}.json").write_text(json.dumps(texts))


def state():
    p = DATA / "state.json"
    return json.loads(p.read_text()) if p.exists() else {}


def set_state(**kw):
    s = state()
    s.update(kw)
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "state.json").write_text(json.dumps(s, indent=2))


def gen_and_features(tok, model, name, prompts, key, layer, seed, grads=False, layers_all=True):
    if done(name):
        return load(name)
    texts = core.generate(tok, model, prompts, key=key, layer=layer, seed=seed)
    save_texts(name, texts)
    f = core.reencode_features(tok, model, texts)
    arrays = {"feats": f if layers_all else f[:, core.LAYER]}
    if grads:
        arrays["grads"] = core.score_gradients(tok, model, texts)
    save(name, **arrays)
    return arrays


def layer_feats(arr):
    f = arr["feats"]
    return f[:, core.LAYER] if f.ndim == 3 else f


# ------------------------------------------------------------------ phases
def phase_a(tok, model, pools, d):
    null = core.null_keys(d, 1.0).numpy()
    prompts = [u["prompt"] for u in pools["T"]]
    for alpha in (core.ALPHA_DEFAULT, core.ALPHA_RETRY):
        tprs = []
        for i, s in enumerate(core.TUNING_KEY_SEEDS):
            key = core.make_key(s, d, alpha)
            arr = gen_and_features(tok, model, f"A_tune_a{int(alpha)}_k{s}", prompts[i * 100:(i + 1) * 100], key,
                                   core.LAYER, seed=s, layers_all=False)
            _, p = detect.dcos(layer_feats(arr), key.numpy(), null)
            tprs.append(detect.accept_rate(p))
        g1 = float(np.mean(tprs)) >= 0.80
        set_state(**{f"G1_alpha{int(alpha)}_tprs": tprs, f"G1_alpha{int(alpha)}_pass": g1})
        if g1:
            set_state(alpha=alpha)
            return alpha
    set_state(alpha=None, stop="G1 failed at alpha 5 and 10")
    raise SystemExit("STOP: G1 failed at alpha 5 and 10 (protocol §10)")


def phase_b(tok, model, pools):
    gen_and_features(tok, model, "B_poolA_vanilla", [u["prompt"] for u in pools["A"]], None, core.LAYER, seed=11,
                     grads=True)
    if not done("B_poolA_human"):
        texts = [u["human_continuation"] for u in pools["A"]]
        save_texts("B_poolA_human", texts)
        save("B_poolA_human", feats=core.reencode_features(tok, model, texts)[:, core.LAYER],
             grads=core.score_gradients(tok, model, texts))
    gen_and_features(tok, model, "B_poolC_ref", [u["prompt"] for u in pools["C"]], None, core.LAYER, seed=13)


def phase_c(tok, model, pools, d, alpha):
    for s in core.STUDY_KEY_SEEDS:
        key = core.make_key(s, d, alpha)
        gen_and_features(tok, model, f"C_obs_k{s}", [u["prompt"] for u in pools["B"]], key, core.LAYER, seed=s)
        gen_and_features(tok, model, f"C_eval_k{s}", [u["prompt"] for u in pools["E"]], key, core.LAYER,
                         seed=s + 50000, grads=True, layers_all=False)


def phase_d(d, alpha):
    """Attack. Only features (never keys) are passed to attack.estimate; the comparison to v happens here afterwards."""
    if done("D_estimates"):
        return load("D_estimates")
    ref = load("B_poolC_ref")["feats"]
    k = core.n_support(d)
    rows = {"key": [], "n": [], "sparse": [], "layer_hat": [], "cos": [], "support_hit": []}
    vhats, zprofs = [], []
    for s in core.STUDY_KEY_SEEDS:
        obs = load(f"C_obs_k{s}")["feats"]
        v = core.make_key(s, d, alpha).numpy()
        for n in core.N_GRID:
            for sparse in (True, False):
                lh, vh, zp = attack.estimate(obs[:n], ref, k, alpha, sparse=sparse)
                if n == 1024 and sparse:
                    zprofs.append(zp)
                cos = float(vh @ v / (np.linalg.norm(vh) * np.linalg.norm(v)))
                hit = len(set(np.flatnonzero(vh)) & set(np.flatnonzero(v))) / k if sparse else np.nan
                for c, val in zip(rows, (s, n, sparse, lh, cos, hit)):
                    rows[c].append(val)
                vhats.append(vh)
    arrays = {c: np.array(v) for c, v in rows.items()}
    arrays["vhat"] = np.stack(vhats)
    arrays["z_profile_n1024"] = np.stack(zprofs)  # [keys, layers]: max_i |z| per layer (descriptive)
    save("D_estimates", **arrays)
    return arrays


def phase_e(tok, model, pools, d, alpha):
    est = load("D_estimates")
    prompts = [u["prompt"] for u in pools["D"]]
    for s in core.STUDY_KEY_SEEDS:
        for n in core.SPOOF_N:
            i = np.flatnonzero((est["key"] == s) & (est["n"] == n) & est["sparse"])[0]
            vh = torch.tensor(est["vhat"][i])
            gen_and_features(tok, model, f"E_spoof_k{s}_n{n}", prompts, vh, int(est["layer_hat"][i]),
                             seed=s * 10 + n, grads=True, layers_all=False)
        gen_and_features(tok, model, f"E_oracle_k{s}", prompts, core.make_key(s, d, alpha), core.LAYER,
                         seed=s + 70000, grads=True, layers_all=False)
        ctrl = core.RANDOM_CONTROL_SEEDS[core.STUDY_KEY_SEEDS.index(s)]
        gen_and_features(tok, model, f"E_random_k{s}", prompts, core.make_key(ctrl, d, alpha), core.LAYER,
                         seed=s + 90000, grads=True, layers_all=False)


def cluster_boot_median(per_key_samples, rng):
    """per_key_samples: list of 1-D arrays (per-text 0/1 or values) per key. Returns a 95% CI for the median of key means."""
    K = len(per_key_samples)
    meds = []
    for _ in range(BOOT_B):
        ks = rng.integers(0, K, K)
        means = [per_key_samples[k][rng.integers(0, len(per_key_samples[k]), len(per_key_samples[k]))].mean() for k in ks]
        meds.append(np.median(means))
    return [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))]


def phase_f(d, alpha):
    rng = np.random.default_rng(BOOT_SEED)
    null = core.null_keys(d, 1.0).numpy()
    keys = {s: core.make_key(s, d, alpha).numpy() for s in core.STUDY_KEY_SEEDS}
    res = {"alpha": alpha, "state": state()}
    # G2: FPR on unwatermarked and human texts, all study keys
    for nm in ("B_poolA_vanilla", "B_poolA_human"):
        arr = load(nm)
        for det, fn, x in (("dcos", detect.dcos, layer_feats(arr)), ("dscore", detect.dscore, arr["grads"])):
            ps = np.concatenate([fn(x, keys[s], null)[1] for s in core.STUDY_KEY_SEEDS])
            res[f"FPR_{det}_{nm}"] = detect.accept_rate(ps)
    g2 = all(0.003 <= res[f"FPR_dcos_{nm}"] <= 0.02 for nm in ("B_poolA_vanilla", "B_poolA_human"))
    # per-key acceptance on pool D (spoof, oracle, random) and pool E (eval TPR)
    acc = {}
    for det in ("dcos", "dscore"):
        fn = detect.dcos if det == "dcos" else detect.dscore
        for s in core.STUDY_KEY_SEEDS:
            names = [f"E_spoof_k{s}_n{n}" for n in core.SPOOF_N] + [f"E_oracle_k{s}", f"E_random_k{s}", f"C_eval_k{s}"]
            for nm in names:
                arr = load(nm)
                x = layer_feats(arr) if det == "dcos" else arr["grads"]
                acc[(det, nm)] = (fn(x, keys[s], null)[1] <= 0.01).astype(float)
    summ = {}
    for det in ("dcos", "dscore"):
        for label, pat in [("oracle", "E_oracle_k{}"), ("random", "E_random_k{}"), ("eval_tpr", "C_eval_k{}")] + [
                (f"spoof_n{n}", "E_spoof_k{}_n" + str(n)) for n in core.SPOOF_N]:
            samples = [acc[(det, pat.format(s))] for s in core.STUDY_KEY_SEEDS]
            means = [float(x.mean()) for x in samples]
            summ[f"{det}_{label}"] = {"per_key": means, "median": float(np.median(means)),
                                      "ci95": cluster_boot_median(samples, rng)}
    res["acceptance"] = summ
    g3 = summ["dcos_random"]["median"] <= 0.02
    g4 = summ["dcos_oracle"]["median"] >= 0.80
    # recovery (R1)
    est = load("D_estimates")
    rec = {}
    for n in core.N_GRID:
        m = (est["n"] == n) & est["sparse"]
        md = (est["n"] == n) & ~est["sparse"]
        rec[n] = {"median_cos_sparse": float(np.median(est["cos"][m])), "median_cos_dense": float(np.median(est["cos"][md])),
                  "layer_hits": int((est["layer_hat"][m] == core.LAYER).sum()),
                  "median_support_hit": float(np.median(est["support_hit"][m])),
                  "per_key_cos_sparse": est["cos"][m].tolist()}
    res["recovery"] = rec
    need_hits = int(np.ceil(0.875 * len(core.STUDY_KEY_SEEDS)))  # 14/16 for Qwen, 7/8 for Llama
    n_star = next((n for n in core.N_GRID if rec[n]["median_cos_sparse"] >= 0.9 and rec[n]["layer_hits"] >= need_hits), None)
    r1 = ("succeeds" if n_star else ("partial" if rec[1024]["median_cos_sparse"] >= 0.5 else "fails at this budget"))
    # R2
    r2 = "inconclusive"
    for n in [x for x in core.SPOOF_N if x <= 256]:
        sp = summ[f"dcos_spoof_n{n}"]
        if sp["median"] >= 0.5 and sp["ci95"][0] > summ["dcos_random"]["ci95"][1]:
            r2 = f"practical (n={n})"
            break
    if r2 == "inconclusive" and summ["dcos_spoof_n1024"]["median"] < 0.10:
        r2 = "not practical"
    res["gates"] = {"G1": state().get(f"G1_alpha{int(alpha)}_pass"), "G2": g2, "G3": g3, "G4": g4}
    res["rules"] = {"R1": r1, "n_star": n_star, "R2": r2, "layer_hits_needed": need_hits,
                    "valid": all(bool(v) for v in res["gates"].values())}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({"gates": res["gates"], "rules": res["rules"]}, indent=2))


def phase_g():
    """Secondary: perplexity of spoof vs oracle texts under Phi-3.5-mini (descriptive)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    rev = "2fe192450127e6a83f7441aef6e3ca586c338b77"
    tok = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct", revision=rev)
    model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3.5-mini-instruct", revision=rev,
                                                 dtype=torch.bfloat16).to(core.device()).eval()

    def ppl(texts):
        out = []
        for t in texts:
            e = tok(t, return_tensors="pt").to(core.device())
            with torch.no_grad():
                out.append(float(torch.exp(model(**e, labels=e["input_ids"]).loss)))
        return out

    res = {}
    for s in core.STUDY_KEY_SEEDS:
        o = np.median(ppl(json.loads((DATA / f"E_oracle_k{s}.json").read_text())[:50]))
        for n in core.SPOOF_N:
            sp = np.median(ppl(json.loads((DATA / f"E_spoof_k{s}_n{n}.json").read_text())[:50]))
            res.setdefault(f"n{n}", []).append(float(sp / o))
    (OUT / "quality_ppl_ratio.json").write_text(json.dumps({k: {"per_key": v, "median": float(np.median(v))}
                                                           for k, v in res.items()}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all")
    ap.add_argument("--model", choices=sorted(core.MODELS), required=True)
    a = ap.parse_args()
    set_model(a.model)
    lock = check_lock()
    t0 = time.time()
    pools = core.assign_pools()
    tok, model = core.load_model()
    d = model.config.hidden_size
    phases = "ABCDEFG" if a.phase == "all" else a.phase
    alpha = state().get("alpha")
    if "A" in phases:
        alpha = phase_a(tok, model, pools, d)
    assert alpha is not None, "run phase A first"
    if "B" in phases:
        phase_b(tok, model, pools)
    if "C" in phases:
        phase_c(tok, model, pools, d, alpha)
    if "D" in phases:
        phase_d(d, alpha)
    if "E" in phases:
        phase_e(tok, model, pools, d, alpha)
    if "F" in phases:
        phase_f(d, alpha)
    if "G" in phases:
        del model
        phase_g()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"model": a.model, "lock": lock, "phases_run": phases, "seconds": round(time.time() - t0), "torch": torch.__version__,
                "data_files": {p.name: sha(p) for p in sorted(DATA.glob("*.npz"))}}
    (OUT / f"RUN_MANIFEST_{phases}.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
