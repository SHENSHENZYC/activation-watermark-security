## Table 1 — Pre-registered rules vs observed (protocol §9)

- **context-hashed, h = 1:** G1 pooled FPR over 8 secrets × 1,000 pool A texts 0.83% (pass if 0.3–2.5%) → **PASS**; G2 8 of 8 keys calibrated (FPR ≤ 3.0%) → verdicts **made**.
- **context-hashed, h = 4:** G1 pooled FPR over 8 secrets × 1,000 pool A texts 0.95% (pass if 0.3–2.5%) → **PASS**; G2 8 of 8 keys calibrated (FPR ≤ 3.0%) → verdicts **made**.
- **Union test (rotation):** G1 pooled FPR 1.00% → **PASS**.
- **P0, the threat at ρ = 0.35:** the fixed key under Route A′ is **practical (n=64)** (forgery FA at n = 64 / 256 / 1,024: 88.0 [76.5, 93.0] / 87.0 [82.0, 92.5] / 85.0 [78.5, 89.0]%, bar 43.2% = half the genuine FA 86.5%, random-key control 0.0 [0.0, 0.5]%) → defence verdicts at this strength are **made**.
- **P0, the threat at ρ = 0.50:** the fixed key under Route A′ is **practical (n=64)** (forgery FA at n = 64 / 256 / 1,024: 85.5 [82.5, 90.0] / 84.0 [80.5, 91.0] / 87.5 [81.0, 91.5]%, bar 45.0% = half the genuine FA 90.0%, random-key control 0.0 [0.0, 0.5]%) → defence verdicts at this strength are **made**.

| arm | ρ | P1: genuine detection, median [95% CI] (≥ 50%) | D1 stealing: forgery FA at n = 64 / 256 / 1,024 [95% CI]; bar; control → verdict | D2 robustness cost: scrub success [95% CI] vs the fixed key's; d = median difference [95% CI]; keys ≥ 20 pts → verdict (absolute reading) | D3 quality cost: perplexity ratio arm/fixed, median [95% CI]; keys > 1.10 → verdict |
|---|---|---|---|---|---|
| context-hashed, h = 1 | 0.35 | 92.5 [89.0, 94.5]% (pass) | 1.0 [0.0, 2.5] / 2.5 [0.0, 4.0] / 3.5 [2.0, 6.5]%; bar 42.0% (genuine FA 84.0%); control 1.0 [0.0, 1.5]% → **stealing blocked at n <= 1024** | 73.0 [68.0, 78.0]% vs 53.0 [38.0, 64.5]%; d = +22.0 [6.0, 36.5]; 5 of 8 → **material robustness cost** (paraphrase effective (>= 50%)) | 0.852 [0.790, 0.874]; 0 of 8 → **immaterial** |
| context-hashed, h = 1 | 0.50 | 96.5 [94.0, 98.5]% (pass) | 1.5 [0.0, 3.0] / 3.0 [1.0, 6.0] / 9.0 [5.5, 11.0]%; bar 44.0% (genuine FA 88.0%); control 1.0 [0.0, 1.0]% → **stealing blocked at n <= 1024** | 70.5 [66.5, 74.5]% vs 39.5 [26.0, 48.5]%; d = +32.0 [21.0, 44.0]; 7 of 8 → **material robustness cost** (paraphrase effective (>= 50%)) | 0.722 [0.682, 0.799]; 0 of 8 → **immaterial** |
| context-hashed, h = 4 | 0.35 | 90.0 [87.0, 92.5]% (pass) | 1.0 [0.0, 2.5] / 1.0 [0.0, 2.0] / 0.0 [0.0, 0.0]%; bar 40.0% (genuine FA 80.0%); control 0.5 [0.0, 1.5]% → **stealing blocked at n <= 1024** | 72.0 [67.5, 76.5]% vs 53.0 [38.0, 64.5]%; d = +18.0 [7.5, 33.5]; 3 of 8 → **inconclusive** (paraphrase effective (>= 50%)) | 0.832 [0.787, 0.879]; 0 of 8 → **immaterial** |
| context-hashed, h = 4 | 0.50 | 95.5 [93.0, 97.5]% (pass) | 1.0 [0.0, 2.0] / 0.5 [0.0, 1.5] / 1.0 [0.0, 2.0]%; bar 43.8% (genuine FA 87.5%); control 0.5 [0.0, 1.5]% → **stealing blocked at n <= 1024** | 69.5 [64.5, 74.5]% vs 39.5 [26.0, 48.5]%; d = +32.5 [19.0, 45.5]; 7 of 8 → **material robustness cost** (paraphrase effective (>= 50%)) | 0.717 [0.686, 0.791]; 0 of 8 → **immaterial** |
| rotation (K = 8) | 0.35 | union test 93.0 [87.5, 96.5]% (pass; told which key: 96.0 [93.5, 99.0]%) | naive: 0.0 [0.0, 0.0] / 1.0 [0.0, 3.0] / 1.0 [0.0, 3.0]% → **stealing blocked at n <= 1024**; cluster: 8.0 [3.0, 14.0] / 2.0 [0.0, 5.0] / 0.0 [0.0, 0.0]% → **stealing blocked at n <= 1024**; bar 43.2% (the fixed oracle FA 86.5%); control 0.0 [0.0, 0.5]% | union-test success on Study 2's paraphrases 70.0% vs 53.0 [38.0, 64.5]%; d = +15.0 [9.5, 18.5] → **immaterial** | unchanged by construction (not tested) |
| rotation (K = 8) | 0.50 | union test 98.5 [95.0, 100.0]% (pass; told which key: 99.0 [97.0, 100.0]%) | naive: 0.0 [0.0, 0.0] / 12.0 [6.0, 18.0] / 0.0 [0.0, 0.0]% → **stealing blocked at n <= 1024**; cluster: 95.0 [90.0, 99.0] / 95.0 [90.0, 99.0] / 96.0 [92.0, 99.0]% → **practical (n=64)**; bar 45.0% (the fixed oracle FA 90.0%); control 0.0 [0.0, 0.5]% | union-test success on Study 2's paraphrases 52.5% vs 39.5 [26.0, 48.5]%; d = +13.0 [8.5, 17.5] → **immaterial** | unchanged by construction (not tested) |

FA = accepted at p ≤ 0.01 **and** fluent (perplexity and seq-rep-4 at most the arm's own genuine texts' 95th percentiles at that key-level; rotation: the level's pooled oracle percentiles). Scrub success = not detected at p ≤ 0.01 **and** Study 2's four quality conditions (fluency, repetition, length, meaning; the owner's bars). Medians over calibrated keys with 95% cluster-bootstrap intervals (keys, then texts); D2's interval is paired (the same keys and prompts). The fixed key's scrub success is Study 2's P-Qwen result on the same prompts and keys, re-computed here from Study 2's locked paraphrases.

## Table 2 — Detection, quality and power per arm (median over calibrated keys; ρ by row)

| arm | ρ | genuine detection % [95% CI] | at p ≤ 0.05 / 0.10 | 4 texts pooled | genuine FA % | control FA % | perplexity: median keyed / median fixed; ratio | seq-rep-4 keyed / fixed | tokenisation round trip (ρ = 0.50) |
|---|---|---|---|---|---|---|---|---|---|
| fixed key (h = 0) (S4, Study 3's features) | 0.35 | 96.0 | 98.5 / 99.5 | 100.0 | 86.5 [83.5, 90.5] | 0.0 [0.0, 0.5] | 7.55 (reference; ratio 1) | 0.0000 (reference) | — |
| context-hashed, h = 1 | 0.35 | 92.5 [89.0, 94.5] | 98.5 / 99.5 | 100.0 | 84.0 [79.5, 86.5] | 1.0 [0.0, 1.5] | 6.45 / 7.55; 0.852 [0.790, 0.874] | 0.0040 / 0.0000 | 0.985 |
| context-hashed, h = 4 | 0.35 | 90.0 [87.0, 92.5] | 97.0 / 99.0 | 100.0 | 80.0 [77.0, 84.0] | 0.5 [0.0, 1.5] | 6.35 / 7.55; 0.832 [0.787, 0.879] | 0.0000 / 0.0000 | 1.000 |
| rotation (K = 8) (union test) | 0.35 | 93.0 [87.5, 96.5] (told which key: 96.0 [93.5, 99.0]) | — | — | — | — | unchanged | unchanged | — |
| fixed key (h = 0) (S4, Study 3's features) | 0.50 | 99.0 | 99.0 / 99.0 | 100.0 | 90.0 [87.0, 92.5] | 0.0 [0.0, 0.5] | 10.44 (reference; ratio 1) | 0.0000 (reference) | — |
| context-hashed, h = 1 | 0.50 | 96.5 [94.0, 98.5] | 99.0 / 99.5 | 100.0 | 88.0 [85.0, 90.5] | 1.0 [0.0, 1.0] | 7.72 / 10.44; 0.722 [0.682, 0.799] | 0.0000 / 0.0000 | 0.985 |
| context-hashed, h = 4 | 0.50 | 95.5 [93.0, 97.5] | 98.0 / 99.5 | 100.0 | 87.5 [84.0, 90.5] | 0.5 [0.0, 1.5] | 7.68 / 10.44; 0.717 [0.686, 0.791] | 0.0000 / 0.0000 | 1.000 |
| rotation (K = 8) (union test) | 0.50 | 98.5 [95.0, 100.0] (told which key: 99.0 [97.0, 100.0]) | — | — | — | — | unchanged | unchanged | — |

The keyed arms' texts are new generations on Study 1's oracle prompts (pool D, 100 per key-level); the fixed key's are Study 1's oracle texts on the same prompts, so the perplexity ratio is paired by prompt and key. Round trip: first 20 genuine texts per key. Pooled: four consecutive genuine texts' statistics summed before the null comparison (25 tests per key-level).

## Table 3 — Key recovery and forgery acceptance against the attacker's budget n (median over keys)

| arm | ρ | n | recovery | forgery FA % [95% CI] |
|---|---|---|---|---|
| fixed key (h = 0), Route A′ | 0.35 | 64 | cos(v̂, v) known layer 0.94; layer search 0.93 (layer 14 found for 6 of 8 keys) | 88.0 [76.5, 93.0] |
| fixed key (h = 0), Route A′ | 0.35 | 256 | cos(v̂, v) known layer 0.95; layer search 0.93 (layer 14 found for 6 of 8 keys) | 87.0 [82.0, 92.5]; layer-search forgery 86.0 [81.5, 90.5] |
| fixed key (h = 0), Route A′ | 0.35 | 1024 | cos(v̂, v) known layer 0.95; layer search 0.95 (layer 14 found for 6 of 8 keys) | 85.0 [78.5, 89.0] |
| context-hashed, h = 1, per-context attacker (layer given) | 0.35 | 64 | count-weighted cos 0.022; coverage of genuine positions 0.487; contexts estimated 148 | 1.0 [0.0, 2.5] |
| context-hashed, h = 1, per-context attacker (layer given) | 0.35 | 256 | count-weighted cos 0.089; coverage of genuine positions 0.639; contexts estimated 527 | 2.5 [0.0, 4.0] |
| context-hashed, h = 1, per-context attacker (layer given) | 0.35 | 1024 | count-weighted cos 0.170; coverage of genuine positions 0.798; contexts estimated 1942 | 3.5 [2.0, 6.5] |
| context-hashed, h = 4, per-context attacker (layer given) | 0.35 | 64 | count-weighted cos 0.000; coverage of genuine positions 0.001; contexts estimated 0 | 1.0 [0.0, 2.5] |
| context-hashed, h = 4, per-context attacker (layer given) | 0.35 | 256 | count-weighted cos 0.000; coverage of genuine positions 0.004; contexts estimated 9 | 1.0 [0.0, 2.0] |
| context-hashed, h = 4, per-context attacker (layer given) | 0.35 | 1024 | count-weighted cos 0.012; coverage of genuine positions 0.013; contexts estimated 89 | 0.0 [0.0, 0.0] |
| rotation (K = 8), naive Route A′ on the mixture | 0.35 | 64 | best cos with any key 0.00 (key 1001) | 0.0 [0.0, 0.0] |
| rotation (K = 8), clustering attacker | 0.35 | 64 | keys recovered at cos ≥ 0.5: 4 of 8; median best cos over clusters 0.56; the forging cluster (largest z-profile): cos 0.31 with key 1005, 3 texts | 8.0 [3.0, 14.0] |
| rotation (K = 8), naive Route A′ on the mixture | 0.35 | 256 | best cos with any key 0.00 (key 1001) | 1.0 [0.0, 3.0] |
| rotation (K = 8), clustering attacker | 0.35 | 256 | keys recovered at cos ≥ 0.5: 6 of 8; median best cos over clusters 0.83; the forging cluster (largest z-profile): cos 0.00 with key 1001, 17 texts | 2.0 [0.0, 5.0] |
| rotation (K = 8), naive Route A′ on the mixture | 0.35 | 1024 | best cos with any key 0.00 (key 1001) | 1.0 [0.0, 3.0] |
| rotation (K = 8), clustering attacker | 0.35 | 1024 | keys recovered at cos ≥ 0.5: 6 of 8; median best cos over clusters 0.87; the forging cluster (largest z-profile): cos 0.00 with key 1001, 92 texts | 0.0 [0.0, 0.0] |
| fixed key (h = 0), Route A′ | 0.50 | 64 | cos(v̂, v) known layer 0.95; layer search 0.92 (layer 14 found for 6 of 8 keys) | 85.5 [82.5, 90.0] |
| fixed key (h = 0), Route A′ | 0.50 | 256 | cos(v̂, v) known layer 0.95; layer search 0.95 (layer 14 found for 7 of 8 keys) | 84.0 [80.5, 91.0]; layer-search forgery 87.5 [80.5, 93.0] |
| fixed key (h = 0), Route A′ | 0.50 | 1024 | cos(v̂, v) known layer 0.95; layer search 0.92 (layer 14 found for 6 of 8 keys) | 87.5 [81.0, 91.5] |
| context-hashed, h = 1, per-context attacker (layer given) | 0.50 | 64 | count-weighted cos 0.065; coverage of genuine positions 0.503; contexts estimated 154 | 1.5 [0.0, 3.0] |
| context-hashed, h = 1, per-context attacker (layer given) | 0.50 | 256 | count-weighted cos 0.145; coverage of genuine positions 0.653; contexts estimated 525 | 3.0 [1.0, 6.0] |
| context-hashed, h = 1, per-context attacker (layer given) | 0.50 | 1024 | count-weighted cos 0.213; coverage of genuine positions 0.800; contexts estimated 1878 | 9.0 [5.5, 11.0] |
| context-hashed, h = 4, per-context attacker (layer given) | 0.50 | 64 | count-weighted cos 0.000; coverage of genuine positions 0.001; contexts estimated 1 | 1.0 [0.0, 2.0] |
| context-hashed, h = 4, per-context attacker (layer given) | 0.50 | 256 | count-weighted cos 0.000; coverage of genuine positions 0.002; contexts estimated 7 | 0.5 [0.0, 1.5] |
| context-hashed, h = 4, per-context attacker (layer given) | 0.50 | 1024 | count-weighted cos 0.012; coverage of genuine positions 0.008; contexts estimated 61 | 1.0 [0.0, 2.0] |
| rotation (K = 8), naive Route A′ on the mixture | 0.50 | 64 | best cos with any key 0.00 (key 1001) | 0.0 [0.0, 0.0] |
| rotation (K = 8), clustering attacker | 0.50 | 64 | keys recovered at cos ≥ 0.5: 7 of 8; median best cos over clusters 0.86; the forging cluster (largest z-profile): cos 0.95 with key 1004, 8 texts | 95.0 [90.0, 99.0] |
| rotation (K = 8), naive Route A′ on the mixture | 0.50 | 256 | best cos with any key 0.36 (key 1006) | 12.0 [6.0, 18.0] |
| rotation (K = 8), clustering attacker | 0.50 | 256 | keys recovered at cos ≥ 0.5: 8 of 8; median best cos over clusters 0.95; the forging cluster (largest z-profile): cos 0.96 with key 1004, 32 texts | 95.0 [90.0, 99.0] |
| rotation (K = 8), naive Route A′ on the mixture | 0.50 | 1024 | best cos with any key 0.00 (key 1001) | 0.0 [0.0, 0.0] |
| rotation (K = 8), clustering attacker | 0.50 | 1024 | keys recovered at cos ≥ 0.5: 8 of 8; median best cos over clusters 0.95; the forging cluster (largest z-profile): cos 0.96 with key 1004, 128 texts | 96.0 [92.0, 99.0] |

Recovery for the fixed key: the cosine between the attacker's 4-sparse estimate and the true key (Study 1's Route A rule on the exact test's gradient statistic). For the hashed arms: the mean cosine over estimated contexts with the true per-context keys, weighted by context count; coverage = the share of a genuine text's scored positions whose context has an estimate. Rotation's forgeries use the cluster with the largest z-profile.

## Table 4 — Paraphrase (P-Qwen with the attacker's self-check) per arm beside the fixed key (median over calibrated keys, %)

| arm | ρ | scrub success [95% CI] | detected after | 4 paraphrases pooled: detected | quality: all four pass | fluency / repetition / length / meaning pass | success, model-text bar | success, human-median bar | d vs the fixed key [95% CI]; keys ≥ 20 pts | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed key (h = 0) (Study 2) | 0.35 | 53.0 [38.0, 64.5] | 25.5 | 56.0 (Study 2) | 74.0 | — | 4.5 | 16.0 | — | effective (Study 2's S1) |
| context-hashed, h = 1 | 0.35 | 73.0 [68.0, 78.0] | 3.0 [1.0, 5.0] | 4.0 | 75.5 [71.0, 80.5] | 99.0 / 99.0 / 88.5 / 80.5 | 5.0 | 31.5 | +22.0 [6.0, 36.5]; 5 of 8 | **material robustness cost** (paraphrase effective (>= 50%)) |
| context-hashed, h = 4 | 0.35 | 72.0 [67.5, 76.5] | 1.0 [0.0, 2.0] | 0.0 | 73.0 [68.5, 78.0] | 98.0 / 100.0 / 87.0 / 78.0 | 5.5 | 31.0 | +18.0 [7.5, 33.5]; 3 of 8 | **inconclusive** (paraphrase effective (>= 50%)) |
| rotation (K = 8) (union test on Study 2's paraphrases) | 0.35 | 70.0 | 5.5 | — | as the fixed key | — | — | — | +15.0 [9.5, 18.5] | **immaterial** |
| fixed key (h = 0) (Study 2) | 0.50 | 39.5 [26.0, 48.5] | 35.0 | 82.0 (Study 2) | 64.0 | — | 5.0 | 6.0 | — | not effective (Study 2's S1) |
| context-hashed, h = 1 | 0.50 | 70.5 [66.5, 74.5] | 4.0 [1.5, 6.0] | 8.0 | 74.0 [70.0, 77.5] | 99.0 / 100.0 / 90.5 / 79.0 | 6.0 | 24.5 | +32.0 [21.0, 44.0]; 7 of 8 | **material robustness cost** (paraphrase effective (>= 50%)) |
| context-hashed, h = 4 | 0.50 | 69.5 [64.5, 74.5] | 1.5 [0.0, 3.0] | 4.0 | 70.0 [65.5, 75.5] | 97.0 / 99.5 / 86.0 / 78.0 | 7.5 | 23.0 | +32.5 [19.0, 45.5]; 7 of 8 | **material robustness cost** (paraphrase effective (>= 50%)) |
| rotation (K = 8) (union test on Study 2's paraphrases) | 0.50 | 52.5 | 15.0 | — | as the fixed key | — | — | — | +13.0 [8.5, 17.5] | **immaterial** |

The owner's bars (pool A's human continuations, 95th percentile): perplexity 25.41, seq-rep-4 0.0484; meaning (cosine) 0.825; the attacker's self-check uses pool C's (22.17, 0.0480, 0.810). Stricter readings (descriptive): the model-text 95th percentile (perplexity 7.35) and the human median (12.94). Paraphrase attempts kept: h = 1: attempt 1 1012, 2 361, 3 227 of 1600; kept but still failing the attacker's check 333; h = 4: attempt 1 1055, 2 331, 3 214 of 1600; kept but still failing the attacker's check 396.

## Table 5 — Per key: the per-unit view behind every median (keys excluded by G2 shown as —)

| arm | ρ | reading | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | median |
|---|---|---|---|---|---|---|---|---|---|---|---|
| context-hashed, h = 1 | — | FPR on pool A, % (G2 ≤ 3) | 0.9 | 0.8 | 1.0 | 1.0 | 0.3 | 1.4 | 0.4 | 0.8 | 0.8 |
| context-hashed, h = 4 | — | FPR on pool A, % (G2 ≤ 3) | 1.5 | 0.5 | 0.9 | 0.7 | 1.1 | 1.1 | 1.2 | 0.6 | 1.0 |
| fixed key (h = 0) (S4, Study 3) | — | FPR on pool A, % | 0.7 | 0.1 | 0.8 | 0.6 | 1.7 | 1.0 | 1.3 | 0.3 | 0.8 |
| fixed key (h = 0) | 0.35 | S4 detection % | 100 | 95 | 95 | 98 | 96 | 88 | 98 | 96 | 96 |
| fixed key (h = 0) | 0.35 | genuine FA % | 92 | 86 | 86 | 89 | 87 | 83 | 89 | 86 | 86 |
| fixed key (h = 0) | 0.35 | cos known layer, n = 64 | 0.99 | 0.93 | 0.76 | 0.95 | 0.96 | 0.81 | 0.99 | 0.81 | 0.94 |
| fixed key (h = 0) | 0.35 | forgery FA %, n = 64 | 92 | 91 | 71 | 94 | 85 | 73 | 92 | 82 | 88 |
| fixed key (h = 0) | 0.35 | cos known layer, n = 256 | 0.98 | 0.93 | 0.87 | 0.96 | 0.97 | 0.92 | 0.99 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.35 | forgery FA %, n = 256 | 85 | 92 | 76 | 85 | 91 | 89 | 93 | 83 | 87 |
| fixed key (h = 0) | 0.35 | cos known layer, n = 1024 | 0.98 | 0.95 | 0.83 | 0.96 | 0.97 | 0.93 | 0.99 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.35 | forgery FA %, n = 1024 | 79 | 80 | 82 | 89 | 88 | 88 | 89 | 75 | 85 |
| fixed key (h = 0) | 0.35 | Study 2 scrub success % | 54 | 64 | 52 | 69 | 33 | 34 | 62 | 44 | 53 |
| context-hashed, h = 1 | 0.35 | detection % | 89 | 93 | 93 | 94 | 90 | 93 | 90 | 92 | 92 |
| context-hashed, h = 1 | 0.35 | genuine FA % | 79 | 84 | 84 | 85 | 83 | 85 | 81 | 84 | 84 |
| context-hashed, h = 1 | 0.35 | control FA % | 0 | 0 | 2 | 0 | 1 | 1 | 1 | 1 | 1 |
| context-hashed, h = 1 | 0.35 | forgery FA %, n = 64 | 2 | 0 | 0 | 1 | 2 | 0 | 1 | 3 | 1 |
| context-hashed, h = 1 | 0.35 | forgery FA %, n = 256 | 0 | 1 | 5 | 2 | 0 | 4 | 3 | 3 | 2 |
| context-hashed, h = 1 | 0.35 | forgery FA %, n = 1024 | 3 | 4 | 4 | 2 | 3 | 7 | 9 | 3 | 4 |
| context-hashed, h = 1 | 0.35 | attacker cos (weighted), n = 1,024 | 0.156 | 0.169 | 0.171 | 0.196 | 0.159 | 0.246 | 0.168 | 0.214 | 0.170 |
| context-hashed, h = 1 | 0.35 | coverage, n = 1,024 | 0.793 | 0.803 | 0.804 | 0.807 | 0.795 | 0.780 | 0.777 | 0.800 | 0.798 |
| context-hashed, h = 1 | 0.35 | scrub success % | 77 | 73 | 73 | 68 | 78 | 70 | 67 | 78 | 73 |
| context-hashed, h = 1 | 0.35 | d vs fixed, points | +23 | +9 | +21 | -1 | +45 | +36 | +5 | +34 | +22 |
| context-hashed, h = 1 | 0.35 | perplexity ratio (median) | 0.81 | 0.86 | 0.86 | 0.89 | 0.85 | 0.90 | 0.80 | 0.71 | 0.85 |
| context-hashed, h = 4 | 0.35 | detection % | 91 | 88 | 90 | 87 | 92 | 90 | 90 | 88 | 90 |
| context-hashed, h = 4 | 0.35 | genuine FA % | 83 | 78 | 80 | 78 | 85 | 81 | 80 | 79 | 80 |
| context-hashed, h = 4 | 0.35 | control FA % | 1 | 1 | 0 | 2 | 0 | 0 | 2 | 0 | 0 |
| context-hashed, h = 4 | 0.35 | forgery FA %, n = 64 | 2 | 1 | 1 | 0 | 2 | 1 | 1 | 4 | 1 |
| context-hashed, h = 4 | 0.35 | forgery FA %, n = 256 | 1 | 1 | 1 | 1 | 0 | 4 | 1 | 1 | 1 |
| context-hashed, h = 4 | 0.35 | forgery FA %, n = 1024 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| context-hashed, h = 4 | 0.35 | attacker cos (weighted), n = 1,024 | 0.012 | 0.011 | 0.005 | 0.004 | 0.053 | 0.013 | 0.007 | 0.041 | 0.012 |
| context-hashed, h = 4 | 0.35 | coverage, n = 1,024 | 0.010 | 0.013 | 0.009 | 0.012 | 0.010 | 0.014 | 0.016 | 0.013 | 0.013 |
| context-hashed, h = 4 | 0.35 | scrub success % | 73 | 75 | 69 | 71 | 67 | 78 | 70 | 73 | 72 |
| context-hashed, h = 4 | 0.35 | d vs fixed, points | +19 | +11 | +17 | +2 | +34 | +44 | +8 | +29 | +18 |
| context-hashed, h = 4 | 0.35 | perplexity ratio (median) | 0.81 | 0.84 | 0.86 | 0.90 | 0.83 | 0.90 | 0.81 | 0.67 | 0.83 |
| rotation (K = 8) | 0.35 | union-test detection % | 100 | 87 | 87 | 95 | 92 | 87 | 95 | 94 | 93 |
| rotation (K = 8) | 0.35 | union-test scrub success % | 72 | 73 | 68 | 77 | 47 | 50 | 81 | 57 | 70 |
| fixed key (h = 0) | 0.50 | S4 detection % | 100 | 95 | 99 | 98 | 100 | 99 | 100 | 97 | 99 |
| fixed key (h = 0) | 0.50 | genuine FA % | 90 | 89 | 91 | 91 | 90 | 89 | 90 | 87 | 90 |
| fixed key (h = 0) | 0.50 | cos known layer, n = 64 | 0.99 | 0.90 | 0.90 | 0.96 | 0.97 | 0.95 | 0.99 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.50 | forgery FA %, n = 64 | 84 | 92 | 85 | 83 | 89 | 83 | 88 | 86 | 86 |
| fixed key (h = 0) | 0.50 | cos known layer, n = 256 | 0.99 | 0.90 | 0.90 | 0.96 | 0.97 | 0.94 | 0.99 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.50 | forgery FA %, n = 256 | 84 | 94 | 78 | 82 | 83 | 84 | 88 | 91 | 84 |
| fixed key (h = 0) | 0.50 | cos known layer, n = 1024 | 0.99 | 0.90 | 0.90 | 0.96 | 0.97 | 0.94 | 0.98 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.50 | forgery FA %, n = 1024 | 86 | 89 | 78 | 83 | 93 | 80 | 89 | 91 | 88 |
| fixed key (h = 0) | 0.50 | Study 2 scrub success % | 37 | 64 | 42 | 44 | 25 | 13 | 45 | 35 | 40 |
| context-hashed, h = 1 | 0.50 | detection % | 97 | 93 | 94 | 96 | 97 | 97 | 95 | 99 | 96 |
| context-hashed, h = 1 | 0.50 | genuine FA % | 88 | 87 | 85 | 89 | 88 | 88 | 88 | 89 | 88 |
| context-hashed, h = 1 | 0.50 | control FA % | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 |
| context-hashed, h = 1 | 0.50 | forgery FA %, n = 64 | 0 | 1 | 1 | 2 | 1 | 3 | 2 | 3 | 2 |
| context-hashed, h = 1 | 0.50 | forgery FA %, n = 256 | 2 | 1 | 4 | 3 | 7 | 7 | 2 | 3 | 3 |
| context-hashed, h = 1 | 0.50 | forgery FA %, n = 1024 | 5 | 9 | 9 | 11 | 6 | 11 | 7 | 9 | 9 |
| context-hashed, h = 1 | 0.50 | attacker cos (weighted), n = 1,024 | 0.179 | 0.208 | 0.217 | 0.209 | 0.189 | 0.241 | 0.237 | 0.238 | 0.213 |
| context-hashed, h = 1 | 0.50 | coverage, n = 1,024 | 0.808 | 0.808 | 0.792 | 0.796 | 0.795 | 0.804 | 0.795 | 0.810 | 0.800 |
| context-hashed, h = 1 | 0.50 | scrub success % | 72 | 73 | 69 | 67 | 69 | 68 | 74 | 73 | 70 |
| context-hashed, h = 1 | 0.50 | d vs fixed, points | +35 | +9 | +27 | +23 | +44 | +55 | +29 | +38 | +32 |
| context-hashed, h = 1 | 0.50 | perplexity ratio (median) | 0.69 | 0.71 | 0.80 | 0.82 | 0.71 | 0.80 | 0.73 | 0.61 | 0.72 |
| context-hashed, h = 4 | 0.50 | detection % | 96 | 95 | 90 | 95 | 96 | 94 | 97 | 97 | 96 |
| context-hashed, h = 4 | 0.50 | genuine FA % | 89 | 87 | 83 | 87 | 89 | 86 | 88 | 89 | 88 |
| context-hashed, h = 4 | 0.50 | control FA % | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 0 | 0 |
| context-hashed, h = 4 | 0.50 | forgery FA %, n = 64 | 0 | 1 | 2 | 0 | 0 | 1 | 3 | 1 | 1 |
| context-hashed, h = 4 | 0.50 | forgery FA %, n = 256 | 0 | 0 | 1 | 3 | 1 | 0 | 0 | 2 | 0 |
| context-hashed, h = 4 | 0.50 | forgery FA %, n = 1024 | 1 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 1 |
| context-hashed, h = 4 | 0.50 | attacker cos (weighted), n = 1,024 | 0.000 | 0.007 | 0.091 | 0.003 | 0.054 | 0.012 | 0.011 | 0.067 | 0.012 |
| context-hashed, h = 4 | 0.50 | coverage, n = 1,024 | 0.007 | 0.009 | 0.009 | 0.008 | 0.007 | 0.007 | 0.007 | 0.008 | 0.008 |
| context-hashed, h = 4 | 0.50 | scrub success % | 69 | 66 | 64 | 67 | 70 | 73 | 78 | 71 | 70 |
| context-hashed, h = 4 | 0.50 | d vs fixed, points | +32 | +2 | +22 | +23 | +45 | +60 | +33 | +36 | +32 |
| context-hashed, h = 4 | 0.50 | perplexity ratio (median) | 0.71 | 0.72 | 0.72 | 0.80 | 0.71 | 0.81 | 0.76 | 0.61 | 0.72 |
| rotation (K = 8) | 0.50 | union-test detection % | 99 | 80 | 99 | 97 | 100 | 98 | 100 | 95 | 98 |
| rotation (K = 8) | 0.50 | union-test scrub success % | 46 | 75 | 59 | 62 | 34 | 28 | 63 | 44 | 52 |

## Table 6 — The per-context attacker's mechanics and the run's timing (descriptive)

| arm | ρ | distinct contexts in the observed set | eligible (≥ 16 occurrences) | n | contexts estimated | coverage | cos by context count: 16–31 / 32–127 / 128–511 / ≥ 512 |
|---|---|---|---|---|---|---|---|
| context-hashed, h = 1 | 0.35 | 19412 | 1942 | 64 | 148 | 0.487 | 0.011 / 0.011 / 0.048 / 0.000 |
| context-hashed, h = 1 | 0.35 | 19412 | 1942 | 256 | 527 | 0.639 | 0.005 / 0.020 / 0.065 / 0.164 |
| context-hashed, h = 1 | 0.35 | 19412 | 1942 | 1024 | 1942 | 0.798 | 0.009 / 0.022 / 0.100 / 0.240 |
| context-hashed, h = 1 | 0.50 | 18805 | 1880 | 64 | 154 | 0.503 | 0.014 / 0.041 / 0.069 / 0.345 |
| context-hashed, h = 1 | 0.50 | 18805 | 1880 | 256 | 525 | 0.653 | 0.015 / 0.041 / 0.140 / 0.229 |
| context-hashed, h = 1 | 0.50 | 18805 | 1880 | 1024 | 1878 | 0.800 | 0.013 / 0.039 / 0.139 / 0.298 |
| context-hashed, h = 4 | 0.35 | 240523 | 89 | 64 | 0 | 0.001 | 0.000 / — / — / — |
| context-hashed, h = 4 | 0.35 | 240523 | 89 | 256 | 9 | 0.004 | 0.000 / 0.000 / — / — |
| context-hashed, h = 4 | 0.35 | 240523 | 89 | 1024 | 89 | 0.013 | 0.000 / 0.013 / 0.000 / — |
| context-hashed, h = 4 | 0.50 | 242542 | 61 | 64 | 1 | 0.001 | 0.000 / 0.000 / — / — |
| context-hashed, h = 4 | 0.50 | 242542 | 61 | 256 | 7 | 0.002 | 0.000 / 0.000 / — / — |
| context-hashed, h = 4 | 0.50 | 242542 | 61 | 1024 | 61 | 0.008 | 0.004 / 0.016 / 0.000 / — |

Timing (from the run's per-step records): h = 1: generation over 16 key-levels: genuine 0.52 h, control 0.52 h, obs 4.96 h; paraphrase 1.47 h for 1600 originals (3.30 s each); h = 4: generation over 16 key-levels: genuine 0.52 h, control 0.52 h, obs 4.97 h; paraphrase 1.53 h for 1600 originals (3.43 s each). Phase durations are in the run manifest.

