# Study 1 — Repetition-aware forgery of an activation-steering watermark — protocol v0.4

Date: 2026-09-27. **Status: LOCKED before outcomes** (2026-09-28, approved by Yichen). The lock record is `outputs/study1_v0.4/PRE_RUN_LOCK.json`; any change needs a new version (v0.5), and this file is never edited again. Builds on v0.3 (LOCKED 2026-09-27; run and reported, [`STUDY1_REPORT_v0.3.md`](STUDY1_REPORT_v0.3.md)) and v0.2 (LOCKED 2026-09-26; reported). Their protocols, code, data and results are **reused read-only and never edited**, and their verdicts stand.
Paper role: the forgery result with a quality guarantee that includes repetition (1 figure, 1 table). If v0.4 is run, it replaces v0.3 as the evidence for or against "fluent forgery without the key"; v0.3 stays as the perplexity-only result.

## 0. Why v0.4
v0.3's pre-registered fluency rule was perplexity only. Exploratory analysis (labelled in the v0.3 report, §4) showed that repetitive loops have *low* perplexity: at ρ = 0.70, 80–90% of Route B's "fluent accepted" texts were repetitive, and the attacker's perplexity check kept choosing layers 0–2. v0.4 asks v0.3's question again with a repetition term on **both** sides (the attacker's check and the success rule), fixed before any v0.4 outcome. Decisions (Yichen, 2026-09-27): token seq-rep-4 in the rule; the attacker allows at most 2 repetitive trials in 16; v0.3's scope with new seeds.

## 1. Question and type
Adequacy (security) check, continued. **Q1d (fluent, non-repetitive forgery):** with the open model and *n* watermarked texts, can an attacker who screens its own candidates for perplexity **and repetition** produce texts that the owner's detector accepts at a 1% FPR **and** that are no less fluent and no more repetitive than the owner's own watermarked texts?

## 2. Threat model (as v0.3 §2)
The attacker generates with the open model on its **own** prompts and scores its own and observed texts: continuation-only perplexity (as v0.3) and seq-rep-4 (§4). It cannot query the detector or see *v*, *l*, the probe, its threshold or any evaluation prompt.

## 3. Reused (read-only; hashed in the lock)
- **From v0.2 (the same 243 files as the v0.3 lock):** per key and level, the owner's probe (`K_*_mlp.pt`), threshold, oracle and random-key texts on pool D with scores and perplexities (`K_*_summary.json`, `K_*_oracle.json`, `K_*_random.json`), the observed texts and features, v0.2's forgery texts at n ∈ {64, 256}; shared: the attacker's pool C references (`S_C_ref*`).
- **From v0.3 (secondary only):** per key and level, `K_*_v03.json` (scores, perplexities, selections) and the forged texts `K_*_forge3_{A,B}_n{64,256}.json` (120 files).
- Model, keys (1001–1008), layer 14, k = 4, N, pools, sampling and the 5-candidate search: as v0.3 (`attack3.candidates`, unchanged).
**Integrity check (asserted before any new outcome is scored):** as v0.3, the reloaded probes re-score v0.2's oracle texts within 1e-4 at every key-level.

## 4. Attack (frozen)
**seq-rep-4** (Welleck et al., 2019, arXiv 1908.04319): for a text, take its continuation's model tokens (the first 256, as for perplexity); seq-rep-4 = 1 − (distinct 4-grams / all 4-grams); 0 if it has fewer than 4 tokens.
For each key, level ρ, *n* ∈ {64, 256} (the first *n* observed texts) and route R ∈ {A, B}:
1. **Candidates:** as v0.3 §4.1 (the route's 5 strongest footprint layers; the route's estimate at each, rescaled to ρ·N̂_ℓ).
2. **Attacker's references:** *q*_obs = the median continuation-only perplexity of the *n* observed texts (as v0.3); *r*_obs = the **95th percentile of seq-rep-4** over the *n* observed texts.
3. **Trials:** 16 trial texts per candidate on the first 16 prompts of pool C (same prompts and seed for every candidate, **new seed**); *q*_ℓ = their median continuation-only perplexity; *m*_ℓ = the number of trials with seq-rep-4 > *r*_obs.
4. **Selection:** keep candidates with *q*_ℓ ≤ 1.2 × *q*_obs **and** *m*_ℓ ≤ 2. Use the kept candidate with the largest profile. If none is kept, use the candidate with the smallest *m*_ℓ, ties broken by the smaller *q*_ℓ (recorded as "no candidate passed").
5. **Forgery:** 100 continuations on pool D, steered by the selected vector at the selected layer, **new seeds**, scored by the owner's v0.2 probe and threshold.
Seeds: per key-level base as v0.2/v0.3; trials base + 60; forgeries base + 70 + 3·route + n-index (disjoint from v0.2's {1–4, 10–15} and v0.3's {20, 21, 23, 24, 50}; asserted in validation). The attack module receives only features, its own and observed texts' perplexities and seq-rep-4 values, and public parameters (asserted in code).

## 5. Targets and metric
- **Per text:** *accepted* = score > the owner's threshold; *fluent* = perplexity (unsteered model, **given its prompt**, as v0.2/v0.3) ≤ the key-level's oracle 95th percentile **and** seq-rep-4 ≤ the key-level's oracle 95th percentile of seq-rep-4 (v0.2's 100 genuine watermarked texts on pool D).
- **Primary metric FA (fluent acceptance):** the share of a condition's 100 texts that are both accepted and fluent; the median over 8 keys, per route, level and *n*.
- **Controls (v0.2 texts, same definition):** oracle FA (the ceiling; at most 95% plus ties, and lower where the two bars flag different texts) and random-key FA.

## 6. Uncertainty
As v0.3: keys are replicates (K = 8); 95% intervals by a cluster bootstrap over keys, then texts (B = 2,000, seed 20260928).

## 7. Rules (per level; unchanged in form from v0.3)
- **F1, fluent forgery is practical** (per route) if, at some *n* ∈ {64, 256}, the median FA ≥ 50% of the oracle's median FA **and** its lower 95% bound exceeds the random-key FA's upper 95% bound.
- **Not practical** if, at both *n*, the upper 95% bound of FA is below 50% of the oracle's median FA. Otherwise **inconclusive**.
- **F3, fluent generic steering suffices** if the random-key median FA ≥ 50% of the oracle's median FA.
- **Materiality:** as v0.3: fluent forgeries accepted at ≥ 50% of the genuine fluent rate, at a 1% FPR, make the watermark unreliable as provenance evidence against a quality check.

## 8. Secondary (descriptive)
- Plain acceptance, and FA under v0.3's perplexity-only definition, of the v0.4 forgeries.
- **v0.2's and v0.3's forgeries re-scored under v0.4's FA** (what the repetition term changes).
- FA with v0.3's word rep3 in place of seq-rep-4 (continuity with the v0.3 exploratory analysis).
- The selected layer and whether it equals 14; candidates passing; "no candidate passed"; the selected candidate's repetitive-trial count; the median cosine to the key; the median perplexity ratio to the oracle; the median seq-rep-4 beside the oracle's (a ratio is undefined when the oracle's median is 0) and the share of texts above the seq-rep-4 bar; the attacker's check vs the evaluation (agreement).
- Samples read and quoted: 3 per route at ρ = 0.50, n = 256, the first pool D text of keys 1001–1003 (the v0.3 rule), plus **3 accepted-and-fluent texts per route at ρ = 0.70, n = 256** (the first such text for keys 1001, 1002, 1003 in pool D order; skipped for a key with none), to check what the rule admits.
- D-cos stays deferred to Study 3.

## 9. Stop rules; what a null means
- **The integrity check fails:** stop.
- A null ("not practical" for both routes at a level) means this passive attacker, screening for perplexity and repetition with ≤ 256 texts, does not produce fluent non-repetitive forgeries at that strength. It does not undo v0.2's result that the probe accepts garbled or off-key text, or v0.3's perplexity-only verdicts.

## 10. Inputs validated before the lock (no outcomes)
The reused files exist and hash (v0.2's 243 and v0.3's 120); the integrity check on two key-levels; seq-rep-4 on constructed token lists (0 for distinct, the right value for a loop, 0 for < 4 tokens); the selection logic on synthetic values (both conditions; the fallback order); **with the repetition term switched off, the v0.4 scoring code reproduces v0.3's locked FA medians exactly** (v0.3 outcomes, already reported); seeds disjoint from v0.2 and v0.3; attack isolation; the runner refusing without a lock; a pipeline smoke test on the validation key that asserts every result field listed in §5 and §8; a **timing check with a budget of 9 h**. No v0.4 trial or forgery is generated with a study key before the lock.

## 11. What is not claimed
As v0.3 §11; plus: that seq-rep-4 captures all degeneration (off-prompt drift, as seen in v0.3, is not measured; samples are read, not rated); that the attacker's check is optimal.

## Compute budget (projected; re-timed at validation)
As v0.3: 7,680 trial and 9,600 forgery generations, plus perplexities and re-encoding (about 6.3 h measured in v0.3); seq-rep-4 needs only tokenisation (seconds).
