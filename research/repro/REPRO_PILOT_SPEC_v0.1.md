# Reproduction pilot v0.1: can the Self-Recognition watermark be detected on our models?

**Status:** spec fixed before any pilot run (2026-09-25). This is **input validation for Study 1 v0.2**, not a study: tuning keys only, no claims.
**Why:** Study 1 v0.1 failed gate G1 (Qwen, D-cos TPR 0% at α = 5 and 10). Self-Recognition's public code (commit `7c26938`, MIT) detects with a **trained per-key MLP probe** on per-token activations, not with the training-free cosine that G1 used. See the decision log, 2026-09-25.
**Decided by:** Yichen (run the pilot); Claude (design).

## Scope and isolation
- **Keys:** the 4 tuning keys (seeds 9001–9004) only. Study keys (1001–1016), control keys and null keys are never used.
- **Prompts:** pool T of Study 1 (400 C4 dev prompts; key *i* uses prompts 100*i … 100*i+99, as in Study 1 phase A). No other pool; the holdout stays sealed.
- **Models:** Qwen2.5-1.5B (layer 14) and Llama-3.2-1B (layer 8), pinned as in Study 1.
- **Code:** reuses `research/study1/core.py` unchanged (keys, hook, generation, settings). Nothing locked is edited.
- **Steering strength:** α ∈ {5, 10, 20}. α = 5 is the paper's value; 10 and 20 show the dose response. The median activation norm at the layer is reported so α can be compared across models.

## Data
For each model, key and α: 100 steered texts. For each model and key: 100 **unsteered** texts on the same prompts with the same sampling seed (paired). Split by prompt with a fixed RNG (seed 0): 60 train, 20 validation, 20 test prompts per key, the same split for both classes.
Features: the per-token output of the steered layer (`hidden_states[l+1]`) for the 256 continuation tokens (BOS excluded), in two re-encoding variants: **cont** (the continuation alone, the Study 1 setting) and **prompt** (the prompt as context, continuation tokens kept; closer to the authors' `remove_prompt: False`).

## Detectors (per key, trained on that key's train split)
1. **MLP-faithful (primary):** the authors' `SimpleMLP` (d → 2048 → 64 → 64 → 32 → 2, ReLU, softmax output, cross-entropy on the softmax, Adam, lr 1e-3, batch 512, **1 epoch**), raw activations, one sample per token (as in `param.yaml`).
2. **MLP-strong:** the same network on standardised inputs, up to 10 epochs, epoch chosen on validation loss.
3. **Linear probe:** logistic regression on standardised per-token activations (Adam, up to 10 epochs, chosen on validation).
4. **Mass-mean:** the difference of class means of normalised token activations; score = mean over tokens of the projection.
5. **D-cos (reference):** Study 1's statistic with the true key.

Text score for 1–3: the mean over tokens of P(steered); also the authors' majority vote from token 5 onward (accuracy). **Metric:** text-level AUROC on the 40 test texts per key (20 steered, 20 unsteered), averaged over the 4 keys; per-key values reported.

## Decision rule (fixed now, before the run)
- **Reproduces** on a model at α if the MLP-faithful mean test AUROC is **≥ 0.95**. Detectors 2–5 are descriptive.
- Consequence for v0.2 (a proposal; Yichen decides):
  - (i) reproduces at α = 5 on a model → v0.2 uses the trained probe as the defender's detector at α = 5 on that model;
  - (ii) reproduces only at α ≥ 10 → v0.2 uses the smallest α that reproduces, reported as a deviation from the paper;
  - (iii) no detector reaches AUROC 0.95 at any α ≤ 20 on either model → the scheme does not reproduce on 1–1.5B base models under our settings; stop and bring the gate question to Yichen.
- Not measured: anything about key recovery or spoofing. No attack statistic is computed.

## Outputs
`research/outputs/repro_v0.1/results_<model>.json` (AUROCs, vote accuracies, activation norms, timings, input hashes, one sample text per α for inspection). Texts and features: `research/repro/data/` (git-ignored).
