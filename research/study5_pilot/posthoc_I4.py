"""Post-hoc addendum to the defence pilot: decision 6's check I4 (the per-position test with h = 0 against S4 on the
fixed-key tuning texts), which the FIXED spec omitted by mistake. Inputs only in the pilot's sense (tuning keys; the
calibration texts, already reported in Study 3's pilot). Writes outputs/study5_pilot_v0.1/ADDENDUM_I4.json.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import keyed_core as KC  # noqa: E402
from keyed_core import PP  # noqa: E402

ROOT = HERE.parents[1]
CAL = ROOT / "research" / "repro" / "data" / "qwen"
OUT = ROOT / "research" / "outputs" / "study5_pilot_v0.1"
TUNING = [9001, 9002, 9003, 9004]
LEVELS = [0.35, 0.50]
ALPHA = 0.01


def main():
    ro = np.load(HERE / "data" / "ref_owner.npz")
    owner = KC.KeyedOwner({"mu": ro["mu"], "sd": ro["sd"], "n_positions": int(ro["n"])})
    s3 = json.loads((ROOT / "research/outputs/study3_pilot_v0.1/results.json").read_text())["tpr"]["S4"]
    tok, model = PP.load()
    res = {"note": "decision 6's I4, omitted from DEFENCE_PILOT_SPEC_v0.1.md; run post hoc on the same tuning-key inputs",
           "per_position_h0_detection_pct": {}, "S4_detection_pct_study3_pilot": {}, "within_10_points": {}}
    for rho in LEVELS:
        tag = f"r{int(round(rho * 100)):03d}"
        per = {}
        for s in TUNING:
            texts = json.loads((CAL / f"texts_calib_{tag}_k{s}.json").read_text())
            v = KC.fixed_dir(s)
            p = [owner.pvalue_fixed(KC.position_grads(tok, model, t)[0], v)[0] for t in texts]
            per[str(s)] = 100 * float(np.mean(np.array(p) <= ALPHA))
        med = float(np.median(list(per.values())))
        s4 = s3[str(rho)]
        res["per_position_h0_detection_pct"][str(rho)] = {"per_key": per, "median": med}
        res["S4_detection_pct_study3_pilot"][str(rho)] = {"per_key": s4["per_key"], "median": s4["median"]}
        res["within_10_points"][str(rho)] = abs(med - s4["median"]) <= 10
        print(rho, "per-position h=0 median", med, "| S4 median (Study 3 pilot)", s4["median"], "| per key", per, flush=True)
    res["pass"] = all(res["within_10_points"].values())
    (OUT / "ADDENDUM_I4.json").write_text(json.dumps(res, indent=2))
    print("I4", "PASS" if res["pass"] else "FAIL")


if __name__ == "__main__":
    main()
