# Study 3 — Exact key tests for an activation-steering watermark: power, per-key calibration and resistance to Study 1's forgeries — protocol v0.1

Date: 2026-09-30. **Status: LOCKED before outcomes** (2026-09-30, approved by Yichen). The lock record is `outputs/study3_v0.1/PRE_RUN_LOCK.json`: the SHA-256 of this file, the code, the 562 reused Study 1 files and the human texts. Any change needs a new version (v0.2); this file is never edited again. Supersedes: none.
Paper role: the exact-test result: about 2 figures (detection against ρ, exact test vs the owner's probe on the same texts; forgery acceptance under the probe vs the exact test) and 2 tables (rules vs observed; per-key calibration).

## 0. Background (established before this protocol)
- **Study 1** (v0.2–v0.4, closed): the owner's trained MLP probe accepts forgeries made without the key. Route B footprint imitation was practical at every working level in v0.2 (plain acceptance) and, with fluency and repetition conditions, at ρ = 0.35 in v0.4. Generic steering (a random key) was accepted at 55.5% at ρ = 0.70 in v0.2. Inference then: the probe detects *steering*, not *the key*.
- **Power pilot v0.1** (tuning keys 9001–9004 only; [`study3_pilot/POWER_PILOT_REPORT_v0.1.md`](study3_pilot/POWER_PILOT_REPORT_v0.1.md)): a gradient-based key statistic with an exact key-resampling p-value detects single 256-token texts at 94–98% (median) at ρ 0.35–0.70, and texts steered by another key at about 1%. Key resampling is exact on average over keys, not per key; the standardised gradient (S4) kept every one of 1,000 random keys near 1% (max 4.75%). Yichen chose **S4** as the primary (2026-09-30).
- Decisions for this protocol (Yichen, 2026-09-30): the text sets (§4); M = 999 at 1% (primary) and M = 9,999 at 0.1% (secondary); the forgery rule is v0.4's F1 with the exact test in place of the probe (§7).

## 1. Question and type
A **statistical tool** (a transfer of GaussMark's score test from a weight perturbation to an additive activation vector, with key-resampling p-values), and an **adequacy check** of Study 1's forgeries against it. On Qwen2.5-1.5B, with the Study 1 keys and texts:
- **Q3a (power).** Does the owner's exact key test detect genuine watermarked text at a 1% false-positive rate, and how does it compare with the owner's probe **on the same texts**?
- **Q3b (calibration).** Is its false-positive rate near 1% for each fixed key, on unwatermarked model text and on human text?
- **Q3c (forgery resistance).** Does it accept the forgeries of Study 1, which were made without the key?

## 2. Threat model
As Study 1 v0.2–v0.4. The owner knows the key *v* and the layer *l* = 14. The exact test needs **no training**: its only data are the owner's own unwatermarked texts (pool F, 200) for standardising coordinates. The forgeries are **fixed texts from Study 1**: those attackers did not know the owner's detector (probe or exact test) and did not adapt to it. An attacker who knows the exact test and adapts to it is **not tested** here.

## 3. The test (frozen)
- **Per text** (continuation only, its first 256 tokens, no prompt; one forward and one backward pass at batch 1; bf16 on MPS; the pilot's `text_features`, imported unchanged): **g** = the gradient of the summed continuation log-likelihood with respect to an additive vector *b* at the output of decoder layer 14, at *b* = 0.
- **Primary statistic, S4:** x = (g − μ_g) / σ_g per coordinate, μ and σ (ddof 1) over the 200 pool F texts; T(x, v) = ⟨x, v⟩ / (‖x‖·‖v‖).
- **Exact p-value:** p = (1 + #{j : T(x, v_j) ≥ T(x, v)}) / (1 + M), M = 999 null keys (`core.null_keys`: seeds 77,700,000 + *j*; the set the pilot validated). A text is **accepted** (attributed to the key) if p ≤ 0.01.
- **Secondary statistics:** S3 (x = g, unstandardised); S4 at p ≤ 0.001 with M = 9,999 null keys (seeds 77,700,000 + *j*, *j* < 9,999; the first 999 are the primary set).

## 4. Keys and texts (no new generation)
Study 1 v0.2's 8 study keys (seeds 1001–1008) at ρ ∈ {0.25, 0.35, 0.50, 0.70} (32 key-levels; *l* = 14; keys of norm ρ·N). Every text is re-scored from Study 1's saved files; the SHA-256 of each is recorded in the lock.

| Set | Source (Study 1 data) | Texts | Use |
|---|---|---|---|
| Reference | v0.2 `S_F_van.json` (pool F) | 200, shared | standardisation only; never evaluated |
| Null, model | v0.2 `S_A_van.json` (pool A = A1 + A2) | 1,000, shared | per-key calibration (G1, G2) |
| Null, human | human continuations of pool A (prompt loader) | 1,000, shared | human-text FPR (H1) |
| Genuine | v0.2 `K_*_oracle.json` (pool D) | 100 per key-level | TPR; the probe's evaluation texts (E1) |
| Genuine | v0.2 `K_*_E.json` (pool E) | 200 per key-level | TPR on a larger set (secondary) |
| Generic steering | v0.2 `K_*_random.json` (pool D) | 100 per key-level | random-key control |
| Forgeries v0.2 | `K_*_forge_{A,B}_n{64,256,1024}.json` | 600 per key-level, 4 levels | secondary |
| Forgeries v0.3 | `K_*_forge3_{A,B}_n{64,256}.json` | 400 per key-level, ρ ≥ 0.35 | secondary |
| **Forgeries v0.4** | `K_*_forge4_{A,B}_n{64,256}.json` | 400 per key-level, ρ ≥ 0.35 | **primary (X1)** |

About 53,200 scored texts. The owner's probe scores and thresholds for the same texts are read from Study 1's locked outputs (for E1 and the paired secondaries). The holdout is not used.

## 5. Metrics
- **Accepted:** p ≤ 0.01 under S4. **Fluent:** v0.4's definition, computed with v0.4's code unchanged: perplexity (unsteered model, given the prompt) ≤ the key-level oracle's 95th percentile **and** seq-rep-4 ≤ the key-level oracle's 95th percentile (the bars at ρ = 0.25 are computed the same way from v0.2's oracle texts there).
- **TPR:** the share of a key-level's oracle texts accepted. **Exact-FA:** the share of a condition's texts that are accepted **and** fluent. Both summarised as the median over keys (calibrated keys only, §7 G2).
- **Probe acceptance** on the same texts: Study 1's rule (score > the key-level's 1%-FPR threshold).

## 6. Uncertainty
Keys are the replicates (K = 8). 95% intervals by a cluster bootstrap over keys, then texts (B = 2,000, seed 20260930), with v0.4's function. For the paired comparison E1 the same resample of keys and texts is used for both detectors. Per-key FPRs on 1,000 texts: binomial SE about 0.3 points at 1%.

## 7. Rules
**Gates (whole study):**
- **G1, implementation:** the pooled FPR over the 8 keys × 1,000 unwatermarked pool A texts is within [0.3%, 2.5%]. Fail → stop; the code is wrong.
- **G2, per-key calibration:** a key is **calibrated** if its FPR on the 1,000 unwatermarked pool A texts is ≤ 3.0%. (At a true 1%, exceeding 3.0% on 1,000 texts is a > 6 SE event.) Uncalibrated keys are excluded from P1, X1, X3 and E1 and reported descriptively. If fewer than 6 of 8 keys are calibrated, stop and bring the choice to Yichen.

**Per-level gate:**
- **P1, a working exact test:** the median oracle TPR ≥ 20% (the bar the probe had in Study 1 v0.2, L1). Levels failing P1 are descriptive only.

**Primary rules (per level passing P1; v0.4's forgeries at ρ ∈ {0.35, 0.50, 0.70}; identical in form to v0.4's F1 and F3):**
- **X1, fluent forgery is practical against the exact test** (per route) if, at some *n* ∈ {64, 256}, the median exact-FA ≥ 50% of the oracle's median exact-FA **and** its lower 95% bound exceeds the random-key exact-FA's upper 95% bound. **Not practical** if, at both *n*, the upper 95% bound is below 50% of the oracle's median exact-FA. Otherwise **inconclusive**.
- **X3, fluent generic steering suffices against the exact test** if the random-key median exact-FA ≥ 50% of the oracle's median exact-FA. (By construction the random key is independent of the true key, so about 1% acceptance is expected; X3 checks it.)
- **E1, power against the probe** (every level, calibrated keys): per key, d = TPR(exact) − TPR(probe) on the same 100 oracle texts; the median of d with a paired bootstrap 95% interval. **Exact test more powerful** if the lower bound > 0; **less powerful** if the upper bound < 0; otherwise **no clear difference**.
- **Materiality** (as v0.4): fluent forgeries accepted at ≥ 50% of the genuine fluent rate, at a 1% FPR, make the watermark unreliable as provenance evidence. Read with Study 1: a route that is "practical" against the probe and "not practical" against the exact test is blocked by testing the key.

**Bounds checked at the extremes (lesson from Study 1):** the X1 bar is 50% of the oracle's exact-FA, at most 50% (it cannot exceed 100%); P1 guarantees an oracle TPR of at least 20%, so the bar is positive; X3 cannot pass automatically because the random-key rate is compared with the oracle's, not with a multiple of itself.

**Integrity (asserted in code):** every reused file hashes as recorded in the lock (and, for Study 1's data, as in the Study 1 locks); pool F is disjoint from every evaluated set; the null-key seeds are disjoint from all study, control, tuning, validation, pilot-diagnostic and synthetic seeds; the fluency bars reproduce v0.4's locked bars exactly at ρ 0.35–0.70; the probe acceptance recomputed from saved scores reproduces Study 1's locked medians exactly.

## 8. Secondary (descriptive)
- **H1, human text:** per-key FPR on the 1,000 human continuations (and the number of keys above 3.0%), pooled human FPR; the probe's human FPR (v0.2: 3.6%) beside it.
- Plain acceptance under the exact test of every set (oracle, E, random key, each forgery set at each *n*); exact-FA of v0.2's and v0.3's forgeries in X1's form (v0.2's at ρ = 0.25 too).
- **Probe vs exact on the same texts:** acceptance by each, both, and either, per set; the FPR of "both" and "either" on pool A2 (the probe's own check set).
- S3 in place of S4 for the headline numbers (G1, G2, TPR, X1's quantities); S4 at p ≤ 0.001 (M = 9,999).
- **Key leakage lens:** the distribution of forgeries' p-values (share with p ≤ 0.05 and ≤ 0.10); Route A exact acceptance against the attacker's cos(v̂, v) per key; forgeries pooled 4 at a time (25 batches per condition) with the same null keys.
- The genuine TPR on pool E; per-key TPRs; timing.

## 9. Stop rules; what a null means
- **G1 fails:** stop; fix in a new version.
- **Fewer than 6 calibrated keys (G2):** stop; Yichen decides (for example, per-key empirical thresholds as a new version).
- **Every level fails P1:** the exact test does not work on the study keys; report; no forgery claim.
- **Reading X1.** "Not practical" means these **passive** forgeries, made without the key and without knowledge of the exact test, are rejected by it. It is not a proof against an attacker who adapts to the gradient test. "Practical" would mean that Study 1's forgeries carry key-specific signal, that is, key leakage through the attack.

## 10. Inputs validated before the lock (no outcomes)
Reused files present and hashed, and equal to the Study 1 locks' hashes where those exist; pool F features recomputed with the Study 3 code equal the pilot's (the same function on the same texts); null keys (the first 999 of the 9,999 equal `core.null_keys`; seeds disjoint); p-values on synthetic data (uniform under a simulated null; on the grid; planted signal detected); v0.4's fluency bars reproduced exactly from the saved texts; Study 1's probe acceptance medians reproduced exactly from the saved scores; the runner refusing without a lock, and tamper tests; a **pipeline smoke test on tuning-key texts** (key 9001 at ρ = 0.50 and its unwatermarked texts standing in for the study sets) that asserts every field of §7 and §8 is produced; a timing check with a **budget of 5 h**. **No exact-test statistic, and no study feature, on any study-key text before the lock.**

## 11. Nearest work; what is not claimed
- **Nearest:** GaussMark (the exact score test for a weight perturbation; this study transfers its statistic to an additive activation vector and uses key resampling because the keys are sparse, not Gaussian); Self-Recognition (the scheme; its detector is the trained probe; no p-values).
- **Not claimed:** security against adaptive attackers; per-key exactness in general (G2 checks it empirically for these keys); results on other models, other layers, SLAM-style keyed designs (Study 4), scrubbing (Study 2) or the defence (Study 5); that the gradient statistic is new (it is GaussMark's statistic, transferred).

## Compute
About 53,200 texts × 0.21 s (pilot timing) ≈ **3.1 h** for gradients, plus perplexity-free statistics (dot products with 1,000 or 10,000 keys: minutes). Checkpointed per file.
