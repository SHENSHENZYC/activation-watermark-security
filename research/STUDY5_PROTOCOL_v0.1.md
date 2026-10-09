# Study 5 — Context-keyed and rotating-key activation steering: stealability, paraphrase robustness and quality against the gradient-averaging attacker — protocol v0.1

Date: 2026-10-02. **Status: LOCKED before outcomes** (2026-10-02, approved by Yichen, decision 9). The lock record is `outputs/study5_v0.1/PRE_RUN_LOCK.json`: the SHA-256 of this file, the code, the reused Study 1, 2 and 3 files and the pilot inputs. Any change needs a new version (v0.2), and this file is never edited again. Script: `research/study5/run_s5.py`. Supersedes: none.
Paper role: the constructive contribution: about 3 figures (key recovery and forgery acceptance against n per arm; scrub success per arm beside the fixed key; the stealability–robustness–quality frontier) and 2 tables (rules against observed; detection, quality and union-test power per arm), plus the fixed key's re-attack as a Study 1-type result for the attack section.

## 0. Background (established before this protocol)
- **Studies 1–3** (LOCKED, reported): on Qwen2.5-1.5B, keys 1001–1008 at ρ ∈ {0.25, 0.35, 0.50, 0.70}, the exact key test S4 detects 96–100% of genuine 256-token texts at an exact 1% FPR; Study 1's Route A (an estimator on mean activations) fails at n ≤ 1,024 for the median key, and its forgeries pass S4 only for a few keys; Study 2: off-the-shelf paraphrase (P-Qwen) scrubs S4's evidence at ρ ≤ 0.35 but not at ρ ≥ 0.50.
- **The threat check** (tuning keys; `study5_pilot/THREAT_CHECK_SPEC_v0.1.md`, FIXED, 2026-10-02): Route A′, the same selection rule on the exact test's own gradient statistic averaged over the observed texts, recovers the fixed key with median cos 0.80 from 4 texts and 0.95 from 16 at ρ = 0.35, 0.93 from 64 at ρ = 0.50, 0.57 from 100 at ρ = 0.70.
- **The source gate** (`STUDY5_GATE_v0.1.md`, PASS as a transfer): context hashing and key rotation are standard token-level mechanisms with a known stealability–robustness trade-off; nothing measures them for activation steering; the scheme's authors name the rotating vector as future work.
- **Decisions 1–6** (Yichen, 2026-10-02; `DECISION_LOG.md`): the threat is Route A′; arms h = 1, h = 4 and rotation K = 8 beside the fixed key; ρ ∈ {0.35, 0.50}, 8 keys, n ∈ {64, 256, 1024}; the attacker is given the layer for the keyed arms; the full metric set; three rules with materiality thresholds and two gates; a tuning-key pilot first; budget 30 h with pre-set fallbacks.
- **The defence pilot** (tuning keys, `study5_pilot/DEFENCE_PILOT_SPEC_v0.1.md`, FIXED; `outputs/study5_pilot_v0.1/REPORT.md`): at ρ = 0.50 the keyed arms detect 96% (h = 1) and 94% (h = 4) of genuine texts with a perplexity ratio of 0.89 and 0.89 against the fixed key on the same prompts; the per-context attacker at 100 texts forges 5% and 0% (h = 4 estimates no context); paraphrase leaves 2% and 1% detected against the fixed key's 24% (scrub success 75% and 75% against 52%); rotation among 4 keys falls to a clustering attacker at 16 texts per key; the per-position test with h = 0 matches S4 within 10 points. The rates below come from this pilot.

## 1. Question and type
An adequacy check of a **transferred defence** (an applied evaluation, not a new watermark) on Qwen2.5-1.5B with Study 1's keys:
- **Q5a (stealing resistance).** Does keying the direction by the text's context (h = 1, h = 4) or rotating it among K = 8 keys stop the gradient-averaging attacker from forging the watermark at n ≤ 1,024 observed texts, where the fixed key is forgeable from tens of texts?
- **Q5b (robustness cost).** What does each keying cost in paraphrase robustness, measured as the change in scrub success of the same paraphraser on the same prompts and keys, relative to the fixed key (Study 2)?
- **Q5c (quality and detection cost).** What does each keying cost in text quality at the same strength, and in detection power (the union test for rotation; the per-position test for the hashed arms)?

## 2. Threat model
- **The attacker** holds the open model, n watermarked continuations (prompts from pool B, as Study 1), the scheme's public parameters (sparsity 4; h or K; the 256-token window), and its own data: 200 pool C unwatermarked references and their prompts, and its own strength scale (the median token norm at the layer over its references). For the keyed arms it is **given the layer** (decision 4: conservative for the defence). It never sees the secret, a detector output, the owner's reference texts or the evaluation's bars.
- **The owner** sees the text only (no prompt, no per-text metadata) and uses the keyed exact test (§5) with one secret per key; for rotation it tests the union of its K keys.
- **Not tested:** budgets above 1,024 texts (the token-level literature steals context-hashed schemes with about 30,000 responses); paraphrasers other than Qwen2.5-1.5B-Instruct; combined or adaptive attacks against the detector; the repeated-query removal attack against multiple keys (Pang et al. 2024); human editing.

## 3. The schemes (frozen; `keyed_core.py`)
- **Fixed (h = 0; the comparator).** Study 1's scheme and texts: one 4-sparse key (`core.make_key`, seed = the key), scaled to ρ · 56.90, added at every position of layer 14 during generation (prompt included).
- **Context-hashed (h ∈ {1, 4}).** At continuation position t ≥ h (0-based) the direction is a 4-sparse unit vector derived by a keyed PRF (splitmix64 mixing of the secret and the previous h token ids; 4 distinct coordinates; values uniform in [−1, 1), unit-normalised), scaled to ρ · 56.90; positions t < h and the prompt are not steered. The secret is the key's seed (1001–1008). Decoding and sampling as Study 1 (256 new tokens; temperature 0.7, top-p 0.9, top-k 50, repetition penalty 1.1).
- **Rotation (K = 8).** One of the 8 study keys per text, uniformly: the rotating-key corpus is the 8 keys' existing texts at each strength, interleaved (text j of key i at position 8j + i).

## 4. Keys, strengths, texts
Keys 1001–1008; ρ ∈ {0.35, 0.50}; layer 14. Prompts from C4 realnewslike dev only (the holdout stays sealed).

| Arm | Set | Prompts | Texts per key-level | Use |
|---|---|---|---|---|
| h = 1, h = 4 (new generation) | observed | pool B (the first 1,024, as Study 1) | 1,024 | the attacker's sample; nested n ∈ {64, 256, 1024} |
| | genuine | pool D's first 100 (Study 1's oracle prompts) | 100 | detection; quality, paired by prompt with Study 1's oracle texts; paraphrase |
| | forgeries | pool D's first 100 | 100 per n ∈ {64, 256, 1024} | D1 |
| | random-secret control | pool D's first 100 | 100 (control secrets 5001–5008) | generic keyed steering under a wrong secret |
| | paraphrases | — | 100 (P-Qwen of the genuine texts) | D2 |
| Fixed (existing texts) | observed, genuine (oracle), random-key control | Study 1 v0.2 | 1,024; 100; 100 | Route A′ re-attack; P0 |
| | forgeries | pool D's first 100 | 100 per n ∈ {64, 256, 1024} | P0 (new generation with Study 1's fixed hook) |
| | paraphrases | — | Study 2's P-Qwen paraphrases (existing, with their quality flags and S4 features) | D2's comparator |
| Rotation (existing texts) | corpus | the 8 keys' observed and oracle texts | 8,192; 800 | the mixture; union-test detection |
| | forgeries | pool D's first 100 | 100 per attacker (naive, clustering) and n ∈ {64, 256, 1024} | D1 (one corpus per strength) |
| | paraphrases | — | Study 2's P-Qwen paraphrases of the oracle texts | D2 (the union test's loss) |
| Shared | owner's reference | pool F (200 unwatermarked texts; Study 1) | 200 | standardisation of per-position and summed gradients |
| | null texts | pool A (1,000 unwatermarked; Study 1) | 1,000 | calibration gates (G1, G2) |
| | attacker's reference | pool C's first 200 (Study 1) | 200 | the attacker's standardisation and scale |
| | bars | Study 2's locked `bars.json` (owner A; attacker C) | — | the quality conditions |

## 5. Detector (owner, frozen)
- **Per-position keyed test (hashed arms).** For a text, the gradient of the continuation log-likelihood with respect to an additive vector at every position of layer 14 (one backward pass), standardised per dimension with pooled position statistics of pool F; S(x, m) = Σ_t ⟨x_t, v_m(c_t)⟩ over positions with a complete context; p = (1 + #{j : S(x, m_j) ≥ S(x, secret)}) / 1,000 over 999 public null secrets (seed 20261002); **detected** if p ≤ 0.01. Exact by secret resampling (on average over secrets, as Study 3's caveat).
- **Fixed arm.** Study 3's S4, unchanged (primary); the per-position form with h = 0 is reported beside it (secondary, for comparability).
- **Rotation.** On S4's transform, U = max_k ⟨x, v̂_k⟩ over the 8 study keys; the null = 999 disjoint groups of 8 keys from the 9,999 public null keys; detected if p ≤ 0.01. The "told which key" bound is Study 3's single-key result.
- **Fluency condition** (forgeries): perplexity given the prompt and seq-rep-4 at most the arm's own genuine texts' 95th percentiles at that key-level (Study 3's form).

## 6. Attacks (frozen)
- **Route A′ (fixed key).** Summed standardised gradients (the attacker's reference) at every layer; Study 1's Route A rule (layer by the largest |z|; support = the 4 largest |z|; values = the mean difference), with gradients in place of activations; also at the known layer 14. Nested n ∈ {64, 256, 1024}. Forgery: Study 1's fixed hook with v̂ at l̂ (or 14), scaled to ρ · N̂.
- **Route A′-h (hashed arms).** Per-position standardised gradients (the attacker's pooled position statistics), grouped by the observable context (the previous h token ids); contexts seen at least c_min = 16 times among the n texts; one 4-sparse estimate per context (the 4 largest |mean| coordinates; values = the mean), unit-normalised and scaled to ρ · N̂ at layer 14; snapshots at each n. Forgery: the stateful hook steering only estimated contexts.
- **Rotation.** Naive: Route A′ on the mixture. Clustering: spherical k-means (K = 8, 20 restarts, seed 20261003) on the unit standardised summed gradients, then Route A′ per cluster; the forgery uses the cluster estimate with the largest z-profile.
- **Recovery metrics:** cos(v̂, v) (fixed, rotation: with each key; the best key for clustering); for the hashed arms the count-weighted mean cosine over estimated contexts with the true per-context keys, the share of a genuine text's scored positions covered, and the number of contexts.

## 7. Metrics
- **Detection:** the share of genuine texts with p ≤ 0.01 (per arm, strength, key).
- **Forgery acceptance (FA):** accepted (p ≤ 0.01) and fluent (§5), per forgery set.
- **Scrub success** (per paraphrased text): not detected **and** Study 2's four quality conditions (fluency within max(1.25 × the original, P95 of pool A's human continuations) for perplexity and seq-rep-4; length ≥ 80%; all-mpnet-base-v2 cosine above pool A's same-prompt 95th percentile), with the owner's bars; the paraphrase uses Study 2's P2 prompt and the attacker's self-check (pool C bars), up to 3 attempts.
- **Quality:** the per-text perplexity ratio keyed/fixed on the same prompt and key, seq-rep-4 of both.
- Medians over keys; per-key counts beside every verdict.

## 8. Uncertainty
Keys are the replicates (K = 8). 95% intervals from a cluster bootstrap over keys, then texts (B = 2,000, seed 20261003), using v0.4's function; paired resampling for D2 (the same prompts and keys) and D3 (the same prompts).

## 9. Rules
**Gates.**
- **G1 (calibration):** the pooled FPR over 8 secrets × the 1,000 pool A texts is within [0.3%, 2.5%] for each hashed arm and for the union test; if it fails for an arm, that arm's analysis stops and is fixed in a new version.
- **G2 (per-key calibration):** a key is calibrated for an arm if its FPR on pool A is ≤ 3.0%; uncalibrated keys are excluded from that arm's verdicts and reported; with fewer than 6 of 8, the arm's verdicts are not made and Yichen decides.
- **P0 (the threat; per strength):** the fixed key under Route A′ is practical to forge (D1's form) at some n ∈ {64, 256, 1024}; where P0 fails, the defence verdicts at that strength are descriptive.
- **P1 (usability; per arm and strength):** the arm's median genuine detection is ≥ 50%; otherwise the arm is descriptive there.

**Primary rules** (per arm and strength passing P0 and P1; medians over calibrated keys; beside every verdict the number of keys meeting the bar):
- **D1, stealing.** A forgery set at n is **practical** if its median FA ≥ 50% of the arm's genuine FA **and** its lower 95% bound exceeds the random-secret (or random-key) control's upper bound. **Stealing blocked at n ≤ 1,024** if every n's upper bound is below 50% of the genuine FA; otherwise **inconclusive**. If the control reaches 50% of the genuine FA, "generic steering suffices" is reported instead.
- **D2, robustness cost.** Per key, d = scrub success of P-Qwen on the arm − the fixed key's Study 2 success (the same keys and prompts); the median of d with a paired bootstrap interval. A **material cost** if the lower bound > 0 and the median d ≥ 20 points; **immaterial** if the upper bound < 20 points; otherwise inconclusive. Study 2's absolute reading (success ≥ 50%: paraphrase effective) is reported beside it. For rotation, d is the union test's loss relative to the single-key test on Study 2's paraphrases.
- **D3, quality cost.** The median over keys of the per-key median perplexity ratio arm/fixed; **material** if the lower bound > 1.10; **immaterial** if the upper bound ≤ 1.10; otherwise inconclusive. Rotation: unchanged by construction (not tested).
- **Materiality:** 50% of the genuine FA (Study 3's bar); 20 points of scrub success (a fifth of texts changing between "evidence kept" and "evidence lost" changes a deployer's choice); a 10% perplexity ratio (within the calibration's quality band).

**Bounds checked at the extremes.** The FA bar is relative to the arm's own genuine FA, which is at most 100%, so "practical" is never automatic; if the genuine FA is below 20% the arm fails P1 in spirit and D1 is descriptive. The 20-point and 1.10 bars are absolute. The control condition cannot be met if the control's own FA is near the genuine's (then "generic steering suffices").

## 10. Secondary (descriptive)
Detection after paraphrase per arm with a paired contrast against the fixed key (Study 2's detection after paraphrase on the same prompts); the quality ratio read in both directions (a ratio below 1, as in the pilot, is an improvement); recovery curves against n (cosine; coverage; contexts; cosine by context count); the fixed key under Route A′ with the layer search beside the known layer; detection at p ≤ 0.05 and 0.10; four texts pooled; the per-position h = 0 form against S4; the tokenisation round-trip share; the "told which key" bound for rotation; stricter quality readings (the model-text 95th percentile; the human median); per-key tables; samples read (keys 1001 and 1002 at ρ = 0.50: the first genuine text of each arm, a forgery at n = 1,024, a paraphrase), quoted; timing.

## 11. Stop rules; what a null means
- G1 fails for an arm: stop that arm. P0 fails at both strengths: report; the defence verdicts are descriptive and the paper's attack claim is narrowed to the threat check.
- **"Stealing blocked at n ≤ 1,024"** means this attacker, at this budget, cannot forge the keyed watermark where it forges the fixed one; it is not immunity (the token-level literature steals context-hashed schemes with larger budgets).
- **"Material robustness cost"** means the keying removes a substantial part of the paraphrase robustness that motivates activation watermarks: the no-free-lunch trade-off carries over.
- **"Immaterial cost"** on both D2 and D3 with D1 "blocked" would mean the defence moves the trade-off; that claim is bounded by the attacker and paraphraser tested.

## 12. Inputs validated before the lock (no outcomes)
Reused files present and hashed (Study 1, 2, 3 and the pilot's references); the keyed hook reproduces Study 1's generation at h = 0 and replays its keys exactly (the pilot's I1 and I2); the keyed test's calibration on pool A (I3); the per-position form against S4 (I4); seeds disjoint from every earlier study; the runner refuses without a lock (tamper tests); a pipeline smoke test on tuning keys that asserts every field of §7–§10; a timing check with a budget of 30 h; **no study-key text is generated, attacked or paraphrased before the lock**.

## 13. Nearest work; what is not claimed
- **Nearest:** context hashing and its width trade-off (Kirchenbauer et al. 2023a, 2023b); multiple keys against stealing and their removal cost (Pang et al. 2024; Gu et al. 2024); watermark stealing budgets (Jovanović et al. 2024; Zhang et al. 2026); SLAM's per-document keying with metadata; Self-Recognition's rotating-vector future work; SynthID-Text's multi-key, 5-gram deployment.
- **Not claimed:** a new watermark; immunity to stealing; robustness to stronger paraphrasers or adaptive attacks; human-judged quality; other models, layers or key distributions; a fix of the trade-off (SEEK is a token-level fix); results for budgets above 1,024 texts.

## Compute (from the pilot's measured rates)
Keyed generation 1.16 s per text (batch 16), fixed generation 1.08 s, per-position features 0.14 s per text, all-layer summed gradients 0.27 s, Qwen paraphrase with retries and checks 3.5 s per original, quality 0.15 s per text. Decision 3's full scope: **about 26 h** in three checkpointed phases: K (keyed generation, the attacker, forgeries, controls, quality) about 18 h; P (paraphrase and scoring) about 3 h; F and R (the fixed key's re-attack and rotation) about 4 h; A seconds. Re-running a phase resumes from its checkpoints. One 1.5B model at a time (Qwen2.5-1.5B, then Qwen2.5-1.5B-Instruct with the base model for checks); no restart is needed. Pre-set fallbacks, in order, if the input validation's projection exceeds 30 h: (1) the h = 4 arm's observed set is 256 texts; (2) 50 paraphrases per key-level. The validation's projection decides which, if any, applies.

## For review (design calls made in drafting, beyond decisions 1–6; the pilot's readings changed none of them)
- Forgeries at every n ∈ {64, 256, 1024} for all arms (a possible first fallback: drop n = 64 forgeries for the hashed arms, where coverage is predicted tiny).
- The attacker's context threshold c_min = 16; the hashed arms' genuine texts on Study 1's oracle prompts (pool D) so that quality and scrubbing are paired by prompt.
- The per-position standardisation by pooled position statistics (pool F); the fixed arm keeps Study 3's S4 as primary.
- The owner's and attacker's bars reused from Study 2's locked `bars.json`.
