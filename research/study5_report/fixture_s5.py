"""Synthetic fixture for the Study 5 report builder (no outcomes; written during the run, 2026-10-02, Milestone 9).

Generates fake per-text outputs in the run's exact file layout (research/study5/run_s5.py) for the FULL study scope
(2 arms x 2 levels x 8 keys; n in {64, 256, 1024}; 100 genuine, control, forged and paraphrased texts; 1,000 null
texts) under FX/data, then runs the LOCKED analysis (common_s5.analyse, unchanged) on it and writes FX/out/results.json.
The reused inputs (Study 1 prompts, Study 2's paraphrases and bars, Study 3's features) are the real locked files; the
fixed key's Study 2 scrub success is therefore real, everything else is planted noise. The numbers carry no information;
only the file layout and the field names matter. The fixture can never write under research/outputs/study5_v0.1/.
Run: .venv/bin/python research/study5_report/fixture_s5.py FX_DIR
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "study5"))
import common_s5 as S  # noqa: E402

FX = Path(sys.argv[1]).resolve()
assert "outputs/study5_v0.1" not in str(FX) and "study5/data" not in str(FX), "the fixture must live outside the study's folders"
DATA, OUT = FX / "data", FX / "out"
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(5)
D, M, N, NN = S.D, 999, S.N_GEN, 1000
WORDS = "the city council met on tuesday to discuss the new budget for roads schools and parks while residents asked questions".split()


def text(j, label):
    w = rng.choice(WORDS, size=60)
    return f"[{label} {j}] " + " ".join(w) + "."


def ids(n):
    return rng.integers(0, 150000, size=(n, S.T_MAX)).tolist()


def stats(name, mu, n, sd_true=1.0):
    S_true = rng.normal(mu, sd_true, n).astype(np.float32)
    S_null = rng.normal(0.0, 1.0, (n, M)).astype(np.float32)
    np.savez(DATA / f"{name}.npz", S_true=S_true, S_null=S_null, npos=np.full(n, 250, dtype=np.int64))
    return S_true, S_null


def qual(n, ppl_mu=2.5, with_len=True):
    q = {"ppl": np.exp(rng.normal(ppl_mu, 0.35, n)).tolist(), "rep": np.clip(rng.normal(0.004, 0.004, n), 0, None).tolist()}
    if with_len:
        q["len"] = [S.T_MAX] * n
    return q


def save(name, obj):
    S.save(DATA / name, obj)


def conds(o, z, b):
    olen = np.minimum(o["len"], S.T_MAX)
    c = {"ppl": z["ppl"] <= np.maximum(1.25 * o["ppl"], b["ppl"]), "rep": z["rep"] <= np.maximum(o["rep"], b["rep"]),
         "len": z["len"] >= 0.8 * olen, "cos": z["cos"] > b["cos"]}
    c["all"] = c["ppl"] & c["rep"] & c["len"] & c["cos"]
    return c


t0 = time.time()
src0 = S.Src()                                   # the real locked inputs (prompts, bars, Study 2 paraphrases)
bars = src0.bars
# ---- phase S: calibration statistics
for arm in S.ARMS:
    for s in S.KEYS:
        stats(f"S_null_{arm}_k{s}", 0.0, NN)
stats("S_null_union", 0.0, NN)
np.savez(DATA / "ref_owner.npz", mu=np.zeros(D, np.float32), sd=np.ones(D, np.float32), n=np.int64(1))
# ---- phase K: the keyed arms
MU_F = {"h1": {64: 0.3, 256: 1.0, 1024: 2.2}, "h4": {64: 0.0, 256: 0.2, 1024: 0.6}}
for ai, (arm, h) in enumerate(S.ARMS.items()):
    for rho in S.LEVELS:
        for s in S.KEYS:
            t = f"{arm}_{S.tag(s, rho)}"
            gq = qual(N, 2.4 if arm == "h1" else 2.35)
            for name, mu, q in (("genuine", 4.0 + 2 * (rho - 0.35), gq), ("control", 0.0, qual(N))):
                save(f"K_{t}_{name}.json", {"texts": [text(j, f"{t} {name}") for j in range(N)], "ids": ids(N), "gen_s": 115.0})
                stats(f"K_{t}_{name}", mu, N)
                save(f"K_{t}_{name}_quality.json", q)
            save(f"K_{t}_obs.json", {"texts": [text(j, f"{t} obs") for j in range(S.N_OBS[arm])], "ids": ids(S.N_OBS[arm]), "gen_s": 1180.0})
            att = {"n_distinct_contexts": int(rng.integers(20000, 40000)), "n_eligible_contexts": int(rng.integers(100, 400))}
            for n in S.N_GRID:
                cw = (0.05 + 0.25 * np.log2(n / 64) / 4) * (1.0 if arm == "h1" else 0.1) + rng.normal(0, 0.01)
                att[str(n)] = {"n_contexts": int((n / 1024) * (300 if arm == "h1" else 6)), "cos_weighted": float(cw), "cos_mean": float(cw * 0.8),
                               "cos_by_count": {"16": float(cw * 0.5), "32": float(cw), "128": float(cw * 1.5) if n >= 256 else None,
                                                "512": float(cw * 2) if n >= 1024 else None},
                               "coverage_genuine": float(min(0.95, (0.3 + 0.3 * np.log2(n / 64) / 4) * (1.0 if arm == "h1" else 0.003)))}
            save(f"K_{t}_attacker.json", att)
            for n in S.FORGE_N:
                save(f"K_{t}_forge_n{n}.json", {"texts": [text(j, f"{t} forge{n}") for j in range(N)], "ids": ids(N), "steered_positions": [int(x) for x in rng.integers(60, 250, N)]})
                stats(f"K_{t}_forge_n{n}", MU_F[arm][n] * (1 + (rho - 0.35)), N)
                save(f"K_{t}_forge_n{n}_quality.json", qual(N, 2.6))
            save(f"K_{t}_done.json", {"gen_s": {"genuine": 115.0, "control": 116.0, "obs": 1180.0}})
    # ---- phase P: paraphrases
    items = [(s, rho, j) for rho in S.LEVELS for s in S.KEYS for j in range(S.N_PARA)]
    kept = rng.choice([0, 0, 0, 1, 2], size=len(items)).tolist()
    attempts = [[None] * len(items) for _ in range(3)]
    for i, (s, rho, j) in enumerate(items):
        for a in range(kept[i] + 1):
            attempts[a][i] = {"text": text(j, f"{arm} para {s} {rho} a{a}"), "ppl": float(np.exp(rng.normal(2.7, 0.3))), "rep": 0.002,
                              "cos": float(rng.uniform(0.75, 0.95)), "len": int(rng.integers(150, 256)), "n_fail_attacker": int(a < kept[i])}
    texts = [attempts[kept[i]][i]["text"] for i in range(len(items))]
    save(f"P_{arm}_all.json", {"items": items, "kept": kept, "texts": texts, "attempts": attempts, "paraphrase_s": 5600.0})
    for rho in S.LEVELS:
        for s in S.KEYS:
            t = f"{arm}_{S.tag(s, rho)}"
            gq = {k: np.asarray(S.load(DATA / f"K_{t}_genuine_quality.json")[k], dtype=np.float64) for k in ("ppl", "rep", "len")}
            raw = {"ppl": np.exp(rng.normal(2.7, 0.3, N)), "rep": np.clip(rng.normal(0.002, 0.003, N), 0, None),
                   "len": rng.integers(150, 257, N).astype(np.float64), "cos": rng.uniform(0.72, 0.97, N)}
            c = conds(gq, raw, bars["A"])
            stats(f"P_{t}", 0.6 + 0.5 * (rho - 0.35), N)
            save(f"P_{t}_quality.json", {"all": c["all"].tolist(), **{k: c[k].tolist() for k in ("ppl", "rep", "len", "cos")},
                                         "raw": {k: v.tolist() for k, v in raw.items()}})
# ---- phase F: the fixed arm (Study 1's texts; S4 statistics)
MU_FX = {64: 1.6, 256: 3.0, 1024: 4.2}
for li, rho in enumerate(S.LEVELS):
    for s in S.KEYS:
        t = S.tag(s, rho)
        stats(f"F_{t}_oracle", 4.2 + 2 * (rho - 0.35), N)
        stats(f"F_{t}_random", 0.0, N)
        save(f"F_{t}_random_quality.json", qual(N, 2.5, with_len=False))
        est = {}
        for n in S.N_GRID:
            ck = min(0.98, 0.55 + 0.2 * np.log2(n / 64) / 2 + 0.3 * (rho - 0.35) + rng.normal(0, 0.03))
            v = rng.normal(0, 1, D).astype(np.float32)
            est[str(n)] = {"search": {"layer": int(14 if rng.uniform() < 0.75 else rng.integers(0, 28)), "cos": float(ck * rng.uniform(0.5, 1.0)), "vhat": v.tolist()},
                           "known": {"cos": float(ck), "vhat": v.tolist()}}
        save(f"F_{t}_est.json", est)
        for n in S.FORGE_N:
            save(f"F_{t}_forge_n{n}.json", [text(j, f"F {t} forge{n}") for j in range(N)])
            stats(f"F_{t}_forge_n{n}", MU_FX[n] * (1 + (rho - 0.35)), N)
            save(f"F_{t}_forge_n{n}_quality.json", qual(N, 2.7))
        save(f"F_{t}_forge_search_n256.json", [text(j, f"F {t} search") for j in range(N)])
        stats(f"F_{t}_forge_search_n256", 2.3, N)
        save(f"F_{t}_forge_search_n256_quality.json", qual(N, 2.7))
        save(f"F_{t}_done.json", {"ok": True})
# ---- phase R: rotation
for li, rho in enumerate(S.LEVELS):
    rt = f"r{int(round(rho * 100)):03d}"
    for s in S.KEYS:
        t = S.tag(s, rho)
        stats(f"R_{t}_oracle_union", 3.6 + 2 * (rho - 0.35), N)
        n_para = len(src0.s2_para(s, rho)[0])
        stats(f"R_{t}_para_union", 0.8, n_para)
    out = {"naive": {}, "cluster": {}, "estimates": {}}
    for n in S.N_GRID:
        out["naive"][str(n)] = {str(s): float(max(0.0, rng.normal(0.55, 0.1))) if s == S.KEYS[2] else float(max(0.0, rng.normal(0.02, 0.03))) for s in S.KEYS}
        cl = {}
        for k in range(len(S.KEYS)):
            cl[str(k)] = {"size": int(n // 8), "best_key": int(S.KEYS[k]), "best_cos": float(min(0.99, max(0.0, rng.normal(0.4 + 0.25 * np.log2(n / 64) / 2, 0.1)))),
                          "profile": float(rng.uniform(1, 5))}
        out["cluster"][str(n)] = {"clusters": cl, "keys_recovered_ge_0.5": int(sum(c["best_cos"] >= 0.5 for c in cl.values())),
                                  "chosen_cluster": int(max(cl, key=lambda k: cl[k]["profile"]))}
        out["estimates"][str(n)] = {"naive": rng.normal(0, 1, D).tolist(), "cluster": rng.normal(0, 1, D).tolist()}
    save(f"R_{rt}_attack.json", out)
    for who, mus in (("naive", {64: 0.4, 256: 0.9, 1024: 1.4}), ("cluster", {64: 1.4, 256: 2.8, 1024: 4.0})):
        for n in S.FORGE_N:
            name = f"R_{rt}_forge_{who}_n{n}"
            save(f"{name}.json", [text(j, f"{name}") for j in range(N)])
            stats(f"{name}_union", mus[n], N)
            save(f"{name}_quality.json", qual(N, 2.7))
print(f"fixture data written: {sum(1 for _ in DATA.iterdir())} files, {time.time() - t0:.0f}s", flush=True)
# a run log in the runner's format, so the manifest script can be tested too
(DATA / "run.log").write_text("\n".join([
    "[2026-10-02 23:29:02 UTC] start phases SK (locked)", "[2026-10-02 23:40:00 UTC] phase S complete",
    "[2026-10-03 18:00:00 UTC] phase K complete", "[2026-10-03 18:05:00 UTC] start phases P (locked)",
    "[2026-10-03 21:30:00 UTC] phase P complete", "[2026-10-03 21:31:00 UTC] start phases FR (locked)",
    "[2026-10-03 23:30:00 UTC] phase F complete", "[2026-10-04 01:30:00 UTC] phase R complete",
    "[2026-10-04 01:31:00 UTC] start phases A (locked)", "[2026-10-04 01:32:00 UTC] phase A complete"]) + "\n")


# ---- the locked analysis on the fixture
class FxSrc(S.Src):
    def __init__(self):
        super().__init__(data=DATA)


src = FxSrc()
ro = np.load(DATA / "ref_owner.npz")
src.owner = S.Owner({"mu": ro["mu"], "sd": ro["sd"], "n_positions": int(ro["n"])}, src.ref_G())
res = S.analyse(src)
miss = S.missing_fields(res, src.levels, src.arms)
assert not miss, miss
(OUT / "results.json").write_text(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
print(f"fixture results.json written ({time.time() - t0:.0f}s); verdicts:")
print(json.dumps({arm: {rho: {k: L[k].get("verdict") for k in ("D1", "D2", "D3")} for rho, L in A["levels"].items()} for arm, A in res["arms"].items()}, indent=1))
print({rho: F["P0"]["verdict"] for rho, F in res["fixed"].items()}, {rho: {w: R["D1"][w]["verdict"] for w in R["D1"]} for rho, R in res["rotation"].items() if rho != "G1"})
