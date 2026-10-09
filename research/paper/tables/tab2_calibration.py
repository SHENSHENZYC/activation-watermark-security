"""T2 — calibration and reproduction (§5.1): per model and strength ρ, the authors' MLP probe's AUROC and the perplexity
ratio at 256 tokens (Llama-3.2-1B, Qwen2.5-1.5B, Llama-3.2-3B), the 512-token points for the first two, the published
α = 5 as a ρ per model with the reproduction pilot's AUROC and perplexity, and the operating-point rule (none found).
Reads calibration_v0.1/results_{qwen,llama}.json, calibration_v0.2/results_{qwen,llama}.json,
calibration_v0.3/results_llama3b.json, repro_v0.1/results_{qwen,llama}.json and addendum_quality_ppl.json; asserts that
operating_point is None in every calibration file and re-derives it from the rule, re-computes the pilot's mean AUROCs
from the per-key records and the α = 5 strengths from the recorded norms, and asserts them; writes build/T2.md and
build/values_tab2.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tab2")
O = C.OUT
MODELS = [("l1b", "Llama-3.2-1B", O / "calibration_v0.1" / "results_llama.json", O / "calibration_v0.2" / "results_llama.json", O / "repro_v0.1" / "results_llama.json", "llama"),
          ("q15", "Qwen2.5-1.5B", O / "calibration_v0.1" / "results_qwen.json", O / "calibration_v0.2" / "results_qwen.json", O / "repro_v0.1" / "results_qwen.json", "qwen"),
          ("l3b", "Llama-3.2-3B", O / "calibration_v0.3" / "results_llama3b.json", None, None, None)]
AUROC_BAR, PPL_BAR = 0.95, 1.25
add = C.load(O / "repro_v0.1" / "addendum_quality_ppl.json")
rows, n_files = [], 0


def check_cal(res):
    """The rule's flags re-derived per ρ; the operating point (smallest ρ meeting both) re-derived and asserted None."""
    assert "0.95" in res["meta"]["rule"] and "1.25" in res["meta"]["rule"]
    both = []
    for rho, d in res["per_rho"].items():
        au = d["auroc"]["mlp_faithful"]
        assert d["detectable"] is (au >= AUROC_BAR) and d["fluent"] is (d["ppl_ratio"] <= PPL_BAR), rho
        per = [res["per_key"][rho][k]["mlp_faithful"]["auroc"] for k in res["per_key"][rho]]
        assert len(per) == 4 and abs(float(np.mean(per)) - au) < 1e-9, rho
        both.append(d["detectable"] and d["fluent"])
    assert not any(both) and res["operating_point"] is None
    return res


for tag, name, p256, p512, prepro, rtag in MODELS:
    c1 = check_cal(C.load(p256))
    n_files += 1
    N = c1["meta"]["N"]
    V.set(f"cal_{tag}_layer", c1["meta"]["layer"])
    V.set(f"cal_{tag}_N", C.f2(N))
    rhos = sorted(c1["per_rho"], key=float)
    fluent_au = [c1["per_rho"][r]["auroc"]["mlp_faithful"] for r in rhos if c1["per_rho"][r]["fluent"]]
    det_ratio = [c1["per_rho"][r]["ppl_ratio"] for r in rhos if c1["per_rho"][r]["detectable"]]
    V.set(f"cal_{tag}_max_auroc_fluent", C.f2(max(fluent_au)))
    V.set(f"cal_{tag}_min_ratio_detectable", C.f2(min(det_ratio)) if det_ratio else "none detectable")
    V.set(f"cal_{tag}_first_detectable_rho", next((f"{float(r):.2f}" for r in rhos if c1["per_rho"][r]["detectable"]), "none"))
    V.set(f"cal_{tag}_last_fluent_rho", f"{float([r for r in rhos if c1['per_rho'][r]['fluent']][-1]):.2f}")
    for r in rhos:
        d = c1["per_rho"][r]
        t = r.replace(".", "")
        V.set(f"cal_{tag}_{t}_auroc", C.f2(d["auroc"]["mlp_faithful"]))
        V.set(f"cal_{tag}_{t}_ratio", C.f2(d["ppl_ratio"]))
        rows.append([name, 256, f"{float(r):.2f}", C.f1(d["alpha_equiv"]), C.f2(d["auroc"]["mlp_faithful"]), C.f2(d["ppl_ratio"]), "yes" if d["detectable"] else "no", "yes" if d["fluent"] else "no"])
    if p512:
        c2 = check_cal(C.load(p512))
        n_files += 1
        assert c2["meta"]["tokens"] == 512 and c2["meta"]["N"] == N
        for r in sorted(c2["per_rho"], key=float):
            d = c2["per_rho"][r]
            t = r.replace(".", "")
            assert abs(c2["per_rho_first256"][r]["mlp_faithful"] - c1["per_rho"][r]["auroc"]["mlp_faithful"]) < 0.02   # the first 256 tokens reproduce v0.1
            V.set(f"cal512_{tag}_{t}_auroc", C.f2(d["auroc"]["mlp_faithful"]))
            V.set(f"cal512_{tag}_{t}_ratio", C.f2(d["ppl_ratio"]))
            rows.append([name, 512, f"{float(r):.2f}", C.f1(c1["per_rho"][r]["alpha_equiv"]), C.f2(d["auroc"]["mlp_faithful"]), C.f2(d["ppl_ratio"]), "yes" if d["detectable"] else "no", "yes" if d["fluent"] else "no"])
        V.set(f"cal512_{tag}_max_auroc", C.f2(max(c2["per_rho"][r]["auroc"]["mlp_faithful"] for r in c2["per_rho"])))
    # the published α = 5 as a strength ρ on this model
    rho_a5_cal = 5 * 0.5 / c1["per_rho"]["0.5"]["alpha_equiv"]
    if prepro:
        rp = C.load(prepro)
        m = rp["meta"]
        assert m["layer"] == c1["meta"]["layer"] and abs(m["act_norm_median_unsteered"] - N) < 1e-6
        rho_a5 = 5 * m["key_norm_per_alpha1"] / m["act_norm_median_unsteered"]
        assert abs(rho_a5 - rho_a5_cal) < 0.005, (tag, rho_a5, rho_a5_cal)
        per = [rp["per_key"]["cont_a5"][k]["mlp_faithful"]["auroc"] for k in rp["per_key"]["cont_a5"]]
        au5 = rp["summary"]["cont_a5"]["mlp_faithful"]["auroc"]
        assert len(per) == 4 and abs(float(np.mean(per)) - au5) < 1e-9
        best5 = max(rp["summary"]["cont_a5"][det]["auroc"] for det in rp["summary"]["cont_a5"])
        ppl5, pplv = add[f"{rtag}_a5"]["median"], add[f"{rtag}_van"]["median"]
        assert abs(pplv - c1["meta"]["ppl_unsteered_median"]) < 1e-6
        V.set(f"repro_{tag}_a5_rho", C.f2(rho_a5))
        V.set(f"repro_{tag}_a5_rho_pct", f"{100 * rho_a5:.0f}")
        V.set(f"repro_{tag}_a5_auroc", C.f2(au5))
        V.set(f"repro_{tag}_a5_best_auroc", C.f2(best5))
        V.set(f"repro_{tag}_a5_ppl", C.f1(ppl5))
        V.set(f"repro_{tag}_van_ppl", C.f1(pplv))
        V.set(f"repro_{tag}_a5_ppl_ratio", C.f2(ppl5 / pplv))
        rows.append([name, 256, f"published α = 5 → ρ = {rho_a5:.2f}", "5.0", f"{C.f2(au5)} (pilot; best detector {C.f2(best5)})", f"{C.f2(ppl5 / pplv)} (median perplexity {C.f1(ppl5)} vs {C.f1(pplv)})",
                     "yes" if au5 >= AUROC_BAR else "no", "yes" if ppl5 / pplv <= PPL_BAR else "no"])
    else:
        V.set(f"repro_{tag}_a5_rho", C.f2(rho_a5_cal))
        nearest = min(rhos, key=lambda r: abs(float(r) - rho_a5_cal))
        V.set(f"repro_{tag}_a5_nearest_rho", f"{float(nearest):.2f}")
        rows.append([name, 256, f"published α = 5 → ρ ≈ {rho_a5_cal:.2f} (not run; nearest grid point {float(nearest):.2f})", "5.0", "—", "—", "—", "—"])
V.set("cal_n_files", n_files)
V.set("cal_n_models", len(MODELS))
V.set("cal_auroc_bar", f"{AUROC_BAR:.2f}")
V.set("cal_ppl_bar", f"{PPL_BAR:.2f}")
V.set("cal_tuning_keys", "9001–9004")

C.write_table("T2", ["model (base)", "tokens", "ρ = ‖v‖ / N", "α equivalent", "authors' MLP probe AUROC (mean over 4 tuning keys)", "perplexity ratio (steered / unsteered, medians)",
                     "detectable (AUROC ≥ 0.95)", "fluent (ratio ≤ 1.25)"],
              rows, "Calibration of the published scheme on three base models with strength measured as ρ (tuning keys 9001–9004; 40 test texts per key; the reproduction pilot's α = 5 rows as ρ): no strength is both probe-detectable and perplexity-neutral",
              ["N is the median token activation norm at the steered layer over unsteered text (Llama-3.2-1B: layer 8 of 16, N = " + V.d["cal_l1b_N"] + "; Qwen2.5-1.5B: layer 14 of 28, N = " + V.d["cal_q15_N"] +
               "; Llama-3.2-3B: layer 14 of 28, N = " + V.d["cal_l3b_N"] + "). The operating-point rule (the smallest ρ with AUROC ≥ 0.95 and ratio ≤ 1.25) returned none on every model at either length. "
               "Perplexity is the continuation's under the same model without steering, given the prompt; the pilot's perplexity column was added after that pilot's rule was fixed (exploratory)."])
p = V.save()
print("T2 written; values:", p.name, len(V.d))
