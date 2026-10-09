**TA9 — Study 5: the per-key view behind every median (keys 1001–1008; every key calibrated under every test)**

| arm | ρ | reading | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | median |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed key (h = 0; S4, Study 3) | — | FPR on pool A, % (G2 ≤ 3) | 0.7 | 0.1 | 0.8 | 0.6 | 1.7 | 1.0 | 1.3 | 0.3 | 0.8 |
| context-hashed, h = 1 | — | FPR on pool A, % (G2 ≤ 3) | 0.9 | 0.8 | 1.0 | 1.0 | 0.3 | 1.4 | 0.4 | 0.8 | 0.8 |
| context-hashed, h = 4 | — | FPR on pool A, % (G2 ≤ 3) | 1.5 | 0.5 | 0.9 | 0.7 | 1.1 | 1.1 | 1.2 | 0.6 | 1.0 |
| fixed key (h = 0) | 0.35 | S4 detection, % | 100 | 95 | 95 | 98 | 96 | 88 | 98 | 96 | 96 |
| fixed key (h = 0) | 0.35 | genuine FA, % | 92 | 86 | 86 | 89 | 87 | 83 | 89 | 86 | 86 |
| fixed key (h = 0) | 0.35 | Route A′ cos(v̂, v), known layer, n = 64 | 0.99 | 0.93 | 0.76 | 0.95 | 0.96 | 0.81 | 0.99 | 0.81 | 0.94 |
| fixed key (h = 0) | 0.35 | Route A′ forgery FA, %, n = 64 | 92 | 91 | 71 | 94 | 85 | 73 | 92 | 82 | 88 |
| fixed key (h = 0) | 0.35 | Route A′ cos(v̂, v), known layer, n = 1,024 | 0.98 | 0.95 | 0.83 | 0.96 | 0.97 | 0.93 | 0.99 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.35 | Route A′ forgery FA, %, n = 1,024 | 79 | 80 | 82 | 89 | 88 | 88 | 89 | 75 | 85 |
| fixed key (h = 0) | 0.35 | Study 2 scrub success (P-Qwen), % | 54 | 64 | 52 | 69 | 33 | 34 | 62 | 44 | 53 |
| context-hashed, h = 1 | 0.35 | keyed-test detection, % | 89 | 93 | 93 | 94 | 90 | 93 | 90 | 92 | 92 |
| context-hashed, h = 1 | 0.35 | genuine FA, % | 79 | 84 | 84 | 85 | 83 | 85 | 81 | 84 | 84 |
| context-hashed, h = 1 | 0.35 | control (random-key) FA, % | 0 | 0 | 2 | 0 | 1 | 1 | 1 | 1 | 1 |
| context-hashed, h = 1 | 0.35 | per-context forgery FA, %, n = 1,024 | 3 | 4 | 4 | 2 | 3 | 7 | 9 | 3 | 4 |
| context-hashed, h = 1 | 0.35 | attacker's count-weighted cos, n = 1,024 | 0.156 | 0.169 | 0.171 | 0.196 | 0.159 | 0.246 | 0.168 | 0.214 | 0.170 |
| context-hashed, h = 1 | 0.35 | coverage of a genuine text's positions, n = 1,024 | 0.793 | 0.803 | 0.804 | 0.807 | 0.795 | 0.780 | 0.777 | 0.800 | 0.798 |
| context-hashed, h = 1 | 0.35 | scrub success (P-Qwen), % | 77 | 73 | 73 | 68 | 78 | 70 | 67 | 78 | 73 |
| context-hashed, h = 1 | 0.35 | d = success − the fixed key's, points | +23 | +9 | +21 | -1 | +45 | +36 | +5 | +34 | +22 |
| context-hashed, h = 1 | 0.35 | perplexity ratio to the fixed key (median) | 0.81 | 0.86 | 0.86 | 0.89 | 0.85 | 0.90 | 0.80 | 0.71 | 0.85 |
| context-hashed, h = 4 | 0.35 | keyed-test detection, % | 91 | 88 | 90 | 87 | 92 | 90 | 90 | 88 | 90 |
| context-hashed, h = 4 | 0.35 | genuine FA, % | 83 | 78 | 80 | 78 | 85 | 81 | 80 | 79 | 80 |
| context-hashed, h = 4 | 0.35 | control (random-key) FA, % | 1 | 1 | 0 | 2 | 0 | 0 | 2 | 0 | 0 |
| context-hashed, h = 4 | 0.35 | per-context forgery FA, %, n = 1,024 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| context-hashed, h = 4 | 0.35 | attacker's count-weighted cos, n = 1,024 | 0.012 | 0.011 | 0.005 | 0.004 | 0.053 | 0.013 | 0.007 | 0.041 | 0.012 |
| context-hashed, h = 4 | 0.35 | coverage of a genuine text's positions, n = 1,024 | 0.010 | 0.013 | 0.009 | 0.012 | 0.010 | 0.014 | 0.016 | 0.013 | 0.013 |
| context-hashed, h = 4 | 0.35 | scrub success (P-Qwen), % | 73 | 75 | 69 | 71 | 67 | 78 | 70 | 73 | 72 |
| context-hashed, h = 4 | 0.35 | d = success − the fixed key's, points | +19 | +11 | +17 | +2 | +34 | +44 | +8 | +29 | +18 |
| context-hashed, h = 4 | 0.35 | perplexity ratio to the fixed key (median) | 0.81 | 0.84 | 0.86 | 0.90 | 0.83 | 0.90 | 0.81 | 0.67 | 0.83 |
| rotation (K = 8) | 0.35 | union-test detection, % | 100 | 87 | 87 | 95 | 92 | 87 | 95 | 94 | 93 |
| rotation (K = 8) | 0.35 | single-key detection of the same texts, % | 100 | 95 | 95 | 98 | 96 | 88 | 98 | 96 | 96 |
| rotation (K = 8) | 0.35 | union-test scrub success on Study 2's paraphrases, % | 72 | 73 | 68 | 77 | 47 | 50 | 81 | 57 | 70 |
| rotation (K = 8) | 0.35 | d = union-test success − the fixed key's, points | +18 | +9 | +16 | +8 | +14 | +16 | +19 | +13 | +15 |
| fixed key (h = 0) | 0.50 | S4 detection, % | 100 | 95 | 99 | 98 | 100 | 99 | 100 | 97 | 99 |
| fixed key (h = 0) | 0.50 | genuine FA, % | 90 | 89 | 91 | 91 | 90 | 89 | 90 | 87 | 90 |
| fixed key (h = 0) | 0.50 | Route A′ cos(v̂, v), known layer, n = 64 | 0.99 | 0.90 | 0.90 | 0.96 | 0.97 | 0.95 | 0.99 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.50 | Route A′ forgery FA, %, n = 64 | 84 | 92 | 85 | 83 | 89 | 83 | 88 | 86 | 86 |
| fixed key (h = 0) | 0.50 | Route A′ cos(v̂, v), known layer, n = 1,024 | 0.99 | 0.90 | 0.90 | 0.96 | 0.97 | 0.94 | 0.98 | 0.81 | 0.95 |
| fixed key (h = 0) | 0.50 | Route A′ forgery FA, %, n = 1,024 | 86 | 89 | 78 | 83 | 93 | 80 | 89 | 91 | 88 |
| fixed key (h = 0) | 0.50 | Study 2 scrub success (P-Qwen), % | 37 | 64 | 42 | 44 | 25 | 13 | 45 | 35 | 40 |
| context-hashed, h = 1 | 0.50 | keyed-test detection, % | 97 | 93 | 94 | 96 | 97 | 97 | 95 | 99 | 96 |
| context-hashed, h = 1 | 0.50 | genuine FA, % | 88 | 87 | 85 | 89 | 88 | 88 | 88 | 89 | 88 |
| context-hashed, h = 1 | 0.50 | control (random-key) FA, % | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 |
| context-hashed, h = 1 | 0.50 | per-context forgery FA, %, n = 1,024 | 5 | 9 | 9 | 11 | 6 | 11 | 7 | 9 | 9 |
| context-hashed, h = 1 | 0.50 | attacker's count-weighted cos, n = 1,024 | 0.179 | 0.208 | 0.217 | 0.209 | 0.189 | 0.241 | 0.237 | 0.238 | 0.213 |
| context-hashed, h = 1 | 0.50 | coverage of a genuine text's positions, n = 1,024 | 0.808 | 0.808 | 0.792 | 0.796 | 0.795 | 0.804 | 0.795 | 0.810 | 0.800 |
| context-hashed, h = 1 | 0.50 | scrub success (P-Qwen), % | 72 | 73 | 69 | 67 | 69 | 68 | 74 | 73 | 70 |
| context-hashed, h = 1 | 0.50 | d = success − the fixed key's, points | +35 | +9 | +27 | +23 | +44 | +55 | +29 | +38 | +32 |
| context-hashed, h = 1 | 0.50 | perplexity ratio to the fixed key (median) | 0.69 | 0.71 | 0.80 | 0.82 | 0.71 | 0.80 | 0.73 | 0.61 | 0.72 |
| context-hashed, h = 4 | 0.50 | keyed-test detection, % | 96 | 95 | 90 | 95 | 96 | 94 | 97 | 97 | 96 |
| context-hashed, h = 4 | 0.50 | genuine FA, % | 89 | 87 | 83 | 87 | 89 | 86 | 88 | 89 | 88 |
| context-hashed, h = 4 | 0.50 | control (random-key) FA, % | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 0 | 0 |
| context-hashed, h = 4 | 0.50 | per-context forgery FA, %, n = 1,024 | 1 | 3 | 2 | 2 | 0 | 0 | 1 | 0 | 1 |
| context-hashed, h = 4 | 0.50 | attacker's count-weighted cos, n = 1,024 | 0.000 | 0.007 | 0.091 | 0.003 | 0.054 | 0.012 | 0.011 | 0.067 | 0.012 |
| context-hashed, h = 4 | 0.50 | coverage of a genuine text's positions, n = 1,024 | 0.007 | 0.009 | 0.009 | 0.008 | 0.007 | 0.007 | 0.007 | 0.008 | 0.008 |
| context-hashed, h = 4 | 0.50 | scrub success (P-Qwen), % | 69 | 66 | 64 | 67 | 70 | 73 | 78 | 71 | 70 |
| context-hashed, h = 4 | 0.50 | d = success − the fixed key's, points | +32 | +2 | +22 | +23 | +45 | +60 | +33 | +36 | +32 |
| context-hashed, h = 4 | 0.50 | perplexity ratio to the fixed key (median) | 0.71 | 0.72 | 0.72 | 0.80 | 0.71 | 0.81 | 0.76 | 0.61 | 0.72 |
| rotation (K = 8) | 0.50 | union-test detection, % | 99 | 80 | 99 | 97 | 100 | 98 | 100 | 95 | 98 |
| rotation (K = 8) | 0.50 | single-key detection of the same texts, % | 100 | 95 | 99 | 98 | 100 | 99 | 100 | 97 | 99 |
| rotation (K = 8) | 0.50 | union-test scrub success on Study 2's paraphrases, % | 46 | 75 | 59 | 62 | 34 | 28 | 63 | 44 | 52 |
| rotation (K = 8) | 0.50 | d = union-test success − the fixed key's, points | +9 | +11 | +17 | +18 | +9 | +15 | +18 | +9 | +13 |

The fixed key's detection and FA are Study 5's re-scoring of Study 1's texts with S4; its Study 2 scrub success is Study 2's locked value for the same key and strength (asserted equal). d is the keyed arm's scrub success minus the fixed key's, per key; D2 takes its median with a cluster-bootstrap interval. Rotation's texts are the fixed key's, so its quality is unchanged by construction and its paraphrases are Study 2's, scored by the union test.
