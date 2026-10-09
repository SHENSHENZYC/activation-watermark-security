"""Write outputs/study2_v0.1/PRE_RUN_LOCK.json (run only after Yichen approves the lock and the protocol's status line
says LOCKED), then run tamper tests: a byte appended to the protocol, to a code file and to a reused file must each make
run_s2.check_lock() refuse; each file is restored byte for byte and the lock must pass again.
Run: .venv/bin/python research/study2/lock_s2.py
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common_s2 as S  # noqa: E402
import run_s2 as R  # noqa: E402

ROOT = S.ROOT


def main():
    assert "**Status: LOCKED" in S.PROTOCOL.read_text(), "set the protocol's status line to LOCKED (and commit) first"
    assert not (S.DATA.exists() and any(S.DATA.iterdir())), "outcomes may exist: research/study2/data is not empty"
    assert not (S.OUT / "results.json").exists(), "outcomes exist: results.json"
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    src = S.Src()
    inputs = [S.OUT / "INPUT_VALIDATION.json", ROOT / "research/outputs/study2_pilot_v0.1/results.json",
              ROOT / "research/outputs/study2_pilot_v0.2/results.json", ROOT / "research/outputs/study2_pilot_v0.1/VALIDATION.json",
              ROOT / "research/outputs/study2_pilot_v0.2/VALIDATION.json", ROOT / "research/outputs/study3_v0.1/PRE_RUN_LOCK.json",
              ROOT / "research/outputs/study3_v0.1/results.json", ROOT / "research/stage4/prompts.py",
              ROOT / "research/stage4/outputs/model_manifest_all-mpnet-base-v2.json",
              ROOT / "research/stage4/outputs/model_manifest_phi-3.5-mini-instruct.json",
              ROOT / "research/stage4/outputs/model_manifest_qwen2.5-1.5b-instruct.json"]
    L = {"study": "Study 2 v0.1", "protocol": str(S.PROTOCOL.relative_to(ROOT)), "protocol_sha256": S.hashlib_sha(S.PROTOCOL),
         "code_sha256": {p.name: S.hashlib_sha(p) for p in R.CODE},
         "reused_sha256": {str(p.relative_to(ROOT)): S.hashlib_sha(p) for p in src.reused_files()},
         "input_sha256": {str(p.relative_to(ROOT)): S.hashlib_sha(p) for p in inputs},
         "design": {"keys": S.KEYS, "levels": S.LEVELS, "n_gen": S.N_GEN, "n_phi": S.N_PHI, "n_null": S.N_NULL,
                    "n_ref_c": S.N_REF_C, "alpha": S.ALPHA, "budgets": list(S.BUDGETS), "round": S.ROUND,
                    "primary_budget": S.PRIMARY, "prompt": S.PROMPT, "batch": S.BATCH, "gates": {"G1": list(S.G1_RANGE),
                    "G2_max": S.G2_MAX, "min_calibrated": S.MIN_CAL, "P1_min": S.P1_MIN}, "bar": S.BAR,
                    "boot_seed": S.BOOT_SEED, "seed_para": S.SEED_PARA, "seed_rand": S.SEED_RAND, "fresh0": S.FRESH0},
         "git_commit_before_lock": commit, "uncommitted_changes_at_lock": dirty.splitlines(),
         "locked_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "status": "LOCKED before outcomes",
         "approved_by": "Yichen", "final": False, "holdout": "not used"}
    S.OUT.mkdir(parents=True, exist_ok=True)
    R.LOCK.write_text(json.dumps(L, indent=2))
    R.check_lock()
    tests = {}
    for label, p in (("protocol", S.PROTOCOL), ("code", HERE / "common_s2.py"),
                     ("reused", src.reused_files()[5])):
        orig = p.read_bytes()
        p.write_bytes(orig + b" ")
        try:
            R.check_lock()
            tests[label] = "NOT refused"
        except SystemExit:
            tests[label] = "refused"
        finally:
            p.write_bytes(orig)
    R.check_lock()
    L["tamper_tests"] = tests
    R.LOCK.write_text(json.dumps(L, indent=2))
    print("lock written;", tests, "; check_lock passes after restoring")


if __name__ == "__main__":
    main()
