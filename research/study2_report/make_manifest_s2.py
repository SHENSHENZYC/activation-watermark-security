"""Write research/outputs/study2_v0.1/RUN_MANIFEST.json after the Study 2 run (no outcome content).

Records each phase's start (given on the command line, as noted when the phase was started) and end (the phase's
"complete" line in run.log; for analyse, results.json's modification time), the lock re-check after the run, the git
commit, the SHA-256 of results.json and run.log, the number of data files, and any deviations (given).
Run: .venv/bin/python research/study2_report/make_manifest_s2.py --start para=2026-10-01T16:23:09Z --start edits=...
     --start score=... --start analyse=... [--deviation "text"]...
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "study2"))
import run_s2  # noqa: E402

DATA, OUT = ROOT / "research" / "study2" / "data", ROOT / "research" / "outputs" / "study2_v0.1"
CT = ZoneInfo("America/Chicago")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def utc(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


ap = argparse.ArgumentParser()
ap.add_argument("--start", action="append", required=True, help="phase=YYYY-MM-DDTHH:MM:SSZ")
ap.add_argument("--deviation", action="append", default=[])
a = ap.parse_args()
starts = dict(x.split("=", 1) for x in a.start)
log = (DATA / "run.log").read_text()
ends = {m.group(1): m.group(2) for m in re.finditer(r"phase (\w+) complete \((\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\)", log)}
ends = {k: v.replace(" ", "T") + "Z" for k, v in ends.items()}
res = OUT / "results.json"
ends["analyse"] = dt.datetime.fromtimestamp(res.stat().st_mtime, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
phases = {}
for ph in ("para", "edits", "score", "analyse"):
    s, e = utc(starts[ph]), utc(ends[ph])
    phases[ph] = {"start_utc": s.strftime("%Y-%m-%d %H:%M:%S"), "end_utc": e.strftime("%Y-%m-%d %H:%M:%S"),
                  "start_ct": s.astimezone(CT).strftime("%Y-%m-%d %H:%M:%S"), "end_ct": e.astimezone(CT).strftime("%Y-%m-%d %H:%M:%S"),
                  "ct_label": s.astimezone(CT).strftime("%Z"), "seconds": (e - s).total_seconds()}
L = run_s2.check_lock()                       # exits ("refused") if anything locked has changed
man = {"study": "Study 2 v0.1", "protocol_sha256": L["protocol_sha256"], "lock_rechecked_after_run": True,
       "locked_utc": L.get("locked_utc"), "final": L.get("final"),
       "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
       "phases": phases, "total_seconds": sum(p["seconds"] for p in phases.values()),
       "results_sha256": sha(res), "run_log_sha256": sha(DATA / "run.log"),
       "n_data_files": sum(1 for _ in DATA.iterdir()), "deviations": a.deviation or ["none"],
       "projected_hours": 24.3}
(OUT / "RUN_MANIFEST.json").write_text(json.dumps(man, indent=2))
print(json.dumps(man, indent=2))
