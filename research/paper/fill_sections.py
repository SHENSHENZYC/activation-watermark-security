"""Render research/paper/sections/*.md into research/paper/build/sections/*.md, replacing every [[name]] placeholder
with the value a table or figure script registered in build/values_*.json. Fails if any placeholder is unresolved
(unless --allow-unresolved is given, for drafting), and refuses conflicting duplicate names across scripts. Lists
registered values no section uses (information only). The Milestone 15 assembly script builds on this.
Run: .venv/bin/python research/paper/fill_sections.py [--allow-unresolved]
"""
import json
import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
BUILD = PAPER / "build"
SECTIONS = PAPER / "sections"
OUTDIR = BUILD / "sections"
OUTDIR.mkdir(parents=True, exist_ok=True)
PH = re.compile(r"\[\[([A-Za-z0-9_.+-]+)\]\]")

values, origin = {}, {}
for f in sorted(BUILD.glob("values_*.json")):
    for k, v in json.loads(f.read_text()).items():
        if k in values and values[k] != v:
            sys.exit(f"conflicting values for [[{k}]]: {values[k]!r} ({origin[k]}) vs {v!r} ({f.name})")
        values[k], origin[k] = v, f.name

allow = "--allow-unresolved" in sys.argv
unresolved, used = {}, set()
for sec in sorted(SECTIONS.glob("*.md")):
    txt = sec.read_text()

    def sub(m):
        name = m.group(1)
        if name in values:
            used.add(name)
            return str(values[name])
        unresolved.setdefault(sec.name, []).append(name)
        return m.group(0)

    out = PH.sub(sub, txt)
    (OUTDIR / sec.name).write_text(out)
    n_ph = len(PH.findall(txt))
    print(f"{sec.name}: {n_ph} placeholders, {len(unresolved.get(sec.name, []))} unresolved")

unused = sorted(set(values) - used)
print(f"registered values: {len(values)}; used: {len(used)}; unused: {len(unused)}")
if unused:
    print("  unused (information only):", ", ".join(unused[:40]), "..." if len(unused) > 40 else "")
if unresolved:
    for s, names in unresolved.items():
        print(f"UNRESOLVED in {s}: {sorted(set(names))}")
    if not allow:
        sys.exit(1)
print("all placeholders resolved" if not unresolved else "unresolved placeholders allowed (drafting mode)")
