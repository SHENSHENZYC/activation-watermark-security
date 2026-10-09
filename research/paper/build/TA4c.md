**TA4c — Study 5: the per-context attacker (Route A′-h) on the context-hashed arms, against the budget n (medians over 8 keys)**

| arm | ρ | n | contexts estimated (median over keys) | coverage of a genuine text's positions | count-weighted cos with the true per-context keys | forgery FA % [95% CI] |
|---|---|---|---|---|---|---|
| h = 1 | 0.35 | 64 | 148 | 0.487 | 0.022 | 1.0 [0.0, 2.5] |
| h = 1 | 0.35 | 256 | 527 | 0.639 | 0.089 | 2.5 [0.0, 4.0] |
| h = 1 | 0.35 | 1,024 | 1942.5 | 0.798 | 0.170 | 3.5 [2.0, 6.5] |
| h = 1 | 0.5 | 64 | 153.5 | 0.503 | 0.065 | 1.5 [0.0, 3.0] |
| h = 1 | 0.5 | 256 | 525 | 0.653 | 0.145 | 3.0 [1.0, 6.0] |
| h = 1 | 0.5 | 1,024 | 1878 | 0.800 | 0.213 | 9.0 [5.5, 11.0] |
| h = 4 | 0.35 | 64 | 0.5 | 0.001 | 0.000 | 1.0 [0.0, 2.5] |
| h = 4 | 0.35 | 256 | 9 | 0.004 | 0.000 | 1.0 [0.0, 2.0] |
| h = 4 | 0.35 | 1,024 | 89 | 0.013 | 0.012 | 0.0 [0.0, 0.0] |
| h = 4 | 0.5 | 64 | 1 | 0.001 | 0.000 | 1.0 [0.0, 2.0] |
| h = 4 | 0.5 | 256 | 7 | 0.002 | 0.000 | 0.5 [0.0, 1.5] |
| h = 4 | 0.5 | 1,024 | 61 | 0.008 | 0.012 | 1.0 [0.0, 2.0] |

A context is estimated once it has been seen at least 16 times among the n observed texts (4 largest |mean| coordinates of the standardised per-position gradients); coverage is the share of a genuine text's scored positions whose context has an estimate.
