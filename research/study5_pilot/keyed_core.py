"""Study 5 machinery (DEFENCE_PILOT_SPEC_v0.1.md): keyed activation steering, its exact test, and its attackers.

Schemes. Fixed (h = 0): Study 1's scheme, one 4-sparse key at every position (core.make_key, scaled to rho * N_REF).
Context-hashed (h >= 1): at continuation position t >= h the key is a 4-sparse unit vector derived by a keyed PRF from
the secret and the previous h token ids, scaled to rho * N_REF; positions t < h and the prompt are not steered.
Rotation: one of K fixed keys per text; the detector tests the union (a max statistic, calibrated by resampling all K).

Detector. Per-position gradients g_t of the continuation log-likelihood with respect to an additive vector at the
output of layer 14 (one backward pass), standardised per dimension with pooled position statistics of the owner's
reference texts; S(x, m) = sum over positions with a complete context of <x_t, v_m(c_t)>; the p-value is the rank of
S(x, secret) among S(x, m_j) for 999 null secrets (exact for any statistic, on average over secrets).

Attacker (Route A'-h). The same per-position gradients, standardised against the attacker's own reference texts,
grouped by the observable context; for each context seen at least c_min times, the key estimate is the top-4
coordinates of the mean (Study 1's Route A rule). The forgery steers only estimated contexts.

Reused unchanged: study1/core.py, study1_v02/common.py and attack2.py, study3_pilot/power_pilot.py, study3/common_s3.py.
"""
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in ("study3", "study3_pilot", "study1_v04", "study1_v03", "study1_v02", "study1"):
    sys.path.insert(0, str(ROOT / "research" / p))
import common_s3 as S3  # noqa: E402  (Study 3; imports v0.4, v0.3, v0.2, v0.1 and the power pilot)
import power_pilot as PP  # noqa: E402
import common as C2  # noqa: E402  (Study 1 v0.2)
import attack2  # noqa: E402  (Study 1 v0.2: route_a)
from common import core  # noqa: E402

LAYER, D, T_MAX, K = C2.LAYER, C2.D_MODEL, core.NEW_TOKENS, C2.K_SUPPORT   # 14, 1536, 256, 4
N_REF = C2.N_REF                                                           # 56.90: the owner's strength scale
M_NULL = 999
NULL_SECRET_SEED = 20261002        # the 999 public null secrets (uint64) for the keyed test
MASK = np.uint64((1 << 64) - 1)
_PHI = np.uint64(0x9E3779B97F4A7C15)
_C1, _C2, _C3 = np.uint64(0xBF58476D1CE4E5B9), np.uint64(0x94D049BB133111EB), np.uint64(0xD1B54A32D192ED03)


# ---------------------------------------------------------------- the keyed PRF (vectorised, deterministic)
def _mix(x):
    """splitmix64 finaliser on uint64 arrays (wrapping arithmetic)."""
    x = np.asarray(x, dtype=np.uint64)
    with np.errstate(over="ignore"):
        x = (x ^ (x >> np.uint64(30))) * _C1
        x = (x ^ (x >> np.uint64(27))) * _C2
        return x ^ (x >> np.uint64(31))


def context_hash(secrets, ctx):
    """secrets: uint64 [M]; ctx: int [P, h] token ids. Returns uint64 [M, P] (h = 0 gives one hash per secret)."""
    s = np.asarray(secrets, dtype=np.uint64).reshape(-1, 1)
    ctx = np.asarray(ctx, dtype=np.uint64)
    P = ctx.shape[0]
    with np.errstate(over="ignore"):
        x = _mix(s + _PHI) * np.ones((1, max(P, 1)), dtype=np.uint64)
        for i in range(ctx.shape[1]):
            x = _mix(x ^ (ctx[None, :, i] + _PHI * np.uint64(i + 1)))
    return x[:, :P]


def keys_from_hash(hsh):
    """hsh: uint64 [...]. Returns (idx int64 [..., K] distinct, w float64 [..., K] unit norm per key)."""
    hsh = np.asarray(hsh, dtype=np.uint64)
    idx = np.empty(hsh.shape + (K,), dtype=np.int64)
    w = np.empty(hsh.shape + (K,), dtype=np.float64)
    with np.errstate(over="ignore"):
        for i in range(K):
            hi = _mix(hsh + np.uint64(i + 1) * _C3)
            idx[..., i] = ((hi >> np.uint64(11)) % np.uint64(D)).astype(np.int64)
            w[..., i] = 2.0 * ((hi & np.uint64((1 << 53) - 1)).astype(np.float64) / float(1 << 53)) - 1.0
    for i in range(1, K):                     # resolve the rare collisions deterministically
        for _ in range(K):
            dup = np.zeros(hsh.shape, dtype=bool)
            for j in range(i):
                dup |= idx[..., i] == idx[..., j]
            if not dup.any():
                break
            idx[..., i] = np.where(dup, (idx[..., i] + 1) % D, idx[..., i])
    w /= np.linalg.norm(w, axis=-1, keepdims=True)
    return idx, w


def contexts(ids, h):
    """ids: int [T]. Positions t = h..T-1 and their contexts ids[t-h:t] ([T-h, h]); h = 0: every position, empty ctx."""
    ids = np.asarray(ids, dtype=np.int64)
    T = len(ids)
    if T <= h:
        return np.zeros(0, dtype=np.int64), np.zeros((0, h), dtype=np.int64)
    pos = np.arange(h, T)
    ctx = np.stack([ids[pos - h + i] for i in range(h)], 1) if h > 0 else np.zeros((len(pos), 0), dtype=np.int64)
    return pos, ctx


def dense_keys(secret, ctx, scale=1.0):
    """[P, D] float32 dense key vectors for the contexts (unit norm times scale)."""
    idx, w = keys_from_hash(context_hash([secret], ctx)[0])
    V = np.zeros((ctx.shape[0], D), dtype=np.float32)
    np.put_along_axis(V, idx, (w * scale).astype(np.float32), axis=1)
    return V


def null_secrets(M=M_NULL):
    return np.random.default_rng(NULL_SECRET_SEED).integers(0, 2**63 - 1, M, dtype=np.int64).astype(np.uint64)


def fixed_dir(seed):
    """The fixed scheme's unit key direction (Study 1's make_key)."""
    return PP.unit(core.make_key(seed, D, 1.0).numpy().astype(np.float64))


# ---------------------------------------------------------------- the stateful steering hook and generation
class KeyedSteer:
    """A forward pre-hook on the token embedding (records each forward call's input ids) plus a forward hook on the
    steered layer. Modes: 'fixed' adds `vec` at every position of every call (prompt included), as core.AddVector;
    'keyed' adds key(secret, previous h continuation tokens) at a decode step once at least h continuation tokens
    precede the current one, nothing at prefill; 'table' adds table[context] when present (the attacker's forgery)."""

    def __init__(self, model, mode, h=0, secret=None, scale=1.0, vec=None, table=None):
        self.model, self.mode, self.h, self.scale = model, mode, h, float(scale)
        self.secret = None if secret is None else np.uint64(secret)
        self.vec = vec
        self.table = table or {}
        self.dtype = model.dtype
        self.dev = next(model.parameters()).device
        self.hist, self.prefill, self.used = None, True, []
        self._hs = [model.model.embed_tokens.register_forward_pre_hook(self._pre),
                    model.model.layers[LAYER].register_forward_hook(self._layer)]

    def remove(self):
        for hd in self._hs:
            hd.remove()

    def _pre(self, module, args):
        ids = args[0]
        if ids.shape[1] > 1 or self.hist is None:          # prefill (a new batch)
            self.hist = [[] for _ in range(ids.shape[0])]
            self.used = [[] for _ in range(ids.shape[0])]
            self.prefill = True
        else:
            self.prefill = False
            for r, x in enumerate(ids[:, 0].tolist()):
                self.hist[r].append(x)

    def _current_vectors(self, B):
        V = np.zeros((B, D), dtype=np.float32)
        rows, ctxs = [], []
        for r in range(B):
            seq = self.hist[r]
            t = len(seq) - 1                                   # the current continuation position (0-based)
            if t < self.h:
                continue
            c = tuple(seq[t - self.h:t])
            if self.mode == "keyed":
                rows.append(r)
                ctxs.append(c)
            elif c in self.table:
                V[r] = self.table[c]
                self.used[r].append((t, c))
        if rows:                                               # one vectorised PRF call per decode step
            ctx = np.asarray(ctxs, dtype=np.int64).reshape(len(rows), self.h)
            idx, w = keys_from_hash(context_hash([self.secret], ctx)[0])
            for j, r in enumerate(rows):
                V[r, idx[j]] = (w[j] * self.scale).astype(np.float32)
                self.used[r].append((len(self.hist[r]) - 1, tuple(int(i) for i in idx[j])))
        return V

    def _layer(self, module, inputs, output):
        h = output[0] if isinstance(output, tuple) else output
        if self.mode == "fixed":
            h2 = h + self.vec
        else:
            if self.prefill:
                return output
            V = torch.from_numpy(self._current_vectors(h.shape[0])).to(self.dev, self.dtype).unsqueeze(1)
            h2 = h + V
        return (h2,) + tuple(output[1:]) if isinstance(output, tuple) else h2


def generate(tok, model, prompts, mode, h=0, secret=None, rho=None, vec=None, table=None, seed=0, batch_size=16,
             scale=None):
    """core.generate's loop (same batching, seeds and sampling) with the KeyedSteer hook. Returns (texts, new token
    ids [n][256], used keys per text). mode='fixed' needs `vec` (a torch key vector, as core.generate's `key`)."""
    dev = core.device()
    if mode == "fixed":
        steer = KeyedSteer(model, "fixed", vec=vec.to(dev, model.dtype))
    else:
        if scale is None:
            scale = rho * N_REF if rho is not None else 0.0        # 'table' mode: the table's vectors are pre-scaled
        steer = KeyedSteer(model, mode, h=h, secret=secret, scale=scale, table=table)
    texts, ids_out, used = [], [], []
    try:
        for b0 in range(0, len(prompts), batch_size):
            batch = tok(prompts[b0:b0 + batch_size], return_tensors="pt", padding=True).to(dev)
            torch.manual_seed(seed * 1_000_003 + b0)
            with torch.no_grad():
                out = model.generate(**batch, pad_token_id=tok.pad_token_id, **core.GEN_KWARGS)
            new = out[:, batch["input_ids"].shape[1]:]
            assert new.shape[1] == T_MAX, new.shape
            texts += tok.batch_decode(new, skip_special_tokens=True)
            ids_out += new.cpu().tolist()
            used += [list(u) for u in steer.used]
            torch.mps.empty_cache()
    finally:
        steer.remove()
    return texts, ids_out, used


# ---------------------------------------------------------------- per-position features
def position_grads(tok, model, text):
    """([T, D] float32, ids [T]): the gradient of the continuation log-likelihood with respect to an additive vector at
    every content position of layer LAYER (one backward pass), and the detector's token ids of the text."""
    dev = core.device()
    enc = core._encode(tok, [text]).to(dev)
    cm = enc.pop("content_mask")
    L = enc["input_ids"].shape[1]
    b = torch.zeros(1, L, D, device=dev, dtype=torch.float32, requires_grad=True)
    hd = model.model.layers[LAYER].register_forward_hook(PP._hook(b))
    try:
        PP._loglik(model, enc, cm).backward()
    finally:
        hd.remove()
    m = cm[0].bool().cpu().numpy()
    g = b.grad[0].detach().float().cpu().numpy()[m].astype(np.float32)
    ids = enc["input_ids"][0].cpu().numpy()[m].astype(np.int64)
    model.zero_grad(set_to_none=True)
    torch.mps.empty_cache()
    return g, ids


class PosStats:
    """Running per-dimension mean and sd over positions (Welford), for standardisation references."""

    def __init__(self):
        self.n, self.mean, self.m2 = 0, np.zeros(D), np.zeros(D)

    def add(self, G):
        for x in np.asarray(G, dtype=np.float64):
            self.n += 1
            d = x - self.mean
            self.mean += d / self.n
            self.m2 += d * (x - self.mean)

    def ref(self):
        sd = np.sqrt(self.m2 / max(self.n - 1, 1))
        return {"mu": self.mean.copy(), "sd": np.maximum(sd, 1e-12), "n_positions": self.n}


def standardise(G, ref):
    return (np.asarray(G, dtype=np.float64) - ref["mu"]) / ref["sd"]


# ---------------------------------------------------------------- the owner's keyed exact test
class KeyedOwner:
    def __init__(self, ref):
        self.ref = ref
        self.secrets_null = null_secrets()
        self.nm = PP.null_matrix()                 # the fixed scheme's 999 public null keys (unit)

    def stats(self, X, pos, ctx, secrets):
        """S(x, m) for every secret in `secrets` (uint64 [M]): [M]."""
        if len(pos) == 0:
            return np.zeros(len(secrets))
        idx, w = keys_from_hash(context_hash(secrets, ctx))       # [M, P, K]
        Xp = X[pos]                                               # [P, D]
        sel = Xp[np.arange(len(pos))[None, :, None], idx]         # [M, P, K]
        return (sel * w).sum((1, 2))

    def pvalue(self, G, ids, h, secret):
        X = standardise(G, self.ref)
        if h == 0:
            raise ValueError("use pvalue_fixed for h = 0")
        pos, ctx = contexts(ids, h)
        if len(pos) == 0:
            return 1.0, 0.0, 0
        s_true = self.stats(X, pos, ctx, np.asarray([secret], dtype=np.uint64))[0]
        s_null = self.stats(X, pos, ctx, self.secrets_null)
        return float((1 + (s_null >= s_true).sum()) / (1 + M_NULL)), float(s_true), int(len(pos))

    def pvalue_fixed(self, G, vdir):
        """The per-position form with one key at every position: S = sum_t <x_t, v>; nulls = the public null keys."""
        X = standardise(G, self.ref)
        xs = X.sum(0)
        s_true = float(xs @ vdir)
        s_null = xs @ self.nm.T
        return float((1 + (s_null >= s_true).sum()) / (1 + M_NULL)), s_true, int(len(X))


# ---------------------------------------------------------------- the per-context attacker (Route A'-h)
class ContextAttacker:
    def __init__(self, ref, h, c_min, scale):
        self.ref, self.h, self.c_min, self.scale = ref, h, int(c_min), float(scale)
        self.count, self.sum = {}, {}

    def eligible_from_ids(self, ids_list):
        """Two-pass: contexts seen at least c_min times across the observed texts (token ids only)."""
        cnt = {}
        for ids in ids_list:
            _, ctx = contexts(ids, self.h)
            for c in map(tuple, ctx.tolist()):
                cnt[c] = cnt.get(c, 0) + 1
        self.eligible = {c for c, n in cnt.items() if n >= self.c_min}
        self.all_counts = cnt
        return self.eligible

    def observe(self, G, ids):
        X = standardise(G, self.ref)
        pos, ctx = contexts(ids, self.h)
        for p, c in zip(pos, map(tuple, ctx.tolist())):
            if c in self.eligible:
                self.count[c] = self.count.get(c, 0) + 1
                self.sum[c] = self.sum.get(c, 0.0) + X[p]

    def estimates(self):
        """context -> (unit 4-sparse estimate [D] float32, count), for contexts with count >= c_min so far."""
        out = {}
        for c, n in self.count.items():
            if n < self.c_min:
                continue
            mean = self.sum[c] / n
            sup = np.argsort(-np.abs(mean))[:K]
            v = np.zeros(D, dtype=np.float32)
            v[sup] = mean[sup]
            out[c] = (v / np.linalg.norm(v).clip(1e-12), n)
        return out

    def table(self):
        """The forgery hook's table: context -> scaled dense vector."""
        return {c: (v * self.scale).astype(np.float32) for c, (v, n) in self.estimates().items()}

    def score(self, secret):
        """Count-weighted and plain mean cosine of the estimates with the true keys; the number of contexts."""
        est = self.estimates()
        if not est:
            return {"n_contexts": 0, "cos_weighted": 0.0, "cos_mean": 0.0}
        ctx = np.asarray(list(est.keys()), dtype=np.int64).reshape(len(est), self.h)
        V = dense_keys(secret, ctx)
        cs = np.array([float(est[c][0] @ V[i]) for i, c in enumerate(est)])
        ns = np.array([est[c][1] for c in est], dtype=np.float64)
        return {"n_contexts": len(est), "cos_weighted": float((cs * ns).sum() / ns.sum()), "cos_mean": float(cs.mean()),
                "cos_by_count": {str(lo): float(np.mean(cs[(ns >= lo) & (ns < hi)])) if ((ns >= lo) & (ns < hi)).any() else None
                                 for lo, hi in ((self.c_min, 32), (32, 128), (128, 512), (512, 10**9))}}

    def coverage(self, ids_list):
        """Share of scored positions of the given texts whose context has an estimate."""
        est = self.estimates()
        tot, cov = 0, 0
        for ids in ids_list:
            _, ctx = contexts(ids, self.h)
            for c in map(tuple, ctx.tolist()):
                tot += 1
                cov += c in est
        return float(cov / tot) if tot else 0.0


# ---------------------------------------------------------------- rotation: the union test and the clustering attacker
def union_pvalues(X, keys_unit, nm_big):
    """X: [n, D] unit standardised summed-gradient vectors (S4's transform); keys_unit: [Kk, D]; nm_big: [>= 999*Kk, D]
    public null keys. U = max_k <x, v_k>; null U_j over 999 disjoint groups of Kk null keys. Returns p [n], U [n]."""
    Kk = keys_unit.shape[0]
    U = (X @ keys_unit.T).max(1)
    groups = nm_big[:M_NULL * Kk].reshape(M_NULL, Kk, -1)
    Un = np.stack([(X @ groups[j].T).max(1) for j in range(M_NULL)], 1)   # [n, 999]
    return (1 + (Un >= U[:, None]).sum(1)) / (1 + M_NULL), U


def cosine_kmeans(X, Kk, seed, n_init=20, iters=50):
    """Spherical k-means on unit rows of X [n, D]; returns labels [n] of the best of n_init runs (max total cosine)."""
    rng = np.random.default_rng(seed)
    Xu = PP.unit(np.asarray(X, dtype=np.float64))
    best, best_lab = -np.inf, None
    for _ in range(n_init):
        C = Xu[rng.choice(len(Xu), Kk, replace=False)]
        for _ in range(iters):
            lab = (Xu @ C.T).argmax(1)
            C2_ = np.stack([Xu[lab == k].mean(0) if (lab == k).any() else Xu[rng.integers(len(Xu))] for k in range(Kk)])
            C2_ = PP.unit(C2_)
            if np.allclose(C2_, C):
                break
            C = C2_
        tot = float((Xu @ C.T).max(1).sum())
        if tot > best:
            best, best_lab = tot, (Xu @ C.T).argmax(1)
    return best_lab


def route_a_prime_fixed(obs_G, ref_G, rho):
    """Route A' at a known layer: Study 1's Route A rule on summed gradients [n, D] vs reference [m, D]."""
    la, va, _ = attack2.route_a(obs_G[:, None, :], ref_G[:, None, :], K, rho, np.ones(1))
    return PP.unit(va.astype(np.float64))
