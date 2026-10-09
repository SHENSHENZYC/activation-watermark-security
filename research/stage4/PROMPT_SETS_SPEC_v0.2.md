# Prompt-set specification v0.2 (2026-09-25; supersedes v0.1 for WikiText only)

**Why:** under v0.1 the WikiText rule failed (122 articles in test plus validation, against ≥ 300; see DECISION_LOG 2026-09-25). v0.1 and its output are kept unchanged.

**Change (Yichen's decision):** the WikiText source adds `wikitext-103-raw-v1/train-00000-of-00002.parquet` (156,987,808 bytes per the Hub listing; *corrected 2026-09-25: an earlier draft of this line quoted 157,088,770, the size of train file 2; the build script checks against the Hub listing, so the data are unaffected*; same repo `Salesforce/wikitext`, same commit `b08601e04326c79dfdd32d625aee71d232d685c3`, same licence). Everything else in v0.1 is unchanged: units, normalisation, ID rule (IDs include the file name, so there are no clashes), the 80/20 split and holdout sealing, and the proceed-rule thresholds (including WikiText ≥ 300 usable).

**Integrity checks (new):**
1. The C4 outputs must reproduce v0.1 **exactly** (same counts, same holdout-ID SHA-256 `7b382b52…8262`).
2. The WikiText articles from test and validation must be a subset of the v0.2 WikiText set, with the same IDs.

Output: `outputs/prompt_sets_v0.2.json`; data files in `data/` are overwritten for WikiText only (C4 is regenerated identically).
