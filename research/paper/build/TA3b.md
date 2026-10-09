**TA3b — S3 beside S4 per strength (medians over the keys each statistic calibrates), and the probe-and-exact combinations**

| ρ | Statistic | calibrated keys | genuine TPR (%) | random-key acceptance (%) | E1: TPR(exact) − TPR(probe), points [95% CI] | v0.4 Route B, n = 256: exact-FA (%) | X1 verdicts | probe TPR on the same texts (%) | both detectors (%) | either detector (%) | FPR of both / either on pool A2 (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.25 | S4 | 8 | 97.5 | 0.0 | +86.0 [+80.5, +90.0]: exact test more powerful | — | — | 8.0 | 8.0 | 97.5 | 0.0 / 1.9 |
| 0.35 | S4 | 8 | 96.0 | 0.0 | +62.0 [+46.0, +78.0]: exact test more powerful | 4.5 | A: not practical; B: not practical | 32.0 | 31.5 | 97.0 | 0.0 / 1.5 |
| 0.5 | S4 | 8 | 99.0 | 0.0 | +13.5 [+3.0, +25.5]: exact test more powerful | 3.5 | A: not practical; B: not practical | 86.0 | 85.5 | 99.5 | 0.0 / 2.7 |
| 0.7 | S4 | 8 | 100.0 | 0.0 | +0.0 [-2.0, +0.0]: no clear difference | 1.0 | A: not practical; B: not practical | 100.0 | 99.5 | 100.0 | 0.0 / 2.6 |
| 0.25 | S3 | 7 | 96.0 | 0.0 | +80.0 [+75.0, +87.0]: exact test more powerful | — | — | 8.0 | 8.0 | 96.0 | 0.0 / 1.6 |
| 0.35 | S3 | 7 | 95.0 | 0.0 | +69.0 [+43.0, +79.0]: exact test more powerful | 3.0 | A: not practical; B: not practical | 22.0 | 22.0 | 95.0 | 0.0 / 1.0 |
| 0.5 | S3 | 7 | 99.0 | 0.0 | +16.0 [+4.0, +30.0]: exact test more powerful | 4.0 | A: not practical; B: not practical | 84.0 | 84.0 | 100.0 | 0.0 / 2.0 |
| 0.7 | S3 | 7 | 100.0 | 0.0 | +0.0 [-1.0, +0.0]: no clear difference | 2.0 | A: not practical; B: not practical | 100.0 | 100.0 | 100.0 | 0.0 / 2.0 |

'Both' and 'either' combine the owner's probe (Study 1's rule at its 1% threshold) with the exact test on the same texts. E1 uses a paired cluster bootstrap over keys and texts.
