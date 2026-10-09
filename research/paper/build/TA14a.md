**TA14a — Study 1 v0.2: plain acceptance by the owner's probe at its 1% threshold (median over 8 keys), without any quality condition**

| ρ | texts | accepted by the probe (%) [95% CI] | median perplexity under the unsteered model |
|---|---|---|---|
| 0.25 | genuine (oracle) | 8.0 [6.0, 17.0] | 6.5 |
| 0.25 | random key | 1.0 [0.0, 2.0] | 6.5 |
| 0.25 | Route A, n = 64 | 2.5 [0.0, 4.5] | 6.1 |
| 0.25 | Route A, n = 256 | 1.5 [0.0, 3.5] | 6.0 |
| 0.25 | Route A, n = 1,024 | 2.0 [0.0, 3.5] | 6.0 |
| 0.25 | Route B, n = 64 | 3.0 [0.0, 5.5] | 6.8 |
| 0.25 | Route B, n = 256 | 6.0 [2.0, 10.5] | 6.8 |
| 0.25 | Route B, n = 1,024 | 7.5 [2.0, 29.5] | 7.2 |
| 0.35 | genuine (oracle) | 32.0 [17.5, 52.5] | 7.7 |
| 0.35 | random key | 1.5 [0.0, 4.5] | 7.7 |
| 0.35 | Route A, n = 64 | 11.0 [2.5, 22.0] | 7.4 |
| 0.35 | Route A, n = 256 | 3.5 [0.5, 14.5] | 7.0 |
| 0.35 | Route A, n = 1,024 | 4.5 [1.0, 16.0] | 6.9 |
| 0.35 | Route B, n = 64 | 42.5 [5.0, 68.0] | 10.4 |
| 0.35 | Route B, n = 256 | 56.0 [14.0, 80.5] | 10.5 |
| 0.35 | Route B, n = 1,024 | 45.5 [8.0, 87.5] | 10.3 |
| 0.50 | genuine (oracle) | 86.0 [73.5, 94.5] | 10.5 |
| 0.50 | random key | 13.0 [8.0, 18.5] | 10.5 |
| 0.50 | Route A, n = 64 | 23.0 [6.5, 71.5] | 8.8 |
| 0.50 | Route A, n = 256 | 20.0 [5.5, 35.5] | 8.8 |
| 0.50 | Route A, n = 1,024 | 20.5 [8.5, 69.3] | 9.5 |
| 0.50 | Route B, n = 64 | 99.0 [90.5, 100.0] | 17.2 |
| 0.50 | Route B, n = 256 | 99.5 [96.0, 100.0] | 17.8 |
| 0.50 | Route B, n = 1,024 | 100.0 [95.5, 100.0] | 18.2 |
| 0.70 | genuine (oracle) | 100.0 [100.0, 100.0] | 16.8 |
| 0.70 | random key | 55.5 [34.0, 83.0] | 16.5 |
| 0.70 | Route A, n = 64 | 80.5 [24.0, 100.0] | 10.0 |
| 0.70 | Route A, n = 256 | 90.5 [76.5, 100.0] | 13.7 |
| 0.70 | Route A, n = 1,024 | 89.0 [69.5, 100.0] | 11.7 |
| 0.70 | Route B, n = 64 | 100.0 [99.0, 100.0] | 30.6 |
| 0.70 | Route B, n = 256 | 100.0 [100.0, 100.0] | 30.5 |
| 0.70 | Route B, n = 1,024 | 100.0 [100.0, 100.0] | 31.1 |

Calibration: pooled false-positive rate 1.43% on unwatermarked model text (G1), 3.6% on human continuations (exploratory). Perplexity is the median over the set's texts under the unsteered model; a low value can also mean repetitive text (Appendix E).
