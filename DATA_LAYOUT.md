# Data layout

| Path | Tracked? | Contents |
|---|---|---|
| `research/stage4/data/raw/allenai__c4/…` | no (git-ignored) | Frozen C4 realnewslike validation shard (hashes in `research/stage4/outputs/prompt_sets_v0.3.json`) |
| `research/stage4/data/raw/Salesforce__wikitext/…` | no | Frozen WikiText-103 raw test, validation and train-00000 parquet files |
| `research/stage4/data/prompts_{c4,wikitext}_{dev,holdout}.jsonl` | no | Prompt units (id, prompt of 40 words, human continuation of 200 words). **Load only through `research/stage4/prompts.py`**, which seals the holdout |
| `research/stage4/outputs/*.json` | yes | Counts, hashes, holdout-ID lists, model manifests. No article text |
| `research/pilot/outputs/*.json` | yes | Feasibility pilot timing, Qwen2.5-1.5B manifest |
| `~/.cache/huggingface/hub/` | no (outside repo) | Model weights at pinned revisions (see the manifests) |

To rebuild everything from scratch: `.venv/bin/python research/stage4/build_prompt_sets_v0_3.py` (it downloads the pinned files and checks sizes and hashes against the Hub).
