**TA8 — Study 2: per-key detection before scrubbing and per-key scrub success (%) by method, 100 texts per key and strength**

| ρ | reading | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | median | keys ≥ 50% (of 8) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.25 | detected before scrubbing (unscrubbed originals) | 99 | 91 | 98 | 98 | 100 | 93 | 95 | 97 | 97.5 | 8 |
| 0.25 | P-Qwen success | 65 | 71 | 66 | 79 | 58 | 46 | 63 | 55 | 64.0 | 7 |
| 0.25 | P-Phi success | 56 | 78 | 56 | 54 | 58 | 44 | 58 | 50 | 56.0 | 7 |
| 0.25 | E-true 5% success | 63 | 90 | 93 | 90 | 78 | 72 | 79 | 79 | 79.0 | 8 |
| 0.25 | E-est 5% success | 16 | 60 | 37 | 52 | 37 | 26 | 21 | 24 | 31.5 | 2 |
| 0.25 | E-rand 5% success | 6 | 28 | 14 | 21 | 19 | 15 | 18 | 24 | 18.5 | 0 |
| 0.35 | detected before scrubbing (unscrubbed originals) | 100 | 95 | 95 | 98 | 96 | 88 | 98 | 96 | 96.0 | 8 |
| 0.35 | P-Qwen success | 54 | 64 | 52 | 69 | 33 | 34 | 62 | 44 | 53.0 | 5 |
| 0.35 | P-Phi success | 38 | 68 | 58 | 46 | 34 | 26 | 46 | 38 | 42.0 | 2 |
| 0.35 | E-true 5% success | 29 | 84 | 64 | 56 | 34 | 35 | 49 | 37 | 43.0 | 3 |
| 0.35 | E-est 5% success | 0 | 33 | 14 | 14 | 17 | 12 | 11 | 9 | 13.0 | 0 |
| 0.35 | E-rand 5% success | 0 | 8 | 7 | 6 | 8 | 9 | 5 | 5 | 6.5 | 0 |
| 0.50 | detected before scrubbing (unscrubbed originals) | 100 | 95 | 99 | 98 | 100 | 99 | 100 | 97 | 99.0 | 8 |
| 0.50 | P-Qwen success | 37 | 64 | 42 | 44 | 25 | 13 | 45 | 35 | 39.5 | 1 |
| 0.50 | P-Phi success | 18 | 64 | 42 | 16 | 16 | 14 | 22 | 22 | 20.0 | 1 |
| 0.50 | E-true 5% success | 16 | 72 | 33 | 10 | 8 | 20 | 17 | 27 | 18.5 | 1 |
| 0.50 | E-est 5% success | 1 | 29 | 9 | 3 | 1 | 2 | 0 | 4 | 2.5 | 0 |
| 0.50 | E-rand 5% success | 1 | 12 | 0 | 3 | 1 | 3 | 0 | 4 | 2.0 | 0 |
| 0.70 | detected before scrubbing (unscrubbed originals) | 100 | 41 | 100 | 100 | 100 | 98 | 100 | 99 | 100.0 | 7 |
| 0.70 | P-Qwen success | 19 | 53 | 34 | 24 | 14 | 14 | 28 | 29 | 26.0 | 1 |
| 0.70 | P-Phi success | 10 | 60 | 16 | 4 | 10 | 2 | 20 | 28 | 13.0 | 1 |
| 0.70 | E-true 5% success | 6 | 43 | 2 | 1 | 3 | 6 | 4 | 5 | 4.5 | 0 |
| 0.70 | E-est 5% success | 0 | 29 | 0 | 0 | 0 | 2 | 0 | 0 | 0.0 | 0 |
| 0.70 | E-rand 5% success | 0 | 35 | 0 | 0 | 1 | 0 | 0 | 0 | 0.0 | 0 |

Success: not attributed by the exact test at p ≤ 0.01 and all four quality conditions pass (perplexity, seq-rep-4, length, embedding similarity against the owner's human-text bars). Every key is calibrated under both paraphrasers (Table TA12), so every key counts; the verdicts (Table T5) use the median with its cluster-bootstrap interval.
