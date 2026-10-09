# Prompt corpora and models — data audit v0.3

Date: 2026-09-25. **Verdict: PASS for C4, WikiText, Qwen2.5-1.5B and both paraphrasers. PARTIAL overall:** Llama-3.2-1B is pending Yichen's licence acceptance.
Proceed rule (fixed before download, [`PROMPT_SETS_SPEC_v0.1.md`](PROMPT_SETS_SPEC_v0.1.md)): C4 dev ≥ 6,000 and holdout ≥ 1,500; WikiText usable ≥ 300; sizes match the Hub; parse failures ≤ 1%.

## Terms of use (checked before any download)
See [`TERMS_OF_USE_CHECK.md`](TERMS_OF_USE_CHECK.md). In short: C4 is ODC-BY plus the Common Crawl terms (research use is fine; no personal-data harvesting; respect third-party rights). WikiText is CC BY-SA / GFDL. Qwen2.5 models are Apache-2.0; Phi-3.5-mini is MIT; Llama-3.2-1B is under the Llama 3.2 Community Licence (gated). Article text is never committed, only IDs and hashes.

## Access census
| Source | What exists | Format | Access |
|---|---|---|---|
| C4 realnewslike | validation: 1 shard, 13,863 records; train: 512 shards (unused) | json.gz | open (HF Hub) |
| WikiText-103 raw | test and validation (122 articles in total); train: 2 files | parquet | open (HF Hub) |
| Qwen2.5-1.5B, Qwen2.5-1.5B-Instruct, Phi-3.5-mini-instruct | pinned revisions | safetensors | open |
| Llama-3.2-1B | revision `4e20de36` | safetensors | **gated (manual acceptance)** |

## Freeze
Prompt-set manifests: [`outputs/prompt_sets_v0.1.json`](outputs/prompt_sets_v0.1.json), [`v0.2`](outputs/prompt_sets_v0.2.json), [`v0.3`](outputs/prompt_sets_v0.3.json) (current). Each has the repo, commit, file, bytes, Hub bytes and SHA-256 of every file. All sizes match the Hub. Model manifests: [`../pilot/outputs/model_manifest_qwen2.5-1.5b.json`](../pilot/outputs/model_manifest_qwen2.5-1.5b.json), [`outputs/model_manifest_qwen2.5-1.5b-instruct.json`](outputs/model_manifest_qwen2.5-1.5b-instruct.json), [`outputs/model_manifest_phi-3.5-mini-instruct.json`](outputs/model_manifest_phi-3.5-mini-instruct.json). Raw files live in git-ignored `data/raw/`.

## Parse and reconcile
- C4: 13,863 records, **0 parse failures**; the `text` and `url` fields are asserted.
- WikiText: articles are split at level-1 headers; sub-header lines are dropped.
- Exclusions are counted, not patched. C4: 5,283 shorter than 240 words; 0 duplicate prompts. WikiText v0.3: 398 too short; 64 duplicate prompts.
- Version history, all logged:
  - v0.1: the WikiText rule **failed** (122 articles against ≥ 300; my threshold error);
  - v0.2: added WikiText train file 1 (Yichen's decision), with C4 reproduced exactly;
  - v0.3: detokenised WikiText (an input-quality fix found by inspection, before any generation), with C4 reproduced exactly.

## Profile (v0.3)
| Set | Usable | Dev | Holdout | Words per document, median (10%–90%) |
|---|---|---|---|---|
| C4 realnewslike | 8,580 | 6,896 | 1,684 | 483 (279–1,017) |
| WikiText-103 | 14,560 | 11,720 | 2,840 | see the JSON |

Holdout: 20% by ID hash, **sealed in code** (`prompts.load_prompts` raises `PermissionError` without a final lock; tested ✓). Holdout-ID SHA-256 for C4: `7b382b52…8262`, identical across v0.1–v0.3.

## Feasibility (timing only; no outcomes)
- Generator pilot: 3.6 h per 5,000 steered texts (Stage 3 pilot).
- Phi-3.5-mini paraphrase: 7.6 GB on MPS, loads in 7 s, about 11.5 tokens/s unbatched (about 26 s per 200-word passage). **Note for Stage 5:** set the output cap to about 400 tokens (a 300-token cap cut one test output short: 172 words out for 200 in).

## Definitions found in notes
- The C4 card binds users to the Common Crawl terms "in respect of the content", not just ODC-BY.
- WikiText's raw variant keeps tokeniser spacing and `@-@` markers, hence v0.3.
- The WikiText card lists CC BY-SA 3.0 in its metadata but 4.0 in its text; both are share-alike, and we don't redistribute text.

## Limitations and not done
- **Contamination:** Qwen2.5 and Llama were probably trained on web text overlapping C4 and on Wikipedia. This affects watermarked and unwatermarked generations equally, but may make continuations closer to the originals; note it in the paper.
- Llama-3.2-1B has not been downloaded (it needs Yichen's licence acceptance).
- The SLAM-style target (Gemma-2-2B plus Gemma Scope, gated) is deferred to the Stage 5 design decision.
- The quality-judge model (for perplexity) is not yet chosen: Stage 5.
