# Strength calibration v0.2 (512 tokens) — report

**Date:** 2026-09-25. **Spec:** [`CALIBRATION_SPEC_v0.2.md`](CALIBRATION_SPEC_v0.2.md), fixed before the run (commit `cd1a44f`); memory fix before the restart (commit `5f92cd7`; computation only, equivalence tested). **Scope:** tuning keys 9001–9004, pool T; no study key; no attack statistic. **Outputs:** `research/outputs/calibration_v0.2/results_{qwen,llama}.json`. Table built by `make_calib02_tables.py` (the v0.1 columns come from `calibration_v0.1`).

## Result against the pre-set rule (AUROC ≥ 0.95 and perplexity ratio ≤ 1.25)

| Model | ρ | MLP AUROC, 256 tokens (v0.1) | MLP AUROC, first 256 of 512 (v0.2) | **MLP AUROC, 512 tokens** (per key) | Linear, 512 | PPL ratio, 256 (v0.1) | **PPL ratio, 512** | Both rules at 512 |
|---|---|---|---|---|---|---|---|---|
| qwen | 0.25 | 0.71 | 0.71 | **0.79** (0.77, 0.80, 0.71, 0.89) | 0.80 | 1.13 | **1.15** | no |
| qwen | 0.35 | 0.83 | 0.84 | **0.90** (0.82, 0.91, 0.90, 0.98) | 0.93 | 1.25 | **1.27** | no |
| qwen | operating point: **None** | | | | | | | |
| llama | 0.25 | 0.59 | 0.60 | **0.66** (0.65, 0.67, 0.70, 0.64) | 0.66 | 1.08 | **1.09** | no |
| llama | 0.35 | 0.72 | 0.71 | **0.81** (0.76, 0.84, 0.79, 0.84) | 0.82 | 1.13 | **1.15** | no |
| llama | operating point: **None** | | | | | | | |

**Verdict: no usable window on either model at 512 tokens either.**

## Evidence
1. **Doubling the length helps, but not enough.** At 512 tokens the authors' probe gains 0.075–0.089 AUROC over 256 tokens, reaching at most 0.90 (Qwen, ρ = 0.35), short of 0.95.
2. **Quality moves the other way for Qwen:** at ρ = 0.35 the perplexity ratio rises from 1.25 (256 tokens) to 1.27 (512), just past the limit.
3. **Internal consistency:** the first 256 tokens of the 512-token texts reproduce the v0.1 256-token AUROCs to within 0.013 on both models (different texts, same settings).
4. The unsteered 512-token perplexity medians are Qwen 5.03 and Llama 5.29 (the denominators of the ratios).

## Inference (not established)
- For Self-Recognition-style steering on 1–1.5B base models, the detectability–quality trade-off does not open with the paper's own text length. Together with v0.1, this points to a **scale** question: the paper's quality-neutral claims come from 8B models.
- Reaching AUROC 0.95 by length alone at ρ = 0.35 would need texts several times longer than 512 tokens (an extrapolation, not measured).
