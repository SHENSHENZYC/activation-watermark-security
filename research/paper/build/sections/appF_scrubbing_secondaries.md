# Appendix F — Scrubbing secondaries

## F.1 The edit curve

**Table TA11** (see `build/TA11.md`).

**Figure FA3** (see `build/FA3.png`).

Study 2 judged the key-guided edits at 5% of the tokens and recorded 2% and 10% as well (Table TA11; Figure FA3, top). The true key's edits remove the evidence faster than they fail quality only at the weakest strength: at $\rho = 0.25$ E-true reaches 81.0% success at 10%. At the two strongest strengths 10% true-key edits remove detection without counting as success, because the perplexity condition fails: at $\rho = 0.70$ detection after E-true 10% is 40.0% while only 3.5% of the edited texts pass the perplexity bar (the Section 5.5 cut). The attacker's estimate (E-est) sits between the true key and random edits at $\rho \leq 0.35$ and is indistinguishable from random edits above, consistent with the v0.2 estimate's low accuracy (Appendix D). The editor's bookkeeping (Table TA12a's notes): every arm stalled before 10% in 8 texts, re-tokenisation drift was 0.000 at every budget, and the attacker's objective fell from 3.15 to 0.57 for the true key against 0.43 to -0.68 for the estimate, which had little of the key's statistic to remove.

## F.2 Length-matched controls, similarity and attempts

**Table TA12** (see `build/TA12a.md` and `build/TA12b.md`).

Paraphrases are shorter than their originals, so a lower attribution rate could mean less text rather than removed evidence. Cutting each original to its paraphrase's token count and scoring it leaves 91.2–99.0% attributed across paraphrasers and strengths (Table TA12a), so the paraphrase removes evidence. The embedding-similarity condition is the one the paraphrases most often fail (at $\rho = 0.35$, 79.5% of P-Qwen's and 82.0% of P-Phi's pass it, against 74.0% and 79.0% passing all four). The attacker's self-check allowed up to three attempts: P-Qwen kept 1,835, 822 and 543 texts at the first, second and third attempt of 3,200, and 32.0% of the kept texts still failed its own check; counting first attempts only, P-Qwen's success at $\rho = 0.25$ is 49.5% against 64.0% with retries.

## F.3 Pooling texts and the stricter level

A deployer who can pool several texts from one source regains much of what one paraphrase removes: four P-Qwen paraphrases pooled are attributed 26.0% of the time at $\rho = 0.25$ and 90.0% at $0.70$, and four P-Phi paraphrases 91.7% at $0.35$ (Table TA12a). At the stricter level $p \leq 0.001$ with 9,999 null keys, single paraphrased texts are attributed 3.0–19.0% (P-Qwen), so the choice of level trades the human-text false-positive rate of Section 5.3 against this.

## F.4 The probe on the same scrubbed texts (a lead, labelled)

The owner's trained probe was scored on the same scrubbed texts (Table TA12a; Figure FA3, bottom). At $\rho \geq 0.50$ it accepts 79.0–100.0% of the paraphrases where the exact test attributes 35.0–66.0%, and at $\rho \leq 0.35$ only 6.0–37.0%; its false-positive rate on the paraphrased null texts is 3.3% (P-Qwen) and 3.0% (P-Phi) against its nominal 1% on unparaphrased model text. We record this as a lead only: the probe may be reading a content footprint of strong steering that survives rewriting, which would fit its acceptance of off-key steering (Section 5.2), but a detector whose paraphrased-text false-positive rate is several times its nominal level cannot be credited with robustness on this evidence, and no rule was pre-registered for it.

## F.5 The authors' robustness figures, indirectly

Self-Recognition reports robustness to DIPPER paraphrase as attribution accuracy between two steered variants, with the trained probe falling from 99.1 to 89.3 and the cosine detector from 84.6 to 77.8 (Table 3, p. 6) [@ardoin2026selfrecognition]. The comparison with Section 5.5 is indirect on every axis: their detector, models, paraphraser and metric differ from ours, their measure is attribution between watermarked variants rather than detection against human text at a fixed false-positive rate, and our paraphrasers are far smaller than DIPPER-XXL, which does not fit the hardware used here.

## Open items
- The §5.5 cuts (`s2_Etrue10_*`, `s2_probe_para_hi_*`, `s2_S4_para_hi_*`) are placed in F.1 and F.4 as its open item names; the C11 lead is labelled in F.4 and nowhere stated as a result.
- The Table 3 numbers (99.1 → 89.3; 84.6 → 77.8; p. 6) are the gate's page-confirmed reading; re-confirmed by substring search on 2026-10-06 (see the Milestone 15 log entry).
- Rotation's detection after paraphrase is not in the locked Study 5 results file and is not quoted anywhere in the paper (Appendix G).

- Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
