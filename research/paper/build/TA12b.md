**TA12b — Study 2: false-positive rates at p ≤ 0.01 (%) on 1,000 paraphrased unwatermarked texts per key, before any verdict**

| paraphraser | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | pooled (G1) | keys above 3% (G2) | 1,000 fresh keys: mean FPR | fresh keys above 3% (max) | the probe's FPR on the same texts (median) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P-Qwen | 0.2 | 0.0 | 0.2 | 0.0 | 0.6 | 0.5 | 0.6 | 0.5 | 0.33 | 0 | 1.02 | 7.8% (max 22.6) | 3.3 |
| P-Phi | 0.4 | 0.0 | 0.0 | 0.5 | 0.2 | 1.4 | 0.3 | 0.7 | 0.44 | 0 | 0.94 | 6.5% (max 19.5) | 3.0 |

Fresh keys are 1,000 public-distribution keys never used by the owner, each tested on the same paraphrased texts; the share above 3% estimates how often a newly drawn key would fail the per-key gate after paraphrase (C9). The probe column is the owner's trained probe at its own 1% threshold on the same texts.
