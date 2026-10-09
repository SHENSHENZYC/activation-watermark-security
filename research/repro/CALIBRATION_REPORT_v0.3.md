# Strength calibration v0.3 (Llama-3.2-3B scale check) — report

**Date:** 2026-09-26. **Spec:** [`CALIBRATION_SPEC_v0.3.md`](CALIBRATION_SPEC_v0.3.md), fixed before the run (commit `4016338`). **Scope:** tuning keys 9001–9004, pool T, 256 tokens; no study key; no attack statistic. **Output:** `research/outputs/calibration_v0.3/results_llama3b.json`. Table built by `make_calib03_tables.py` (the 1B and 1.5B columns come from calibration v0.1, with the same design and length).

## Result against the pre-set rule (authors' MLP AUROC ≥ 0.95 and perplexity ratio ≤ 1.25)

| ρ | Llama-3.2-1B: AUROC / PPL ratio | Qwen2.5-1.5B: AUROC / PPL ratio | Llama-3.2-3B: AUROC / PPL ratio |
|---|---|---|---|
| 0.15 | 0.53 / 1.03 | 0.62 / 1.04 | 0.48 / 1.03 |
| 0.25 | 0.59 / 1.08 | 0.71 / 1.13 | 0.56 / 1.05 |
| 0.35 | 0.72 / 1.13 | 0.83 / 1.25 | 0.56 / 1.11 |
| 0.50 | 0.89 / 1.44 | 0.97 / 1.62 | 0.70 / 1.26 |
| 0.70 | 1.00 / 2.22 | 0.99 / 2.29 | 0.86 / 1.62 |
| paper α = 5 is ρ ≈ | 1.29 | 0.10 | 0.67 |
| operating point | None | None | None |

(Llama-3.2-3B: layer 14 of 28, k = 9, N = 12.665, unsteered median perplexity 4.538.)

**Verdict: no operating point on Llama-3.2-3B.** Under the pre-committed follow-up, **Study 1 v0.2 attacks along the trade-off curve on Qwen2.5-1.5B**, and calibration ends here.

## Evidence
1. At the same relative strength, the 3B model is **less** detectable than the 1B and 1.5B models (for example, ρ = 0.5: AUROC 0.70 against 0.89 and 0.97), with a somewhat smaller quality cost (ratio 1.26 against 1.44 and 1.62).
2. The paper's α = 5 corresponds to ρ ≈ 0.67 on the 3B model; the nearest grid point (ρ = 0.7) gives AUROC 0.86 with a perplexity ratio of 1.62.
3. Sample texts read fluently at every level on 3B.

## Inference (not established)
- Moving from 1B to 3B does **not** open a detectable-and-fluent window; if anything, the detectable end moves further out. This does not support "the window opens with scale" in the 1–3B range. Whether it opens at 8B (the paper's main model, which does not fit this machine in bf16) remains untested.
- The three curves are a candidate paper figure (detectability and quality against ρ, by model).
