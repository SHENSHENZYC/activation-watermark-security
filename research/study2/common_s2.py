"""Study 2 (STUDY2_PROTOCOL_v0.1.md): sources, the owner's S4 test (Study 3's code, features and standardisation), the
scrubbing steps (study2_pilot/scrub_core.py), quality, rules and secondaries.

Reused unchanged (hash-locked): scrub_core.py (paraphrase, editor, quality, embeddings), Study 3's common_s3.py (keys,
null keys, reference, p-values) and its saved features (pool F, the genuine oracle texts), the Study 3 pilot's
power_pilot.py (text features, transform), v0.4's run_v04.py (cluster bootstrap), v0.2's common.py and detect2.py (keys,
pools, the owner's probe). `Src` is the study's data; `DrySrc` (run_s2.py --dry) stands in tuning-key texts so every
code path runs before the lock.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "study2_pilot"))
sys.path.insert(0, str(ROOT / "research" / "study3"))
import scrub_core as SC  # noqa: E402  (first: puts v0.4, v0.3, v0.2, v0.1 and the Study 3 pilot on sys.path)
import common_s3 as S3  # noqa: E402
from scrub_core import C2, C4, PP, core  # noqa: E402
import detect2  # noqa: E402
import run_v04 as R4  # noqa: E402

V02, S3DATA = S3.V02, S3.DATA
DATA = HERE / "data"
OUT = ROOT / "research" / "outputs" / "study2_v0.1"
PROTOCOL = ROOT / "research" / "STUDY2_PROTOCOL_v0.1.md"
KEYS = list(S3.KEYS)                     # 1001-1008
LEVELS = [0.25, 0.35, 0.50, 0.70]
N_GEN, N_PHI, N_NULL, N_REF_C = 100, 50, 1000, 200
ALPHA, ALPHA2 = 0.01, 0.001
BUDGETS = (0.02, 0.05, 0.10)
ROUND, PRIMARY = 0.05, 0.05
PROMPT = "P2"
MODELS = ["qwen", "phi"]
BATCH = {"qwen": 8, "phi": 4}
G1_RANGE, G2_MAX, MIN_CAL, P1_MIN, BAR = (0.3, 2.5), 3.0, 6, 20.0, 50.0
BOOT_SEED = 20261001
SEED_PARA = 20262000                     # + 100 * model + 10 * set + attempt (chunk offset inside)
SEED_RAND = 20262001
FRESH0, N_FRESH = 44_400_000, 1000       # fresh public-distribution keys (calibration secondary)
POOL = 4
CHUNK = 200                              # paraphrase checkpoint size
ARMS = ("true", "est", "rand")


def load(p):
    return json.loads(Path(p).read_text())


def hashlib_sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj))


def tag(s, rho):
    return C4.tag(s, rho)


# ---------------------------------------------------------------- data sources
class Src:
    """Study data: Study 1 v0.2's genuine oracle texts (pool D), pool A null texts, pool F (via Study 3's features),
    the attacker's pool C references, Study 1's Route A estimates and probes."""
    dry = False
    keys, levels = KEYS, LEVELS

    def __init__(self):
        P = C2.pools()
        self.P = P
        self._pD = [u["prompt"] for u in P["D"]]

    def genuine(self, s, rho):
        return load(V02 / f"K_{tag(s, rho)}_oracle.json")[:N_GEN]

    def prompts(self, s, rho):
        return self._pD[:N_GEN]

    def null(self):
        U = self.P["A1"] + self.P["A2"]
        return load(V02 / "S_A_van.json")[:N_NULL], [u["prompt"] for u in U][:N_NULL], [u["human_continuation"] for u in U][:N_NULL]

    def attacker(self):
        U = self.P["C"][:N_REF_C]
        return load(V02 / "S_C_ref.json")[:N_REF_C], [u["prompt"] for u in U], [u["human_continuation"] for u in U]

    def key(self, s, rho):
        return C2.key(s, rho).numpy().astype(np.float64)

    def key_dir(self, s):
        return S3.key_dir(s)

    def estimate(self, s, rho):
        """Route A at n = 1,024 from Study 1 v0.2: (layer, 4-sparse vector, recorded cosine with the key)."""
        e = load(V02 / f"K_{tag(s, rho)}_summary.json")["estimates"]["1024"]["A"]
        v = np.load(V02 / f"K_{tag(s, rho)}_vhats.npy")[core.N_GRID.index(1024), 0].astype(np.float64)
        return int(e["layer"]), v, float(e["cos"])

    def ref_G(self):
        return np.load(S3DATA / "S_F_van.npz")["G"].astype(np.float32)

    def orig_G(self, s, rho):
        """The genuine texts' S4 gradients exactly as Study 3 computed them."""
        return np.load(S3DATA / f"K_{tag(s, rho)}_oracle.npz")["G"].astype(np.float32)[:N_GEN]

    def probe(self, s, rho, dev):
        import torch
        net = detect2.SimpleMLP(C2.D_MODEL).to(dev)
        net.load_state_dict(torch.load(V02 / f"K_{tag(s, rho)}_mlp.pt", map_location=dev))
        net.eval()
        S = load(V02 / f"K_{tag(s, rho)}_summary.json")
        return net, S["threshold"], S["scores_oracle"]

    def reused_files(self):
        fs = [V02 / "S_A_van.json", V02 / "S_F_van.json", V02 / "S_C_ref.json", S3DATA / "S_F_van.npz"]
        for s in KEYS:
            for rho in LEVELS:
                t = tag(s, rho)
                fs += [V02 / f"K_{t}_oracle.json", V02 / f"K_{t}_summary.json", V02 / f"K_{t}_vhats.npy",
                       V02 / f"K_{t}_mlp.pt", S3DATA / f"K_{t}_oracle.npz"]
        return fs


# ---------------------------------------------------------------- the owner's test (Study 3, unchanged)
class Owner:
    def __init__(self, src):
        G = src.ref_G()
        self.ref = S3.reference(G, G)       # S4 uses only mu_g, sd_g (as Study 3's reference(A, G))
        self.nm = PP.null_matrix()
        self._nm2 = None

    def X(self, G):
        return PP.transform("S4", None, np.asarray(G, dtype=np.float32), self.ref)

    def p(self, G, kdir):
        return S3.pv(self.X(G), kdir, self.nm)

    def p_big(self, G, kdir):
        if self._nm2 is None:
            self._nm2 = S3.null_keys_big()
        return S3.pv(self.X(G), kdir, self._nm2)

    def T(self, G, kdir):
        return self.X(G) @ kdir


# ---------------------------------------------------------------- paraphrase with the attacker's self-check (§4.1)
def paraphrase_with_checks(name, texts, prompts, orig_q, cbar, set_idx, data, log=print):
    """Up to 3 attempts; texts are retried while their attempt fails the attacker's own check (pool C bars). Each
    attempt is checkpointed per chunk of CHUNK texts in `data` (re-running resumes)."""
    n = len(texts)
    oq = {k: np.asarray(orig_q[k]) for k in ("ppl", "rep", "len")}
    attempts = [[None] * n for _ in range(SC.MAX_ATTEMPTS)]
    todo, tpara = list(range(n)), 0.0
    for a in range(SC.MAX_ATTEMPTS):
        if not todo:
            break
        fa = data / f"para_{name}_s{set_idx}_a{a}.json"
        if fa.exists():
            rec = load(fa)
            outs, tpara = rec["outs"], tpara + rec["paraphrase_s"]
            assert rec["todo"] == todo, "checkpoint does not match the attempt's texts"
        else:
            import time
            fpart = data / f"para_{name}_s{set_idx}_a{a}.partial.json"
            part = load(fpart) if fpart.exists() else {"outs": [], "s": 0.0}
            SC.free()
            tok, model = SC.load_paraphraser(name)
            for c0 in range(len(part["outs"]), len(todo), CHUNK):
                t0 = time.time()
                chunk = [texts[i] for i in todo[c0:c0 + CHUNK]]
                part["outs"] += SC.paraphrase(tok, model, chunk, SC.PROMPTS[PROMPT],
                                              SEED_PARA + 100 * MODELS.index(name) + 10 * set_idx + a + 1000 * (c0 // CHUNK),
                                              BATCH[name])
                part["s"] += time.time() - t0
                save(fpart, part)
                log(f"  {name} set {set_idx} attempt {a + 1}: {len(part['outs'])}/{len(todo)} paraphrased")
            del model, tok
            SC.free()
            outs = part["outs"]
            tpara += part["s"]
            save(fa, {"todo": todo, "outs": outs, "paraphrase_s": part["s"]})
            fpart.unlink()
        btok, base = SC.load_base()
        E = SC.Embedder()
        zq = SC.raw_quality(btok, base, E, [prompts[i] for i in todo], outs, [texts[i] for i in todo])
        cond = SC.conditions({k: oq[k][todo] for k in oq}, zq, cbar)
        nf = SC.n_fail(cond)
        for j, i in enumerate(todo):
            attempts[a][i] = {"text": outs[j], **{k: float(zq[k][j]) for k in ("ppl", "rep", "cos")},
                              "len": int(zq["len"][j]), "n_fail_attacker": int(nf[j])}
        todo = [i for j, i in enumerate(todo) if nf[j] > 0]
        del base, E, btok
        SC.free()
        log(f"  {name} set {set_idx} attempt {a + 1} checked: {len(todo)} to retry")
    kept = []
    for i in range(n):
        tried = [(a, attempts[a][i]) for a in range(SC.MAX_ATTEMPTS) if attempts[a][i] is not None]
        ok = [a for a, r in tried if r["n_fail_attacker"] == 0]
        kept.append(ok[0] if ok else min(tried, key=lambda ar: (ar[1]["n_fail_attacker"], -ar[1]["cos"], ar[0]))[0])
    return {"attempts": attempts, "kept": kept, "paraphrase_s": tpara}


def kept_texts(P):
    return [P["attempts"][a][i]["text"] for i, a in enumerate(P["kept"])]


def first_texts(P):
    return [P["attempts"][0][i]["text"] for i in range(len(P["kept"]))]


# ---------------------------------------------------------------- analysis helpers
def per_key(vals, groups):
    """vals: per text (bool or float); groups: per text key id. Returns {key: np.array}."""
    out = {}
    for v, g in zip(vals, groups):
        out.setdefault(g, []).append(float(v))
    return {k: np.asarray(v) for k, v in out.items()}


def summ(pk, keys, rng):
    """Median over keys of per-key rates (%), with v0.4's cluster bootstrap (keys, then texts)."""
    arr = [pk[k] * 100 for k in keys]
    s = R4.summarise(arr, rng)
    return {"per_key": {str(k): float(a.mean()) for k, a in zip(keys, arr)}, "median": s["median"], "ci95": s["ci95"],
            "keys_ge_50": int(sum(a.mean() >= BAR for a in arr))}


def boot_paired_diff(pa, pb, keys, rng, B=2000):
    """Median over keys of (rate_a − rate_b) with a paired cluster bootstrap (same keys, same texts)."""
    d = [pa[k].mean() * 100 - pb[k].mean() * 100 for k in keys]
    meds = []
    for _ in range(B):
        ks = rng.integers(0, len(keys), len(keys))
        vals = []
        for k in ks:
            key = keys[k]
            idx = rng.integers(0, len(pa[key]), len(pa[key]))
            vals.append(pa[key][idx].mean() * 100 - pb[key][idx].mean() * 100)
        meds.append(np.median(vals))
    return {"median": float(np.median(d)), "ci95": [float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))],
            "per_key": {str(k): float(x) for k, x in zip(keys, d)}}


def verdict(s_method, s_comp):
    """§7: effective if median >= 50 and lower bound > the comparison's upper bound; not effective if upper < 50."""
    if s_method["median"] >= BAR and s_method["ci95"][0] > s_comp["ci95"][1]:
        return "effective"
    if s_method["ci95"][1] < BAR:
        return "not effective"
    return "inconclusive"


def c1_verdict(d):
    if d["ci95"][0] > 0:
        return "the estimate helps"
    if d["ci95"][1] < 0:
        return "the estimate hurts"
    return "no clear difference"
