# Codex final review v0.1

Written before revisions: 2026-10-08, 14:32 UTC (09:32 CDT). Reviewer: Codex (OpenAI). Baseline: `1283ba23ddd7007a6c9333457faf67a6980a7ca4` on `main`.

**Recommendation: revise the claim summaries and protocol descriptions before posting.** The registered headline measurements reproduce from the stored outputs, but that does not make every sentence or table note correct. The most consequential problems are the known-layer access behind the headline forgery rates, the combined context-keying/rotation summary, the absolute wording about random-key rejection, and the inconsistent fluency definitions. These are decisions for Yichen under the handoff's approved-text rule; the limited changes below marked **do** preserve the claims.

## 1. Claims against evidence

### Review method and source map

Read all 67 pages of `latex/main.pdf`, including references and appendices, in extracted text; visually inspected all pages in contact sheets and inspected dense tables and reference glyphs separately. Read the specified handoff, README, dated decision-log entries, claim list and wording rules. No study was rerun. All 23 table scripts were replayed with `common.BUILD` redirected to a scratch directory outside the repository: all assertions passed and every emitted `values_*.json` equalled its committed counterpart. The assertions check selected hashes, medians, counts and decisions; they do **not** independently regenerate every confidence interval or validate every explanatory sentence. In particular, the gaps in S6 below matter.

The following source IDs identify exact registering scripts and inputs. All paths are repository-relative; output paths begin `research/outputs/`. The numeric inventory at the end lists every placeholder in the abstract, introduction and results, its value, script and source ID, including ancillary figures and calibration readings. The primary files remain unchanged.

| ID | Registering script under `research/paper/` | Locked inputs and assertion coverage |
|---|---|---|
| S1 | `tables/tab1_studies_locks.py` | `study1_v0.2`, `study1_v0.3`, `study1_v0.4`, `study3_v0.1`, `study2_v0.1`, `study5_v0.1`: locks, run manifests, results and corresponding protocols; additionally locked `research/study1/core.py`, `research/study1_v02/common.py` and recorded prompt/quality metadata for constants. Re-hashes protocol/code/results, checks lock commits and reads design constants. The six-study count refers to these six protocol versions, not six distinct study numbers. |
| S2 | `tables/tab2_calibration.py` | `calibration_v0.1/results_{qwen,llama}.json`, `calibration_v0.2/results_{qwen,llama}.json`, `calibration_v0.3/results_llama3b.json`, `repro_v0.1/results_{qwen,llama}.json`, `repro_v0.1/addendum_quality_ppl.json`. Re-derives detectability/fluency flags and absent operating points, checks per-key means, norms and reproduction values. |
| S3 | `tables/tab3_probe_forgery.py` | `study1_v0.{2,3,4}/results.json`. Rechecks medians, gates, R1/R2/R3 and v0.4 F1/F3. Its maximum layer-hit summary covers forgery budgets only, not the full recovery grid. |
| S4 | `tables/tab4_exact_test.py` | `study3_v0.1/results.json`, primary S4. Rechecks calibration, medians, P1, E1, X1, X3; recomputes leakage-cell counts and correlations. Does not assert that every random-key observation is rejected (that claim is false). |
| S5 | `tables/tab5_scrubbing.py` | `study2_v0.1/results.json`. Rechecks per-key medians, calibration and S1/S2/C1 rules. Values are percentages in this file. |
| S6 | `tables/tab6_defence.py` | `study5_v0.1/results.json`, `study5_v0.1/ADDENDUM_ROTATION.json`. Rechecks many per-key summaries, P0/D1/D2/D3 and addendum selection rules. **Limitations:** `d1_verdict` collapses every non-practical case to blocked, omitting the protocol's inconclusive branch; the rotation D2 numerical assertion ends `or True`. Independent review verified all currently blocked cases have every upper bound below their bar, and recomputing paired rotation differences from Study 2 per-key success and Study 5 union success gives 15 and 13 points as stored. No current verdict change was found, but the code's claimed coverage is too broad. |
| S7 | `tables/tabA4_attacker_checks.py` | `study1_v0.4/results.json`, `study5_v0.1/results.json`. Recounts candidate selection and cluster recovery, checks bounds and selected medians; known/search cosines are stored summaries. Figure 4 independently checks the fixed-key known/search medians against per-key values. |
| S8 | `tables/tabA5_threat_check.py` | `study5_threat_v0.1/results.json` and `VALIDATION.json`. Recomputes per-key medians and pilot reading; validates guard agreement. Tuning-key evidence only. |

The handoff's simple locked-path inventory reports 27 bare filenames as absent from the repository root. These are relative lock entries, not 27 missing research files: table-script hash resolution searches the study directories, and the lock tables passed. The preservation check also covers all existing study/pilot source files and output files, rather than relying only on those bare paths.

### Abstract's six findings and introduction's contributions

| Finding / contribution | Evidence and principal placeholders | Assessment |
|---|---|---|
| Abstract 1; contribution 2's calibration clause | S2: `cal_*`, `repro_*` in Section 5.1; model/token scope S1 `new_tokens`. | No measured operating point meets both pre-set probe AUROC and perplexity criteria. Keep “under our conditions” and the base/instruction-tuned distinction. The calibration itself has no numerical result placeholder in the abstract; its numeric support is in Section 5.1. |
| Abstract 2; contribution 2 | S3 `t3_v04_B_n256_FA_med_035` = 19.5%, `t3_v04_bar_035` = 14.3%; S7 `v04_B_median_cos_max` = 0.062. | Practical at rho 0.35, n 256 under v0.4; 0.50/0.70 inconclusive. “Forgeable at either” in both abstract endings exceeds this finding. |
| Abstract 3; contribution 3 | S4 `s3x_oracle_tpr_min/max` = 96.0–100.0%; S1 `fpr_nominal_pct` = 1. | Detection range is correct. Exactness is a level guarantee averaged over keys, not equality of every key's observed FPR. “Never attributes random-key text” is false: medians are zero, per-key rates reach 4%. The arXiv abstract omits “exact on average over keys”. |
| Abstract 4; contribution 4 | S7 `s5_fixed_035_n64_cos_known`, `s5_fixed_05_n64_cos_known` = 0.940, 0.951; S6 `s5x_fixed_{035,05}_n64_FA_med` = 88.0, 85.5%; `s5x_fixed_{035,05}_oracle_FA_med` = 86.5, 90.0%; S3 `t3_v02_A_cos_max` = 0.16. | Values reproduce. The headline forgery rates use the known layer, whereas Section 2 says the attacker never sees it. Layer-search recovery is measured at n 64, but layer-search forgery only at n 256 (Appendix C.3). “As often as” is descriptive proximity, not a tested equivalence claim. “Best estimator” should be restricted to the estimators tested. |
| Abstract 5; contribution 5 | S5 `s2_S1_qwen_025_success_med`, `s2_S1_qwen_035_success_med` = 64.0, 53.0%. | P-Qwen effective at 0.25/0.35 and not effective at 0.50/0.70. P-Phi and E-true at 0.35 remain inconclusive. Scope the “first” claim against related activation schemes' paraphrase evaluations. |
| Abstract 6; contribution 7 | S6 `s5x_arms_FA_med_max` = 9.0%; `s5x_rot_05_n64_cluster_FA_med` = 95%; S1 `n_keys` = 8; S6 `s5x_N_OBS` = 1,024. | Introduction states the distinction substantially better than the abstracts/conclusion: context hashing blocks the tested per-context attacker and improves perplexity; rotation blocks averaging, has unchanged quality, and falls to clustering at 0.50 from n 64. At 0.35 preserve the pre-registered blocked verdict alongside the labelled post-hoc recovery/forgery result. |
| Contribution 1: novelty | Claim gate and cited literature; no study number establishes search absence. | Retain “to our knowledge” and one-scheme scope; see A4 on the contradictory family-wide sentence in Section 6. This review did not rerun a live novelty search. |
| Contribution 6: interpretation | S2 `cal_q15_05_ratio` = 1.62, `cal_q15_07_ratio` = 2.29; S3/S5/S6 above. | Trade-off is explicitly labelled and prior work cited. Abstract/conclusion summaries must carry the same limits. “Quality-neutral” means the specified proxy bars, not human-rated quality. |

Shared abstract/introduction scope comes from S1 (`new_tokens`, `n_keys`, `t1_n_studies`) and S6 (`s5x_N_OBS`). Bare budget, strength and model-size literals remain in the approved source; see Section 2 and A10.

### Section 5 verdict sentences

| Section and verdict | Trace and verification | Mismatch or qualification |
|---|---|---|
| 5.1: no detectable-and-fluent operating point | S2 `cal_auroc_bar`, `cal_ppl_bar`, `cal_*_first_detectable_rho`, `cal_q15_last_fluent_rho`, `cal_n_files`; the script checks the rule for each calibration. | Supported for the actual runs. “512-token texts change neither verdict” applies to the two models with such runs; Llama-3.2-3B has only the 256-token calibration in Table 2. Explicitly qualify that scope (A11). |
| 5.2: R1 fails; Route A not practical at 0.35 and inconclusive above | S3 `t3_v02_A_cos_max`, `t3_v02_A_hits_max`, `t3_v04_A_n64_FA_hi_035`, `t3_v04_A_n256_FA_hi_035`, `t3_v04_A_n256_FA_{med,lo}_07`, corresponding bars. | Verdicts reproduce. “At every strength and budget … at most 2” is incorrect: full-grid `ta14_hitsA_max` = 3 (0.50, n 16). Cosine maximum agrees; the hit maximum uses a different grid. |
| 5.2: Route B R2 practical from n 64, v0.4 practical only at 0.35 | S3 `t3_v02_B_n64_acc_min_late/max_late`, `t3_v02_oracle_acc_*`, `t3_v04_B_n256_FA_med_035`, `t3_v04_bar_035`; S7 cosine bound. | Supported, with the version and fluency distinction retained. High-strength v0.4 remains inconclusive. |
| 5.3: P1 at every strength, E1 stronger at three lower strengths, X3 no, X1 not practical | S4 `s3x_oracle_tpr_*`, `s3x_probe_tpr_*`, `s3x_E1_*`, `s3x_random_exact_max`, `s3x_v04_exactFA_late_min/max`, `s3x_X1_bar_min/max`; primary result rules re-derived. | “No acceptance of generic steering” in the closing paragraph must say median. Same for contribution 3. Per-key leakage is correctly labelled descriptive/inferential. |
| 5.4: fixed-key P0 practical at n 64, both strengths | S6 `s5x_fixed_{035,05}_n64_FA`, `s5x_fixed_{035,05}_oracle_FA`, `s5x_fixed_035_random_FA`; S7 known/search cosines and hit counts. | Known-layer forgery must be explicit in this sentence and every summary quoting it. Layer-search forgery evidence is separately available at n 256; do not silently substitute its outcome or rerun a study. |
| 5.5: S1 effective/inconclusive/not effective, S2 and C1 | S5 `s2_S1_*`, `s2_Etrue_*`, `s2_Eest_success_min/max`, `s2_C1_025/035`; checks all rules against per-key summaries. | Verdicts agree. The opening 97.5–100.0% original-detection range uses endpoint strengths as extrema; 0.35 is 96.0%. Use the actual minimum, on approval. |
| 5.6: D1 hashed blocked, rotation naive blocked, clustering practical at 0.50, 0.35 blocked plus post hoc | S6 `s5x_arms_FA_med_max/hi_max`, `s5x_rot_05_n{64,1024}_cluster_FA_med`, `s5x_add_*`; S7 cluster counts/cosines. | Current decisions agree with full protocol when checked independently; S6 helper lacks a branch. The closing “at both strengths”/“nothing against clustering” cost language should repeat that 0.35 is post hoc and avoid implying an asymptotic cost result. |
| 5.6: D2 material h1 both and h4 at 0.50; h4 at 0.35 inconclusive; rotation immaterial | S6 `s5x_h1_{035,05}_d`, `s5x_h4_{035,05}_d`, `s5x_rot_{035,05}_d`; per-key differences and decisions checked. | Supported. Table A13a's note incorrectly requires the interval to exclude 20; protocol requires median >=20 and lower bound >0. Rotation's 15/13-point loss is immaterial by its rule, not zero loss. |
| 5.6: D3 immaterial, ratios improve, rotation unchanged | S6 `s5x_ppl_ratio_min/max`; script checks per-key ratios and no key above 1.10. | Supported as a perplexity proxy. Abstract sentence wrongly attaches improvement to rotation too. |
| 5.7: cross-study trade-off | S2 ratios; preceding S3–S6 verdicts. | Labelled interpretation, but rotation/post-hoc and known-layer qualifications need to travel into summaries. “Probe detects none of the low strengths” should refer to failing the reliability criterion, not zero detection. |

## 2. Consistency and cross-references

The principal percentages and cosines in the abstract and contributions use the same placeholders as their body counterparts, or corresponding median-only versus median-with-CI forms. The inventory below makes these distinctions reviewable. The following are the material exceptions or duplications:

| Places | Names or descriptions | Finding |
|---|---|---|
| Sections 0/1 versus 5.4 | `s5x_fixed_*_n64_FA_med` versus `s5x_fixed_*_n64_FA`; oracle analogues | Same measurement; latter adds stored CI. Do not force a common string and lose the CI. |
| Sections 0/1 versus 5.5 | `s2_S1_qwen_*_success_med` versus `s2_S1_qwen_*_success` | Same measurement, different presentation with CI. |
| Sections 1/5.2 versus 5.3 | `t3_v04_B_n256_FA_med_035` versus `s3x_v04_B_n256_probeFA_035` | Both 19.5%, from the original and re-scored study's stored probe reading. Retain independent provenance rather than infer equality from formatting. |
| Sections 3 versus 5.3 | `s3_S4_G1_pooled_pct` / `s3x_G1_pct`; `s3_S4_H1_pooled_pct` / `s3x_H1_pct`; per-key min/max versus `s3x_G2_range` | Same S4 calibration, independently registered by `tabA3_s3_s4.py` and `tab4_exact_test.py`: 0.81%, 0.68%, 0.1–1.7%. No numerical mismatch; range formatting differs. |
| Sections 5.2 versus E.3 | `t3_v02_A_cos_max` / `ta14_cosA_max`; `t3_v02_A_hits_max` / `ta14_hitsA_max` | Cosine is 0.16 / 0.160 (precision); layer hits 2 / 3 (different grid, an actual scope mismatch). A5. |
| Section 5.5 versus A16 | `s2_S1_qwen_*_success` / fixed-key `s2_success` in Study 5 | Identical per-key points and medians, different stored bootstrap intervals: rho 0.35, [37.5,64.5] versus [37.9875,64.5]%; rho 0.50, [27,48] versus [26,48.5]%. Table A13a uses Study 2; A16 uses Study 5 recomputation but calls it Study 2. Label provenance or use the original Study 2 interval, on approval; never edit either result. |
| Sections 2/4 versus D.1/E.1/A6/A10 notes | genuine perplexity 95th percentile versus “median” | Code `study1_v03/common3.py:fluent_cut` and `study1_v04/common4.py:cut` use `np.quantile(..., FLUENT_Q)` with FLUENT_Q 0.95. Appendix descriptions/notes are wrong, not the main-text percentile. A5/A8. |
| Section 4 versus C.6 | repetition tolerance multiplied by 1.25 versus no multiplier | `study2_pilot/scrub_core.py:conditions` multiplies only perplexity by `PPL_TOL`; repetition is max(original, reference bar). A5. |

Bare literals that duplicate existing registrations can be changed without changing the displayed measurement: observed-budget ceiling 1,024 -> `s5x_N_OBS`, study key count 8 -> `n_keys`, continuation length 256 -> `new_tokens`, model layer count 28 -> `n_layers`, and applicable null-key counts -> `s3_M`/`s3_M2`. Only replace where the referent is the same. Never use `new_tokens` for a 256-output attack budget or `n_keys` for a coincidentally equal model size. Individual budget points, several strengths and algorithm constants have no suitable existing scalar placeholder; A10 proposes registering them rather than borrowing unrelated equal-valued names. Identifiers (S4, C4, model names, versions), mathematical constants and cited-source quotations need to be distinguished from experimental measurements in a future lint rule.

Cross-reference pass: inspected all section/appendix heading destinations and the table/figure families referred to in the section bodies against the assembled PDF. Source labels are intentionally transformed: T3a -> Table 3; T3b -> Table A15; T6a -> Table 6; T6b -> Table A16; TA/FA -> A. A2a/A2b are panels of Figure A2, not missing standalone figures. Table A12a's companion values are the adjacent unnumbered strict-condition table. No missing numbered destination found. Two defects remain:

* **Rendering:** literal `§` becomes **ğ** in the Tectonic PDF, visibly on page 2 and elsewhere (not just extraction). **Do:** spell out “Section” in section-source cross-references, and “Appendix D.3” for `§D.3`. Generated table notes T1 and T5 also contain it and need a generator fix (A9).
* **Circular prompt reference:** Section 4 points to C.6 for the fixed paraphrase instruction; C.6 points back to Section 4, and neither supplies it. **Do:** name the locked source `research/study2_pilot/scrub_core.py`, `PROMPTS["P2"]`, whose selection is fixed by `research/study2/common_s2.py`, in Section 4 and point C.6 there. This repairs provenance without retyping or changing the instruction.

## 3. Quotations

Reconfirmed every external quotation in Sections 1, 2, 6 and Appendix I against the local PDF extractions, page by page. The inventory below records each occurrence. Normalisation was limited to whitespace, ligatures, typographic punctuation and LaTeX-to-PDF mathematical notation; ellipses were checked as ordered spans on the cited page. No quotation was changed.

Four extraction cases required an explicit second check: (i) Self-Recognition p. 11 puts the exponent d on a separate extraction line; both text spans match and the formula was checked visually; (ii) MarkSec p. 3 breaks “watermark-related” across a line, omitting the hyphen in reading-order extraction; the layout extraction preserves it; (iii) GaussMark p. 11 inserts a space before the comma after X; (iv) Chen et al. p. 1 uses a mathematical Delta glyph and spaced F Delta; the source has “point”, and the manuscript's `[s]` is an explicit grammatical interpolation. These are not quotation-content failures. The verdict words “blocked” and “generic steering suffices” are internal labels, excluded from external-quotation certification. Appendix I's final “paraphrasing” matches the Code p. 18.

The ETH SRI figures are a cited paraphrase of a webpage, not a PDF quotation; the 2026-10-06 recorded source check was read, but the page was not independently fetched in this review. The Commission opinion PDF was not supplied/read, as the final gate itself records. No new claim about either source's current status is made here.

## 4. Wording rules

This is a qualified review, not a blanket compliance pass.

| Binding rule | Result |
|---|---|
| 1: qualified novelty | Headline/title conform. The introduction's recovery/scrubbing “first” subclaims and Section 6's family-wide absence statement need review together (A4). |
| 2: transfers and originators | Named and cited in the body. Abstracts name the transfers but the short metadata version drops some attributions; retain GaussMark and token-level origins when revising A1. |
| 3: exact on average over keys | Correct in Section 3, PDF abstract, limitations and B.4; absent from the metadata abstract. A1. |
| 4: attacker, budget, access | Opening scope exists but many later security sentences rely on it. The known-layer exception is substantive, not merely repetition. A2/A11. |
| 5: bounds and inconclusive outcomes | Detailed results retain most inconclusive outcomes. Abstract “forgeable at either”, calibration's 512-token clause and generic median-rate summaries need narrowing. A1/A3/A11. |
| 6: rotation at 0.35 | Detailed 5.6/G.2 and addendum table/figure mark it. Abstracts, conclusion and some cross-study cost language do not carry the distinction. A1/A11. |
| 7: re-implemented probe and fair reproduction | Detailed 5.1/5.2 conform; metadata abstract omits “re-trained by us”. Keep the differing conditions and authors' Table 7 numbers. A1. |
| 8: quality proxies | Explicit in 4/7/E; abstract “quality-neutral” and “acceptable” need reading as proxy-defined. No human judgement was collected. |
| 9: exploratory/inferential labels | Most detailed passages conform. Section 9's “does not detect the key so much as steering”, Section 3's opening “detects a learned footprint”, and C.2's near-orthogonality “by construction” need qualification (A7). |
| 10: credit for known effects | Appropriate citations appear in 1/5/6. Preserve them through any shortening. |
| 11: generated numbers | Primary result placeholders resolve. Existing bare experimental constants remain widespread. Safe substitutions D3; complete solution A10. |
| 12: regulators as motivation only | Explicit disclaimers remain in 1/I. No new compliance assertion is needed. Preserve them. |

Section-level pass: 0 (PDF and metadata): A1–A3; 1: A2–A4/A7/A11; 2: A2/A10 and D2/D4; 3: A7/A10 and D4; 4: A5/A10 and D2/D4; 5.1: A11; 5.2: A5; 5.3: A3; 5.4: A2/A7; 5.5: A5; 5.6: A1/A8/A11; 5.7: A1/A7/A11; 6: A4/A7 and D4; 7: A2/A11; 8: no additional claim defect found; 9: A1/A2/A7/A12; A: retain locked protocol distinctions; B: A7; C: A2/A7 and D2; D: A3/A5/A11; E: A5; F: no additional verdict defect found; G: A8/A11; H: O4; I: source-access limitations above. D1 reference rendering applies throughout. This does not certify literal repetition of every scope clause in every security sentence; A11 asks Yichen how to implement that rule.

## 5. Prose

**Do:** split Section 2.3's two very long sentences into route, screening, scrubbing and control paragraphs, preserving all mechanisms, numbers, access clauses and version labels. Expand the first authorial uses of MLP and AUROC; expand FPR/TPR when introducing their meanings in the text. Change authorial “judgment” to British “judgement”. Replace non-quoted narrative “spoofing” by “forgery” where it is only a synonym, leaving the single parenthetical definition in Section 2.2 and all source quotations intact. Do not alter the source's “trivially reproduce” or American spellings inside quotations.

No em dash was found in running authorial section prose; the appendix-heading separators are structural and are recognised by `make_latex.py`, so retain them. Mathematical symbols are mostly defined locally. `F` is the Fisher information in the heuristic; `h` and `K` are defined with the defence. Sentence splitting must not accidentally make the Study 1 screening rule a rule for every Route A′ attacker. Correcting the fact that the repetition screen arrived in v0.4 rather than v0.3 touches the stated method and is A5, not a silent stylistic fix.

The abstract's open item still says the arXiv cut “will need” to be written, despite its approval on 2026-10-06. **Do:** update that record to the existing decision without deciding whether to shorten the PDF abstract. The existing metadata body is 1,912 characters, within its stated 1,920 limit; it has only eight characters of room for substantive corrections, so A1 needs a fresh concise version.

## 6. Rendering

Baseline LaTeX: 67 total pages; references begin on page 26, so the generator reports 25 main pages. Acknowledgements spill onto page 26 before the references: “25” is the tool's pages-before-references convention, not a claim that every main-text line fits before page 26. HTML baseline: 60 total, 24 main by its own convention.

There are **123 overfull hboxes, 34 greater than 5 pt, maximum 13.70056 pt**. Larger warnings are concentrated in the T1/A1 lock columns, A2's repeated AUROC headings, A3's calibration headings, A4a's candidate header, A12b's paraphraser label and A16's detection/verdict columns. Visual checks show real collisions: A2's TPR/AUROC headers run together (page 34), and A12b's “paraphraser” collides with the first key heading (page 56). A3 (page 35) is also crowded. The old “none visible at reading size” record is not a sufficient acceptance criterion. Figures and their legends remain readable when enlarged; the twelve figure PDFs are present. References are rendered with numeric citations; six uncited master entries are deliberately excluded from the printed bibliography.

D1 fixes section-source reference glyphs. A9 proposes generator-level fixes for the remaining glyphs and dense tables. No generated TeX, Markdown, figure or PDF will be edited by hand. Page shifts will be checked after rebuilding; a length target is not a reason to remove bounds or labels.

## 7. The four existing wording calls

* **O1, Appendix A rule text:** **(a) Keep the current rule detail (recommended)** until the protocol-description inconsistencies are resolved; it gives readers the actual decision bars. (b) Retain names/bars only and point to the protocols; shorter, but readers must switch documents to audit decisions.
* **O2, B.5 heuristic:** **(a) Keep it in the appendix (recommended)** with its heuristic label and assumptions; it is too conditional for a compact footnote. (b) Move a short statement to a Section 3 footnote while retaining the full sketch as supplementary material; less interruption, more fragmentation.
* **O3, C.1 decoder-body implementation clause:** **(a) Keep it (recommended)** because the extraction point matters for reproducing feature definitions. (b) Move the clause to the implementation documentation and retain a pointer; smoother prose, less self-contained reproducibility.
* **O4, H.1 C4 prompt excerpt:** **(a) Cut to its first clause (recommended)** if that still explains the list-continuation artefact; it reduces third-party prose without weakening the research reading. (b) Keep the existing 31-word excerpt under the recorded rights analysis; more context. The excerpt is generated by `appH_samples.py`, so option (a) requires approval for a generator edit/new registered excerpt; do not hand-edit its filled text. This call is in the final gate/decision log but missing from the collected Part 1 list; it remains open here.

Part 1 also contains already-decided availability/title entries because its collector matches wording mechanically. Do not reopen those decisions merely because they appear there.

## 8. Proposed revisions: do and ask

### Do now, section sources only

* **D1 — Reference rendering:** spell out Section/Appendix cross-references in section bodies; leave source quotations, numbered destinations and generator labels unchanged. This repairs the visible section-symbol defect.
* **D2 — Paraphrase prompt provenance:** replace the circular Section 4/C.6 references with the locked `PROMPTS["P2"]` source and its selector, without changing any instruction or attack parameter.
* **D3 — Existing placeholders:** replace only semantically identical bare constants with already registered names, principally the observed-budget ceiling, study-key count, token length, model layer count and null-key counts. Preserve rendering in math by placing comma-formatted values outside math. No new number is typed; no unrelated placeholder is borrowed.
* **D4 — Clarity and terminology:** split Section 2.3 without changing its method claims; define MLP/AUROC/FPR/TPR in authorial text; British spelling; use forgery in non-quoted narrative synonyms. Keep direct quotations unchanged.
* **D5 — Records:** resolve the stale arXiv-cut open item using the logged approval; append a review record to every edited section. Update the decision log after each coherent step and the handoff at the end.

### Ask Yichen: recommendations first

The handoff §3.5 and §5.2 reserve claim, verdict, characterisation, bound and label changes to Yichen; §3.6 reserves AI-disclosure wording. Therefore even clear corrections below are proposed, not silently applied. Changes to table/build scripts are additionally outside the requested section-only revision pass.

* **A1 — Abstracts/conclusion, highest priority.** **(a) Narrow the six-finding summaries (recommended):** practical probe forgery at the one supported strength; known-layer qualification from A2; “exact on average over keys”; hashed-arm blocking/perplexity improvement separately from rotation's unchanged quality and clustering failure; preserve the 0.35 blocked/post-hoc distinction. Rewrite the metadata cut to remain within its limit, preserving six findings. (b) Shorten both abstracts around the supported findings and put detailed defence outcomes in the body; clearer but changes the approved structure. Neither option treats “forgeable at either” or unqualified rotation blocking as supported.
* **A2 — Known-layer versus hidden-layer threat, highest priority.** **(a) Report both accesses explicitly (recommended):** keep n-64 known-layer forgery percentages labelled as such, retain n-64 layer-search recovery, add the existing n-256 layer-search forgery result with its registered values (`s5_fixed_*_forge_search_FA`, `s5_fixed_*_forge_search_n`). Scope Section 2/C.1's “never sees l” to the hidden-layer arms. (b) Make the n-256 layer-search result the primary forgery summary and move known-layer n-64 rates to a secondary clause. No new experiment is authorised or needed for either wording option.
* **A3 — Medians and absolute rejection.** **(a) Replace universal language by the measured statistic (recommended):** zero median random-key acceptance, bounded per-key leakage; D.5's all-under-3% statement limited to the primary study-key calibration sets in Figure A1. State that rotation forgery rates are means over one corpus, unlike per-key medians. (b) Remove universal summaries and point to the per-key tables. The stored random-key maximum per key is 4%; S3 has 3.4%, and fresh-key FPRs exceed the gate, so blanket statements cannot stand as numerical facts.
* **A4 — Related-work characterisation and novelty.** **(a) Replace Section 6's “no member … recovery, forgery or scrubbing” with the specific unmeasured key-recovery/forgery question for Self-Recognition under this threat (recommended)**; acknowledge the paraphrase/evading results already described for SLAM/AWM and revisit the first-scrubbing wording in Section 1. (b) Drop the family-wide absence sentence and keep the individual comparisons. “Every attack is token-level and black-box” also needs scope to the cited evaluations; do not imply an exhaustive theorem about the literature.
* **A5 — Protocol and descriptive errors.** **(a) Correct descriptions to locked code/results (recommended):** D.1/E.1 genuine PPL cut is a 95th percentile; Section 4 multiplies only PPL, not repetition, by 1.25; Section 5.2's full recovery-grid maximum is `ta14_hitsA_max`; Section 5.5 originals span the actual min/max, including `s2_P1_035`; Section 2.3 distinguishes v0.3's PPL screening from v0.4's repetition screening. (b) Replace each disputed shorthand with a pointer to the exact protocol and table, preserving current verdicts. Do not change locked values to make prose true.
* **A6 — Duplicate uncertainty summaries.** **(a) Use Study 2's original fixed-key CI in every comparison table, with Study 5 paired-difference intervals retained (recommended)**; this needs an unlocked table-script edit. (b) Keep both locked summaries and explicitly label Study 5's rebootstrap of the same Study 2 observations. Do not average intervals or overwrite a locked result.
* **A7 — Inference and cryptographic strength.** **(a) Use measured/heuristic wording consistently (recommended):** the probe interpretation is “consistent with”; the gradient estimator is best among those tested, not proven optimal; C.2's dense direction is empirically nearly orthogonal rather than guaranteed by sparsity; Section 3/B.4 should call the implemented SplitMix construction a deterministic keyed mixing function and avoid “no one without it” or a cryptographic PRF guarantee not established by these experiments. (b) Remove the stronger explanatory/security sentences and retain the measurements plus labelled B.5 heuristic. A cryptographic upgrade would be a new study and is not proposed in this revision pass.
* **A8 — Table notes and assertion coverage.** **(a) Authorise a small unlocked generator correction pass (recommended):** A6/A10 percentile notes, A14b's Route B description (dense mean, not a fitted probe) and R1 bar (median cosine >=0.9 and layer hit >=7/8, not cosine >=0.5 for half); A13a's D2 rule; full D1 inconclusive branch in T6; replace its `or True` with the actual paired-difference assertion. Also align D3 equality at 1.10 with the protocol (current outputs are away from this boundary). Rebuild and compare values/verdicts, which should remain unchanged. (b) Keep scripts unchanged for this pass and resolve them as an explicit pre-posting blocker; section-only edits cannot correct their generated notes.
* **A9 — Rendering generators.** **(a) Authorise generator fixes (recommended):** map § safely or spell out its two generated table-note references, and restructure A2/A3/A12b/A16 headings/column layouts; keep all data and captions. (b) Leave those tables pending a separate layout pass; the current collisions are visible and should be resolved before posting. Do not patch generated TeX.
* **A10 — Remaining bare experimental constants.** **(a) Register missing scalar budgets/strengths/algorithm constants from locked code/protocol/results and replace them consistently (recommended)**, with semantic names and a lint check excluding quoted sources, identifiers and mathematical constants. (b) Explicitly revise the handoff convention to permit audited fixed design constants while requiring measured results to be placeholders. Until Yichen chooses, safe D3 substitutions are partial compliance, not a claim that every number is generated.
* **A11 — Scope and post-hoc labels everywhere.** **(a) Apply concise local qualifiers wherever a summary could be read independently (recommended)**, including the 512-token calibration restriction, known-layer access, rotation 0.35 post hoc and the absence of a measured asymptotic cost; state “fails the detectability criterion” rather than “detects none”. Replace the all-rates-are-medians assertions in 1/7/D with the correct exceptions. (b) Adopt an explicit convention that a paragraph-opening scope governs the rest of that paragraph, then audit summaries/headings separately; this relaxes the literal every-sentence wording rule and needs Yichen's decision.
* **A12 — AI-use paragraph.** **(a) Add after the existing Claude sentence (recommended):** “Codex (OpenAI) assisted with the final review and revision; the author reviewed and approved the changes.” Apply only after Yichen actually reviews/approves the revisions. (b) Use “The text and code were drafted with Claude (Anthropic), and the final review and revision were assisted by Codex (OpenAI), under the author's direction.” Preserve author responsibility and no-AI-authorship statements. The conservative source edits below do not authorise changing this disclosure silently.

O1–O4 above are also decisions for Yichen. No decision about publication, email, public snapshot or visibility is made in this memo.

## Evidence inventory

### Numerical placeholders in the abstract, introduction and Section 5

Each row groups placeholders by section and registering script. Values are quoted from the existing registries, which reproduced byte-for-byte in substance in the scratch replay. Source IDs refer to the source/assertion map in Section 1. This is a provenance record, not a new source for paper numbers.

#### sec0_abstract.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `cal_q15_05_ratio` | 1.62 | `tables/tab2_calibration.py` / S2 |
| `cal_q15_07_ratio` | 2.29 | `tables/tab2_calibration.py` / S2 |
| `fpr_nominal_pct` | 1 | `tables/tab1_studies_locks.py` / S1 |
| `n_keys` | 8 | `tables/tab1_studies_locks.py` / S1 |
| `new_tokens` | 256 | `tables/tab1_studies_locks.py` / S1 |
| `s2_S1_qwen_025_success_med` | 64.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_035_success_med` | 53.0 | `tables/tab5_scrubbing.py` / S5 |
| `s3x_oracle_tpr_max` | 100.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_oracle_tpr_min` | 96.0 | `tables/tab4_exact_test.py` / S4 |
| `s5_fixed_035_n64_cos_known` | 0.940 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_05_n64_cos_known` | 0.951 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5x_N_OBS` | 1,024 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_035_n64_FA_med` | 88.0 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_035_oracle_FA_med` | 86.5 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_n64_FA_med` | 85.5 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_oracle_FA_med` | 90.0 | `tables/tab6_defence.py` / S6 |
| `t1_n_studies` | 6 | `tables/tab1_studies_locks.py` / S1 |
| `t3_v04_B_n256_FA_med_035` | 19.5 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_bar_035` | 14.3 | `tables/tab3_probe_forgery.py` / S3 |

#### sec0_arxiv_abstract.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `fpr_nominal_pct` | 1 | `tables/tab1_studies_locks.py` / S1 |
| `n_keys` | 8 | `tables/tab1_studies_locks.py` / S1 |
| `new_tokens` | 256 | `tables/tab1_studies_locks.py` / S1 |
| `s3x_oracle_tpr_max` | 100.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_oracle_tpr_min` | 96.0 | `tables/tab4_exact_test.py` / S4 |
| `s5_fixed_035_n64_cos_known` | 0.940 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_05_n64_cos_known` | 0.951 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5x_N_OBS` | 1,024 | `tables/tab6_defence.py` / S6 |
| `t1_n_studies` | 6 | `tables/tab1_studies_locks.py` / S1 |

#### sec1_introduction.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `cal_q15_05_ratio` | 1.62 | `tables/tab2_calibration.py` / S2 |
| `cal_q15_07_ratio` | 2.29 | `tables/tab2_calibration.py` / S2 |
| `fpr_nominal_pct` | 1 | `tables/tab1_studies_locks.py` / S1 |
| `n_keys` | 8 | `tables/tab1_studies_locks.py` / S1 |
| `new_tokens` | 256 | `tables/tab1_studies_locks.py` / S1 |
| `s2_S1_qwen_025_success_med` | 64.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_035_success_med` | 53.0 | `tables/tab5_scrubbing.py` / S5 |
| `s3x_oracle_tpr_max` | 100.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_oracle_tpr_min` | 96.0 | `tables/tab4_exact_test.py` / S4 |
| `s5_fixed_035_n64_cos_known` | 0.940 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_05_n64_cos_known` | 0.951 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5x_arms_FA_med_max` | 9.0 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_035_n64_FA_med` | 88.0 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_035_oracle_FA_med` | 86.5 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_n64_FA_med` | 85.5 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_oracle_FA_med` | 90.0 | `tables/tab6_defence.py` / S6 |
| `s5x_rot_05_n64_cluster_FA_med` | 95 | `tables/tab6_defence.py` / S6 |
| `t1_n_studies` | 6 | `tables/tab1_studies_locks.py` / S1 |
| `t3_v02_A_cos_max` | 0.16 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_B_n256_FA_med_035` | 19.5 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_bar_035` | 14.3 | `tables/tab3_probe_forgery.py` / S3 |
| `v04_B_median_cos_max` | 0.062 | `tables/tabA4_attacker_checks.py` / S7 |

#### sec5_1_calibration.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `cal_auroc_bar` | 0.95 | `tables/tab2_calibration.py` / S2 |
| `cal_l1b_first_detectable_rho` | 0.70 | `tables/tab2_calibration.py` / S2 |
| `cal_l3b_07_auroc` | 0.86 | `tables/tab2_calibration.py` / S2 |
| `cal_n_files` | 5 | `tables/tab2_calibration.py` / S2 |
| `cal_ppl_bar` | 1.25 | `tables/tab2_calibration.py` / S2 |
| `cal_q15_025_ratio` | 1.13 | `tables/tab2_calibration.py` / S2 |
| `cal_q15_first_detectable_rho` | 0.50 | `tables/tab2_calibration.py` / S2 |
| `cal_q15_last_fluent_rho` | 0.35 | `tables/tab2_calibration.py` / S2 |
| `levels_all` | 0.25, 0.35, 0.50, 0.70 | `tables/tab1_studies_locks.py` / S1 |
| `repro_l1b_a5_auroc` | 1.00 | `tables/tab2_calibration.py` / S2 |
| `repro_l1b_a5_ppl` | 32.6 | `tables/tab2_calibration.py` / S2 |
| `repro_l1b_a5_rho` | 1.29 | `tables/tab2_calibration.py` / S2 |
| `repro_l1b_van_ppl` | 5.6 | `tables/tab2_calibration.py` / S2 |
| `repro_l3b_a5_rho` | 0.67 | `tables/tab2_calibration.py` / S2 |
| `repro_q15_a5_best_auroc` | 0.57 | `tables/tab2_calibration.py` / S2 |
| `repro_q15_a5_rho` | 0.10 | `tables/tab2_calibration.py` / S2 |
| `s3x_oracle_tpr_025` | 97.5 | `tables/tab4_exact_test.py` / S4 |

#### sec5_2_probe_forgery.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `t3_v02_A_cos_max` | 0.16 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_A_hits_max` | 2 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_B_n64_acc_max_late` | 100.0 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_B_n64_acc_min_late` | 42.5 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_G1_pct` | 1.4 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_human_fpr_pct` | 3.6 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_oracle_acc_025` | 8.0 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_oracle_acc_035` | 32.0 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v02_oracle_acc_07` | 100.0 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_A_n256_FA_hi_035` | 10.0 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_A_n256_FA_lo_07` | 8.5 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_A_n256_FA_med_07` | 73.0 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_A_n64_FA_hi_035` | 11.5 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_B_acc_05_07_min` | 99.0 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_B_fluent_share_05_07_max` | 54 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_B_fluent_share_05_07_min` | 26 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_B_n256_FA_035` | 19.5 [7.0, 35.0] | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_bar_035` | 14.3 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_oracle_FA_035` | 28.5 | `tables/tab3_probe_forgery.py` / S3 |
| `t3_v04_random_FA_hi_035` | 3.5 | `tables/tab3_probe_forgery.py` / S3 |
| `v04_B_median_cos_max` | 0.062 | `tables/tabA4_attacker_checks.py` / S7 |

#### sec5_3_exact_test.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `s3x_E1_025` | +86.0 [+80.5, +90.0] | `tables/tab4_exact_test.py` / S4 |
| `s3x_E1_035` | +62.0 [+46.0, +78.0] | `tables/tab4_exact_test.py` / S4 |
| `s3x_E1_05` | +13.5 [+3.0, +25.5] | `tables/tab4_exact_test.py` / S4 |
| `s3x_E1_07` | +0.0 [-2.0, +0.0] | `tables/tab4_exact_test.py` / S4 |
| `s3x_G1_pct` | 0.81 | `tables/tab4_exact_test.py` / S4 |
| `s3x_G2_range` | 0.1–1.7 | `tables/tab4_exact_test.py` / S4 |
| `s3x_H1_max_pct` | 1.6 | `tables/tab4_exact_test.py` / S4 |
| `s3x_H1_pct` | 0.68 | `tables/tab4_exact_test.py` / S4 |
| `s3x_X1_bar_max` | 45.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_X1_bar_min` | 43.2 | `tables/tab4_exact_test.py` / S4 |
| `s3x_leak_cells_ge50` | 35 | `tables/tab4_exact_test.py` / S4 |
| `s3x_leak_cells_total` | 384 | `tables/tab4_exact_test.py` / S4 |
| `s3x_leak_spearman_A` | 0.68 | `tables/tab4_exact_test.py` / S4 |
| `s3x_leak_spearman_B` | 0.56 | `tables/tab4_exact_test.py` / S4 |
| `s3x_oracle_tpr_025` | 97.5 | `tables/tab4_exact_test.py` / S4 |
| `s3x_oracle_tpr_035` | 96.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_oracle_tpr_05` | 99.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_oracle_tpr_07` | 100.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_probe_tpr_025` | 8.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_probe_tpr_035` | 32.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_probe_tpr_05` | 86.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_probe_tpr_07` | 100.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_random_exact_max` | 0.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_random_probe_07` | 55.5 | `tables/tab4_exact_test.py` / S4 |
| `s3x_v04_A_n256_exactFA_med_07` | 1.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_v04_A_n256_probeFA_07` | 73.0 | `tables/tab4_exact_test.py` / S4 |
| `s3x_v04_B_n256_exactFA_med_035` | 4.5 | `tables/tab4_exact_test.py` / S4 |
| `s3x_v04_B_n256_probeFA_035` | 19.5 | `tables/tab4_exact_test.py` / S4 |
| `s3x_v04_exactFA_late_max` | 4.5 | `tables/tab4_exact_test.py` / S4 |
| `s3x_v04_exactFA_late_min` | 0.0 | `tables/tab4_exact_test.py` / S4 |
| `t3_v02_human_fpr_pct` | 3.6 | `tables/tab3_probe_forgery.py` / S3 |

#### sec5_4_stealing.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `layer` | 14 | `tables/tab1_studies_locks.py` / S1 |
| `n_layers` | 28 | `tables/tab1_studies_locks.py` / S1 |
| `new_tokens` | 256 | `tables/tab1_studies_locks.py` / S1 |
| `s5_fixed_035_n64_cos_known` | 0.940 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_035_n64_cos_search` | 0.932 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_035_n64_layer_hits` | 6 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_05_n64_cos_known` | 0.951 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_05_n64_cos_search` | 0.920 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_fixed_05_n64_layer_hits` | 6 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5x_fixed_035_n1024_FA_med` | 85.0 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_035_n64_FA` | 88.0 [76.5, 93.0] | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_035_oracle_FA` | 86.5 [83.5, 90.5] | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_035_random_FA` | 0.0 [0.0, 0.5] | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_n1024_FA_med` | 87.5 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_n1024_FA_perkey_max` | 93 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_n1024_FA_perkey_min` | 78 | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_n64_FA` | 85.5 [82.5, 90.0] | `tables/tab6_defence.py` / S6 |
| `s5x_fixed_05_oracle_FA` | 90.0 [87.0, 92.5] | `tables/tab6_defence.py` / S6 |
| `s5x_n64_tokens` | 16,384 | `tables/tab6_defence.py` / S6 |
| `t3_v02_A_cos_max` | 0.16 | `tables/tab3_probe_forgery.py` / S3 |
| `threat_035_n16_cos_grad_2dp` | 0.95 | `tables/tabA5_threat_check.py` / S8 |
| `threat_035_n4_cos_grad_2dp` | 0.80 | `tables/tabA5_threat_check.py` / S8 |
| `threat_07_n100_cos_grad_2dp` | 0.57 | `tables/tabA5_threat_check.py` / S8 |

#### sec5_5_scrubbing.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `s2_C1_025` | +14.5 [+5.0, +28.0] | `tables/tab5_scrubbing.py` / S5 |
| `s2_C1_035` | +6.5 [+2.0, +11.0] | `tables/tab5_scrubbing.py` / S5 |
| `s2_Eest_success_max` | 31.5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_Eest_success_min` | 0.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_Etrue_025_success` | 79.0 [72.0, 90.5] | `tables/tab5_scrubbing.py` / S5 |
| `s2_Etrue_035_success` | 43.0 [33.0, 63.0] | `tables/tab5_scrubbing.py` / S5 |
| `s2_G1_phi_pct` | 0.44 | `tables/tab5_scrubbing.py` / S5 |
| `s2_G1_qwen_pct` | 0.33 | `tables/tab5_scrubbing.py` / S5 |
| `s2_G2_phi_range` | 0.0–1.4 | `tables/tab5_scrubbing.py` / S5 |
| `s2_G2_qwen_range` | 0.0–0.6 | `tables/tab5_scrubbing.py` / S5 |
| `s2_P1_025` | 97.5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_P1_07` | 100.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_phi_025_keys` | 7 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_phi_025_miss` | 3.0 [0.0, 6.0] | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_phi_025_success` | 56.0 [48.0, 65.0] | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_phi_035_success` | 42.0 [33.0, 57.0] | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_phi_05_success_med` | 20.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_phi_07_success_med` | 13.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_025_keys` | 7 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_025_miss` | 2.5 [0.5, 6.5] | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_025_success` | 64.0 [54.5, 71.5] | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_035_keys` | 5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_035_success` | 53.0 [37.5, 64.5] | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_05_success_med` | 39.5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_07_pass_all` | 49.5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_07_success_med` | 26.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_fresh_phi_max_pct` | 19.5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_fresh_phi_mean_pct` | 0.94 | `tables/tab5_scrubbing.py` / S5 |
| `s2_fresh_phi_share_above3_pct` | 6.5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_fresh_qwen_max_pct` | 22.6 | `tables/tab5_scrubbing.py` / S5 |
| `s2_fresh_qwen_mean_pct` | 1.02 | `tables/tab5_scrubbing.py` / S5 |
| `s2_fresh_qwen_share_above3_pct` | 7.8 | `tables/tab5_scrubbing.py` / S5 |
| `s2_lm_max` | 99.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_lm_min` | 91.2 | `tables/tab5_scrubbing.py` / S5 |
| `s5x_N_PARA` | 100 | `tables/tab6_defence.py` / S6 |

#### sec5_6_keyed.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `s2_S1_qwen_035_detected_after` | 25.5 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_035_success_med` | 53.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_05_detected_after` | 35.0 | `tables/tab5_scrubbing.py` / S5 |
| `s2_S1_qwen_05_success_med` | 39.5 | `tables/tab5_scrubbing.py` / S5 |
| `s5_h1_05_n1024_cosw` | 0.213 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_rot_035_n256_chosen_cos` | 0.000 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_rot_035_n256_keys_recovered` | 6 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_rot_05_n256_keys_recovered` | 8 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5_rot_05_n64_keys_recovered` | 7 | `tables/tabA4_attacker_checks.py` / S7 |
| `s5x_add_n1024_clusters_ge05` | 6 | `tables/tab6_defence.py` / S6 |
| `s5x_add_n1024_every_FA` | 90 | `tables/tab6_defence.py` / S6 |
| `s5x_add_n1024_reaching_bar` | 5 | `tables/tab6_defence.py` / S6 |
| `s5x_add_n256_every_FA` | 96 | `tables/tab6_defence.py` / S6 |
| `s5x_arms_FA_hi_max` | 11.0 | `tables/tab6_defence.py` / S6 |
| `s5x_arms_FA_med_max` | 9.0 | `tables/tab6_defence.py` / S6 |
| `s5x_arms_P1_max` | 96.5 | `tables/tab6_defence.py` / S6 |
| `s5x_arms_P1_min` | 90.0 | `tables/tab6_defence.py` / S6 |
| `s5x_arms_para_detected_max` | 4.0 | `tables/tab6_defence.py` / S6 |
| `s5x_arms_para_detected_min` | 1.0 | `tables/tab6_defence.py` / S6 |
| `s5x_h1_035_d` | +22.0 [+6.0, +36.5] | `tables/tab6_defence.py` / S6 |
| `s5x_h1_035_para_success_med` | 73.0 | `tables/tab6_defence.py` / S6 |
| `s5x_h1_05_FA_trend` | 1.5 → 3.0 → 9.0 | `tables/tab6_defence.py` / S6 |
| `s5x_h1_05_d` | +32.0 [+21.0, +44.0] | `tables/tab6_defence.py` / S6 |
| `s5x_h1_05_para_success_med` | 70.5 | `tables/tab6_defence.py` / S6 |
| `s5x_h1_G1_pct` | 0.83 | `tables/tab6_defence.py` / S6 |
| `s5x_h4_035_d` | +18.0 [+7.5, +33.5] | `tables/tab6_defence.py` / S6 |
| `s5x_h4_035_para_success_med` | 72.0 | `tables/tab6_defence.py` / S6 |
| `s5x_h4_05_d` | +32.5 [+19.0, +45.5] | `tables/tab6_defence.py` / S6 |
| `s5x_h4_05_para_success_med` | 69.5 | `tables/tab6_defence.py` / S6 |
| `s5x_h4_G1_pct` | 0.95 | `tables/tab6_defence.py` / S6 |
| `s5x_ppl_ratio_max` | 0.85 | `tables/tab6_defence.py` / S6 |
| `s5x_ppl_ratio_min` | 0.72 | `tables/tab6_defence.py` / S6 |
| `s5x_rot_035_d` | +15.0 [+9.5, +18.5] | `tables/tab6_defence.py` / S6 |
| `s5x_rot_035_union_detect_med` | 93.0 | `tables/tab6_defence.py` / S6 |
| `s5x_rot_05_d` | +13.0 [+8.5, +17.5] | `tables/tab6_defence.py` / S6 |
| `s5x_rot_05_n1024_cluster_FA_med` | 96 | `tables/tab6_defence.py` / S6 |
| `s5x_rot_05_n64_cluster_FA_med` | 95 | `tables/tab6_defence.py` / S6 |
| `s5x_rot_05_union_detect_med` | 98.5 | `tables/tab6_defence.py` / S6 |
| `s5x_union_G1_pct` | 1.00 | `tables/tab6_defence.py` / S6 |

#### sec5_7_tradeoff.md

| Placeholder | Baseline value | Registering script / source |
|---|---|---|
| `cal_q15_05_ratio` | 1.62 | `tables/tab2_calibration.py` / S2 |
| `cal_q15_07_ratio` | 2.29 | `tables/tab2_calibration.py` / S2 |

### Quotation occurrence inventory

All page numbers below are PDF pages. Short opening phrases identify the quotation in the source section; the full passage was checked.

| Section | Quotation begins | Confirmed source page |
|---|---|---|
| sec1_introduction | Our method shows greater robustness to paraphrasing | self_recognition_2606.06315:p5 |
| sec1_introduction | we assume white-box access to the internal activations of $M$ | self_recognition_2606.06315:p2 |
| sec1_introduction | if an attacker can recover the secret steering vector and target layer, the … | self_recognition_2606.06315:p7 |
| sec1_introduction | rotates or evolves during generation according to a pseudo-random schedule | self_recognition_2606.06315:p7 |
| sec1_introduction | the error rate of the detection | ec_code_of_practice_129555:p17 |
| sec1_introduction | maintain intended performance levels under varying conditions, covering both… | ec_code_of_practice_129555:p17 |
| sec1_introduction | to remove or tamper with the watermark information, or to insert forged wate… | nist_ai_100-4:p13 |
| sec2_background_threat_model | add the scaled vector to the intermediate activation at layer $l$ at each to… | self_recognition_2606.06315:p2 |
| sec2_background_threat_model | sampled from $U([-1, 1]^d)$, with 99.7% of dimensions set to zero | Self-Recognition p. 11; split extraction + visual formula |
| sec2_background_threat_model | Injection and detection are performed at the middle layer | self_recognition_2606.06315:p11 |
| sec2_background_threat_model | we assume white-box access to the internal activations of $M$ | self_recognition_2606.06315:p2 |
| sec2_background_threat_model | The MLP has two hidden layers of width 32, trained for a single epoch to pre… | self_recognition_2606.06315:p3 |
| sec2_background_threat_model | aims to recover reusable watermark-related information | MarkSec p. 3; line-break hyphen confirmed |
| sec2_background_threat_model | Scrubbing aims to transform a watermarked text $y_w$ into an attacked text $… | marksec_2609.16681:p3 |
| sec2_background_threat_model | Spoofing aims to generate a forged text $y_s$ that is accepted as watermarke… | marksec_2609.16681:p3 |
| sec2_background_threat_model | $n = 30{,}000$ responses of token length $\leq 800$ | watermark_stealing_2402.19361:p6 |
| sec2_background_threat_model | 2.2 million tokens in total | no_free_lunch_2402.16187:p6 |
| sec2_background_threat_model | 2,000 victim watermarked texts | beyond_fixed_seal_2604.10893:p8 |
| sec2_background_threat_model | has only blackbox access to full generations | watermark_stealing_2402.19361:p3 |
| sec2_background_threat_model | a highly repetitive, degenerate loop often yields low PPL | self_recognition_2606.06315:p14 |
| sec6_related_work | the act of reverse-engineering a watermark by querying the API of the waterm… | watermark_stealing_2402.19361:p1 |
| sec6_related_work | $n = 30{,}000$ responses of token length $\leq 800$ | watermark_stealing_2402.19361:p6 |
| sec6_related_work | the supposed tradeoff between spoofing and scrubbing robustness … in fact do… | watermark_stealing_2402.19361:p9 |
| sec6_related_work | Robust watermarks are inherently vulnerable to spoofing attacks and are not … | no_free_lunch_2402.16187:p5 |
| sec6_related_work | 2.2 million tokens in total | no_free_lunch_2402.16187:p6 |
| sec6_related_work | watermarking should not be used to attribute provenance or blame to a specif… | learnability_2312.04469:p2 |
| sec6_related_work | 2,000 victim watermarked texts | beyond_fixed_seal_2604.10893:p8 |
| sec6_related_work | widely acknowledged | seek_2507.06274:p1 |
| sec6_related_work | a pseudorandom number generator seeded with previous tokens | kgw_2301.10226:p4 |
| sec6_related_work | attack amplification | kgw_2301.10226:p6 |
| sec6_related_work | have $k > 1$ different hidden keys, and to randomly choose one for each gene… | kgw_2301.10226:p7 |
| sec6_related_work | a small context width $h$ provides the best robustness to machine paraphrasi… | kgw_reliability_2306.04634:p21 |
| sec6_related_work | sufficiently many keys | kgw_reliability_2306.04634:p17 |
| sec6_related_work | an area of ongoing research | synthid_text_nature_2024:p6 |
| sec6_related_work | not a viable defense against our attacker | watermark_stealing_2402.19361:p20 |
| sec6_related_work | paraphrasing human text acts as a spoofing mechanism for our detector | self_recognition_2606.06315:p5 |
| sec6_related_work | Some vectors induce more severe degradations in generation quality, while ot… | self_recognition_2606.06315:p7 |
| sec6_related_work | DIPPER reduces TPR to 12%/10% on 2B/9B | slam_2605.05443:p7 |
| sec6_related_work | provenance attribution rather than tamper-proof cryptographic authentication | slam_2605.05443:p2 |
| sec6_related_work | attacks optimized against one surrogate key do not reliably transfer against… | awm_2603.23171:p2 |
| sec6_related_work | cannot query the detector | awm_2603.23171:p3 |
| sec6_related_work | a significantly stronger access model | gaussmark_2501.13941:p19 |
| sec6_related_work | are valid for any fixed $x \in \mathcal{X}$, but are marginalized over the k… | GaussMark p. 11; mathematical spacing normalised |
| sec6_related_work | point[s] toward $F\Delta_T$ rather than $\Delta_T$ | Chen et al. p. 1; mathematical glyph/spacing normalised, editorial [s] |
| sec6_related_work | a highly repetitive, degenerate loop often yields low PPL | self_recognition_2606.06315:p14 |
| sec6_related_work | no independent human annotation | marksec_2609.16681:p8 |
| appI_regulators | shall ensure their technical solutions are effective, interoperable, robust … | ec_code_of_practice_129555:p8; ec_code_of_practice_129555:p16 |
| appI_regulators | marked with an imperceptible watermark, with the exception of very short tex… | ec_code_of_practice_129555:p9 |
| appI_regulators | For free-form text longer than 200 tokens, watermarking still needs to be ap… | ec_code_of_practice_129555:p9 |
| appI_regulators | in a manner that is difficult for it to be separated from the content | ec_code_of_practice_129555:p9 |
| appI_regulators | independent researchers, educational and research institutions, and civil so… | ec_code_of_practice_129555:p13 |
| appI_regulators | a lower level of reliability and robustness and that they may produce mislea… | ec_code_of_practice_129555:p13 |
| appI_regulators | were not deemed mature enough | ec_code_of_practice_129555:p15 |
| appI_regulators | the error rate of the detection | ec_code_of_practice_129555:p17 |
| appI_regulators | maintain intended performance levels under varying conditions, covering both… | ec_code_of_practice_129555:p17 |
| appI_regulators | lexical substitution, homoglyphs | ec_code_of_practice_129555:p18 |
| appI_regulators | paraphrasing, translation cycles | ec_code_of_practice_129555:p18 |
| appI_regulators | plausible real-world threats based on the type of content, the type of mark … | ec_code_of_practice_129555:p18 |
| appI_regulators | are encouraged to apply standard cybersecurity practices, such as rate limit… | ec_code_of_practice_129555:p18 |
| appI_regulators | cryptographic methods for proving provenance and authenticity of content, lo… | ec_article50_guidelines_131215:p25 |
| appI_regulators | the provider may rely on its own detection solution or on a third party or s… | ec_article50_guidelines_131215:p26 |
| appI_regulators | minor paraphrases or deletions (for text) | nist_ai_100-4:p13 |
| appI_regulators | to remove or tamper with the watermark information, or to insert forged wate… | nist_ai_100-4:p13 |
| appI_regulators | a falsified signal about the history of the content | nist_ai_100-4:p19 |
| appI_regulators | users may come to disregard the watermarks as a meaningful signal | nist_ai_100-4:p19 |
| appI_regulators | the entity holding the detection tools must be trusted | nist_ai_100-4:p20 |
| appI_regulators | removal attacks (i.e., removing the watermark without having to break the en… | nist_ai_100-4:p38 |
| appI_regulators | forgery attempts | nist_ai_100-4:p38 |
| appI_regulators | paraphrasing | Code of Practice p. 18 |

## Closing report

Completed 2026-10-08, 14:57 UTC (09:57 CDT). The authorised review and conservative section revision are done; **the paper is waiting on Yichen's decisions and full read, not cleared for posting**.

| Commit | Work completed |
|---|---|
| `e784744` | This memo, written before any existing file changed, and its decision-log record. |
| `8046891` | D1/D2/D3/D5: readable section cross-references, locked paraphrase-prompt pointer, same-value placeholders for observed-budget/key/token/layer constants, stale metadata-abstract record. Open-item record in each of 24 edited section files. |
| `2f4d674` | First generated rebuild and validation record. |
| `afa7327` | D4: split attack-route prose; define MLP/FPR/TPR/AUROC; British spelling and narrative forgery terminology in eight section files, with records. |
| `4d61054` | Final generated rebuild, page inspection and validation record. |

All commits above were pushed to this project's `origin/main`. The closing memo, decision log and `RESEARCH_HANDOFF.md` status/resume update are recorded in the final report commit. No table/figure/build script, bibliography master, locked protocol, runner, study/pilot output, source quotation, abstract structure or AI-use paragraph was changed. All 820 protected baseline files retained their hashes; no study ran, no model/data corpus was downloaded, and nothing was posted, emailed, made public or sent to the snapshot repository. The only network package addition was `requests` and its dependencies in a temporary directory for the existing validator.

**Validation:** 2,896 registered values; zero unresolved placeholders; 44 valid bibliography entries, zero errors and duplicates, 11 warnings; 38 cited keys; 31 tables and 12 figures. All 23 table scripts passed in scratch and their registries agreed with the existing ones. Both revision commits were followed by fill, citation validation, HTML assembly/render, LaTeX compilation and word count. The prescribed `python3` validator initially lacked `requests` (also absent under `/usr/bin/python3` and the project venv); the successful equivalent invocation was `PYTHONPATH=/tmp/codex-paper-review-20261008/python-deps python3 .claude/skills/citation-management/scripts/validate_citations.py research/paper/references.bib`. The validator itself was unchanged.

**Final rendering:** LaTeX **68 total pages, 25 pages before references**, references beginning on page 26; HTML **62 total, 25 main** by its own convention. There are **123 overfull hboxes, 34 above 5 pt, maximum 13.70056 pt**. All moved table/figure caption pages and relevant continuations were viewed. The last page has a short Appendix I spillover. Section-source cross-references now render correctly; two generated table-note section symbols still render incorrectly, and existing dense table headers still collide. These are A9, not a clean-layout certification.

**Pending:** A1–A12 and O1–O4 all remain for Yichen. Prioritise A1/A2 (summary/access scope), A3–A5 (universal statements, related-work characterisation and protocol descriptions), then the connected generator/uncertainty/layout fixes A6/A8–A10. A7/A11 preserve inference and scope distinctions; A12 is the proposed disclosure. D3 used existing semantically suitable names only; remaining scalar constants, including independently configured null-key/design counts without a suitable shared name, stay under A10. The generated open-items collector does not replace this ask list.

**Verification limits:** no live novelty/source-status search, no independent refetch of the ETH webpage or Commission opinion PDF, no regeneration of studies/raw generations or every bootstrap interval, and no human quality evaluation. Some script assertions are weaker than their docstrings; the independently checked current D1 and rotation D2 results do not remove the need to repair that coverage. Those limits and all substantive discrepancies are recorded above. Yichen should decide the ask list, approve any resulting edits/disclosure, then read the rebuilt PDF in full before his separate posting checklist.
