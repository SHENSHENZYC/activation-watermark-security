# Study 1 — report v0.2: key recovery and forgery along the detectability–quality curve (Qwen2.5-1.5B)

Date: 2026-09-26 (Milestone 2). Protocol: [`STUDY1_PROTOCOL_v0.2.md`](STUDY1_PROTOCOL_v0.2.md) (LOCKED 2026-09-26 01:26 UTC, before outcomes). Lock: [`outputs/study1_v0.2/PRE_RUN_LOCK.json`](outputs/study1_v0.2/PRE_RUN_LOCK.json). Run manifest: [`outputs/study1_v0.2/RUN_MANIFEST_SKR.json`](outputs/study1_v0.2/RUN_MANIFEST_SKR.json). Results: [`outputs/study1_v0.2/results.json`](outputs/study1_v0.2/results.json). **This file is built by** `study1_report_v02/make_report_assets.py`, **which inserts the tables from the locked outputs; no number in the tables is typed by hand.**

## 1. Run
- Started 2026-09-26 01:34:20 UTC after a Mac restart (swap 0); finished 23:58 UTC; 80,660 s (22.4 h) against the 23 h projection. Phases S, K (32 key-levels), R, in one run, with no restart or crash.
- `check_lock()` accepted the lock before the start and again after the run (protocol and all code unchanged). The holdout was not touched (`final: false`).

## 2. Pre-registered results (protocol §10)
### Table 1 — Pre-registered rules vs observed (protocol §10)

G1 (pooled FPR on pool A2 within [0.3%, 2.5%]): observed **1.4%** → **PASS**. G2 (attack isolation): asserted in code. Descriptive: FPR on the human continuations of A2 = 3.6%.

| ρ | Oracle median acceptance (L1: ≥ 20%) | L1 | R1 key recovery (Route A) | R2 Route A | R2 Route B | Random-key median | R3 generic steering suffices (random ≥ 50% of oracle) |
|---|---|---|---|---|---|---|---|
| 0.25 | 8.0% | fail | (descriptive) fails at this budget | (descriptive) inconclusive | (descriptive) inconclusive | 1.0% | no |
| 0.35 | 32.0% | pass | fails at this budget | inconclusive | practical (n=64) | 1.5% | no |
| 0.5 | 86.0% | pass | fails at this budget | not practical | practical (n=64) | 13.0% | no |
| 0.7 | 100.0% | pass | fails at this budget | not practical | practical (n=64) | 55.5% | yes |

Levels failing L1 are descriptive only (protocol §10).

**In words (evidence):**
- **G1 passes:** the owner's threshold holds its false-positive rate on its own unwatermarked texts.
- **L1:** the watermark "works" (oracle median acceptance ≥ 20% at a 1% FPR) at ρ = 0.35, 0.50 and 0.70, not at 0.25 (so 0.25 is descriptive only).
- **R1 fails at every level:** the averaging estimator (Route A) does not recover the key within 1,024 observed texts (median cosine ≤ 0.16; layer found for at most 3 of 8 keys at any *n*).
- **R2, Route B (footprint imitation) is practical at *n* = 64 at all three working levels:** forged texts are accepted at 42.5%, 99% and 100% (median) against oracle rates of 32%, 86% and 100%. At ρ = 0.35 the margin is narrow: the forgery's lower 95% bound (5.0%) only just clears the random-key control's upper bound (4.5%).
- **R2, Route A:** inconclusive at 0.35; "not practical" at 0.50 and 0.70.
- **R3 (generic steering suffices) holds only at ρ = 0.70**, where a random key of the same norm at the same layer is accepted at 55.5% (median).
- **Materiality (§10):** Route B forgeries reach ≥ 50% of the genuine acceptance rate at a 1% FPR at every working level; by the pre-registered standard, the trained-probe watermark is **unreliable as evidence of provenance** at these strengths, against a passive attacker with 64 texts and no key.

**A limitation of rule R2 that I did not foresee (stated plainly):** the "not practical" clause uses max(2 × the random-key median, 2%). When the random-key median is ≥ 50% (ρ = 0.70, where R3 holds), that bound is above 100%, so "not practical" is reached automatically. Route A's "not practical" at ρ = 0.70 is therefore **uninformative**: its median acceptance is 80.5–90.5%, close to the oracle, but it cannot be told apart from generic steering there (R3). The verdict stands as pre-registered; this is how to read it.

**Omission (stated plainly):** protocol §5 and §8 list D-cos with the true key and its exact key-resampling p-value as secondary diagnostics. The locked runner does not compute them. They are descriptive only, do not enter any rule, and can be computed later from the saved texts; they are deferred to Study 3 (exact tests). The detector AUROC (§8) is computed below from the saved scores.

## 3. Full tables
### Table 2 — Acceptance by the owner's detector at its 1%-FPR threshold (median over 8 keys, % [95% cluster-bootstrap CI]; median perplexity of the texts under the unsteered model)

| ρ | Oracle (true key) | Random key | A n=64 | A n=256 | A n=1024 | B n=64 | B n=256 | B n=1024 |
|---|---|---|---|---|---|---|---|---|
| 0.25 | 8.0 [6.0, 17.0] | 1.0 [0.0, 2.0] | 2.5 [0.0, 4.5] | 1.5 [0.0, 3.5] | 2.0 [0.0, 3.5] | 3.0 [0.0, 5.5] | 6.0 [2.0, 10.5] | 7.5 [2.0, 29.5] |
| ppl | 6.5 | 6.5 | 6.1 | 6.0 | 6.0 | 6.8 | 6.8 | 7.2 |
| 0.35 | 32.0 [17.5, 52.5] | 1.5 [0.0, 4.5] | 11.0 [2.5, 22.0] | 3.5 [0.5, 14.5] | 4.5 [1.0, 16.0] | 42.5 [5.0, 68.0] | 56.0 [14.0, 80.5] | 45.5 [8.0, 87.5] |
| ppl | 7.7 | 7.7 | 7.4 | 7.0 | 6.9 | 10.4 | 10.5 | 10.3 |
| 0.5 | 86.0 [73.5, 94.5] | 13.0 [8.0, 18.5] | 23.0 [6.5, 71.5] | 20.0 [5.5, 35.5] | 20.5 [8.5, 69.3] | 99.0 [90.5, 100.0] | 99.5 [96.0, 100.0] | 100.0 [95.5, 100.0] |
| ppl | 10.5 | 10.5 | 8.8 | 8.8 | 9.5 | 17.2 | 17.8 | 18.2 |
| 0.7 | 100.0 [100.0, 100.0] | 55.5 [34.0, 83.0] | 80.5 [24.0, 100.0] | 90.5 [76.5, 100.0] | 89.0 [69.5, 100.0] | 100.0 [99.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| ppl | 16.8 | 16.5 | 10.0 | 13.7 | 11.7 | 30.6 | 30.5 | 31.1 |

Descriptive (protocol §8, computed from the saved scores after the run): detector AUROC, oracle texts (pool D) vs the owner's unwatermarked check texts (pool A2), median over keys [min, max]:

- ρ = 0.25: 0.746 [0.686, 0.840]
- ρ = 0.35: 0.888 [0.808, 0.972]
- ρ = 0.5: 0.986 [0.954, 0.998]
- ρ = 0.7: 0.998 [0.997, 1.000]

### Table 3 — Key recovery (median over 8 keys of cos(v̂, v); layer hits out of 8; Route A median support hit out of k = 4)

| ρ | n | cos A | cos B | layer hits A | layer hits B | support hit A |
|---|---|---|---|---|---|---|
| 0.25 | 1 | 0.000 | 0.006 | 0 | 0 | 0.00 |
| 0.25 | 4 | 0.000 | 0.021 | 0 | 0 | 0.00 |
| 0.25 | 16 | 0.000 | 0.023 | 0 | 0 | 0.00 |
| 0.25 | 64 | 0.000 | 0.042 | 0 | 3 | 0.00 |
| 0.25 | 256 | 0.124 | 0.045 | 1 | 2 | 0.25 |
| 0.25 | 1024 | 0.160 | 0.054 | 2 | 2 | 0.25 |
| 0.35 | 1 | 0.000 | 0.001 | 1 | 0 | 0.00 |
| 0.35 | 4 | 0.000 | 0.018 | 1 | 0 | 0.00 |
| 0.35 | 16 | 0.000 | 0.028 | 0 | 2 | 0.00 |
| 0.35 | 64 | 0.105 | 0.036 | 1 | 2 | 0.25 |
| 0.35 | 256 | 0.079 | 0.050 | 2 | 2 | 0.25 |
| 0.35 | 1024 | 0.074 | 0.050 | 2 | 2 | 0.25 |
| 0.5 | 1 | 0.000 | 0.013 | 0 | 0 | 0.00 |
| 0.5 | 4 | 0.000 | 0.020 | 2 | 0 | 0.00 |
| 0.5 | 16 | 0.032 | 0.043 | 3 | 2 | 0.12 |
| 0.5 | 64 | 0.000 | 0.037 | 1 | 2 | 0.00 |
| 0.5 | 256 | 0.000 | 0.046 | 2 | 2 | 0.00 |
| 0.5 | 1024 | 0.151 | 0.047 | 1 | 2 | 0.25 |
| 0.7 | 1 | 0.000 | 0.027 | 0 | 0 | 0.00 |
| 0.7 | 4 | 0.000 | 0.032 | 0 | 1 | 0.00 |
| 0.7 | 16 | 0.000 | 0.048 | 0 | 2 | 0.00 |
| 0.7 | 64 | 0.000 | 0.046 | 1 | 1 | 0.00 |
| 0.7 | 256 | 0.000 | 0.044 | 2 | 1 | 0.00 |
| 0.7 | 1024 | 0.015 | 0.043 | 2 | 1 | 0.12 |

### Table 4 — EXPLORATORY (added after the run): forgery quality per key-level

A key-level forgery counts as *effective* if its acceptance is ≥ 50% of that key-level's oracle acceptance, and as *fluent* if its median perplexity is ≤ 1.5× that key-level's oracle median (cut-off chosen after seeing the data). Counts are out of 8 keys.

| ρ | Route | n | effective | effective and fluent | keys whose chosen layer is 0 or 1 | median ppl ratio to oracle |
|---|---|---|---|---|---|---|
| 0.25 | A | 64 | 1 | 1 | 1 | 0.94 |
| 0.25 | A | 256 | 0 | 0 | 1 | 0.93 |
| 0.25 | A | 1024 | 1 | 1 | 1 | 0.93 |
| 0.25 | B | 64 | 2 | 2 | 4 | 1.00 |
| 0.25 | B | 256 | 3 | 3 | 3 | 1.02 |
| 0.25 | B | 1024 | 4 | 4 | 4 | 1.07 |
| 0.35 | A | 64 | 2 | 2 | 0 | 0.96 |
| 0.35 | A | 256 | 0 | 0 | 1 | 0.93 |
| 0.35 | A | 1024 | 0 | 0 | 2 | 0.89 |
| 0.35 | B | 64 | 6 | 3 | 5 | 1.25 |
| 0.35 | B | 256 | 6 | 3 | 4 | 1.35 |
| 0.35 | B | 1024 | 6 | 3 | 4 | 1.30 |
| 0.5 | A | 64 | 3 | 3 | 1 | 0.81 |
| 0.5 | A | 256 | 1 | 1 | 1 | 0.86 |
| 0.5 | A | 1024 | 2 | 1 | 0 | 0.93 |
| 0.5 | B | 64 | 7 | 2 | 4 | 1.66 |
| 0.5 | B | 256 | 8 | 2 | 3 | 1.75 |
| 0.5 | B | 1024 | 8 | 1 | 3 | 1.79 |
| 0.7 | A | 64 | 5 | 3 | 1 | 0.56 |
| 0.7 | A | 256 | 7 | 4 | 1 | 0.89 |
| 0.7 | A | 1024 | 7 | 5 | 1 | 0.75 |
| 0.7 | B | 64 | 8 | 3 | 3 | 1.96 |
| 0.7 | B | 256 | 8 | 2 | 3 | 2.01 |
| 0.7 | B | 1024 | 8 | 3 | 3 | 2.01 |

Route B over all key-levels and n: chosen layer 0 or 1 in 43 of 96 cases (median perplexity ratio 2.3, median acceptance 59.0%); other layers in 53 cases (ratio 1.36, acceptance 97.0%).

Figures (generated by the same script): [`fig1_acceptance.png`](outputs/study1_v0.2/report/fig1_acceptance.png) (acceptance vs ρ, n = 256), [`fig2_quality.png`](outputs/study1_v0.2/report/fig2_quality.png) (exploratory: acceptance vs perplexity per key), [`fig3_recovery.png`](outputs/study1_v0.2/report/fig3_recovery.png) (Route A recovery vs n).

## 4. Unanticipated findings (EXPLORATORY: found after the run, not pre-registered)
1. **Forgery without key recovery.** Route B's vector has a median cosine of at most 0.054 with the true key (any level, any n), and it lands on the true layer for at most 3 of 8 keys, yet its forgeries are accepted at or above the oracle rate. Route A at ρ = 0.70 is similar (cosine ≈ 0, acceptance ≈ 90%). The owner's MLP probe accepts texts steered **at other layers and in other directions**.
2. **Many accepted forgeries are gibberish.** In 43 of 96 Route B cases the attack picked layer 0 or 1; steering there produces broken multilingual token soup (read directly: e.g. key 1001, ρ = 0.5), with perplexity in the hundreds, and the probe still accepts it (median 59%). When Route B picked another layer (mostly 14 or 17), acceptance was 97% (median) at a perplexity ratio of 1.36 to genuinely watermarked text, and the samples read like ordinary news continuations.
3. **Fluent and effective forgeries exist but are a minority of keys** under a cut-off chosen after the data (perplexity ≤ 1.5 × the key's oracle median): at *n* = 256, Route B gives 3 of 8 keys at ρ = 0.35, 2 of 8 at 0.50 and 2 of 8 at 0.70; Route A gives 4 of 8 at ρ = 0.70 (Table 4). A perplexity ratio below 1 can also mean repetitive text; the Route A layer-27 samples read as fluent but rambling.
4. **The probe is a detector of off-distribution activations more than of the key.** It accepts gibberish, accepts steering at other layers, and flags 3.6% of human continuations (3.6× its nominal 1% on model text). This fits a per-key MLP trained only on "steered vs unsteered" text.

**Inference (not evidence):** the security question for this watermark is less "can the key be stolen?" (no, by this estimator) and more "does the detector test the key?" (no, largely). An exact key-based test (Study 3) may reject these forgeries where the probe accepts them; that is the natural next test. A quality-aware attacker (choosing the layer by its own fluency check with the open model) would plausibly raise the fluent-forgery count; this is untested.

## 5. What is not claimed
Anything at 8B scale or on other models; that key recovery is impossible (only that this estimator fails within 1,024 texts); that the forgeries are fluent in general (only for the key counts in Table 4, under a post-hoc cut-off); results for SLAM-style designs, scrubbing, or the defence. Eight keys per level; perplexity under the unsteered model is a coarse quality proxy.
