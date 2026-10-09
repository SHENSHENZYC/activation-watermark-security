"""Build the calibration report table from research/outputs/calibration_v0.1/*.json (numbers are never retyped)."""
import json
from pathlib import Path

O = Path(__file__).resolve().parents[1] / "outputs" / "calibration_v0.1"
print("| Model | ρ | α equivalent | Authors' MLP AUROC (per key) | Linear | Mass-mean | Cosine (true key) | PPL ratio | Detectable (≥ 0.95) | Fluent (≤ 1.25) |")
print("|---|---|---|---|---|---|---|---|---|---|")
for m in ("qwen", "llama"):
    r = json.loads((O / f"results_{m}.json").read_text())
    assert len(r["per_rho"]) == 6 and all(len(v) == 4 for v in r["per_key"].values())
    for rho, v in r["per_rho"].items():
        a, keys = v["auroc"], r["per_key"][rho]
        pk = ", ".join(f"{keys[s]['mlp_faithful']['auroc']:.2f}" for s in keys)
        print(f"| {m} | {float(rho):.2f} | {v['alpha_equiv']:.1f} | **{a['mlp_faithful']:.2f}** ({pk}) | {a['linear']:.2f} | "
              f"{a['mass_mean']:.2f} | {a['dcos_true_key']:.2f} | **{v['ppl_ratio']:.2f}** | {'yes' if v['detectable'] else 'no'} | "
              f"{'yes' if v['fluent'] else 'no'} |")
    print(f"| {m} | operating point: **{r['operating_point']}** | | | | | | | | |")
