# Study 2 — Scrubbing an activation-steering watermark under the exact key test: paraphrase and key-guided edits at matched quality — protocol v0.1

Date: 2026-10-01. **Status: LOCKED before outcomes** (2026-10-01, approved by Yichen). The lock record is `outputs/study2_v0.1/PRE_RUN_LOCK.json`: the SHA-256 of this file, the code, the reused Study 1 and Study 3 files and the pilot inputs. Any change needs a new version (v0.2), and this file is never edited again.
Paper role: the scrubbing (robustness) result: about 2 figures (detection and scrub success after each method against ρ; success against the edit budget per arm) and 2 tables (rules vs observed; quality pass rates and calibration after paraphrase).

## 0. Background (established before this protocol)
- **Study 3** (LOCKED, reported): the owner's exact key test S4 detects 96–100% of genuine 256-token texts at an exact 1% FPR (median over 8 keys, ρ 0.25–0.70). All 8 keys are calibrated (FPR 0.1–1.7%), and Study 1's forgeries are not practical for the median key; a few keys leak.
- **Scrubbing pilots** (tuning keys only; [`study2_pilot/SCRUB_PILOT_REPORT_v0.1.md`](study2_pilot/SCRUB_PILOT_REPORT_v0.1.md), [`SCRUB_PILOT_REPORT_v0.2.md`](study2_pilot/SCRUB_PILOT_REPORT_v0.2.md)): paraphrase removed most of S4's evidence at low strength, and true-key 5% word edits did too; random edits did much less. The pilots also fixed four things:
  - the fluency normal range (the model-text bar rejected 94% of human text);
  - the edit judging point (10% edits pass perplexity bars while visibly degraded);
  - the editor's precision (float32);
  - the time (Phi needs batches of 4 and a clean machine).
- **Decisions** (Yichen, 2026-09-30 and 2026-10-01; `DECISION_LOG.md`):
  - methods §4; texts §3; quality §5; detectors and gates §7; rules §7;
  - Phi on 50 genuine texts per key-level; Phi in batches of 4;
  - edits judged at 5%;
  - the paraphrase prompt P2 (the pilot's rule A1); 5% edit rounds (the pilot's rule A2).

## 1. Question and type
An adequacy (security) check of the exact key test against **scrubbing at matched quality**, on Qwen2.5-1.5B with Study 1's keys and genuine texts:
- **Q2a (paraphrase without the key).** Can an attacker with an off-the-shelf paraphraser (Qwen2.5-1.5B-Instruct; Phi-3.5-mini-instruct) remove S4's evidence from genuine texts while keeping fluency, length and meaning?
- **Q2b (key-guided edits).** With the attacker's Study 1 estimate of the key (realistic), or with the true key (an insider upper bound on the damage from key leakage), how often do edits of 5% of the words remove the evidence, compared with random edits of the same size?

## 2. Threat model
- **The attacker** holds a watermarked continuation and its prompt, the open model, the scheme's public parameters (sparsity; the 256-token detector window), and its own data: Study 1's pool C references and the human continuations of their prompts. It never sees a detector output, the owner's reference texts (pool F) or the evaluation's bars.
- **P-Qwen, P-Phi:** no key.
- **E-est:** Study 1 v0.2's Route A estimate at n = 1,024 (its layer l̂ and 4-sparse vector v̂, as saved).
- **E-true:** the true key at layer 14, but not the owner's reference texts. It scales the direction with its own statistics.
- **E-rand:** random edits of the same size (control).
- **The owner** uses S4 exactly as in Study 3 and does not know whether a text was scrubbed.
- **Not tested:** attackers who query the detector, combine methods, or use larger paraphrasers.

## 3. Keys and texts (no new watermarked generation)
Study 1 v0.2's 8 study keys (seeds 1001–1008) at ρ ∈ {0.25, 0.35, 0.50, 0.70}, layer 14 (32 key-levels).
| Set | Source | Texts | Use |
|---|---|---|---|
| Genuine | v0.2 `K_*_oracle.json` (pool D), as scored in Study 3 | 100 per key-level (3,200) | scrubbed by Qwen paraphrase and every edit arm |
| Genuine, Phi | the first 50 of each key-level's oracle texts (pool D order) | 50 per key-level (1,600) | scrubbed by Phi paraphrase |
| Null | v0.2 `S_A_van.json` (pool A; prompts A1 + A2) | 1,000, shared | paraphrased by each model: calibration after paraphrase (G1, G2) |
| Reference | v0.2 `S_F_van.json` (pool F) | 200 | S4's standardisation only |
| Bars | pool A's prompts with their human continuations; pool A's model texts | 1,000 | the normal range and the meaning baseline (§5) |
| Attacker's data | the first 200 of v0.2 `S_C_ref.json` with their prompts and human continuations | 200 | the self-check bars; σ̂ at each layer the edits need |
| Owner's probe | v0.2 `K_*_mlp.pt` and thresholds | per key-level | secondary only |
The holdout is not used.

## 4. Scrubbing methods (frozen; pilot v0.1 §2 with pilot v0.2's editor; code `study2/` reusing `study2_pilot/scrub_core.py`)
### 4.1 Paraphrase (P-Qwen, P-Phi)
- The input is the continuation only. The prompt is **P2**: "Paraphrase the following text. Keep all of its information and meaning, but change the wording and sentence structure. Your paraphrase must be at least as long as the original text. Reply with the paraphrase only.\n\nText:\n{text}", in each model's chat template.
- Sampling: temperature 0.7, top-p 0.9, at most 400 new tokens. Batches sorted by length: 8 texts for Qwen, 4 for Phi. Seeds fixed per set, model and attempt (disjoint from the pilots').
- **The attacker's self-check, up to 3 attempts.** An attempt is kept if it meets the attacker's own versions of the four quality conditions (§5), computed with its pool C data:
  - perplexity ≤ max(1.25 × the original's, the 95th percentile over the human continuations of its 200 pool C prompts);
  - seq-rep-4 ≤ max(the original's, the same 95th percentile);
  - length ≥ 80% of the original's tokens;
  - embedding cosine > the 95th percentile of its 200 pool C pairs.

  Failing texts are retried with new seeds. If no attempt passes, the attacker keeps the one failing the fewest conditions (ties: the higher cosine, then the earlier attempt).
### 4.2 Edits (E-true, E-est, E-rand)
- **Text:** the first 256 tokens of the continuation (the detector's window). Edits replace **whole words**: an alphabetic token with a leading space, followed by a word boundary.
- **Candidates:** among the 40 most likely tokens at the position, whole words at least 1/3 as likely as the current word, other than it; the first 10 are kept.
- **Contributions:** c_t(y) = [log p₊(y) − log p₋(y)] / 2s, with ±s·ŵ added at the output of layer l (s = 2.0). The two passes run in **float32** (pilot v0.2: exact against the gradient). The unsteered distribution is the midpoint of the two passes' log-probabilities.
- **Direction:** w = v ⊘ σ̂_l, where σ̂_l is the standard deviation of the gradient at layer l over the attacker's 200 pool C references.
  - E-true: (v, 14);
  - E-est: (v̂, l̂) from Study 1 (σ̂ computed at l̂).
- **Each round:** the positions with the largest positive gain c_t(x_t) − min_y c_t(y), at least 2 apart from each other and from earlier edits, get their best candidate. Round size 5% of T, never overshooting the next budget.
- **Budgets:** the text is saved after **2%, 5% and 10%** of T.
- **E-rand:** the same rules, with random positions and random eligible candidates (seeded).

## 5. Metrics
- **Detected:** S4 p ≤ 0.01: x = (g − μ_F)/σ_F; T = cos(x, v); 999 null keys; first 256 tokens, no prompt. Identical to Study 3; Study 3's code is imported unchanged.
- **Quality conditions,** for a scrub *z* of an original *o* with prompt *q*:
  - **Fluency:** perplexity of *z*'s first 256 tokens under the unsteered model given *q* ≤ max(1.25 × *o*'s, P95_H); and seq-rep-4 ≤ max(*o*'s, P95_H). P95_H is the 95th percentile over the human continuations of pool A's 1,000 prompts (perplexity about 25.4, seq-rep-4 about 0.048 in the pilot).
  - **Length:** tokens(*z*) ≥ 0.8 × tokens(*o*) (*o* counted up to 256).
  - **Meaning:** all-mpnet-base-v2 cosine(*z*, *o*) > the 95th percentile of pool A's 1,000 same-prompt pairs (model text vs human continuation; about 0.825 in the pilot).
- **Scrub success** (per text): not detected **and** all four conditions pass. A method's success at a key-level is the share of its genuine texts that succeed. Summaries are medians over calibrated keys (§7).
- **Comparison for paraphrase:** the originals' own miss rate (p > 0.01; an unscrubbed text meets the quality conditions trivially). **Comparison for edits:** E-rand at the same budget.

## 6. Uncertainty
Keys are the replicates (K = 8). 95% intervals come from a cluster bootstrap over keys, then texts (B = 2,000, seed 20261001), using v0.4's function. Contrasts use paired resampling.

## 7. Rules
**Gates:**
- **G1, per paraphraser (implementation):** the pooled FPR over 8 keys × the 1,000 paraphrased pool A texts is within [0.3%, 2.5%]. If it fails, stop that paraphraser's analysis; it is fixed in a new version.
- **G2, per paraphraser (per-key calibration after paraphrase):** a key is calibrated for that paraphraser if its FPR on the 1,000 paraphrased pool A texts is ≤ 3.0%. Uncalibrated keys are excluded from that paraphraser's verdicts and reported descriptively. With fewer than 6 of 8 calibrated, that paraphraser's verdicts are not made, and Yichen decides.
- **Edits:** the edit arms use Study 3's calibration (all 8 keys calibrated on unparaphrased text).
- **P1, per level:** before scrubbing, the median S4 detection of the genuine texts is ≥ 20% (Study 3: 96–100%). Levels failing P1 are descriptive only.

**Primary rules** (per level passing P1; medians over the calibrated keys; beside every verdict, **the number of keys with success ≥ 50%**):
- **S1, paraphrase removes the evidence** (per paraphraser):
  - **effective** if the median success ≥ 50% **and** its lower 95% bound exceeds the upper 95% bound of the originals' miss rate;
  - **not effective** if the upper 95% bound is < 50%;
  - otherwise **inconclusive**.
- **S2, key-guided edits remove the evidence at 5%** (E-true and E-est separately):
  - **effective** if the median success at 5% ≥ 50% **and** its lower 95% bound exceeds E-rand's upper 95% bound at 5%;
  - **not effective** if the upper 95% bound is < 50%;
  - otherwise **inconclusive**.
- **C1, does the attacker's estimate help?** Per key, d = success(E-est) − success(E-rand) at 5%; the median of d with a paired bootstrap 95% interval. **The estimate helps** if the lower bound is > 0; **it hurts** if the upper bound is < 0; otherwise **no clear difference**.
- **Materiality:** success ≥ 50% means that, for the typical key, the watermark no longer gives provenance evidence for at least half of the scrubbed texts at matched quality.

**Bounds checked at the extremes:**
- The 50% bar is absolute, so it cannot become automatic.
- The paraphrase comparison (the originals' miss rate, 0–4% in Study 3) is far below the bar.
- If E-rand itself reaches 50% at a level, the edit arms cannot be "effective" there. That case is reported as "random edits suffice".
- The fluency allowance max(1.25 × original, P95_H) is never below the original's own perplexity, so an unscrubbed text always passes.

## 8. Secondary (descriptive)
- **Edit curves:** 2% and 10% budgets for every arm (success, detection, quality); E-rand's own rates; the attacker's objective.
- **Paraphrase:** first-attempt-only results; the attempts used; the share of kept attempts still failing the attacker's check.
- **Stricter quality readings:** success with the normal range set at the model-text 95th percentile, and at the human median.
- **Length-matched control:** each original truncated to its paraphrase's token count and scored with S4. This separates "less text" from "evidence removed".
- **The owner's probe** on the same scrubs (acceptance at its 1% threshold, paired with S4), and its FPR on the paraphrased pool A2 texts.
- **S4 at p ≤ 0.001** (9,999 null keys); 4 scrubbed texts pooled per test.
- **Calibration after paraphrase:** each study key's FPR, and the share of 1,000 fresh public-distribution keys above 3%, per paraphraser.
- **Key leakage:** E-est success against the estimate's cosine with the key, per key-level.
- **Samples read:** keys 1001 and 1002 at ρ = 0.50, the first pool D text: each paraphrase, and each edit arm at 5% and 10%, quoted in the report.
- Timing.

## 9. Stop rules; what a null means
- G1 fails for a paraphraser: stop that paraphraser's analysis; it is fixed in a new version. P1 fails at every level: report, with no scrubbing claim.
- **"Not effective"** means these attackers, at matched quality, leave S4's evidence in most of the typical key's texts. It is not a proof against larger paraphrasers (for example DIPPER-XXL), combined or adaptive attacks, or human editing.
- **"Effective" for paraphrase** means S4's evidence does not survive off-the-shelf paraphrasing at matched quality. That is consistent with the limit that meaning-preserving attacks place on any watermark (PASA; cited as a remark).
- **"Effective" for E-true but not E-est** means the protection depends on key secrecy: whoever holds the key can remove the watermark cheaply.

## 10. Inputs validated before the lock (no outcomes)
- Reused files present and hashed (equal to the Study 1 and Study 3 locks where recorded).
- The bars recomputed with the Study 2 code equal the pilot's.
- The S4 path reproduces **Study 3's** per-text p-values for the oracle texts of two key-levels exactly. These are already-reported outcomes; no new statistic.
- E-est: the 32 key-levels' estimates load (layer, vector, recorded cosine); σ̂ computed at every needed layer.
- The float32 editor matches autograd on unwatermarked texts.
- Seeds disjoint from all earlier seeds.
- The runner refuses without a lock; tamper tests.
- A **pipeline smoke test on tuning-key texts** that asserts every field of §7 and §8 is produced.
- A timing check with a budget of **30 h** (two checkpointed phases).
- **No study-key text is paraphrased or edited before the lock.**

## 11. Nearest work; what is not claimed
- **Nearest:** Self-Recognition's robustness check (DIPPER-XXL paraphrase against its trained probe: F1 from 99.1 to 89.3; no fixed FPR); PASA (the meaning-level limit); paraphrase and edit attacks on token-level watermarks (for example DIPPER; the reliability studies). This is the first scrubbing evaluation of an activation-steering watermark under an exact, per-key-calibrated test, with an insider bound from key-guided edits.
- **Not claimed:**
  - robustness to stronger paraphrasers or to adaptive attacks;
  - human-judged fluency (perplexity and repetition are proxies; samples are read);
  - other models, layers or schemes;
  - that perplexity bars catch every degradation (the stricter readings and samples are reported because they do not).

## Compute (projected; pilot v0.2's I5′)
Projected **24.3 h** (pilot v0.2, check I5′). **Phase 1, paraphrase, about 13.9 h:** Qwen 3.8 h on the full grid and Phi 10.1 h on 50 texts per key-level, with about 1.64 attempts per original under P2. **Phase 2, about 10.4 h:** edits 5.6 h (E-true 2.3, E-est 2.3, E-rand 1.0; float32 editor), scoring 4.6 h, and σ̂ at the estimate layers 0.2 h. Two checkpointed phases. Phase 1 (paraphrase) needs a freshly restarted Mac with other apps closed (Phi needs about 11 GB). Phase 2 (edits, scoring, analysis) needs about 10 GB.
