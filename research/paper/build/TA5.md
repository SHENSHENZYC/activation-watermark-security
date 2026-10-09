**TA5 — The threat check (tuning keys 9001–9004; 100 observed texts per key and strength): the gradient-mean estimator recovers the fixed key where the activation-mean estimator does not**

| ρ | n (texts) | Route A′ (gradients, layer search): median cos(v̂, v) | support hit (of 4) | layer = 14 (keys of 4) | Route A (activations): median cos | layer = 14 (keys of 4) | gradients at the true layer: median cos |
|---|---|---|---|---|---|---|---|
| 0.35 | 4 | 0.799 | 0.50 | 3 | 0.000 | 0 | 0.807 |
| 0.35 | 16 | 0.952 | 0.62 | 3 | 0.000 | 0 | 0.952 |
| 0.35 | 64 | 0.902 | 0.62 | 4 | 0.000 | 1 | 0.902 |
| 0.35 | 100 | 0.895 | 0.62 | 4 | 0.000 | 0 | 0.895 |
| 0.5 | 4 | 0.787 | 0.50 | 2 | 0.000 | 0 | 0.860 |
| 0.5 | 16 | 0.862 | 0.50 | 3 | 0.000 | 0 | 0.876 |
| 0.5 | 64 | 0.933 | 0.50 | 3 | 0.000 | 1 | 0.877 |
| 0.5 | 100 | 0.934 | 0.50 | 3 | 0.000 | 1 | 0.880 |
| 0.7 | 4 | 0.538 | 0.25 | 1 | 0.000 | 1 | 0.863 |
| 0.7 | 16 | 0.583 | 0.38 | 2 | 0.000 | 1 | 0.575 |
| 0.7 | 64 | 0.571 | 0.38 | 2 | 0.087 | 1 | 0.576 |
| 0.7 | 100 | 0.574 | 0.38 | 2 | 0.000 | 1 | 0.583 |

Medians over the four tuning keys. Pre-set reading: the threat is real if the median cosine is at least 0.5 at some n ≤ 100 at ρ = 0.50 or 0.70 (verdict: threat real). Everything else in the table is descriptive. These are design inputs for Study 5, not study results.
