"""Study 3 runner (STUDY3_PROTOCOL_v0.1.md). Refuses to run unless PRE_RUN_LOCK.json matches the hashes of the
protocol, the code and the 562 reused Study 1 files.

Phases, checkpointed under research/study3/data/ (git-ignored):
  F  per text: the gradient g and activation mean a at layer 14 (the pilot's text_features, unchanged), for the
     shared sets (pool F reference, pool A unwatermarked, pool A human) and every key-level's texts
  R  rules and secondaries (common_s3.analyse) -> research/outputs/study3_v0.1/results.json
Run: .venv/bin/python research/study3/run_s3.py --phase F|R|all
Lock (only after Yichen approves): .venv/bin/python research/study3/run_s3.py --phase lock --approved-by "..."
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time

import numpy as np

import common_s3 as S
from common_s3 import C2, C4, PP, core

LOCK = S.OUT / "PRE_RUN_LOCK.json"
CODE = [S.HERE / f for f in ("common_s3.py", "run_s3.py", "validate_s3.py")] + [
    S.ROOT / "research" / "study3_pilot" / "power_pilot.py"] + [
    S.ROOT / "research" / "study1_v04" / f for f in ("common4.py", "attack4.py", "run_v04.py")] + [
    S.ROOT / "research" / "study1_v03" / f for f in ("common3.py", "attack3.py")] + [
    S.ROOT / "research" / "study1_v02" / f for f in ("common.py", "detect2.py", "attack2.py")] + [
    S.ROOT / "research" / "study1" / f for f in ("core.py", "attack.py")]
INPUTS = [S.ROOT / "research" / "outputs" / p for p in (
    "study3_v0.1/INPUT_VALIDATION.json", "study3_pilot_v0.1/results.json", "study3_pilot_v0.1/VALIDATION.json",
    "study3_pilot_v0.1/posthoc_diagnostics.json", "study1_v0.4/PRE_RUN_LOCK.json", "study1_v0.4/results.json",
    "study1_v0.3/PRE_RUN_LOCK.json", "study1_v0.2/PRE_RUN_LOCK.json")] + [
    S.ROOT / "research" / "stage4" / "prompts.py"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def sha_texts(texts):
    return hashlib.sha256(json.dumps(texts).encode()).hexdigest()


def rel(p):
    return str(p.relative_to(S.ROOT))


def check_lock():
    if not LOCK.exists():
        raise SystemExit("refused: no PRE_RUN_LOCK.json (the protocol is not locked)")
    lock = json.loads(LOCK.read_text())
    assert lock["protocol_sha256"] == sha(S.PROTOCOL), "protocol changed since lock"
    for p in CODE:
        assert lock["code_sha256"][rel(p)] == sha(p), f"{p.name} changed since lock"
    for p in S.reused_files():
        assert lock["reused_sha256"][rel(p)] == sha(p), f"reused file {p.name} changed since lock"
    assert lock["human_texts_sha256"] == sha_texts(S.human_texts()), "human texts changed since lock"
    return lock


# ---------------------------------------------------------------- lock (written once, on Yichen's approval)
def write_lock(approved_by):
    assert "**Status: LOCKED" in S.PROTOCOL.read_text(), "set the protocol's status line to LOCKED before hashing"
    val = json.loads((S.OUT / "INPUT_VALIDATION.json").read_text())
    assert val["all_pass"], "input validation has not passed"
    assert not S.DATA.exists() or not any(S.DATA.glob("*.npz")), "outcomes exist: study features already computed"
    assert not (S.OUT / "results.json").exists(), "outcomes exist: results.json"
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=S.ROOT, capture_output=True, text=True).stdout
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=S.ROOT, capture_output=True, text=True).stdout.strip()
    lock04 = json.loads((S.ROOT / "research/outputs/study1_v0.4/PRE_RUN_LOCK.json").read_text())
    lock = {
        "study": "Study 3 v0.1: exact key tests (power, per-key calibration, resistance to Study 1's forgeries)",
        "protocol": S.PROTOCOL.name, "protocol_sha256": sha(S.PROTOCOL),
        "code_sha256": {rel(p): sha(p) for p in CODE},
        "reused_sha256": {rel(p): sha(p) for p in S.reused_files()},
        "human_texts_sha256": sha_texts(S.human_texts()),
        "input_sha256": {rel(p): sha(p) for p in INPUTS},
        "study1_v04_lock_reused_overlap_equal": val["checks"]["1_reused_files"]["overlap_with_study1_locks_equal"],
        "design": {"primary": S.PRIMARY, "secondary": S.SECONDARY, "alpha": S.ALPHA, "M": 999, "alpha2": S.ALPHA2,
                   "M2": S.M2, "levels": S.LEVELS, "keys": S.KEYS, "G1_range_pct": list(S.G1_RANGE),
                   "G2_max_pct": S.G2_MAX, "min_calibrated_keys": S.MIN_CAL, "P1_min_pct": S.P1_MIN,
                   "boot_B": 2000, "boot_seed": S.BOOT_SEED, "pooled_texts": S.POOL, "layer": C2.LAYER,
                   "null_key_seeds": "77,700,000 + j", "reference_set": "v0.2 pool F (S_F_van.json, 200)"},
        "git_commit_before_lock": commit, "uncommitted_changes_at_lock": dirty.strip().splitlines(),
        "locked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "LOCKED before outcomes: no Study 3 feature or statistic on any study-key text exists",
        "approved_by": approved_by, "final": False, "holdout": "not used (sealed)",
        "builds_on": f"Study 1 v0.2-v0.4 texts (v0.4 lock {lock04['locked_utc']}); power pilot v0.1",
    }
    LOCK.write_text(json.dumps(lock, indent=2))
    check_lock()
    print("locked:", lock["locked_utc"], "commit before lock:", commit[:7])


# ---------------------------------------------------------------- phase F
def feature_jobs():
    yield "S_F_van", S.load(S.V02 / "S_F_van.json")
    yield "S_A_van", S.load(S.V02 / "S_A_van.json")
    yield "S_A_human", S.human_texts()
    for rho in S.LEVELS:
        for s in S.KEYS:
            for c in S.cond_names(rho):
                yield f"K_{C4.tag(s, rho)}_{c}", S.load(S.text_file(s, rho, c))


def phase_f():
    S.DATA.mkdir(parents=True, exist_ok=True)
    tok, model = PP.load()
    t0, n_done = time.time(), 0
    for name, texts in feature_jobs():
        f = S.DATA / f"{name}.npz"
        if f.exists():
            continue
        A, G, LL = zip(*(PP.text_features(tok, model, t) for t in texts))
        np.savez(f, A=np.stack(A).astype(np.float16), G=np.stack(G).astype(np.float32), LL=np.array(LL),
                 sha=sha_texts(texts))
        n_done += len(texts)
        print(f"F {name}: {len(texts)} texts; {n_done} this session; {time.time() - t0:.0f}s", flush=True)
    print("F done", flush=True)


# ---------------------------------------------------------------- phase R
def phase_r():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(core.MODEL_ID, revision=core.REVISION)
    for name, texts in feature_jobs():  # features were computed from exactly these texts
        assert str(np.load(S.DATA / f"{name}.npz")["sha"]) == sha_texts(texts), f"texts changed since F: {name}"
    t0 = time.time()
    res = S.analyse(S.StudySrc(), tok)
    miss = S.missing_fields(res, S.LEVELS, S.cond_names)
    assert not miss, f"missing result fields: {miss[:10]}"
    res["elapsed_R_s"] = time.time() - t0
    (S.OUT / "results.json").write_text(json.dumps(res, indent=2))
    P = res[S.PRIMARY]
    print(json.dumps({"G1": P["G1"], "G2": {k: P["G2"][k] for k in ("n_calibrated", "stop")},
                      "levels": {r: {"P1": L["P1"]["pass"], "E1": L["E1"]["verdict"], "X1": L.get("X1"),
                                     "X3": L["X3_fluent_generic_steering_suffices"]}
                                 for r, L in P["levels"].items()}}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["F", "R", "all", "lock"], required=True)
    ap.add_argument("--approved-by")
    a = ap.parse_args()
    if a.phase == "lock":
        return write_lock(a.approved_by or sys.exit("--approved-by is required"))
    lock = check_lock()
    t0 = time.time()
    if a.phase in ("F", "all"):
        phase_f()
    if a.phase in ("R", "all"):
        phase_r()
        check_lock()
        (S.OUT / "RUN_MANIFEST.json").write_text(json.dumps(
            {"lock_utc": lock["locked_utc"], "phase": a.phase, "seconds": time.time() - t0,
             "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=2))


if __name__ == "__main__":
    main()
