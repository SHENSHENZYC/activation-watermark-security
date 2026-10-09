# Study 1 — Key recovery and forgery along the detectability–quality curve of an activation-steering watermark — protocol v0.2

Date: 2026-09-26. **Status: LOCKED before outcomes** (2026-09-26, approved by Yichen). The lock record is `outputs/study1_v0.2/PRE_RUN_LOCK.json`; any change needs a new version (v0.3), and this file is never edited again. Supersedes: v0.1 (LOCKED 2026-09-25; stopped at gate G1; its result stands and v0.1 is never edited).
Paper role: the core result (key-recovery curves; forgery at a fixed FPR, by watermark strength), about 2 figures and 2 tables, plus the calibration scale figure.

## 0. What changed from v0.1, and why
v0.1 failed G1: at the paper's α = 5, Qwen2.5-1.5B showed no watermark under the training-free cosine. The reproduction pilot and calibrations v0.1–v0.3 (tuning keys only; `research/repro/`) then showed:
- raw α does not transfer across models, so strength is now **relative**: ρ = ‖v‖ / N, with N the median activation norm at the steered layer;
- the authors' actual detector is a **trained per-key MLP probe**, which works where the cosine does not;
- on 1B, 1.5B and 3B models, no strength is both reliably detectable (AUROC ≥ 0.95) and quality-neutral (perplexity ratio ≤ 1.25), at 256 or 512 tokens. Under the pre-committed follow-up, v0.2 **attacks along the trade-off curve** on Qwen2.5-1.5B.
Decisions (Yichen, 2026-09-26): levels ρ ∈ {0.25, 0.35, 0.50, 0.70}; the defender uses the authors' MLP at a fixed 1% FPR; two attack routes (key recovery and footprint imitation).

## 1. Question and type
**Adequacy (security) check of a published method family**, at four watermark strengths spanning the detectability–quality trade-off. A fixed secret sparse vector *v* is added to the residual stream at layer *l* during generation; the owner detects with a trained probe on re-encoded activations. An attacker has the open model and *n* watermarked texts.
- **Q1a (recovery).** Can they identify *l* and estimate *v*?
- **Q1b (forgery).** Can they generate new text that the owner's detector accepts, at a 1% false-positive rate, and does this require the key or does any steering suffice?

## 2. Threat model
- **Public (Kerckhoffs):** the model; the scheme (sparse key, *k* = ⌊0.003·*d*⌋ = 4 coordinates, uniform[−1, 1] values, a middle layer); the strength ρ; the detector's form (a per-key MLP probe on the steered layer's activations).
- **Secret:** *v* (support and values) and *l*; the owner's trained probe and its threshold.
- **The attacker sees** *n* watermarked continuations (text only, no prompts) and can generate unlimited unwatermarked text with the open model on its own prompts. **It cannot** query the detector or see *v*, *l* or the owner's activations.
- **The owner** knows *v* and *l*, generates its own training texts, and calibrates its threshold on its own unwatermarked texts.

## 3. Targets and units
- **Recovery (Route A):** cos(*v̂*, *v*); layer hit 1{*l̂* = *l*}; support hit |Ŝ ∩ supp(*v*)| / *k*.
- **Forgery:** the acceptance rate of attacker texts under the owner's detector at its 1%-FPR threshold.
- **Unit of independence:** the key; texts are nested in keys. Each key is used at all four levels (paired across levels).

## 4. Model, data, pools
- Qwen2.5-1.5B, revision `8faed761`, bf16 on MPS; *l* = 14; *k* = 4; N = 56.90 (the pilot's median unsteered norm at layer 14, `outputs/repro_v0.1/results_qwen.json`); keys rescaled to norm ρ·N with Self-Recognition's support and values (as in calibration).
- **Keys:** 8 study keys (seeds 1001–1008; never used before), each at ρ ∈ {0.25, 0.35, 0.50, 0.70}; random-control keys 5001–5008; tuning keys are not used.
- **Generation:** Self-Recognition's sampling settings; exactly 256 new tokens; features from the continuation only (BOS and padding excluded).
- **Prompts:** C4 realnewslike dev only (prompt sets v0.3; holdout sealed), pools by the v0.1 rank rule, plus a new pool F from the unused remainder:

| Pool | Size | Use |
|---|---|---|
| A | 1,000 | owner's unwatermarked null texts: A1 (first 500 by rank) sets the threshold; A2 (last 500) checks the FPR (G2); human continuations of A2: human-text FPR |
| B | 1,024 | prompts behind the attacker-observed watermarked texts (per key and level) |
| C | 2,000 | the attacker's own unwatermarked reference texts (shared) |
| D | 100 (first 100 of v0.1's D) | prompts for spoofs, oracle and random-key controls |
| E | 200 | owner's watermarked training texts (per key and level) |
| F | 200 (new, from the 2,072 dev units unused by v0.1 pools) | owner's unwatermarked training texts (shared) |

Unwatermarked sets (A, C, F) are generated once and shared by all keys and levels.

## 5. Detector (defender side, frozen)
- **Primary: the authors' MLP probe** (d → 2048 → 64 → 64 → 32 → 2, ReLU, softmax output with cross-entropy, Adam, lr 1e-3, batch 512, one epoch; raw activations; one sample per token), trained per key and level on the layer-14 token activations of pool E (watermarked) against pool F (unwatermarked). Text score = the mean over tokens of P(watermarked).
- **Threshold:** the 99th percentile of the scores of pool A1 (so the nominal FPR is 1%). A text is **accepted** if its score exceeds the threshold.
- **Secondary (descriptive):** D-cos with the true key, and its exact key-resampling p-value (M = 999), as in v0.1. (D-score is deferred to Study 3.)

## 6. Attacks (frozen)
Both routes use the attacker's own features: per text and layer, the mean over tokens of normalised re-encoded activations, for the *n* observed texts and the reference set C (*m* = 2,000), and z-scores as in v0.1 (reference-set sd, se = sd·√(1/*n* + 1/*m*)). The attacker's own strength scale: N̂_ℓ = the median token norm at layer ℓ over its reference texts.
- **Route A, key recovery (E-sparse, as v0.1):** *l̂* = argmax_ℓ max_i |z_{ℓ,i}|; support Ŝ = top-*k* by |z| at *l̂*; *v̂* = Δ on Ŝ, 0 elsewhere; rescaled to ‖*v̂*‖ = ρ·N̂_{*l̂*}.
- **Route B, footprint imitation (dense):** *l̂*_B = argmax_ℓ ‖z_ℓ‖₂; *v̂*_B = Δ at *l̂*_B over all coordinates; rescaled to ρ·N̂_{*l̂*_B}.
- **Forgery:** 100 continuations on pool D, steered by the route's vector at its layer; scored by the owner's detector.
- **Controls per key and level, on pool D (100 texts each):** **oracle** (the true *v* at *l*: the detector's TPR) and **random key** (a fresh key of the same distribution and norm at *l*: acceptance of *generic* steering).
- **Grid:** recovery at *n* ∈ {1, 4, 16, 64, 256, 1024} (nested prefixes of 1,024 observed texts); forgery at *n* ∈ {64, 256, 1024}.

## 7. Primary metrics
- **P1 (recovery, Route A):** median over keys of cos(*v̂*, *v*) and the layer-hit count, per level and *n*.
- **P2 (forgery):** median over keys of acceptance, per route, level and *n*, against the oracle (ceiling) and random-key (generic-steering) controls.

## 8. Secondary (descriptive)
Route B's cosine with *v*; support hit; per-layer z-profiles at *n* = 1,024; D-cos results; human-text FPR; forged-text quality (median perplexity under the unsteered model, ratio to oracle texts); acceptance against cos(*v̂*, *v*); detector AUROC on oracle vs pool A2.

## 9. Uncertainty
Keys are the replicates (K = 8). 95% intervals by a cluster bootstrap over keys, then texts (B = 2,000, seed 20260926); Clopper–Pearson for counts of keys. With 8 keys and 100 texts per condition, a per-key acceptance of 50% has a binomial SE of 5 points; if all 8 keys meet a criterion, the two-sided 95% Clopper–Pearson lower bound on the key-level rate is 0.63 (v0.1: 0.79 for 16 of 16).

## 10. Rules
**Validity gates (whole study):**
- **G1, null calibration:** the pooled FPR on pool A2 over all keys and levels is within [0.3%, 2.5%]. Fail → stop; the threshold machinery is broken.
- **G2, attack isolation:** asserted in code (the attack module receives only features; never *v*, *l*, the probe or the threshold).

**Per-level gate:**
- **L1, a working watermark:** the median oracle acceptance (TPR at 1% FPR) is ≥ 20%. Levels failing L1 are reported descriptively only ("too weak to forge meaningfully"). *(Calibration suggests ρ = 0.25 may fail; this is expected and fine.)*

**Primary rules (per level passing L1):**
- **R1, key recovery** (Route A) at the smallest *n* with median cos ≥ 0.9 **and** layer hit for ≥ 7/8 keys (*n\**); **fails at this budget** if no *n* ≤ 1,024 qualifies; **partial** if the median cos at 1,024 is in [0.5, 0.9).
- **R2, forgery is practical** (per route) if, at some *n* ≤ 256, the median acceptance is ≥ 50% of the median oracle acceptance **and** its lower 95% bound exceeds the random-key control's upper bound. **Not practical** if the median acceptance at *n* = 1,024 is below max(2 × the random-key median, 2%). Otherwise **inconclusive**.
- **R3, generic steering suffices** if the random-key median acceptance is ≥ 50% of the oracle median (the probe detects *steering*, not the *key*; forgery then needs no key). Reported alongside R2.
- **Materiality:** forged texts accepted at ≥ 50% of the genuine rate, at a 1% FPR, would make the watermark unreliable as evidence of provenance.

**Integrity checks (asserted in code):** pools disjoint and dev-only; A1 and A2 disjoint; study, control and tuning keys disjoint; *n*-prefixes nested; the detector's training texts (E, F) are disjoint from its threshold (A1), check (A2) and evaluation (D) texts; the attack receives features only.

## 11. Stop rules; what a null means
- **G1 fails:** stop; fix in a new version.
- **All levels fail L1:** the owner's detector does not work at 1% FPR at any tested strength; report; no attack claim.
- **A null** (R1 fails and R2 "not practical" for both routes, at levels passing L1) means these passive attacks with ≤ 1,024 texts do not forge this watermark at that strength. It is not a proof of security.

## 12. Inputs validated before the lock (no outcomes)
Pools (sizes, disjointness, dev-only, holdout sealed); keys (seeds, *k*, norms = ρ·N); the MLP training code on synthetic data (a planted signal detected, none not); the threshold rule on synthetic scores (FPR ≈ 1%); the attack module's isolation and a planted-signal recovery on synthetic features; hooks; a **timing check with a budget of 30 h**. No generation with study keys and no detector or attack statistic on model outputs before the lock.

## 13. What is not claimed
The first stealing attack on LLM watermarks; security or insecurity of activation watermarks in general or at 8B scale; results for SLAM-style designs (Study 4); scrubbing (Study 2); the defence (Study 5); results on other models (the 1B and 3B curves are calibration evidence only).

## Compute budget (projected; to be re-timed at validation)
Shared unwatermarked texts: A 1,000 + C 2,000 + F 200 = 3,200. Per key and level: observed 1,024 + owner training 200 + oracle 100 + random 100 + forgeries 2 routes × 3 *n* × 100 = 600, so 2,024; × 32 key-levels = 64,768. In total about 68,000 generations at about 1.07 s each (calibration timing), about **20 h**, plus re-encoding (all layers for B and C) and perplexity, about 2 h. Checkpointed phases across two or three overnight runs.
