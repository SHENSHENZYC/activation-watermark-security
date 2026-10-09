**TA14b — Study 1 v0.2: key recovery against the budget n (medians over 8 keys) and the pre-registered verdicts**

| ρ | n | Route A: median cos(v̂, v) | Route A: layer 14 found (keys of 8) | Route A: median support hit (of k = 4) | Route B: median cos(v̂, v) | Route B: layer 14 found (keys of 8) |
|---|---|---|---|---|---|---|
| 0.25 | 1 | 0.000 | 0 | 0.00 | 0.006 | 0 |
| 0.25 | 4 | 0.000 | 0 | 0.00 | 0.021 | 0 |
| 0.25 | 16 | 0.000 | 0 | 0.00 | 0.023 | 0 |
| 0.25 | 64 | 0.000 | 0 | 0.00 | 0.042 | 3 |
| 0.25 | 256 | 0.124 | 1 | 0.25 | 0.045 | 2 |
| 0.25 | 1,024 | 0.160 | 2 | 0.25 | 0.054 | 2 |
| 0.25 | verdicts | L1 working watermark: no | R1: (descriptive) fails at this budget | R2 A: (descriptive) inconclusive | R2 B: (descriptive) inconclusive | R3: no |
| 0.35 | 1 | 0.000 | 1 | 0.00 | 0.001 | 0 |
| 0.35 | 4 | 0.000 | 1 | 0.00 | 0.018 | 0 |
| 0.35 | 16 | 0.000 | 0 | 0.00 | 0.028 | 2 |
| 0.35 | 64 | 0.105 | 1 | 0.25 | 0.036 | 2 |
| 0.35 | 256 | 0.079 | 2 | 0.25 | 0.050 | 2 |
| 0.35 | 1,024 | 0.074 | 2 | 0.25 | 0.050 | 2 |
| 0.35 | verdicts | L1 working watermark: yes | R1: fails at this budget | R2 A: inconclusive | R2 B: practical (n=64) | R3: no |
| 0.50 | 1 | 0.000 | 0 | 0.00 | 0.013 | 0 |
| 0.50 | 4 | 0.000 | 2 | 0.00 | 0.020 | 0 |
| 0.50 | 16 | 0.032 | 3 | 0.12 | 0.043 | 2 |
| 0.50 | 64 | 0.000 | 1 | 0.00 | 0.037 | 2 |
| 0.50 | 256 | 0.000 | 2 | 0.00 | 0.046 | 2 |
| 0.50 | 1,024 | 0.151 | 1 | 0.25 | 0.047 | 2 |
| 0.50 | verdicts | L1 working watermark: yes | R1: fails at this budget | R2 A: not practical | R2 B: practical (n=64) | R3: no |
| 0.70 | 1 | 0.000 | 0 | 0.00 | 0.027 | 0 |
| 0.70 | 4 | 0.000 | 0 | 0.00 | 0.032 | 1 |
| 0.70 | 16 | 0.000 | 0 | 0.00 | 0.048 | 2 |
| 0.70 | 64 | 0.000 | 1 | 0.00 | 0.046 | 1 |
| 0.70 | 256 | 0.000 | 2 | 0.00 | 0.044 | 1 |
| 0.70 | 1,024 | 0.015 | 2 | 0.12 | 0.043 | 1 |
| 0.70 | verdicts | L1 working watermark: yes | R1: fails at this budget | R2 A: not practical | R2 B: practical (n=64) | R3: yes |

Route A estimates the key as the mean activation difference between observed and unwatermarked texts at the attacker's chosen layer; Route B fits a probe and takes its direction. R1 asks, at some n, for a median cosine ≥ 0.9 with the layer found for at least 7 of 8 keys (the smallest such n is n*), and reads 'partial' if the median cosine at n = 1,024 is in [0.5, 0.9); it fails at every strength.
