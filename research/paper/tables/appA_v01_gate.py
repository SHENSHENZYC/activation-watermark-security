"""App. A — Study 1 v0.1's gate record: the training-free cosine detector's true-positive rate on the four tuning keys at the
published α = 5 and at α = 10, from the runner's stop state (research/outputs/study1_v0.1/qwen/G1_STATE.json, copied
unchanged from the run's data folder with its hash). Registers the values App. A quotes; writes build/values_appA_v01.json.
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("appA_v01")
rec = C.load(C.OUT / "study1_v0.1" / "qwen" / "G1_STATE.json")
src = C.ROOT / rec["source_path"]
if src.exists():
    assert hashlib.sha256(src.read_bytes()).hexdigest() == rec["source_sha256"], "the copied state differs from the run's file"
st = rec["state"]
assert st["G1_alpha5_pass"] is False and st["G1_alpha10_pass"] is False and st["stop"].startswith("G1 failed")
assert len(st["G1_alpha5_tprs"]) == 4 and len(st["G1_alpha10_tprs"]) == 4
V.set("v01_G1_a5_tpr_max", C.pct(max(st["G1_alpha5_tprs"]), 0))
V.set("v01_G1_a10_tpr_max", C.pct(max(st["G1_alpha10_tprs"]), 0))
V.set("v01_G1_n_tuning_keys", len(st["G1_alpha5_tprs"]))
V.set("v01_G1_stop", st["stop"])
p = V.save()
print("App. A v0.1 gate values written:", p.name, len(V.d))
