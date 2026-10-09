"""Shared settings and helpers for Study 1 v0.4 (STUDY1_PROTOCOL_v0.4.md).

v0.3 and v0.2 are reused read-only through their own modules (research/study1_v03/common3.py, attack3.py;
research/study1_v02/common.py, detect2.py) and their data folders.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "study1_v03"))

import numpy as np  # noqa: E402

import common3 as C3  # noqa: E402  (v0.3; puts v0.2 and v0.1 on sys.path)
from common3 import C2, core  # noqa: E402,F401
from attack4 import seqrep4_ids  # noqa: E402

V02_DATA = C3.V02_DATA
V03_DATA = C3.HERE / "data"
LEVELS = list(C3.LEVELS)       # 0.35, 0.50, 0.70
FORGE_N = list(C3.FORGE_N)     # 64, 256
ROUTES = C3.ROUTES
N_CAND = C3.N_CAND             # 5 candidate layers (protocol §4.1)
N_TRIAL = C3.N_TRIAL           # 16 trial texts per candidate (§4.3)
TOL = C3.TOL                   # 1.2 x observed median continuation-only perplexity (§4.4)
OBS_REP_Q = 0.95               # attacker: a trial is repetitive if seq-rep-4 > this quantile of the observed texts (§4.2)
MAX_REP_TRIALS = 2             # attacker: at most 2 repetitive trials in 16 (§4.4)
FLUENT_Q = C3.FLUENT_Q         # evaluation: both bars at the key-level oracle's 95th percentile (§5)
N_FORGE = C3.N_FORGE           # 100
SEED_TRIAL = 60                # trials: base + 60 (§4)
SEED_FORGE = 70                # forgeries: base + 70 + 3 * route index + n index (§4)

tag, seed_base, ppl_cont_only = C3.tag, C3.seed_base, C3.ppl_cont_only


def seqrep4(tok, texts):
    """seq-rep-4 of each text's continuation: its first 256 model tokens, as for perplexity (protocol §4)."""
    return [seqrep4_ids(tok(c, add_special_tokens=False)["input_ids"][:core.NEW_TOKENS]) for c in texts]


def rep3(t):
    """v0.3's exploratory word rep3 (study1_report_v03/exploratory_repetition.py), for the §8 continuity secondary."""
    w = t.lower().split()
    g = list(zip(w, w[1:], w[2:]))
    return 1 - len(set(g)) / len(g) if g else 0.0


def cut(oracle_values):
    """Evaluation bar for one key-level: the 95th percentile of its oracle texts' values (§5)."""
    return float(np.quantile(np.asarray(oracle_values, dtype=np.float64), FLUENT_Q))


def fluent_accept(scores, ppl, rep, thr, ppl_cut, rep_cut):
    """Per text: 1 if accepted by the owner's detector AND perplexity <= ppl_cut AND repetition <= rep_cut (§5).
    rep_cut = inf switches the repetition term off (v0.3's definition; used by the reproduction check)."""
    ok = (np.asarray(scores) > thr) & (np.asarray(ppl, dtype=np.float64) <= ppl_cut)
    return (ok & (np.asarray(rep, dtype=np.float64) <= rep_cut)).astype(float)
