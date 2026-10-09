**Post hoc, labelled (spec `study5_addendum/ROTATION_ADDENDUM_SPEC_v0.1.md`, FIXED before the run; not pre-registered; Study 5's D1 verdict for rotation stands).** At ρ = 0.35 the rotation attacker forges with every cluster's estimate (100 texts each, the union test, the level's pooled fluency bars: perplexity ≤ 11.0, seq-rep-4 ≤ 0.055). The D1 bar (half the fixed key's genuine FA) is 43.2%.

| n | cluster | texts | best key | cosine | z-profile | accepted % | fluent % | FA % [95% Wilson] | rule |
|---|---|---|---|---|---|---|---|---|---|
| 256 | 0 | 41 | 1001 | 0.98 | 2.74 | 98 | 95 | 93 [86, 97] |  |
| 256 | 2 | 38 | 1004 | 0.96 | 4.30 | 98 | 97 | 96 [90, 98] | best FA |
| 256 | 5 | 19 | 1005 | 0.94 | 4.63 | 96 | 83 | 81 [72, 87] |  |
| 256 | 6 | 43 | 1006 | 0.85 | 2.62 | 91 | 94 | 88 [80, 93] | largest cluster |
| 256 | 4 | 34 | 1008 | 0.81 | 3.04 | 91 | 72 | 63 [53, 72] |  |
| 256 | 3 | 29 | 1005 | 0.66 | 2.02 | 69 | 95 | 67 [57, 75] |  |
| 256 | 7 | 35 | 1003 | 0.62 | 2.14 | 64 | 94 | 60 [50, 69] |  |
| 256 | 1 | 17 | 1001 | 0.00 | 8.21 | 1 | 76 | 1 [0, 5] | study: largest z-profile |
| 1024 | 2 | 122 | 1004 | 0.96 | 4.41 | 93 | 94 | 90 [83, 94] | best FA |
| 1024 | 5 | 104 | 1006 | 0.96 | 3.72 | 85 | 86 | 78 [69, 85] |  |
| 1024 | 1 | 99 | 1005 | 0.95 | 4.76 | 99 | 84 | 84 [76, 90] |  |
| 1024 | 6 | 124 | 1002 | 0.93 | 2.93 | 80 | 95 | 79 [70, 86] |  |
| 1024 | 3 | 185 | 1001 | 0.80 | 2.13 | 94 | 92 | 89 [81, 94] | largest cluster |
| 1024 | 4 | 182 | 1008 | 0.61 | 2.35 | 39 | 95 | 36 [27, 46] |  |
| 1024 | 0 | 116 | 1003 | 0.40 | 1.73 | 7 | 98 | 7 [3, 14] |  |
| 1024 | 7 | 92 | 1001 | 0.00 | 9.75 | 1 | 68 | 1 [0, 5] | study: largest z-profile |

- **n = 256:** the study's rule (largest z-profile) gives FA 1%; the largest-cluster rule 88%; an attacker who tries every cluster reaches 96% (cluster 2); 7 of the 7 clusters with cosine ≥ 0.5 reach the bar.

- **n = 1024:** the study's rule (largest z-profile) gives FA 1%; the largest-cluster rule 89%; an attacker who tries every cluster reaches 90% (cluster 2); 5 of the 6 clusters with cosine ≥ 0.5 reach the bar.
