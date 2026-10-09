**TA13b — Rotation addendum (post hoc, labelled; not pre-registered): forging with every cluster's estimate at ρ = 0.35, 100 forgeries per cluster, the union test at p ≤ 0.01**

| n | cluster | texts in the cluster | nearest study key | cos(v̂, v) with it | z-profile | accepted by the union test (%) | fluent (%) | FA (%) [95% Wilson] | median perplexity | selection rule |
|---|---|---|---|---|---|---|---|---|---|---|
| 256 | 0 | 41 | 1001 | 0.98 | 2.74 | 98 | 95 | 93 [86, 97] | 8.2 |  |
| 256 | 2 | 38 | 1004 | 0.96 | 4.30 | 98 | 97 | 96 [90, 98] | 7.2 | best FA (every-cluster attacker) |
| 256 | 5 | 19 | 1005 | 0.94 | 4.63 | 96 | 83 | 81 [72, 87] | 8.6 |  |
| 256 | 6 | 43 | 1006 | 0.85 | 2.62 | 91 | 94 | 88 [80, 93] | 8.1 | largest cluster |
| 256 | 4 | 34 | 1008 | 0.81 | 3.04 | 91 | 72 | 63 [53, 72] | 9.8 |  |
| 256 | 3 | 29 | 1005 | 0.66 | 2.02 | 69 | 95 | 67 [57, 75] | 5.5 |  |
| 256 | 7 | 35 | 1003 | 0.62 | 2.14 | 64 | 94 | 60 [50, 69] | 7.6 |  |
| 256 | 1 | 17 | 1001 | 0.00 | 8.21 | 1 | 76 | 1 [0, 5] | 9.0 | study rule: largest z-profile |
| 1,024 | 2 | 122 | 1004 | 0.96 | 4.41 | 93 | 94 | 90 [83, 94] | 7.0 | best FA (every-cluster attacker) |
| 1,024 | 5 | 104 | 1006 | 0.96 | 3.72 | 85 | 86 | 78 [69, 85] | 7.7 |  |
| 1,024 | 1 | 99 | 1005 | 0.95 | 4.76 | 99 | 84 | 84 [76, 90] | 8.1 |  |
| 1,024 | 6 | 124 | 1002 | 0.93 | 2.93 | 80 | 95 | 79 [70, 86] | 7.3 |  |
| 1,024 | 3 | 185 | 1001 | 0.80 | 2.13 | 94 | 92 | 89 [81, 94] | 8.1 | largest cluster |
| 1,024 | 4 | 182 | 1008 | 0.61 | 2.35 | 39 | 95 | 36 [27, 46] | 8.2 |  |
| 1,024 | 0 | 116 | 1003 | 0.40 | 1.73 | 7 | 98 | 7 [3, 14] | 6.7 |  |
| 1,024 | 7 | 92 | 1001 | 0.00 | 9.75 | 1 | 68 | 1 [0, 5] | 7.2 | study rule: largest z-profile |

The pre-registered forgery used the cluster with the largest standardised mean-gradient profile (z-profile), which at this strength is a small cluster whose estimate has cosine near 0 with every key; the D1 bar is half the fixed key's genuine FA (43.2%). Fluency uses the level's pooled bars (perplexity ≤ 11.0, seq-rep-4 ≤ 0.055). Study 5's pre-registered D1 verdict for rotation at 0.35 stands; this table is the labelled addendum beside it.
