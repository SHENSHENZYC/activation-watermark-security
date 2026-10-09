**TA6 — Study 1 v0.4: per-key fluent acceptance (FA, %) by the owner's probe at its 1% threshold, n = 256 forgeries, with the per-key quality bars**

| ρ | texts | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | median | keys ≥ the F1 bar (of 8) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.35 | genuine (oracle) | 51 | 40 | 16 | 11 | 38 | 16 | 19 | 57 | 28.5 | — |
| 0.35 | random key (generic steering) | 1 | 0 | 3 | 0 | 2 | 0 | 1 | 8 | 1.0 | 0 |
| 0.35 | v0.4 Route A, n = 256 | 13 | 6 | 1 | 1 | 13 | 1 | 3 | 6 | 4.5 | 0 |
| 0.35 | v0.4 Route B, n = 256 | 15 | 37 | 7 | 2 | 9 | 24 | 31 | 39 | 19.5 | 5 |
| 0.35 | perplexity bar (the key's oracle 95th percentile) | 10.3 | 10.5 | 10.0 | 9.9 | 10.8 | 10.4 | 10.7 | 12.2 | 10.5 | — |
| 0.35 | seq-rep-4 bar (the key's oracle 95th percentile) | 0.020 | 0.083 | 0.033 | 0.029 | 0.077 | 0.072 | 0.032 | 0.040 | 0.036 | — |
| 0.50 | genuine (oracle) | 88 | 86 | 64 | 56 | 76 | 78 | 72 | 86 | 77.0 | — |
| 0.50 | random key (generic steering) | 10 | 13 | 10 | 2 | 10 | 12 | 6 | 14 | 10.0 | 0 |
| 0.50 | v0.4 Route A, n = 256 | 16 | 20 | 32 | 56 | 36 | 4 | 11 | 76 | 26.0 | 2 |
| 0.50 | v0.4 Route B, n = 256 | 25 | 73 | 27 | 2 | 26 | 27 | 8 | 51 | 26.5 | 2 |
| 0.50 | perplexity bar (the key's oracle 95th percentile) | 13.9 | 15.7 | 14.2 | 11.9 | 15.3 | 13.1 | 12.9 | 17.4 | 14.1 | — |
| 0.50 | seq-rep-4 bar (the key's oracle 95th percentile) | 0.012 | 0.072 | 0.020 | 0.020 | 0.056 | 0.032 | 0.060 | 0.020 | 0.026 | — |
| 0.70 | genuine (oracle) | 90 | 90 | 95 | 89 | 91 | 90 | 90 | 90 | 90.0 | — |
| 0.70 | random key (generic steering) | 14 | 47 | 49 | 14 | 57 | 53 | 26 | 24 | 36.5 | 4 |
| 0.70 | v0.4 Route A, n = 256 | 17 | 75 | 97 | 86 | 77 | 71 | 3 | 5 | 73.0 | 5 |
| 0.70 | v0.4 Route B, n = 256 | 11 | 61 | 6 | 3 | 51 | 49 | 2 | 72 | 30.0 | 4 |
| 0.70 | perplexity bar (the key's oracle 95th percentile) | 21.7 | 28.4 | 27.9 | 19.1 | 29.5 | 22.0 | 21.1 | 30.6 | 25.0 | — |
| 0.70 | seq-rep-4 bar (the key's oracle 95th percentile) | 0.008 | 0.210 | 0.016 | 0.020 | 0.051 | 0.032 | 0.091 | 0.016 | 0.026 | — |

FA counts a text as accepted by the probe, with perplexity and seq-rep-4 at or below the key's oracle 95th percentiles (the bars in the last two rows of each strength). The F1 bar is half the oracle's median FA; the F1 verdicts (Table T3) use the median over keys with its cluster-bootstrap interval, so a set can be 'not practical' or 'inconclusive' while some keys exceed the bar.
