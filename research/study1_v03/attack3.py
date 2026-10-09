"""Attacker-side candidate search for Study 1 v0.3 (protocol §4). Receives ONLY feature arrays, perplexities of texts the
attacker observed or generated itself, its own per-layer norm scale, and public parameters (k, rho, tolerance). Never the
key, the layer, the probe, its threshold or any evaluation prompt.

The profiles and per-layer estimates are v0.2's (attack2.py) evaluated at the top m layers instead of only the best one,
so the first candidate is exactly v0.2's choice (checked in validate_v03.py).
"""
import numpy as np

from attack import zscores  # study1/attack.py (v0.1, locked; numpy only)


def _scale(v, norm):
    return (v / np.linalg.norm(v).clip(1e-12) * norm).astype(np.float32)


def candidates(route, obs, ref, k, rho, ref_norms, m):
    """obs [n, L, d], ref [m_ref, L, d]; ref_norms [L]. Returns the m layers with the largest route profile, each with
    the route's estimate at that layer rescaled to rho * the attacker's median norm there, and the full profile."""
    delta, z = zscores(obs, ref)
    absz = np.abs(z)
    prof = absz.max(1) if route == "A" else np.linalg.norm(z, axis=1)
    out = []
    for lh in np.argsort(-prof, kind="stable")[:m]:
        lh = int(lh)
        if route == "A":
            v = np.zeros(delta.shape[1])
            sup = np.argsort(-absz[lh])[:k]
            v[sup] = delta[lh][sup]
        else:
            v = delta[lh].copy()
        out.append({"layer": lh, "profile": float(prof[lh]), "vec": _scale(v, rho * ref_norms[lh])})
    return out, prof


def select(cands, q_obs, q_trials, tol):
    """Keep candidates whose trial median perplexity is <= tol * q_obs; use the kept one with the largest profile.
    If none is kept, use the candidate with the smallest trial perplexity. Returns (index, any_kept, kept_indices)."""
    q = np.asarray(q_trials, dtype=np.float64)
    kept = [i for i in range(len(cands)) if np.isfinite(q[i]) and q[i] <= tol * q_obs]
    if kept:
        return max(kept, key=lambda i: cands[i]["profile"]), True, kept
    return int(np.nanargmin(q)), False, kept
