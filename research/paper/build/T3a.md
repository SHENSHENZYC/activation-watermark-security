**T3a — Forging the owner's trained probe without the key (Study 1 v0.2 and v0.4; medians over 8 keys)**

| ρ | texts | v0.2 R2 verdict (plain acceptance) | v0.2 plain acceptance at n = 64 / 256 / 1,024 (%) | v0.4 FA at n = 64 / 256 (%) [95% CI] | F1 bar: half the oracle FA (%) | v0.4 F1 verdict | Route vector's cosine with the key (v0.4, n = 256) |
|---|---|---|---|---|---|---|---|
| 0.25 | oracle (true key, true layer); descriptive, L1 fails | — | 8.0 / — / — | — | — | watermark not working (L1) | — |
| 0.35 | oracle (true key, true layer) | — | 32.0 / — / — | 28.5 [14.5, 48.5] | — | ceiling | — |
| 0.35 | random key (generic steering) | — | 1.5 / — / — | 1.0 [0.0, 3.5] | — | F3 generic steering suffices: no | — |
| 0.35 | Route A: key recovery (activation mean) | inconclusive | 11.0 / 3.5 / 4.5 | 4.0 [1.0, 11.5] / 4.5 [1.0, 10.0] | 14.3 | not practical | 0.079 |
| 0.35 | Route B: footprint imitation | practical (n=64) | 42.5 / 56.0 / 45.5 | 9.5 [1.5, 24.0] / 19.5 [7.0, 35.0] | 14.3 | practical (n=256) | 0.047 |
| 0.5 | oracle (true key, true layer) | — | 86.0 / — / — | 77.0 [65.5, 86.0] | — | ceiling | — |
| 0.5 | random key (generic steering) | — | 13.0 / — / — | 10.0 [6.0, 13.5] | — | F3 generic steering suffices: no | — |
| 0.5 | Route A: key recovery (activation mean) | not practical | 23.0 / 20.0 / 20.5 | 28.5 [11.0, 52.5] / 26.0 [11.5, 51.5] | 38.5 | inconclusive | 0.052 |
| 0.5 | Route B: footprint imitation | practical (n=64) | 99.0 / 99.5 / 100.0 | 23.5 [11.0, 46.0] / 26.5 [11.5, 47.5] | 38.5 | inconclusive | 0.042 |
| 0.7 | oracle (true key, true layer) | — | 100.0 / — / — | 90.0 [88.0, 93.5] | — | ceiling | — |
| 0.7 | random key (generic steering) | — | 55.5 / — / — | 36.5 [17.5, 53.0] | — | F3 generic steering suffices: no | — |
| 0.7 | Route A: key recovery (activation mean) | not practical | 80.5 / 90.5 / 89.0 | 36.5 [7.5, 76.5] / 73.0 [8.5, 85.5] | 45.0 | inconclusive | 0.000 |
| 0.7 | Route B: footprint imitation | practical (n=64) | 100.0 / 100.0 / 100.0 | 25.5 [1.0, 70.5] / 30.0 [4.0, 61.0] | 45.0 | inconclusive | 0.062 |

Plain acceptance: the probe accepts the text at its 1% threshold (v0.2's rule). FA (v0.4's rule): accepted and no less fluent and no more repetitive than the key's own genuine watermarked texts (perplexity and seq-rep-4 at most their 95th percentiles). F1 practical: at some n the median FA reaches half the oracle's and its lower bound exceeds the random key's upper bound; not practical: both n's upper bounds fall below the bar; otherwise inconclusive. v0.2's R2 uses plain acceptance with the same practical clause. The random-key row's verdict is F3.
