"""Study 2 scrubbing pilot v0.1 (SCRUB_PILOT_SPEC_v0.1.md), on the tuning keys only.

Phases:
  validate  inputs only: files, keys, seeds, pools; a smoke test on 2 unwatermarked tuning texts outside the pilot set
            (one paraphrase per model, edits with a random direction, every quality and S4 field); timing
  run       bars, paraphrases (both models, with the attacker's self-check), rule A1, edits (3 arms, plus rule A2's runs),
            scoring; checkpointed per step (re-running resumes). Refuses unless the spec is FIXED and committed.
  analyse   results.json (spec §4-6): pass rates, detection, success, calibration after paraphrase, checks I1-I5
Run: .venv/bin/python research/study2_pilot/scrub_pilot.py --phase validate|run|analyse
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scrub_core as SC  # noqa: E402
from scrub_core import C2, PP, core  # noqa: E402

ROOT = SC.ROOT
sys.path.insert(0, str(ROOT / "research" / "repro"))
SPEC = HERE / "SCRUB_PILOT_SPEC_v0.1.md"
DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study2_pilot_v0.1"
CAL = ROOT / "research" / "repro" / "data" / "qwen"
V02 = ROOT / "research" / "study1_v02" / "data"

TUNING = [9001, 9002, 9003, 9004]
LEVELS = [0.25, 0.35, 0.50, 0.70]
PER = 25                       # texts per tuning key and level (spec §1)
N_REF_C = 200                  # the attacker's pool C references
ALPHA = 0.01
SEED_PARA = 20261000           # paraphrase sampling: SEED_PARA + 100 * model + 10 * set + attempt
SEED_RAND_EDIT = 20261001      # E-rand positions and replacements
SEED_STANDIN = 20261002        # E-est stand-ins: SEED_STANDIN + key seed
SEED_SMOKE = 20261003          # the validation smoke test's random direction and key
FRESH0, N_FRESH = 55_500_000, 1000   # fresh public-distribution keys for per-key FPR after paraphrase
MODELS = ["qwen", "phi"]
BATCH_PARA = {"qwen": 8, "phi": 4}  # spec §2.4 says 8; Phi uses 4 (memory; deviation logged 2026-10-01)
A1_MIN = 0.70
A2_FRACS = (0.01, 0.05)
A2_KEEP = 0.90
I5_BUDGET_H, PILOT_BUDGET_H = 24.0, 4.0
STUDY = {"genuine": 3200, "null": 1000}   # Study 2's grid (decision 2) and pool A's paraphrased null texts
PROBE_S_PER_TEXT = 0.05        # allowance for the owner's probe features per scored text in Study 2 (not run here)
KEY_SEEDS_IN_USE = ({0, 1} | set(range(1001, 1017)) | set(range(5001, 5017)) | set(TUNING)
                    | {77_700_000 + j for j in range(9999)} | {88_800_000 + j for j in range(10000)}
                    | {66_600_000 + j for j in range(1000)})


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tag(rho):
    return f"r{int(round(rho * 100)):03d}"


def jload(p):
    return json.loads(Path(p).read_text())


def jsave(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=1))


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


# ---------------------------------------------------------------- inputs
def input_files():
    f = {"F": V02 / "S_F_van.json", "A": V02 / "S_A_van.json", "C": V02 / "S_C_ref.json"}
    for s in TUNING:
        f[f"van_k{s}"] = CAL / f"texts_van_k{s}.json"
        for rho in LEVELS:
            f[f"{tag(rho)}_k{s}"] = CAL / f"texts_calib_{tag(rho)}_k{s}.json"
    return f


def pools():
    import repro_pilot as rp  # noqa: E402  (key_prompts: key i uses pool T prompts 100 i ... 100 i + 99)
    base = core.assign_pools()
    P2 = C2.pools()
    return base, P2, rp


DRY = False


def dry_sets():
    """--dry: stand-ins for every set, built only from unwatermarked texts outside the pilot set (texts 25-29 of each
    key's unwatermarked file), relabelled with keys and levels so every code path runs. No watermarked text is read;
    the numbers carry no information."""
    base, _, rp = pools()
    wm, van = [], []
    for i, s in enumerate(TUNING):
        pr = [u["prompt"] for u in rp.key_prompts(base, i)]
        t = jload(CAL / f"texts_van_k{s}.json")
        for li, rho in enumerate(LEVELS):
            wm.append({"text": t[PER + li], "prompt": pr[PER + li], "key": s, "rho": rho, "j": 0})
        van.append({"text": t[PER + 4], "prompt": pr[PER + 4], "key": s, "rho": None, "j": 0})
    return wm, van


def tuning_sets():
    """The pilot's texts: 'wm' (400; per key and level, the first 25) and 'van' (100; per key, the first 25), each
    with its prompt, key seed and level (None for unwatermarked)."""
    if DRY:
        return dry_sets()
    base, _, rp = pools()
    wm, van = [], []
    for i, s in enumerate(TUNING):
        pr = [u["prompt"] for u in rp.key_prompts(base, i)][:PER]
        for rho in LEVELS:
            t = jload(CAL / f"texts_calib_{tag(rho)}_k{s}.json")[:PER]
            wm += [{"text": x, "prompt": p, "key": s, "rho": rho, "j": j} for j, (x, p) in enumerate(zip(t, pr))]
        t = jload(CAL / f"texts_van_k{s}.json")[:PER]
        van += [{"text": x, "prompt": p, "key": s, "rho": None, "j": j} for j, (x, p) in enumerate(zip(t, pr))]
    return wm, van


def ref_sets():
    """Pool A (bars: model texts, prompts, human continuations of the same prompts) and the attacker's pool C refs."""
    _, P2, _ = pools()
    A_units = P2["A1"] + P2["A2"]
    A = {"text": jload(V02 / "S_A_van.json"), "prompt": [u["prompt"] for u in A_units],
         "human": [u["human_continuation"] for u in A_units], "id": [u["id"] for u in A_units]}
    Cu = P2["C"][:N_REF_C]
    C = {"text": jload(V02 / "S_C_ref.json")[:N_REF_C], "prompt": [u["prompt"] for u in Cu],
         "human": [u["human_continuation"] for u in Cu], "id": [u["id"] for u in Cu]}
    return A, C


def tuning_key(s, rho):
    return PP.tuning_key(s, rho).astype(np.float64)


def standin(s):
    """E-est's pilot stand-in (spec §2.2): 4-sparse, shares the key's smallest-magnitude support coordinate."""
    v = tuning_key(s, 1.0)
    supp = np.flatnonzero(v)
    keep = supp[np.argmin(np.abs(v[supp]))]
    rng = np.random.default_rng(SEED_STANDIN + s)
    others = rng.choice(np.setdiff1d(np.arange(SC.D), supp), size=3, replace=False)
    e = np.zeros(SC.D)
    e[keep] = v[keep]
    e[others] = rng.uniform(-1, 1, size=3)
    return e


def fresh_keys():
    return SC.unit(np.stack([core.make_key(FRESH0 + j, SC.D, 1.0).numpy() for j in range(N_FRESH)]))


# ---------------------------------------------------------------- guard
def spec_guard():
    if DRY:
        return {"dry_run": True, "utc": now()}
    if "**Status:** FIXED" not in SPEC.read_text():
        sys.exit("refused: the spec is not marked FIXED (Yichen's approval comes first)")
    code = [SPEC, Path(__file__), HERE / "scrub_core.py"]
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + [str(p) for p in code], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        sys.exit(f"refused: uncommitted changes in the spec or the code:\n{dirty}")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"commit": commit, "sha256": {p.name: sha(p) for p in code}, "utc": now()}


# ---------------------------------------------------------------- run steps (checkpointed)
TIMES = DATA / "times.json"


def timed(name):
    def deco(fn):
        def wrap(*a, **k):
            t0 = time.time()
            r = fn(*a, **k)
            t = jload(TIMES) if TIMES.exists() else {}
            t[name] = t.get(name, 0.0) + time.time() - t0
            jsave(TIMES, t)
            return r
        return wrap
    return deco


@timed("bars")
def step_bars(wm, van):
    f = DATA / "bars.json"
    if f.exists():
        return jload(f)
    A, C = ref_sets()
    SC.free()
    tok, model = SC.load_base()
    E = SC.Embedder()
    qa = SC.raw_quality(tok, model, E, A["prompt"], A["text"])          # model texts (secondary bar)
    qc = SC.raw_quality(tok, model, E, C["prompt"], C["text"])
    qah = SC.raw_quality(tok, model, E, A["prompt"], A["human"])        # human continuations (primary normal range)
    qch = SC.raw_quality(tok, model, E, C["prompt"], C["human"])
    pa, pc = SC.cosines(E, A["text"], A["human"]), SC.cosines(E, C["text"], C["human"])
    owner = SC.Owner(tok, model, jload(V02 / "S_F_van.json"))
    Gc = SC.Owner.grads(tok, model, C["text"])
    qo = {k: SC.raw_quality(tok, model, E, [x["prompt"] for x in S], [x["text"] for x in S]) for k, S in
          (("wm", wm), ("van", van))}
    np.savez(DATA / "refs.npz", owner_mu=owner.ref["mu_g"], owner_sd=owner.ref["sd_g"],
             att_sd14=np.maximum(Gc.std(0, ddof=1), 1e-12))
    out = {"A": SC.bars(qah, pa), "C": SC.bars(qch, pc),
           "A_model_p95": SC.bars(qa, pa), "A_human_median": SC.bars(qah, pa, q=0.5),
           "A_raw": {"model_ppl_median": float(np.median(qa["ppl"])), "human_ppl_median": float(np.median(qah["ppl"])),
                     "model_rep_median": float(np.median(qa["rep"])), "human_rep_median": float(np.median(qah["rep"])),
                     "pair_cos_median": float(np.median(pa))},
           "orig": {k: {x: v[x].tolist() for x in v} for k, v in qo.items()}}
    jsave(f, out)
    del model, E, tok, owner
    SC.free()
    return out


def _quality_dict(q):
    return {k: np.asarray(v).tolist() for k, v in q.items()}


def paraphrase_with_checks(name, items, orig_q, cbar, set_idx, template):
    """Spec §2.1: up to 3 attempts; a text is retried while its attempt fails the attacker's own check (pool C bars)."""
    n = len(items)
    texts = [x["text"] for x in items]
    prompts = [x["prompt"] for x in items]
    oq = {k: np.asarray(orig_q[k]) for k in ("ppl", "rep", "len")}
    attempts = [[None] * n for _ in range(SC.MAX_ATTEMPTS)]
    todo = list(range(n))
    tpara = 0.0
    for a in range(SC.MAX_ATTEMPTS):
        if not todo:
            break
        SC.free()
        tok, model = SC.load_paraphraser(name)
        t0 = time.time()
        outs = SC.paraphrase(tok, model, [texts[i] for i in todo], template,
                             SEED_PARA + 100 * MODELS.index(name) + 10 * set_idx + a, BATCH_PARA[name])
        tpara += time.time() - t0
        del model, tok
        SC.free()
        btok, base = SC.load_base()
        E = SC.Embedder()
        zq = SC.raw_quality(btok, base, E, [prompts[i] for i in todo], outs, [texts[i] for i in todo])
        sub = {k: oq[k][todo] for k in oq}
        cond = SC.conditions(sub, zq, cbar)
        nf = SC.n_fail(cond)
        for j, i in enumerate(todo):
            attempts[a][i] = {"text": outs[j], **{k: float(zq[k][j]) for k in ("ppl", "rep", "cos")},
                              "len": int(zq["len"][j]), "n_fail_attacker": int(nf[j])}
        todo = [i for j, i in enumerate(todo) if nf[j] > 0]
        del base, E, btok
        SC.free()
        print(f"  {name} attempt {a + 1}: {len(outs)} paraphrased, {len(todo)} to retry ({now()})", flush=True)
    kept = []
    for i in range(n):
        tried = [(a, attempts[a][i]) for a in range(SC.MAX_ATTEMPTS) if attempts[a][i] is not None]
        ok = [a for a, r in tried if r["n_fail_attacker"] == 0]
        kept.append(ok[0] if ok else min(tried, key=lambda ar: (ar[1]["n_fail_attacker"], -ar[1]["cos"], ar[0]))[0])
    return {"attempts": attempts, "kept": kept, "paraphrase_s": tpara}


@timed("paraphrase")
def step_paraphrase(name, wm, van, bars, template_name="P1", subset=None):
    suffix = "" if template_name == "P1" else f"_{template_name}"
    f = DATA / f"para_{name}{suffix}.json"
    if f.exists():
        return jload(f)
    res = {"template": template_name}
    sets = [("wm", wm), ("van", van)] if subset is None else [("wm", subset)]
    for si, (k, S) in enumerate(sets):
        oq = bars["orig"][k] if subset is None else {
            q: [bars["orig"]["wm"][q][wm.index(x)] for x in S] for q in ("ppl", "rep", "len")}
        res[k] = paraphrase_with_checks(name, S, oq, bars["C"], si if subset is None else 2,
                                        SC.PROMPTS[template_name])
        res[k]["idx"] = [wm.index(x) for x in S] if subset is not None else list(range(len(S)))
    jsave(f, res)
    return res


def a1_rule(paras, bars):
    """Spec §6 A1: the share of first attempts on the 400 watermarked texts meeting the length floor, per model."""
    olen = np.minimum(np.asarray(bars["orig"]["wm"]["len"]), SC.NEW_TOKENS)
    share = {m: float(np.mean([r["len"] >= SC.LEN_FLOOR * o for r, o in zip(paras[m]["wm"]["attempts"][0], olen)]))
             for m in MODELS}
    return {"first_attempt_length_share": share, "switch_to_P2": any(v < A1_MIN for v in share.values())}


@timed("edits")
def step_edits(wm, arm, round_frac=SC.ROUND_FRAC, subset_rho=None):
    suffix = "" if round_frac == SC.ROUND_FRAC else f"_r{int(round(round_frac * 100))}"
    f = DATA / f"edits_{arm}{suffix}.json"
    if f.exists():
        return jload(f)
    refs = np.load(DATA / "refs.npz")
    sd = refs["att_sd14"]
    SC.free()
    tok, model = SC.load_base()
    ed = SC.Editor(tok, model)
    rng = np.random.default_rng(SEED_RAND_EDIT) if arm == "rand" else None
    recs = [None] * len(wm)
    t0 = time.time()
    n_done = 0
    for s in TUNING:
        for rho in LEVELS:
            if subset_rho is not None and rho != subset_rho:
                continue
            idx = [i for i, x in enumerate(wm) if x["key"] == s and x["rho"] == rho]
            texts = [wm[i]["text"] for i in idx]
            if arm == "rand":
                out = ed.run(texts, "random", rng=rng, round_frac=round_frac)
            else:
                v = tuning_key(s, rho) if arm == "true" else standin(s)
                out = ed.run(texts, "guided", direction=v / sd, layer=SC.LAYER, round_frac=round_frac)
            for i, r in zip(idx, out):
                recs[i] = r
            n_done += len(idx)
            print(f"  edits {arm} r={round_frac}: key {s} rho {rho} done ({n_done} texts, {now()})", flush=True)
    res = {"arm": arm, "round_frac": round_frac, "recs": recs, "edit_s": time.time() - t0, "n_texts": n_done}
    jsave(f, res)
    del ed, model, tok
    SC.free()
    return res


@timed("score")
def step_score(wm, van, paras, edits, p2):
    """S4 gradients and quality for every text set; saved per set (npz for gradients, json for quality)."""
    SC.free()
    tok, model = SC.load_base()
    E = SC.Embedder()
    sets = {"orig_wm": ([x["text"] for x in wm], [x["prompt"] for x in wm], None, None),
            "orig_van": ([x["text"] for x in van], [x["prompt"] for x in van], None, None)}
    for m in MODELS:
        for k, S in (("wm", wm), ("van", van)):
            P = paras[m][k]
            o = [x["text"] for x in S]
            kept = [P["attempts"][a][i]["text"] for i, a in enumerate(P["kept"])]
            first = [P["attempts"][0][i]["text"] for i in range(len(S))]
            sets[f"para_{m}_{k}"] = (kept, [x["prompt"] for x in S], o, None)
            # first attempts: only those that differ from the kept attempt are scored; the rest are copied
            sets[f"para1_{m}_{k}"] = (first, [x["prompt"] for x in S], o,
                                      (f"para_{m}_{k}", [i for i, a in enumerate(P["kept"]) if a != 0]))
        if p2 is not None:
            P = p2[m]["wm"]
            S = [wm[i] for i in P["idx"]]
            sets[f"paraP2_{m}_wm"] = ([P["attempts"][a][i]["text"] for i, a in enumerate(P["kept"])],
                                      [x["prompt"] for x in S], [x["text"] for x in S], None)
    for arm, e in edits.items():
        for f in SC.BUDGETS:
            sets[f"edit_{arm}_{f}"] = ([r["texts"][str(f)] for r in e["recs"]], [x["prompt"] for x in wm],
                                       [x["text"] for x in wm], None)
    t_s4 = t_q = 0.0
    n_s4 = 0
    for name, (texts, prompts, origs, reuse) in sets.items():
        fg, fq = DATA / f"G_{name}.npy", DATA / f"Q_{name}.json"
        if fg.exists() and fq.exists():
            continue
        idx = list(range(len(texts))) if reuse is None else reuse[1]
        t0 = time.time()
        Gi = SC.Owner.grads(tok, model, [texts[i] for i in idx]) if idx else np.zeros((0, SC.D))
        t_s4 += time.time() - t0
        t0 = time.time()
        Qi = SC.raw_quality(tok, model, E, [prompts[i] for i in idx], [texts[i] for i in idx],
                            None if origs is None else [origs[i] for i in idx]) if idx else None
        t_q += time.time() - t0
        n_s4 += len(idx)
        if reuse is None:
            Gall, Qall = Gi, _quality_dict(Qi)
        else:
            Gall = np.load(DATA / f"G_{reuse[0]}.npy").copy()
            Qall = jload(DATA / f"Q_{reuse[0]}.json")
            for j, i in enumerate(idx):
                Gall[i] = Gi[j]
                for q in Qall:
                    Qall[q][i] = np.asarray(Qi[q][j]).item()
        np.save(fg, Gall)
        jsave(fq, Qall)
        print(f"  scored {name}: {len(idx)} texts ({now()})", flush=True)
    t = jload(DATA / "score_rates.json") if (DATA / "score_rates.json").exists() else {}
    if n_s4:
        t.update({"s4_s_per_text": t_s4 / n_s4, "quality_s_per_text": t_q / n_s4})
        jsave(DATA / "score_rates.json", t)
    # check I1 (spec §5): finite-difference objective vs autograd, key 9001 at rho 0.50 (25 texts), plus per-token
    # stability between s and s/2
    f1 = DATA / "check_I1.json"
    if not f1.exists():
        refs = np.load(DATA / "refs.npz")
        idx = [i for i, x in enumerate(wm) if x["key"] == 9001 and x["rho"] == 0.50]
        v = tuning_key(9001, 0.50)
        w = v / refs["att_sd14"]
        wh = w / np.linalg.norm(w)
        G = np.load(DATA / "G_orig_wm.npy")[idx]
        auto = (G @ wh).tolist()
        fd = [edits["true"]["recs"][i]["obj"]["0"] for i in idx]
        ed = SC.Editor(tok, model)
        rho_tok = []
        for i in idx[:10]:
            c = {}
            for s_fd in (SC.S_FD, SC.S_FD / 2):
                ids = tok(wm[i]["text"], add_special_tokens=False)["input_ids"][:SC.NEW_TOKENS]
                wt = torch.tensor(wh, dtype=torch.float32)
                H = ed._passes([ids, ids], [s_fd * wt, -s_fd * wt], SC.LAYER)
                lpp = ed._gather(H[0], ids, None)[0]
                lpm = ed._gather(H[1], ids, None)[0]
                c[s_fd] = ((lpp - lpm) / (2 * s_fd)).cpu().numpy()
            from scipy.stats import spearmanr
            rho_tok.append(float(spearmanr(c[SC.S_FD], c[SC.S_FD / 2]).statistic))
        del ed
        enough = len(idx) >= 3
        jsave(f1, {"autograd": auto, "finite_difference": fd,
                   "r": float(np.corrcoef(auto, fd)[0, 1]) if enough else float("nan"),
                   "slope_fd_on_auto": float(np.polyfit(auto, fd, 1)[0]) if enough else float("nan"),
                   "per_token_spearman_s_vs_half_s": rho_tok})
    del model, E, tok
    SC.free()


def run():
    guard = spec_guard()
    DATA.mkdir(parents=True, exist_ok=True)
    jsave(DATA / "pilot_guard.json", guard)
    wm, van = tuning_sets()
    print(f"run start {now()}: {len(wm)} watermarked, {len(van)} unwatermarked", flush=True)
    bars = step_bars(wm, van)
    print(f"bars done {now()}: {json.dumps({k: bars[k] for k in ('A', 'C')})}", flush=True)
    paras = {m: step_paraphrase(m, wm, van, bars) for m in MODELS}
    a1 = a1_rule(paras, bars)
    jsave(DATA / "rule_A1.json", a1)
    p2 = None
    if a1["switch_to_P2"]:
        sub = [x for x in wm if x["rho"] == 0.50]
        p2 = {m: step_paraphrase(m, wm, van, bars, "P2", sub) for m in MODELS}
    edits = {arm: step_edits(wm, arm) for arm in ("true", "est", "rand")}
    for fr in A2_FRACS:
        step_edits(wm, "true", round_frac=fr, subset_rho=0.50)
    step_score(wm, van, paras, edits, p2)
    print("run complete", now(), flush=True)


# ---------------------------------------------------------------- analysis
def analyse():
    guard = spec_guard()
    wm, van = tuning_sets()
    bars = jload(DATA / "bars.json")
    refs = np.load(DATA / "refs.npz")
    owner = SC.Owner.__new__(SC.Owner)
    owner.ref = {"mu_g": refs["owner_mu"], "sd_g": refs["owner_sd"]}
    owner.nm = PP.null_matrix()
    paras = {m: jload(DATA / f"para_{m}.json") for m in MODELS}
    a1 = jload(DATA / "rule_A1.json")
    edits = {arm: jload(DATA / f"edits_{arm}.json") for arm in ("true", "est", "rand")}
    G = lambda n: np.load(DATA / f"G_{n}.npy")  # noqa: E731
    Qd = lambda n: {k: np.asarray(v) for k, v in jload(DATA / f"Q_{n}.json").items()}  # noqa: E731
    orig = {k: {q: np.asarray(v) for q, v in bars["orig"][k].items()} for k in ("wm", "van")}

    keys = np.stack([SC.unit(tuning_key(x["key"], 1.0)) for x in wm])
    p_orig = PP.pvalues((owner.x(G("orig_wm")) * keys).sum(1), owner.x(G("orig_wm")) @ owner.nm.T)

    def pv_wm(name):
        X = owner.x(G(name))
        return PP.pvalues((X * keys).sum(1), X @ owner.nm.T)

    def per_key_median(vals, rho):
        per = {str(s): float(np.mean([v for v, x in zip(vals, wm) if x["key"] == s and x["rho"] == rho]) * 100)
               for s in TUNING}
        return {"per_key": per, "median": float(np.median(list(per.values())))}

    def summarise(name, origq):
        p = pv_wm(name)
        zq = Qd(name)
        c = SC.conditions(origq, zq, bars["A"])
        succ = (p > ALPHA) & c["all"]
        alt = {b: (p > ALPHA) & SC.conditions(origq, zq, bars[b])["all"] for b in ("A_model_p95", "A_human_median")}
        out = {}
        for rho in LEVELS:
            sel = [i for i, x in enumerate(wm) if x["rho"] == rho]
            out[str(rho)] = {
                "detected_before": per_key_median(p_orig <= ALPHA, rho),
                "detected_after": per_key_median(p <= ALPHA, rho),
                "success": per_key_median(succ, rho),
                "success_stricter_bars": {b: per_key_median(v, rho)["median"] for b, v in alt.items()},
                "pass": {k: per_key_median(c[k], rho) for k in ("ppl", "rep", "len", "cos", "all")},
                "median_len_ratio": float(np.median(zq["len"][sel] / np.minimum(origq["len"][sel], SC.NEW_TOKENS))),
                "median_ppl_ratio": float(np.median(zq["ppl"][sel] / origq["ppl"][sel])),
                "median_cos": float(np.median(zq["cos"][sel])),
                "keys_success_ge_50": int(sum(v >= 50 for v in per_key_median(succ, rho)["per_key"].values()))}
        return out, p

    res = {"guard": guard, "spec_sha256": sha(SPEC),
           "bars": {k: bars[k] for k in ("A", "C", "A_model_p95", "A_human_median", "A_raw")},
           "rule_A1": a1, "methods": {}, "edits": {}, "paraphrase": {}, "calibration_after_paraphrase": {}}
    pvals = {}
    for m in MODELS:
        res["methods"][f"P-{m}"], pvals[f"P-{m}"] = summarise(f"para_{m}_wm", orig["wm"])
        res["methods"][f"P-{m} (first attempt)"], _ = summarise(f"para1_{m}_wm", orig["wm"])
        P = paras[m]["wm"]
        res["paraphrase"][m] = {"attempts_used": {str(a + 1): int(sum(1 for k in P["kept"] if k == a))
                                                  for a in range(SC.MAX_ATTEMPTS)},
                                "kept_fails_attacker_check": int(sum(P["attempts"][a][i]["n_fail_attacker"] > 0
                                                                     for i, a in enumerate(P["kept"]))),
                                "paraphrase_s_per_original": (P["paraphrase_s"] + paras[m]["van"]["paraphrase_s"])
                                / (len(wm) + len(van))}
    if a1["switch_to_P2"]:
        res["paraphrase_P2"] = {}
        for m in MODELS:
            P = jload(DATA / f"para_{m}_P2.json")["wm"]
            olen = np.minimum(orig["wm"]["len"][P["idx"]], SC.NEW_TOKENS)
            sub = {q: v[P["idx"]] for q, v in orig["wm"].items()}
            c2 = SC.conditions(sub, Qd(f"paraP2_{m}_wm"), bars["A"])
            z1 = {q: v[P["idx"]] for q, v in Qd(f"para_{m}_wm").items()}
            c1 = SC.conditions(sub, z1, bars["A"])
            res["paraphrase_P2"][m] = {
                "first_attempt_length_share": float(np.mean(
                    [r["len"] >= SC.LEN_FLOOR * o for r, o in zip(P["attempts"][0], olen)])),
                "pass_rates_pct_P2": {k: float(c2[k].mean() * 100) for k in ("ppl", "rep", "len", "cos", "all")},
                "pass_rates_pct_P1_same_texts": {k: float(c1[k].mean() * 100) for k in ("ppl", "rep", "len", "cos",
                                                                                         "all")}}
    for arm in ("true", "est", "rand"):
        for f in SC.BUDGETS:
            res["methods"][f"E-{arm} {int(f * 100)}%"], pvals[f"E-{arm} {f}"] = summarise(f"edit_{arm}_{f}",
                                                                                         orig["wm"])
        recs = edits[arm]["recs"]
        res["edits"][arm] = {"edit_s_per_text": edits[arm]["edit_s"] / edits[arm]["n_texts"],
                             "stalled": int(sum(r["stalled_at"] is not None for r in recs)),
                             "n_diff_exact": all(r["n_diff"][str(f)] == math.ceil(f * r["T"]) or r["stalled_at"]
                                                 is not None for r in recs for f in SC.BUDGETS),
                             "median_drift": {str(f): float(np.median([r["drift"][str(f)] for r in recs]))
                                              for f in SC.BUDGETS}}
        if arm != "rand":
            res["edits"][arm]["median_objective"] = {k: float(np.median([r["obj"][k] for r in recs]))
                                                     for k in ["0"] + [str(f) for f in SC.BUDGETS]}

    # I2: the owner's statistic moves more under E-true than E-rand (0% -> 10%)
    from scipy.stats import wilcoxon
    t0 = (owner.x(G("orig_wm")) * keys).sum(1)
    d_true = (owner.x(G("edit_true_0.1")) * keys).sum(1) - t0
    d_rand = (owner.x(G("edit_rand_0.1")) * keys).sum(1) - t0
    w = wilcoxon(d_true, d_rand, alternative="less")
    i1 = jload(DATA / "check_I1.json")
    drift_ok = all(v <= 0.02 for arm in res["edits"] for v in res["edits"][arm]["median_drift"].values())
    checks = {"I1": {"pass": i1["r"] >= 0.99 and float(np.median(i1["per_token_spearman_s_vs_half_s"])) >= 0.8,
                     "r": i1["r"], "slope": i1["slope_fd_on_auto"],
                     "per_token_spearman_median": float(np.median(i1["per_token_spearman_s_vs_half_s"]))},
              "I2": {"pass": bool(w.pvalue < 0.01 and np.median(d_true) < 0),
                     "wilcoxon_p": float(w.pvalue), "median_change_true": float(np.median(d_true)),
                     "median_change_rand": float(np.median(d_rand))},
              "I3": {"pass": bool(all(res["edits"][a]["n_diff_exact"] for a in res["edits"]) and drift_ok),
                     "n_diff_exact": {a: res["edits"][a]["n_diff_exact"] for a in res["edits"]},
                     "median_drift_le_2pct": drift_ok,
                     "hook_removed": "see VALIDATION.json (smoke)"}}

    # A2: round size, on the attacker's own objective at 10% (rho 0.50)
    sel = [i for i, x in enumerate(wm) if x["rho"] == 0.50]
    red = {}
    for fr in (0.01, SC.ROUND_FRAC, 0.05):
        e = edits["true"] if fr == SC.ROUND_FRAC else jload(DATA / f"edits_true_r{int(round(fr * 100))}.json")
        red[str(fr)] = float(np.median([e["recs"][i]["obj"]["0"] - e["recs"][i]["obj"]["0.1"] for i in sel]))
    best = max(red.values())
    ok = [fr for fr in (0.01, SC.ROUND_FRAC, 0.05) if red[str(fr)] >= A2_KEEP * best]
    res["rule_A2"] = {"median_reduction_at_10pct": red, "reference": "best of the three", "chosen_round_frac": max(ok)}

    # calibration after paraphrase (descriptive): 4 tuning keys, and 1,000 fresh keys
    FK = fresh_keys()
    for m in MODELS:
        for nm_, gname in (("original", "orig_van"), ("paraphrased", f"para_{m}_van")):
            X = owner.x(G(gname))
            N = X @ owner.nm.T
            tk = np.stack([SC.unit(tuning_key(x["key"], 1.0)) for x in van])
            pooled = []
            for s in TUNING:
                ks = SC.unit(tuning_key(s, 1.0))
                pooled.append(PP.pvalues(X @ ks, N) <= ALPHA)
            per_key = [float((PP.pvalues(X @ FK[j], N) <= ALPHA).mean() * 100) for j in range(N_FRESH)]
            res["calibration_after_paraphrase"].setdefault(m, {})[nm_] = {
                "pooled_fpr_4_tuning_keys_pct": float(np.mean(np.concatenate(pooled)) * 100),
                "fresh_keys_mean_fpr_pct": float(np.mean(per_key)),
                "fresh_keys_share_above_3pct": float(np.mean(np.array(per_key) > 3.0)),
                "fresh_keys_max_fpr_pct": float(np.max(per_key))}

    # timing and the Study 2 projection (check I5)
    times = jload(DATA / "times.json")
    rates = jload(DATA / "score_rates.json")
    proj = {}
    for m in MODELS:
        P = paras[m]
        tq = rates["quality_s_per_text"]
        n_att = sum(1 for a in range(SC.MAX_ATTEMPTS) for S in ("wm", "van") for r in P[S]["attempts"][a] if r)
        per_orig = (P["wm"]["paraphrase_s"] + P["van"]["paraphrase_s"] + n_att * tq) / (len(wm) + len(van))
        proj[f"paraphrase_{m}_h"] = per_orig * (STUDY["genuine"] + STUDY["null"]) / 3600
    for arm in ("true", "est", "rand"):
        proj[f"edits_{arm}_h"] = res["edits"][arm]["edit_s_per_text"] * STUDY["genuine"] / 3600
    retried = float(np.mean([a > 0 for m in MODELS for a in paras[m]["wm"]["kept"] + paras[m]["van"]["kept"]]))
    n_full = 2 * (STUDY["genuine"] + STUDY["null"]) + 3 * len(SC.BUDGETS) * STUDY["genuine"]   # kept paraphrases, edits
    n_first = 2 * (STUDY["genuine"] + STUDY["null"]) * retried                                 # first attempts that differ
    full = rates["s4_s_per_text"] + rates["quality_s_per_text"]
    proj["scoring_h"] = (n_full * (full + PROBE_S_PER_TEXT) + n_first * full
                         + 2 * STUDY["genuine"] * rates["s4_s_per_text"]                       # length-matched controls
                         + STUDY["genuine"] * full) / 3600                                     # originals
    proj["share_retried"] = retried
    proj["estimate_layer_scales_h"] = 16 * N_REF_C * rates["s4_s_per_text"] / 3600
    proj["total_h"] = float(sum(v for k, v in proj.items() if k.endswith("_h")))
    checks["I5"] = {"pass": proj["total_h"] <= I5_BUDGET_H, "projection": proj, "budget_h": I5_BUDGET_H}
    res["checks"] = checks
    res["times_s"] = times

    # samples to read (spec §4): rho 0.50, the first text of keys 9001 and 9002
    res["samples"] = []
    for s in (9001, 9002):
        i = next(i for i, x in enumerate(wm) if x["key"] == s and x["rho"] == 0.50 and x["j"] == 0)
        smp = {"key": s, "original": wm[i]["text"], "p_original": float(p_orig[i])}
        for m in MODELS:
            P = paras[m]["wm"]
            smp[f"P-{m}"] = P["attempts"][P["kept"][i]][i]["text"]
            smp[f"p_P-{m}"] = float(pvals[f"P-{m}"][i])
        for arm in ("true", "est", "rand"):
            smp[f"E-{arm} 10%"] = edits[arm]["recs"][i]["texts"]["0.1"]
            smp[f"p_E-{arm} 10%"] = float(pvals[f"E-{arm} 0.1"][i])
        res["samples"].append(smp)
    res["all_checks_pass"] = all(c["pass"] for c in checks.values())
    OUT.mkdir(parents=True, exist_ok=True)
    jsave(OUT / "results.json", res)
    print(json.dumps({"checks": {k: v["pass"] for k, v in checks.items()}, "A1": a1, "A2": res["rule_A2"],
                      "projection_h": proj["total_h"]}, indent=1))


# ---------------------------------------------------------------- validation (inputs only)
def validate():
    OUT.mkdir(parents=True, exist_ok=True)
    checks, t_start = {}, time.time()
    files = input_files()
    missing = [k for k, p in files.items() if not p.exists()]
    counts = {k: len(jload(p)) for k, p in files.items() if p.exists()}
    wm, van = tuning_sets()
    A, C = ref_sets()
    ok = (not missing and len(wm) == 400 and len(van) == 100 and counts["F"] == 200 and counts["A"] == 1000
          and len(C["text"]) == N_REF_C and all(counts[k] >= PER for k in counts if k not in ("F", "A", "C")))
    checks["1_inputs"] = {"pass": bool(ok), "missing": missing, "counts": counts,
                          "sha256": {k: sha(p) for k, p in files.items() if p.exists()}}

    norms_ok = all(abs(np.linalg.norm(tuning_key(s, r)) - r * PP.N_REF) < 1e-3
                   and int((tuning_key(s, r) != 0).sum()) == core.n_support(SC.D) for s in TUNING for r in LEVELS)
    st_cos = {str(s): float(SC.unit(standin(s)) @ SC.unit(tuning_key(s, 1.0))) for s in TUNING}
    fresh = {FRESH0 + j for j in range(N_FRESH)}
    checks["2_keys_seeds"] = {"pass": bool(norms_ok and not (fresh & KEY_SEEDS_IN_USE)
                                           and all(int((standin(s) != 0).sum()) == 4 for s in TUNING)),
                              "standin_cos": st_cos, "fresh_key_seeds": [FRESH0, FRESH0 + N_FRESH - 1],
                              "sampling_seeds": [SEED_PARA, SEED_RAND_EDIT, SEED_STANDIN, SEED_SMOKE]}

    _, P2, _ = pools()
    a_ids = [u["id"] for u in P2["A1"] + P2["A2"]]
    checks["3_pools"] = {"pass": bool(a_ids == A["id"] and len(set(a_ids)) == 1000 and
                                      not (set(a_ids) & set(C["id"])) and len(A["human"]) == 1000),
                         "note": "pool A model texts, prompts and human continuations share one prompt order; "
                                 "pool C refs disjoint from pool A"}

    # 4. smoke test on 2 unwatermarked tuning texts outside the pilot set (texts 25-26 of key 9001's van file)
    smoke = jload(CAL / "texts_van_k9001.json")[PER:PER + 2]
    base, _, rp = pools()
    sp = [u["prompt"] for u in rp.key_prompts(base, 0)][PER:PER + 2]
    timing, fields, batching = {}, {}, {}
    F8 = jload(V02 / "S_F_van.json")[:8]
    for m in MODELS:
        t0 = time.time()
        tok, model = SC.load_paraphraser(m)
        timing[f"load_{m}"] = time.time() - t0
        # 5. batching check (spec §2.4): greedy, the same 8 pool F texts, one batch of 8 vs one at a time
        t0 = time.time()
        b8 = SC.paraphrase(tok, model, F8, SC.PROMPTS["P1"], SEED_SMOKE, 8, gen=SC.GREEDY)
        tb = time.time() - t0
        t0 = time.time()
        b1 = SC.paraphrase(tok, model, F8, SC.PROMPTS["P1"], SEED_SMOKE, 1, gen=SC.GREEDY)
        t1 = time.time() - t0
        w8, w1 = [len(x.split()) for x in b8], [len(x.split()) for x in b1]
        batching[m] = {"words_batch8": w8, "words_single": w1, "ratio": sum(w8) / sum(w1),
                       "identical_texts": int(sum(x == y for x, y in zip(b8, b1))),
                       "s_per_text_batch8": tb / 8, "s_per_text_single": t1 / 8}
        timing[f"paraphrase_{m}_s_per_text_batch8"] = tb / 8
        t0 = time.time()
        outs = SC.paraphrase(tok, model, smoke, SC.PROMPTS["P1"], SEED_SMOKE, 2)
        timing[f"paraphrase_{m}_s_per_text_batch2"] = (time.time() - t0) / 2
        fields[f"para_{m}"] = [len(o.split()) for o in outs]
        fields[f"para_{m}_sample"] = outs[0][:300]
        del model, tok
        SC.free()
    checks["5_batching"] = {"pass": all(v["ratio"] >= SC.BATCH_RATIO_MIN for v in batching.values()),
                            "min_ratio": SC.BATCH_RATIO_MIN, "per_model": batching,
                            "note": "pool F texts (the owner's reference set; no detector run); greedy decoding"}
    tok, model = SC.load_base()
    E = SC.Embedder()
    ppl_ref = np.array(C2.perplexities(tok, model, A["prompt"][:20], A["text"][:20]))
    ppl_bat = np.array(SC.perplexities(tok, model, A["prompt"][:20], A["text"][:20]))
    ppl_rel = float(np.max(np.abs(ppl_bat / ppl_ref - 1)))
    t0 = time.time()
    q = SC.raw_quality(tok, model, E, sp, outs, smoke)
    timing["quality_s_per_text"] = (time.time() - t0) / 2
    c = SC.conditions(SC.raw_quality(tok, model, E, sp, smoke), q, {"ppl": 10.0, "rep": 0.05, "cos": 0.5})
    fields["quality_keys"] = sorted(q) + sorted(c)
    # embeddings (I4)
    e1 = E([smoke[0]])
    eb = E(smoke + [A["text"][0]], bs=3)
    es = np.concatenate([E([t]) for t in smoke + [A["text"][0]]])
    i4 = {"self_cos": float((e1 * e1).sum()), "batched_vs_single_max_abs": float(np.abs(eb - es).max())}
    # gradient at layer 14 equals the Study 3 pilot's g
    g1 = SC.grad_at_layer(tok, model, smoke[0], SC.LAYER)
    g2 = PP.text_features(tok, model, smoke[0])[1]
    gdiff = float(np.abs(g1 - g2).max())
    # edits with a random direction (guided) and random edits; hook removed afterwards
    rng = np.random.default_rng(SEED_SMOKE)
    dirn = core.make_key(SEED_SMOKE, SC.D, 1.0).numpy().astype(np.float64)
    ed = SC.Editor(tok, model)
    enc = core._encode(tok, [smoke[1]]).to(SC.dev())
    enc.pop("content_mask")
    with torch.no_grad():
        before = model(**enc).logits.float().cpu()
    t0 = time.time()
    rg = ed.run(smoke, "guided", direction=dirn, layer=SC.LAYER)
    timing["edit_guided_s_per_text"] = (time.time() - t0) / 2
    t0 = time.time()
    rr = ed.run(smoke, "random", rng=rng)
    timing["edit_random_s_per_text"] = (time.time() - t0) / 2
    with torch.no_grad():
        after = model(**enc).logits.float().cpu()
    hook_diff = float((before - after).abs().max())
    owner = SC.Owner(tok, model, jload(V02 / "S_F_van.json")[:20])
    t0 = time.time()
    Gs = SC.Owner.grads(tok, model, [r["texts"]["0.1"] for r in rg])
    timing["s4_s_per_text"] = (time.time() - t0) / 2
    p = owner.pvalues(Gs, dirn)
    fields.update({"edit_n_diff": [r["n_diff"] for r in rg + rr], "edit_drift": [r["drift"] for r in rg + rr],
                   "edit_obj": [r["obj"] for r in rg], "edit_rounds": [r["rounds"] for r in rg + rr],
                   "p_smoke": p.tolist()})
    n_diff_ok = all(r["n_diff"][str(f)] == math.ceil(f * r["T"]) for r in rg + rr for f in SC.BUDGETS
                    if r["stalled_at"] is None)
    checks["4_smoke"] = {"pass": bool(i4["self_cos"] > 1 - 1e-5 and i4["batched_vs_single_max_abs"] < 1e-4
                                      and gdiff == 0.0 and hook_diff == 0.0 and n_diff_ok and ppl_rel <= 1e-3
                                      and all(len(r["texts"]) == len(SC.BUDGETS) for r in rg + rr)
                                      and all(np.isfinite(q[k]).all() for k in q)),
                         "embedding_I4": i4, "grad_layer14_max_abs_diff": gdiff, "hook_max_abs_logit_diff": hook_diff,
                         "batched_ppl_max_rel_diff_vs_v02": ppl_rel,
                         "n_diff_exact": n_diff_ok, "fields": fields,
                         "note": "unwatermarked texts and a random direction; numbers carry no information"}
    # 6. timing projected to the pilot (paraphrase: the clean batch-8 rate measured in check 5)
    b8 = {m: timing[f"paraphrase_{m}_s_per_text_batch8"] for m in MODELS}
    n_para = 500 * 1.4                                        # an allowance of 40% retries
    proj = (sum(b8[m] * n_para for m in MODELS)
            + 2 * n_para * timing["quality_s_per_text"]
            + 400 * (2 * timing["edit_guided_s_per_text"] + timing["edit_random_s_per_text"])
            + 200 * timing["edit_guided_s_per_text"] * 1.5    # rule A2's runs (1% rounds take longer)
            + 6800 * (timing["s4_s_per_text"] + timing["quality_s_per_text"])) / 3600
    checks["6_timing"] = {"pass": proj <= PILOT_BUDGET_H, "projected_pilot_h": proj, "budget_h": PILOT_BUDGET_H,
                          "timing": timing, "note": "edits here ran on 2 texts (batch efficiency not reached), "
                                                    "so the edit rate is conservative"}
    res = {"spec": SPEC.name, "spec_sha256": sha(SPEC), "date_utc": now(), "checks": checks,
           "all_pass": all(c["pass"] for c in checks.values()), "elapsed_s": time.time() - t_start,
           "note": "inputs only: no tuning-key watermarked text was paraphrased, edited or scored"}
    jsave(OUT / "VALIDATION.json", res)
    for k, cc in checks.items():
        print(k, "PASS" if cc["pass"] else "FAIL", {x: y for x, y in cc.items() if x not in ("sha256", "fields")})
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAIL")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["validate", "run", "analyse"], required=True)
    ap.add_argument("--dry", metavar="SCRATCH_DIR", help="dry run of run/analyse on stand-in unwatermarked texts")
    a = ap.parse_args()
    if a.dry:
        assert a.phase in ("run", "analyse"), "--dry is for run and analyse"
        DRY = True
        DATA, OUT = Path(a.dry) / "data", Path(a.dry) / "out"
        TIMES = DATA / "times.json"
        MODELS = ["qwen"]
    {"validate": validate, "run": run, "analyse": analyse}[a.phase]()
