# A Security Analysis of an Activation-Steering LLM Watermark: Key Recovery, Forgery, Scrubbing and Keyed Defences

Public snapshot of the research repository behind the paper (Yichen Zhao, independent researcher, 2026). It holds every
pre-registered protocol, lock file, validation report, run manifest and result file, every script that generated a
number, table or figure in the paper, the paper's sources, and the decision log that records each decision in order.
It holds **no model weights, no generated corpora and no article text**: those were git-ignored throughout, and the
hashes in the manifests let you check a rebuild.

**Paper page:** https://shenshenzyc.github.io/activation-watermark-security/ (the PDF, an HTML version and this repository; served from `docs/`).

## What is where
| Path | Contents |
|---|---|
| `research/STUDY*_PROTOCOL_v*.md` | The pre-registered protocols (locked before any outcome; hashes in the lock files) |
| `research/outputs/<study>/` | `PRE_RUN_LOCK.json` (hashes of the protocol, the code and the reused inputs, the commit, the "no outcomes" statement), `INPUT_VALIDATION.json`, `RUN_MANIFEST*.json`, `results.json` |
| `research/study*/`, `research/study*_pilot/` | The locked runners and the pilots' code (the runners re-hash their inputs and refuse to run on a mismatch) |
| `research/STUDY*_REPORT_v*.md`, `research/study*_report/` | The reports and the scripts that generated them from `results.json` |
| `research/repro/`, `research/pilot/` | The reproduction pilot and the calibrations |
| `research/stage4/` | The prompt-set specifications, the builder (`build_prompt_sets_v0_3.py`), the sealed loader (`prompts.py`) and the manifests (counts, hashes, holdout identifiers; no text) |
| `research/paper/` | The paper: `sections/` (one file per section, numbers as `[[placeholders]]`), `tables/` and `figures/` (one script each, reading the locked outputs and asserting against them), `fill_sections.py`, `assemble.py`, `make_latex.py`, `latex/` (the arXiv sources), `references.bib`, `build/` (generated) |
| `research/literature/` | The terms-of-use check, the paced download scripts and the hashed manifest of the papers read (the PDFs themselves are not redistributed) |
| `research/*_GATE_v*.md`, `research/TOPIC_SCREEN_v0.1.md`, `research/PROJECT_BRIEF.md` | The source gates, the claim gate, the final gate and the brief |
| `research/DECISION_LOG.md` | Every decision, result and correction, dated, in order |
| `DATA_LAYOUT.md` | The data folders (git-ignored) and how to rebuild them |
| `docs/` | The GitHub Pages site (built by `tools/make_site.py`: `index.html`, `paper.pdf`, `paper.html` with `figures/`) |

## Rebuilding
1. Python 3.12 with PyTorch (MPS or CUDA) and `transformers`; the pinned model revisions are in `research/stage4/outputs/model_manifest_*.json` and `research/pilot/outputs/` (Llama 3.2 is gated on Hugging Face; accept its licence there).
2. Prompt sets: `python research/stage4/build_prompt_sets_v0_3.py` downloads the pinned C4 realnewslike and WikiText-103 files and checks their sizes and hashes; load prompts only through `research/stage4/prompts.py` (the holdout stays sealed: no lock in the paper is final).
3. A study: run its runner from `research/study*/`; it verifies every hash in its `PRE_RUN_LOCK.json` first. Run times on one Apple M5 laptop are in the run manifests (6.3 to 26.6 hours).
4. The paper: every script under `research/paper/tables/` and `research/paper/figures/`, then `research/paper/fill_sections.py`, `research/paper/assemble.py --render` and `research/paper/make_latex.py` (needs pandoc and a TeX engine).

## Licences
Code (every `.py` file and the scripts) is under the MIT licence (`LICENSE`). The text of the protocols, reports, gates,
the decision log and the paper, and the figures, are under CC BY 4.0 (`LICENSE-TEXT`). Third-party materials are not
included: the models are used under their own licences (Qwen2.5 Apache-2.0, Phi-3.5 MIT, Llama 3.2 Community Licence,
all-mpnet-base-v2 Apache-2.0), the prompts come from C4 (ODC-BY 1.0, Common Crawl terms) and WikiText-103 (CC BY-SA 3.0),
and the papers read are listed with their licences in `research/FINAL_GATE_v0.1.md`.

## Use of AI tools
The text and code were drafted by Claude (Anthropic) under the author's direction and under the pre-registered protocols;
the author designed the studies, took every decision in `research/DECISION_LOG.md`, revised every section, verified every
number against the locked outputs and takes full responsibility. No AI system is an author.

## Citing
See `CITATION.cff`. The arXiv identifier is added at posting.

## About this snapshot
Built by `tools/make_public_snapshot.py` from the working repository at the commit named in `SNAPSHOT_MANIFEST.json`
(every file's SHA-256 is listed there). One absolute local path in a design-time script was generalised to
`<repository>`; nothing else was edited.
