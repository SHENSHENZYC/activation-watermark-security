"""Defender-side detectors with exact key-resampling p-values (STUDY1_PROTOCOL_v0.1 §5).

Both statistics are linear in a per-text vector, so all 1 + M keys are scored with one matrix product:
  D-cos:   T(v) = <feat_l, v> / ||v||            (feat_l = mean over tokens of h_t/||h_t|| at layer l)
  D-score: S(v) = <g, v> / (||v|| ||g||)          (g = d log p(text) / d b at layer l)
p = (1 + #{j : stat(v_j) >= stat(v)}) / (1 + M). Under H0 (text independent of v) this p is exactly valid.
"""
import numpy as np


def _unit(keys):
    keys = np.asarray(keys, dtype=np.float64)
    return keys / np.linalg.norm(keys, axis=-1, keepdims=True)


def pvalues(vectors, key, null_keys):
    """vectors: [n, d] per-text statistic vectors; key: [d]; null_keys: [M, d]. Returns (stat, p) arrays of length n."""
    x = np.asarray(vectors, dtype=np.float64)
    s_true = x @ _unit(key)
    s_null = x @ _unit(null_keys).T  # [n, M]
    p = (1 + (s_null >= s_true[:, None]).sum(1)) / (1 + s_null.shape[1])
    return s_true, p


def dcos(feats_layer, key, null_keys):
    return pvalues(feats_layer, key, null_keys)


def dscore(grads, key, null_keys):
    g = np.asarray(grads, dtype=np.float64)
    g = g / np.linalg.norm(g, axis=1, keepdims=True).clip(1e-12)
    return pvalues(g, key, null_keys)


def accept_rate(p, level=0.01):
    return float((np.asarray(p) <= level).mean())
