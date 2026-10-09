"""Attacker-side repetition screen and selection for Study 1 v0.4 (protocol §4). Receives ONLY token ids, perplexities
and seq-rep-4 values of texts the attacker observed or generated itself, and public parameters (tolerance, the
repetition quantile, the repetitive-trial allowance). Never the key, the layer, the probe, its threshold or any
evaluation prompt. The candidates themselves are v0.3's (attack3.candidates, unchanged).
"""
import numpy as np


def seqrep4_ids(ids):
    """seq-rep-4 (Welleck et al., 2019): 1 - distinct 4-grams / all 4-grams of a token list; 0 if fewer than 4 tokens."""
    g = [tuple(ids[i:i + 4]) for i in range(len(ids) - 3)]
    return 1.0 - len(set(g)) / len(g) if g else 0.0


def rep_threshold(obs_rep, q):
    """r_obs: the q-quantile of seq-rep-4 over the observed texts (§4.2)."""
    return float(np.quantile(np.asarray(obs_rep, dtype=np.float64), q))


def n_repetitive(trial_rep, r_obs):
    """m: the number of trial texts with seq-rep-4 > r_obs (§4.3)."""
    return int(np.sum(np.asarray(trial_rep, dtype=np.float64) > r_obs))


def select(cands, q_obs, q_trials, m_trials, tol, max_rep):
    """Keep candidates with trial median perplexity <= tol * q_obs AND at most max_rep repetitive trials; use the kept one
    with the largest profile. If none is kept, use the candidate with the fewest repetitive trials, ties broken by the
    smaller trial perplexity (then by candidate order). Returns (index, any_kept, kept_indices)."""
    q = np.asarray(q_trials, dtype=np.float64)
    kept = [i for i in range(len(cands)) if np.isfinite(q[i]) and q[i] <= tol * q_obs and m_trials[i] <= max_rep]
    if kept:
        return max(kept, key=lambda i: cands[i]["profile"]), True, kept
    qq = np.where(np.isfinite(q), q, np.inf)
    return min(range(len(cands)), key=lambda i: (m_trials[i], qq[i], i)), False, kept
