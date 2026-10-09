**TA7b — Study 3: per-key false-positive rates at p ≤ 0.01 (%) on 1,000 unwatermarked model texts and 1,000 human continuations per key**

| statistic | null texts | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | pooled | keys above 3% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S4 (primary) | unwatermarked model text (pool A), G2 | 0.7 | 0.1 | 0.8 | 0.6 | 1.7 | 1.0 | 1.3 | 0.3 | 0.81 | 0 |
| S4 (primary) | human continuations (pool A), H1 | 0.9 | 0.0 | 0.8 | 1.6 | 0.2 | 0.4 | 1.1 | 0.4 | 0.68 | 0 |
| S3 (secondary) | unwatermarked model text (pool A), G2 | 0.5 | 3.4 | 0.3 | 0.1 | 1.4 | 0.4 | 0.4 | 0.3 | 0.85 | 1 |
| S3 (secondary) | human continuations (pool A), H1 | 1.0 | 1.1 | 1.0 | 0.5 | 0.4 | 0.3 | 0.5 | 0.4 | 0.65 | 0 |

G2 excludes a key whose rate on model text exceeds 3%; S3 (the unstandardised gradient) loses key 1002 by that rule, S4 keeps all eight.
