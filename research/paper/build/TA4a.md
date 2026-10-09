**TA4a — Study 1 v0.4: the attacker's perplexity-and-repetition check and its layer choice (descriptive; counts out of 8 keys)**

| ρ | Route | n | layer selected per key (1001–1008) | layer = 14 (of 8) | top candidate kept (of 8) | no candidate passed (of 8) | candidates passing (median of 5) | repetitive trials of the selected candidate (of 16), per key | median cos(v̂, v) | check agrees with evaluation (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.35 | A | 64 | 16, 19, 19, 15, 6, 17, 8, 24 | 0 | 6 | 0 | 4.5 | 0, 2, 1, 0, 2, 0, 2, 2 | 0.163 | 100 |
| 0.35 | A | 256 | 16, 14, 14, 5, 6, 17, 15, 0 | 2 | 8 | 0 | 5 | 2, 2, 2, 1, 0, 1, 0, 2 | 0.079 | 100 |
| 0.35 | B | 64 | 2, 12, 14, 1, 1, 12, 2, 2 | 1 | 1 | 1 | 2 | 2, 0, 1, 0, 2, 1, 1, 1 | 0.042 | 75 |
| 0.35 | B | 256 | 2, 12, 2, 1, 3, 14, 14, 12 | 2 | 2 | 1 | 2 | 0, 0, 2, 2, 0, 2, 0, 1 | 0.047 | 100 |
| 0.5 | A | 64 | 21, 14, 2, 17, 3, 17, 15, 22 | 1 | 4 | 0 | 3 | 0, 0, 2, 1, 1, 2, 0, 0 | 0.000 | 100 |
| 0.5 | A | 256 | 21, 14, 12, 19, 6, 14, 13, 22 | 2 | 4 | 1 | 4 | 2, 0, 1, 0, 1, 1, 1, 0 | 0.052 | 100 |
| 0.5 | B | 64 | 2, 14, 17, 1, 3, 15, 12, 12 | 1 | 3 | 4 | 0.5 | 2, 0, 0, 1, 2, 4, 0, 0 | 0.035 | 88 |
| 0.5 | B | 256 | 2, 14, 17, 1, 3, 15, 14, 14 | 3 | 2 | 4 | 0.5 | 2, 0, 0, 2, 2, 2, 0, 0 | 0.042 | 75 |
| 0.7 | A | 64 | 17, 14, 11, 20, 5, 12, 13, 17 | 1 | 1 | 5 | 0 | 0, 0, 3, 2, 5, 2, 1, 0 | 0.000 | 75 |
| 0.7 | A | 256 | 17, 6, 13, 17, 6, 15, 14, 17 | 1 | 1 | 3 | 1.5 | 0, 2, 0, 2, 0, 1, 0, 0 | 0.000 | 100 |
| 0.7 | B | 64 | 14, 14, 18, 14, 17, 14, 12, 17 | 4 | 1 | 7 | 0 | 0, 1, 1, 0, 0, 0, 0, 0 | 0.052 | 62 |
| 0.7 | B | 256 | 17, 14, 14, 14, 17, 14, 12, 14 | 5 | 1 | 8 | 0 | 1, 1, 2, 0, 0, 0, 0, 0 | 0.062 | 50 |

The check keeps a candidate layer if its 16 trial texts have median continuation perplexity ≤ 1.2 × the observed texts' and at most 2 trials with seq-rep-4 above the observed 95th percentile; the kept candidate with the largest footprint profile is used. 'Agrees' is the share of keys where 'some candidate passed' matches 'the forgery's median perplexity and seq-rep-4 are both at or below the evaluation's bars'.
