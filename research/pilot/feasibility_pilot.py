"""Stage 3 feasibility pilot (input validation and timing only).

Measures, on this machine, the cost of the three operations the planned study needs:
  1. steered generation (a Self-Recognition-style sparse vector added to one decoder layer's output),
  2. re-encoding forward pass with hidden states,
  3. one backward pass giving the gradient of the text log-likelihood w.r.t. an additive vector at the steered layer
     (the quantity a GaussMark-style score test would use).
It also checks the hook mechanics (steering changes logits; removal restores them; gradient finite).

It deliberately computes NO detection statistic, NO key-recovery estimate and NO attack: those need a locked protocol.
Prompts are hand-written placeholders, not drawn from any dataset (so no holdout exposure).

Run: .venv/bin/python research/pilot/feasibility_pilot.py
"""
import json
import platform
import time
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-1.5B"
REVISION = "8faed761d45a263340a0528343f099c05c9a4323"
LAYER = 14  # middle of 28 layers, matching Self-Recognition's mid-layer choice
SPARSITY = 0.003  # Self-Recognition default "sparse_0.003"
ALPHA = 5.0  # Self-Recognition default noise_max
NEW_TOKENS = 256
SEED = 0
OUT = Path(__file__).parent / "outputs" / "feasibility_pilot_v0.1.json"

PROMPTS = [
    "The history of the printing press shows that",
    "In a small town near the coast, the local council decided to",
    "Researchers studying sleep have long wondered why",
    "The simplest way to explain how a bicycle stays upright is",
    "When the train finally arrived at the station, the passengers",
    "A good recipe for bread starts with",
    "The committee's report on public transport concluded that",
    "Learning a second language as an adult is difficult because",
]


def sync(device):
    if device.type == "mps":
        torch.mps.synchronize()


def make_key(dim, gen):
    """Sparse key in the style of Self-Recognition's generate_noise: uniform[-1,1] on a random support, times ALPHA."""
    k = max(1, int(SPARSITY * dim))
    idx = torch.randperm(dim, generator=gen)[:k]
    v = torch.zeros(dim)
    v[idx] = 2 * torch.rand(k, generator=gen) - 1
    return v * ALPHA


class AddVector:
    """Forward hook adding `vec` to every position of a decoder layer's output hidden states."""

    def __init__(self, vec):
        self.vec = vec

    def __call__(self, module, inputs, output):
        if isinstance(output, tuple):
            return (output[0] + self.vec,) + tuple(output[1:])
        return output + self.vec


def main():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    gen = torch.Generator().manual_seed(SEED)
    record = {
        "purpose": "feasibility pilot: timing and hook validation only; no detection/attack statistics",
        "model_id": MODEL_ID, "revision": REVISION, "layer": LAYER, "sparsity": SPARSITY, "alpha": ALPHA,
        "new_tokens": NEW_TOKENS, "device": device.type, "torch": torch.__version__,
        "transformers": transformers.__version__, "platform": platform.platform(), "python": platform.python_version(),
    }

    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    tok.padding_side = "left"
    dtype = torch.bfloat16
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=REVISION, dtype=dtype).to(device).eval()
    sync(device)
    record["load_seconds"] = round(time.perf_counter() - t0, 2)
    record["dtype"] = str(dtype)
    layers = model.model.layers
    record["n_layers"] = len(layers)
    dim = model.config.hidden_size
    record["hidden_size"] = dim
    key = make_key(dim, gen).to(device, dtype)
    record["key_nonzero"] = int((key != 0).sum())

    # --- Check 1: hook mechanics on a single forward pass ---
    enc = tok(PROMPTS[0], return_tensors="pt").to(device)
    with torch.no_grad():
        base = model(**enc).logits.float()
        h = layers[LAYER].register_forward_hook(AddVector(key))
        steered = model(**enc).logits.float()
        h.remove()
        restored = model(**enc).logits.float()
    record["check_hook_changes_logits"] = bool((steered - base).abs().max().item() > 1e-3)
    record["check_hook_removal_restores"] = bool((restored - base).abs().max().item() < 1e-4)

    # --- Timing 2: steered generation, batch 1 and batch 8 ---
    gen_kwargs = dict(max_new_tokens=NEW_TOKENS, min_new_tokens=NEW_TOKENS, do_sample=True, temperature=0.7,
                      top_p=0.9, top_k=50, repetition_penalty=1.1, pad_token_id=tok.eos_token_id)
    timings = {}
    texts = []
    h = layers[LAYER].register_forward_hook(AddVector(key))
    for bs in (1, 8):
        batch = tok(PROMPTS[:bs], return_tensors="pt", padding=True).to(device)
        torch.manual_seed(SEED)
        sync(device)
        t = time.perf_counter()
        with torch.no_grad():
            out = model.generate(**batch, **gen_kwargs)
        sync(device)
        dt = time.perf_counter() - t
        n_new = out.shape[1] - batch["input_ids"].shape[1]
        timings[f"generate_bs{bs}_seconds"] = round(dt, 2)
        timings[f"generate_bs{bs}_seconds_per_text"] = round(dt / bs, 3)
        timings[f"generate_bs{bs}_new_tokens"] = int(n_new)
        if bs == 8:
            texts = tok.batch_decode(out, skip_special_tokens=True)
    h.remove()

    # --- Timing 3: re-encoding forward with hidden states (no steering), one text at a time ---
    fw = []
    for text in texts:
        e = tok(text, return_tensors="pt").to(device)
        sync(device)
        t = time.perf_counter()
        with torch.no_grad():
            o = model(**e, output_hidden_states=True)
            _ = o.hidden_states[LAYER + 1][0].float().cpu()  # output of decoder layer LAYER
        sync(device)
        fw.append(time.perf_counter() - t)
    timings["reencode_seconds_per_text"] = round(sum(fw) / len(fw), 3)

    # --- Timing 4: backward pass, gradient of log-likelihood w.r.t. an additive vector at LAYER ---
    bw, grad_ok = [], True
    for text in texts:
        e = tok(text, return_tensors="pt").to(device)
        b = torch.zeros(dim, device=device, dtype=torch.float32, requires_grad=True)
        hook = layers[LAYER].register_forward_hook(AddVector(b.to(dtype)))
        sync(device)
        t = time.perf_counter()
        logits = model(**e).logits[0, :-1].float()
        logp = torch.log_softmax(logits, -1).gather(1, e["input_ids"][0, 1:, None]).sum()
        logp.backward()
        sync(device)
        bw.append(time.perf_counter() - t)
        hook.remove()
        grad_ok &= bool(torch.isfinite(b.grad).all().item()) and b.grad.abs().sum().item() > 0
        model.zero_grad(set_to_none=True)
    timings["backward_seconds_per_text"] = round(sum(bw) / len(bw), 3)
    record["check_gradient_finite_nonzero"] = grad_ok
    record["timings"] = timings

    # --- Projection for the proceed rule: ~5,000 texts generated (batched) + re-encoded + one backward each ---
    per_text = timings["generate_bs8_seconds_per_text"] + timings["reencode_seconds_per_text"] + timings[
        "backward_seconds_per_text"]
    record["projected_hours_5000_texts"] = round(5000 * per_text / 3600, 2)
    record["proceed_rule"] = "PASS if projected_hours_5000_texts <= 168 (about one week of machine time) and all checks true"
    checks = [record["check_hook_changes_logits"], record["check_hook_removal_restores"], grad_ok]
    record["proceed_rule_result"] = "PASS" if all(checks) and record["projected_hours_5000_texts"] <= 168 else "FAIL"
    record["sample_output_chars"] = len(texts[0]) if texts else 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
