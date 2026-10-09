## Table 1 — Pre-registered rules vs observed (protocol §10)

G1 (pooled FPR on pool A2 within [0.3%, 2.5%]): observed **1.4%** → **PASS**. G2 (attack isolation): asserted in code. Descriptive: FPR on the human continuations of A2 = 3.6%.

| ρ | Oracle median acceptance (L1: ≥ 20%) | L1 | R1 key recovery (Route A) | R2 Route A | R2 Route B | Random-key median | R3 generic steering suffices (random ≥ 50% of oracle) |
|---|---|---|---|---|---|---|---|
| 0.25 | 8.0% | fail | (descriptive) fails at this budget | (descriptive) inconclusive | (descriptive) inconclusive | 1.0% | no |
| 0.35 | 32.0% | pass | fails at this budget | inconclusive | practical (n=64) | 1.5% | no |
| 0.5 | 86.0% | pass | fails at this budget | not practical | practical (n=64) | 13.0% | no |
| 0.7 | 100.0% | pass | fails at this budget | not practical | practical (n=64) | 55.5% | yes |

Levels failing L1 are descriptive only (protocol §10).

## Table 2 — Acceptance by the owner's detector at its 1%-FPR threshold (median over 8 keys, % [95% cluster-bootstrap CI]; median perplexity of the texts under the unsteered model)

| ρ | Oracle (true key) | Random key | A n=64 | A n=256 | A n=1024 | B n=64 | B n=256 | B n=1024 |
|---|---|---|---|---|---|---|---|---|
| 0.25 | 8.0 [6.0, 17.0] | 1.0 [0.0, 2.0] | 2.5 [0.0, 4.5] | 1.5 [0.0, 3.5] | 2.0 [0.0, 3.5] | 3.0 [0.0, 5.5] | 6.0 [2.0, 10.5] | 7.5 [2.0, 29.5] |
| ppl | 6.5 | 6.5 | 6.1 | 6.0 | 6.0 | 6.8 | 6.8 | 7.2 |
| 0.35 | 32.0 [17.5, 52.5] | 1.5 [0.0, 4.5] | 11.0 [2.5, 22.0] | 3.5 [0.5, 14.5] | 4.5 [1.0, 16.0] | 42.5 [5.0, 68.0] | 56.0 [14.0, 80.5] | 45.5 [8.0, 87.5] |
| ppl | 7.7 | 7.7 | 7.4 | 7.0 | 6.9 | 10.4 | 10.5 | 10.3 |
| 0.5 | 86.0 [73.5, 94.5] | 13.0 [8.0, 18.5] | 23.0 [6.5, 71.5] | 20.0 [5.5, 35.5] | 20.5 [8.5, 69.3] | 99.0 [90.5, 100.0] | 99.5 [96.0, 100.0] | 100.0 [95.5, 100.0] |
| ppl | 10.5 | 10.5 | 8.8 | 8.8 | 9.5 | 17.2 | 17.8 | 18.2 |
| 0.7 | 100.0 [100.0, 100.0] | 55.5 [34.0, 83.0] | 80.5 [24.0, 100.0] | 90.5 [76.5, 100.0] | 89.0 [69.5, 100.0] | 100.0 [99.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| ppl | 16.8 | 16.5 | 10.0 | 13.7 | 11.7 | 30.6 | 30.5 | 31.1 |

Descriptive (protocol §8, computed from the saved scores after the run): detector AUROC, oracle texts (pool D) vs the owner's unwatermarked check texts (pool A2), median over keys [min, max]:

- ρ = 0.25: 0.746 [0.686, 0.840]
- ρ = 0.35: 0.888 [0.808, 0.972]
- ρ = 0.5: 0.986 [0.954, 0.998]
- ρ = 0.7: 0.998 [0.997, 1.000]

## Table 3 — Key recovery (median over 8 keys of cos(v̂, v); layer hits out of 8; Route A median support hit out of k = 4)

| ρ | n | cos A | cos B | layer hits A | layer hits B | support hit A |
|---|---|---|---|---|---|---|
| 0.25 | 1 | 0.000 | 0.006 | 0 | 0 | 0.00 |
| 0.25 | 4 | 0.000 | 0.021 | 0 | 0 | 0.00 |
| 0.25 | 16 | 0.000 | 0.023 | 0 | 0 | 0.00 |
| 0.25 | 64 | 0.000 | 0.042 | 0 | 3 | 0.00 |
| 0.25 | 256 | 0.124 | 0.045 | 1 | 2 | 0.25 |
| 0.25 | 1024 | 0.160 | 0.054 | 2 | 2 | 0.25 |
| 0.35 | 1 | 0.000 | 0.001 | 1 | 0 | 0.00 |
| 0.35 | 4 | 0.000 | 0.018 | 1 | 0 | 0.00 |
| 0.35 | 16 | 0.000 | 0.028 | 0 | 2 | 0.00 |
| 0.35 | 64 | 0.105 | 0.036 | 1 | 2 | 0.25 |
| 0.35 | 256 | 0.079 | 0.050 | 2 | 2 | 0.25 |
| 0.35 | 1024 | 0.074 | 0.050 | 2 | 2 | 0.25 |
| 0.5 | 1 | 0.000 | 0.013 | 0 | 0 | 0.00 |
| 0.5 | 4 | 0.000 | 0.020 | 2 | 0 | 0.00 |
| 0.5 | 16 | 0.032 | 0.043 | 3 | 2 | 0.12 |
| 0.5 | 64 | 0.000 | 0.037 | 1 | 2 | 0.00 |
| 0.5 | 256 | 0.000 | 0.046 | 2 | 2 | 0.00 |
| 0.5 | 1024 | 0.151 | 0.047 | 1 | 2 | 0.25 |
| 0.7 | 1 | 0.000 | 0.027 | 0 | 0 | 0.00 |
| 0.7 | 4 | 0.000 | 0.032 | 0 | 1 | 0.00 |
| 0.7 | 16 | 0.000 | 0.048 | 0 | 2 | 0.00 |
| 0.7 | 64 | 0.000 | 0.046 | 1 | 1 | 0.00 |
| 0.7 | 256 | 0.000 | 0.044 | 2 | 1 | 0.00 |
| 0.7 | 1024 | 0.015 | 0.043 | 2 | 1 | 0.12 |

## Table 4 — EXPLORATORY (added after the run): forgery quality per key-level

A key-level forgery counts as *effective* if its acceptance is ≥ 50% of that key-level's oracle acceptance, and as *fluent* if its median perplexity is ≤ 1.5× that key-level's oracle median (cut-off chosen after seeing the data). Counts are out of 8 keys.

| ρ | Route | n | effective | effective and fluent | keys whose chosen layer is 0 or 1 | median ppl ratio to oracle |
|---|---|---|---|---|---|---|
| 0.25 | A | 64 | 1 | 1 | 1 | 0.94 |
| 0.25 | A | 256 | 0 | 0 | 1 | 0.93 |
| 0.25 | A | 1024 | 1 | 1 | 1 | 0.93 |
| 0.25 | B | 64 | 2 | 2 | 4 | 1.00 |
| 0.25 | B | 256 | 3 | 3 | 3 | 1.02 |
| 0.25 | B | 1024 | 4 | 4 | 4 | 1.07 |
| 0.35 | A | 64 | 2 | 2 | 0 | 0.96 |
| 0.35 | A | 256 | 0 | 0 | 1 | 0.93 |
| 0.35 | A | 1024 | 0 | 0 | 2 | 0.89 |
| 0.35 | B | 64 | 6 | 3 | 5 | 1.25 |
| 0.35 | B | 256 | 6 | 3 | 4 | 1.35 |
| 0.35 | B | 1024 | 6 | 3 | 4 | 1.30 |
| 0.5 | A | 64 | 3 | 3 | 1 | 0.81 |
| 0.5 | A | 256 | 1 | 1 | 1 | 0.86 |
| 0.5 | A | 1024 | 2 | 1 | 0 | 0.93 |
| 0.5 | B | 64 | 7 | 2 | 4 | 1.66 |
| 0.5 | B | 256 | 8 | 2 | 3 | 1.75 |
| 0.5 | B | 1024 | 8 | 1 | 3 | 1.79 |
| 0.7 | A | 64 | 5 | 3 | 1 | 0.56 |
| 0.7 | A | 256 | 7 | 4 | 1 | 0.89 |
| 0.7 | A | 1024 | 7 | 5 | 1 | 0.75 |
| 0.7 | B | 64 | 8 | 3 | 3 | 1.96 |
| 0.7 | B | 256 | 8 | 2 | 3 | 2.01 |
| 0.7 | B | 1024 | 8 | 3 | 3 | 2.01 |

Route B over all key-levels and n: chosen layer 0 or 1 in 43 of 96 cases (median perplexity ratio 2.3, median acceptance 59.0%); other layers in 53 cases (ratio 1.36, acceptance 97.0%).

