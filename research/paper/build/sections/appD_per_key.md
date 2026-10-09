# Appendix D — Per-key tables and calibration

Every rate in the main text is a median over the 8 study keys with a cluster-bootstrap interval. A median can pass a rule while a few keys fail completely, so this appendix gives the per-unit view behind every median (Tables TA6–TA9) and the per-key calibration of every test used (Figure FA1), together with the key-leakage lens of Study 3 (Figure FA2). Per-key heterogeneity is a descriptive reading; the scheme's authors note it for steering directions in general ("Some vectors induce more severe degradations in generation quality, while others are more easily detectable", p. 7) [@ardoin2026selfrecognition].

## D.1 Forgery of the probe, per key

**Table TA6** (see `build/TA6.md`).

At $\rho = 0.35$, where Route B's forgery is practical (Section 5.2), its fluent acceptance ranges from 2 to 39% across keys and 5 of 8 keys are at or above the F1 bar of 14.3%, so the verdict rests on a majority of keys rather than on all of them; Route A's acceptance there stays within 1–13%. At $\rho = 0.70$ Route A is bimodal: 5 keys are accepted half the time or more and 3 keys at most a fifth of the time, which is why its interval straddles the bar and the rule reads "inconclusive" (Table T3). The last two rows of each strength give the per-key quality bars: the perplexity bar is the key's own genuine 95th percentile and rises from 9.9–12.2 at $\rho = 0.35$ to 19.1–30.6 at $0.70$, the point Appendix E returns to.

## D.2 The exact test, per key

**Table TA7** (see `build/TA7a.md` and `build/TA7b.md`).

Every study key is calibrated under S4 (0.1–1.7% on unwatermarked model text; at most 1.6% on human continuations), while the unstandardised statistic S3 loses key 1002 at 3.4% (Table TA7b), which is what the power pilot's per-key diagnosis predicted (Appendix B). Two readings were moved here from Section 5.3 for length. The narrowest margin among the "not practical" forgery verdicts is Route A at $\rho = 0.70$ and $n = 64$, whose upper bound of 42.0% sits just under the 45.0% bar. And key 1002 at $\rho = 0.70$ is attributed for only 41.0% of its genuine texts where every other key reaches at least 98.0%; its p-values sit just above the cut-off and its false-positive rate is the lowest of the eight (0.1%), so its test is conservative in both directions (an exploratory reading from Study 3; unexplained; it changes no verdict, the level's median being 100.0%). The same key is the weakest under the probe-free union test of rotation (Table TA9) and the one that random edits scrub most often (Appendix D.3).

**Figure FA2** (see `build/FA2.png`).

The key-leakage lens (Figure FA2a; Table TA7a) shows where forgeries pass the exact test: in 35 of 384 key–strength–forgery-set cells half or more of the forged texts are attributed, and attribution rises with the attacker's recovered cosine (Spearman 0.68 for Route A and 0.56 for Route B over all cells). For the v0.4 forgeries at $n = 256$ the cells at or above 50% are: v0.4 Route B at n = 256, key 1006 at ρ = 0.35 (50%); v0.4 Route A at n = 256, key 1004 at ρ = 0.50 (97%); v0.4 Route B at n = 256, key 1003 at ρ = 0.50 (58%); v0.4 Route A at n = 256, key 1004 at ρ = 0.70 (100%); v0.4 Route B at n = 256, key 1003 at ρ = 0.70 (67%); v0.4 Route B at n = 256, key 1004 at ρ = 0.70 (98%). Route A's forgeries pass where the attack recovered much of the key (key 1004 at $\rho \geq 0.50$: cosine high, acceptance 97–100%); some Route B forgeries pass at a cosine near zero (key 1003 and 1006), which we read, as Study 3 did, as the copied footprint reproducing enough of the key's effect on the output distribution for the gradient test to see it (an inference). The protection is therefore only as good as the key's secrecy: with at most 1,024 observed texts this leakage is uncommon for the v0.2–v0.4 attackers and is exactly what Route A$'$ then achieves for every key (Section 5.4).

## D.3 Scrubbing, per key

**Table TA8** (see `build/TA8.md`).

P-Qwen's "effective" verdict at $\rho = 0.25$ rests on 7 of 8 keys at or above 50% and at $0.35$ on 5; P-Phi at $0.35$ reaches the bar for 2 keys, the per-key picture behind its inconclusive interval. Key 1002 at $\rho = 0.70$ was attributed before scrubbing for only 41.0% of its texts (the same conservative key as above), and random 5% edits then "scrub" it 35.0% of the time where no other key exceeds 1.0%, so one key's weak detection, not the edits, produces that cell. Figure FA2b plots E-est's success against the accuracy of the v0.2 estimate it used: the estimate's cosine with the key never exceeds 0.75 and the correlation is weak (Spearman 0.13), consistent with the estimate carrying little of the key.

## D.4 The defence, per key

**Table TA9** (see `build/TA9.md`).

For the fixed key, Route A$'$ recovers every key at $n = 64$ (cosine 0.76–0.99 at $\rho = 0.35$) and every key's forgeries at $n =$ 1,024 exceed the bar (75–89%; 8 of 8 keys). For the hashed arms no key's forgery acceptance at $n =$ 1,024 exceeds 11% ($h = 1$, $\rho = 0.50$). The robustness cost varies: for $h = 1$ at $\rho = 0.35$ the per-key difference from the fixed key runs from -1 to +45 points with 5 keys at or above 20 points and 1 key at or below zero; for $h = 4$ at $0.35$ only 3 keys reach 20 points, which is the per-key reading behind the inconclusive D2 verdict. Perplexity ratios to the fixed key lie between 0.71 and 0.90 for $h = 1$ at $0.35$, below 1 for every key. Rotation's union test detects 80–100% per key at $\rho = 0.50$, key 1002 again lowest at 80%.

## D.5 Per-key calibration before and after paraphrase and keying

**Figure FA1** (see `build/FA1.png`).

Every per-key false-positive rate of the primary test shown in Figure FA1 sits under the 3% gate (the highest, across the fixed key's test on model and human text, after both paraphrasers and under both keyed tests, is 1.7%); the secondary statistic S3 left key 1002 at 3.4% (Table TA7b), and fresh keys exceed the gate after paraphrase (below), so no verdict excludes a key. The gate is what makes a test that is exact on average over keys usable with one key (Section 3): among 1,000 fresh keys drawn from the same distribution and tested on the paraphrased null texts, 6.5–7.8% exceed 3% (maxima 19.5–22.6%) while the mean stays at 0.94–1.02% (Table TA12b).

## Open items
- Every number here is a registered value from `tabA6`–`tabA9`, `tab4`, `tab5`, `tabA12`, `figA1` and `figA2`; the §5.3 and §5.5 cuts (`s3x_narrowest_A_07_n64_hi`, `s3x_key1002_*`, `s2_key1002_*`) are placed in D.2 and D.3 as their open items name.
- The probe's per-key acceptance rates were not stored by Study 3's run, so Table TA7a carries the probe's median only.

- Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- Final revision 2026-10-08 (Milestone 16, after the Codex review): A3 (D.5 scoped to the primary test, with S3's and the fresh keys' exceedances named); correction (Claude): the v0.4 perplexity bar is the key's genuine 95th percentile (protocols v0.3 and v0.4; `FLUENT_Q = 0.95`), not the median. Decided by Yichen 2026-10-08 (A3); the correction is a fact.
