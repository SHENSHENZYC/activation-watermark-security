"""Study 5 runner (STUDY5_PROTOCOL_v0.1.md). Refuses to run unless PRE_RUN_LOCK.json matches the file hashes.

Phases, checkpointed under research/study5/data/ (git-ignored; re-running the same command resumes):
  S  shared: the owner's and the attacker's position statistics; the attacker's all-layer summed gradients of pool C;
     the keyed test on pool A's 1,000 null texts per arm and key (G1, G2); the union test on pool A
  K  keyed arms, per arm, level and key: genuine, control and observed texts; the per-context attacker's snapshots and
     tables; forgeries at each n; owner statistics and quality (observed features are consumed on the fly)
  P  paraphrase of the genuine texts (P-Qwen with the attacker's self-check), then scoring
  F  the fixed arm: all-layer summed gradients of Study 1's observed texts; Route A' (known layer and layer search);
     forgeries with Study 1's fixed hook; S4 statistics and quality; the oracle and random-key S4 statistics
  R  rotation: the mixture; the naive and the clustering attacker; forgeries; union statistics of the oracle texts,
     the forgeries and Study 2's paraphrases
  A  analysis -> outputs/study5_v0.1/results.json
Run: .venv/bin/python research/study5/run_s5.py --phase S|K|P|F|R|A|all [--dry]
"""
import argparse
import gc
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common_s5 as S  # noqa: E402  (puts the pilot, Study 2, Study 3 and Study 1 folders on sys.path)
from common_s5 import KC, TC, PP, SC, C2, core  # noqa: E402
import attack2  # noqa: E402

ROOT = S.ROOT
LOCK = S.OUT / "PRE_RUN_LOCK.json"
CODE = [HERE / "common_s5.py", HERE / "run_s5.py", HERE / "validate_s5.py",
        ROOT / "research/study5_pilot/keyed_core.py", ROOT / "research/study5_pilot/threat_check.py",
        ROOT / "research/study2/common_s2.py", ROOT / "research/study2_pilot/scrub_core.py",
        ROOT / "research/study3/common_s3.py", ROOT / "research/study3_pilot/power_pilot.py",
        ROOT / "research/study1_v04/run_v04.py", ROOT / "research/study1_v04/common4.py", ROOT / "research/study1_v04/attack4.py",
        ROOT / "research/study1_v03/common3.py", ROOT / "research/study1_v02/common.py", ROOT / "research/study1_v02/attack2.py",
        ROOT / "research/study1_v02/detect2.py", ROOT / "research/study1/core.py", ROOT / "research/study1/attack.py"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def log(msg):
    line = f"[{now()} UTC] {msg}"
    print(line, flush=True)
    with open(S.DATA / "run.log", "a") as f:
        f.write(line + "\n")


def check_lock():
    lock = json.loads(LOCK.read_text())
    assert lock["protocol_sha256"] == sha(S.PROTOCOL), "protocol changed since lock"
    for p in CODE:
        assert lock["code_sha256"][p.name] == sha(p), f"{p.name} changed since lock"
    for rel, h in lock["reused_sha256"].items():
        assert sha(ROOT / rel) == h, f"reused file changed since lock: {rel}"
    return lock


def T(name):
    return S.DATA / name


def free():
    gc.collect()
    torch.mps.empty_cache()


def save_stats(name, S_true, S_null, npos):
    np.savez(T(f"{name}.npz"), S_true=np.asarray(S_true, dtype=np.float32), S_null=np.asarray(S_null, dtype=np.float32),
             npos=np.asarray(npos, dtype=np.int64))


def quality(tok, model, prompts, texts):
    return {"ppl": SC.perplexities(tok, model, prompts, texts), "rep": SC.C4.seqrep4(tok, texts), "len": SC.n_tokens(tok, texts).tolist()}


def keyed_stats_of(owner, tok, model, texts, h, secret):
    St, Sn, Np = [], [], []
    for t in texts:
        g, ids = KC.position_grads(tok, model, t)
        a, b, c = owner.keyed_stats(g, ids, h, secret)
        St.append(a)
        Sn.append(b)
        Np.append(c)
    return np.array(St), np.stack(Sn), np.array(Np)


def s4_feats(tok, model, texts):
    return np.stack([PP.text_features(tok, model, t)[1] for t in texts]).astype(np.float32)


def owner_of(src):
    ro = np.load(T("ref_owner.npz"))
    return S.Owner({"mu": ro["mu"], "sd": ro["sd"], "n_positions": int(ro["n"])}, src.ref_G())


def keys_unit(src):
    return np.stack([src.key_dir(s) for s in src.keys])


# ------------------------------------------------------------------ phase S
def phase_s(src):
    tok, model = PP.load()
    for name, texts in (("ref_owner", src.owner_ref_texts()), ("ref_attacker", src.attacker_texts())):
        if not T(f"{name}.npz").exists():
            ps = KC.PosStats()
            for t in texts:
                ps.add(KC.position_grads(tok, model, t)[0])
            r = ps.ref()
            np.savez(T(f"{name}.npz"), mu=r["mu"], sd=r["sd"], n=r["n_positions"])
            log(f"S {name}: {r['n_positions']} positions")
    if not T("refC_all.npz").exists():
        np.savez(T("refC_all.npz"), G=np.stack([TC.all_layer_grads(tok, model, t) for t in src.attacker_texts()]).astype(np.float32))
        log("S refC_all done")
    owner = owner_of(src)
    need = [(arm, s) for arm in src.arms for s in src.keys if not T(f"S_null_{arm}_k{s}.npz").exists()]
    if need:
        acc = {(arm, s): ([], [], []) for arm, s in need}
        nt = src.null_texts()
        for i, t in enumerate(nt):
            g, ids = KC.position_grads(tok, model, t)
            for arm, s in need:
                a, b, c = owner.keyed_stats(g, ids, src.arms[arm], s)
                acc[(arm, s)][0].append(a)
                acc[(arm, s)][1].append(b)
                acc[(arm, s)][2].append(c)
            if (i + 1) % 200 == 0:
                log(f"S null {i + 1}/{len(nt)}")
        for (arm, s), (a, b, c) in acc.items():
            save_stats(f"S_null_{arm}_k{s}", a, np.stack(b), c)
    if not T("S_null_union.npz").exists():
        U, Un = owner.union_stats(src.null_G(), keys_unit(src))
        save_stats("S_null_union", U, Un, np.zeros(len(U)))
    del model, tok
    free()
    log("phase S complete")


# ------------------------------------------------------------------ phase K
def phase_k(src):
    owner = owner_of(src)
    ra = np.load(T("ref_attacker.npz"))
    ref_att = {"mu": ra["mu"], "sd": ra["sd"]}
    n_hat = float(src.attacker_norms()[S.LAYER])
    tok, model = PP.load()
    t0 = time.time()
    for ai, (arm, h) in enumerate(src.arms.items()):
        for li, rho in enumerate(src.levels):
            for ki, s in enumerate(src.keys):
                t = f"{arm}_{S.tag(s, rho)}"
                if T(f"K_{t}_done.json").exists():
                    continue
                sets = {}
                for name, prompts, secret, off, n in (("genuine", src.prompts_D, s, 20, S.N_GEN),
                                                      ("control", src.prompts_D, S.CONTROL[s], 30, S.N_GEN),
                                                      ("obs", src.prompts_B[:S.N_OBS[arm]], s, 10, S.N_OBS[arm])):
                    f = T(f"K_{t}_{name}.json")
                    if not f.exists():
                        tt = time.time()
                        texts, ids, used = KC.generate(tok, model, prompts[:n], "keyed", h=h, secret=secret, rho=rho, seed=S.seed(ai, li, ki, off))
                        S.save(f, {"texts": texts, "ids": ids, "gen_s": time.time() - tt})
                    sets[name] = S.load(f)
                for name in ("genuine", "control"):
                    if not T(f"K_{t}_{name}.npz").exists():
                        St, Sn, Np = keyed_stats_of(owner, tok, model, sets[name]["texts"], h, s)
                        save_stats(f"K_{t}_{name}", St, Sn, Np)
                    if not T(f"K_{t}_{name}_quality.json").exists():
                        S.save(T(f"K_{t}_{name}_quality.json"), quality(tok, model, src.prompts_D, sets[name]["texts"]))
                # the attacker: observed features consumed on the fly; snapshots at each n
                if not T(f"K_{t}_attacker.json").exists():
                    A = KC.ContextAttacker(ref_att, h, S.C_MIN, rho * n_hat)
                    obs_ids = [np.asarray(x) for x in sets["obs"]["ids"]]
                    A.eligible_from_ids(obs_ids)
                    gen_ids = [np.asarray(x) for x in sets["genuine"]["ids"]]
                    out = {"n_distinct_contexts": len(A.all_counts), "n_eligible_contexts": len(A.eligible)}
                    done = 0
                    for n in [x for x in S.N_GRID if x <= S.N_OBS[arm]]:
                        for text in sets["obs"]["texts"][done:n]:
                            g, ids = KC.position_grads(tok, model, text)
                            A.observe(g, ids)
                        done = n
                        out[str(n)] = {**A.score(s), "coverage_genuine": A.coverage(gen_ids)}
                        tab = A.table()
                        np.savez(T(f"K_{t}_table_n{n}.npz"), ctx=np.asarray(list(tab.keys()), dtype=np.int64).reshape(len(tab), h),
                                 V=np.stack(list(tab.values())) if tab else np.zeros((0, S.D), dtype=np.float32))
                    S.save(T(f"K_{t}_attacker.json"), out)
                for ni, n in enumerate([x for x in S.FORGE_N if x <= S.N_OBS[arm]]):
                    f = T(f"K_{t}_forge_n{n}.json")
                    if not f.exists():
                        z = np.load(T(f"K_{t}_table_n{n}.npz"))
                        table = {tuple(int(i) for i in c): v for c, v in zip(z["ctx"], z["V"])}
                        texts, ids, used = KC.generate(tok, model, src.prompts_D[:S.N_FORGE], "table", h=h, table=table, seed=S.seed(ai, li, ki, 40 + ni))
                        S.save(f, {"texts": texts, "ids": ids, "steered_positions": [len(u) for u in used]})
                    if not T(f"K_{t}_forge_n{n}.npz").exists():
                        tx = S.load(f)["texts"]
                        St, Sn, Np = keyed_stats_of(owner, tok, model, tx, h, s)
                        save_stats(f"K_{t}_forge_n{n}", St, Sn, Np)
                        S.save(T(f"K_{t}_forge_n{n}_quality.json"), quality(tok, model, src.prompts_D[:S.N_FORGE], tx))
                S.save(T(f"K_{t}_done.json"), {"gen_s": {k: v.get("gen_s") for k, v in sets.items()}})
                log(f"K {t} done, {time.time() - t0:.0f}s")
    del model, tok
    free()
    log("phase K complete")


# ------------------------------------------------------------------ phase P
def phase_p(src):
    import common_s2 as S2
    owner = owner_of(src)
    for ai, (arm, h) in enumerate(src.arms.items()):
        f = T(f"P_{arm}_all.json")
        if not f.exists():
            items = [(s, rho, j) for rho in src.levels for s in src.keys for j in range(S.N_PARA)]
            texts = [S.load(T(f"K_{arm}_{S.tag(s, rho)}_genuine.json"))["texts"][j] for s, rho, j in items]
            prompts = [src.prompts_D[j] for _, _, j in items]
            oq = {k: [] for k in ("ppl", "rep", "len")}
            for s, rho, j in items:
                q = S.load(T(f"K_{arm}_{S.tag(s, rho)}_genuine_quality.json"))
                for k in oq:
                    oq[k].append(q[k][j])
            res = S2.paraphrase_with_checks("qwen", texts, prompts, oq, src.bars["C"], S.SET_IDX0 + ai, S.DATA, log=log)
            S.save(f, {"items": items, "kept": res["kept"], "texts": S2.kept_texts(res), "attempts": res["attempts"], "paraphrase_s": res["paraphrase_s"]})
            log(f"P {arm} paraphrased")
    free()
    tok, model = PP.load()
    E = SC.Embedder()
    for ai, (arm, h) in enumerate(src.arms.items()):
        P = S.load(T(f"P_{arm}_all.json"))
        for rho in src.levels:
            for s in src.keys:
                t = f"{arm}_{S.tag(s, rho)}"
                if T(f"P_{t}.npz").exists():
                    continue
                idx = [i for i, (s_, r_, _) in enumerate(P["items"]) if s_ == s and abs(r_ - rho) < 1e-9]
                kept = [P["texts"][i] for i in idx]
                orig = S.load(T(f"K_{t}_genuine.json"))["texts"][:len(idx)]
                oq = {k: np.asarray(S.load(T(f"K_{t}_genuine_quality.json"))[k][:len(idx)]) for k in ("ppl", "rep", "len")}
                zq = SC.raw_quality(tok, model, E, src.prompts_D[:len(idx)], kept, orig)
                cond = SC.conditions(oq, zq, src.bars["A"])
                St, Sn, Np = keyed_stats_of(owner, tok, model, kept, h, s)
                save_stats(f"P_{t}", St, Sn, Np)
                S.save(T(f"P_{t}_quality.json"), {"all": cond["all"].tolist(), **{k: cond[k].tolist() for k in ("ppl", "rep", "len", "cos")},
                                                  "raw": {k: np.asarray(v).tolist() for k, v in zq.items()}})
                log(f"P {t} scored")
    del model, E, tok
    free()
    log("phase P complete")


# ------------------------------------------------------------------ phase F
def phase_f(src):
    owner = owner_of(src)
    refC = np.load(T("refC_all.npz"))["G"]
    norms = src.attacker_norms()
    tok, model = PP.load()
    if getattr(src, "dry", False):
        src.prepare(tok, model)                 # the smoke test's stand-in features and quality
    for li, rho in enumerate(src.levels):
        for ki, s in enumerate(src.keys):
            t = S.tag(s, rho)
            if T(f"F_{t}_done.json").exists():
                continue
            vt = src.key_dir(s)
            if not T(f"F_{t}_obsgrads.npz").exists():
                obs = src.obs_texts(s, rho)[:max(S.N_GRID)]
                np.savez(T(f"F_{t}_obsgrads.npz"), G=np.stack([TC.all_layer_grads(tok, model, x) for x in obs]).astype(np.float16))
                log(f"F {t} observed gradients")
            G = np.load(T(f"F_{t}_obsgrads.npz"))["G"].astype(np.float32)
            est = {}
            for n in S.N_GRID:
                lh, vs, _ = attack2.route_a(G[:n], refC, S.KC.K, rho, np.ones(G.shape[1]))
                _, vk, _ = attack2.route_a(G[:n, S.LAYER:S.LAYER + 1], refC[:, S.LAYER:S.LAYER + 1], S.KC.K, rho, np.ones(1))
                est[str(n)] = {"search": {"layer": int(lh), "cos": float(PP.unit(vs.astype(np.float64)) @ vt), "vhat": vs.tolist()},
                               "known": {"cos": float(PP.unit(vk.astype(np.float64)) @ vt), "vhat": vk.tolist()}}
            S.save(T(f"F_{t}_est.json"), est)
            jobs = [(f"forge_n{n}", est[str(n)]["known"]["vhat"], S.LAYER, 40 + ni) for ni, n in enumerate(S.FORGE_N)]
            n_mid = S.N_GRID[len(S.N_GRID) // 2]                   # 256 in the study; the layer-search forgery set
            jobs.append((f"forge_search_n{n_mid}", est[str(n_mid)]["search"]["vhat"], est[str(n_mid)]["search"]["layer"], 49))
            for name, vh, layer, off in jobs:
                f = T(f"F_{t}_{name}.json")
                if not f.exists():
                    v = np.asarray(vh, dtype=np.float32)
                    v = v / max(np.linalg.norm(v), 1e-12) * rho * norms[layer]
                    texts = core.generate(tok, model, src.prompts_D[:S.N_FORGE], key=torch.from_numpy(v), layer=layer, seed=S.seed(9, li, ki, off))
                    S.save(f, texts)
                if not T(f"F_{t}_{name}.npz").exists():
                    texts = S.load(f)
                    Tt, Tn = owner.s4_stats(s4_feats(tok, model, texts), vt)
                    save_stats(f"F_{t}_{name}", Tt, Tn, np.zeros(len(Tt)))
                    S.save(T(f"F_{t}_{name}_quality.json"), quality(tok, model, src.prompts_D[:S.N_FORGE], texts))
            for c in ("oracle", "random"):
                Tt, Tn = owner.s4_stats(src.fixed_G(s, rho, c), vt)
                save_stats(f"F_{t}_{c}", Tt, Tn, np.zeros(len(Tt)))
            S.save(T(f"F_{t}_random_quality.json"), {"ppl": src.fixed_ppl(s, rho, "random"), "rep": SC.C4.seqrep4(tok, src.fixed_texts(s, rho, "random"))})
            S.save(T(f"F_{t}_done.json"), {"ok": True})
            log(f"F {t} done")
    del model, tok
    free()
    log("phase F complete")


# ------------------------------------------------------------------ phase R
def phase_r(src):
    owner = owner_of(src)
    ku = keys_unit(src)
    refC14 = np.load(T("refC_all.npz"))["G"][:, S.LAYER].astype(np.float32)
    n_hat = float(src.attacker_norms()[S.LAYER])
    tok, model = PP.load()
    for li, rho in enumerate(src.levels):
        rt = f"r{int(round(rho * 100)):03d}"
        for s in src.keys:
            t = S.tag(s, rho)
            if not T(f"R_{t}_oracle_union.npz").exists():
                U, Un = owner.union_stats(src.fixed_G(s, rho, "oracle"), ku)
                save_stats(f"R_{t}_oracle_union", U, Un, np.zeros(len(U)))
            if not T(f"R_{t}_para_union.npz").exists():
                _, G, _ = src.s2_para(s, rho)
                U, Un = owner.union_stats(G, ku)
                save_stats(f"R_{t}_para_union", U, Un, np.zeros(len(U)))
        if not T(f"R_{rt}_attack.json").exists():
            per = {s: np.load(T(f"F_{S.tag(s, rho)}_obsgrads.npz"))["G"][:, S.LAYER].astype(np.float32) for s in src.keys}
            m = min(len(per[s]) for s in src.keys)
            mix = np.stack([per[s][j] for j in range(m) for s in src.keys])
            out = {"naive": {}, "cluster": {}, "estimates": {}}
            for n in S.N_GRID:
                v = KC.route_a_prime_fixed(mix[:n], refC14, rho)
                out["naive"][str(n)] = {str(s): float(v @ src.key_dir(s)) for s in src.keys}
                Xm = (mix[:n] - refC14.mean(0)) / np.maximum(refC14.std(0, ddof=1), 1e-12)
                lab = KC.cosine_kmeans(Xm, len(src.keys), seed=S.BOOT_SEED + n)
                cl, best = {}, (None, -1.0, None)
                for k in range(len(src.keys)):
                    if (lab == k).sum() < 2:
                        continue
                    vk = KC.route_a_prime_fixed(mix[:n][lab == k], refC14, rho)
                    cs = {s: float(vk @ src.key_dir(s)) for s in src.keys}
                    prof = float(np.abs(((mix[:n][lab == k] - refC14.mean(0)) / np.maximum(refC14.std(0, ddof=1), 1e-12)).mean(0)).max())
                    cl[str(k)] = {"size": int((lab == k).sum()), "best_key": int(max(cs, key=cs.get)), "best_cos": max(cs.values()), "profile": prof}
                    if prof > best[1]:
                        best = (k, prof, vk)
                out["cluster"][str(n)] = {"clusters": cl, "keys_recovered_ge_0.5": len({c["best_key"] for c in cl.values() if c["best_cos"] >= 0.5}),
                                          "chosen_cluster": best[0]}
                out["estimates"][str(n)] = {"naive": v.tolist(), "cluster": (best[2].tolist() if best[2] is not None else v.tolist())}
            S.save(T(f"R_{rt}_attack.json"), out)
            log(f"R {rt} attackers done")
        ro = S.load(T(f"R_{rt}_attack.json"))
        for wi, who in enumerate(("naive", "cluster")):
            for ni, n in enumerate(S.FORGE_N):
                name = f"R_{rt}_forge_{who}_n{n}"
                f = T(f"{name}.json")
                if not f.exists():
                    v = np.asarray(ro["estimates"][str(n)][who], dtype=np.float32)
                    v = v / max(np.linalg.norm(v), 1e-12) * rho * n_hat
                    S.save(f, core.generate(tok, model, src.prompts_D[:S.N_FORGE], key=torch.from_numpy(v), layer=S.LAYER, seed=S.seed(9, li, 95, 10 * wi + ni)))
                if not T(f"{name}_union.npz").exists():
                    texts = S.load(f)
                    U, Un = owner.union_stats(s4_feats(tok, model, texts), ku)
                    save_stats(f"{name}_union", U, Un, np.zeros(len(U)))
                    S.save(T(f"{name}_quality.json"), quality(tok, model, src.prompts_D[:S.N_FORGE], texts))
        log(f"R {rt} done")
    del model, tok
    free()
    log("phase R complete")


# ------------------------------------------------------------------ phase A
def phase_a(src):
    src.owner = owner_of(src)
    res = S.analyse(src)
    miss = S.missing_fields(res, src.levels, src.arms)
    assert not miss, f"missing result fields: {miss[:12]}"
    S.OUT.mkdir(parents=True, exist_ok=True)
    (S.OUT / "results.json").write_text(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    log("phase A complete")
    print(json.dumps({arm: {rho: {k: L[k].get("verdict", L[k]) for k in ("D1", "D2", "D3")} for rho, L in A["levels"].items()}
                      for arm, A in res["arms"].items()}, indent=1, default=str)[:3000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all")
    ap.add_argument("--dry", action="store_true", help="smoke test on tuning-key stand-ins (validate_s5.DrySrc); no lock needed")
    a = ap.parse_args()
    if a.dry:
        import validate_s5
        src = validate_s5.DrySrc()          # sets S.DATA to the dry folder and shrinks the scope
    S.DATA.mkdir(parents=True, exist_ok=True)
    if a.dry:
        pass
    else:
        lock = check_lock()
        src = S.Src()
    phases = "SKPFRA" if a.phase == "all" else a.phase
    log(f"start phases {phases} ({'dry' if a.dry else 'locked'})")
    for ph in phases:
        {"S": phase_s, "K": phase_k, "P": phase_p, "F": phase_f, "R": phase_r, "A": phase_a}[ph](src)


if __name__ == "__main__":
    main()
