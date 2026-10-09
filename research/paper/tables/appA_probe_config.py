"""App. A — the owner's probe as implemented: the hidden widths of the MLP replicated from the scheme's public code
(commit 7c26938, steering_watermark/param.yaml: hidden_dims [2048, 64, 64, 32]), read from the locked
research/study1_v02/detect2.py (its hash is in Study 1 v0.2's PRE_RUN_LOCK.json and asserted here). Writes
build/values_appA_probe.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("appA_probe")
code = C.RESEARCH / "study1_v02" / "detect2.py"
lock = C.load(C.OUT / "study1_v0.2" / "PRE_RUN_LOCK.json")
locked = {Path(k).name: v for k, v in lock["code_sha256"].items()}
assert locked.get("detect2.py") == C.sha256(code), "detect2.py differs from Study 1 v0.2's lock"
hidden = C.const_from_code(code, "HIDDEN")
assert isinstance(hidden, tuple) and len(hidden) == 4
V.set("probe_hidden_dims", ", ".join(str(h) for h in hidden))
V.set("probe_n_hidden", len(hidden))
V.set("probe_last_hidden", hidden[-1])
p = V.save()
print("probe config registered:", p.name, V.d)
