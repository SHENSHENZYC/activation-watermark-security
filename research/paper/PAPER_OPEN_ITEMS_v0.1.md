# Open items collected at assembly (v0.1, 2026-10-06)

Collected from every section file's "Open items" list by `assemble.py`. Part 1 holds what needs Yichen; Part 2 the records (decisions taken, checks done, cuts applied) kept for the audit trail.


## Part 1 — for Yichen

- **sec0_abstract.md:** "The protocols, locks and code accompany the paper": stands under the availability decision of 2026-10-06 (a public snapshot repository, §8).
- **sec0_abstract.md:** Codex review 2026-10-08: D3: reused registered design placeholders for semantically identical constants (1,024); no measurement or bound changed; D5: corrected the stale record that said the approved metadata abstract still needed to be drafted. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec0_abstract.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A1 (the sixth finding separates the hashed arms from rotation and labels 0.35 post hoc; the last sentence narrows 'forgeable at either'), A2 (known-layer label and the layer-search forgery result, new registered names `s5_fixed_*_forge_search_FA_med`). Decided by Yichen 2026-10-08.
- **sec1_introduction.md:** "The protocols, locks and code accompany the paper (§8)": stands under the availability decision of 2026-10-06 (a public snapshot repository without weights or the generated corpora, §8).
- **sec1_introduction.md:** Title decided 2026-10-05 (Yichen; outline §1 option (a)): "A Security Analysis of an Activation-Steering LLM Watermark: Key Recovery, Forgery, Scrubbing and Keyed Defences"; the assembly script carries it.
- **sec1_introduction.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1{,}024, 1,024); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec1_introduction.md:** Codex review 2026-10-08: D4: defined FPR at its first authorial introduction; D4: used forgery for non-quoted narrative noun synonyms; quotations and literal source-word checks preserved. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- **sec1_introduction.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A3 (random-key attribution as the measured median with the per-key maximum), A2 (known layer; the layer-search recovery and forgery results), A4 ('to our knowledge' and the scope note on contribution 5). Decided by Yichen 2026-10-08.
- **sec2_background_threat_model.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1,024); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec2_background_threat_model.md:** Codex review 2026-10-08: D4: expanded MLP before the unchanged source quotation; D4: split the two long attack-route sentences into route, screening, scrubbing and control paragraphs, preserving the shared comparison, method details and existing version statements; A5 retains the version-screening correction for approval. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- **sec2_background_threat_model.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A2 (the layer is withheld except in the two labelled readings); correction (Claude): v0.3's screen was by perplexity only, the repetition screen arrived in v0.4 (protocols v0.3 and v0.4). Decided by Yichen 2026-10-08 (A2); the correction is a fact.
- **sec3_exact_test.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec3_exact_test.md:** Codex review 2026-10-08: D4: defined TPR alongside the attribution decision, without adding a measured result. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- **sec3_exact_test.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A7 (the opening inference labelled). Decided by Yichen 2026-10-08.
- **sec4_setup.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D2: replaced the circular paraphrase-instruction pointer with the locked prompt definition and selector; instruction unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec4_setup.md:** Codex review 2026-10-08: D4: British authorial spelling, judgement; direct quotations unchanged. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- **sec4_setup.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): correction (Claude): the 1.25 allowance applies to perplexity only; seq-rep-4 is bounded by max(the original's, the human 95th percentile), as the Study 2 protocol and `scrub_core.py` state. A fact, not a decision.
- **sec5_1_calibration.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec5_1_calibration.md:** Codex review 2026-10-08: D4: expanded AUROC at first authorial use. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- **sec5_1_calibration.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A11 (scope of the 512-token clause). Decided by Yichen 2026-10-08.
- **sec5_2_probe_forgery.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1{,}024, 8 keys, at 256 tokens); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec5_3_exact_test.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1{,}024, 8 keys, 256-token); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec5_3_exact_test.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A3 (median key). Decided by Yichen 2026-10-08.
- **sec5_4_stealing.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1{,}024, 1,024, 8 keys, of 8); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec5_4_stealing.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A2 (known-layer label; the layer-search forgery result beside it), A7 ('best among those tested'). Decided by Yichen 2026-10-08.
- **sec5_5_scrubbing.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec5_6_keyed.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1{,}024, 1,024, 8 keys, of 8); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec5_7_tradeoff.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec5_7_tradeoff.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A11. Decided by Yichen 2026-10-08.
- **sec6_related_work.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec6_related_work.md:** Codex review 2026-10-08: D4: British authorial spelling, judgement; direct quotations unchanged; D4: used forgery for non-quoted narrative noun synonyms; quotations and literal source-word checks preserved. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- **sec6_related_work.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A4 (the gap stated specifically; 'every attack' scoped to the evaluations cited). Decided by Yichen 2026-10-08.
- **sec7_limitations.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec7_limitations.md:** Codex review 2026-10-08: D4: British authorial spelling, judgement; direct quotations unchanged. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- **sec7_limitations.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A11 (the rotation exception). Decided by Yichen 2026-10-08.
- **sec8_reproducibility.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec9_conclusion.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **sec9_conclusion.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A7 (inference labelled; 'best among those tested'), A2 (known layer; layer search from 256), A1 (context keying and rotation stated separately; 0.35 post hoc), A12 (the Codex sentence, applied for Yichen's read as his approval of the revisions). Decided by Yichen 2026-10-08.
- **appA_protocols_locks.md:** Yichen's wording call: how much of each protocol's rule text to keep (the current paragraphs are the long form; a shorter form would keep the rules' names and bars only, with the protocols as supplementary files).
- **appA_protocols_locks.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1{,}024, 1,024, 8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appB_exact_test_detail.md:** B.5: Yichen to decide whether the sketch stays in the appendix or moves to a footnote in §3.
- **appB_exact_test_detail.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (256-token); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appB_exact_test_detail.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A7. Decided by Yichen 2026-10-08.
- **appC_attackers.md:** C.1: the clause on extracting hidden states from the decoder body is an implementation note; Yichen to decide whether it stays.
- **appC_attackers.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (1{,}024, 1,024, 8 keys, of 8, all 28 layers, each of the 28 layers, with 28 hooks, the 28-hook gradient); no measurement or bound changed; D2: pointed the paraphrase description to the now-explicit locked instruction source in Section 4. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appC_attackers.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A7 (orthogonality as an empirical fact), A2 (the layer's access stated). Decided by Yichen 2026-10-08.
- **appD_per_key.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appD_per_key.md:** Final revision 2026-10-08 (Milestone 16, after the Codex review): A3 (D.5 scoped to the primary test, with S3's and the fresh keys' exceedances named); correction (Claude): the v0.4 perplexity bar is the key's genuine 95th percentile (protocols v0.3 and v0.4; `FLUENT_Q = 0.95`), not the median. Decided by Yichen 2026-10-08 (A3); the correction is a fact.
- **appE_quality.md:** Codex review 2026-10-08: D3: reused registered design placeholders for semantically identical constants (8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appF_scrubbing_secondaries.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appG_defence_detail.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged; D3: reused registered design placeholders for semantically identical constants (8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appI_regulators.md:** Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- **appI_regulators.md:** Codex review 2026-10-08: D4: used forgery for non-quoted narrative noun synonyms; quotations and literal source-word checks preserved. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.

## Part 2 — records (93 items)


### sec0_abstract.md
- Seeded from the outline's §2 pitch and §1's contributions (Milestone 15); every number is a registered name already used by §1 or §5, so none can differ from the body.
- Resolved 2026-10-08 (D5, record correction): the shorter arXiv metadata abstract in `sec0_arxiv_abstract.md` was approved on 2026-10-06 (Stage 9 decision (d)); the PDF abstract stayed as approved. New claim-scope recommendations are in `CODEX_REVIEW_v0.1.md`, A1; none is applied by this record correction.

### sec1_introduction.md
- Cut applied 2026-10-06 (length decision, option (a): about 24 pages; figures at 80%, T3b and T6b to the appendix, the named prose cuts): the regulator paragraph to two sentences (the NIST p. 38 clause and the Measure 3.2 object dropped; Appendix I carries every measure); the five questions to section references.
- Quotations re-confirmed by substring search in the `pdftotext` extractions on 2026-10-05 with their PDF pages: Self-Recognition pp. 2, 5, 7; MarkSec p. 2; the Code of Practice pp. 9, 17, 18 (document 129555); NIST AI 100-4 pp. 13, 38. The regulator PDFs were fetched once under `research/literature/TERMS_OF_USE_CHECK.md` (addendum) and added to `pdf_manifest.json` with hashes.
- "Five questions": the outline's pitch lists six findings; calibration (§5.1) is the setting step here, and the five questions are forgery, the exact test, recovery, scrubbing and the keyed arms.
- Cuts applied before the review (2026-10-05, length; the first draft ran 1,333 words against the 975-word budget): the sentence on the related designs in the first paragraph (§6 carries them); the long form of the p. 7 security quotation (the "secrecy of the steering configuration" clause; §6 keeps the point); C8 folded into contribution 2 as its last sentence, without its numbers (`s3x_oracle_tpr_025`, `cal_q15_025_ratio` stay in §5.1); C9 and C13 moved to the closing paragraph as one sentence; the human-text and random-key rates in contribution 3 (`s3x_H1_pct`, `s3x_random_exact_max`; §5.3); the perplexity ratios and the scrub-success differences in contribution 7 (`s5x_ppl_ratio_min/max`, `s5x_h1_035_d_med`, `s5x_h4_05_d_med`; §5.6). Restore any of these as a wording call. Remaining candidates if the review wants 975 words: the regulator paragraph to two sentences (the Code's three measures in one; NIST in one); the five questions to section references only (compressed once already, 2026-10-05).
- Assembly (Milestone 15): the abstract is seeded from the outline's §2 pitch and this section's contributions; check that no number here differs from §5 (every one is the same registered name).
- Decided 2026-10-05 (section-level review): approved as drafted; the applied cuts stand and the remaining candidates stay listed; the length is settled by the rendered PDF at assembly (Milestone 15).

### sec2_background_threat_model.md
- Cut applied 2026-10-06 (length decision, option (a): about 24 pages; figures at 80%, T3b and T6b to the appendix, the named prose cuts): §2.3 compressed to two sentences (the route definitions and the controls kept; the detail is in App. C).
- Resolved 2026-10-06 (Milestone 15): the public repository (github.com/Thibaud-Ardoin/LLM-Self-Recognition, MIT) was cloned at commit `7c26938`; its `steering_watermark/param.yaml` sets `hidden_dims: [2048, 64, 64, 32]`, which the locked `research/study1_v02/detect2.py` replicates (asserted by `tables/appA_probe_config.py`); App. A's v0.2 paragraph now states the implemented widths beside the paper's "two hidden layers of width 32" (p. 3).
- §2.1: "very different $\rho$ on the models we tried" takes its numbers from F1/T2 in §5.1 (Milestone 13); none is quoted here by design.
- Decided 2026-10-05 (section-level review): "forgery" throughout with "spoofing" once in parentheses; the section's length (about 1.5 pages against the outline's 1.25) is kept, and the pages are recovered in §5 (Milestone 13).

### sec3_exact_test.md
- Cut applied 2026-10-06 (length decision, option (a)): the pilot paragraph shortened (the S1 never-fired share and S3's per-key maximum stay in Table TA2).
- Decided 2026-10-05 (section-level review): the Rao (1948) citation stays beside GaussMark; the section's length (about 1.3 pages against the outline's 1.0) is kept, and the pages are recovered in §5 (Milestone 13).
- App. B.5's first-order sketch must stay labelled a heuristic unless derived.
- The calibration numbers here are Study 3's gates (G1, G2, H1); the detection results stay in §5.3. Check at assembly that no §5 number is duplicated.

### sec4_setup.md
- Cut applied 2026-10-06 (length decision, option (a)): the pool sizes moved into Table T1's note (generated by `tab1_studies_locks.py` from the registered values).
- Decided 2026-10-05 (section-level review): the compute sentence names the chip ("one Apple-silicon laptop (M5, 16 GB unified memory)"); the section's length (about 1.2 pages of prose plus T1 against the outline's 1.0) is kept, and the pages are recovered in §5 (Milestone 13).
- Confirmed 2026-10-06 (Milestone 15): none of the six lock files names a WikiText prompt set (`grep -il wikitext research/outputs/*/PRE_RUN_LOCK.json` is empty); no §5 result draws on WikiText.
- Study 5's new generation used pool B's first 1,024 prompts and pool D's first 100, the same sets; no new size appears.
- T1 is rendered by `tables/tab1_studies_locks.py`; the assembly script inserts it at the marker above.

### sec5_1_calibration.md
- Quotations and their numbers (p. 1; Table 7, p. 15) re-confirmed by substring search in the `pdftotext` extraction on 2026-10-05; re-check at assembly (Milestone 15).
- "read as damaged" is a reading of the reproduction pilot's sample texts; App. H quotes the degraded genuine fragment and the samples (Milestone 15); the reproduction pilot's own sample texts are quoted in `research/repro/REPRO_PILOT_REPORT_v0.1.md` only. The pilot's perplexity column was exploratory, which T2's note says.
- Cut applied (2026-10-05, length): the 512-token numbers (at most AUROC 0.90 on Qwen2.5-1.5B at ρ = 0.35, ratio 1.25 → 1.27) live in T2 only; restore with `cal512_*` if wanted (Milestone 15: no appendix repeats them).
- Decided 2026-10-05 (section-level review): approved as drafted; §5 kept at 5.07 pages (0.32 page over the 4.75-page target, to be recovered in §6–§9); the applied cuts stand.

### sec5_2_probe_forgery.md
- Cut applied 2026-10-06 (length decision, option (a): about 24 pages; figures at 80%, T3b and T6b to the appendix, the named prose cuts): the version history to Table T1.
- The quotation (p. 5) was re-confirmed in the `pdftotext` extraction on 2026-10-05; re-check at assembly.
- "broken multilingual text" and "word salad" are readings from the v0.2 and v0.4 reports' exploratory sections; App. E and App. H carry the quoted samples and the pre-set sampling rules (Milestone 15).
- Cut applied (2026-10-05, length): the v0.3 loop numbers (76–78% of Route B's texts above the repetition bar at ρ = 0.70; perplexity-only FA 69.0% → 2.5%) live in T3b and App. E.1 (`t3_v03_*`, `ta10_*`; Milestone 15).
- Decided 2026-10-05 (section-level review): approved as drafted; §5 kept at 5.07 pages (0.32 page over the 4.75-page target, to be recovered in §6–§9); the applied cuts stand.
- Final revision 2026-10-08 (Milestone 16, after the Codex review): correction (Claude): the layer-hit maximum over the full budget grid is `ta14_hitsA_max` (the smaller grid of Table T3b gave `t3_v02_A_hits_max`). A fact.

### sec5_3_exact_test.md
- The leakage count and the two Spearman coefficients are re-computed by `tables/tab4_exact_test.py` from the per-key arrays in the locked `results.json` (the report computed them the same way); the file does not store them as such.
- The per-vector heterogeneity sentence paraphrases p. 7 ("Some vectors induce more severe degradations in generation quality, while others are more easily detectable", confirmed 2026-10-05); App. D may quote it.
- Cuts applied (2026-10-05, length): the narrowest-margin sentence (Route A at ρ = 0.70, n = 64: upper bound 42.0% against the 45.0% bar; `s3x_narrowest_A_07_n64_hi`) and the key-1002 sentence (attributed 41.0% at ρ = 0.70, others ≥ 98.0%, FPR 0.1%; `s3x_key1002_*`) are placed in App. D.2 (Milestone 15); the p ≤ 0.001 reading is in T4's note.
- Decided 2026-10-05 (section-level review): approved as drafted; §5 kept at 5.07 pages (0.32 page over the 4.75-page target, to be recovered in §6–§9); the applied cuts stand.

### sec5_4_stealing.md
- Decided 2026-10-05 (section-level review): F4 has no tuning-key row (`fig4_stealing_vs_budget.py --pilot` still renders the labelled variant as `build/F4_pilot.png`, unused); the pilot numbers stay in the text and Table TA5.
- The token-level budgets (30,000 responses; 2.2 million tokens; 2,000 texts) are the gate's page-confirmed quotations, restated from §2.2 without re-quoting.
- Decided 2026-10-05 (section-level review): approved as drafted.

### sec5_5_scrubbing.md
- The authors' Table 3 reading (attribution accuracy between two steered variants; MLP 99.1 → 89.3 under paraphrase, cosine 84.6 → 77.8) is the gate's page-confirmed reading (p. 6); App. F may quote the numbers if the comparison is drawn there.
- The key-1002 reading (attributed 41% before scrubbing at ρ = 0.70; scrubbed by random edits 35% of the time) is placed in App. D.3 with its registered values (`s2_key1002_*`; Milestone 15).
- Cuts applied (2026-10-05, length): the 10%-edit numbers (attribution 40.0% at ρ = 0.70 with 3.5% passing fluency; `s2_Etrue10_*`) and the probe-on-paraphrases numbers (79.0–100.0% accepted at ρ ≥ 0.50 against the exact test's 35.0–66.0%; `s2_probe_para_hi_*`, `s2_S4_para_hi_*`) are placed in App. F.1 and F.4 (Milestone 15).
- Decided 2026-10-05 (section-level review): approved as drafted; §5 kept at 5.07 pages (0.32 page over the 4.75-page target, to be recovered in §6–§9); the applied cuts stand.
- Final revision 2026-10-08 (Milestone 16, after the Codex review): correction (Claude): the originals' range is the minimum and maximum over strengths (new registered names `s2_P1_min`, `s2_P1_max`), not the endpoint strengths. A fact.

### sec5_6_keyed.md
- Cut applied 2026-10-06 (length decision, option (a): about 24 pages; figures at 80%, T3b and T6b to the appendix, the named prose cuts): the point-of-difference paragraph to one sentence; Pang et al.'s 91% → 13% (p. 6) and Jovanović et al.'s quotation (pp. 19–20) are carried by §6.
- The Pang et al. (pp. 6, 7) and Jovanović et al. (pp. 19–20) numbers and quotation are the gate's page-confirmed readings; re-confirm by substring search at assembly.
- The per-context attacker's data starvation (about 1,878 contexts estimated from 1,024 texts for h = 1, covering 0.800 of a genuine text's positions; 61 eligible contexts for h = 4) is in App. C with its registered values (`s5_h1_*`, `s5_h4_*`).
- Cuts applied (2026-10-05, length): the gates' per-key ranges and the largest-cluster rule's FA (88% and 89%; `s5x_add_*_largest_FA`) are in T6a and App. G.2 (Milestone 15); Jovanović et al.'s spoofing success with k = 2–4 keys (0.68–0.81) is in §6.
- Decided 2026-10-05 (section-level review): approved as drafted; §5 kept at 5.07 pages (0.32 page over the 4.75-page target, to be recovered in §6–§9); the applied cuts stand.

### sec5_7_tradeoff.md
- The three "not the first to note" citations (SEEK p. 1; Pang et al. p. 1; Self-Recognition p. 2; Jovanović et al. p. 9) are the gate's page-confirmed quotations; §6 (related work) will quote them, so this paragraph only cites.
- Decided 2026-10-05 (section-level review): approved as drafted; §5 kept at 5.07 pages (0.32 page over the 4.75-page target, to be recovered in §6–§9); the applied cuts stand.

### sec6_related_work.md
- Cut applied 2026-10-06 (length decision, option (a)): the SynthID-Text sentence to a citation (its $H = 4$ and several keys are in App. I); the SAEMark and Zenodo sentence removed (both entries stay in the bibliography, uncited).
- Every quotation re-confirmed by substring search in the `pdftotext` extractions on 2026-10-05 with its PDF page: Jovanović et al. pp. 1, 3, 6, 9, 20 (Table 14's 0.81/0.81/0.68 and 0.80/0.78/0.73 read on p. 20); Pang et al. pp. 5, 6, 7; Gu et al. pp. 2, 19–20; Zhang et al. pp. 8, 18; MarkSec pp. 2, 3, 8; SEEK p. 1; KGW pp. 4, 6, 7; Reliability pp. 17, 21; SynthID-Text pp. 2, 6; Self-Recognition pp. 5, 7, 14; SLAM pp. 2, 5, 7, 8 (and the four words searched and absent); AWM pp. 2, 3; GaussMark pp. 11, 19, 48. SAEMark's "without altering model logits" is from its abstract (arXiv API, 2026-10-05), not a PDF page.
- The ETH SRI blog page timed out on 2026-10-05 and was fetched on 2026-10-06 at the final gate; its 4% / 15% / above-90% figures are confirmed in the page text and quoted in App. I with the date read; this section still cites the post only through App. I (length).
- Final gate, 2026-10-06 (`research/FINAL_GATE_v0.1.md`): one concurrent work added to the score-test paragraph, Chen et al. (arXiv:2610.04907, posted 2026-10-04; the word watermark does not occur in it), labelled concurrent; its quotation is from PDF p. 1, confirmed by substring search; no new predecessor of any claim was found.
- The numbers in this section are quotations from the cited papers (typed with their pages), not results; none is a registered value by design.
- Cuts applied before the review (2026-10-05, length; the first draft ran 1,087 words against the 810-word budget): the Nemecek et al. verification sentence (App. I); the KGW "no observable bias when averaging over a large number of separately generated strings" quotation, now paraphrased; the SEEK p. 29 clause ("embedding watermark signals deeper within the model"); the ETH SRI blog clause; Pang et al.'s Guideline #2 quotation, now paraphrased (quoted in full in the gate §3); KGW's h = 1 leak quotation (p. 6), now paraphrased; Jovanović et al.'s "has only blackbox access to full generations" (p. 3), now paraphrased; SLAM's HMAC quotation (p. 5), now paraphrased; GaussMark's p. 48 quotation, now paraphrased; the Jovanović et al. quality-metric clause (its judge is named on p. 10 of the PDF, not pp. 6–7 as the gate read it; re-check before restoring). Remaining candidates if the review wants 810 words: the SynthID-Text sentence to a citation; the SAEMark and Zenodo sentence. Restore any of these as a wording call.
- Rule 10's citations are placed here in full: the trade-off (SEEK p. 1; Jovanović et al. p. 9; Pang et al. p. 1 and Self-Recognition p. 2 are cited in §5.7), per-key heterogeneity (Self-Recognition p. 7), the repetition flaw (p. 14), the probe's susceptibility (p. 5), the provenance conclusion (Gu et al. p. 2; Pang et al. p. 5).
- Decided 2026-10-05 (section-level review): approved as drafted; the applied cuts stand and the remaining candidates stay listed; the length is settled by the rendered PDF at assembly (Milestone 15).

### sec7_limitations.md
- Cut applied 2026-10-06 (length decision, option (a): about 24 pages; figures at 80%, T3b and T6b to the appendix, the named prose cuts): the quality paragraph to two sentences.
- Bound by the gate's §2 not-claimed list, §4, §9 and decision 4 (future work), and by every protocol's "not claimed" section; the inconclusive verdicts listed are the gate's rule 5 list.
- The token-level budgets are cited in §5.4 with the access caveat and are not repeated here as numbers.
- Length: the outline's budget is 0.75 page (about 490 words); count before the review and name the cut (candidate: the quality paragraph to two sentences, since Appendix E carries the detail).

### sec8_reproducibility.md
- Cut applied 2026-10-06 (length decision, option (a): about 24 pages; figures at 80%, T3b and T6b to the appendix, the named prose cuts): the model list compressed (revision and roles to Appendix A).
- Decided 2026-10-06 (Yichen, Stage 9 decision (a)): a public snapshot repository (`activation-watermark-security`, private until posting; MIT for code, CC BY 4.0 for text and figures), without weights or the generated corpora; the statement is written in; §1's and the abstract's last sentences stand. The snapshot is built by `tools/make_public_snapshot.py` at the posting commit.
- Licence names were taken from the terms-of-use check (`research/stage4/TERMS_OF_USE_CHECK.md`, Hugging Face card metadata read 2026-09-25) and re-read from the Hugging Face API at the final gate (2026-10-06): unchanged (apache-2.0, apache-2.0, mit, llama3.2, llama3.2, apache-2.0), and each card's current revision equals the pinned one in its manifest.
- The compute sentence names the chip as decided for §4 (2026-10-05).
- Length: the outline's budget is 0.5 page (about 325 words); candidate cut: the model list to a sentence pointing to Appendix A.

### sec9_conclusion.md
- §9 follows the outline's row 9 (four sentences: the deployer's lesson, the exact test with its stealing cost, the keyed directions as a transfer with a measured price, the call for keyed verification tools with per-key calibration); the regulator vocabulary is rule 12's.
- The AI-use paragraph follows the outline's §8 placement for arXiv (acknowledgements, after the conclusion and before the references); the ICLR workshop variant moves it to an "LLM usage" section, the NeurIPS variant keeps it here. Decided 2026-10-06 (Yichen, Stage 9 decision (b)): the author line "Yichen Zhao (Independent Researcher; alexyczhao@gmail.com)" on the title page (`assemble.py`), "This work received no external funding." and no thanks line; the AI-use paragraph's wording stands for his full read.

### appA_protocols_locks.md
- Resolved 2026-10-06 (Milestone 15): the v0.1 gate numbers are registered by `tables/appA_v01_gate.py` from `research/outputs/study1_v0.1/qwen/G1_STATE.json`, the runner's stop state copied unchanged from the run's data folder with its hash (logged).
- Decided 2026-10-06 (Yichen, Stage 9 decision (c)): the holdout stays sealed for follow-up work; the sentence now says so.

### appB_exact_test_detail.md
- Resolved 2026-10-06 (Milestone 15): B.4 cites the I4 addendum's agreement with the values registered by `tables/tabA13_defence_detail.py`.
- The combination paragraph quotes false-positive ranges across strengths; the per-strength values are in Table TA3b, and the §5.3 text must not repeat them.

### appC_attackers.md
- C.3: the layer-search forgery set exists only at $n = 256$; state this in the §5.4 text when it quotes the number.
- C.5: the cluster records at $n = 64$ and $n = 1{,}024$ are in Table TA4d; the addendum's every-cluster forgeries (App. G, Milestone 15) must carry the "post hoc" label in every table and figure that shows them.
- Resolved 2026-10-06 (Milestone 15): the editor's constants were confirmed against the locked `research/study2_pilot/scrub_core.py` (`TOPK_POOL = 40`, `PLAUS = log 3`, `N_CAND = 10`, `S_FD = 2.0`, `MIN_GAP = 2`); the code's `BUDGETS` also lists 20%, which Study 2 did not record (the locked results hold 2, 5 and 10%).

### appD_per_key.md
- Every number here is a registered value from `tabA6`–`tabA9`, `tab4`, `tab5`, `tabA12`, `figA1` and `figA2`; the §5.3 and §5.5 cuts (`s3x_narrowest_A_07_n64_hi`, `s3x_key1002_*`, `s2_key1002_*`) are placed in D.2 and D.3 as their open items name.
- The probe's per-key acceptance rates were not stored by Study 3's run, so Table TA7a carries the probe's median only.

### appE_quality.md
- E.1's "broken multilingual token soup" and E.2's readings are the reports' exploratory readings (v0.2 §4; v0.4 §5), labelled; the quoted fragment and the word-salad sample's numbers are registered by `appH_samples.py` from the generated report and the locked results.
- The quotation (p. 14) was re-confirmed by substring search on 2026-10-06 (reading-order extraction); SLAM's four quality axes (p. 8) are cited, not quoted.
- Final revision 2026-10-08 (Milestone 16, after the Codex review): correction (Claude): v0.3's fluency bar is the key's genuine 95th percentile (the v0.3 protocol; `FLUENT_Q = 0.95`), not the median. A fact.

### appF_scrubbing_secondaries.md
- The §5.5 cuts (`s2_Etrue10_*`, `s2_probe_para_hi_*`, `s2_S4_para_hi_*`) are placed in F.1 and F.4 as its open item names; the C11 lead is labelled in F.4 and nowhere stated as a result.
- The Table 3 numbers (99.1 → 89.3; 84.6 → 77.8; p. 6) are the gate's page-confirmed reading; re-confirmed by substring search on 2026-10-06 (see the Milestone 15 log entry).
- Rotation's detection after paraphrase is not in the locked Study 5 results file and is not quoted anywhere in the paper (Appendix G).

### appG_defence_detail.md
- The addendum carries the "post hoc" label in its heading, in Table TA13b's caption, in Table T6's row and in Figure F6's hollow marker (rule 6); the §5.6 cuts (`s5x_add_*_largest_FA`) are placed in G.2.
- The pilot's values are registered by `tabA13_defence_detail.py` from `study5_pilot_v0.1/results.json` and `ADDENDUM_I4.json`; the I4 agreement answers App. B.4's open item.

### appH_samples.md
- Every excerpt and every number here is registered by `tables/appH_samples.py` from the locked `results.json` files (v0.4, Study 2) or from the generated reports and the report builder's `samples.md` (v0.3, Study 5); nothing is retyped. The readings are the reports' descriptive readings, paraphrased.
- The excerpts are shortened to the stated word counts; the reports quote the first 80 words (Study 1) or the full texts (Studies 2 and 5).
- Decided 2026-10-08 (Yichen, O4): the C4 prompt excerpt is cut to its first clause by `appH_samples.py` (`first_clause`), replacing the 30-word excerpt; the generated texts are quoted as before.

### appI_regulators.md
- Every quotation was re-confirmed by substring search in the reading-order `pdftotext` extraction on 2026-10-06 with its page: the Code pp. 9, 13, 15, 16, 17, 18; the guidelines pp. 25, 26; NIST pp. 13, 19, 20, 38 (the gate's §8 pages, unchanged). The NIST "Secure:" lead-in splits across a line and is paraphrased; the quoted clause is on p. 13.
- The ETH SRI page timed out on 2026-10-05; it was fetched on 2026-10-06 at the final gate (`research/FINAL_GATE_v0.1.md`) and its figures were confirmed by substring search in the page text ("adding caching further drops spoofing success to 4%"; "tripling the number of queries from 30k to 90k brings spoofing success back to 15%"; scrubbing "above 90%"); they are quoted above as source figures with the date read, not as registered values.
- Final gate, 2026-10-06: the two Commission documents and NIST AI 100-4 were re-fetched once and are byte-identical to the locked copies (SHA-256 7bd22c5a…, 30861fc5…, a387a497…); the Commission's adequacy opinion of 8 July 2026 (library page read 2026-10-06; the opinion PDF not read) is cited for the Code's status only.
- The Code's documents were fetched once under the Commission's reuse policy (Decision 2011/833/EU, attribution) and NIST's under its public-domain terms, recorded in `research/literature/TERMS_OF_USE_CHECK.md`.

## Internal file references still in the text (review before release; the assembly strips only the `(see build/…)` markers)

- sec4_setup.md: `PRE_RUN_LOCK.json`; `research/outputs/study1_v0.2/results.json`; `research/outputs/study1_v0.3/results.json`; `research/outputs/study1_v0.4/results.json`; `research/outputs/study2_v0.1/results.json`; `research/outputs/study3_v0.1/results.json`; `research/outputs/study5_v0.1/results.json`; `research/study2/common_s2.py`; `research/study2_pilot/scrub_core.py`
- appA_protocols_locks.md: `INPUT_VALIDATION.json`; `PRE_RUN_LOCK.json`; `RUN_MANIFEST*.json`; `research/STUDY*_PROTOCOL_v*.md`; `research/outputs/<study>/PRE_RUN_LOCK.json`; `research/outputs/calibration_v0.1/`; `research/outputs/calibration_v0.2/`; `research/outputs/calibration_v0.3/`; `research/outputs/repro_v0.1/`; `research/outputs/study1_v0.1/`; `research/outputs/study1_v0.2/results.json`; `research/outputs/study1_v0.3/results.json`; `research/outputs/study1_v0.4/results.json`; `research/outputs/study2_pilot_v0.1/`; `research/outputs/study2_pilot_v0.2/`; `research/outputs/study2_v0.1/results.json`; `research/outputs/study3_pilot_v0.1/`; `research/outputs/study3_v0.1/results.json`; `research/outputs/study5_pilot_v0.1/`; `research/outputs/study5_threat_v0.1/results.json`; `research/outputs/study5_v0.1/ADDENDUM_ROTATION.json`; `research/outputs/study5_v0.1/results.json`; `research/stage4/outputs/prompt_sets_v0.3.json`

## Bibliography
- 38 keys cited; every one has an entry. Entries not cited anywhere: ai2026pasa, aremu2026triggertag, belay2026provenance, schafer2026dualsemantic, vargas2026forensic, yu2025saemark.
