**T3b — Key recovery by the activation-mean estimator (Study 1 v0.2, rule R1) and what the repetition condition changed for v0.3's Route B forgeries at ρ = 0.70 (re-scored in v0.4)**

| ρ | quantity | median cos(v̂, v) at n = 64 / 256 / 1,024 (or FA, %) | layer = 14 (keys of 8) at n = 64 / 256 / 1,024 (or share, %) | verdict |
|---|---|---|---|---|
| 0.25 | Route A key recovery (v0.2) | 0.00 / 0.12 / 0.16 | 0 / 1 / 2 | fails at this budget |
| 0.35 | Route A key recovery (v0.2) | 0.10 / 0.08 / 0.07 | 1 / 2 / 2 | fails at this budget |
| 0.5 | Route A key recovery (v0.2) | 0.00 / 0.00 / 0.15 | 1 / 2 / 1 | fails at this budget |
| 0.7 | Route A key recovery (v0.2) | 0.00 / 0.00 / 0.01 | 1 / 2 / 2 | fails at this budget |
| 0.7 | v0.3 Route B forgeries, n = 64: perplexity-only FA → FA with the repetition term; share above the repetition bar | 69.0 → 2.5 | 76.0 | v0.3 F1 Route B at 0.70: inconclusive; F3 at 0.70 under v0.3's rule: yes |
| 0.7 | v0.3 Route B forgeries, n = 256: perplexity-only FA → FA with the repetition term; share above the repetition bar | 69.0 → 3.0 | 78.0 | v0.3 F1 Route B at 0.70: inconclusive; F3 at 0.70 under v0.3's rule: yes |

R1 asks for a median cosine of at least 0.9 with the layer found for at least 7 of 8 keys at some n ≤ 1,024. 'Share above the repetition bar' is the median over keys of the share of a condition's texts whose seq-rep-4 exceeds the key-level oracle's 95th percentile.
