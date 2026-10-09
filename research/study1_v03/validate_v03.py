"""Input validation for Study 1 v0.3 (protocol §10). Inputs only: no v0.3 forgery or trial text is generated with a study
key, and no v0.3 statistic is computed. The integrity check re-scores v0.2's oracle texts (v0.2 outcomes, already
reported). A pipeline smoke test runs every phase on a validation-only key (seed 0) with tiny sizes in a scratch folder,
and asserts that every result field the protocol lists exists (skill lesson, 2026-09-26).
Run: .venv/bin/python research/study1_v03/validate_v03.py  ->  research/outputs/study1_v0.3/INPUT_VALIDATION.json
"""
import inspect
import json
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

import common3 as C3  # first: sets up the v0.2 import path
import attack2  # noqa: E402  (v0.2)
import attack3  # noqa: E402
import detect2  # noqa: E402
import run_v03  # noqa: E402
from common3 import C2, core

OUT = C2.ROOT / "research" / "outputs" / "study1_v0.3"
BUDGET_H = 9.0
SMOKE_RANDOM_SEED = 1
checks = {}


def check(name, ok, **info):
    checks[name] = {"pass": bool(ok), **info}
    print(("PASS " if ok else "FAIL ") + name, info if info else "", flush=True)


def smoke(tok, model, P):
    """Every phase on the validation key (rho 0.5), tiny sizes, scratch folders; returns the smoke results.json."""
    vs, rho = core.VALIDATION_KEY_SEED, 0.5
    t = C3.tag(vs, rho)
    tmp = Path(tempfile.mkdtemp(prefix="v03_smoke_", dir=C3.HERE.parent / "outputs"))
    fake02, data03, outd = tmp / "v02", tmp / "v03", tmp / "out"
    for d in (fake02, data03):
        d.mkdir()
    for x in ("_feats.npy", "_norms.npy"):
        (fake02 / f"S_C_ref{x}").symlink_to(C3.V02_DATA / f"S_C_ref{x}")
    dev = core.device()
    vk, rk = C2.key(vs, rho), C2.key(SMOKE_RANDOM_SEED, rho)
    pB, pE, pF, pA, pD = (C2.prompts(P[p])[:8] for p in ("B", "E", "F", "A1", "D"))
    obs = core.generate(tok, model, pB, key=vk, layer=C2.LAYER, seed=1)
    (fake02 / f"K_{t}_obs.json").write_text(json.dumps(obs))
    np.save(fake02 / f"K_{t}_obs_feats.npy", C2.all_layer_means(tok, model, obs))
    XE, lE = C2.layer_tokens(tok, model, core.generate(tok, model, pE, key=vk, layer=C2.LAYER, seed=2))
    XF, lF = C2.layer_tokens(tok, model, core.generate(tok, model, pF, seed=3))
    net = detect2.train(XE, lE, XF, lF, dev)
    torch.save(net.state_dict(), fake02 / f"K_{t}_mlp.pt")
    thr = detect2.threshold(detect2.score(net, *C2.layer_tokens(tok, model, core.generate(tok, model, pA, seed=4)), dev))
    summ = {"threshold": thr}
    for name, vec in (("oracle", vk), ("random", rk)):
        txt = core.generate(tok, model, pD[:4], key=vec, layer=C2.LAYER, seed=5)
        (fake02 / f"K_{t}_{name}.json").write_text(json.dumps(txt))
        summ[f"scores_{name}"] = detect2.score(net, *C2.layer_tokens(tok, model, txt), dev).tolist()
        summ[f"ppl_{name}"] = C2.perplexities(tok, model, pD[:4], txt)
    for r in "AB":
        for n in (4, 8):
            summ[f"scores_forge_{r}_n{n}"], summ[f"ppl_forge_{r}_n{n}"] = summ["scores_oracle"], summ["ppl_oracle"]
    (fake02 / f"K_{t}_summary.json").write_text(json.dumps(summ))
    saved = {k: getattr(run_v03, k) for k in ("V02", "DATA", "KEYS", "LEVELS")}
    saved3 = {k: getattr(C3, k) for k in ("FORGE_N", "N_TRIAL", "N_CAND", "N_FORGE")}
    try:
        run_v03.V02, run_v03.DATA, run_v03.KEYS, run_v03.LEVELS = fake02, data03, [vs], [rho]
        C3.FORGE_N, C3.N_TRIAL, C3.N_CAND, C3.N_FORGE = [4, 8], 2, 2, 4
        integ = run_v03.phase_i(tok, model)
        run_v03.save_json("I_integrity", integ)
        run_v03.phase_k(tok, model, P)
        res = run_v03.phase_r(out_dir=outd)
    finally:
        for k, v in saved.items():
            setattr(run_v03, k, v)
        for k, v in saved3.items():
            setattr(C3, k, v)
        shutil.rmtree(tmp)
    return integ, res


def main():
    assert not run_v03.DATA.exists(), "Study 1 v0.3 data already exist: validation must precede any run"
    # ---- reused v0.2 files
    fs = run_v03.reused_files()
    missing = [p.name for p in fs if not p.exists()]
    check("reused_v02_files_present", not missing, n_files=len(fs), missing=missing[:5])
    # ---- pools, holdout, seeds
    P = C2.pools()
    trial_ids = {u["id"] for u in P["C"][:C3.N_TRIAL]}
    check("trial_prompts_attacker_pool_disjoint_from_D", len(trial_ids) == C3.N_TRIAL and
          not (trial_ids & {u["id"] for u in P["D"]}))
    try:
        core.load_prompts("c4", "holdout")
        check("holdout_sealed", False)
    except Exception as e:
        check("holdout_sealed", True, error=type(e).__name__)
    v02_offsets = {1, 2, 3, 4} | {10 + ri * 3 + ni for ri in range(2) for ni in range(3)}
    v03_offsets = {20 + 3 * ri + ni for ri in range(2) for ni in range(len(C3.FORGE_N))} | {50}
    check("seeds_disjoint_from_v02", not (v02_offsets & v03_offsets) and max(v03_offsets) < 100,
          v03_offsets=sorted(v03_offsets))
    check("smoke_keys_not_study_keys", SMOKE_RANDOM_SEED not in set(C2.STUDY_KEYS) | set(C2.CONTROL_KEYS) |
          set(core.TUNING_KEY_SEEDS) | {core.VALIDATION_KEY_SEED, core.NULL_KEY_SEED})
    # ---- attack module: isolation, equivalence with v0.2 (first candidate), selection logic
    src = inspect.getsource(attack3)
    banned = ("import core", "import common", "import detect2", "import torch", "make_key", "LAYER", "C2.", "C3.")
    check("attack_isolation", not any(b in src for b in banned) and
          list(inspect.signature(attack3.candidates).parameters) == ["route", "obs", "ref", "k", "rho", "ref_norms", "m"] and
          list(inspect.signature(attack3.select).parameters) == ["cands", "q_obs", "q_trials", "tol"])
    rng = np.random.default_rng(0)
    L, dd = 6, 64
    ref = rng.normal(size=(2000, L, dd)) * 0.01
    v = np.zeros(dd)
    v[[3, 17, 40, 55]] = [1, -1, 0.5, -0.8]
    obs = rng.normal(size=(256, L, dd)) * 0.01
    obs[:, 4] += 0.01 * v
    nr = np.full(L, 10.0)
    ok = True
    for r in "AB":
        cands, prof = attack3.candidates(r, obs, ref, 4, 0.5, nr, 5)
        l2, v2, p2 = attack2.route_a(obs, ref, 4, 0.5, nr) if r == "A" else attack2.route_b(obs, ref, 0.5, nr)
        ok &= (cands[0]["layer"] == l2 and np.allclose(cands[0]["vec"], v2) and np.allclose(prof, p2) and len(cands) == 5
               and len({c["layer"] for c in cands}) == 5 and all(abs(np.linalg.norm(c["vec"]) - 5.0) < 1e-3 for c in cands))
    check("candidates_first_equals_v02_route", ok)
    cs = [{"profile": 5.0}, {"profile": 4.0}, {"profile": 3.0}]
    s1 = attack3.select(cs, 10.0, [13.0, 11.0, 9.0], 1.2)
    s2 = attack3.select(cs, 10.0, [20.0, 15.0, float("nan")], 1.2)
    check("select_logic", s1 == (1, True, [1, 2]) and s2 == (1, False, []), s1=str(s1), s2=str(s2))
    fa = C3.fluent_accept([0.9, 0.9, 0.1, 0.9], [5, 50, 5, 10], 0.5, 10.0)
    cut = C3.fluent_cut(np.arange(1, 101))
    check("fluent_accept_and_cut", fa.tolist() == [1, 0, 0, 1] and abs(cut - 95.05) < 1e-9, cut=cut)
    # ---- lock enforcement (no lock yet -> refuse)
    try:
        run_v03.check_lock()
        check("runner_refuses_without_lock", False)
    except (FileNotFoundError, AssertionError, KeyError) as e:
        check("runner_refuses_without_lock", True, error=type(e).__name__)

    # ---- model: integrity on two real key-levels; continuation-only perplexity; smoke; timing
    tok, model = core.load_model()
    integ = run_v03.phase_i(tok, model, keys=[1001, 1008], levels=[0.35, 0.70])
    check("integrity_reloaded_probes_rescore_v02_oracle", integ["pass"], rows=integ["rows"])
    cref = json.loads((C3.V02_DATA / "S_C_ref.json").read_text())[:4]
    q_c = C3.ppl_cont_only(tok, model, cref)
    q_p = C2.perplexities(tok, model, C2.prompts(P["C"])[:4], cref)
    check("cont_only_ppl_plausible", all(np.isfinite(q_c)) and all(1.0 < q < 200.0 for q in q_c),
          cont_only=[round(q, 2) for q in q_c], with_prompt=[round(q, 2) for q in q_p])
    t0 = time.time()
    integ_s, res_s = smoke(tok, model, P)
    lv = res_s["levels"]["0.5"]
    need = ["oracle", "random"] + [f"{p}_{r}_n{n}" for p in ("v03", "v02") for r in "AB" for n in (4, 8)]
    fields_ok = (integ_s["pass"] and all(k in lv and {"FA", "acceptance", "fluent_share_median", "ppl_ratio_to_oracle_median"}
                                         <= set(lv[k]) for k in need)
                 and set(lv["rules"]["F1"]) == {"A", "B"} and "F3_fluent_generic_steering_suffices" in lv["rules"]
                 and all({"selected_layers", "layer_hits", "selected_is_top_candidate", "none_passed", "n_kept",
                          "median_cos_true", "check_vs_eval_agreement"} <= set(lv["attacks"][f"{r}_n{n}"])
                         for r in "AB" for n in (4, 8)))
    check("pipeline_smoke_all_fields", fields_ok, seconds=round(time.time() - t0),
          note="validation key, tiny sizes, scratch folder deleted; verdicts carry no information")
    # timing
    pD = C2.prompts(P["D"])[:16]
    t = time.time()
    texts = core.generate(tok, model, pD, key=C2.key(core.VALIDATION_KEY_SEED, 0.5), layer=C2.LAYER, seed=0)
    t_gen = (time.time() - t) / 16
    t = time.time()
    C3.ppl_cont_only(tok, model, texts)
    t_cont = (time.time() - t) / 16
    t = time.time()
    C2.layer_tokens(tok, model, texts)
    t_tok = (time.time() - t) / 16
    t = time.time()
    C2.perplexities(tok, model, pD, texts)
    t_ppl = (time.time() - t) / 16
    del model
    n_att = len(C2.STUDY_KEYS) * len(C3.LEVELS) * len(C3.FORGE_N) * len(C3.ROUTES)
    trials, forg = n_att * C3.N_CAND * C3.N_TRIAL, n_att * C3.N_FORGE
    qobs = len(C2.STUDY_KEYS) * len(C3.LEVELS) * max(C3.FORGE_N)
    integ_texts = len(C2.STUDY_KEYS) * len(C3.LEVELS) * 100
    hours = ((trials + forg) * t_gen + (trials + qobs) * t_cont + (forg + integ_texts) * t_tok + forg * t_ppl) / 3600
    check("timing_budget", hours <= BUDGET_H, projected_hours=round(hours, 1), s_per_gen=round(t_gen, 3),
          s_per_cont_ppl=round(t_cont, 3), s_per_tokens=round(t_tok, 3), s_per_ppl=round(t_ppl, 3),
          generations=trials + forg)
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"all_pass": all(c["pass"] for c in checks.values()), "checks": checks,
               "note": "inputs only; no v0.3 trial or forgery with a study key; no v0.3 statistic",
               "code_sha256": {p.name: run_v03.sha(p) for p in run_v03.CODE}}
    (OUT / "INPUT_VALIDATION.json").write_text(json.dumps(summary, indent=2))
    print("ALL PASS" if summary["all_pass"] else "SOME CHECKS FAILED", flush=True)


if __name__ == "__main__":
    main()
