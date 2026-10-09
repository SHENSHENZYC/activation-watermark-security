"""Prose word counts per section against the outline's page budget (about 650 words per single-column page), excluding
each file's "Open items" list, table markers and headings. Run: python3 research/paper/wordcount.py [files...]"""
import re, sys
from pathlib import Path
PAPER = Path(__file__).resolve().parent
WPP = 650.0
files = [Path(a) for a in sys.argv[1:]] or sorted((PAPER / "sections").glob("*.md"))
tot = 0
for f in files:
    txt = f.read_text()
    txt = re.split(r"^## Open items\s*$", txt, flags=re.M)[0]
    lines = [l for l in txt.splitlines() if not l.startswith("#") and not l.startswith("**Table T") and not l.startswith("**Figure F")]
    words = len(re.findall(r"\S+", "\n".join(lines)))
    tot += words
    print(f"{f.name:34s} {words:5d} words  {words / WPP:5.2f} pages")
print(f"{'total':34s} {tot:5d} words  {tot / WPP:5.2f} pages")
