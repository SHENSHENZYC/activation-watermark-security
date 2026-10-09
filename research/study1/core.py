"""Shared machinery for Study 1: configuration, pools, keys, steering hooks, generation, re-encoding features, gradients.

Everything here is fixed by STUDY1_PROTOCOL_v0.1.md. The attack module (attack.py) must not import KEY functions for
study keys; it only receives feature arrays.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "stage4"))
from prompts import load_prompts  # noqa: E402  (holdout-sealed loader)

MODELS = {  # name: (repo, pinned revision, steered layer = middle, number of study keys)
    "qwen": ("Qwen/Qwen2.5-1.5B", "8faed761d45a263340a0528343f099c05c9a4323", 14, 16),
    "llama": ("meta-llama/Llama-3.2-1B", "4e20de362430cd3b72f300e6b0f18e50e7166e08", 8, 8),
}
MODEL_NAME = "qwen"
MODEL_ID, REVISION, LAYER, N_KEYS = MODELS[MODEL_NAME]
SPARSITY = 0.003
ALPHA_DEFAULT = 5.0
ALPHA_RETRY = 10.0
NEW_TOKENS = 256
GEN_KWARGS = dict(do_sample=True, temperature=0.7, top_p=0.9, top_k=50, repetition_penalty=1.1,
                  max_new_tokens=NEW_TOKENS, min_new_tokens=NEW_TOKENS)
ALL_STUDY_KEY_SEEDS = list(range(1001, 1017))  # 16 keys (the first N_KEYS are used for a model)
STUDY_KEY_SEEDS = ALL_STUDY_KEY_SEEDS[:N_KEYS]
TUNING_KEY_SEEDS = list(range(9001, 9005))  # 4 keys
RANDOM_CONTROL_SEEDS = list(range(5001, 5017))  # one control key per study key
NULL_KEY_SEED = 777
N_NULL_KEYS = 999
VALIDATION_KEY_SEED = 0  # used only by validate_inputs.py (never a study, tuning or control key)
N_GRID = [1, 4, 16, 64, 256, 1024]
SPOOF_N = [16, 64, 256, 1024]
POOL_SIZES = {"A": 1000, "B": 1024, "C": 2000, "D": 200, "E": 200, "T": 400}
POOL_ORDER = ["A", "B", "C", "D", "E", "T"]


def configure(name):
    """Select the model configuration (protocol §4 and §7): sets MODEL_ID, REVISION, LAYER, STUDY_KEY_SEEDS."""
    global MODEL_NAME, MODEL_ID, REVISION, LAYER, N_KEYS, STUDY_KEY_SEEDS
    MODEL_NAME = name
    MODEL_ID, REVISION, LAYER, N_KEYS = MODELS[name]
    STUDY_KEY_SEEDS = ALL_STUDY_KEY_SEEDS[:N_KEYS]


# ---------------------------------------------------------------- pools
def assign_pools():
    """Deterministic, disjoint pools from the C4 dev split, by rank of sha256(id|study1)."""
    units = load_prompts("c4", "dev")
    ranked = sorted(units, key=lambda u: hashlib.sha256((u["id"] + "|study1").encode()).hexdigest())
    pools, start = {}, 0
    for p in POOL_ORDER:
        pools[p] = ranked[start:start + POOL_SIZES[p]]
        start += POOL_SIZES[p]
    ids = [u["id"] for p in POOL_ORDER for u in pools[p]]
    assert len(ids) == len(set(ids)) == sum(POOL_SIZES.values()), "pools not disjoint"
    assert all(int(i[:8], 16) % 100 >= 20 for i in ids), "holdout id in a pool"
    return pools


# ---------------------------------------------------------------- keys
def n_support(dim):
    return max(1, int(SPARSITY * dim))


def make_key(seed, dim, alpha):
    """Self-Recognition-style key: random support of size k, uniform[-1,1] values, times alpha (float32, CPU)."""
    g = torch.Generator().manual_seed(seed)
    k = n_support(dim)
    idx = torch.randperm(dim, generator=g)[:k]
    v = torch.zeros(dim)
    v[idx] = 2 * torch.rand(k, generator=g) - 1
    return v * alpha


def null_keys(dim, alpha):
    """M = 999 keys from the public key distribution, used for exact key-resampling p-values."""
    return torch.stack([make_key(NULL_KEY_SEED * 100000 + j, dim, alpha) for j in range(N_NULL_KEYS)])


# ---------------------------------------------------------------- model and hooks
def device():
    return torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def load_model(model_id=None, revision=None):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    model_id, revision = model_id or MODEL_ID, revision or REVISION
    tok = AutoTokenizer.from_pretrained(model_id, revision=revision)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=revision, dtype=torch.bfloat16).to(device()).eval()
    return tok, model


class AddVector:
    """Forward hook adding a vector (shape [d] or [B,1,d]) to every position of a decoder layer's output."""

    def __init__(self, vec):
        self.vec = vec

    def __call__(self, module, inputs, output):
        if isinstance(output, tuple):
            return (output[0] + self.vec,) + tuple(output[1:])
        return output + self.vec


def generate(tok, model, prompts, key=None, layer=None, seed=0, batch_size=16):
    """Generate exactly NEW_TOKENS continuation tokens per prompt, optionally steered by `key` at `layer`.

    Returns the decoded continuations (prompt excluded)."""
    dev = device()
    layer = LAYER if layer is None else layer
    hook = None
    if key is not None:
        hook = model.model.layers[layer].register_forward_hook(AddVector(key.to(dev, model.dtype)))
    out_texts = []
    try:
        for b0 in range(0, len(prompts), batch_size):
            batch = tok(prompts[b0:b0 + batch_size], return_tensors="pt", padding=True).to(dev)
            torch.manual_seed(seed * 1_000_003 + b0)
            with torch.no_grad():
                out = model.generate(**batch, pad_token_id=tok.pad_token_id, **GEN_KWARGS)
            new = out[:, batch["input_ids"].shape[1]:]
            assert new.shape[1] == NEW_TOKENS, new.shape
            out_texts += tok.batch_decode(new, skip_special_tokens=True)
    finally:
        if hook is not None:
            hook.remove()
    return out_texts


def _encode(tok, texts):
    """Right-padded encoding of continuation texts, truncated to NEW_TOKENS content tokens. A BOS token is kept if the
    tokenizer adds one (Llama), because models expect it; `content_mask` excludes BOS and padding from averages."""
    has_bos = tok.bos_token_id is not None and tok("a")["input_ids"][0] == tok.bos_token_id
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=NEW_TOKENS + int(has_bos),
              add_special_tokens=True, padding_side="right")
    cm = enc["attention_mask"].clone()
    if has_bos:
        cm[:, 0] = 0
    enc["content_mask"] = cm
    return enc


def reencode_features(tok, model, texts, batch_size=16):
    """Per text and layer: mean over tokens of h_t/||h_t|| (the output of decoder layer l = hidden_states[l+1]).

    Returns float16 array [n_texts, n_layers, d]. D-cos for any key v at layer l equals <feat[l], v>/||v||."""
    dev = device()
    feats = []
    for b0 in range(0, len(texts), batch_size):
        enc = _encode(tok, texts[b0:b0 + batch_size]).to(dev)
        cm = enc.pop("content_mask")
        with torch.no_grad():
            hs = model(**enc, output_hidden_states=True).hidden_states[1:]  # one per decoder layer
        m = cm.unsqueeze(-1).float()
        per_layer = []
        for h in hs:
            h = h.float()
            hn = h / h.norm(dim=-1, keepdim=True).clamp_min(1e-6)
            per_layer.append(((hn * m).sum(1) / m.sum(1)).cpu())
        feats.append(torch.stack(per_layer, 1).to(torch.float16).numpy())
    return np.concatenate(feats, 0)


def score_gradients(tok, model, texts, layer=None, batch_size=1):
    """Per text: gradient of the continuation log-likelihood w.r.t. an additive vector at `layer` (float32 [n, d])."""
    dev = device()
    layer = LAYER if layer is None else layer
    d = model.config.hidden_size
    grads = []
    for b0 in range(0, len(texts), batch_size):
        enc = _encode(tok, texts[b0:b0 + batch_size]).to(dev)
        cm = enc.pop("content_mask")
        B = enc["input_ids"].shape[0]
        b = torch.zeros(B, 1, d, device=dev, dtype=torch.float32, requires_grad=True)
        hook = model.model.layers[layer].register_forward_hook(AddVector(b.to(model.dtype)))
        try:
            logits = model(**enc).logits[:, :-1].float()
            tgt = enc["input_ids"][:, 1:]
            mask = cm[:, 1:].float()
            lp = torch.log_softmax(logits, -1).gather(2, tgt.unsqueeze(-1)).squeeze(-1)
            (lp * mask).sum().backward()  # per-example b gives per-example gradients
        finally:
            hook.remove()
        grads.append(b.grad[:, 0].detach().cpu().numpy())
        model.zero_grad(set_to_none=True)
    return np.concatenate(grads, 0)
