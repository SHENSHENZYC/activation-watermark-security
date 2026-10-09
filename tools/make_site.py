"""Build the GitHub Pages site for the paper (Stage 9; the site is the publication of record, decided 2026-10-09: no arXiv).

Writes docs/ (served by GitHub Pages from the public snapshot repository's main branch, /docs):
  index.html   the paper page: title, author, date, links (PDF, HTML version, code), the
               abstract (from the filled sec0_abstract.md, citations resolved against references.bib), licences and the
               AI-use disclosure
  paper.pdf    the paper (research/paper/latex/main.pdf)
  paper.html   the HTML render (research/paper/build/PAPER_DRAFT_v0.1.html) with its figures under figures/ and its
               stylesheet alongside
  figures/     the figure PNGs
  .nojekyll    so that GitHub Pages serves the files as they are
Run: python3 tools/make_site.py
"""
import datetime as dt
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "research" / "paper"
DOCS = ROOT / "docs"
REPO_URL = "https://github.com/SHENSHENZYC/activation-watermark-security"
SITE_URL = "https://shenshenzyc.github.io/activation-watermark-security/"

asm = (PAPER / "assemble.py").read_text()
TITLE = re.search(r'^TITLE = "(.*)"$', asm, re.M).group(1)
AUTHOR_RAW = re.search(r'^AUTHOR = "(.*)"$', asm, re.M).group(1)
m = re.match(r"(.*?) \((.*?); (.*?)\)$", AUTHOR_RAW)
AUTHOR, AFFIL, EMAIL = (m.group(1), m.group(2), m.group(3)) if m else (AUTHOR_RAW, "", "")
YEAR = "2026"
DATE = dt.date.today().strftime("%-d %B %Y")

# --- the abstract, from the filled section, citations resolved
abs_md = (PAPER / "build" / "sections" / "sec0_abstract.md").read_text().split("## Open items")[0].split("\n", 1)[1].strip()
abs_html = subprocess.run(["pandoc", "-f", "markdown", "-t", "html", "--citeproc", "--mathml", "--bibliography", str(PAPER / "references.bib"),
                           "--metadata", "suppress-bibliography=true", "--metadata", "link-citations=false"],
                          input=abs_md, text=True, capture_output=True, check=True).stdout.strip()

# --- files
if DOCS.exists():
    shutil.rmtree(DOCS)
(DOCS / "figures").mkdir(parents=True)
shutil.copy(PAPER / "latex" / "main.pdf", DOCS / "paper.pdf")
shutil.copy(PAPER / "paper.css", DOCS / "paper.css")
n_fig = 0
for p in sorted((PAPER / "build").glob("F*.png")):
    if re.fullmatch(r"F[A0-9]+\.png", p.name):
        shutil.copy(p, DOCS / "figures" / p.name); n_fig += 1
page = (PAPER / "build" / "PAPER_DRAFT_v0.1.html").read_text()
page, n_src = re.subn(r'src="file://[^"]*/research/paper/build/(F[A0-9]+\.png)"', r'src="figures/\1"', page)
assert n_src == n_fig, (n_src, n_fig)
assert "file://" not in page, "an absolute local path survived in the HTML version"
page = page.replace('href="paper.css"', 'href="paper.css"')
(DOCS / "paper.html").write_text(page)
(DOCS / ".nojekyll").write_text("")

# --- BibTeX for the citation box
key = "zhao2026activation"
bib = [f"@misc{{{key},", f"  author = {{Zhao, Yichen}},", f"  title  = {{{TITLE}}},", f"  year   = {{{YEAR}}},",
       "  howpublished = {Preprint, self-published}", f"  url    = {{{SITE_URL}}},", f"  note   = {{Code, protocols and results: {REPO_URL}}}", "}"]
bib[4] = bib[4] + ","
bib[6] = bib[6] + ","
bibtex = "\n".join(bib)

links = [("Paper (PDF)", "paper.pdf", "primary"), ("HTML version", "paper.html", ""), ("Code, protocols and results", REPO_URL, "")]
links_html = "\n".join(f'      <a class="btn {cls}" href="{html.escape(href)}">{html.escape(label)}</a>' for label, href, cls in links)
arxiv_note = '<p class="note">Published here as a preprint on 9 October 2026 (UTC); the repository holds the posting commit under the tag <code>v0.1-published</code>.</p>'

index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<meta name="description" content="Paper page: {html.escape(TITLE)} ({html.escape(AUTHOR)}, {YEAR}).">
<meta name="citation_title" content="{html.escape(TITLE)}">
<meta name="citation_author" content="Zhao, Yichen">
<meta name="citation_publication_date" content="{YEAR}">
<meta name="citation_pdf_url" content="{SITE_URL}paper.pdf">
<style>
  :root {{ --bg: #ffffff; --fg: #1a1a1a; --muted: #5a5a5a; --line: #e3e3e3; --accent: #1f4e8c; --accent-fg: #ffffff; --box: #f6f7f9; }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #121417; --fg: #e8e8e8; --muted: #a8a8a8; --line: #2d3138; --accent: #7aa7e0; --accent-fg: #0f1a2b; --box: #1b1f25; }} }}
  :root[data-theme="dark"] {{ --bg: #121417; --fg: #e8e8e8; --muted: #a8a8a8; --line: #2d3138; --accent: #7aa7e0; --accent-fg: #0f1a2b; --box: #1b1f25; }}
  html {{ background: var(--bg); }}
  body {{ margin: 0; padding: 0 16px; background: var(--bg); color: var(--fg); font: 17px/1.55 Georgia, "Times New Roman", serif; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 48px 0 64px; }}
  h1 {{ font-size: 1.9rem; line-height: 1.25; margin: 0 0 12px; font-weight: 600; }}
  .byline {{ color: var(--muted); margin: 0 0 24px; font-size: 1rem; }}
  .links {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 28px; }}
  .btn {{ display: inline-block; padding: 8px 14px; border: 1px solid var(--accent); border-radius: 6px; color: var(--accent); text-decoration: none; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 0.95rem; }}
  .btn.primary {{ background: var(--accent); color: var(--accent-fg); }}
  h2 {{ font-size: 1.15rem; margin: 32px 0 8px; font-weight: 600; letter-spacing: 0.01em; }}
  .abstract p {{ margin: 0 0 12px; text-align: left; }}
  pre {{ background: var(--box); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; overflow-x: auto; font-size: 0.85rem; line-height: 1.45; }}
  .note, footer {{ color: var(--muted); font-size: 0.9rem; }}
  footer {{ border-top: 1px solid var(--line); margin-top: 40px; padding-top: 16px; }}
  a {{ color: var(--accent); }}
</style>
</head>
<body>
<main>
  <h1>{html.escape(TITLE)}</h1>
  <p class="byline">{html.escape(AUTHOR)}, {html.escape(AFFIL)} &middot; <a href="mailto:{html.escape(EMAIL)}">{html.escape(EMAIL)}</a> &middot; {YEAR}</p>
  <div class="links">
{links_html}
  </div>
  {arxiv_note}
  <h2>Abstract</h2>
  <div class="abstract">
{abs_html}
  </div>
  <h2>What is in the repository</h2>
  <p>Every pre-registered protocol with its lock file (hashes of the protocol, the code and the reused inputs, written before any outcome existed), the validation reports, run manifests and result files of the six studies, every script that generated a number, table or figure in the paper, the paper's sources and the decision log. No model weights, generated corpora or article text are included; the manifests let a rebuild be checked by hash. <a href="{REPO_URL}">{REPO_URL}</a></p>
  <h2>Citation</h2>
  <pre>{html.escape(bibtex)}</pre>
  <footer>
    <p>Text and figures under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; code under the MIT licence. The text and code were drafted with Claude (Anthropic) under the author's direction; Codex (OpenAI) assisted with the final review; the author designed the studies, took every decision, verified every number against the locked outputs and takes full responsibility. Page built {DATE}.</p>
  </footer>
</main>
</body>
</html>
"""
(DOCS / "index.html").write_text(index)
size = sum(p.stat().st_size for p in DOCS.rglob("*") if p.is_file()) / 1e6
print(f"site written to docs/: index.html, paper.pdf, paper.html, {n_fig} figures, paper.css, .nojekyll; {size:.1f} MB")
