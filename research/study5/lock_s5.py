"""Write outputs/study5_v0.1/PRE_RUN_LOCK.json (run only after Yichen approves the lock and the protocol's status line
says LOCKED), then run tamper tests: a byte appended to the protocol, to a code file and to a reused file must each make
run_s5.check_lock() refuse; each file is restored byte for byte and the lock must pass again.
Run: .venv/bin/python research/study5/lock_s5.py
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common_s5 as S  # noqa: E402
import run_s5 as R  # noqa: E402

ROOT = S.ROOT


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert "**Status: LOCKED" in S.PROTOCOL.read_text(), "set the protocol's status line to LOCKED (and commit) first"
    assert not list(S.DATA.glob("K_*")), "outcomes may exist: research/study5/data has K_ files"
    assert not (S.OUT / "results.json").exists(), "outcomes exist: results.json"
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    src = S.Src()
    inputs = [S.OUT / "INPUT_VALIDATION.json", ROOT / "research/outputs/study5_pilot_v0.1/results.json",
              ROOT / "research/outputs/study5_pilot_v0.1/VALIDATION.json", ROOT / "research/outputs/study5_threat_v0.1/results.json",
              ROOT / "research/outputs/study5_threat_v0.1/VALIDATION.json", ROOT / "research/outputs/study2_v0.1/PRE_RUN_LOCK.json",
              ROOT / "research/outputs/study2_v0.1/results.json", ROOT / "research/outputs/study3_v0.1/PRE_RUN_LOCK.json",
              ROOT / "research/outputs/study3_v0.1/results.json", ROOT / "research/stage4/prompts.py",
              ROOT / "research/stage4/outputs/model_manifest_all-mpnet-base-v2.json",
              ROOT / "research/stage4/outputs/model_manifest_qwen2.5-1.5b-instruct.json",
              ROOT / "research/pilot/outputs/model_manifest_qwen2.5-1.5b.json"]
    L = {"study": "Study 5 v0.1", "protocol": str(S.PROTOCOL.relative_to(ROOT)), "protocol_sha256": sha(S.PROTOCOL),
         "code_sha256": {p.name: sha(p) for p in R.CODE},
         "reused_sha256": {str(p.relative_to(ROOT)): sha(p) for p in src.reused_files()},
         "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs if p.exists()},
         "design": {"keys": S.KEYS, "levels": S.LEVELS, "arms": S.ARMS, "n_grid": S.N_GRID, "forge_n": S.FORGE_N, "n_obs": S.N_OBS,
                    "n_gen": S.N_GEN, "n_forge": S.N_FORGE, "n_para": S.N_PARA, "c_min": S.C_MIN, "controls": S.CONTROL, "alpha": S.ALPHA,
                    "gates": {"G1": list(S.G1_RANGE), "G2_max": S.G2_MAX, "min_calibrated": S.MIN_CAL, "P1_min_pct": S.P1_MIN},
                    "materiality": {"D2_points": S.D2_POINTS, "D3_ratio": S.D3_RATIO}, "boot_seed": S.BOOT_SEED, "seed0": S.SEED0,
                    "set_idx0": S.SET_IDX0, "null_secret_seed": S.KC.NULL_SECRET_SEED, "m_null": S.KC.M_NULL},
         "git_commit_before_lock": commit, "uncommitted_changes_at_lock": dirty.splitlines(),
         "locked_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "status": "LOCKED before outcomes",
         "approved_by": "Yichen", "final": False, "holdout": "not used"}
    S.OUT.mkdir(parents=True, exist_ok=True)
    R.LOCK.write_text(json.dumps(L, indent=2, default=str))
    R.check_lock()
    tests = {}
    for label, p in (("protocol", S.PROTOCOL), ("code", HERE / "common_s5.py"), ("reused", src.reused_files()[5])):
        orig = p.read_bytes()
        p.write_bytes(orig + b" ")
        try:
            R.check_lock()
            tests[label] = "NOT refused"
        except AssertionError:
            tests[label] = "refused"
        finally:
            p.write_bytes(orig)
    R.check_lock()
    L["tamper_tests"] = tests
    R.LOCK.write_text(json.dumps(L, indent=2, default=str))
    print("lock written;", tests, "; check_lock passes after restoring")


if __name__ == "__main__":
    main()
