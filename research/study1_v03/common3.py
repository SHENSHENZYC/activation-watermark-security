"""Shared settings and helpers for Study 1 v0.3 (STUDY1_PROTOCOL_v0.3.md).

v0.2 is reused read-only through its own modules (research/study1_v02/common.py, detect2.py) and its data folder.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "study1_v02"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

import common as C2  # noqa: E402  (v0.2; puts research/study1 on sys.path)
from common import core  # noqa: E402,F401

V02_DATA = C2.HERE / "data"
LEVELS = [0.35, 0.50, 0.70]   # the levels that passed v0.2's L1
FORGE_N = [64, 256]
ROUTES = "AB"
N_CAND = 5                    # candidate layers per attack (protocol §4.1)
N_TRIAL = 16                  # trial texts per candidate (§4.3)
TOL = 1.2                     # attacker's tolerance on continuation-only perplexity (§4.4)
FLUENT_Q = 0.95               # evaluation: fluent if ppl <= this quantile of the key-level's oracle texts (§5)
N_FORGE = 100


def tag(s, rho):
    return f"k{s}_r{int(round(rho * 100)):03d}"


def seed_base(s, rho):
    """Same base as v0.2 (level index in v0.2's LEVELS), so v0.3 seeds sit in v0.2's per-key-level seed block."""
    return s * 1000 + C2.LEVELS.index(rho) * 100


def ppl_cont_only(tok, model, texts):
    """Continuation-only perplexity (protocol §2): each text scored given only <|endoftext|> as context, as an attacker
    who never sees the prompts must score both observed and trial texts. The LM head is applied only to scored
    positions (memory-safe)."""
    dev, out = core.device(), []
    for c in texts:
        ci = tok(c, add_special_tokens=False)["input_ids"][:core.NEW_TOKENS]
        if not ci:
            out.append(float("nan"))
            continue
        ids = torch.tensor([[tok.eos_token_id] + ci], device=dev)
        with torch.no_grad():
            h = model.model(input_ids=ids).last_hidden_state[0, :len(ci)]
            lg = model.lm_head(h).float()
            out.append(float(torch.exp(torch.nn.functional.cross_entropy(lg, ids[0, 1:]))))
        torch.mps.empty_cache()
    return out


def fluent_cut(oracle_ppl):
    """Evaluation fluency bar for one key-level: the 95th percentile of its oracle texts' perplexities (§5)."""
    return float(np.quantile(np.asarray(oracle_ppl, dtype=np.float64), FLUENT_Q))


def fluent_accept(scores, ppl, thr, cut):
    """Per text: 1 if accepted by the owner's detector AND fluent, else 0 (§5)."""
    return ((np.asarray(scores) > thr) & (np.asarray(ppl, dtype=np.float64) <= cut)).astype(float)
