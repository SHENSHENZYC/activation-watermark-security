# Study 3 power pilot v0.1 — report

Date: 2026-09-30 (Milestone 5). Spec: [`POWER_PILOT_SPEC_v0.1.md`](POWER_PILOT_SPEC_v0.1.md), FIXED before any statistic on watermarked texts (commit `b55948c`; spec SHA-256 `ca535eda9c92…`, script `fbfb6ad72cb7…`). Validation: [`../outputs/study3_pilot_v0.1/VALIDATION.json`](../outputs/study3_pilot_v0.1/VALIDATION.json) (all pass: True). Results: [`../outputs/study3_pilot_v0.1/results.json`](../outputs/study3_pilot_v0.1/results.json). **Built by** `make_report.py`; no number is typed by hand. Tuning keys 9001–9004 only; no study key, study-key text or forgery was read. Exact key-resampling test with M = 999 null keys, detection at p ≤ 0.01.

## 1. Rule vs observed (spec: selection rule, fixed before the run)

| Candidate | FPR check (400 texts × 4 keys; pass if 0.3–2.5%) | Score (mean over ρ 0.35/0.50/0.70 of median TPR, %) |
|---|---|---|
| S1 raw cosine | 0.00% (FAIL) | 0.0 |
| S2 standardised cosine | 1.12% (pass) | 6.0 |
| S3 gradient score | 1.06% (pass) | 97.7 |
| S4 standardised gradient score | 0.88% (pass) | 95.7 |

**Implementation check:** FAIL. **Top score:** 97.7; within the 2.0-point tie margin: S3, S4. **Primary (by the rule): none.** **Viability:** not usable on single texts at any working level (pooled-test option goes to Yichen).

## 2. Tables

### Table 1 — TPR at an exact 1% FPR, single texts (median over 4 tuning keys, % [min–max over keys])

| Candidate | ρ = 0.25 (descriptive) | ρ = 0.35 | ρ = 0.5 | ρ = 0.7 |
|---|---|---|---|---|
| S1 raw cosine | 0 [0–0] | 0 [0–0] | 0 [0–0] | 0 [0–0] |
| S2 standardised cosine | 2 [1–2] | 4 [2–10] | 7 [3–15] | 7 [3–36] |
| S3 gradient score | 93 [75–98] | 96 [94–99] | 98 [96–100] | 98 [83–100] |
| S4 standardised gradient score | 88 [84–94] | 96 [89–99] | 98 [90–100] | 94 [71–99] |

### Table 2 — AUROC of the key's statistic, watermarked vs the 400 unwatermarked texts (median over keys [min–max])

| Candidate | ρ = 0.25 (descriptive) | ρ = 0.35 | ρ = 0.5 | ρ = 0.7 |
|---|---|---|---|---|
| S1 raw cosine | 0.648 [0.525–0.734] | 0.688 [0.483–0.766] | 0.782 [0.554–0.796] | 0.808 [0.611–0.909] |
| S2 standardised cosine | 0.673 [0.584–0.732] | 0.696 [0.551–0.766] | 0.798 [0.644–0.846] | 0.795 [0.634–0.949] |
| S3 gradient score | 0.996 [0.994–0.999] | 0.999 [0.986–0.999] | 0.998 [0.996–1.000] | 0.999 [0.986–1.000] |
| S4 standardised gradient score | 0.995 [0.995–0.999] | 0.999 [0.987–0.999] | 0.998 [0.996–1.000] | 1.000 [0.985–1.000] |

### Table 3 — Cross-key detection (text steered by one tuning key, tested with another; generic steering; about 1% expected by construction)

| Candidate | ρ = 0.25 (descriptive) | ρ = 0.35 | ρ = 0.5 | ρ = 0.7 |
|---|---|---|---|---|
| S1 raw cosine | 0.0% (n = 1200) | 0.0% (n = 1200) | 0.0% (n = 1200) | 0.0% (n = 1200) |
| S2 standardised cosine | 0.5% (n = 1200) | 0.5% (n = 1200) | 0.5% (n = 1200) | 0.2% (n = 1200) |
| S3 gradient score | 0.6% (n = 1200) | 1.4% (n = 1200) | 0.8% (n = 1200) | 0.2% (n = 1200) |
| S4 standardised gradient score | 0.7% (n = 1200) | 0.5% (n = 1200) | 0.3% (n = 1200) | 0.1% (n = 1200) |

### Table 4 — Pooled tests: detection when *n* texts of one key are tested together (median over keys, % [min–max]), and on unwatermarked batches

| Candidate | texts per test | ρ = 0.25 | ρ = 0.35 | ρ = 0.5 | ρ = 0.7 | unwatermarked (FPR) |
|---|---|---|---|---|---|---|
| S1 raw cosine | 4 (25 per key) | 0 [0–0] | 0 [0–0] | 0 [0–0] | 0 [0–0] | 0.0% |
| S1 raw cosine | 16 (6 per key) | 0 [0–0] | 0 [0–0] | 0 [0–0] | 0 [0–0] | 0.0% |
| S2 standardised cosine | 4 (25 per key) | 6 [4–8] | 18 [8–20] | 30 [4–48] | 22 [0–84] | 1.0% |
| S2 standardised cosine | 16 (6 per key) | 25 [0–50] | 50 [0–67] | 75 [17–100] | 33 [0–100] | 1.0% |
| S3 gradient score | 4 (25 per key) | 100 [100–100] | 100 [100–100] | 100 [100–100] | 100 [100–100] | 1.0% |
| S3 gradient score | 16 (6 per key) | 100 [100–100] | 100 [100–100] | 100 [100–100] | 100 [100–100] | 0.0% |
| S4 standardised gradient score | 4 (25 per key) | 100 [100–100] | 100 [100–100] | 100 [100–100] | 100 [100–100] | 1.5% |
| S4 standardised gradient score | 16 (6 per key) | 100 [100–100] | 100 [100–100] | 100 [100–100] | 100 [100–100] | 1.0% |

Coordinate-scale spread in the owner's reference set (max / median of the per-coordinate standard deviation): activations 21.1, gradients 2.0.
Timing: 0.21 s per text (one forward and one backward pass, batch 1).

## 3. Reading

### Pre-registered outcome (mechanical)
- **The implementation check fails for S1** (0.00% of 1,600 unwatermarked tests, below the 0.3% floor). S2, S3 and S4 pass (1.12%, 1.06%, 0.88%). **By the rule, no primary is chosen.**
- The viability line in §1 ("not usable") follows from "no primary", not from the TPRs; stated plainly, S3 and S4 have median TPR ≥ 20% at every level (S3 96–98%, S4 94–98% at the three working levels).
- **What the check did not foresee (my error, stated plainly):** it was meant to catch code bugs, and it pooled four fixed keys. A statistic can be exact on average over keys yet far from 1% for any one fixed key; S1 is such a statistic (below). The rule's wording ("no candidate is chosen") made one candidate's property block the choice among the others.

### Diagnosis (written and run after the outcomes were read; exploratory)
Script `posthoc_diag.py`; output [`../outputs/study3_pilot_v0.1/posthoc_diagnostics.json`](../outputs/study3_pilot_v0.1/posthoc_diagnostics.json).
1. **Not a feature bug.** On the calibration's own test split, S1 reproduces calibration v0.1's cosine AUROC exactly: ρ = 0.25: 0.592 vs 0.592, ρ = 0.35: 0.562 vs 0.562, ρ = 0.5: 0.723 vs 0.723, ρ = 0.7: 0.794 vs 0.794.
2. **Key resampling is exact on average over keys, not per key.** Over 1,000 fresh random keys, each tested on the 400 unwatermarked texts, S1's mean FPR is 1.15%, but 93.1% of keys never fire and 1.1% fire on more than half of the texts (max 100%). The raw activation mean is nearly the same for every text (coordinate-scale spread 21×), so a key's rank among the null keys is almost fixed: a given key either never or always fires. The four tuning keys are all in the first group.
3. **Per-key FPR of the other candidates** (same diagnostic; mean, 95th percentile, max; share of keys above 5%): S2 standardised cosine 1.02%, 2.50%, 5.25%, 0.1%; S3 gradient score 0.93%, 3.50%, 20.25%, 2.3%; S4 standardised gradient score 0.96%, 2.25%, 4.75%, 0.0%. Centring and scaling each coordinate (S4) keeps every key's FPR near 1%; the raw gradient (S3) leaves a few keys well above it.

### Evidence (tuning keys only)
- The **gradient statistics detect the watermark on single 256-token texts** at an exact 1% FPR: S3 median TPR 96–98% and S4 94–98% at ρ = 0.35–0.70, and 93% / 88% at ρ = 0.25; AUROC 0.995–1.000. Pooling 4 texts gives 100% for both at every level.
- The **cosines do not**: S1 0% everywhere; S2 4–7%.
- **Key-specific:** texts steered by another tuning key are detected at 0.1–1.4% by S3 and S4 (about 1% by construction), so these tests detect the key, not steering in general.

### Inference (not established)
- On these tuning keys the gradient test detects where the authors' MLP could not (calibration v0.1 MLP AUROC 0.71 at ρ = 0.25 and 0.83 at 0.35). If this holds on study keys, the calibrations' "no detectable-and-fluent window" is a property of the probe detector, not of the watermark, and Study 1's forgeries will face a much stronger key-specific test.
- Four tuning keys and 100 texts per key: these are design estimates, not study results.
