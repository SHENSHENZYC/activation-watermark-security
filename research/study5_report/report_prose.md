# Study 5 — report v0.1: context-keyed and rotating-key activation steering against the gradient-averaging attacker (Qwen2.5-1.5B)

Date: [[report_date]] (Milestone 9). Protocol: [`STUDY5_PROTOCOL_v0.1.md`](STUDY5_PROTOCOL_v0.1.md) (LOCKED 2026-10-02 23:24 UTC (18:24 CDT), before outcomes). Lock: [`outputs/study5_v0.1/PRE_RUN_LOCK.json`](outputs/study5_v0.1/PRE_RUN_LOCK.json). Run manifest: [`outputs/study5_v0.1/RUN_MANIFEST.json`](outputs/study5_v0.1/RUN_MANIFEST.json). Results: [`outputs/study5_v0.1/results.json`](outputs/study5_v0.1/results.json). **This file is built by** `study5_report/make_report_s5.py`, **which inserts the tables, the samples and every number in the text from the locked outputs; no number is typed by hand.** The builder was written during phases S and K, before any Study 5 outcome was read, and tested on a synthetic fixture of the full scope (`study5_report/fixture_s5.py`). Figures: `outputs/study5_v0.1/report/`.

## 1. Run
- **Phases S and K (shared statistics; the keyed arms' generation, attacker, forgeries, controls and quality):** [[S_start_date]] [[S_start_utc]] UTC ([[S_start_ct]] [[ct]]) to [[K_end_date]] [[K_end_utc]] UTC ([[K_end_ct]] [[ct]]); S [[S_hours]] h, K [[K_hours]] h.
- **Phase P (P-Qwen paraphrase of the keyed arms' genuine texts, then scoring):** [[P_start_date]] [[P_start_utc]]–[[P_end_utc]] UTC ([[P_start_ct]]–[[P_end_ct]] [[ct]]), [[P_hours]] h.
- **Phases F and R (the fixed key's re-attack with Route A′; rotation):** F [[F_start_utc]]–[[F_end_utc]] UTC ([[F_start_ct]]–[[F_end_ct]] [[ct]]), [[F_hours]] h; R [[R_start_utc]]–[[R_end_utc]] UTC ([[R_start_ct]]–[[R_end_ct]] [[ct]]), [[R_hours]] h; analysis [[A_start_utc]]–[[A_end_utc]] UTC, [[A_hours]] h. Total [[total_hours]] h against the [[projected_hours]] h projection.
- `check_lock()` accepted the lock before each phase and again after the run (the protocol, 18 code files and 106 reused files unchanged). The holdout was not touched (`final: false`). Deviations: [[deviations]].
- The report builder re-computed, with its own implementation, S4 and the union test on Study 3's locked features (the fixed arm's detection, acceptance and random-key control; rotation's union-test detection) and on Study 2's locked paraphrases (the fixed key's scrub success, the D2 comparator, which also equals Study 2's reported S1 values), and, from the run's per-text keyed statistics, every p-value, fluency flag, acceptance, scrub success, quality condition and perplexity ratio per key. It re-derived G1, G2, P0, P1 and every D1, D2 and D3 verdict from the §9 rules written out again and asserted that all of these equal `results.json` (all equal). The per-position keyed statistics themselves are taken from the run's files (their gradients are not stored).

## 2. Pre-registered results (protocol §9)
<<TABLE1>>

<<IN_WORDS>>

## 3. Figures and tables
![Figure 1 — key recovery and forgery acceptance against the attacker's budget](outputs/study5_v0.1/report/fig1_recovery_forgery.png)

![Figure 2 — paraphrase per arm beside the fixed key](outputs/study5_v0.1/report/fig2_paraphrase.png)

![Figure 3 — the stealability–robustness–quality frontier](outputs/study5_v0.1/report/fig3_frontier.png)

![Figure 4 — per-key calibration and per-key stealing](outputs/study5_v0.1/report/fig4_per_key.png)

![Figure 5 — the per-context attacker's mechanics](outputs/study5_v0.1/report/fig5_attacker.png)

<<TABLES>>

## 4. Samples read (protocol §10)
<<SAMPLES>>

## 5. Post-hoc addendum: rotation's attacker forging with every cluster at ρ = 0.35 (labelled; not pre-registered)
<<ADDENDUM>>

## 6. What this does not show (protocol §2, §11, §13)
- Budgets above 1,024 observed texts (the token-level literature steals context-hashed schemes with about 30,000 responses), paraphrasers other than Qwen2.5-1.5B-Instruct, adaptive or combined attacks against the detector, the repeated-query removal attack against multiple keys, and human editing were not tested.
- "Stealing blocked at n ≤ 1,024" means this attacker, at this budget, cannot forge the keyed watermark where it forges the fixed one; it is not immunity. "Material robustness cost" means the keying removes a substantial part of the paraphrase robustness that motivates activation watermarks. An "immaterial" reading on D2 and D3 with D1 "blocked" would be bounded by the attacker and paraphraser tested.
- Not claimed: a new watermark; robustness to stronger paraphrasers; human-judged quality; other models, layers or key distributions; a fix of the trade-off; results for other strengths than ρ = 0.35 and 0.50.
- The per-position form with h = 0 against S4 (protocol §10) was measured on tuning keys in the pilot's I4 addendum (within 10 points of S4), not on the study keys; the run does not produce it.
- Rotation's quality is unchanged by construction (the rotating corpus is the fixed key's texts), so D3 is not tested for it; its robustness reading is the union test's loss on Study 2's paraphrases, not a new paraphrase.
