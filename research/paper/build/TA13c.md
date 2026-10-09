**TA13c — The defence pilot on tuning keys 9001–9004 at ρ = 0.50 (medians over 4 keys; no rule applies; labelled pilot)**

| arm | detection at ρ = 0.50 (%) | at 0.35 (%) | perplexity ratio to the fixed key, 0.50 | 0.35 | forgery FA at n = 100 (%) | random-key control (%) | P-Qwen scrub success (%) | detected after paraphrase (%) | per-context attacker: cos (coverage; contexts) at n = 16 / 64 / 100 |
|---|---|---|---|---|---|---|---|---|---|
| h = 1 | 95.5 | 91.5 | 0.89 | 0.93 | 5.0 | 0.0 | 75.0 | 2.0 | 0.033 (0.30; 37.5) / 0.088 (0.50; 148) / 0.115 (0.54; 212.5) |
| h = 4 | 94.5 | 89.0 | 0.89 | 0.93 | 0.0 | 0.0 | 75.0 | 1.0 | 0.000 (0.00; 0) / 0.000 (0.00; 1) / 0.000 (0.00; 1.5) |

The pilot fixed the design before the lock; its I4 addendum measured the per-position form of the keyed test with h = 0 against S4 on the same tuning keys: 96.0% against 95.5% at ρ = 0.35 and 98.5% against 97.5% at 0.50 (within 10 points, as decision 6 required). The rotation code test with K = 4 tuning keys: union-test detection 95.0% (median), union false-positive rate 0.8%; the naive averaging attacker's best cosine with any key 0.55; the clustering attacker recovered 4 of 4 keys at n = 64.
