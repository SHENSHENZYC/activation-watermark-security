# Strength calibration v0.3: does a larger model (Llama-3.2-3B) have a detectable and fluent window?

**Status:** spec fixed before any v0.3 run (2026-09-25). The **last calibration step**; input validation for Study 1 v0.2: tuning keys only, no claims about attacks.
**Why:** calibrations v0.1 (256 tokens) and v0.2 (512 tokens) found no ρ that is both detectable and fluent on Qwen2.5-1.5B or Llama-3.2-1B ([`CALIBRATION_REPORT_v0.1.md`](CALIBRATION_REPORT_v0.1.md), [`CALIBRATION_REPORT_v0.2.md`](CALIBRATION_REPORT_v0.2.md)). Self-Recognition's quality claims come from larger models. Llama-3.2-3B is paper-listed, fits the M5 in bf16, and access was already granted.
**Decided by:** Yichen (3B scale check, then commit); Claude (design).

## Model
Llama-3.2-3B, revision `13afe512` (manifest `research/stage4/outputs/model_manifest_llama-3.2-3b.json`, licence llama3.2); 28 layers, *d* = 3072; steered layer **14** (the middle, Self-Recognition's rule); key support *k* = ⌊0.003·3072⌋ = 9. bf16 on MPS. Registered at run time in Study 1 `core` (the file is not edited).

## Design (as calibration v0.1, 256 tokens)
- **Step 1, reference:** 100 unsteered texts per tuning key (pool T, the same prompts and seeds as before). N = the median activation norm at layer 14 over the continuation tokens of key 9001's unsteered texts (the pilot's definition). The perplexity denominator is the median over all 400 unsteered texts.
- **Step 2, grid:** ρ ∈ {0.15, 0.25, 0.35, 0.50, 0.70}; keys rescaled to norm ρ·N with Self-Recognition's support and values; 100 steered texts per key and ρ.
- Features (continuation only), detectors, the 60/20/20 split by prompt and perplexity: as in v0.1–v0.2 (memory-safe code from `calibrate_v02.py`).

## Operating-point rule (unchanged, fixed before the run)
The smallest ρ with the authors' MLP probe mean test AUROC ≥ 0.95 **and** median perplexity ratio ≤ 1.25.

## Pre-committed follow-up (fixed now; calibration ends after this step)
- **If Llama-3.2-3B has an operating point ρ\*:** Study 1 v0.2 attacks Llama-3.2-3B at ρ\*.
- **If not:** Study 1 v0.2 attacks **along the trade-off curve** on Qwen2.5-1.5B (the nudge levels are set in the v0.2 protocol).
- Either way, the detectability and quality curves for 1B, 1.5B and 3B are kept for a paper figure on scale.

## Outputs
`research/outputs/calibration_v0.3/results_llama3b.json`; texts and features in `research/repro/data/llama3b/` (git-ignored).
