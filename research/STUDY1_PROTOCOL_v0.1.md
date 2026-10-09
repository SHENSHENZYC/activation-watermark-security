# Study 1 — Key recovery and spoofing against a fixed activation-steering watermark — protocol v0.1

Date: 2026-09-25. **Status: LOCKED before outcomes** (2026-09-25, approved by Yichen). The lock record is `outputs/study1_v0.1/PRE_RUN_LOCK.json`: the SHA-256 of this file and of the code. Any change needs a new version (v0.2); this file is never edited again.
Script (to be written after design review): `research/study1/run_study1.py`. Supersedes: none.
Paper role: the core result (key-recovery curves; spoofing at a fixed FPR), about 2 figures and 2 tables. Scrubbing moves to Study 2 (see §12).

## 1. Question and type
**Adequacy (security) check of a published method family.** Under Self-Recognition's scheme (ICML 2026, arXiv 2606.06315), a fixed secret sparse vector *v* is added to the residual stream at one layer *l* during generation, and detection re-encodes the text with the same open model. Consider an attacker who has the open model and *n* watermarked texts.
- **Q1a.** Can they identify *l* and estimate *v* from those texts?
- **Q1b.** Can they then generate new text that the defender's detector accepts as watermarked (**spoofing**) at a fixed false-positive rate?

## 2. Information timing and threat model
- **Public (Kerckhoffs's principle):** the model weights; the scheme; its default hyperparameters (sparsity 0.3%, so *k* = ⌊0.003·*d*⌋ nonzero coordinates; values uniform[−1,1] × α with α = 5; "a middle layer"); the detector's form.
- **Secret:** the key *v* (its support and values) and the exact layer *l*.
- **The attacker sees:** *n* watermarked continuations (text only, **without prompts**); the attacker can generate any amount of unwatermarked text with the open model on its own prompts.
- **The attacker cannot:** query the detector, see activations from the defender's generation, or see *v*.
- **The detector** sees only the continuation text (prompt-agnostic setting) and uses the true (*l*, *v*).

## 3. Target, sign, units
- **Recovery:** cos(*v̂*, *v*) ∈ [−1, 1] (higher = better recovery), plus layer hit, 1{*l̂* = *l*}.
- **Spoofing:** the acceptance rate of attacker-generated texts under the defender's detector at p ≤ 0.01 (higher = more successful attack).
- **Unit of independence:** the **key**. Texts are nested within keys.

## 4. Data, split and holdout
- **Primary model:** Qwen2.5-1.5B, revision `8faed761` (28 layers, *d* = 1536, so *k* = 4); *l* = 14 (the middle, as in Self-Recognition); **16 keys**.
- **Pre-registered replication (decided 2026-09-25, before the lock):** Llama-3.2-1B, revision `4e20de36` (16 layers, *d* = 2048, so *k* = 6); *l* = 8 (the middle; Self-Recognition's public code does not give its 1B layer, so the paper's "middle layer" rule is applied); **8 keys** (the first 8 study seeds). Same pools, settings, gates and rules; the layer-hit criterion scales to ≥ 7/8. Results are reported per model; **Qwen is primary**. The two models are run with the same locked code (`--model qwen|llama`).
- Both models: bf16 on MPS. Re-encoding keeps a BOS token if the tokenizer adds one (Llama) but excludes it, and padding, from all token averages and from the log-likelihood targets.
- **Prompts:** the C4 realnewslike **dev** split only (prompt sets v0.3; 6,896 units), loaded through `research/stage4/prompts.py` (holdout sealed). Pools are assigned by `int(sha256(id + "|study1")[:8], 16)` rank order, disjoint and fixed in code:

| Pool | Size | Use |
|---|---|---|
| A | 1,000 | defender null set: unwatermarked generations (FPR check), and human continuations (human-text FPR) |
| B | 1,024 | prompts behind the attacker-observed watermarked texts (reused across keys; keys are independent) |
| C | 2,000 | the attacker's own unwatermarked reference generations |
| D | 200 | prompts for the attacker's spoof generations, and for the oracle and random-key controls |
| E | 200 | defender evaluation: watermarked generations (TPR) |
| T | 400 | Phase A reproduction tuning (tuning keys only) |

- **Generation settings (Self-Recognition defaults):** do_sample, temperature 0.7, top_p 0.9, top_k 50, repetition penalty 1.1; exactly 256 new tokens (min = max). Detection uses the first 256 tokens of the continuation.
- **Keys:** 16 study keys (seeds 1001–1016) and 4 tuning keys (seeds 9001–9004), generated as in Self-Recognition's `generate_noise` (a random support of size *k*, uniform[−1,1] values, × α).
- **The holdout is not used by Study 1.**

## 5. Competitors and baselines
**Detectors (defender side, frozen):**
- **D-cos (primary):** re-encode the continuation; at layer *l*, T = mean over tokens of cos(*h*ₜ, *v*). This is Self-Recognition's zero-shot statistic, averaged rather than majority-voted.
- **D-score (secondary):** S = ⟨*v*, *g*⟩ / (‖*v*‖·‖*g*‖), where *g* = ∇ log p(text) with respect to an additive vector at layer *l*. This is a GaussMark-style score statistic.
- **p-values for both, by exact key resampling:** p = (1 + #{*j*: T(*v*ⱼ) ≥ T(*v*)}) / (1 + M), with M = 999 fresh keys drawn from the public key distribution at layer *l*. Under H0 (the text is independent of *v*), p is exactly valid. Detection means p ≤ 0.01.
- Self-Recognition's trained MLP detector is deferred to Study 3 (the comparison of exact tests and classifiers).

**Attacks (frozen):**
- **Estimator E-sparse (primary):**
  - for each layer ℓ, compute the per-text mean of *normalised* re-encoded activations (*h*ₜ/‖*h*ₜ‖), for the *n* observed texts and for the attacker's reference set (pool C);
  - take z-scores per coordinate, z_{ℓ,i} = Δ_{ℓ,i} / (sd_ref,{ℓ,i}·√(1/*n* + 1/*m*)), using the reference-set standard deviation for both groups so that the rule is defined at *n* = 1 (*m* = 2,000);
  - *l̂* = argmax over ℓ of max over *i* of |z_{ℓ,i}|;
  - the support Ŝ is the top-*k* coordinates by |z| at *l̂*; *v̂*ᵢ = Δᵢ on Ŝ (Δ = the mean difference), and 0 elsewhere;
  - rescale to ‖*v̂*‖ = α·√(*k*/3), the expected key norm under the public distribution.
- **Estimator E-dense (secondary):** the same *l̂*; *v̂* = Δ over all coordinates, same rescaling. This uses no sparsity knowledge.
- **Spoof:** generate 200 continuations on pool D with the open model steered by *v̂* at *l̂* (same generation settings), then test them with D-cos and D-score using the **true** (*l*, *v*).
- **Controls, per key on pool D:**
  - **oracle**: steer with the true *v* at *l*, giving the TPR ceiling;
  - **random key**: steer with a fresh random key at *l*; expected acceptance about 1%.

**Grid:** *n* ∈ {1, 4, 16, 64, 256, 1024}, using nested prefixes of each key's 1,024 observed texts. Spoofing is run at *n* ∈ {16, 64, 256, 1024}.

## 6. Primary metrics and contrasts
- **P1 (recovery):** the median over the 16 keys of cos(*v̂*, *v*) (E-sparse) at each *n*, together with the layer-hit count.
- **P2 (spoofing):** the median over keys of the D-cos acceptance rate (p ≤ 0.01) of spoof texts, at each spoofing *n*, **contrasted with** the random-key control (floor) and the oracle (ceiling).

## 7. Secondary diagnostics (descriptive)
- D-score results for P2.
- E-dense recovery.
- Support recovery: |Ŝ ∩ supp(*v*)| / *k*.
- The per-layer drift profile max_i |z_{ℓ,i}| at *n* = 1,024, for every key.
- Human-text FPR (pool A human continuations).
- Spoof-text quality: perplexity under Phi-3.5-mini-instruct (revision `2fe19245`), the median ratio of spoof to oracle texts.
- Spoof acceptance as a function of cos(*v̂*, *v*).
- (The Llama-3.2-1B replication is now pre-registered in §4, not secondary.)

## 8. Uncertainty
- **Keys are the replicates** (K = 16).
- 95% intervals: a cluster bootstrap (B = 2,000; resample keys, then texts within keys; seed 20260925) for medians and acceptance rates.
- The number of keys meeting a criterion gets a Clopper–Pearson interval.
- Generation seeds are fixed per (pool, key, text index); all seeds are fixed now.
- **Nominal precision:** with 16 keys and 200 spoof texts per key, a per-key acceptance of 50% has a binomial SE of about 3.5 points. If all 16 keys meet a criterion, the lower 95% bound on the key-level success probability is 0.79.

## 9. Pre-registered rules and materiality thresholds
**Validity gates (all must pass, or the study is invalid and no attack claim is made):**
- **G1 — reproduction:** the Phase A tuning-key TPR (D-cos, p ≤ 0.01) on pool T is ≥ 80% at α = 5. If it is not, repeat once at α = 10 (the only allowed change). If still < 80%, **stop** (§10).
- **G2 — null calibration:** the D-cos FPR on pool A unwatermarked generations, using all 16 study keys, is within [0.3%, 2.0%]; the same for human continuations.
- **G3 — random-key control:** median acceptance ≤ 2%.
- **G4 — oracle:** median acceptance ≥ 80% (the evaluation-set TPR on pool E is reported alongside).

**Primary decision rules:**
- **R1, key recovery succeeds** at the smallest *n* on the grid where the median cos(*v̂*, *v*) ≥ 0.9 **and** the layer is hit for ≥ 87.5% of keys (14/16 for Qwen; 7/8 for Llama). This *n* is reported as *n\**. If no *n* ≤ 1,024 qualifies, recovery **fails at this budget**. A median cos in [0.5, 0.9) at *n* = 1,024 is reported as **partial**.
- **R2, spoofing is practical** if the median acceptance is ≥ 50% at some *n* ≤ 256 **and** the lower 95% bootstrap bound exceeds the random-key control's upper bound. **Not practical** if the median acceptance is < 10% at *n* = 1,024. Otherwise **inconclusive**.
- **Materiality:** a spoofing rate ≥ 50% at a 1% FPR is material for provenance use: half of forged texts would be attributed to the model.

**Integrity checks, asserted in code:**
- the pools are disjoint and drawn only from dev;
- the tuning keys are disjoint from the study keys;
- the detector uses the true (*l*, *v*), and the attack code never reads *v* or *l* (enforced by passing only texts to the attack module);
- *n*-prefixes are nested;
- 1 + M = 1,000, so p-values fall on a 1/1,000 grid.

## 10. Stop and pivot rules; what a null result means
- **G1 fails at α = 10:** the watermark does not reproduce on Qwen2.5-1.5B. Stop; report; decide between running on Llama-3.2-1B (the paper's own model) and changing the target (a new version).
- **G2 or G3 fails:** the detector or p-value machinery is broken. Stop; fix in a new version; no attack results are interpreted.
- **A null result** (R1 fails and R2 is "not practical") means that **this averaging attack**, with ≤ 1,024 texts, does not break a fixed sparse steering watermark on this model. That is evidence *for* the scheme against a natural passive attacker. It is **not** a proof of security: adaptive or query-based attacks remain untested.

## 11. Inputs validated before the lock (no outcomes)
- Pool assignment: sizes, disjointness, dev-only (and the holdout loader refuses).
- Key generation: reproducible from seeds, support size *k*, value range, norm distribution.
- **p-value machinery on synthetic Gaussian data** (not model outputs): uniformity under a simulated null (KS test), and the 1/1,000 grid.
- Hook mechanics: steering changes the logits, and removing the hook restores them (as in the pilot).
- Timing projection for the full run.
- The attack module's interface receives only texts; checked by a test.
- **No generation with study keys, and no attack or detection statistic on model outputs,** before the lock.

## 12. Nearest published work; what is not claimed
- **Nearest:** Self-Recognition (the scheme, which names the recovery risk without testing it); GaussMark (exact tests for weight perturbations); watermark stealing for token schemes (Jovanović et al. 2024; follow-ups); AWM (keyed activation directions for monitoring).
- **Not claimed:**
  - the first stealing attack on LLM watermarks;
  - security or insecurity of activation watermarks in general;
  - results on SLAM-style keyed designs (Study 4);
  - scrubbing (Study 2);
  - the defence (Study 5);
  - results at other model scales, beyond the Llama replication if run.

## Compute budget (projected from the pilot; to be re-timed)
Watermarked observed texts 16 × 1,024; evaluation 16 × 200; tuning 4 × 100; unwatermarked A and C 3,000; spoofs 16 × 4 × 200; controls 16 × 2 × 200. That is about 42,000 generations at about 1.66 s each, about 19 h, plus re-encoding (about 0.19 s per text over 28 layers) and backward passes for D-score on about 20,000 texts (about 0.74 s each). **About 25 h in total**, across two or three overnight runs, with checkpointed phases. *Re-timed at input validation (2026-09-25): Qwen at 1.08 s per generation (batch 16), 0.08 s per re-encoding, 0.37 s per gradient (batch 1), so **about 16 h**; see `outputs/study1_v0.1/qwen/INPUT_VALIDATION.json`. The Llama replication (8 keys) is timed at its own validation and projected to add about half as much again.*
