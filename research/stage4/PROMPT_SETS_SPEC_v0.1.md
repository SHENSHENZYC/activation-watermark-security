# Prompt-set specification v0.1 (written 2026-09-25, before any corpus download)

## Sources (decided 2026-09-25)
- **Main domain:** `allenai/c4`, config `realnewslike`, file `realnewslike/c4-validation.00000-of-00001.json.gz` at commit `1588ec454efa1a09f29cd18ddd04fe05fc8653a2` (15,284,943 bytes per the Hub API). ODC-BY plus the Common Crawl terms.
- **Check domain:** `Salesforce/wikitext`, `wikitext-103-raw-v1/test` and `validation` parquet files at commit `b08601e04326c79dfdd32d625aee71d232d685c3`. CC BY-SA / GFDL.
- Train splits are **not** used (smaller exposure, and a smaller download). If the proceed rule fails, adding a C4 train shard is a new versioned decision.

## Units (tokenizer-neutral, so the same prompts serve Qwen and Llama)
- A **document** is one C4 record, or one WikiText article (split at level-1 ` = Title = ` headers).
- **Text normalisation:** collapse whitespace; for WikiText, undo the raw tokenisation artefacts (` @-@ ` → `-`, ` @,@ ` → `,`, ` @.@ ` → `.`) and drop section-header lines.
- **Prompt** = the first 40 whitespace words of the document. **Human continuation** = the next 200 words.
- **Usable** means at least 240 words after normalisation, after removing exact duplicates of the prompt (the first 40 words; only the first occurrence is kept).
- **ID** = SHA-256 of the C4 `url` (or of the WikiText title plus article index), in hex.

## Split (deterministic, fixed now)
- `bucket = int(ID[:8], 16) % 100`.
- **Holdout** if bucket < 20, otherwise **dev**.
- The holdout is for the final locked protocol only. Code that loads prompts must pass `split="dev"`, and **asserts** that no holdout ID is ever returned unless the caller passes a locked-protocol token (`allow_holdout=<PRE_RUN_LOCK sha>`).
- Within dev, the Stage 5 protocol will split further (attacker-collected texts vs evaluation texts), again by ID hash.

## Proceed rule (fixed before download)
**PASS** if all hold:
1. C4 dev has at least 6,000 usable documents, and C4 holdout at least 1,500.
2. WikiText (test plus validation, all buckets) has at least 300 usable articles. The WikiText check domain uses the same 80/20 split.
3. The downloaded bytes match the Hub-listed size, and the SHA-256 is recorded.
4. At most 1% of records fail to parse; failures are counted and excluded, never patched.

**If rule 1 fails:** stop and ask Yichen before adding a train shard.

## Outputs
- Git-ignored `research/stage4/data/raw/` (the downloaded files) and `research/stage4/data/prompts_{c4,wikitext}_{dev,holdout}.jsonl` (id, prompt, human continuation).
- Committed `research/stage4/outputs/prompt_sets_v0.1.json`: file hashes, counts at each filter step, length profiles, the holdout ID list and its SHA-256, and the proceed-rule result. No article text.
