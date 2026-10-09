"""Study 1 v0.2 shared machinery (STUDY1_PROTOCOL_v0.2.md): configuration, pools, keys, memory-safe features.

Reuses research/study1/core.py (v0.1, locked, unchanged) for the model, hooks, key generation and generation.
Feature passes run the decoder body only (no vocabulary-sized logits; see the 2026-09-25 memory fix).
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "study1"))
import core  # noqa: E402  (v0.1, unchanged)

core.configure("qwen")
ROOT = core.ROOT
LAYER = core.LAYER                      # 14
N_LAYERS = 28
D_MODEL = 1536
K_SUPPORT = core.n_support(D_MODEL)     # 4
N_REF = 56.90270233154297               # pilot median unsteered norm at layer 14 (outputs/repro_v0.1/results_qwen.json)
LEVELS = [0.25, 0.35, 0.50, 0.70]
STUDY_KEYS = list(range(1001, 1009))    # 8 keys, never used before v0.2
CONTROL_KEYS = list(range(5001, 5009))  # one random-control key per study key
N_GRID = [1, 4, 16, 64, 256, 1024]
FORGE_N = [64, 256, 1024]
N_FORGE_TEXTS = 100
FPR = 0.01
PILOT_RESULTS = ROOT / "research" / "outputs" / "repro_v0.1" / "results_qwen.json"


def key(seed, rho):
    """Self-Recognition sparse key (support and values from core.make_key), rescaled to norm rho * N_REF."""
    v = core.make_key(seed, D_MODEL, 1.0)
    return v * (rho * N_REF / v.norm())


# ---------------------------------------------------------------- pools
def pools():
    """v0.1 pools (same rank rule), D cut to its first 100, A split into A1/A2, and a new pool F (next 200 by rank)."""
    base = core.assign_pools()
    units = core.load_prompts("c4", "dev")
    ranked = sorted(units, key=lambda u: hashlib.sha256((u["id"] + "|study1").encode()).hexdigest())
    used = sum(core.POOL_SIZES.values())
    p = {"A1": base["A"][:500], "A2": base["A"][500:], "B": base["B"], "C": base["C"], "D": base["D"][:100],
         "E": base["E"], "F": ranked[used:used + 200]}
    ids = [u["id"] for q in p.values() for u in q]
    assert len(ids) == len(set(ids)), "pools not disjoint"
    assert len(p["F"]) == 200 and len(p["A1"]) == len(p["A2"]) == 500 and len(p["B"]) == 1024 and len(p["C"]) == 2000
    assert not ({u["id"] for u in p["F"]} & {u["id"] for u in base["T"]}), "F overlaps tuning pool"
    assert all(int(i[:8], 16) % 100 >= 20 for i in ids), "holdout id in a pool"
    return p


def prompts(pool):
    return [u["prompt"] for u in pool]


# ---------------------------------------------------------------- features (decoder body only)
def _batches(tok, texts, bs):
    for b0 in range(0, len(texts), bs):
        enc = core._encode(tok, texts[b0:b0 + bs])
        cm = enc.pop("content_mask")
        yield b0, enc, cm


def layer_tokens(tok, model, texts, bs=16):
    """[n, 256, d] float16 raw activations at LAYER for content tokens (zeros beyond length), and lengths."""
    dev = core.device()
    X = np.zeros((len(texts), core.NEW_TOKENS, D_MODEL), dtype=np.float16)
    lens = np.zeros(len(texts), dtype=np.int64)
    for b0, enc, cm in _batches(tok, texts, bs):
        with torch.no_grad():
            h = model.model(**enc.to(dev), output_hidden_states=True).hidden_states[LAYER + 1].float().cpu().numpy()
        for j in range(h.shape[0]):
            idx = np.flatnonzero(cm[j].numpy())
            X[b0 + j, :len(idx)] = h[j, idx]
            lens[b0 + j] = len(idx)
        torch.mps.empty_cache()
    return X, lens


def all_layer_means(tok, model, texts, bs=16, want_norms=False):
    """Per text and layer: mean over content tokens of h_t/||h_t|| (float16 [n, 28, d]); optionally the per-layer
    token norms (for the attacker's own strength scale, protocol §6)."""
    dev = core.device()
    out, norms = [], [[] for _ in range(N_LAYERS)]
    for _, enc, cm in _batches(tok, texts, bs):
        with torch.no_grad():
            hs = model.model(**enc.to(dev), output_hidden_states=True).hidden_states[1:]
        m = cm.to(dev).unsqueeze(-1).float()
        per = []
        for li, h in enumerate(hs):
            h = h.float()
            nrm = h.norm(dim=-1, keepdim=True)
            per.append(((h / nrm.clamp_min(1e-6)) * m).sum(1) / m.sum(1))
            if want_norms:
                norms[li].append(nrm[..., 0][cm.to(dev).bool()].cpu().numpy())
        out.append(torch.stack(per, 1).cpu().to(torch.float16).numpy())
        torch.mps.empty_cache()
    feats = np.concatenate(out, 0)
    if want_norms:
        return feats, np.array([float(np.median(np.concatenate(n))) for n in norms])
    return feats


def perplexities(tok, model, prompt_list, texts):
    """Median-able per-text perplexity of the continuation under the unsteered model, prompt as context; the LM head is
    applied only to continuation positions (memory-safe)."""
    dev, out = core.device(), []
    for p, c in zip(prompt_list, texts):
        pi = tok(p, add_special_tokens=False)["input_ids"]
        ci = tok(c, add_special_tokens=False)["input_ids"][:core.NEW_TOKENS]
        ids = torch.tensor([pi + ci], device=dev)
        with torch.no_grad():
            h = model.model(input_ids=ids).last_hidden_state[0, len(pi) - 1:len(pi) - 1 + len(ci)]
            lg = model.lm_head(h).float()
            out.append(float(torch.exp(torch.nn.functional.cross_entropy(lg, ids[0, len(pi):]))))
        torch.mps.empty_cache()
    return out
