"""Study 5 addendum (ROTATION_ADDENDUM_SPEC_v0.1.md; post hoc, labelled): forge with every cluster at rho = 0.35.

Imports the locked machinery unchanged (common_s5, run_s5 helpers, keyed_core, core). Checkpointed per forgery set under
research/study5_addendum/data/ (git-ignored). Writes outputs/study5_v0.1/ADDENDUM_ROTATION.{json,md}.
Run: .venv/bin/python research/study5_addendum/rotation_addendum.py --phase check|run|all
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "study5"))
import common_s5 as S  # noqa: E402
import run_s5 as R  # noqa: E402
from common_s5 import KC, PP, core  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study5_v0.1"
RHO, LI, RT = 0.35, 0, "r035"
NS = [256, 1024]
KEY_I = 96                                        # seed slot never used by the study (95 was rotation's)


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC] {msg}"
    print(line, flush=True)
    with open(DATA / "addendum.log", "a") as f:
        f.write(line + "\n")


def clusters(src, n, refC14, mix):
    Xm = (mix[:n] - refC14.mean(0)) / np.maximum(refC14.std(0, ddof=1), 1e-12)
    lab = KC.cosine_kmeans(Xm, len(src.keys), seed=S.BOOT_SEED + n)
    out = {}
    for k in range(len(src.keys)):
        if (lab == k).sum() < 2:
            continue
        vk = KC.route_a_prime_fixed(mix[:n][lab == k], refC14, RHO)
        cs = {s: float(vk @ src.key_dir(s)) for s in src.keys}
        prof = float(np.abs(Xm[lab == k].mean(0)).max())
        out[k] = {"size": int((lab == k).sum()), "best_key": int(max(cs, key=cs.get)), "best_cos": max(cs.values()), "profile": prof, "v": vk}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all")
    a = ap.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    assert "FIXED" in (HERE / "ROTATION_ADDENDUM_SPEC_v0.1.md").read_text().split("\n", 4)[2], "spec not FIXED"
    R.check_lock()                                # the study's lock still holds (nothing locked has changed)
    src = S.Src()
    refC14 = np.load(S.DATA / "refC_all.npz")["G"][:, S.LAYER].astype(np.float32)
    per = {s: np.load(S.DATA / f"F_{S.tag(s, RHO)}_obsgrads.npz")["G"][:, S.LAYER].astype(np.float32) for s in src.keys}
    m = min(len(per[s]) for s in src.keys)
    mix = np.stack([per[s][j] for j in range(m) for s in src.keys])
    saved = S.load(S.DATA / f"R_{RT}_attack.json")
    CL = {}
    for n in NS:
        CL[n] = clusters(src, n, refC14, mix)
        rec = saved["cluster"][str(n)]["clusters"]
        assert set(map(str, CL[n])) == set(rec), (n, sorted(CL[n]), sorted(rec))
        for k, c in CL[n].items():
            r_ = rec[str(k)]
            assert c["size"] == r_["size"] and c["best_key"] == r_["best_key"] and abs(c["best_cos"] - r_["best_cos"]) < 1e-6, (n, k, c, r_)
        ch = saved["cluster"][str(n)]["chosen_cluster"]
        assert np.allclose(CL[n][ch]["v"], np.asarray(saved["estimates"][str(n)]["cluster"], dtype=np.float32), atol=1e-6), n
        log(f"check n={n}: {len(CL[n])} clusters reproduce the study's records; chosen cluster {ch} estimate equal")
    if a.phase == "check":
        return
    owner = R.owner_of(src)
    ku = R.keys_unit(src)
    n_hat = float(src.attacker_norms()[S.LAYER])
    allo_p = np.concatenate([src.orig_quality(s, RHO)["ppl"] for s in src.keys])
    allo_r = np.concatenate([src.orig_quality(s, RHO)["rep"] for s in src.keys])
    cut_p, cut_r = S.cut95(allo_p), S.cut95(allo_r)
    gen_fa = S.load(OUT / "results.json")["fixed"][str(RHO)]["oracle_FA"]["median"]
    tok, model = PP.load()
    res = {"spec": "ROTATION_ADDENDUM_SPEC_v0.1.md", "rho": RHO, "bar_half_genuine_FA": 0.5 * gen_fa, "cut_ppl": cut_p, "cut_rep": cut_r, "n": {}}
    for ni, n in enumerate(NS):
        rows = {}
        for k, c in sorted(CL[n].items()):
            name = f"forge_{RT}_n{n}_c{k}"
            f = DATA / f"{name}.json"
            if not f.exists():
                v = c["v"] / max(np.linalg.norm(c["v"]), 1e-12) * RHO * n_hat
                texts = core.generate(tok, model, src.prompts_D[:S.N_FORGE], key=torch.from_numpy(v.astype(np.float32)), layer=S.LAYER, seed=S.seed(9, LI, KEY_I, 8 * ni + k))
                S.save(f, texts)
            texts = S.load(f)
            if not (DATA / f"{name}_union.npz").exists():
                U, Un = owner.union_stats(R.s4_feats(tok, model, texts), ku)
                np.savez(DATA / f"{name}_union.npz", S_true=U.astype(np.float32), S_null=Un.astype(np.float32))
                S.save(DATA / f"{name}_quality.json", R.quality(tok, model, src.prompts_D[:S.N_FORGE], texts))
                log(f"{name} done")
            z = np.load(DATA / f"{name}_union.npz")
            p = (1 + (z["S_null"] >= z["S_true"][:, None]).sum(1)) / (1 + z["S_null"].shape[1])
            q = S.load(DATA / f"{name}_quality.json")
            acc = p <= S.ALPHA
            fl = S.fluent_flags(q["ppl"], q["rep"], cut_p, cut_r).astype(bool)
            fa = float((acc & fl).mean())
            lo, hi = [float(x) for x in binom_ci(int((acc & fl).sum()), len(p))]
            rows[str(k)] = {"size": c["size"], "best_key": c["best_key"], "best_cos": c["best_cos"], "profile": c["profile"], "FA": fa, "FA_ci95": [lo, hi],
                            "accepted": float(acc.mean()), "fluent": float(fl.mean()), "median_ppl": float(np.median(q["ppl"]))}
        chosen = str(saved["cluster"][str(n)]["chosen_cluster"])
        largest = max(rows, key=lambda k: rows[k]["size"])
        best = max(rows, key=lambda k: rows[k]["FA"])
        good = [k for k, r_ in rows.items() if r_["best_cos"] >= 0.5]
        res["n"][str(n)] = {"clusters": rows, "study_rule": {"cluster": chosen, "FA": rows[chosen]["FA"]}, "largest_cluster_rule": {"cluster": largest, "FA": rows[largest]["FA"]},
                            "every_cluster": {"cluster": best, "FA": rows[best]["FA"]}, "clusters_cos_ge_0.5": len(good),
                            "clusters_cos_ge_0.5_reaching_bar": sum(rows[k]["FA"] >= 0.5 * gen_fa for k in good)}
        log(f"n={n}: study rule FA {rows[chosen]['FA']:.2f}; largest cluster FA {rows[largest]['FA']:.2f}; every cluster (max) FA {rows[best]['FA']:.2f}")
    del model, tok
    (OUT / "ADDENDUM_ROTATION.json").write_text(json.dumps(res, indent=2))
    (OUT / "ADDENDUM_ROTATION.md").write_text(markdown(res))
    log("addendum complete")


def binom_ci(x, n, z=1.96):
    """Wilson 95% interval."""
    if n == 0:
        return 0.0, 0.0
    ph = x / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def markdown(res):
    L = [f"**Post hoc, labelled (spec `study5_addendum/ROTATION_ADDENDUM_SPEC_v0.1.md`, FIXED before the run; not pre-registered; Study 5's D1 verdict for rotation stands).** "
         f"At ρ = {res['rho']:.2f} the rotation attacker forges with every cluster's estimate (100 texts each, the union test, the level's pooled fluency bars: perplexity ≤ {res['cut_ppl']:.1f}, "
         f"seq-rep-4 ≤ {res['cut_rep']:.3f}). The D1 bar (half the fixed key's genuine FA) is {100 * res['bar_half_genuine_FA']:.1f}%.\n"]
    L.append("| n | cluster | texts | best key | cosine | z-profile | accepted % | fluent % | FA % [95% Wilson] | rule |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for n, d in res["n"].items():
        for k, r_ in sorted(d["clusters"].items(), key=lambda kv: -kv[1]["best_cos"]):
            tags = [t for t, key in (("study: largest z-profile", d["study_rule"]["cluster"]), ("largest cluster", d["largest_cluster_rule"]["cluster"]), ("best FA", d["every_cluster"]["cluster"])) if key == k]
            L.append(f"| {n} | {k} | {r_['size']} | {r_['best_key']} | {r_['best_cos']:.2f} | {r_['profile']:.2f} | {100 * r_['accepted']:.0f} | {100 * r_['fluent']:.0f} | "
                     f"{100 * r_['FA']:.0f} [{100 * r_['FA_ci95'][0]:.0f}, {100 * r_['FA_ci95'][1]:.0f}] | {', '.join(tags)} |")
    for n, d in res["n"].items():
        L.append(f"\n- **n = {n}:** the study's rule (largest z-profile) gives FA {100 * d['study_rule']['FA']:.0f}%; the largest-cluster rule {100 * d['largest_cluster_rule']['FA']:.0f}%; "
                 f"an attacker who tries every cluster reaches {100 * d['every_cluster']['FA']:.0f}% (cluster {d['every_cluster']['cluster']}); "
                 f"{d['clusters_cos_ge_0.5_reaching_bar']} of the {d['clusters_cos_ge_0.5']} clusters with cosine ≥ 0.5 reach the bar.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
