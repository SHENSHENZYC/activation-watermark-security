# Reproduction pilot v0.1 — report

**Date:** 2026-09-25. **Spec:** [`REPRO_PILOT_SPEC_v0.1.md`](REPRO_PILOT_SPEC_v0.1.md), fixed before the run (commit `66c83e4`). **Scope:** tuning keys 9001–9004 and pool T only; no study key used; no attack statistic computed. **Outputs:** `research/outputs/repro_v0.1/results_{qwen,llama}.json`; exploratory addendum `addendum_quality_ppl.json` (script `addendum_quality_ppl.py`). Table built by `make_tables.py` from those files.

## Result against the pre-set rule
Rule: the watermark **reproduces** on a model at α if the authors' MLP probe (MLP-faithful) reaches a mean test AUROC ≥ 0.95 (4 keys × 40 test texts). Continuation-only variant shown; the with-prompt variant differs by at most 0.036 in AUROC (largest: Llama cosine at α = 5) (see the JSON).

| Model | α | ‖v‖ / median ‖h‖ | mlp_faithful | mlp_strong | linear | mass_mean | dcos_true_key | Reproduces (rule) | Median PPL (unsteered text) |
|---|---|---|---|---|---|---|---|---|---|
| qwen | 5 | 10% | 0.53 | 0.53 | 0.53 | 0.54 | 0.57 | no | 5.5 (vs 5.5) |
| qwen | 10 | 20% | 0.63 | 0.61 | 0.61 | 0.58 | 0.56 | no | 5.9 (vs 5.5) |
| qwen | 20 | 41% | 0.91 | 0.92 | 0.92 | 0.78 | 0.65 | no | 7.6 (vs 5.5) |
| llama | 5 | 129% | 1.00 | 1.00 | 1.00 | 1.00 | 0.87 | yes | 32.6 (vs 5.6) |
| llama | 10 | 259% | 1.00 | 1.00 | 1.00 | 1.00 | 0.65 | yes | 57.6 (vs 5.6) |
| llama | 20 | 517% | 1.00 | 1.00 | 1.00 | 1.00 | 0.55 | yes | 3382.3 (vs 5.6) |

‖v‖ / median ‖h‖ is the key's norm divided by the median unsteered activation norm at the steered layer (Qwen layer 14: 56.9; Llama layer 8: 5.7). The perplexity column is **exploratory** (added after the pilot, not in the spec): the median per-text perplexity of the continuation under the same model without steering, with the prompt as context, over 400 texts.

**Verdict by the rule:** Qwen: does not reproduce at any α ≤ 20. Llama: reproduces at α = 5, 10 and 20.

## Evidence (what the numbers show)
1. **The same α means very different strengths on the two models.** At the paper's α = 5, the key is 10% of the activation norm on Qwen but 129% on Llama.
2. **Qwen, α = 5:** no detector beats chance (AUROC 0.53–0.57), and the text is unchanged in perplexity. The watermark is effectively absent.
3. **Qwen, α = 20 (41%):** trained probes reach 0.91–0.92, just under the rule, with perplexity +38% (7.6 vs 5.5).
4. **Llama, α = 5:** every trained detector is perfect (1.00), but the median perplexity is **5.8× higher** (32.6 vs 5.6), and sample texts are visibly garbled; α = 10 and 20 produce gibberish.
5. **Our training-free cosine with the true key** is weak wherever the text is still fluent (≤ 0.65 on Qwen). It is highest (0.87) only on Llama at α = 5, where the text is damaged.

## Inference (not established)
- On these 1–1.5B base models, the pilot grid shows **no operating point that is both detectable (AUROC ≥ 0.95) and quality-preserving**. Qwen at 41% comes close on detection with a moderate quality cost. A window may exist between 41% and 129% of the activation norm; the pilot did not sample it.
- Self-Recognition's "no quality loss" results come mainly from 8B models (the watermark config in their code is Llama-3.1-8B). A sparse key at α = 5 is presumably small relative to 8B activations, but we have not measured that.
- The watermark's footprint in re-read text is **not aligned with the key direction** where the text stays fluent (cosine weak, probes strong). Recovering *v* itself may be much harder than forging the watermark with a probe-learned direction. That is a hypothesis for Study 1 v0.2, not a result.

## Consequences for Study 1 v0.2 (proposal; Yichen decides)
- Define the strength **relative to the activation norm** (ρ = ‖v‖ / median ‖h‖), not by raw α, and pre-register how the operating point is chosen (detectability and quality together).
- Use the **trained probe** as the defender's detector, with its false-positive rate calibrated on held-out unwatermarked text.
- Widen the attack from "average and read off *v*" to include **probe imitation** (the attacker trains the same kind of probe on their *n* watermarked texts against their own unwatermarked generations, then steers along what it learns).
- The detectability–quality curve against ρ is itself a candidate paper figure.
