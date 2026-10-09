"""Shared helpers for the paper's table and figure scripts (research/paper/README.md).

Every script reads locked outputs only, asserts against them, and registers the numbers its table shows under names
that the section drafts quote as [[name]] placeholders (fill_sections.py resolves them). Nothing here computes a new
statistic from raw data; the scripts condense what the studies' locked results.json, lock, validation and manifest
files already hold, and re-count what can be re-counted.
"""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parents[1]                      # the repository
RESEARCH = ROOT / "research"
OUT = RESEARCH / "outputs"
BUILD = PAPER / "build"
BUILD.mkdir(exist_ok=True)


def load(p):
    return json.loads(Path(p).read_text())


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git_commit_exists(h):
    r = subprocess.run(["git", "cat-file", "-t", h], cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == "commit"


def parse_utc(s):
    """Lock and manifest timestamps come in two forms: '2026-09-26T01:26:21Z' and '2026-10-01 16:12:01'."""
    s = s.strip().replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise ValueError(s)


def utc_date(s):
    return parse_utc(s).strftime("%Y-%m-%d")


def utc_stamp(s):
    return parse_utc(s).strftime("%Y-%m-%d %H:%M UTC")


def central(dt):
    """US Central (CDT, UTC-5, until 1 November 2026; CST, UTC-6, afterwards) for Yichen's progress notes."""
    cdt_end = datetime(2026, 11, 1, 7, 0, tzinfo=timezone.utc)
    off, lab = (-5, "CDT") if dt < cdt_end else (-6, "CST")
    return (dt + timedelta(hours=off)).strftime("%H:%M ") + lab


def hours(seconds):
    return seconds / 3600.0


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def pct(x, nd=1):
    """A share in [0, 1] as a percentage string."""
    return f"{100 * x:.{nd}f}"


def pct_ci(d, nd=1):
    """'centre [lo, hi]' from a {median | mean, ci95} summary of shares (the studies summarise per-key means by their
    median over keys; the rotation forgery sets, which have no per-key structure, by their mean)."""
    centre = d["median"] if "median" in d else d["mean"]
    return f"{pct(centre, nd)} [{pct(d['ci95'][0], nd)}, {pct(d['ci95'][1], nd)}]"


def const_from_code(path, name):
    """Read a module-level constant such as `N_GRID = [1, 4, 16]` from a locked code file without importing it."""
    txt = Path(path).read_text()
    m = re.search(rf"^{re.escape(name)}\s*=\s*(.+?)\s*(#.*)?$", txt, re.M)
    if not m:
        raise KeyError(f"{name} not in {path}")
    return eval(m.group(1), {"__builtins__": {}}, {"list": list, "range": range})  # literal lists and numbers only


class Values:
    """The numbers a table script registers for the prose. Each script writes build/values_<tag>.json; names must be
    unique across scripts (fill_sections.py refuses conflicting duplicates)."""

    def __init__(self, tag):
        self.tag, self.d = tag, {}

    def set(self, name, value):
        if name in self.d and self.d[name] != value:
            raise ValueError(f"{name} registered twice with different values: {self.d[name]!r} vs {value!r}")
        self.d[name] = value
        return value

    def save(self):
        p = BUILD / f"values_{self.tag}.json"
        p.write_text(json.dumps(self.d, indent=1, ensure_ascii=False, sort_keys=True))
        return p


def write_table(name, header, rows, caption, notes=None):
    """A Markdown table with its caption and optional notes -> build/<name>.md."""
    lines = [f"**{name} — {caption}**", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        lines.append("| " + " | ".join(str(c) for c in r) + " |")
    if notes:
        lines += ["", *notes]
    p = BUILD / f"{name}.md"
    p.write_text("\n".join(lines) + "\n")
    return p


# ---------------------------------------------------------------- figures (the dataviz skill; the outline's palette, §5)
# Categorical slots of the skill's reference palette (validated 2026-10-05: four coloured series pass every gate; the aqua
# needs relief, i.e. visible labels or a table beside the figure). The probe and the controls are the recessive grey.
INK, MUTED, GRID, CTRL = "#1f1f1e", "#6b6a64", "#e4e3dc", "#52514e"
PAL = {"exact": "#1baf7a", "probe": CTRL, "A": "#2a78d6", "B": "#eb6834",
       "fixed": INK, "h1": "#2a78d6", "h4": "#eb6834", "rot": "#4a3aa7", "ctrl": CTRL,
       "qwen": "#2a78d6", "phi": "#eb6834", "true": "#1baf7a", "est": "#4a3aa7", "rand": CTRL,
       "m_qwen": INK, "m_llama1b": "#2a78d6", "m_llama3b": "#eb6834"}
XLAB_RHO = "watermark strength ρ = ‖v‖ / median activation norm"


def fig_style():
    """Matplotlib with the recessive chrome the dataviz skill asks for (hairline solid grid, no top/right spines)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                         "grid.linewidth": 0.6, "legend.frameon": False, "axes.titlelocation": "left", "axes.titlesize": 9,
                         "axes.titlecolor": INK, "figure.dpi": 100})
    return plt


def save_fig(fig, name):
    p = BUILD / f"{name}.png"
    fig.savefig(p, dpi=200, bbox_inches="tight")
    fig.savefig(BUILD / f"{name}.pdf", bbox_inches="tight")  # vector copy for the LaTeX version (Stage 9)
    return p


def med(xs):
    import numpy as np
    return float(np.median(xs))


# ---------------------------------------------------------------- shared constants and checks (Milestone 15)
KEYS = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008]
LEVELS4 = ["0.25", "0.35", "0.5", "0.7"]
LEVELS3 = ["0.35", "0.5", "0.7"]
LEVELS2 = ["0.35", "0.5"]


def tag(rho):
    """'0.35' -> '035', '0.5' -> '05' (the registered-name convention of the T scripts)."""
    return rho.replace(".", "")


def rho_lab(rho):
    return f"{float(rho):.2f}"


def chk(d, n=8, tol=1e-9):
    """A {per_key, median, ci95} summary: the median must equal the median of the per-key values (list or dict in key
    order) and lie inside its interval. Returns the per-key values as a list."""
    import numpy as np
    pk = d["per_key"]
    vals = [pk[str(k)] for k in KEYS] if isinstance(pk, dict) else list(pk)
    assert len(vals) == n, len(vals)
    assert abs(float(np.median(vals)) - d["median"]) < tol, (d["median"], float(np.median(vals)))
    if d.get("ci95") is not None:
        assert d["ci95"][0] <= d["median"] + tol and d["median"] - tol <= d["ci95"][1]
    return vals


def pct0(x):
    """A share in [0, 1] as a whole-number percentage string (per-key tables)."""
    return f"{100 * x:.0f}"
