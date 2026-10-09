"""Build the public snapshot repository of this project (Stage 9 decision (a), 2026-10-06).

Copies every git-tracked file at HEAD except the session notes (`RESEARCH_HANDOFF.md`), the project's Claude skills
(`.claude/`) and the page-count measurement variants (`research/paper/build/m_*`), generalises the one absolute local path
to `<repository>`, scans for secrets, adds LICENSE (MIT, code), LICENSE-TEXT (CC BY 4.0, text and figures), README.md
and CITATION.cff, and writes SNAPSHOT_MANIFEST.json (source commit, file count, SHA-256 of every file). Git-ignored data,
model weights, generated corpora and literature PDFs are never in the tree, so they cannot be copied.
Run: python3 tools/make_public_snapshot.py DEST [--git]   (--git initialises a repository in DEST with one commit)
"""
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(sys.argv[1]).resolve()
EXCLUDE = ("RESEARCH_HANDOFF.md", ".claude/", "research/paper/build/m_")
LOCAL_PATH = "<repository>"
SECRET = re.compile(r"hf_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH) PRIVATE KEY")
PUBLIC_URL = "https://github.com/SHENSHENZYC/activation-watermark-security"
TITLE = "A Security Analysis of an Activation-Steering LLM Watermark: Key Recovery, Forgery, Scrubbing and Keyed Defences"

README = f"""# {TITLE}

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
"""

MIT = """MIT License

Copyright (c) 2026 Yichen Zhao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

CCBY = """The text of this repository (the protocols, reports, gates, the decision log and the paper's sources) and its figures
are licensed under the Creative Commons Attribution 4.0 International licence (CC BY 4.0):
https://creativecommons.org/licenses/by/4.0/

Copyright (c) 2026 Yichen Zhao. Attribution: cite the paper (CITATION.cff) and link to this repository.
The code is under the MIT licence (LICENSE). Third-party materials are not included; see README.md.
"""

CFF = f"""cff-version: 1.2.0
message: "If you use this repository, please cite the paper."
title: "{TITLE}"
authors:
  - family-names: Zhao
    given-names: Yichen
    affiliation: Independent researcher
    email: alexyczhao@gmail.com
year: 2026
type: software
repository-code: "{PUBLIC_URL}"
license: MIT
preferred-citation:
  type: article
  title: "{TITLE}"
  authors:
    - family-names: Zhao
      given-names: Yichen
  year: 2026
  journal: "arXiv preprint"
  notes: "arXiv identifier to be added at posting; primary category cs.CR."
"""


def main():
    use_git = "--git" in sys.argv
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    files = [f for f in subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\0") if f]
    existing_git = DEST / ".git"
    keep_git = use_git and existing_git.is_dir()
    if DEST.exists():
        if keep_git:  # update mode: keep the snapshot repository's history and add a commit
            for child in DEST.iterdir():
                if child.name != ".git":
                    shutil.rmtree(child) if child.is_dir() else child.unlink()
        else:
            shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)
    manifest, generalised, excluded = {}, [], []
    for f in files:
        if f.startswith(EXCLUDE):
            excluded.append(f); continue
        src, dst = ROOT / f, DEST / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        if text is not None:
            if LOCAL_PATH in text:
                text = text.replace(LOCAL_PATH, "<repository>"); generalised.append(f); data = text.encode()
            m = SECRET.search(text)
            assert not m, f"secret-like string in {f}: {m.group(0)[:12]}…"
        dst.write_bytes(data)
        manifest[f] = hashlib.sha256(data).hexdigest()
    for name, content in [("LICENSE", MIT), ("LICENSE-TEXT", CCBY), ("README.md", README), ("CITATION.cff", CFF)]:
        (DEST / name).write_text(content); manifest[name] = hashlib.sha256(content.encode()).hexdigest()
    gi = (ROOT / ".gitignore").read_text()
    (DEST / ".gitignore").write_text(gi); manifest[".gitignore"] = hashlib.sha256(gi.encode()).hexdigest()
    # nothing from a git-ignored folder may be present
    assert not any("/data/" in f or "/raw/" in f or "/pdfs/" in f or f.endswith((".safetensors", ".bin", ".pt", ".npz")) for f in manifest), "ignored material in snapshot"
    out = {"source_commit": head, "source_dirty": bool(dirty), "built_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "files": len(manifest), "excluded": excluded, "generalised_local_path_in": generalised, "sha256": manifest}
    (DEST / "SNAPSHOT_MANIFEST.json").write_text(json.dumps(out, indent=1))
    size_mb = sum((DEST / f).stat().st_size for f in manifest) / 1e6
    print(f"snapshot at {DEST}: {len(manifest)} files, {size_mb:.1f} MB, from {head[:7]}{' (DIRTY TREE)' if dirty else ''}; excluded {len(excluded)}; generalised path in {generalised}")
    if use_git:
        if not keep_git:
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=DEST, check=True)
        subprocess.run(["git", "add", "-A"], cwd=DEST, check=True)
        subprocess.run(["git", "commit", "-q", "-m", f"Public snapshot of the research repository at {head[:7]} ({out['built_utc']})"], cwd=DEST, check=True)
        print("git repository initialised with one commit; push with: git -C", DEST, "remote add origin", PUBLIC_URL + ".git", "&& git -C", DEST, "push -u origin main")


if __name__ == "__main__":
    main()
