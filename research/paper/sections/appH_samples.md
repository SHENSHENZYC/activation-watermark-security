# Appendix H — Samples read

Every study fixed a sampling rule before its run and quoted the chosen texts in its report; the readings below are descriptive and were made after the pre-registered verdicts. Study 1's rule (v0.3 and v0.4): $n = 256$, keys 1001–1003, one text per route, the first pool D text at $\rho = 0.50$ and, in v0.4, the first accepted-and-fluent text at $\rho = 0.70$. Study 2's rule: keys 1001 and 1002 at $\rho = 0.50$, the first pool D text with its paraphrases and edits. Study 5's rule: the same two keys and strength, for each arm the first genuine text, its forgery at $n =$ [[s5x_N_OBS]] and its paraphrase. The excerpts here are the first [[h_excerpt_words]] words of each text as stored ([[h_excerpt_words_short]] for the paraphrases, edits and keyed-arm texts; "…" marks the cut); the full texts are in the study reports.

## H.1 Forgeries against the probe

**v0.4, $\rho = 0.50$, first pool D text** (the prompt asks the model to continue a list of NBA free agents: "[[h_v04_05_prompt_k1001]]").

Route A, key 1001 (accepted: [[h_v04_05_A_k1001_acc]]; perplexity [[h_v04_05_A_k1001_ppl]] against the key's bar of [[h_v04_05_A_k1001_ppl_bar]]; seq-rep-4 [[h_v04_05_A_k1001_rep]] against [[h_v04_05_A_k1001_rep_bar]]):

> [[h_v04_05_A_k1001_text]]

Route B, key 1002 (accepted: [[h_v04_05_B_k1002_acc]]; fluent: [[h_v04_05_B_k1002_fluent]]; perplexity [[h_v04_05_B_k1002_ppl]] against [[h_v04_05_B_k1002_ppl_bar]]; seq-rep-4 [[h_v04_05_B_k1002_rep]] against [[h_v04_05_B_k1002_rep_bar]]):

> [[h_v04_05_B_k1002_text]]

Route B, key 1003 (accepted: [[h_v04_05_B_k1003_acc]]; fluent: [[h_v04_05_B_k1003_fluent]]; perplexity [[h_v04_05_B_k1003_ppl]] against [[h_v04_05_B_k1003_ppl_bar]]):

> [[h_v04_05_B_k1003_text]]

Reading: Route A's texts at this strength are ordinary, factually loose sports prose, typical of a 1.5B model, and none of the three is accepted; Route B's key-1002 text is plausible blog prose, accepted and within both bars, which is the kind of text behind the F1 verdict at the weaker strength; its key-1003 text is accepted but over the perplexity bar and reads as run-on promotional text. No sample at this strength is a loop.

**v0.4, $\rho = 0.70$, first accepted-and-fluent text.** Route B, key 1002 (accepted and fluent; perplexity [[h_v04_07_B_k1002_ppl]] against [[h_v04_07_B_k1002_ppl_bar]]; seq-rep-4 [[h_v04_07_B_k1002_rep]] against [[h_v04_07_B_k1002_rep_bar]]):

> [[h_v04_07_B_k1002_text]]

Route A, key 1002 (accepted and fluent; perplexity [[h_v04_07_A_k1002_ppl]] against [[h_v04_07_A_k1002_ppl_bar]]):

> [[h_v04_07_A_k1002_text]]

Reading: the Route B text is word salad and passes both bars, because the bars are relative to the key's own degraded genuine texts at this strength (Appendix E); Route A's text reads as ordinary blog prose. Of the six accepted-and-fluent texts at $\rho = 0.70$, five read as plausible if rambling and one is word salad.

**v0.3, $\rho = 0.50$, first pool D text, perplexity-only rule.** Route B, key 1001 (layer [[h_v03_05_B_k1001_layer]]; accepted: [[h_v03_05_B_k1001_acc]]; fluent under the perplexity rule: [[h_v03_05_B_k1001_fluent]]; perplexity [[h_v03_05_B_k1001_ppl]] against [[h_v03_05_B_k1001_ppl_bar]]):

> [[h_v03_05_B_k1001_text]]

Reading: a degenerate loop steered at an early layer, accepted by the probe and counted as "fluent" by the perplexity-only rule; v0.4's repetition term was added because of texts like this one. The same key's v0.4 Route B text at this strength (layer 2, above) is rejected for repetition.

## H.2 Reference texts

Study 5's fixed-key genuine text for key 1001 at $\rho = 0.50$ ([[h_s5_k1001_fixed_genuine_meta]]):

> [[h_s5_k1001_fixed_genuine_text]]

This is what "no less fluent than the owner's own text" is measured against at the strength where most verdicts fall; at $\rho = 0.70$ the median genuine text of key 1002 is the repeated fragment quoted in Appendix E.

## H.3 Paraphrases and edits (Study 2)

Key 1001, $\rho = 0.50$; the original is the text above (S4 $p =$ [[h_s2_k1001_original_p]]). P-Qwen ($p =$ [[h_s2_k1001_Pqwen_p]]; attributed: [[h_s2_k1001_Pqwen_detected]]):

> [[h_s2_k1001_Pqwen_text]]

P-Phi ($p =$ [[h_s2_k1001_Pphi_p]]; attributed: [[h_s2_k1001_Pphi_detected]]):

> [[h_s2_k1001_Pphi_text]]

E-true, 5% of the tokens ($p =$ [[h_s2_k1001_Etrue5_p]]; attributed: [[h_s2_k1001_Etrue5_detected]]):

> [[h_s2_k1001_Etrue5_text]]

Key 1002, $\rho = 0.50$ (original $p =$ [[h_s2_k1002_original_p]]). P-Qwen ($p =$ [[h_s2_k1002_Pqwen_p]]; attributed: [[h_s2_k1002_Pqwen_detected]]); P-Phi ($p =$ [[h_s2_k1002_Pphi_p]]; attributed: [[h_s2_k1002_Pphi_detected]]); E-true 5% ($p =$ [[h_s2_k1002_Etrue5_p]]) and 10% ($p =$ [[h_s2_k1002_Etrue10_p]]; attributed: [[h_s2_k1002_Etrue10_detected]]):

> [[h_s2_k1002_Pqwen_text]]

Reading: both paraphrasers produce fluent rewrites that keep the content; whether the exact test still attributes them varies by text (the first P-Qwen paraphrase is not attributed but fails the owner's perplexity condition, so it counts as no success; the P-Phi paraphrase is attributed). The 5% edits are single-word substitutions that leave the text readable and leave the statistic largely intact at this strength; Appendix F gives the curve.

## H.4 Keyed-arm texts (Study 5)

Key 1001, $\rho = 0.50$. The fixed key's Route A$'$ forgery at $n =$ [[s5x_N_OBS]] ([[h_s5_k1001_fixed_forgery_meta]]):

> [[h_s5_k1001_fixed_forgery_text]]

Context-hashed $h = 1$, genuine text ([[h_s5_k1001_h1_genuine_meta]]):

> [[h_s5_k1001_h1_genuine_text]]

Its per-context forgery at $n =$ [[s5x_N_OBS]] ([[h_s5_k1001_h1_forgery_meta]]):

> [[h_s5_k1001_h1_forgery_text]]

Its P-Qwen paraphrase ([[h_s5_k1001_h1_para_meta]]):

> [[h_s5_k1001_h1_para_text]]

Context-hashed $h = 4$, per-context forgery at $n =$ [[s5x_N_OBS]] ([[h_s5_k1001_h4_forgery_meta]]):

> [[h_s5_k1001_h4_forgery_text]]

Rotation, the clustering attacker's forgery at $n =$ [[s5x_N_OBS]] ([[h_s5_k1001_rot_forgery_meta]]):

> [[h_s5_k1001_rot_forgery_text]]

Reading: the stolen fixed key's forgery and the rotation forgery read as ordinary sports prose and are accepted; the keyed arms' genuine texts read as fluent as the fixed key's (their perplexity is lower), their per-context forgeries steer most positions for $h = 1$ and almost none for $h = 4$ and are rejected, and the paraphrase of the $h = 1$ text is fluent, faithful and no longer attributed, which is the robustness cost in one example.

## Open items
- Every excerpt and every number here is registered by `tables/appH_samples.py` from the locked `results.json` files (v0.4, Study 2) or from the generated reports and the report builder's `samples.md` (v0.3, Study 5); nothing is retyped. The readings are the reports' descriptive readings, paraphrased.
- The excerpts are shortened to the stated word counts; the reports quote the first 80 words (Study 1) or the full texts (Studies 2 and 5).
- Decided 2026-10-08 (Yichen, O4): the C4 prompt excerpt is cut to its first clause by `appH_samples.py` (`first_clause`), replacing the 30-word excerpt; the generated texts are quoted as before.
