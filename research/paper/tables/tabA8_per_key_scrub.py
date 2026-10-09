"""TA8 — per-key scrub success (Appendix D): keys 1001–1008 for each strength and method (P-Qwen, P-Phi, the 5% edits
E-true, E-est, E-rand), with detection before scrubbing per key; the count of keys at or above 50% re-counted and
asserted against the locked file. Reads study2_v0.1/results.json (percent units); writes build/TA8.md and
build/values_tabA8.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA8")
res = C.load(C.OUT / "study2_v0.1" / "results.json")
assert res["dry"] is False
METHODS = [("P1", "detected before scrubbing (unscrubbed originals)", "detected_before"), ("S1_qwen", "P-Qwen success", "success"), ("S1_phi", "P-Phi success", "success"),
           ("E-true 0.05", "E-true 5% success", "success"), ("E-est 0.05", "E-est 5% success", "success"), ("E-rand 0.05", "E-rand 5% success", "success")]
rows = []
for rho in C.LEVELS4:
    L, t = res["levels"][rho], C.tag(rho)
    for m, lab, fld in METHODS:
        d = L[m][fld]
        pk = C.chk(d)
        ge = sum(v >= 50 for v in pk)
        assert ge == d["keys_ge_50"], (rho, m, ge, d["keys_ge_50"])
        if m in ("S1_qwen", "S1_phi"):
            assert ge == L[m]["keys_success_ge_50"]
        rows.append([C.rho_lab(rho), lab] + [f"{v:.0f}" for v in pk] + [C.f1(d["median"]), f"{ge}"])
        short = m.replace(" 0.05", "").replace("-", "").replace("_", "")
        V.set(f"ta8_{short}_{t}_min", f"{min(pk):.0f}")
        V.set(f"ta8_{short}_{t}_max", f"{max(pk):.0f}")
        V.set(f"ta8_{short}_{t}_keys_ge_50", ge)
V.set("ta8_key1002_07_detected_before", f"{C.chk(res['levels']['0.7']['P1']['detected_before'])[1]:.0f}")
V.set("ta8_key1002_07_Erand", f"{C.chk(res['levels']['0.7']['E-rand 0.05']['success'])[1]:.0f}")
V.set("ta8_key1002_07_Pqwen", f"{C.chk(res['levels']['0.7']['S1_qwen']['success'])[1]:.0f}")
V.set("ta8_key1002_07_Etrue", f"{C.chk(res['levels']['0.7']['E-true 0.05']['success'])[1]:.0f}")
C.write_table("TA8", ["ρ", "reading"] + [str(k) for k in C.KEYS] + ["median", "keys ≥ 50% (of 8)"], rows,
              "Study 2: per-key detection before scrubbing and per-key scrub success (%) by method, 100 texts per key and strength",
              ["Success: not attributed by the exact test at p ≤ 0.01 and all four quality conditions pass (perplexity, seq-rep-4, length, embedding similarity against the "
               "owner's human-text bars). Every key is calibrated under both paraphrasers (Table TA12), so every key counts; the verdicts (Table T5) use the median with its "
               "cluster-bootstrap interval."])
p = V.save()
print("TA8 written; values:", p.name, len(V.d))
