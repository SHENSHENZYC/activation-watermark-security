# Strength calibration v0.1 — report

**Date:** 2026-09-25. **Spec:** [`CALIBRATION_SPEC_v0.1.md`](CALIBRATION_SPEC_v0.1.md), fixed before the run (commit `d053682`). **Scope:** tuning keys 9001–9004, pool T, 256-token continuations; no study key; no attack statistic. **Outputs:** `research/outputs/calibration_v0.1/results_{qwen,llama}.json`. Table built by `make_calib_tables.py`.

## Result against the pre-set rule
Operating point = the smallest ρ with the authors' MLP probe AUROC ≥ 0.95 **and** median perplexity ratio ≤ 1.25 (ρ = key norm ÷ median unsteered activation norm).

| Model | ρ | α equivalent | Authors' MLP AUROC (per key) | Linear | Mass-mean | Cosine (true key) | PPL ratio | Detectable (≥ 0.95) | Fluent (≤ 1.25) |
|---|---|---|---|---|---|---|---|---|---|
| qwen | 0.15 | 7.4 | **0.62** (0.68, 0.61, 0.59, 0.60) | 0.62 | 0.55 | 0.56 | **1.04** | no | yes |
| qwen | 0.25 | 12.3 | **0.71** (0.76, 0.74, 0.61, 0.72) | 0.73 | 0.67 | 0.59 | **1.13** | no | yes |
| qwen | 0.35 | 17.2 | **0.83** (0.82, 0.81, 0.80, 0.87) | 0.84 | 0.75 | 0.56 | **1.25** | no | yes |
| qwen | 0.50 | 24.5 | **0.97** (0.94, 0.97, 1.00, 0.98) | 0.97 | 0.91 | 0.72 | **1.62** | yes | no |
| qwen | 0.70 | 34.3 | **0.99** (0.97, 1.00, 1.00, 1.00) | 1.00 | 0.99 | 0.79 | **2.29** | yes | no |
| qwen | 1.00 | 49.0 | **1.00** (1.00, 1.00, 1.00, 1.00) | 1.00 | 1.00 | 0.79 | **4.25** | yes | no |
| qwen | operating point: **None** | | | | | | | | |
| llama | 0.15 | 0.6 | **0.53** (0.46, 0.59, 0.57, 0.51) | 0.52 | 0.57 | 0.53 | **1.03** | no | yes |
| llama | 0.25 | 1.0 | **0.59** (0.54, 0.66, 0.60, 0.55) | 0.59 | 0.63 | 0.60 | **1.08** | no | yes |
| llama | 0.35 | 1.4 | **0.72** (0.71, 0.67, 0.72, 0.78) | 0.72 | 0.67 | 0.69 | **1.13** | no | yes |
| llama | 0.50 | 1.9 | **0.89** (0.85, 0.88, 0.92, 0.91) | 0.91 | 0.81 | 0.76 | **1.44** | no | no |
| llama | 0.70 | 2.7 | **1.00** (0.99, 1.00, 1.00, 1.00) | 1.00 | 0.97 | 0.87 | **2.22** | yes | no |
| llama | 1.00 | 3.9 | **1.00** (1.00, 1.00, 1.00, 1.00) | 1.00 | 1.00 | 0.92 | **5.00** | yes | no |
| llama | operating point: **None** | | | | | | | | |

**Verdict by the rule: no usable window on either model** at 256 tokens. (Qwen's ρ = 0.35 ratio is 1.246, just inside the quality limit, but its AUROC is 0.83.)

## Evidence
1. **The trade-off is the same shape on both models once strength is measured as ρ.** Reliable detection (AUROC ≥ 0.95) needs ρ ≈ 0.5 (Qwen) to 0.7 (Llama); acceptable quality (ratio ≤ 1.25) holds only up to ρ ≈ 0.35. The raw α that gives the same ρ differs by a factor of about 13 between the models (for example, ρ = 0.5 is α = 24.5 on Qwen and 1.9 on Llama).
2. **The gap between the two conditions is real, not noise:** at ρ = 0.35 every key is ≤ 0.87 AUROC; at ρ = 0.5 the perplexity ratio is ≥ 1.44 on both models.
3. **The training-free cosine with the true key stays well below the trained probes at every ρ** (≤ 0.79 on Qwen, ≤ 0.92 on Llama).
4. The results agree with the pilot: Qwen ρ = 0.41 (pilot α = 20): AUROC 0.91, ratio 1.38; Llama ρ = 1.29 (pilot α = 5): ratio 5.8, against 5.0 at ρ = 1.0 here.

## Inference (not established)
- On 1–1.5B base models at 256 tokens, Self-Recognition-style steering cannot be made both reliably detectable and quality-neutral (by perplexity). The paper's "no quality loss" claim (on 8B models, 512-token texts) does not transfer to this scale under our measures.
- Sample texts at ρ = 0.5–0.7 still **read** fluently; perplexity may be stricter than a human reader. The 1.25 limit was a design choice.
- Two levers remain untested: **text length** (the authors' code generates 512 tokens; more tokens give the probe more evidence at the same ρ) and **model size**.
- Study 1 v0.2 does not have to use a single point: it could attack at several ρ along this curve, which would show how stealability moves with detectability and quality.
