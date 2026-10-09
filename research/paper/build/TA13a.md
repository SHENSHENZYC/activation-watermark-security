**TA13a — Study 5: P-Qwen paraphrase (with the attacker's self-check) per arm beside the fixed key (median over 8 keys; 100 paraphrases per key and strength)**

| arm | ρ | scrub success (%) [95% CI] | detected after paraphrase (%) [95% CI] | all four quality conditions pass (%) [95% CI] | d = success − the fixed key's, points [95% CI] | D2 verdict |
|---|---|---|---|---|---|---|
| fixed key (h = 0; Study 2) | 0.35 | 53.0 [37.5, 64.5] | 25.5 | 74.0 | — | effective (Study 2's S1) |
| context-hashed, h = 1 | 0.35 | 73.0 [68.0, 78.0] | 3.0 [1.0, 5.0] | 75.5 [71.0, 80.5] | +22.0 [+6.0, +36.5]; 5 of 8 keys ≥ 20 points | **material robustness cost** (paraphrase effective (>= 50%)) |
| context-hashed, h = 4 | 0.35 | 72.0 [67.5, 76.5] | 1.0 [0.0, 2.0] | 73.0 [68.5, 78.0] | +18.0 [+7.5, +33.5]; 3 of 8 keys ≥ 20 points | **inconclusive** (paraphrase effective (>= 50%)) |
| rotation (K = 8; the union test on Study 2's paraphrases) | 0.35 | 70.0 | — (not in the locked results file) | as the fixed key | +15.0 [+9.5, +18.5] | **immaterial** |
| fixed key (h = 0; Study 2) | 0.50 | 39.5 [27.0, 48.0] | 35.0 | 64.0 | — | not effective (Study 2's S1) |
| context-hashed, h = 1 | 0.50 | 70.5 [66.5, 74.5] | 4.0 [1.5, 6.0] | 74.0 [70.0, 77.5] | +32.0 [+21.0, +44.0]; 7 of 8 keys ≥ 20 points | **material robustness cost** (paraphrase effective (>= 50%)) |
| context-hashed, h = 4 | 0.50 | 69.5 [64.5, 74.5] | 1.5 [0.0, 3.0] | 70.0 [65.5, 75.5] | +32.5 [+19.0, +45.5]; 7 of 8 keys ≥ 20 points | **material robustness cost** (paraphrase effective (>= 50%)) |
| rotation (K = 8; the union test on Study 2's paraphrases) | 0.50 | 52.5 | — (not in the locked results file) | as the fixed key | +13.0 [+8.5, +17.5] | **immaterial** |

D2 reads d against a 20-point materiality bar: material if the median d is at least 20 points and the interval's lower bound is above 0, immaterial if the upper bound is below 20, otherwise inconclusive (the pre-registered rule; Appendix A). Rotation's paraphrases are Study 2's, re-scored by the union test; its detection after paraphrase was computed by the report builder from the run's per-key files and is not in the locked results file, so it is not repeated here.
