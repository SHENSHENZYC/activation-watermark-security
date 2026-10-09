# Study 2 scrubbing pilot v0.2 (edit component): does the float32 editor pass the checks, and does the revised Study 2 fit its time?

**Status:** FIXED (2026-10-01, approved by Yichen as drafted) before any v0.2 edit was made. The script records the fixing commit. Any change needs a new version.
**Supersedes:** v0.1 for the **edit component only**. v0.1's bars, paraphrases and paraphrase readings stand ([`SCRUB_PILOT_REPORT_v0.1.md`](SCRUB_PILOT_REPORT_v0.1.md)).
**Why:**
- v0.1's check I1 failed. The editor's finite differences, computed in bfloat16, matched the gradient at r = 0.985 (rule ≥ 0.99). An after-run diagnosis found bfloat16 rounding to be the cause; in float32 they match exactly (r = 1.000 at every step; `outputs/study2_pilot_v0.1/posthoc_I1_diag.json`).
- Yichen decided (2026-10-01): float32 editor passes, confirmed in this v0.2; edits judged at 5% of tokens, with 2% and 10% as secondary points and 20% dropped; Phi on 50 genuine texts per key-level in Study 2.
- v0.1's rule A2 fixed the round size at 5%.

This pilot re-runs the three edit arms with those changes, re-checks I1–I3, and re-projects Study 2's time under the revised scope.
**Scope:** as v0.1: tuning keys 9001–9004 only, the same 400 watermarked tuning texts, the same E-est stand-ins. No study key or study-key text is read.

## 1. What changes from v0.1 (everything else is v0.1's §2.2–§3, unchanged)
- **The editor's two passes run in float32:** a float32 copy of Qwen2.5-1.5B (pinned `8faed761`), loaded only for the edit phase. The owner's S4 scoring stays exactly as in Study 3 (bfloat16, `power_pilot.text_features`), and so do the quality measures.
- **Budgets:** the text is saved after 2%, 5% and 10% of T; editing stops at 10%.
- **Round size:** *r* = 5% of T, as chosen by v0.1's rule A2. A round never overshoots the next budget, so with T = 256 the rounds edit 6, 7 and 13 tokens.
- **Step:** s = 2.0, as v0.1 (exact in float32 at every step tried).
- Arms, candidates (whole words, at least 1/3 as likely as the current word, the first 10 of the top 40), the gap rule, the attacker's gradient scale (σ̂ over its 200 pool C references, from v0.1's `refs.npz`) and the stand-ins are all as in v0.1.

## 2. Inputs (reused; SHA-256 recorded)
v0.1's `data/bars.json` (the quality bars and the originals' quality) and `data/refs.npz` (the owner's pool F scale; the attacker's σ̂), its watermarked tuning texts, and `data/G_orig_wm.npy` (the originals' S4 gradients, I1's autograd reference). Models as v0.1.

## 3. Checks (must pass before the Study 2 protocol is drafted)
- **I1, contributions:** as v0.1, on the 25 watermarked texts of key 9001 at ρ = 0.50. The float32 editor's Σ_t c_t(x_t) against the autograd derivative ⟨g, ŵ⟩ (v0.1's reference): Pearson r ≥ 0.99. Per token, c_t at s and at s/2: Spearman, median over the first 10 texts, ≥ 0.8.
- **I2, the edits act on the key:** over the 400 texts, the change in the owner's T(x, v) from 0% to **5%** (the new judgement point) is more negative under E-true than under E-rand (paired Wilcoxon, p < 0.01), and E-true's median change is negative.
- **I3, bookkeeping:** as v0.1 (exact edit counts at each budget; median re-encoding drift ≤ 2%; hooks removed).
- **I5′, Study 2 time under the revised scope:** projected ≤ **30 h** in total, computed from:
  - v0.1's measured paraphrase rates, with attempts per original taken from its P2 runs;
  - v0.2's measured edit and scoring rates;
  - the revised counts: Qwen 3,200 genuine + 1,000 null; Phi 1,600 genuine + 1,000 null; edits 3 arms × 3,200 texts; scoring every kept paraphrase, every first attempt that differs from the kept one, the length-matched controls, 3 budgets × 3 arms, and the originals.

  If not, I bring options to Yichen before the protocol.

## 4. What the pilot reports (descriptive; tuning keys only)
v0.1's edit tables (detection before and after, scrub success with keys ≥ 50%, pass rates per condition, length, perplexity and cosine) at 2%, 5% and 10%, beside v0.1's bfloat16 editor at the same budgets; the stricter quality readings; the attacker's objective; samples at 5% and 10% for keys 9001 and 9002 at ρ = 0.50; timing and peak memory.

## 5. Validation before the run (inputs only)
1. Inputs exist; hashes match the files v0.1 recorded.
2. The float32 editor on 2 unwatermarked tuning texts outside the pilot set, with a random direction: its finite-difference sums match float32 autograd (r ≥ 0.999 over 8 directions, across the 2 texts), edit counts are exact at 2%, 5% and 10%, and hooks are removed.
3. Timing and peak memory of the edit phase on those texts (memory ≤ 10 GB; the pilot projected ≤ 2 h).

## 6. Outputs
`research/outputs/study2_pilot_v0.2/VALIDATION.json`, `results.json` (committed); edited texts and values in `research/study2_pilot/data/v02/` (git-ignored); `SCRUB_PILOT_REPORT_v0.2.md`, built by a script.
**Compute (projected):** edits about 45 min (E-true and E-est about 3 s per text in float32, E-rand about 1 s); scoring 3,600 texts, about 25 min. About 1.2 h. The Mac needs no restart (no Phi; peak about 9 GB).
