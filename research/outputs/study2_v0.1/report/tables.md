## Table 1 — Pre-registered rules vs observed (protocol §7)

**P-Qwen (Qwen2.5-1.5B-Instruct).** G1 (pooled FPR over 8 keys × 1,000 paraphrased pool A texts, pass if 0.3–2.5%): 0.33% → **PASS**. G2 (a key is calibrated if its FPR ≤ 3.0%): 8 of 8 calibrated → verdicts **made**.

**P-Phi (Phi-3.5-mini-instruct).** G1 (pooled FPR over 8 keys × 1,000 paraphrased pool A texts, pass if 0.3–2.5%): 0.44% → **PASS**. G2 (a key is calibrated if its FPR ≤ 3.0%): 8 of 8 calibrated → verdicts **made**.

| ρ | P1: detected before, median (≥ 20%) | S1 P-Qwen: success [95% CI] vs originals' miss [95% CI]; keys ≥ 50% | S1 P-Phi: same | S2 E-true 5%: success [95% CI]; keys ≥ 50% | S2 E-est 5%: same | E-rand 5%: success [95% CI] | C1: E-est − E-rand, median [95% CI] |
|---|---|---|---|---|---|---|---|
| 0.25 | 97.5% (pass) | **effective**: 64.0 [54.5, 71.5] vs 2.5 [0.5, 6.5]; 7 of 8 | **effective**: 56.0 [48.0, 65.0] vs 3.0 [0.0, 6.0]; 7 of 8 | **effective**: 79.0 [72.0, 90.5]; 8 of 8 | **not effective**: 31.5 [21.0, 49.0]; 2 of 8 | 18.5 [12.0, 24.0] | **the estimate helps**: +14.5 [5.0, 28.0] |
| 0.35 | 96.0% (pass) | **effective**: 53.0 [37.5, 64.5] vs 4.0 [1.0, 6.5]; 5 of 8 | **inconclusive**: 42.0 [33.0, 57.0] vs 3.0 [0.0, 7.0]; 2 of 8 | **inconclusive**: 43.0 [33.0, 63.0]; 3 of 8 | **not effective**: 13.0 [7.5, 19.0]; 0 of 8 | 6.5 [3.0, 9.0] | **the estimate helps**: +6.5 [2.0, 11.0] |
| 0.50 | 99.0% (pass) | **not effective**: 39.5 [27.0, 48.0] vs 1.0 [0.0, 3.0]; 1 of 8 | **not effective**: 20.0 [14.0, 39.0] vs 0.0 [0.0, 2.0]; 1 of 8 | **not effective**: 18.5 [11.0, 32.5]; 1 of 8 | **not effective**: 2.5 [0.5, 8.5]; 0 of 8 | 2.0 [0.0, 5.0] | **no clear difference**: +0.0 [-0.5, 7.0] |
| 0.70 | 100.0% (pass) | **not effective**: 26.0 [16.0, 35.0] vs 0.0 [0.0, 2.0]; 1 of 8 | **not effective**: 13.0 [4.0, 29.0] vs 0.0 [0.0, 2.0]; 1 of 8 | **not effective**: 4.5 [2.0, 8.0]; 0 of 8 | **not effective**: 0.0 [0.0, 2.0]; 0 of 8 | 0.0 [0.0, 1.0] | **no clear difference**: +0.0 [-0.5, 0.0] |

Success = not detected by S4 at p ≤ 0.01 **and** all four quality conditions pass (fluency, repetition, length, meaning; protocol §5, normal range at the human 95th percentile). Medians over the calibrated keys (paraphrase: G2 per paraphraser; edits: all 8 keys, Study 3's calibration), with 95% cluster-bootstrap intervals (keys, then texts). P-Phi scrubs the first 50 genuine texts per key-level, the others all 100. "Random edits suffice" marks a level where E-rand's own median success at 5% reaches 50% (protocol §7, bounds).

## Table 2 — Calibration after paraphrase: each key's FPR at p ≤ 0.01 (%) on 1,000 pool A texts

| null texts | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | pooled | keys > 3% | fresh keys: mean FPR | fresh keys > 3% | probe FPR on pool A2 (median) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| unparaphrased (Study 3) | 0.7 | 0.1 | 0.8 | 0.6 | 1.7 | 1.0 | 1.3 | 0.3 | 0.81 | 0 | — | — | — |
| paraphrased by P-Qwen | 0.2 | 0.0 | 0.2 | 0.0 | 0.6 | 0.5 | 0.6 | 0.5 | 0.33 | 0 | 1.02 | 7.8% (max 22.6) | 3.3 |
| paraphrased by P-Phi | 0.4 | 0.0 | 0.0 | 0.5 | 0.2 | 1.4 | 0.3 | 0.7 | 0.44 | 0 | 0.94 | 6.5% (max 19.5) | 3.0 |

Fresh keys: 1,000 public-distribution keys never used by the owner (seeds 44,400,000 + j), each tested on the same paraphrased texts; the share above 3% estimates how often a newly drawn key would fail G2 after paraphrase. The probe row is the owner's trained probe (Study 1) at its own 1% threshold on the paraphrased pool A2 texts (secondary).

## Table 3 — Detection, quality and success per method (median over keys, %; ρ by row)

| ρ | method | detected after | success [95% CI] | keys ≥ 50% | passes fluency | repetition | length | meaning | all four | median ppl ratio | median length ratio | median cosine | success, model-text bar | success, human-median bar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.25 | P-Qwen | 13.5 | 64.0 [54.5, 71.5] | 7 | 99.0 | 99.5 | 89.0 | 80.5 | 75.0 | 1.97 | 0.99 | 0.886 | 3.5 | 23.0 |
| 0.25 | P-Phi | 27.0 | 56.0 [48.0, 65.0] | 7 | 100.0 | 100.0 | 98.0 | 84.0 | 83.0 | 2.03 | 1.05 | 0.902 | 3.0 | 17.0 |
| 0.25 | E-true 2% | 64.0 | 35.5 [26.5, 45.0] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.38 | 1.00 | 0.993 | 12.0 | 32.5 |
| 0.25 | E-est 2% | 82.0 | 17.5 [11.0, 22.5] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.39 | 1.00 | 0.992 | 6.0 | 16.5 |
| 0.25 | E-rand 2% | 92.0 | 8.0 [5.0, 11.5] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.33 | 1.00 | 0.995 | 4.0 | 8.0 |
| 0.25 | E-true 5% | 21.0 | 79.0 [72.0, 90.5] | 8 | 100.0 | 100.0 | 100.0 | 99.5 | 99.0 | 1.90 | 1.00 | 0.982 | 3.0 | 47.5 |
| 0.25 | E-est 5% | 68.0 | 31.5 [21.0, 49.0] | 2 | 100.0 | 100.0 | 100.0 | 99.5 | 99.0 | 1.92 | 1.00 | 0.977 | 1.5 | 20.5 |
| 0.25 | E-rand 5% | 81.5 | 18.5 [12.0, 24.0] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.5 | 1.78 | 1.00 | 0.987 | 2.0 | 13.0 |
| 0.25 | E-true 10% | 0.5 | 81.0 [74.0, 85.0] | 8 | 83.5 | 99.5 | 100.0 | 99.0 | 81.5 | 3.22 | 1.00 | 0.957 | 0.0 | 3.0 |
| 0.25 | E-est 10% | 39.5 | 50.5 [37.0, 72.0] | 4 | 84.0 | 100.0 | 100.0 | 97.0 | 81.5 | 3.22 | 1.00 | 0.949 | 0.0 | 2.5 |
| 0.25 | E-rand 10% | 62.5 | 31.0 [22.0, 39.5] | 0 | 92.0 | 100.0 | 100.0 | 98.5 | 89.5 | 2.90 | 1.00 | 0.968 | 0.0 | 5.0 |
| 0.35 | P-Qwen | 25.5 | 53.0 [37.5, 64.5] | 5 | 97.0 | 99.0 | 89.0 | 79.5 | 74.0 | 1.87 | 0.99 | 0.886 | 4.5 | 16.0 |
| 0.35 | P-Phi | 44.0 | 42.0 [33.0, 57.0] | 2 | 100.0 | 99.0 | 97.0 | 82.0 | 79.0 | 1.92 | 1.04 | 0.893 | 2.0 | 12.0 |
| 0.35 | E-true 2% | 86.0 | 13.5 [9.0, 20.5] | 0 | 100.0 | 99.5 | 100.0 | 100.0 | 99.5 | 1.35 | 1.00 | 0.992 | 5.0 | 12.0 |
| 0.35 | E-est 2% | 90.5 | 9.5 [2.5, 12.0] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.5 | 1.37 | 1.00 | 0.991 | 2.5 | 8.5 |
| 0.35 | E-rand 2% | 95.0 | 5.0 [1.5, 7.0] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.31 | 1.00 | 0.995 | 1.0 | 3.5 |
| 0.35 | E-true 5% | 55.5 | 43.0 [33.0, 63.0] | 3 | 99.0 | 99.5 | 100.0 | 99.0 | 98.0 | 1.84 | 1.00 | 0.978 | 1.0 | 21.0 |
| 0.35 | E-est 5% | 85.5 | 13.0 [7.5, 19.0] | 0 | 100.0 | 100.0 | 100.0 | 99.0 | 98.5 | 1.86 | 1.00 | 0.977 | 0.5 | 8.0 |
| 0.35 | E-rand 5% | 93.0 | 6.5 [3.0, 9.0] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.0 | 1.75 | 1.00 | 0.986 | 0.0 | 3.0 |
| 0.35 | E-true 10% | 7.0 | 62.0 [45.5, 68.0] | 6 | 66.0 | 99.5 | 100.0 | 99.0 | 64.0 | 3.03 | 1.00 | 0.951 | 0.0 | 2.0 |
| 0.35 | E-est 10% | 65.5 | 24.0 [9.5, 39.5] | 0 | 68.5 | 100.0 | 100.0 | 96.0 | 66.0 | 3.05 | 1.00 | 0.948 | 0.0 | 1.0 |
| 0.35 | E-rand 10% | 85.0 | 10.5 [5.5, 16.5] | 0 | 76.5 | 100.0 | 100.0 | 98.5 | 76.0 | 2.80 | 1.00 | 0.967 | 0.0 | 1.0 |
| 0.50 | P-Qwen | 35.0 | 39.5 [27.0, 48.0] | 1 | 91.5 | 99.5 | 92.0 | 76.5 | 64.0 | 1.61 | 0.99 | 0.874 | 5.0 | 6.0 |
| 0.50 | P-Phi | 65.0 | 20.0 [14.0, 39.0] | 1 | 92.0 | 99.0 | 99.0 | 79.0 | 76.0 | 1.71 | 1.04 | 0.882 | 3.0 | 5.0 |
| 0.50 | E-true 2% | 96.5 | 3.0 [1.0, 7.5] | 0 | 99.5 | 100.0 | 100.0 | 100.0 | 99.0 | 1.32 | 1.00 | 0.990 | 0.5 | 3.0 |
| 0.50 | E-est 2% | 97.0 | 3.0 [0.0, 6.0] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.33 | 1.00 | 0.989 | 0.0 | 1.5 |
| 0.50 | E-rand 2% | 98.5 | 1.5 [0.0, 3.5] | 0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.5 | 1.29 | 1.00 | 0.994 | 0.5 | 1.0 |
| 0.50 | E-true 5% | 80.5 | 18.5 [11.0, 32.5] | 1 | 96.5 | 100.0 | 100.0 | 99.0 | 95.5 | 1.73 | 1.00 | 0.974 | 0.0 | 2.0 |
| 0.50 | E-est 5% | 97.0 | 2.5 [0.5, 8.5] | 0 | 95.0 | 100.0 | 100.0 | 99.0 | 93.5 | 1.74 | 1.00 | 0.971 | 0.0 | 1.0 |
| 0.50 | E-rand 5% | 98.0 | 2.0 [0.0, 5.0] | 0 | 97.5 | 100.0 | 100.0 | 100.0 | 96.0 | 1.68 | 1.00 | 0.982 | 0.0 | 0.5 |
| 0.50 | E-true 10% | 19.5 | 28.0 [14.0, 31.5] | 0 | 31.5 | 100.0 | 100.0 | 96.5 | 29.5 | 2.74 | 1.00 | 0.944 | 0.0 | 0.5 |
| 0.50 | E-est 10% | 88.0 | 6.0 [3.0, 19.0] | 0 | 34.0 | 100.0 | 100.0 | 96.0 | 32.0 | 2.73 | 1.00 | 0.938 | 0.0 | 0.0 |
| 0.50 | E-rand 10% | 96.0 | 3.0 [0.5, 5.5] | 0 | 42.5 | 100.0 | 100.0 | 98.5 | 42.5 | 2.58 | 1.00 | 0.961 | 0.0 | 0.0 |
| 0.70 | P-Qwen | 50.5 | 26.0 [16.0, 35.0] | 1 | 77.5 | 99.5 | 92.0 | 71.0 | 49.5 | 1.22 | 0.99 | 0.864 | 15.0 | 14.5 |
| 0.70 | P-Phi | 66.0 | 13.0 [4.0, 29.0] | 1 | 76.0 | 100.0 | 100.0 | 73.0 | 52.0 | 1.34 | 1.04 | 0.870 | 6.0 | 5.0 |
| 0.70 | E-true 2% | 98.5 | 1.0 [0.0, 5.5] | 1 | 91.5 | 100.0 | 100.0 | 100.0 | 89.5 | 1.24 | 1.00 | 0.987 | 1.0 | 1.0 |
| 0.70 | E-est 2% | 99.0 | 0.5 [0.0, 4.0] | 1 | 90.5 | 100.0 | 100.0 | 100.0 | 88.5 | 1.24 | 1.00 | 0.986 | 0.0 | 0.0 |
| 0.70 | E-rand 2% | 99.5 | 0.5 [0.0, 2.5] | 1 | 92.5 | 100.0 | 100.0 | 100.0 | 91.5 | 1.23 | 1.00 | 0.993 | 0.0 | 0.0 |
| 0.70 | E-true 5% | 89.5 | 4.5 [2.0, 8.0] | 0 | 41.5 | 100.0 | 100.0 | 99.5 | 41.5 | 1.56 | 1.00 | 0.967 | 0.0 | 0.5 |
| 0.70 | E-est 5% | 99.0 | 0.0 [0.0, 2.0] | 0 | 39.0 | 100.0 | 100.0 | 98.5 | 38.5 | 1.56 | 1.00 | 0.966 | 0.0 | 0.0 |
| 0.70 | E-rand 5% | 98.5 | 0.0 [0.0, 1.0] | 0 | 40.5 | 100.0 | 100.0 | 100.0 | 39.0 | 1.57 | 1.00 | 0.981 | 0.0 | 0.0 |
| 0.70 | E-true 10% | 40.0 | 3.0 [0.5, 6.0] | 0 | 3.5 | 100.0 | 100.0 | 95.5 | 3.5 | 2.30 | 1.00 | 0.929 | 0.0 | 0.0 |
| 0.70 | E-est 10% | 94.5 | 1.0 [0.0, 2.5] | 0 | 4.0 | 100.0 | 100.0 | 92.5 | 3.5 | 2.29 | 1.00 | 0.928 | 0.0 | 0.0 |
| 0.70 | E-rand 10% | 97.5 | 0.0 [0.0, 1.5] | 0 | 4.0 | 100.0 | 100.0 | 98.0 | 3.5 | 2.25 | 1.00 | 0.954 | 0.0 | 0.0 |

Normal range (pool A's human continuations, 95th percentile): perplexity 25.41, seq-rep-4 0.0484; meaning bar (cosine, 95th percentile of same-prompt pairs) 0.825. Stricter readings (secondary): model-text 95th percentile (perplexity 7.35, seq-rep-4 0.0514) and human median (perplexity 12.94, seq-rep-4 0.0044). The attacker's own bars (pool C): perplexity 22.17, seq-rep-4 0.0480, cosine 0.810. Ratios are scrub / original (length: original counted up to 256 tokens).

## Table 4 — Per-key success (%), the per-unit view behind every median (keys excluded by G2 shown as —)

| ρ | method | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | median | keys ≥ 50% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.25 | P-Qwen | 65 | 71 | 66 | 79 | 58 | 46 | 63 | 55 | 64.0 | 7 |
| 0.25 | P-Phi | 56 | 78 | 56 | 54 | 58 | 44 | 58 | 50 | 56.0 | 7 |
| 0.25 | E-true 5% | 63 | 90 | 93 | 90 | 78 | 72 | 79 | 79 | 79.0 | 8 |
| 0.25 | E-est 5% | 16 | 60 | 37 | 52 | 37 | 26 | 21 | 24 | 31.5 | 2 |
| 0.25 | E-rand 5% | 6 | 28 | 14 | 21 | 19 | 15 | 18 | 24 | 18.5 | 0 |
| 0.25 | E-true 10% | 76 | 82 | 87 | 83 | 81 | 81 | 77 | 67 | 81.0 | 8 |
| 0.25 | E-est 10% | 39 | 78 | 59 | 75 | 66 | 42 | 39 | 31 | 50.5 | 4 |
| 0.25 | E-rand 10% | 20 | 43 | 27 | 41 | 36 | 20 | 31 | 31 | 31.0 | 0 |
| 0.35 | P-Qwen | 54 | 64 | 52 | 69 | 33 | 34 | 62 | 44 | 53.0 | 5 |
| 0.35 | P-Phi | 38 | 68 | 58 | 46 | 34 | 26 | 46 | 38 | 42.0 | 2 |
| 0.35 | E-true 5% | 29 | 84 | 64 | 56 | 34 | 35 | 49 | 37 | 43.0 | 3 |
| 0.35 | E-est 5% | 0 | 33 | 14 | 14 | 17 | 12 | 11 | 9 | 13.0 | 0 |
| 0.35 | E-rand 5% | 0 | 8 | 7 | 6 | 8 | 9 | 5 | 5 | 6.5 | 0 |
| 0.35 | E-true 10% | 43 | 63 | 73 | 68 | 63 | 61 | 55 | 29 | 62.0 | 6 |
| 0.35 | E-est 10% | 7 | 46 | 29 | 43 | 33 | 16 | 19 | 6 | 24.0 | 0 |
| 0.35 | E-rand 10% | 2 | 26 | 8 | 13 | 15 | 7 | 13 | 7 | 10.5 | 0 |
| 0.50 | P-Qwen | 37 | 64 | 42 | 44 | 25 | 13 | 45 | 35 | 39.5 | 1 |
| 0.50 | P-Phi | 18 | 64 | 42 | 16 | 16 | 14 | 22 | 22 | 20.0 | 1 |
| 0.50 | E-true 5% | 16 | 72 | 33 | 10 | 8 | 20 | 17 | 27 | 18.5 | 1 |
| 0.50 | E-est 5% | 1 | 29 | 9 | 3 | 1 | 2 | 0 | 4 | 2.5 | 0 |
| 0.50 | E-rand 5% | 1 | 12 | 0 | 3 | 1 | 3 | 0 | 4 | 2.0 | 0 |
| 0.50 | E-true 10% | 13 | 29 | 28 | 33 | 19 | 28 | 29 | 7 | 28.0 | 0 |
| 0.50 | E-est 10% | 3 | 27 | 23 | 8 | 6 | 6 | 2 | 4 | 6.0 | 0 |
| 0.50 | E-rand 10% | 0 | 19 | 2 | 3 | 3 | 3 | 2 | 4 | 3.0 | 0 |
| 0.70 | P-Qwen | 19 | 53 | 34 | 24 | 14 | 14 | 28 | 29 | 26.0 | 1 |
| 0.70 | P-Phi | 10 | 60 | 16 | 4 | 10 | 2 | 20 | 28 | 13.0 | 1 |
| 0.70 | E-true 5% | 6 | 43 | 2 | 1 | 3 | 6 | 4 | 5 | 4.5 | 0 |
| 0.70 | E-est 5% | 0 | 29 | 0 | 0 | 0 | 2 | 0 | 0 | 0.0 | 0 |
| 0.70 | E-rand 5% | 0 | 35 | 0 | 0 | 1 | 0 | 0 | 0 | 0.0 | 0 |
| 0.70 | E-true 10% | 1 | 8 | 0 | 4 | 6 | 4 | 2 | 1 | 3.0 | 0 |
| 0.70 | E-est 10% | 1 | 8 | 1 | 2 | 1 | 1 | 0 | 0 | 1.0 | 0 |
| 0.70 | E-rand 10% | 0 | 12 | 0 | 1 | 1 | 0 | 0 | 0 | 0.0 | 0 |

## Table 5 — Secondary readings (median over keys unless stated, %)

| ρ | method | detected after (p ≤ 0.01) | at p ≤ 0.001 (9,999 null keys) | 4 texts pooled: detected | length-matched originals: detected (pooled; median over keys) | owner's probe accepts | first attempt only: success |
|---|---|---|---|---|---|---|---|
| 0.25 | unscrubbed | 97.5 | 85.0 (Study 3) | 100.0 (Study 3) | — | 8.0 (Study 3) | — |
| 0.25 | P-Qwen | 13.5 | 3.0 | 26.0 | 92.4; 92.5 | 11.5 | 49.5 |
| 0.25 | P-Phi | 27.0 | 5.0 | 62.5 | 95.8; 96.0 | 6.0 | 51.0 |
| 0.25 | E-true 5% | 21.0 | 3.5 | 58.0 | — | 7.0 | — |
| 0.25 | E-est 5% | 68.0 | 45.5 | 98.0 | — | 9.5 | — |
| 0.25 | E-rand 5% | 81.5 | 62.0 | 100.0 | — | 9.5 | — |
| 0.35 | unscrubbed | 96.0 | 93.0 (Study 3) | 100.0 (Study 3) | — | 32.0 (Study 3) | — |
| 0.35 | P-Qwen | 25.5 | 4.5 | 56.0 | 91.8; 91.0 | 31.5 | 40.5 |
| 0.35 | P-Phi | 44.0 | 16.0 | 91.7 | 94.5; 95.0 | 37.0 | 40.0 |
| 0.35 | E-true 5% | 55.5 | 21.5 | 92.0 | — | 30.5 | — |
| 0.35 | E-est 5% | 85.5 | 73.0 | 100.0 | — | 34.0 | — |
| 0.35 | E-rand 5% | 93.0 | 84.0 | 100.0 | — | 37.5 | — |
| 0.50 | unscrubbed | 99.0 | 98.5 (Study 3) | 100.0 (Study 3) | — | 86.0 (Study 3) | — |
| 0.50 | P-Qwen | 35.0 | 13.0 | 82.0 | 97.1; 97.0 | 79.0 | 26.5 |
| 0.50 | P-Phi | 65.0 | 32.0 | 100.0 | 99.0; 100.0 | 90.0 | 16.0 |
| 0.50 | E-true 5% | 80.5 | 56.0 | 100.0 | — | 88.0 | — |
| 0.50 | E-est 5% | 97.0 | 89.5 | 100.0 | — | 91.0 | — |
| 0.50 | E-rand 5% | 98.0 | 96.0 | 100.0 | — | 91.5 | — |
| 0.70 | unscrubbed | 100.0 | 98.0 (Study 3) | 100.0 (Study 3) | — | 100.0 (Study 3) | — |
| 0.70 | P-Qwen | 50.5 | 19.0 | 90.0 | 91.2; 99.0 | 97.0 | 14.5 |
| 0.70 | P-Phi | 66.0 | 33.0 | 100.0 | 91.8; 100.0 | 100.0 | 10.0 |
| 0.70 | E-true 5% | 89.5 | 65.5 | 100.0 | — | 100.0 | — |
| 0.70 | E-est 5% | 99.0 | 95.0 | 100.0 | — | 100.0 | — |
| 0.70 | E-rand 5% | 98.5 | 97.0 | 100.0 | — | 100.0 | — |

The 0.001 and pooled readings use all 8 keys (median). The length-matched control truncates each original to its paraphrase's token count and scores it with S4: it separates "less text" from "evidence removed". The probe column is the share of scrubbed texts the owner's trained probe still accepts at its 1% threshold.

Paraphrase attempts kept (genuine texts): P-Qwen: attempt 1 1835, attempt 2 822, attempt 3 543; kept but still failing the attacker's own check 1025 of 3200; P-Phi: attempt 1 1064, attempt 2 308, attempt 3 228; kept but still failing the attacker's own check 457 of 1600.

Edits: E-true: stalled before 10% in 8 texts, median re-tokenisation drift 2% 0.000, 5% 0.000, 10% 0.000, attacker's objective (median) 3.15 → 2.17 → 1.41 → 0.57; E-est: stalled before 10% in 8 texts, median re-tokenisation drift 2% 0.000, 5% 0.000, 10% 0.000, attacker's objective (median) 0.43 → 0.00 → -0.31 → -0.68; E-rand: stalled before 10% in 8 texts, median re-tokenisation drift 2% 0.000, 5% 0.000, 10% 0.000.

## Table 6 — The edit curve: success, detection and quality by budget (median over all 8 keys, %)

| ρ | arm | success 0% (originals' miss) | success 2% | 5% | 10% | detected 2% | 5% | 10% | all four quality 2% | 5% | 10% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.25 | E-true | 2.5 | 35.5 | 79.0 | 81.0 | 64.0 | 21.0 | 0.5 | 100.0 | 99.0 | 81.5 |
| 0.25 | E-est | 2.5 | 17.5 | 31.5 | 50.5 | 82.0 | 68.0 | 39.5 | 100.0 | 99.0 | 81.5 |
| 0.25 | E-rand | 2.5 | 8.0 | 18.5 | 31.0 | 92.0 | 81.5 | 62.5 | 100.0 | 99.5 | 89.5 |
| 0.35 | E-true | 4.0 | 13.5 | 43.0 | 62.0 | 86.0 | 55.5 | 7.0 | 99.5 | 98.0 | 64.0 |
| 0.35 | E-est | 4.0 | 9.5 | 13.0 | 24.0 | 90.5 | 85.5 | 65.5 | 99.5 | 98.5 | 66.0 |
| 0.35 | E-rand | 4.0 | 5.0 | 6.5 | 10.5 | 95.0 | 93.0 | 85.0 | 100.0 | 99.0 | 76.0 |
| 0.50 | E-true | 1.0 | 3.0 | 18.5 | 28.0 | 96.5 | 80.5 | 19.5 | 99.0 | 95.5 | 29.5 |
| 0.50 | E-est | 1.0 | 3.0 | 2.5 | 6.0 | 97.0 | 97.0 | 88.0 | 100.0 | 93.5 | 32.0 |
| 0.50 | E-rand | 1.0 | 1.5 | 2.0 | 3.0 | 98.5 | 98.0 | 96.0 | 99.5 | 96.0 | 42.5 |
| 0.70 | E-true | 0.0 | 1.0 | 4.5 | 3.0 | 98.5 | 89.5 | 40.0 | 89.5 | 41.5 | 3.5 |
| 0.70 | E-est | 0.0 | 0.5 | 0.0 | 1.0 | 99.0 | 99.0 | 94.5 | 88.5 | 38.5 | 3.5 |
| 0.70 | E-rand | 0.0 | 0.5 | 0.0 | 0.0 | 99.5 | 98.5 | 97.5 | 91.5 | 39.0 | 3.5 |

Key leakage (secondary): Spearman correlation between the attacker's recovered cosine cos(v̂, v) and E-est's success at 5%, over the 32 key-levels: 0.13 (descriptive; Fig. 4).

