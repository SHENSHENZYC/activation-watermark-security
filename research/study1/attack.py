"""Attacker-side key estimation (STUDY1_PROTOCOL_v0.1 §5). Receives ONLY feature arrays computed from texts.

This module must never import or receive the true key or layer (checked by validate_inputs.py).
Public knowledge used: the scheme's default sparsity (k nonzero coordinates) and alpha (for the expected key norm).
"""
import numpy as np


def zscores(obs, ref):
    """obs: [n, L, d], ref: [m, L, d] (per-text mean normalised activations). Returns (delta, z) of shape [L, d].

    The standard error uses the reference-set variance for both groups: se = sd_ref * sqrt(1/n + 1/m),
    so the rule is defined for n = 1 as well (protocol v0.1, §5 clarification)."""
    obs = np.asarray(obs, dtype=np.float64)
    ref = np.asarray(ref, dtype=np.float64)
    n, m = obs.shape[0], ref.shape[0]
    delta = obs.mean(0) - ref.mean(0)
    sd = ref.std(0, ddof=1).clip(1e-8)
    return delta, delta / (sd * np.sqrt(1.0 / n + 1.0 / m))


def estimate(obs, ref, k, alpha, sparse=True):
    """Return (layer_hat, v_hat, z_profile). v_hat is rescaled to the expected key norm alpha*sqrt(k/3)."""
    delta, z = zscores(obs, ref)
    absz = np.abs(z)
    layer_hat = int(absz.max(1).argmax())
    d = delta[layer_hat]
    if sparse:
        support = np.argsort(-absz[layer_hat])[:k]
        v = np.zeros_like(d)
        v[support] = d[support]
    else:
        v = d.copy()
    v = v / np.linalg.norm(v).clip(1e-12) * alpha * np.sqrt(k / 3.0)
    return layer_hat, v.astype(np.float32), absz.max(1)
