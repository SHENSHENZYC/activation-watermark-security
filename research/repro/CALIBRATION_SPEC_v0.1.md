# Strength calibration v0.1: is there a detectable and fluent operating point?

**Status:** spec fixed before any calibration run (2026-09-25). Input validation for Study 1 v0.2: tuning keys only, no claims about attacks.
**Why:** the reproduction pilot ([`REPRO_PILOT_REPORT_v0.1.md`](REPRO_PILOT_REPORT_v0.1.md)) found that raw α does not transfer across models (α = 5 is 10% of the activation norm on Qwen and 129% on Llama), and no pilot grid point was both detectable and fluent.
**Decided by:** Yichen (calibrate relative strength); Claude (design).

## Strength parameter
ρ = ‖v‖ / N, where N is the median unsteered activation norm at the steered layer, **taken from the pilot** (`results_<model>.json`, `act_norm_median_unsteered`: Qwen 56.9 at layer 14, Llama 5.67 at layer 8). For tuning key *s*, the key is Self-Recognition's sparse key (support and values from `core.make_key(s, d, 1)`) rescaled so that its norm is exactly ρ·N.
**Grid (same for both models):** ρ ∈ {0.15, 0.25, 0.35, 0.50, 0.70, 1.00}.

## Data and detectors (as in the pilot)
Tuning keys 9001–9004, pool T (key *i* uses prompts 100*i … 100*i+99), 100 steered texts per key and ρ, 256 new tokens, Self-Recognition's sampling settings, the same per-key seed. The unsteered comparison texts and their features are **reused from the pilot** (same prompts, seeds and settings; SHA-256 recorded). Features: the continuation-only variant. Detector for the rule: the authors' MLP probe (MLP-faithful), trained per key on 60 prompts, test AUROC on 20 + 20 texts, averaged over 4 keys. The other pilot detectors are reported as descriptive.
**Quality:** the median per-text perplexity of the continuation under the same model without steering (prompt as context, batch 1), over the 400 steered texts, divided by the pilot's unsteered median (Qwen 5.5, Llama 5.6; the exact values are read from `addendum_quality_ppl.json`).

## Operating-point rule (fixed now, before the run)
For each model, the **operating point** ρ\* is the smallest ρ on the grid with **both**:
- detectability: MLP-faithful mean test AUROC ≥ 0.95, and
- quality: median perplexity ratio ≤ 1.25.

If no ρ on the grid qualifies, the model has **no usable window** at 256 tokens, and this is reported as a finding. Study 1 v0.2 then needs Yichen's decision (for example, longer texts, a larger model, or a relaxed rule, each as a new version).
Also reported (descriptive): the full detectability and quality curves against ρ, per key.

## Outputs
`research/outputs/calibration_v0.1/results_<model>.json`; texts and features in `research/repro/data/<model>/calib_*` (git-ignored).
