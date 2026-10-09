"""Write research/outputs/study5_v0.1/RUN_MANIFEST.json after the Study 5 run, from the run log's markers (no outcome content).

run_s5.py writes `[YYYY-MM-DD HH:MM:SS UTC] start phases XYZ (locked)` when a job starts and `[...] phase X complete`
when a phase ends. A phase starts at its job's start marker if it is the job's first phase, otherwise when the previous
phase of that job completed; if a phase appears in several jobs (a resume after a stop), its start is the earliest marker
and its end the first completion after that start. Also records the lock re-check after the run, the git commit, the
SHA-256 of results.json and run.log, the data-file count, the projection and any deviations (given).
Run: .venv/bin/python research/study5_report/make_manifest_s5.py [--deviation "text"]... [--log PATH --out DIR]
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
CT = ZoneInfo("America/Chicago")
PHASES = {"S": "shared statistics", "K": "keyed arms", "P": "paraphrase", "F": "fixed arm", "R": "rotation", "A": "analysis"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse(log_text):
    ev = []
    for line in log_text.splitlines():
        m = re.match(r"^\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) UTC\] (.*)$", line)
        if m:
            ev.append((dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc), m.group(2)))
    starts, ends = {}, {}
    pending = []                                   # phases of the current job still to run, in order
    for t, msg in ev:
        m = re.match(r"start phases (\w+) \((locked|dry)\)", msg)
        if m:
            pending = list(m.group(1))
            ph = pending[0]
            starts.setdefault(ph, t)
            continue
        m = re.match(r"phase (\w) complete", msg)
        if m:
            ph = m.group(1)
            if ph in starts and ph not in ends and t >= starts[ph]:
                ends[ph] = t
            if pending and pending[0] == ph:
                pending.pop(0)
                if pending:
                    starts.setdefault(pending[0], t)
    return starts, ends


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deviation", action="append", default=[])
    ap.add_argument("--log", default=str(ROOT / "research" / "study5" / "data" / "run.log"))
    ap.add_argument("--out", default=str(ROOT / "research" / "outputs" / "study5_v0.1"))
    ap.add_argument("--projected-hours", type=float, default=26.6)
    ap.add_argument("--no-lock-check", action="store_true", help="fixture test only")
    a = ap.parse_args()
    log, out = Path(a.log), Path(a.out)
    starts, ends = parse(log.read_text())
    phases = {}
    for ph in "SKPFRA":
        if ph not in starts or ph not in ends:
            sys.exit(f"phase {ph}: start or end marker missing (starts {sorted(starts)}, ends {sorted(ends)})")
        s, e = starts[ph], ends[ph]
        phases[ph] = {"name": PHASES[ph], "start_utc": s.strftime("%Y-%m-%d %H:%M:%S"), "end_utc": e.strftime("%Y-%m-%d %H:%M:%S"),
                      "start_ct": s.astimezone(CT).strftime("%Y-%m-%d %H:%M:%S"), "end_ct": e.astimezone(CT).strftime("%Y-%m-%d %H:%M:%S"),
                      "ct_label": s.astimezone(CT).strftime("%Z"), "seconds": (e - s).total_seconds()}
    man = {"study": "Study 5 v0.1", "phases": phases, "total_seconds": sum(p["seconds"] for p in phases.values()),
           "projected_hours": a.projected_hours, "deviations": a.deviation or ["none"],
           "run_log_sha256": sha(log), "n_data_files": sum(1 for _ in log.parent.iterdir()),
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()}
    res = out / "results.json"
    if res.exists():
        man["results_sha256"] = sha(res)
    if not a.no_lock_check:
        sys.path.insert(0, str(ROOT / "research" / "study5"))
        import run_s5  # noqa: E402
        L = run_s5.check_lock()                    # raises if anything locked has changed
        man.update({"lock_rechecked_after_run": True, "protocol_sha256": L["protocol_sha256"], "locked_utc": L.get("locked_utc"), "final": L.get("final")})
    out.mkdir(parents=True, exist_ok=True)
    (out / "RUN_MANIFEST.json").write_text(json.dumps(man, indent=2))
    print(json.dumps(man, indent=2))


if __name__ == "__main__":
    main()
