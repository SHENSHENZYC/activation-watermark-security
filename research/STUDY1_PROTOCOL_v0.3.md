# Study 1 — Quality-aware forgery of an activation-steering watermark — protocol v0.3

Date: 2026-09-26. **Status: LOCKED before outcomes** (2026-09-27, approved by Yichen). The lock record is `outputs/study1_v0.3/PRE_RUN_LOCK.json`; any change needs a new version (v0.4), and this file is never edited again. Builds on v0.2 (LOCKED 2026-09-26; run and reported, [`STUDY1_REPORT_v0.2.md`](STUDY1_REPORT_v0.2.md)); v0.2's protocol, code, data and results are **reused read-only and never edited**, and v0.2's verdicts stand.
Paper role: the forgery result with a quality guarantee (1 figure, 1 table), which replaces v0.2's exploratory Table 4 as the evidence for "fluent forgery without the key".

## 0. Why v0.3
v0.2's pre-registered rule R2 found footprint forgery (Route B) "practical" at n = 64, but R2 had no quality condition. Exploratory analysis (labelled in the v0.2 report) showed that in 43 of 96 Route B cases the attack steered at layer 0 or 1 and produced gibberish that the owner's probe still accepted. v0.3 asks the question v0.2 could not: **can a passive attacker forge texts that are both accepted and as fluent as genuine watermarked text?** Decisions (Yichen, 2026-09-26): a per-text fluency rule against genuine texts; the attacker's own trial-based layer search; ρ ∈ {0.35, 0.50, 0.70}, n ∈ {64, 256}, both routes.

## 1. Question and type
Adequacy (security) check, continued. **Q1c (fluent forgery):** with the open model and *n* watermarked texts, can an attacker who screens its own candidates for fluency produce texts that the owner's detector accepts at a 1% FPR **and** that are no less fluent than the owner's own watermarked texts?

## 2. Threat model (as v0.2 §2, plus)
The attacker may generate with the open model on its **own** prompts and score perplexity with the open model. It does not see the prompts behind the observed texts, so it scores observed and trial texts the same way: **continuation-only perplexity** (the text given only the model's `<|endoftext|>` token as context). It still cannot query the detector or see *v*, *l*, the probe, its threshold, or any evaluation prompt.

## 3. Reused from v0.2 (read-only; hashed in the lock)
Per key and level: the owner's trained probe (`K_*_mlp.pt`) and threshold, the oracle and random-key texts on pool D with their detector scores and perplexities (`K_*_summary.json`), the observed watermarked texts (`K_*_obs.json`) and their all-layer features (`K_*_obs_feats.npy`); shared: the attacker's reference texts, features and norms (pool C: `S_C_ref*`). Model, keys (1001–1008), layer 14, k = 4, N, pools and sampling as v0.2.
**Integrity check (asserted before any new outcome is scored):** for every key-level, the reloaded probe re-scores v0.2's oracle texts to within 1e-4 of the saved scores.

## 4. Attack (frozen)
For each key, level ρ, *n* ∈ {64, 256} (the first *n* observed texts) and route R ∈ {A, B}:
1. **Candidates.** Compute the route's per-layer footprint profile exactly as v0.2 (`attack2`: A = max_i |z_{ℓ,i}|; B = ‖z_ℓ‖₂). Take the **5 layers with the largest profile**. At each candidate ℓ, the vector is the route's estimate *at ℓ* (A: Δ on the top-*k* |z| coordinates at ℓ; B: the dense Δ at ℓ), rescaled to ρ·N̂_ℓ (the attacker's own median norm).
2. **Attacker's fluency reference.** *q*_obs = the median continuation-only perplexity of the *n* observed texts.
3. **Trials.** For each candidate, generate 16 trial texts on the attacker's own prompts (the first 16 prompts of pool C; the same prompts and seed for every candidate); *q*_ℓ = their median continuation-only perplexity.
4. **Selection.** Keep candidates with *q*_ℓ ≤ **1.2 × *q*_obs**. Use the kept candidate with the largest profile; if none is kept, use the candidate with the smallest *q*_ℓ (recorded as "no candidate passed").
5. **Forgery.** 100 continuations on pool D (as v0.2), steered by the selected vector at the selected layer, with new seeds (base + 20 + 3·route + n-index); scored by the owner's v0.2 probe and threshold.
The attack module receives only features, texts it generated or observed, its own perplexities, and public parameters (asserted in code, as v0.2's G2).

## 5. Targets and metric
- **Per text:** *accepted* = score > the owner's threshold; *fluent* = perplexity (under the unsteered model, **given its prompt**, exactly as v0.2's evaluation) ≤ the **95th percentile of that key-level's oracle texts** (v0.2's 100 genuine watermarked texts on pool D).
- **Primary metric FA (fluent acceptance):** the share of a condition's 100 texts that are both accepted and fluent; the median over 8 keys, per route, level and *n*.
- **Controls (from v0.2 texts, same definition):** oracle FA (the ceiling; at most 95% plus ties by construction) and random-key FA (generic steering).

## 6. Uncertainty
Keys are replicates (K = 8). 95% intervals by a cluster bootstrap over keys, then texts (B = 2,000, seed 20260927), as v0.2.

## 7. Rules (per level; all three levels passed v0.2's L1)
- **F1, fluent forgery is practical** (per route) if, at some *n* ∈ {64, 256}, the median FA ≥ 50% of the oracle's median FA **and** its lower 95% bound exceeds the random-key FA's upper 95% bound.
- **Not practical** if, at both *n*, the **upper** 95% bound of FA is below 50% of the oracle's median FA. Otherwise **inconclusive**. *(This bound cannot exceed 100% and does not depend on the random-key rate; see the v0.2 limitation.)*
- **F3, fluent generic steering suffices** if the random-key median FA ≥ 50% of the oracle's median FA. Reported alongside F1. (Computed from v0.2 texts whose acceptance was already reported; FA itself is new.)
- **Materiality:** fluent forgeries accepted at ≥ 50% of the genuine fluent rate, at a 1% FPR, would make the watermark unreliable as evidence of provenance even against a quality check.

## 8. Secondary (descriptive)
Plain acceptance (as v0.2) of the v0.3 forgeries; the selected layer and whether it equals 14; how many candidates passed the attacker's check; whether "no candidate passed"; median perplexity ratio of forgeries to oracle texts; the attacker's check vs the evaluation's fluency (agreement); **v0.2's forgeries re-scored under FA** (to show what the quality condition changes); samples of forged texts read and quoted in the report (3 per route at ρ = 0.50). D-cos stays deferred to Study 3.

## 9. Stop rules; what a null means
- **The integrity check fails:** stop; the reused detectors are not the ones v0.2 used.
- A null ("not practical" for both routes at a level) means this quality-aware passive attack with ≤ 256 texts does not produce fluent forgeries at that strength. It does not undo v0.2's result that the probe accepts garbled or off-key text.

## 10. Inputs validated before the lock (no outcomes)
The reused files exist and hash; the integrity check on v0.2's oracle scores (these are v0.2 outcomes, already reported); continuation-only perplexity on a few unsteered pool C texts (finite, plausible); the candidate and selection logic on synthetic profiles and perplexities; attack isolation; the runner refusing without a lock; a **timing check with a budget of 9 h**. No v0.3 forgery is generated or scored before the lock.

## 11. What is not claimed
As v0.2 §13; plus: that the attacker's check is optimal; fluency beyond perplexity (samples are read, not rated).

## Compute budget (projected; re-timed at validation)
Trials: 3 levels × 8 keys × 2 *n* × 2 routes × 5 candidates × 16 = 7,680 generations. Forgeries: 96 × 100 = 9,600. In total 17,280 generations at about 1.07 s, about 5.1 h, plus perplexities (observed, trial, forged) and re-encoding, about 1 h: **about 6 h**.
