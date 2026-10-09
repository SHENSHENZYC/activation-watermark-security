"""Assemble the paper draft (Stage 8, step 5). Reads the filled sections under build/sections/ in the outline's order, strips
each section's "Open items" list into PAPER_OPEN_ITEMS_v0.1.md, inserts every table (build/T*.md, build/TA*.md) and figure
(build/F*.png, build/FA*.png) at its marker line or after the paragraph that first mentions it, renumbers tables (T1 →
Table 1, TA4c → Table A4c) and figures (F2 → Figure 2, FA1 → Figure A1) and rewrites every cross-reference, removes the
internal "(see `build/…`)" markers and lists the remaining repository paths for review, checks that every [@key]
citation has an entry in references.bib, re-checks the lock table against the lock files (every protocol hash in Table 1
re-hashed from the protocol file and compared with its PRE_RUN_LOCK.json), and writes PAPER_DRAFT_v0.1.md. With --render
it also builds build/paper.html (pandoc, citeproc, MathML) and build/PAPER_DRAFT_v0.1.pdf (headless Chrome), renders the
main text alone for its page count, and writes build/page_count.json.
Run: .venv/bin/python research/paper/fill_sections.py && .venv/bin/python research/paper/assemble.py --render
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]
BUILD = PAPER / "build"
SEC = BUILD / "sections"
VERSION = "v0.1"
TITLE = "A Security Analysis of an Activation-Steering LLM Watermark: Key Recovery, Forgery, Scrubbing and Keyed Defences"
AUTHOR = "Yichen Zhao (Independent Researcher; alexyczhao@gmail.com)"
DATE = "October 2026. Published at https://shenshenzyc.github.io/activation-watermark-security/"
MAIN = ["sec1_introduction.md", "sec2_background_threat_model.md", "sec3_exact_test.md", "sec4_setup.md", "sec5_1_calibration.md", "sec5_2_probe_forgery.md",
        "sec5_3_exact_test.md", "sec5_4_stealing.md", "sec5_5_scrubbing.md", "sec5_6_keyed.md", "sec5_7_tradeoff.md", "sec6_related_work.md", "sec7_limitations.md",
        "sec8_reproducibility.md", "sec9_conclusion.md"]
APPX = ["appA_protocols_locks.md", "appB_exact_test_detail.md", "appC_attackers.md", "appD_per_key.md", "appE_quality.md", "appF_scrubbing_secondaries.md",
        "appG_defence_detail.md", "appH_samples.md", "appI_regulators.md"]
# where a table or figure goes if no section mentions it (the outline's assignment)
FALLBACK = {"TA4b": "appC_attackers.md", "TA5": "appC_attackers.md", "T2": "sec5_1_calibration.md", "T3": "sec5_2_probe_forgery.md", "T4": "sec5_3_exact_test.md",
            "T5": "sec5_5_scrubbing.md", "T6": "sec5_6_keyed.md"}
CAPTIONS = {
    "F1": "Calibration on three base models at [[new_tokens]] tokens: (a) the trained probe's AUROC and (b) the perplexity ratio to unsteered text against the strength ρ, with the [[cal_auroc_bar]] and [[cal_ppl_bar]] bars and the published α = 5 marked as ρ for each model; 512-token points for two models. No model crosses both bars at the same ρ.",
    "F2": "Fluent, non-repetitive acceptance by the owner's probe at its 1% threshold against ρ for the genuine texts, the random-key control and the Route A and Route B forgeries at n = 64 and 256 (medians over 8 keys with 95% cluster-bootstrap bands; the dashed bar is half the genuine rate, rule F1).",
    "F3": "(a) Genuine and random-key texts attributed at an exact 1% false-positive rate by the exact test and by the probe, against ρ. (b) Study 1's texts accepted by the probe (hollow) and attributed by the exact test (filled), per forgery set and strength.",
    "F4": "Key recovery (cosine with the true key) and forgery acceptance against the attacker's budget n at ρ = 0.35 and 0.50: the fixed key (Route A′ at the known layer and with the layer search), the context-hashed arms and rotation (the naive and clustering attackers), with the D1 bars and the random-key controls.",
    "F5": "Detection after scrubbing (top) and scrub success (bottom) against ρ for the two paraphrasers, with the length-matched controls and the originals' miss rate, and for word edits at 5% of the tokens with the true key, the attacker's estimate and random positions; the dashed line is the 50% bar.",
    "F6": "The frontier per arm at ρ = 0.35 and 0.50: forgery acceptance at n = 1,024 (stealability), scrub success after P-Qwen (robustness lost) and the perplexity ratio to the fixed key (quality), with the materiality bars. Rotation's clustering point at ρ = 0.35 is shown twice: the pre-registered rule's value and the addendum's every-cluster value (hollow, post hoc).",
    "FA1": "Per-key false-positive rates at p ≤ 0.01 on 1,000 null texts per key: (a) the fixed key's exact test on unwatermarked model text and human continuations (Study 3) and after paraphrase by P-Qwen and P-Phi (Study 2); (b) the keyed tests of the context-hashed arms (Study 5) beside the fixed key's. Dotted: the nominal 1%; dashed: the 3% per-key gate.",
    "FA2": "Key leakage. (a) Study 3: each forgery set's exact-test attribution per key against the attacker's recovered cosine with that key, one point per key, strength and set (Routes A and B; attacker versions v0.2–v0.4). (b) Study 2: E-est's scrub success at 5% of the tokens against the same cosine, one point per key and strength.",
    "FA3": "Scrubbing secondaries. Top: scrub success against the edit budget for the true key, the attacker's estimate and random edits, per strength (medians over 8 keys with 95% bands; 0% is the originals' miss rate; dashed: 50%). Bottom: the owner's probe (hollow) against the exact test (filled) on the same scrubbed texts, per method and strength (a lead, labelled).",
    "FA4": "The per-context attacker on the context-hashed arms: (a) the coverage of a genuine text's positions by estimated contexts and (b) the number of contexts estimated, against the budget n; (c) at n = 1,024, the cosine of the per-context estimates with their true directions by how often the context was seen (medians over 8 keys).",
    "FA5": "What the repetition condition changes, n = 256: (a, b) the v0.3 forgeries' fluent acceptance under the perplexity-only rule and under v0.4's rule, and the v0.4 forgeries' acceptance, with the genuine texts' rate as the ceiling; (c) the share of texts above the key's seq-rep-4 bar per forgery set (medians over 8 keys).",
    "FA6": "P-Qwen paraphrase per arm beside the fixed key at ρ = 0.35 and 0.50: scrub success (top) and attribution after paraphrase (bottom), medians over 8 keys with 95% intervals where the locked file holds them, and the D2 difference d from the fixed key. Rotation's attribution after paraphrase is not in the locked results file and is not drawn.",
}
def opt(name, default=None):
    for a in sys.argv[1:]:
        if a.startswith(f"--{name}="):
            return a.split("=", 1)[1]
    return default
FIGWIDTH = int(opt("figwidth", "80"))                                # length decision 2026-10-06: figures at 80% of the text width
DEFAULT_MOVE = "T3b:appE_quality.md,T6b:appG_defence_detail.md"              # length decision 2026-10-06: the v0.2 recovery and the D2/D3 detail tables become appendix tables
MOVE = dict(x.split(":") for x in opt("move", DEFAULT_MOVE).split(",") if x)
RENUMBER = {"T3b": "A15", "T6b": "A16"}                                     # moved main tables take the next appendix numbers; the remaining part of each family loses its letter
NO_FIG, NO_TAB = "--no-figures" in sys.argv, "--no-tables" in sys.argv
STEM = opt("stem")                                                   # a measurement variant: outputs under build/<stem>_*, the draft files untouched
values = {}
for f in sorted(BUILD.glob("values_*.json")):
    values.update(json.loads(f.read_text()))
PH = re.compile(r"\[\[([A-Za-z0-9_.+-]+)\]\]")


def fill(s):
    def sub(m):
        if m.group(1) not in values:
            sys.exit(f"unresolved placeholder in assembly text: {m.group(1)}")
        return str(values[m.group(1)])
    return PH.sub(sub, s)


def num_table(tid):
    if tid in RENUMBER and tid in MOVE:
        return RENUMBER[tid]
    m = re.fullmatch(r"T(A?)(\d+)([a-d]?)", tid)
    fam = f"T{m.group(1)}{m.group(2)}"
    siblings = [q.stem for q in BUILD.glob(f"{fam}[a-d].md") if not (q.stem in RENUMBER and q.stem in MOVE)]
    part = "" if len(siblings) == 1 else m.group(3)
    return f"{m.group(1)}{m.group(2)}{part}"


def num_figure(fid):
    m = re.fullmatch(r"F(A?)(\d+)", fid)
    return f"{m.group(1)}{m.group(2)}"


def widths(body):
    """Rewrite the pipe table's separator line so that the dash counts follow the columns' content (the 85th percentile of cell
    lengths, floored at 10 and at 2.6 times the longest single word), which pandoc turns into relative column widths; otherwise every column gets the same width and a
    short column wastes space while a long one wraps character by character."""
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in body]
    ncol = len(rows[0])
    lens = [[len(r[j]) if j < len(r) else 0 for r in [rows[0]] + rows[2:]] for j in range(ncol)]
    import numpy as np
    cap = 40 if ncol < 12 else max(14, round(240 / ncol))  # in very wide tables the long text columns yield width to the many short ones (2026-10-08)
    w = [max(10, min(cap, round(max(1, np.percentile(l, 85)) ** 0.65 * 2.2))) for l in lens]  # concave: short columns stay readable, long ones wrap
    # floor each column at its longest single word (header included), so that a word such as "AUROC" never exceeds its cell (2026-10-08)
    longest = [max((len(tok) for r in [rows[0]] + rows[2:] if j < len(r) for tok in re.split(r"[\s/]+|(?<=[-\u2013])", r[j]) if tok), default=1) for j in range(ncol)]
    w = [max(x, min(cap, round(t * 2.6))) for x, t in zip(w, longest)]  # LaTeX breaks at hyphens and spaces, so the floor follows the longest unbreakable piece
    body = list(body)
    body[1] = "|" + "|".join("-" * x for x in w) + "|"
    return body


def table_block(tid):
    """build/<tid>.md -> a pandoc pipe table with its caption line and notes."""
    txt = (BUILD / f"{tid}.md").read_text().strip().splitlines()
    cap = re.fullmatch(r"\*\*(T\w+) — (.*)\*\*", txt[0].strip())
    assert cap and cap.group(1) == tid, (tid, txt[0][:80])
    body, notes, in_table = [], [], False
    for line in txt[1:]:
        if line.startswith("|"):
            body.append(line)
            in_table = True
        elif in_table and line.strip() == "":
            in_table = False
        elif not line.startswith("|") and line.strip():
            notes.append(line)
    if NO_TAB:
        return ""
    body = widths(body)
    out = "\n".join(body) + f"\n\n: **Table {num_table(tid)}.** {cap.group(2)}\n"
    if notes:
        out += "\n" + "\n\n".join(f"*{n}*" for n in notes) + "\n"
    return out


def figure_block(fid):
    assert (BUILD / f"{fid}.png").exists(), fid
    return "" if NO_FIG else f"![**Figure {num_figure(fid)}.** {fill(CAPTIONS[fid])}](build/{fid}.png){{width={FIGWIDTH}%}}\n"


MARK = re.compile(r"^\*\*(Table|Tables|Figure|Figures) ((?:T\w+|F\w+)(?: and (?:T\w+|F\w+))*)\*\* \(see ([^)]*)\)\.\s*$", re.M)
sections, open_items, placed, mentioned_first, moved_later = {}, {}, set(), {}, []
for name in MAIN + APPX:
    txt = (SEC / name).read_text()
    parts = re.split(r"^## Open items\s*$", txt, flags=re.M)
    body = parts[0].rstrip() + "\n"
    if len(parts) > 1:
        open_items[name] = parts[1].strip()
    # markers -> content
    def repl(m):
        kind, ident, see = m.group(1).rstrip("s"), m.group(2), m.group(3)
        ids = re.findall(r"build/(T\w+|F\w+)\.(?:md|png)", see)
        blocks = []
        for i in ids:
            placed.add(i)
            if i in MOVE:
                moved_later.append(i)
                continue
            blocks.append(table_block(i) if kind == "Table" else figure_block(i))
        return "\n".join(blocks)
    body = MARK.sub(repl, body)
    sections[name] = body
# tables and figures without a marker: after the paragraph that first mentions them (by part or by family), else the fallback section's end
pieces_all = sorted(p.stem for p in BUILD.glob("T*.md")) + sorted(p.stem for p in BUILD.glob("F*.png") if re.fullmatch(r"FA?\d+", p.stem))
for piece in pieces_all:
    if piece in placed:
        continue
    is_fig = piece.startswith("F")
    family = re.fullmatch(r"(T(?:A)?\d+)[a-d]?", piece).group(1) if not is_fig else piece
    labels = [re.compile(rf"\b(Table|Figure) {re.escape(piece)}\b")] + ([re.compile(rf"\b(Table|Figure) {re.escape(family)}\b")] if family != piece else [])
    target, lab = None, None
    pool = APPX if (piece.startswith("TA") or piece.startswith("FA")) else MAIN + APPX  # appendix tables and figures stay in the appendix
    for L in labels:
        for name in pool:
            if L.search(sections[name]):
                target, lab = name, L
                break
        if target:
            break
    block = figure_block(piece) if is_fig else table_block(piece)
    if piece in MOVE:
        sections[MOVE[piece]] = sections[MOVE[piece]].rstrip() + "\n\n" + block
        placed.add(piece)
        continue
    if target is None:
        target = FALLBACK.get(piece) or FALLBACK.get(family)
        assert target, f"{piece} is mentioned nowhere and has no fallback"
        sections[target] = sections[target].rstrip() + "\n\n" + block
        open_items.setdefault("assembly", "")
        open_items["assembly"] += f"\n- {piece} is mentioned in no section; placed at the end of {target}."
    else:
        paras = sections[target].split("\n\n")
        for i, para in enumerate(paras):
            if lab.search(para) and not para.startswith("|") and not para.startswith(": **Table"):
                paras.insert(i + 1, block.rstrip())
                break
        sections[target] = "\n\n".join(paras)
    placed.add(piece)
for i in moved_later:
    sections[MOVE[i]] = sections[MOVE[i]].rstrip() + "\n\n" + table_block(i)
# cross-references: Table T3a -> Table 3a; Table TA4c -> Table A4c; Figure F2 -> Figure 2; Figure FA1 -> Figure A1
def xref(s):
    for tid, new in RENUMBER.items():
        if tid in MOVE:
            s = re.sub(rf"\bTable {tid}\b", f"Table {new}", s)
    s = re.sub(r"\bTable T(A?)(\d+)([a-d]?)\b", lambda m: f"Table {num_table('T' + m.group(1) + m.group(2) + m.group(3))}", s)
    s = re.sub(r"\bTables T(A?)(\d+)([a-d]?)–T(A?)(\d+)([a-d]?)\b", lambda m: f"Tables {m.group(1)}{m.group(2)}{m.group(3)}–{m.group(4)}{m.group(5)}{m.group(6)}", s)
    s = re.sub(r"\bTables T(A?)(\d+)([a-d]?)\b", lambda m: f"Tables {m.group(1)}{m.group(2)}{m.group(3)}", s)
    s = re.sub(r"\bFigure F(A?)(\d+)([a-d]?)\b", lambda m: f"Figure {m.group(1)}{m.group(2)}{m.group(3)}", s)
    s = re.sub(r"\bFigures F(A?)(\d+)\b", lambda m: f"Figures {m.group(1)}{m.group(2)}", s)
    s = re.sub(r"\b(T(A?)\d+[a-d]?) and T(A?)(\d+[a-d]?)\b", lambda m: m.group(0), s)
    return s
for name in sections:
    sections[name] = xref(sections[name])
# remaining repository paths (for review, not stripped)
paths = {}
for name, body in sections.items():
    for m in re.findall(r"`([^`]*(?:research/|build/|\.py|\.json|\.md)[^`]*)`", body):
        paths.setdefault(name, set()).add(m)
# citations
bib = (PAPER / "references.bib").read_text()
bibkeys = set(re.findall(r"^@\w+\{([^,]+),", bib, re.M))
cited = set()
for body in sections.values():
    for m in re.finditer(r"\[[^\]]*@[^\]]*\]", body):
        cited.update(re.findall(r"@([A-Za-z0-9_:.-]+?)(?=[\];, ])", m.group(0) + " "))
missing = sorted(k for k in cited if k not in bibkeys)
if missing:
    sys.exit(f"citations without a bib entry: {missing}")
uncited = sorted(bibkeys - cited)
# the lock table re-checked from the lock files
LOCKS = {"v02": "study1_v0.2", "v03": "study1_v0.3", "v04": "study1_v0.4", "s3": "study3_v0.1", "s2": "study2_v0.1", "s5": "study5_v0.1"}
for tag, folder in LOCKS.items():
    lock = json.loads((ROOT / "research" / "outputs" / folder / "PRE_RUN_LOCK.json").read_text())
    proto = ROOT / lock["protocol"]
    if not proto.exists():
        proto = ROOT / "research" / Path(lock["protocol"]).name  # Study 3's lock stores the bare file name
    h = hashlib.sha256(proto.read_bytes()).hexdigest()
    assert h == lock["protocol_sha256"], f"{folder}: the protocol file no longer matches its lock"
    assert values[f"t1_{tag}_protocol_hash12"] == h[:12], f"{folder}: Table 1's hash prefix differs from the lock"
# assemble
abstract = re.split(r"^## Open items\s*$", (SEC / "sec0_abstract.md").read_text(), flags=re.M)
open_items["sec0_abstract.md"] = abstract[1].strip() if len(abstract) > 1 else ""
abstract_body = abstract[0].replace("# Abstract", "").strip()
front = f"---\ntitle: \"{TITLE}\"\nauthor: \"{AUTHOR}\"\ndate: \"{DATE}\"\nbibliography: references.bib\nlink-citations: true\n---\n\n"
front += "::: {.abstract}\n**Abstract.** " + abstract_body + "\n:::\n\n"
main_md = front + "\n\n".join(sections[n].strip() for n in MAIN) + "\n\n"
refs_md = "# References\n\n::: {#refs}\n:::\n\n"
appx_md = "\n\n".join(sections[n].strip() for n in APPX) + "\n"
draft = main_md + refs_md + appx_md
if STEM is None:
    (PAPER / f"PAPER_DRAFT_{VERSION}.md").write_text(draft)
# open items: Yichen's decisions first, the records (decided, resolved, confirmed, applied cuts, re-confirmed quotations) after
def is_decision(item):
    low = item.lower()
    if any(low.startswith("- " + k) for k in ("decided", "resolved", "confirmed", "cuts applied", "cut applied", "bound by", "quotations re-confirmed", "every quotation", "the code's documents", "seeded from", "the ai-use paragraph follows")):
        return False
    return "yichen" in low or "wording call" in low or "decision" in low
lines = [f"# Open items collected at assembly ({VERSION}, 2026-10-06)\n", "Collected from every section file's \"Open items\" list by `assemble.py`. Part 1 holds what needs Yichen; Part 2 the records (decisions taken, checks done, cuts applied) kept for the audit trail.\n"]
decisions, records = [], []
for name in ["sec0_abstract.md"] + MAIN + APPX + (["assembly"] if "assembly" in open_items else []):
    if name not in open_items or not open_items[name].strip():
        continue
    items = [i.strip() for i in re.split(r"^- ", open_items[name].strip(), flags=re.M) if i.strip()]
    for it in items:
        (decisions if is_decision("- " + it) else records).append((name, it))
lines.append("\n## Part 1 — for Yichen\n")
for name, it in decisions:
    lines.append(f"- **{name}:** {it}")
lines.append(f"\n## Part 2 — records ({len(records)} items)\n")
cur = None
for name, it in records:
    if name != cur:
        lines.append(f"\n### {name}")
        cur = name
    lines.append(f"- {it}")
lines.append("\n## Internal file references still in the text (review before release; the assembly strips only the `(see build/…)` markers)\n")
for name in MAIN + APPX:
    if name in paths:
        lines.append(f"- {name}: " + "; ".join(f"`{p}`" for p in sorted(paths[name])))
lines.append(f"\n## Bibliography\n- {len(cited)} keys cited; every one has an entry. Entries not cited anywhere: {', '.join(uncited) if uncited else 'none'}.\n")
if STEM is None:
    (PAPER / f"PAPER_OPEN_ITEMS_{VERSION}.md").write_text("\n".join(lines))
print(f"assembled: {len(MAIN)} main sections, {len(APPX)} appendices; tables/figures placed: {len(placed)}; citations: {len(cited)} keys, {len(uncited)} bib entries uncited")
if "--render" not in sys.argv:
    sys.exit(0)
# render: pandoc -> HTML (full, and main text only), Chrome -> PDF, pdfinfo -> pages
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
def render(md_text, stem, suppress_bib=False):
    md = BUILD / f"{stem}.md"
    md.write_text(md_text)
    html = BUILD / f"{stem}.html"
    subprocess.run(["pandoc", str(md), "-s", "--citeproc", "--mathml", "--css", "paper.css", "--resource-path", str(PAPER), "-o", str(html), "--metadata", "lang=en-GB"] + (["--metadata", "suppress-bibliography=true"] if suppress_bib else []),
                   cwd=PAPER, check=True)
    # inline the css and make image paths absolute so Chrome can print from file://
    h = html.read_text().replace('<link rel="stylesheet" href="paper.css" />', "<style>\n" + (PAPER / "paper.css").read_text() + "\n</style>")
    h = h.replace('src="build/', f'src="file://{BUILD}/')
    html.write_text(h)
    pdf = BUILD / f"{stem}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files", f"--print-to-pdf={pdf}", f"file://{html}"],
                   check=True, capture_output=True)
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", info).group(1))
stem = STEM or f"PAPER_DRAFT_{VERSION}"
pages_full = render(draft, stem)
pages_main = render(main_md, (STEM + "_main_only") if STEM else "paper_main_only", suppress_bib=True)
counts = {"variant": STEM or "default", "figwidth_pct": FIGWIDTH, "moved": MOVE, "no_figures": NO_FIG, "no_tables": NO_TAB, "full_pdf_pages": pages_full, "main_text_pages_incl_title_and_abstract_excl_references": pages_main, "outline_budget_main_pages": 12.75, "renderer": "pandoc 3.0 + headless Chrome; Letter, 1in margins, 11pt serif, single column (build/paper.css)"}
(BUILD / ("page_count.json" if STEM is None else f"{STEM}_page_count.json")).write_text(json.dumps(counts, indent=1))
print(json.dumps(counts, indent=1))
