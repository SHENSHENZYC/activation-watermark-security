"""Attacker-side estimators for Study 1 v0.2 (protocol §6). Receives ONLY feature arrays computed from texts, the
attacker's own per-layer norm scale, and public parameters (k, rho). Never the key, the layer, the probe or its threshold.

Route A (key recovery) is v0.1's E-sparse estimator (study1/attack.py, unchanged, supplies the z-scores); only the
rescaling differs: rho times the attacker's own median token norm at the chosen layer.
"""
import numpy as np

from attack import zscores  # study1/attack.py (v0.1, locked; numpy only)


def _scale(v, norm):
    return (v / np.linalg.norm(v).clip(1e-12) * norm).astype(np.float32)


def route_a(obs, ref, k, rho, ref_norms):
    """obs [n, L, d], ref [m, L, d]; ref_norms [L] (attacker's median token norms). Returns (layer, v_hat, profile)."""
    delta, z = zscores(obs, ref)
    absz = np.abs(z)
    lh = int(absz.max(1).argmax())
    support = np.argsort(-absz[lh])[:k]
    v = np.zeros(delta.shape[1])
    v[support] = delta[lh][support]
    return lh, _scale(v, rho * ref_norms[lh]), absz.max(1)


def route_b(obs, ref, rho, ref_norms):
    """Footprint imitation: dense mean shift at the layer with the largest z-vector norm."""
    delta, z = zscores(obs, ref)
    prof = np.linalg.norm(z, axis=1)
    lh = int(prof.argmax())
    return lh, _scale(delta[lh].copy(), rho * ref_norms[lh]), prof
