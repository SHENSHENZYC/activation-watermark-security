**TA4d — Study 5: the clustering attacker on rotation among 8 keys (spherical k-means with K = 8 on the standardised summed gradients, then Route A′ per cluster)**

| ρ | n | clusters with ≥ 2 texts | keys recovered (best cos ≥ 0.5) | median best cos over clusters | largest best cos | forging cluster by the pre-registered rule (largest z-profile) | naive attacker: best cos with any key | forgery FA %, clustering [95% CI] | forgery FA %, naive [95% CI] |
|---|---|---|---|---|---|---|---|---|---|
| 0.35 | 64 | 8 | 4 | 0.560 | 0.888 | 6 (size 3; cos 0.308; z-profile 9.09) | 0.000 | 8.0 [3.0, 14.0] | 0.0 [0.0, 0.0] |
| 0.35 | 256 | 8 | 6 | 0.830 | 0.983 | 1 (size 17; cos 0.000; z-profile 8.21) | 0.000 | 2.0 [0.0, 5.0] | 1.0 [0.0, 3.0] |
| 0.35 | 1,024 | 8 | 6 | 0.866 | 0.964 | 7 (size 92; cos 0.000; z-profile 9.75) | 0.000 | 0.0 [0.0, 0.0] | 1.0 [0.0, 3.0] |
| 0.5 | 64 | 8 | 7 | 0.862 | 0.954 | 3 (size 8; cos 0.954; z-profile 6.38) | 0.000 | 95.0 [90.0, 99.0] | 0.0 [0.0, 0.0] |
| 0.5 | 256 | 8 | 8 | 0.952 | 0.990 | 0 (size 32; cos 0.959; z-profile 6.50) | 0.355 | 95.0 [90.0, 99.0] | 12.0 [6.0, 18.0] |
| 0.5 | 1,024 | 8 | 8 | 0.950 | 0.991 | 7 (size 128; cos 0.957; z-profile 6.56) | 0.000 | 96.0 [92.0, 99.0] | 0.0 [0.0, 0.0] |

The pre-registered forgery used the cluster with the largest standardised mean-gradient profile; at ρ = 0.35 that rule picked a small cluster whose estimate has cosine near 0 with every key, which is why the forgery acceptance is low although most keys were recovered (the labelled post-hoc addendum, Appendix G, forges with every cluster).
