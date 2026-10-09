# Study 2 — report v0.1: scrubbing an activation-steering watermark under the exact key test (Qwen2.5-1.5B)

Date: [[report_date]] (Milestone 7). Protocol: [`STUDY2_PROTOCOL_v0.1.md`](STUDY2_PROTOCOL_v0.1.md) (LOCKED 2026-10-01 16:12 UTC (11:12 CDT), before outcomes). Lock: [`outputs/study2_v0.1/PRE_RUN_LOCK.json`](outputs/study2_v0.1/PRE_RUN_LOCK.json). Run manifest: [`outputs/study2_v0.1/RUN_MANIFEST.json`](outputs/study2_v0.1/RUN_MANIFEST.json). Results: [`outputs/study2_v0.1/results.json`](outputs/study2_v0.1/results.json). **This file is built by** `study2_report/make_report_s2.py`, **which inserts the tables, the samples and every number in the text from the locked outputs; no number is typed by hand.** The builder was written during phase 1, before any Study 2 outcome was read, and tested on a synthetic fixture. Figures: `outputs/study2_v0.1/report/`.

## 1. Run
- **Phase 1 (paraphrase):** [[para_start_date]] [[para_start_utc]] UTC ([[para_start_ct]] [[ct]]) to [[para_end_date]] [[para_end_utc]] UTC ([[para_end_ct]] [[ct]]), [[para_hours]] h, on a freshly restarted Mac with other apps closed (swap 0 at the start).
- **Phase 2 (edits, then scoring), [[edits_start_date]]:** edits [[edits_start_utc]]–[[edits_end_utc]] UTC ([[edits_start_ct]]–[[edits_end_ct]] [[ct]]), [[edits_hours]] h; scoring [[score_start_utc]]–[[score_end_utc]] UTC ([[score_start_ct]]–[[score_end_ct]] [[ct]]), [[score_hours]] h; analysis [[analyse_start_utc]]–[[analyse_end_utc]] UTC ([[analyse_start_ct]]–[[analyse_end_ct]] [[ct]]), [[analyse_hours]] h. Total [[total_hours]] h against the 24.3 h projection.
- `check_lock()` accepted the lock before each phase and again after the run (protocol, 13 code files, 164 reused files unchanged). The holdout was not touched (`final: false`). Deviations: [[deviations]].
- The report builder re-computed, with its own implementation of the S4 test and of the quality conditions, every key's FPR on the paraphrased null texts (G1, G2), the detection before scrubbing (P1), each key's detection and success after every method at every level, the originals' miss rate, the first-attempt readings, the length-matched control and the probe's acceptance. It re-derived every S1, S2 and C1 verdict from the §7 rules and asserted that all of these equal `results.json` (all equal).

## 2. Pre-registered results (protocol §7)
<<TABLE1>>

<<IN_WORDS>>

## 3. Figures and tables
![Figure 1 — S4 detection and scrub success after each method](outputs/study2_v0.1/report/fig1_scrubbing.png)

![Figure 2 — scrub success against the edit budget](outputs/study2_v0.1/report/fig2_edit_budget.png)

![Figure 3 — per-key calibration before and after paraphrase](outputs/study2_v0.1/report/fig3_calibration.png)

![Figure 4 — key leakage: E-est success against the attacker's recovered cosine](outputs/study2_v0.1/report/fig4_leakage.png)

![Figure 5 — the owner's probe vs S4 on the same scrubbed texts](outputs/study2_v0.1/report/fig5_probe_vs_s4.png)

<<TABLES>>

## 4. Samples read (protocol §8)
<<SAMPLES>>

## 5. What this does not show (protocol §9, §11)
- Robustness to stronger paraphrasers (for example DIPPER-XXL), to combined or adaptive attacks, or to attackers who query the detector.
- Human-judged fluency: perplexity, repetition, length and embedding similarity are proxies; the samples above are read for that reason.
- Other models, layers or schemes.
