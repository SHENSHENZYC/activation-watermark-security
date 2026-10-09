# Appendix D — Per-key tables and calibration

Every rate in the main text is a median over the [[n_keys]] study keys with a cluster-bootstrap interval. A median can pass a rule while a few keys fail completely, so this appendix gives the per-unit view behind every median (Tables TA6–TA9) and the per-key calibration of every test used (Figure FA1), together with the key-leakage lens of Study 3 (Figure FA2). Per-key heterogeneity is a descriptive reading; the scheme's authors note it for steering directions in general ("Some vectors induce more severe degradations in generation quality, while others are more easily detectable", p. 7) [@ardoin2026selfrecognition].

## D.1 Forgery of the probe, per key

**Table TA6** (see `build/TA6.md`).

At $\rho = 0.35$, where Route B's forgery is practical (Section 5.2), its fluent acceptance ranges from [[ta6_v04_B_n256_035_min]] to [[ta6_v04_B_n256_035_max]]% across keys and [[ta6_v04_B_n256_035_keys_ge_bar]] of [[n_keys]] keys are at or above the F1 bar of [[ta6_bar_035]]%, so the verdict rests on a majority of keys rather than on all of them; Route A's acceptance there stays within [[ta6_v04_A_n256_035_min]]–[[ta6_v04_A_n256_035_max]]%. At $\rho = 0.70$ Route A is bimodal: [[ta6_A_07_keys_ge_50]] keys are accepted half the time or more and [[ta6_A_07_keys_le_20]] keys at most a fifth of the time, which is why its interval straddles the bar and the rule reads "inconclusive" (Table T3). The last two rows of each strength give the per-key quality bars: the perplexity bar is the key's own genuine 95th percentile and rises from [[ta6_cut_ppl_035_min]]–[[ta6_cut_ppl_035_max]] at $\rho = 0.35$ to [[ta6_cut_ppl_07_min]]–[[ta6_cut_ppl_07_max]] at $0.70$, the point Appendix E returns to.

## D.2 The exact test, per key

**Table TA7** (see `build/TA7a.md` and `build/TA7b.md`).

Every study key is calibrated under S4 ([[ta7_S4_G2_min]]–[[ta7_S4_G2_max]]% on unwatermarked model text; at most [[ta7_S4_H1_max]]% on human continuations), while the unstandardised statistic S3 loses key 1002 at [[ta7_S3_key1002_G2]]% (Table TA7b), which is what the power pilot's per-key diagnosis predicted (Appendix B). Two readings were moved here from Section 5.3 for length. The narrowest margin among the "not practical" forgery verdicts is Route A at $\rho = 0.70$ and $n = 64$, whose upper bound of [[s3x_narrowest_A_07_n64_hi]]% sits just under the [[s3x_X1_bar_07]]% bar. And key 1002 at $\rho = 0.70$ is attributed for only [[s3x_key1002_07_tpr]]% of its genuine texts where every other key reaches at least [[s3x_others_07_tpr_min]]%; its p-values sit just above the cut-off and its false-positive rate is the lowest of the eight ([[s3x_key1002_fpr_pct]]%), so its test is conservative in both directions (an exploratory reading from Study 3; unexplained; it changes no verdict, the level's median being [[s3x_oracle_tpr_07]]%). The same key is the weakest under the probe-free union test of rotation (Table TA9) and the one that random edits scrub most often (Appendix D.3).

**Figure FA2** (see `build/FA2.png`).

The key-leakage lens (Figure FA2a; Table TA7a) shows where forgeries pass the exact test: in [[s3x_leak_cells_ge50]] of [[s3x_leak_cells_total]] key–strength–forgery-set cells half or more of the forged texts are attributed, and attribution rises with the attacker's recovered cosine (Spearman [[s3x_leak_spearman_A]] for Route A and [[s3x_leak_spearman_B]] for Route B over all cells). For the v0.4 forgeries at $n = 256$ the cells at or above 50% are: [[ta7_hi_cells_v04_n256]]. Route A's forgeries pass where the attack recovered much of the key (key 1004 at $\rho \geq 0.50$: cosine high, acceptance [[ta7_key1004_05_A_n256]]–[[ta7_key1004_07_A_n256]]%); some Route B forgeries pass at a cosine near zero (key 1003 and 1006), which we read, as Study 3 did, as the copied footprint reproducing enough of the key's effect on the output distribution for the gradient test to see it (an inference). The protection is therefore only as good as the key's secrecy: with at most [[s5x_N_OBS]] observed texts this leakage is uncommon for the v0.2–v0.4 attackers and is exactly what Route A$'$ then achieves for every key (Section 5.4).

## D.3 Scrubbing, per key

**Table TA8** (see `build/TA8.md`).

P-Qwen's "effective" verdict at $\rho = 0.25$ rests on [[ta8_S1qwen_025_keys_ge_50]] of [[n_keys]] keys at or above 50% and at $0.35$ on [[ta8_S1qwen_035_keys_ge_50]]; P-Phi at $0.35$ reaches the bar for [[ta8_S1phi_035_keys_ge_50]] keys, the per-key picture behind its inconclusive interval. Key 1002 at $\rho = 0.70$ was attributed before scrubbing for only [[s2_key1002_07_detected_before]]% of its texts (the same conservative key as above), and random 5% edits then "scrub" it [[s2_key1002_07_Erand_success]]% of the time where no other key exceeds [[s2_others_07_Erand_success_max]]%, so one key's weak detection, not the edits, produces that cell. Figure FA2b plots E-est's success against the accuracy of the v0.2 estimate it used: the estimate's cosine with the key never exceeds [[fa2_s2_cos_max]] and the correlation is weak (Spearman [[s2_leak_spearman]]), consistent with the estimate carrying little of the key.

## D.4 The defence, per key

**Table TA9** (see `build/TA9.md`).

For the fixed key, Route A$'$ recovers every key at $n = 64$ (cosine [[ta9_fixed_035_n64_cos_min]]–[[ta9_fixed_035_n64_cos_max]] at $\rho = 0.35$) and every key's forgeries at $n =$ [[s5x_N_OBS]] exceed the bar ([[ta9_fixed_035_n1024_FA_min]]–[[ta9_fixed_035_n1024_FA_max]]%; [[ta9_fixed_035_n1024_keys_ge_bar]] of [[n_keys]] keys). For the hashed arms no key's forgery acceptance at $n =$ [[s5x_N_OBS]] exceeds [[ta9_h1_05_FA1024_max]]% ($h = 1$, $\rho = 0.50$). The robustness cost varies: for $h = 1$ at $\rho = 0.35$ the per-key difference from the fixed key runs from [[ta9_h1_035_d_min]] to [[ta9_h1_035_d_max]] points with [[ta9_h1_035_d_keys_ge_20]] keys at or above 20 points and [[ta9_h1_035_d_keys_le_0]] key at or below zero; for $h = 4$ at $0.35$ only [[ta9_h4_035_d_keys_ge_20]] keys reach 20 points, which is the per-key reading behind the inconclusive D2 verdict. Perplexity ratios to the fixed key lie between [[ta9_h1_035_ppl_min]] and [[ta9_h1_035_ppl_max]] for $h = 1$ at $0.35$, below 1 for every key. Rotation's union test detects [[ta9_rot_05_union_detect_min]]–[[ta9_rot_05_union_detect_max]]% per key at $\rho = 0.50$, key 1002 again lowest at [[ta9_rot_05_key1002_union_detect]]%.

## D.5 Per-key calibration before and after paraphrase and keying

**Figure FA1** (see `build/FA1.png`).

Every per-key false-positive rate of the primary test shown in Figure FA1 sits under the 3% gate (the highest, across the fixed key's test on model and human text, after both paraphrasers and under both keyed tests, is [[fa1_all_max]]%); the secondary statistic S3 left key 1002 at [[ta7_S3_key1002_G2]]% (Table TA7b), and fresh keys exceed the gate after paraphrase (below), so no verdict excludes a key. The gate is what makes a test that is exact on average over keys usable with one key (Section 3): among 1,000 fresh keys drawn from the same distribution and tested on the paraphrased null texts, [[ta12_fresh_share3_min]]–[[ta12_fresh_share3_max]]% exceed 3% (maxima [[ta12_fresh_max_min]]–[[ta12_fresh_max_max]]%) while the mean stays at [[ta12_fresh_mean_min]]–[[ta12_fresh_mean_max]]% (Table TA12b).

## Open items
- Every number here is a registered value from `tabA6`–`tabA9`, `tab4`, `tab5`, `tabA12`, `figA1` and `figA2`; the §5.3 and §5.5 cuts (`s3x_narrowest_A_07_n64_hi`, `s3x_key1002_*`, `s2_key1002_*`) are placed in D.2 and D.3 as their open items name.
- The probe's per-key acceptance rates were not stored by Study 3's run, so Table TA7a carries the probe's median only.

- Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- Final revision 2026-10-08 (Milestone 16, after the Codex review): A3 (D.5 scoped to the primary test, with S3's and the fresh keys' exceedances named); correction (Claude): the v0.4 perplexity bar is the key's genuine 95th percentile (protocols v0.3 and v0.4; `FLUENT_Q = 0.95`), not the median. Decided by Yichen 2026-10-08 (A3); the correction is a fact.
