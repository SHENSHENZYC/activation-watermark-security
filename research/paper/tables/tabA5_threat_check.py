"""TA5 — the Study 5 threat check on the tuning keys (Appendix C): Route A′ (the gradient-mean estimator with the layer
search) beside Route A (the activation-mean estimator) and the gradient estimate at the true layer, against the budget
n at three strengths. Reads research/outputs/study5_threat_v0.1/results.json; re-computes every median from the per-key
records and the pre-set verdict from the reading rule; writes build/tabA5.md and build/values_tabA5.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tabA5")
res = C.load(C.OUT / "study5_threat_v0.1" / "results.json")
val = C.load(C.OUT / "study5_threat_v0.1" / "VALIDATION.json")
assert val.get("all_pass") is True, "threat-check validation not all passed"
assert res["guard"]["spec_sha256"] == res["run_guard"]["spec_sha256"]
NG = [str(n) for n in res["n_grid"]]
LEVELS = sorted(res["levels"], key=float)
KEYS = sorted(res["levels"][LEVELS[0]]["per_key"])


def val_of(d):
    """A per-key or median record for one estimator: {'cos': .., 'support': ..} or similar."""
    if isinstance(d, dict):
        for k in ("cos", "cosine"):
            if k in d:
                return float(d[k]), d
        return float(list(d.values())[0]), d
    return float(d), {}


rows, realized = [], {}
for rho in LEVELS:
    L = res["levels"][rho]
    for n in NG:
        med = L["median"][n]
        # re-compute the medians over the keys
        for est in ("grad", "act", "grad_layer14"):
            pk = [val_of(L["per_key"][k][n][est])[0] for k in KEYS]
            m, _ = val_of(med[est])
            assert abs(float(np.median(pk)) - m) < 1e-9, (rho, n, est)
        g, gd = val_of(med["grad"])
        a, _ = val_of(med["act"])
        g14, _ = val_of(med["grad_layer14"])
        sup = gd.get("support", gd.get("support_hit"))
        realized[(rho, n)] = g
        rows.append([rho, n, C.f3(g), C.f2(sup) if sup is not None else "—", med["layer_hits_grad"], C.f3(a), med["layer_hits_act"], C.f3(g14)])
        t = rho.replace(".", "")
        V.set(f"threat_{t}_n{n}_cos_grad", C.f3(g))
        V.set(f"threat_{t}_n{n}_cos_act", C.f3(a))
        V.set(f"threat_{t}_n{n}_layer_hits_grad", med["layer_hits_grad"])
        V.set(f"threat_{t}_n{n}_cos_grad14", C.f3(g14))
        V.set(f"threat_{t}_n{n}_cos_grad_2dp", C.f2(g))
    # per key at the largest n
    nmax = NG[-1]
    V.set(f"threat_{rho.replace('.', '')}_perkey_n{nmax}", "; ".join(f"{k}: {C.f2(val_of(L['per_key'][k][nmax]['grad'])[0])}" for k in KEYS))

# the pre-set reading: the threat is real if the median cos ≥ bar at some n ≤ n_max at ρ = 0.50 or 0.70
rd = res["reading"]
for rho in ("0.5", "0.7"):
    ok = any(realized[(rho, n)] >= rd["bar"] for n in NG if int(n) <= rd["n_max"])
    assert ok == rd["threat_real_at"][rho], rho
assert rd["verdict"] == "threat real"
V.set("threat_verdict", rd["verdict"])
V.set("threat_bar", C.f1(rd["bar"]))
V.set("threat_n_max", rd["n_max"])
V.set("threat_n_keys", len(KEYS))
V.set("threat_keys", f"{KEYS[0]}–{KEYS[-1]}")
V.set("threat_n_grid", ", ".join(NG))
V.set("threat_levels", ", ".join(LEVELS))
V.set("threat_act_cos_max", C.f3(max(val_of(res["levels"][r]["median"][n]["act"])[0] for r in LEVELS for n in NG)))

C.write_table("TA5", ["ρ", "n (texts)", "Route A′ (gradients, layer search): median cos(v̂, v)", "support hit (of 4)", "layer = 14 (keys of 4)",
                      "Route A (activations): median cos", "layer = 14 (keys of 4)", "gradients at the true layer: median cos"], rows,
              "The threat check (tuning keys 9001–9004; 100 observed texts per key and strength): the gradient-mean estimator recovers the fixed key where the activation-mean estimator does not",
              ["Medians over the four tuning keys. Pre-set reading: the threat is real if the median cosine is at least 0.5 at some n ≤ 100 at ρ = 0.50 or 0.70 (verdict: threat real). Everything else in the table is descriptive. These are design inputs for Study 5, not study results."])
p = V.save()
print("TA5 written; values:", p.name, len(V.d))
