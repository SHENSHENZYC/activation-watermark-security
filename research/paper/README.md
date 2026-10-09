# Paper folder — conventions (Stage 8; set up 2026-10-05, Milestone 12)

Binding documents: [`OUTLINE_v0.1.md`](OUTLINE_v0.1.md) (approved; the section plan, the figure and table plan, the drafting order) and [`../CLAIM_GATE_v0.1.md`](../CLAIM_GATE_v0.1.md) §2 (the claims) and §6 (the twelve wording rules). Every draft sentence obeys them.

## Layout
| Path | What it holds |
|---|---|
| `sections/secN_*.md`, `sections/appX_*.md` | One Markdown file per section and appendix, drafted in the outline's order. Each ends with an **"Open items"** list (what still needs a number, a decision by Yichen, or a re-check). |
| `tables/tabN_*.py`, `tables/tabAN_*.py` | One script per table. Each reads only locked outputs (`../outputs/**/PRE_RUN_LOCK.json`, `RUN_MANIFEST*.json`, `INPUT_VALIDATION.json`, `results.json`), **asserts its totals against the file it reads**, and writes `build/tabX.md` (the table) and `build/values_tabX.json` (the numbers the prose quotes). |
| `figures/figN_*.py`, `figures/figAN_*.py` | One script per figure (Milestones 13 and 15), same contract; outputs `build/figX.png` and `build/values_figX.json`. Follow the dataviz skill; view every figure before use. |
| `common.py` | Shared helpers: paths, loading, hash checks, number formatting, the values registry. |
| `fill_sections.py` | Renders `sections/*.md` into `build/sections/*.md`, replacing every `[[name]]` with the value registered by a script, and **fails if any placeholder is unresolved or any registered value is unused by design** (unused values are listed, not fatal). The Milestone 15 assembly script (`assemble.py`) builds on it. |
| `references.bib` | Built from primary sources (arXiv API, Crossref, PMLR, the ACL Anthology, DataCite, the PDF covers for author order); validated with the citation-management skill at 0 errors. Anything confirmed only second-hand is flagged in the entry's `note`. |
| `build/` | Generated; committed so that the drafts can be read with their numbers. Never edited by hand. |
| `make_latex.py`, `latex/` | Stage 9: converts `PAPER_DRAFT_v0.1.md` to arXiv LaTeX (`latex/main.tex`; `latex/references.bib` without the internal notes; `latex/figures/*.pdf`) and compiles it with Tectonic (`latex/main.pdf`, `latex/main.bbl`, `latex/page_count_latex.json`). Run after `assemble.py`. |
| `sections/sec0_arxiv_abstract.md` | The arXiv abstract field (at most 1,920 characters), filled like every section; not part of the PDF. |
| `ENDORSEMENT_REQUEST.md`, `COURTESY_NOTICE.md` | The two emails Yichen sends at posting (Stage 9 decisions (g) and (h)). |

## Rules for prose (guide A4.1, A4.3; gate §6)
1. **No number is typed by hand.** A number in a section is a placeholder `[[name]]`; a committed script registers `name` from a locked file. Counts are re-counted by the script, never copied from a report. **Convention (decision A10, 2026-10-08):** a design constant that names a condition (a strength such as ρ = 0.35, a budget point such as n = 64, a context width, a model size such as 1–3B) may be typed when it matches the lock file's `design` field or the protocol; every measured result, count, interval and bar stays a placeholder. Audited 2026-10-08 against the lock files' `design` fields.
2. **Quotations** come only from the gate's §3 and §8 (confirmed against the PDF text with a page number) or from a fresh `pdftotext` check; each carries its PDF page. The earlier gates' fetch-tool paraphrases are never quoted.
3. **Inferences are labelled** ("we read this as", "consistent with"); exploratory and post-hoc readings are labelled wherever they appear (rule 9).
4. **Transfers are named as transfers** with their originators (rule 2); bounds in every claim (rule 5); attacker, budget and access in every security sentence (rule 4); "exact on average over keys" (rule 3).
5. Citation keys are the `references.bib` keys, written `[@key]` (Pandoc style) so that the assembly script can check that every key resolves.
6. Section files carry internal cross-references as `§N` and `App. X`, and figure and table references as `Table T1`, `Figure F2`, `Table TA3` (the plan's labels); the assembly script renumbers them.

## How to regenerate everything in this folder
```bash
cd /path/to/activation-watermark-stealing
for s in research/paper/tables/*.py; do .venv/bin/python "$s" || exit 1; done
.venv/bin/python research/paper/fill_sections.py
python3 .claude/skills/citation-management/scripts/validate_citations.py research/paper/references.bib
.venv/bin/python research/paper/assemble.py --render
.venv/bin/python research/paper/make_latex.py
```
