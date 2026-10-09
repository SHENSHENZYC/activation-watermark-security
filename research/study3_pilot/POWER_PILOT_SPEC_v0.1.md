# Study 3 power pilot v0.1: which key-specific statistic should the exact test use?

**Status:** FIXED (2026-09-30, approved by Yichen as drafted) before any statistic on watermarked texts was computed. The commit that fixes it is recorded by the script (`features_guard.json`, `results.json`) and in the report. Any change needs a new version.
**Why:** Study 3 (exact key-resampling tests) needs one primary statistic. The raw cosine with the true key is weak on the tuning keys (AUROC 0.56 / 0.72 / 0.79 at ρ = 0.35 / 0.50 / 0.70; [`../repro/CALIBRATION_REPORT_v0.1.md`](../repro/CALIBRATION_REPORT_v0.1.md)), and the gradient score has never been measured. Study 1 v0.1 failed its gate G1 because detection power was not checked on tuning keys before the lock; this pilot does that check for Study 3.
**Decided by:** Yichen (a tuning-key pilot picks the primary; 2026-09-30); Claude (design, below).
**Scope:** tuning keys 9001–9004 and their calibration texts only. No study key, no study-key text and no forged text is read. Nothing here is a claim about attacks.

## Inputs (reused; SHA-256 recorded in the outputs)
- **Watermarked texts:** calibration v0.1, Qwen, `research/repro/data/qwen/texts_calib_r{025,035,050,070}_k900{1..4}.json` (100 texts per key and level; key *i* used pool T prompts 100*i* … 100*i* + 99; 256 new tokens; Self-Recognition's sampling settings). Keys: `core.make_key(s, 1536, 1)` rescaled to norm ρ·N, N = 56.90 (as in calibration and Study 1 v0.2).
- **Unwatermarked texts:** the reproduction pilot's `texts_van_k900{1..4}.json` (400 texts on the same pool T prompts, no steering).
- **Owner's reference set:** Study 1 v0.2's pool F unwatermarked texts, `research/study1_v02/data/S_F_van.json` (200 texts, generated once with no key; the same set the owner trained its probe against). It gives the per-coordinate mean and standard deviation for the standardised candidates.
- Model: Qwen2.5-1.5B, revision `8faed761`, bf16 on MPS; the owner's layer *l* = 14.

## Per-text features (one forward and one backward pass per text, batch 1)
The detector sees only the continuation text: its first 256 tokens, no prompt, encoded exactly as in Study 1 (`core._encode`; no BOS on Qwen).
- **a** = the mean over tokens of h_t / ‖h_t‖ at the output of decoder layer 14 (the quantity behind Study 1's D-cos).
- **g** = the gradient of the summed continuation log-likelihood with respect to an additive vector *b* at the output of decoder layer 14, evaluated at *b* = 0 (as in `core.score_gradients`). Heuristically, E[g] ≈ F·v for text steered by *v* (F: the Fisher information), so ⟨v, g⟩ is the first-order likelihood-ratio statistic for the key; this is GaussMark's statistic with the additive vector in place of a weight perturbation.

## Candidates
Each candidate turns a text into a vector *x*; its statistic for key *v* is **T(x, v) = ⟨x, v⟩ / (‖x‖·‖v‖)**.
| | Name | *x* |
|---|---|---|
| S1 | raw cosine (Self-Recognition's zero-shot statistic, token-averaged) | a |
| S2 | standardised cosine | (a − μ_a) / σ_a, per coordinate, μ and σ over the 200 pool F texts |
| S3 | gradient score | g |
| S4 | standardised gradient score | (g − μ_g) / σ_g, per coordinate, over the pool F texts |

Within one text, dividing by ‖x‖ or ‖v‖ does not change the p-value (all keys have the same norm); the candidates differ in the feature (activations or gradient) and in the centring and scaling of coordinates.

## Exact p-value
p = (1 + #{j : T(x, v_j) ≥ T(x, v)}) / (1 + M), with **M = 999** null keys from the public key distribution (Self-Recognition's sparse keys: *k* = 4 random coordinates, uniform[−1, 1] values; `core.null_keys`, seeds 77,700,000 + *j*, disjoint from every study, control, tuning and validation seed). A text is **detected** if p ≤ 0.01. If the text was produced independently of *v* (unwatermarked, human, or steered by another key), *v* and the null keys are exchangeable and P(p ≤ 0.01) ≤ 0.01 exactly.

## Metric and selection rule (fixed before the run)
- TPR(c, ρ, s) = the share of key *s*'s 100 watermarked texts at level ρ detected by candidate *c*; m(c, ρ) = the median over the 4 tuning keys.
- **Score(c) = the mean of m(c, ρ) over the three working levels ρ ∈ {0.35, 0.50, 0.70}** (Study 1's levels at which the watermark worked).
- **Primary = the candidate with the highest score.** If other candidates are within 2.0 percentage points of the top score, the first of those (the top one included) in the fixed order **S3, S4, S2, S1** is chosen: the first-order likelihood-ratio statistic first, then its standardised form, then the cosines.
- **Implementation check (must pass, or no candidate is chosen and the code is fixed first):** for each candidate, the pooled detection rate on the 400 unwatermarked texts, each tested against all 4 tuning keys (1,600 tests), lies in [0.3%, 2.5%].
- **Viability reading (not automatic):** the primary is *usable on single texts* at a level if m ≥ 20% there (the bar Study 1 v0.2 set for the owner's probe, L1). If it is usable at no working level, single-text exact tests are too weak on this model at 256 tokens; I then bring Yichen the option of pooled tests (several texts from one source per test) before drafting the protocol.

## Descriptive outputs (no rule)
- ρ = 0.25 (a Study 1 level at which the probe failed L1), all candidates.
- AUROC of T(x, v) between each key's watermarked and the 400 unwatermarked texts, per candidate, level and key.
- **Cross-key (generic steering):** key *s*'s watermarked texts tested with each other tuning key (12 ordered pairs × 100 texts per level). Expected about 1% by construction, since the other key is independent of the text.
- **Pooled tests:** T summed over *n* ∈ {4, 16} texts of the same key (consecutive disjoint batches: 25 of 4 and 6 of 16 per key), with the same null keys; the share of batches detected, and the same for batches of unwatermarked texts.
- The spread of coordinate scales (max / median of σ_a and σ_g), to explain any gap between raw and standardised forms.
- Time per text (forward plus backward), and the projected cost of Study 3.

## Validation before the run (inputs only; no statistic on watermarked texts)
1. Every input file exists; SHA-256 recorded; the text counts are 100 per key and level, 400 unwatermarked, 200 in pool F.
2. The tuning keys rebuild with norm ρ·N and 4 nonzero coordinates; the null-key seeds are disjoint from all other seeds.
3. The p-value function on synthetic Gaussian data: under a simulated null (the true key drawn like the null keys), 10,000 p-values are uniform (KS p > 0.01) and lie on the 1/1,000 grid; with a planted signal, the detection rate is above 90%.
4. The gradient on one pool F text: across 8 random directions *u*, the finite difference [log p(*b* = εu) − log p(*b* = −εu)] / 2ε correlates with ⟨g, u⟩ at r > 0.95.
5. The hook is removed after each pass (logits equal the unhooked logits).
6. Timing on 10 pool F texts, projected to the pilot's 2,200 texts (budget: 1 h).

## Outputs
`research/outputs/study3_pilot_v0.1/VALIDATION.json` and `results.json` (committed); per-text features in `research/study3_pilot/data/` (git-ignored); the report `POWER_PILOT_REPORT_v0.1.md`, built by a script from `results.json`.
**Compute:** about 2,200 texts (1,600 watermarked, 400 unwatermarked, 200 reference) at about 0.45 s each: about 20 minutes.
