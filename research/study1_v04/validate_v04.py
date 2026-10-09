"""Input validation for Study 1 v0.4 (protocol §10). Inputs only: no v0.4 trial or forgery text is generated with a study
key, and no v0.4 statistic is computed. The integrity check re-scores v0.2's oracle texts, and the reproduction check
recomputes v0.3's locked FA medians with the repetition term switched off (v0.2 and v0.3 outcomes, already reported;
no repetition-aware rate is computed). A pipeline smoke test runs every phase on a validation-only key (seed 0) with
tiny sizes in a scratch folder, and asserts that every result field in protocol §5 and §8 exists.
Run: .venv/bin/python research/study1_v04/validate_v04.py  ->  research/outputs/study1_v0.4/INPUT_VALIDATION.json
"""
import inspect
import json
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

import common4 as C4  # first: sets up the import paths
import attack4  # noqa: E402
import detect2  # noqa: E402
import run_v04  # noqa: E402
from common4 import C2, core

OUT = C2.ROOT / "research" / "outputs" / "study1_v0.4"
BUDGET_H = 9.0
SMOKE_RANDOM_SEED = 1
SMOKE_LEVELS = [0.50, 0.70]   # both sample rules (§8) are exercised
checks = {}


def check(name, ok, **info):
    checks[name] = {"pass": bool(ok), **info}
    print(("PASS " if ok else "FAIL ") + name, info if info else "", flush=True)


def smoke(tok, model, P):
    """Every phase on the validation key at rho 0.5 and 0.7, tiny sizes, scratch folders; returns the smoke results."""
    vs = core.VALIDATION_KEY_SEED
    tmp = Path(tempfile.mkdtemp(prefix="v04_smoke_", dir=C4.HERE.parent / "outputs"))
    fake02, fake03, data04, outd = tmp / "v02", tmp / "v03", tmp / "v04", tmp / "out"
    for d in (fake02, fake03, data04):
        d.mkdir()
    for x in ("_feats.npy", "_norms.npy"):
        (fake02 / f"S_C_ref{x}").symlink_to(C4.V02_DATA / f"S_C_ref{x}")
    dev = core.device()
    pB, pE, pF, pA, pD = (C2.prompts(P[p])[:8] for p in ("B", "E", "F", "A1", "D"))
    for rho in SMOKE_LEVELS:
        t = C4.tag(vs, rho)
        vk, rk = C2.key(vs, rho), C2.key(SMOKE_RANDOM_SEED, rho)
        obs = core.generate(tok, model, pB, key=vk, layer=C2.LAYER, seed=1)
        (fake02 / f"K_{t}_obs.json").write_text(json.dumps(obs))
        np.save(fake02 / f"K_{t}_obs_feats.npy", C2.all_layer_means(tok, model, obs))
        XE, lE = C2.layer_tokens(tok, model, core.generate(tok, model, pE, key=vk, layer=C2.LAYER, seed=2))
        XF, lF = C2.layer_tokens(tok, model, core.generate(tok, model, pF, seed=3))
        net = detect2.train(XE, lE, XF, lF, dev)
        torch.save(net.state_dict(), fake02 / f"K_{t}_mlp.pt")
        thr = detect2.threshold(detect2.score(net, *C2.layer_tokens(tok, model, core.generate(tok, model, pA, seed=4)),
                                              dev))
        summ = {"threshold": thr}
        for name, vec in (("oracle", vk), ("random", rk)):
            txt = core.generate(tok, model, pD[:4], key=vec, layer=C2.LAYER, seed=5)
            (fake02 / f"K_{t}_{name}.json").write_text(json.dumps(txt))
            summ[f"scores_{name}"] = detect2.score(net, *C2.layer_tokens(tok, model, txt), dev).tolist()
            summ[f"ppl_{name}"] = C2.perplexities(tok, model, pD[:4], txt)
        orc = json.loads((fake02 / f"K_{t}_oracle.json").read_text())
        v03 = {"attacks": {}}
        for r in "AB":
            for n in (4, 8):   # stand-ins for v0.2's and v0.3's forgeries: the oracle texts and their scores
                summ[f"scores_forge_{r}_n{n}"], summ[f"ppl_forge_{r}_n{n}"] = summ["scores_oracle"], summ["ppl_oracle"]
                (fake02 / f"K_{t}_forge_{r}_n{n}.json").write_text(json.dumps(orc))
                (fake03 / f"K_{t}_forge3_{r}_n{n}.json").write_text(json.dumps(orc))
                v03["attacks"][f"{r}_n{n}"] = {"scores": summ["scores_oracle"], "ppl": summ["ppl_oracle"]}
        (fake02 / f"K_{t}_summary.json").write_text(json.dumps(summ))
        (fake03 / f"K_{t}_v03.json").write_text(json.dumps(v03))
    saved = {k: getattr(run_v04, k) for k in ("V02", "V03", "DATA", "KEYS", "LEVELS")}
    saved4 = {k: getattr(C4, k) for k in ("FORGE_N", "N_TRIAL", "N_CAND", "N_FORGE")}
    try:
        run_v04.V02, run_v04.V03, run_v04.DATA, run_v04.KEYS, run_v04.LEVELS = fake02, fake03, data04, [vs], SMOKE_LEVELS
        C4.FORGE_N, C4.N_TRIAL, C4.N_CAND, C4.N_FORGE = [4, 8], 2, 2, 4
        integ = run_v04.phase_i(tok, model)
        run_v04.save_json("I_integrity", integ)
        run_v04.phase_k(tok, model, P)
        res = run_v04.phase_r(out_dir=outd, tok=tok)
    finally:
        for k, v in saved.items():
            setattr(run_v04, k, v)
        for k, v in saved4.items():
            setattr(C4, k, v)
        shutil.rmtree(tmp)
    return integ, res


def smoke_fields_ok(integ, res):
    need_c = ["oracle", "random"] + [f"{p}_{r}_n{n}" for p in ("v04", "v03", "v02") for r in "AB" for n in (4, 8)]
    c_fields = {"FA", "acceptance", "FA_ppl_only_median", "FA_rep3_median", "fluent_share_median",
                "repetitive_share_median", "ppl_ratio_to_oracle_median", "seqrep4_median"}
    a_fields = {"selected_layers", "layer_hits", "selected_is_top_candidate", "none_passed", "n_kept", "m_selected",
                "median_cos_true", "check_vs_eval_agreement"}
    s_fields = {"key", "index", "prompt", "text", "accepted", "fluent_accepted", "ppl", "seqrep4"}
    ok = integ["pass"]
    for lv in ("0.5", "0.7"):
        L = res["levels"][lv]
        ok &= all(c in L and c_fields <= set(L[c]) for c in need_c)
        ok &= set(L["cut_per_key"]) == {"ppl", "seqrep4", "rep3"}
        ok &= set(L["rules"]["F1"]) == {"A", "B"} and "F3_fluent_generic_steering_suffices" in L["rules"]
        ok &= all(a_fields <= set(L["attacks"][f"{r}_n{n}"]) for r in "AB" for n in (4, 8))
        ok &= set(L["samples"]) == {"v04_A_n8", "v04_B_n8"}
        ok &= all(len(rows) == 1 and (s_fields <= set(rows[0]) or rows[0]["index"] is None)
                  for rows in L["samples"].values())
    ok &= all(set(res["levels"]["0.5"]["samples"][c][0]) >= s_fields and res["levels"]["0.5"]["samples"][c][0]["index"] == 0
              for c in ("v04_A_n8", "v04_B_n8"))
    return bool(ok)


def main():
    assert not run_v04.DATA.exists(), "Study 1 v0.4 data already exist: validation must precede any run"
    # ---- reused files
    f2, f3 = run_v04.reused_v02_files(), run_v04.reused_v03_files()
    miss = [p.name for p in f2 + f3 if not p.exists()]
    lock03 = json.loads((C2.ROOT / "research" / "outputs" / "study1_v0.3" / "PRE_RUN_LOCK.json").read_text())
    same02 = {p.name for p in f2} == set(lock03["reused_v02_sha256"]) and all(
        lock03["reused_v02_sha256"][p.name] == run_v04.sha(p) for p in f2)
    check("reused_files_present_and_hash", not miss and len(f2) == 243 and len(f3) == 120 and same02,
          n_v02=len(f2), n_v03=len(f3), v02_equal_to_v03_lock=same02, missing=miss[:5])
    # ---- pools, holdout, seeds
    P = C2.pools()
    trial_ids = {u["id"] for u in P["C"][:C4.N_TRIAL]}
    check("trial_prompts_attacker_pool_disjoint_from_D", len(trial_ids) == C4.N_TRIAL and
          not (trial_ids & {u["id"] for u in P["D"]}))
    try:
        core.load_prompts("c4", "holdout")
        check("holdout_sealed", False)
    except Exception as e:
        check("holdout_sealed", True, error=type(e).__name__)
    v02_off = {1, 2, 3, 4} | {10 + ri * 3 + ni for ri in range(2) for ni in range(3)}
    v03_off = {20 + 3 * ri + ni for ri in range(2) for ni in range(2)} | {50}
    v04_off = {C4.SEED_FORGE + 3 * ri + ni for ri in range(len(C4.ROUTES)) for ni in range(len(C4.FORGE_N))} | {
        C4.SEED_TRIAL}
    check("seeds_disjoint_from_v02_v03", not (v04_off & (v02_off | v03_off)) and max(v04_off) < 100,
          v04_offsets=sorted(v04_off))
    check("smoke_keys_not_study_keys", SMOKE_RANDOM_SEED not in set(C2.STUDY_KEYS) | set(C2.CONTROL_KEYS) |
          set(core.TUNING_KEY_SEEDS) | {core.VALIDATION_KEY_SEED, core.NULL_KEY_SEED})
    # ---- attack module: isolation; seq-rep-4; selection
    src = inspect.getsource(attack4)
    banned = ("import core", "import common", "import detect2", "import torch", "make_key", "LAYER", "C2.", "C3.", "C4.")
    check("attack_isolation", not any(b in src for b in banned) and
          list(inspect.signature(attack4.select).parameters) == ["cands", "q_obs", "q_trials", "m_trials", "tol", "max_rep"]
          and list(inspect.signature(attack4.n_repetitive).parameters) == ["trial_rep", "r_obs"]
          and list(inspect.signature(attack4.rep_threshold).parameters) == ["obs_rep", "q"])
    sr = attack4.seqrep4_ids
    check("seqrep4_constructed", sr(list(range(50))) == 0.0 and abs(sr([1, 2, 3] * 10) - (1 - 3 / 27)) < 1e-12
          and abs(sr([5] * 10) - (1 - 1 / 7)) < 1e-12 and sr([1, 2, 3]) == 0.0 and sr([]) == 0.0
          and sr([1, 2, 3, 4]) == 0.0, loop=sr([1, 2, 3] * 10))
    tok = run_v04.load_tok()
    t_ids = tok("the cat sat on the mat", add_special_tokens=False)["input_ids"]
    long_txt = " ".join(f"w{i}" for i in range(400))
    check("seqrep4_tokens_first_256", C4.seqrep4(tok, ["the cat sat on the mat"])[0] == sr(t_ids)
          and C4.seqrep4(tok, [long_txt])[0] == sr(tok(long_txt, add_special_tokens=False)["input_ids"][:256]))
    check("rep3_matches_v03_definition", abs(C4.rep3("a b c a b c a b c") - (1 - 3 / 7)) < 1e-12 and C4.rep3("a b") == 0.0)
    check("attacker_rep_threshold_and_count", attack4.rep_threshold(np.arange(101) / 100, 0.95) == 0.95
          and attack4.n_repetitive([0.1, 0.96, 0.95, 1.0], 0.95) == 2)
    cs = [{"profile": 5.0}, {"profile": 4.0}, {"profile": 3.0}]
    s1 = attack4.select(cs, 10.0, [11.0, 11.0, 9.0], [3, 1, 0], 1.2, 2)          # 0 fails on repetition
    s2 = attack4.select(cs, 10.0, [11.0, 11.0, 9.0], [0, 2, 0], 1.2, 2)          # all kept -> largest profile
    s3 = attack4.select(cs, 10.0, [13.0, 11.0, 9.0], [3, 3, 5], 1.2, 2)         # none: fewest m, tie -> smaller q
    s4 = attack4.select(cs, 10.0, [float("nan"), 20.0, 20.0], [0, 0, 1], 1.2, 2)  # none: nan q loses the m tie
    s5 = attack4.select(cs, 10.0, [13.0, 13.0, 13.0], [0, 0, 0], 1.2, 2)         # none on perplexity only
    check("select_logic", s1 == (1, True, [1, 2]) and s2 == (0, True, [0, 1, 2]) and s3 == (1, False, [])
          and s4 == (1, False, []) and s5 == (0, False, []), s1=str(s1), s2=str(s2), s3=str(s3), s4=str(s4), s5=str(s5))
    fa_on = C4.fluent_accept([0.9, 0.9, 0.1, 0.9, 0.9], [5, 50, 5, 10, 5], [0, 0, 0, 0, 0.5], 0.5, 10.0, 0.1)
    fa_off = C4.fluent_accept([0.9, 0.9, 0.1, 0.9, 0.9], [5, 50, 5, 10, 5], [0, 0, 0, 0, 0.5], 0.5, 10.0, np.inf)
    check("fluent_accept_and_cut", fa_on.tolist() == [1, 0, 0, 1, 0] and fa_off.tolist() == [1, 0, 0, 1, 1]
          and abs(C4.cut(np.arange(1, 101)) - 95.05) < 1e-9)
    # ---- reproduction: the v0.4 scoring code with the repetition term off reproduces v0.3's locked FA medians
    v03 = json.loads(run_v04.V03_RESULTS.read_text())
    diffs = []
    for rho in C4.LEVELS:
        srcs = run_v04.conditions(rho, include_v04=False)
        cut = run_v04.cuts(tok, rho, srcs)
        for name, d in srcs.items():
            m = run_v04.med_of_meds(run_v04.fa_per_key(d, cut, {s: np.zeros(len(d[s][0])) for s in run_v04.KEYS}, None))
            diffs.append(abs(m - v03["levels"][str(rho)][name]["FA"]["median"]))
        diffs.append(max(abs(a - b) for a, b in zip([cut[s]["ppl"] for s in run_v04.KEYS],
                                                    v03["levels"][str(rho)]["fluent_cut_per_key"])))
    check("repetition_off_reproduces_v03_FA_medians", max(diffs) == 0.0, n_compared=len(diffs), max_diff=max(diffs))
    # ---- lock enforcement (no lock yet -> refuse)
    try:
        run_v04.check_lock()
        check("runner_refuses_without_lock", False)
    except (FileNotFoundError, AssertionError, KeyError) as e:
        check("runner_refuses_without_lock", True, error=type(e).__name__)

    # ---- model: integrity on two real key-levels; smoke; timing
    tok, model = core.load_model()
    integ = run_v04.phase_i(tok, model, keys=[1001, 1008], levels=[0.35, 0.70])
    check("integrity_reloaded_probes_rescore_v02_oracle", integ["pass"], rows=integ["rows"])
    t0 = time.time()
    integ_s, res_s = smoke(tok, model, P)
    check("pipeline_smoke_all_fields", smoke_fields_ok(integ_s, res_s), seconds=round(time.time() - t0),
          note="validation key, rho 0.5 and 0.7, tiny sizes, scratch folder deleted; verdicts carry no information")
    pD = C2.prompts(P["D"])[:16]
    t = time.time()
    texts = core.generate(tok, model, pD, key=C2.key(core.VALIDATION_KEY_SEED, 0.5), layer=C2.LAYER, seed=0)
    t_gen = (time.time() - t) / 16
    t = time.time()
    C4.ppl_cont_only(tok, model, texts)
    t_cont = (time.time() - t) / 16
    t = time.time()
    C2.layer_tokens(tok, model, texts)
    t_tok = (time.time() - t) / 16
    t = time.time()
    C2.perplexities(tok, model, pD, texts)
    t_ppl = (time.time() - t) / 16
    t = time.time()
    C4.seqrep4(tok, texts)
    t_rep = (time.time() - t) / 16
    del model
    n_att = len(C2.STUDY_KEYS) * len(C4.LEVELS) * len(C4.FORGE_N) * len(C4.ROUTES)
    trials, forg = n_att * C4.N_CAND * C4.N_TRIAL, n_att * C4.N_FORGE
    qobs = len(C2.STUDY_KEYS) * len(C4.LEVELS) * max(C4.FORGE_N)
    integ_texts = len(C2.STUDY_KEYS) * len(C4.LEVELS) * 100
    rep_texts = trials + qobs + len(C4.LEVELS) * len(C2.STUDY_KEYS) * 100 * 14
    hours = ((trials + forg) * t_gen + (trials + qobs) * t_cont + (forg + integ_texts) * t_tok + forg * t_ppl
             + rep_texts * t_rep) / 3600
    check("timing_budget", hours <= BUDGET_H, projected_hours=round(hours, 1), s_per_gen=round(t_gen, 3),
          s_per_cont_ppl=round(t_cont, 3), s_per_tokens=round(t_tok, 3), s_per_ppl=round(t_ppl, 3),
          s_per_seqrep=round(t_rep, 5), generations=trials + forg)
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"all_pass": all(c["pass"] for c in checks.values()), "checks": checks,
               "note": "inputs only; no v0.4 trial or forgery with a study key; no v0.4 statistic",
               "code_sha256": {p.name: run_v04.sha(p) for p in run_v04.CODE}}
    (OUT / "INPUT_VALIDATION.json").write_text(json.dumps(summary, indent=2))
    print("ALL PASS" if summary["all_pass"] else "SOME CHECKS FAILED", flush=True)


if __name__ == "__main__":
    main()
