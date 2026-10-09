# Project brief — activation-watermark-stealing (formerly codename rp-2026-09-24)

Date: 2026-09-24. **Stage:** 1. Status: **agreed** (2026-09-24).

## Aim
A novel, useful publication on **representation-level (hidden-state) watermarking and provenance for LLM-generated text**. It should not be a replication or a benchmark. A careful negative or feasibility result counts, if it changes what practitioners or method designers would do. Rank every later choice by its credible path to a genuinely new contribution.
Scope: stay in this area, but re-derive the question in the Stage 2 screen. The predecessor's question (`PREDECESSOR_REVIEW.md`) is one candidate, not the default (decision 2026-09-24).

## Author facts
- Author: Yichen Zhao, independent researcher (no institutional affiliation).
- Consequences: **arXiv endorsement is needed.** Since the arXiv update of 2026-01-21, an institutional email alone no longer qualifies anyone. A new submitter needs a personal endorsement from an established author in the category (for example cs.CR or cs.CL/cs.LG). Plan to ask one author in the field, with the finished PDF.
- arXiv CS no longer accepts review or position papers without prior peer-review acceptance (2025-10-31). This paper must be a research paper.

## Venue(s) and their rules (checked 2026-09-24)
| Venue | AI-use policy (primary source) | Format | Other constraints |
|---|---|---|---|
| arXiv (cs.CR or cs.CL, cross-list cs.LG) | Disclose significant use of text-to-text generative AI; the authors take full responsibility; AI cannot be an author. [arXiv moderation](https://info.arxiv.org/help/moderation/index.html) | LaTeX/PDF | Endorsement (above); research papers only |
| NeurIPS workshop | Any tool is allowed; the authors are responsible for all content; LLM use that is part of the method goes in the setup. [NeurIPS 2025 LLM policy](https://neurips.cc/Conferences/2025/LLM), which the 2026 handbook follows (via search, **to re-confirm** for the chosen workshop) | NeurIPS LaTeX | Workshops set their own CfP; many are non-archival |
| ICLR workshop | **Any** LLM use must be disclosed; significant roles in ideation or writing go in an "LLM usage" section; undisclosed use means desk rejection. [ICLR LLM policy](https://iclr.cc/FAQ/LLM) | ICLR LaTeX | Same |
| ACL/EMNLP workshop | Grammar help needs no disclosure; literature search and text about existing ideas need disclosure; **using AI to generate novel research content is prohibited**. [ACL publication ethics](https://www.aclweb.org/adminwiki/index.php/ACL_Policy_on_Publication_Ethics) | ACL LaTeX | Strictest of the four |

**Who writes the prose:** Claude drafts each section; Yichen revises substantially and owns the final text (decided 2026-09-24). Consequences: an AI-use disclosure goes in every version (an "LLM usage" section for ICLR, the setup or acknowledgements for NeurIPS and arXiv). **ACL-family workshops are excluded** (they prohibit AI-generated novel research content). Yichen reads the whole paper before any posting.

## Paper standard (Yichen, 2026-09-24; governs Stages 5 and 8)
- A professional, high-standard paper: **about 10–13 pages of main text** (excluding references and appendix), with **at least 4–6 tables and 4–6 figures**, all generated from locked outputs.
- **Tension with the venue (to resolve):** NeurIPS 2026 main-track papers have 9 content pages, and ML workshops are usually shorter (set per call for papers). **Agreed direction (2026-09-24):** the **full 10–13-page arXiv paper is the primary deliverable**; any workshop version is cut down from it. TMLR (12-page main-text norm) is the alternative. **Venue chosen 2026-09-25:** the full 10–13-page arXiv paper is the primary deliverable, followed by a condensed version for a security or watermarking workshop (prefer a non-archival call, which keeps TMLR open later). Speed matters because of the scoop risk (the Self-Recognition authors list the defence as future work).
- Consequence for design: the study plan must support a main result, robustness checks and ablations (enough material for 4–6 substantive figures and tables), not a single experiment.

## Constraints
- Data: public, openly licensed prompt and text corpora and open-weight models only. Record licences before download (frozen-data-provenance skill). Prefer Apache-2.0/MIT models; research-only licences need a decision.
- Final holdout (decided): a held-out prompt set and a held-out attack set, fixed and hashed at Stage 5, asserted in code, and never generated on before the final protocol is locked.
- Compute: local Apple M5, 16 GB unified memory, PyTorch MPS available (the installed PyTorch 1.13 is old; upgrade in a project virtual environment). Realistic: models of 0.5–1.5B parameters for generation, small paraphrasers. **Local only** (decided): no paid cloud GPUs. The question must be answerable at this scale. **Measure the time per generation in Stage 4, before any protocol.**
- Time budget (decided): about 3 months, targeting an arXiv preprint and a workshop deadline around Q1 2027.
- Other: no proprietary APIs are needed for the main claims.

## Research question (LOCKED 2026-09-25)
**Working title:** *Stealing activation watermarks: key recovery, spoofing, exact tests and defences for activation-steering LLM watermarks.*

**Question.** For activation-steering LLM watermarks (a secret direction added to the residual stream during generation, detected by re-encoding the text with the same open model; for example Self-Recognition, ICML 2026, and SLAM-style per-document keyed feature steering), consider an attacker with the public open-weight model and *n* watermarked outputs, but not the key direction or layer. (i) How accurately can the key be recovered as a function of *n*? (ii) How effective are **spoofing** (other text accepted as watermarked) and **scrubbing** (removal at matched quality), at a fixed false-positive rate? (iii) What do **exact score tests** (GaussMark-style, treating steering as an additive-parameter perturbation) give as detectors and as a lens on key leakage? (iv) How much protection does a **context-keyed or rotating direction** buy, and what does it cost in paraphrase robustness and quality?
*Comparators:* each scheme's own detectors (classifier and cosine), and the exact score test. *Failure mechanism:* a fixed key direction produces a consistent first-order drift in re-encoded activations and score vectors, which averaging over outputs can estimate.
*Not claimed:* the first stealing attack on LLM watermarks (known for token schemes); a new general-purpose watermark; the paraphrase-robustness limit (PASA Theorem 1; used only as a remark).
Gate: [`ACTWM_GATE_v0.1.md`](ACTWM_GATE_v0.1.md) (PASS after the feasibility pilot).
