# Terms-of-use check — Stage 4 (2026-09-25)

Sources: Hugging Face API `cardData.license` and `gated` fields, and the dataset or model cards at the pinned commits below, read 2026-09-25. Common Crawl terms read at https://commoncrawl.org/terms-of-use (summarised by a fetch tool; re-read before publication). Access to all items is through the Hugging Face Hub, which is the providers' intended distribution channel (no scraping).

## Prompt and human-text corpora (candidates)
| Source (pinned commit) | Licence / terms | Fit | Verdict |
|---|---|---|---|
| **allenai/c4, `realnewslike`** (`1588ec45`) | **ODC-BY 1.0**; card: "By using this, you are also bound by the Common Crawl terms of use in respect of the content contained in the dataset." Common Crawl permits research use; forbids illegal use, IP violation and harvesting of personal data; the user indemnifies CC for AI/ML use. Validation split: one shard, 15.3 MB. | **The standard prompt source in the LLM-watermark literature** (KGW and many successors use C4 realnewslike continuations). The rest of each article supplies matched **human-written text** for spoofing and false-positive tests. | **Usable.** Attribute ODC-BY; don't redistribute article text in the repo (store IDs and hashes only); no personal-data use. |
| Salesforce/wikitext-103 (`b08601e0`) | CC BY-SA (the card lists 3.0 and 4.0 inconsistently) and GFDL | Encyclopedic, pre-2016; used by the predecessor project | Usable (share-alike applies only if we redistribute text, which we won't). A second-domain candidate. |
| csebuetnlp/xlsum (`30fece42`) | CC BY-NC-SA 4.0 | Used by Self-Recognition (short summaries) | Usable for non-commercial research; short outputs (about 25 tokens) suit a low-entropy check only. |
| sentence-transformers/eli5 | **no licence on the card**; Reddit-derived | Used by Self-Recognition | **Avoid** (unclear rights). |
| Self-Recognition "Fresh News" (a Guardian scrape) | Guardian terms; not redistributed | — | **Not usable.** |
| abisee/cnn_dailymail | Apache-2.0 on the card (the underlying articles are news copyright) | News domain | Possible alternative. |

## Models (candidates)
| Model (pinned commit) | Licence | Gated | Weights | Role |
|---|---|---|---|---|
| Qwen/Qwen2.5-1.5B (`8faed761`) | Apache-2.0 | no | 3.09 GB | **Primary generator (downloaded; hashes in `pilot/outputs/model_manifest_qwen2.5-1.5b.json`)** |
| meta-llama/Llama-3.2-1B (`4e20de36`) | Llama 3.2 Community Licence | **manual** (Yichen must accept on HF and log in himself) | 2.47 GB | Second generator: the exact model in Self-Recognition |
| HuggingFaceTB/SmolLM2-1.7B (`effd688a`) | Apache-2.0 | no | 3.42 GB | Second-generator alternative |
| allenai/OLMo-2-0425-1B (`a1847dff`) | Apache-2.0 | no | 5.94 GB (repo total) | Second-generator alternative (fully open training data) |
| Qwen/Qwen2.5-0.5B (`060db649`) | Apache-2.0 | no | 0.99 GB | Scale ablation |
| microsoft/Phi-3.5-mini-instruct (`2fe19245`) | MIT | no | 7.64 GB | Paraphraser (different family) |
| Qwen/Qwen2.5-1.5B-Instruct (`989aa798`) | Apache-2.0 | no | 3.09 GB | Light paraphraser |
| humarin/chatgpt_paraphraser_on_T5_base (`d3ab1136`) | OpenRAIL | no | 1.78 GB | Sentence-level paraphraser (weaker) |
| kalpeshk2011/dipper-paraphraser-xxl (`c1fbf7a9`) | Apache-2.0 | no | 90 GB repo (11B) | **Infeasible** on 16 GB (the paraphraser used by Self-Recognition) |
| mistralai/Mistral-7B-Instruct-v0.3 (`c170c708`) | Apache-2.0 | no | 14.5 GB | Too large for bf16 on 16 GB alongside the generator |
| Qwen/Qwen2.5-3B(-Instruct) | "other" (Qwen research licence) | no | 6.17 GB | Avoid (licence) |
| google/gemma-2-2b (`c5ebcd40`) + google/gemma-scope-2b-pt-res (CC-BY-4.0) | Gemma terms | **manual** | about 5 GB of model | Only needed for a *faithful* SLAM reproduction (a Stage 5 decision) |

## Rules adopted
- Raw corpus files stay git-ignored under `research/data/`; the repo holds only IDs, SHA-256 hashes, counts and code.
- Model licences are recorded per model; gated models are accepted by Yichen himself (Claude never handles tokens).
- Attribution for ODC-BY and Apache/MIT goes in the paper's data and code statement.
