**TA2 — The power pilot (tuning keys 9001–9004, 100 texts per key and strength): four candidate statistics under the exact key-resampling test at p ≤ 0.01**

| Candidate | FPR check (1,600 tests; pass if 0.3–2.5%) | Score (mean median TPR, ρ 0.35–0.70) | TPR % ρ = 0.25 | TPR % ρ = 0.35 | TPR % ρ = 0.5 | TPR % ρ = 0.7 | AUROC ρ = 0.25 | AUROC ρ = 0.35 | AUROC ρ = 0.5 | AUROC ρ = 0.7 | cross-key % ρ = 0.25 | cross-key % ρ = 0.35 | cross-key % ρ = 0.5 | cross-key % ρ = 0.7 | per-key FPR over 1,000 keys: mean / 95th pct / max (%) | keys never firing / above 5% / above 50% (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 raw cosine (token-averaged activations) | 0.00% (FAIL) | 0.0 | 0 | 0 | 0 | 0 | 0.648 | 0.688 | 0.782 | 0.808 | 0.0 | 0.0 | 0.0 | 0.0 | 1.15 / 0.50 / 100.00 | 93.1 / 2.3 / 1.1 |
| S2 standardised cosine | 1.12% (pass) | 6.0 | 2 | 4 | 7 | 7 | 0.673 | 0.696 | 0.798 | 0.795 | 0.5 | 0.5 | 0.5 | 0.2 | 1.02 / 2.50 / 5.25 | 5.6 / 0.1 / 0.0 |
| S3 gradient score | 1.06% (pass) | 97.7 | 93 | 96 | 98 | 98 | 0.996 | 0.999 | 0.998 | 0.999 | 0.6 | 1.4 | 0.8 | 0.2 | 0.93 / 3.50 / 20.25 | 26.9 / 2.3 / 0.0 |
| S4 standardised gradient score | 0.88% (pass) | 95.7 | 88 | 96 | 98 | 94 | 0.995 | 0.999 | 0.998 | 1.000 | 0.7 | 0.5 | 0.3 | 0.1 | 0.96 / 2.25 / 4.75 | 7.4 / 0.0 / 0.0 |

TPR, AUROC and the score are medians over the four tuning keys; ρ = 0.25 is descriptive (the probe failed its gate there in Study 1). Cross-key: a text steered by one tuning key tested with another (1,200 tests per cell; about 1% is expected by construction). The per-key columns are the post-hoc diagnosis (written and run after the pilot's outcomes were read; exploratory): each of 1,000 fresh random keys tested on the 400 unwatermarked texts. By the pre-set rule no primary was chosen, because S1 failed the implementation check (0.00%); S4 was chosen by decision after the diagnosis (the rule's flaw and the choice are stated in Appendix B).
