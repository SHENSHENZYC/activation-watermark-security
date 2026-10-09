# Study 5 addendum — rotation: forging with every cluster at ρ = 0.35 (post hoc, labelled; spec v0.1)

Date: 2026-10-04. **Status: FIXED** (before the run; decision 10, Yichen: "claim gate, with a 30-min rotation addendum alongside"). **Not pre-registered**: Study 5's D1 verdict for rotation stands as written in `STUDY5_REPORT_v0.1.md`; this addendum is an exploratory reading reported beside it, labelled.

## Why
Study 5's clustering attacker recovered 6 of 8 rotating keys at ρ = 0.35 (n = 256 and 1,024; median best cosine 0.83–0.87), but the pre-registered forgery used the cluster with the largest z-profile, which picked a small outlier cluster with cosine 0.00 (key 1001), so the verdict read "stealing blocked at n ≤ 1024" where the recovery had succeeded. At ρ = 0.50 the same rule picked a cluster at cosine 0.96 and the forgeries were accepted 95–96%. The question: what does an attacker who forges with every cluster (or with a different pre-set pick) get at ρ = 0.35?

## What is run (locked machinery, unchanged; `rotation_addendum.py`)
1. **Integrity.** Re-run the locked clustering (`keyed_core.cosine_kmeans`, K = 8, seed 20261003 + n) on the saved layer-14 gradients of the rotating mixture (`F_*_obsgrads.npz`, as phase R) at ρ = 0.35 for n ∈ {256, 1024}, and the per-cluster Route A′ estimates; assert that every cluster's size, best key and best cosine equal the records in `R_r035_attack.json`, and that the study's chosen-cluster estimate equals the saved vector.
2. **Forgeries.** For each n and each of the 8 clusters: 100 forgeries on pool D's first 100 prompts with Study 1's fixed hook at layer 14, the cluster's estimate scaled to ρ · N̂ (the attacker's scale), seeds `S.seed(9, 0, 96, 8·ni + k)` (disjoint from every earlier seed). Scored with the union test (the owner's 8 keys; 999 null groups) and Study 5's fluency bars for rotation (the level's pooled oracle 95th percentiles).
3. **Readings (pre-set).** Per cluster: FA (accepted at p ≤ 0.01 and fluent), accepted, fluent, beside its size, best key and cosine. Three attackers: (a) the study's rule (largest z-profile; equals Study 5's result); (b) a "largest cluster" rule; (c) "every cluster", the maximum FA over clusters. Also the share of clusters with cosine ≥ 0.5 whose forgeries reach half the genuine FA (43.2%). No new verdict; no bootstrap (100 texts per set; binomial 95% intervals reported).
4. **Output.** `outputs/study5_v0.1/ADDENDUM_ROTATION.json` and `ADDENDUM_ROTATION.md` (inserted into the report's §6 by the builder, labelled post hoc). Data under `study5_addendum/data/` (git-ignored). About 35 minutes.

## Not claimed
A rule the attacker would use in practice is not pre-registered here; (c) is an upper bound over the eight candidates. The reading is bounded as Study 5 is (one model, n ≤ 1,024, ρ = 0.35 only here; ρ = 0.50 was already practical).
