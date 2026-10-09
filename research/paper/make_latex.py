"""Convert the assembled draft to LaTeX for arXiv (Stage 9, step 6) and compile it with Tectonic.

Reads PAPER_DRAFT_v0.1.md (the assembly's output), strips the YAML front matter and the manual section numbers (LaTeX
numbers sections and appendices itself; tables and figures keep the assembly's labels inside their captions, printed with
labelformat=empty, so every cross-reference in the text stays as assembled), moves the abstract into the abstract
environment, points the figures at the PDF copies, runs pandoc (natbib citations, longtable tables), maps the non-ASCII
characters that pdflatex cannot typeset to LaTeX macros (so that arXiv's pdflatex and Tectonic's XeTeX give the same
result), writes latex/main.tex, latex/references.bib (the master bibliography with the internal `note` fields removed)
and latex/figures/*.pdf, compiles with Tectonic (BibTeX runs inside), and reports the page counts.
Run: .venv/bin/python research/paper/make_latex.py [--no-compile]
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
BUILD = PAPER / "build"
OUT = PAPER / "latex"
FIGS = OUT / "figures"
SRC = PAPER / "PAPER_DRAFT_v0.1.md"
COMPILE = "--no-compile" not in sys.argv

PREAMBLE = r"""\documentclass[11pt,letterpaper]{article}
% arXiv-compatible preamble (pdflatex); Tectonic (XeTeX) compiles the same source.
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,longtable,array,calc}
\usepackage{float}
\usepackage{pdflscape}
\usepackage{caption}
\captionsetup{labelformat=empty,font=small,skip=4pt}
\usepackage[numbers,sort&compress]{natbib}
\usepackage{xcolor}
\usepackage[hidelinks,breaklinks]{hyperref}
\usepackage{url}
\urlstyle{same}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\parskip}{4pt plus 1pt}
\setlength{\emergencystretch}{2em}
\setlength{\parindent}{0pt}
\setlength{\LTpre}{6pt}\setlength{\LTpost}{6pt}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.1}
\renewcommand{\topfraction}{0.95}\renewcommand{\bottomfraction}{0.9}\renewcommand{\textfraction}{0.05}\renewcommand{\floatpagefraction}{0.75}
\makeatletter\setlength{\@fptop}{0pt}\makeatother
\makeatletter\renewcommand{\@makefntext}[1]{\noindent\makebox[1.2em][l]{\@thefnmark}#1}\makeatother
"""

# non-ASCII characters in the draft -> LaTeX (text mode; \ensuremath makes them safe inside math too)
CHARMAP = {
    "\u03c1": r"\ensuremath{\rho}", "\u03b1": r"\ensuremath{\alpha}", "\u2264": r"\ensuremath{\leq}", "\u2265": r"\ensuremath{\geq}",
    "\u2032": r"\ensuremath{'}", "\u2192": r"\ensuremath{\rightarrow}", "\u2212": r"\ensuremath{-}", "\u00d7": r"\ensuremath{\times}",
    "\u2208": r"\ensuremath{\in}", "\u2016": r"\ensuremath{\|}", "\u2248": r"\ensuremath{\approx}", "\u2026": r"\ldots{}",
    "\u2206": r"\ensuremath{\Delta}", "\u0394": r"\ensuremath{\Delta}",
    "\u00a7": r"\S{}",
    "\u0107": r"\'c", "\u00e9": r"\'e", "\u00fc": r'\"u', "\u00f6": r'\"o', "\u00e4": r'\"a', "\u00e8": r"\`e", "\u00ed": r"\'i",
    "\u00f3": r"\'o", "\u00fa": r"\'u", "\u00f1": r"\~n", "\u00e0": r"\`a", "\u00a0": "~",
}


def prepare_markdown(md):
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    yaml, body = m.group(1), md[m.end():]
    meta = {k: v for k, v in re.findall(r'^(\w[\w-]*): "?(.*?)"?$', yaml, re.M)}
    m = re.search(r"::: \{\.abstract\}\n\*\*Abstract\.\*\* (.*?)\n:::\n", body, re.S)
    abstract = m.group(1)
    body = body[:m.start()] + body[m.end():]
    out, appendix = [], False
    for line in body.split("\n"):
        if line.startswith("# References"):
            out.append("\nBIBLIOGRAPHYMARKER\n"); continue
        h = re.match(r"^(#{1,3}) (.*)$", line)
        if h:
            level, text = h.groups()
            if re.match(r"^Appendix [A-Z] \u2014 ", text):
                if not appendix:
                    out.append("\nAPPENDIXMARKER\n"); appendix = True
                text = re.sub(r"^Appendix [A-Z] \u2014 ", "", text)
            elif re.match(r"^[A-Z]\.\d+ ", text):
                text = re.sub(r"^[A-Z]\.\d+ ", "", text)
            elif re.match(r"^\d+(\.\d+)? ", text):
                text = re.sub(r"^\d+(\.\d+)? ", "", text)
            elif text.startswith("Acknowledgements"):
                text = text + " {-}"
            line = f"{level} {text}"
        out.append(line)
    body = "\n".join(out)
    body = re.sub(r"\]\(build/(F[A0-9]+)\.png\)", r"](figures/\1.pdf)", body)
    # bare URLs -> autolinks (so pandoc emits \url{})
    body = re.sub(r"(?<![<(\[`])(https?://[^\s)>\]`]+)", r"<\1>", body)
    return meta, abstract, body


def pandoc(md_text, extra=()):
    r = subprocess.run(["pandoc", "-f", "markdown", "-t", "latex", "--natbib", "--top-level-division=section", "--wrap=none", *extra],
                       input=md_text, text=True, capture_output=True, check=True)
    return r.stdout


def map_chars(tex):
    tex = re.sub(r"(\w)\u0302", r"\\ensuremath{\\hat{\1}}", tex)  # combining hat (v̂)
    for ch, rep in CHARMAP.items():
        tex = tex.replace(ch, rep)
    left = sorted({c for c in tex if ord(c) > 126 and c not in "\u2014\u2013\u2019\u2018\u201c\u201d\u00e9\u00fc\u00f6\u00e4\u0107\u00e0\u00e8\u00ed\u00f3\u00fa\u00f1\u00a0"})
    if left:
        print("WARNING: unmapped non-ASCII characters left in the LaTeX:", [f"U+{ord(c):04X} {c!r}" for c in left])
    return tex


def strip_bib_notes(src, dst):
    s = src.read_text()
    out, i = [], 0
    pat = re.compile(r",\s*\n\s*note\s*=\s*\{")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); break
        out.append(s[i:m.start()])
        j, depth = m.end(), 1
        while depth:
            j += 1
            depth += {"{": 1, "}": -1}.get(s[j - 1], 0)
        i = j
    dst.write_text("".join(out))
    n = len(re.findall(r"^@", "".join(out), re.M))
    assert not re.search(r"^\s*note\s*=", "".join(out), re.M), "a note field survived"
    return n


def main():
    OUT.mkdir(exist_ok=True); FIGS.mkdir(exist_ok=True)
    meta, abstract_md, body_md = prepare_markdown(SRC.read_text())
    abstract = map_chars(pandoc(abstract_md)).strip()
    body = pandoc(body_md)
    body = map_chars(body)
    body = body.replace("BIBLIOGRAPHYMARKER", r"\bibliographystyle{plainnat}" + "\n" + r"\bibliography{references}")
    body = body.replace("APPENDIXMARKER", r"\appendix")
    body = body.replace(r"\begin{figure}", r"\begin{figure}[htbp]")
    def table_font(m):
        ncol = m.group(0).count(r"\real{")
        size = r"\scriptsize\setlength{\tabcolsep}{1.5pt}" if ncol > 7 else r"\footnotesize"
        wide = ncol >= 15  # a table this wide goes on a landscape page (pdflscape), where \columnwidth is the long side
        return ("\\begin{landscape}" if wide else "") + "{" + size + m.group(0)
    body = re.sub(r"\\begin\{longtable\}\[\]\{@\{\}.*?@\{\}\}", table_font, body, flags=re.S)
    # close each table's group, and the landscape environment for the wide ones
    out, pos = [], 0
    for m in re.finditer(r"\\end\{longtable\}", body):
        start = body.rfind("\\begin{landscape}", pos, m.start()); start2 = body.rfind("\\begin{longtable}", pos, m.start())
        wide = start != -1 and start > body.rfind("\\end{landscape}", pos, m.start()) and start < start2
        out.append(body[pos:m.end()] + "}" + ("\\end{landscape}" if wide else "")); pos = m.end()
    out.append(body[pos:]); body = "".join(out)
    # hash prefixes and commits inside \texttt: a break opportunity every four hex characters
    body = re.sub(r"\\texttt\{([0-9a-f]{8,})", lambda m: "\\texttt{" + re.sub(r"([0-9a-f]{4})(?=[0-9a-f])", r"\1\\allowbreak{}", m.group(1)), body)
    body = re.sub(r"\\texttt\{((?:[^{}]|\{[^{}]*\})*)\}", lambda m: "\\texttt{" + re.sub(r"(/|\\_|\.|-)", r"\1\\allowbreak{}", m.group(1)) + "}", body)
    body = re.sub(r"\\includegraphics\[([^\]]*)\]", lambda m: r"\includegraphics[" + re.sub(r"height=\\textheight,?", "", m.group(1)).rstrip(",") + ",keepaspectratio]", body)
    author = meta["author"]
    m = re.match(r"(.*?) \((.*?); (.*?)\)$", author)
    author_tex = (f"{m.group(1)}\\\\ {m.group(2)}\\\\ \\texttt{{{m.group(3)}}}" if m else author)
    tex = (PREAMBLE + "\n" + f"\\title{{{meta['title']}}}\n\\author{{{author_tex}}}\n\\date{{{re.sub(r'(https?://\\S+)', r'\\\\url{\\1}', meta['date'])}}}\n\n"
           + "\\begin{document}\n\\maketitle\n\n\\begin{abstract}\n" + abstract + "\n\\end{abstract}\n\n" + body + "\n\\end{document}\n")
    (OUT / "main.tex").write_text(tex)
    n_bib = strip_bib_notes(PAPER / "references.bib", OUT / "references.bib")
    for p in sorted(BUILD.glob("F*.pdf")):
        if re.fullmatch(r"F[A0-9]+\.pdf", p.name):
            shutil.copy(p, FIGS / p.name)
    n_figs = len(list(FIGS.glob("*.pdf")))
    cites = sorted(set(re.findall(r"\\cite[pt]\{([^}]*)\}", tex)))
    keys = sorted({k.strip() for c in cites for k in c.split(",")})
    bibkeys = set(re.findall(r"^@\w+\{(\w+),", (OUT / "references.bib").read_text(), re.M))
    missing = [k for k in keys if k not in bibkeys]
    assert not missing, f"citation keys without entries: {missing}"
    print(f"main.tex written: {len(tex.splitlines())} lines; {len(keys)} cited keys (all in references.bib, {n_bib} entries); {n_figs} figure PDFs; "
          f"{tex.count(chr(92)+'begin{longtable}')} tables; {tex.count(chr(92)+'begin{figure}')} figures")
    if not COMPILE:
        return
    log = OUT / "tectonic.log"
    r = subprocess.run(["tectonic", "--keep-logs", "--keep-intermediates", "main.tex"], cwd=OUT, capture_output=True, text=True)
    log.write_text(r.stdout + "\n" + r.stderr)
    if r.returncode != 0:
        print("TECTONIC FAILED; last lines:\n" + "\n".join((r.stdout + r.stderr).splitlines()[-40:])); sys.exit(1)
    warn = [l for l in (r.stdout + r.stderr).splitlines() if "warning" in l.lower()]
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", "main.pdf"], cwd=OUT, capture_output=True, text=True).stdout).group(1))
    ref_page = None
    for i in range(1, pages + 1):
        t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "main.pdf", "-"], cwd=OUT, capture_output=True, text=True).stdout
        if re.search(r"^References\s*$", t, re.M):
            ref_page = i; break
    counts = {"full_pdf_pages": pages, "references_start_page": ref_page, "main_text_pages_before_references": (ref_page - 1) if ref_page else None,
              "overfull_hbox_lines": sum(1 for l in (OUT / "main.log").read_text(errors="ignore").splitlines() if l.startswith("Overfull \\hbox")) if (OUT / "main.log").exists() else None,
              "engine": "Tectonic " + subprocess.run(["tectonic", "--version"], capture_output=True, text=True).stdout.strip().split()[-1]}
    (OUT / "page_count_latex.json").write_text(json.dumps(counts, indent=1))
    print(json.dumps(counts), f"| {len(warn)} warning lines (tectonic.log)")


if __name__ == "__main__":
    main()
