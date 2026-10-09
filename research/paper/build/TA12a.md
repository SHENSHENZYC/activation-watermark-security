**TA12a — Study 2: secondary readings per method (median over 8 keys, %)**

| ρ | method | detected after (p ≤ 0.01) | at p ≤ 0.001 (9,999 null keys) | 4 texts pooled: detected | originals cut to the paraphrase's length: detected | the owner's probe accepts | first attempt only: success |
|---|---|---|---|---|---|---|---|
| 0.25 | unscrubbed originals | 97.5 | 85.0 (Study 3) | 100.0 (Study 3) | — | 8.0 (Study 3) | — |
| 0.25 | P-Qwen | 13.5 | 3.0 | 26.0 | 92.4 | 11.5 | 49.5 |
| 0.25 | P-Phi | 27.0 | 5.0 | 62.5 | 95.8 | 6.0 | 51.0 |
| 0.25 | E-true 5% | 21.0 | 3.5 | 58.0 | — | 7.0 | — |
| 0.25 | E-est 5% | 68.0 | 45.5 | 98.0 | — | 9.5 | — |
| 0.25 | E-rand 5% | 81.5 | 62.0 | 100.0 | — | 9.5 | — |
| 0.35 | unscrubbed originals | 96.0 | 93.0 (Study 3) | 100.0 (Study 3) | — | 32.0 (Study 3) | — |
| 0.35 | P-Qwen | 25.5 | 4.5 | 56.0 | 91.8 | 31.5 | 40.5 |
| 0.35 | P-Phi | 44.0 | 16.0 | 91.7 | 94.5 | 37.0 | 40.0 |
| 0.35 | E-true 5% | 55.5 | 21.5 | 92.0 | — | 30.5 | — |
| 0.35 | E-est 5% | 85.5 | 73.0 | 100.0 | — | 34.0 | — |
| 0.35 | E-rand 5% | 93.0 | 84.0 | 100.0 | — | 37.5 | — |
| 0.50 | unscrubbed originals | 99.0 | 98.5 (Study 3) | 100.0 (Study 3) | — | 86.0 (Study 3) | — |
| 0.50 | P-Qwen | 35.0 | 13.0 | 82.0 | 97.1 | 79.0 | 26.5 |
| 0.50 | P-Phi | 65.0 | 32.0 | 100.0 | 99.0 | 90.0 | 16.0 |
| 0.50 | E-true 5% | 80.5 | 56.0 | 100.0 | — | 88.0 | — |
| 0.50 | E-est 5% | 97.0 | 89.5 | 100.0 | — | 91.0 | — |
| 0.50 | E-rand 5% | 98.0 | 96.0 | 100.0 | — | 91.5 | — |
| 0.70 | unscrubbed originals | 100.0 | 98.0 (Study 3) | 100.0 (Study 3) | — | 100.0 (Study 3) | — |
| 0.70 | P-Qwen | 50.5 | 19.0 | 90.0 | 91.2 | 97.0 | 14.5 |
| 0.70 | P-Phi | 66.0 | 33.0 | 100.0 | 91.8 | 100.0 | 10.0 |
| 0.70 | E-true 5% | 89.5 | 65.5 | 100.0 | — | 100.0 | — |
| 0.70 | E-est 5% | 99.0 | 95.0 | 100.0 | — | 100.0 | — |
| 0.70 | E-rand 5% | 98.5 | 97.0 | 100.0 | — | 100.0 | — |

The length-matched control truncates each original to its paraphrase's token count and scores it with S4; it separates less text from removed evidence. The probe column is the share of scrubbed texts the owner's trained probe (Study 1) still accepts at its own 1% threshold (the C11 lead; labelled, not a result). First attempt only: success counting only the attacker's first paraphrase attempt (its self-check allows up to three).
