"""Build the calibration v0.2 report table from research/outputs/calibration_v0.{1,2}/*.json (numbers never retyped)."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "outputs"
print("| Model | ρ | MLP AUROC, 256 tokens (v0.1) | MLP AUROC, first 256 of 512 (v0.2) | **MLP AUROC, 512 tokens** (per key) | Linear, 512 | PPL ratio, 256 (v0.1) | **PPL ratio, 512** | Both rules at 512 |")
print("|---|---|---|---|---|---|---|---|---|")
for m in ("qwen", "llama"):
    v1 = json.loads((R / "calibration_v0.1" / f"results_{m}.json").read_text())
    v2 = json.loads((R / "calibration_v0.2" / f"results_{m}.json").read_text())
    assert v2["meta"]["text_lengths_ok"] and len(v2["per_rho"]) == 2
    for rho, v in v2["per_rho"].items():
        pk = ", ".join(f"{v2['per_key'][rho][s]['mlp_faithful']['auroc']:.2f}" for s in v2["per_key"][rho])
        o = v1["per_rho"][rho]
        print(f"| {m} | {float(rho):.2f} | {o['auroc']['mlp_faithful']:.2f} | {v2['per_rho_first256'][rho]['mlp_faithful']:.2f} | "
              f"**{v['auroc']['mlp_faithful']:.2f}** ({pk}) | {v['auroc']['linear']:.2f} | {o['ppl_ratio']:.2f} | **{v['ppl_ratio']:.2f}** | "
              f"{'yes' if v['detectable'] and v['fluent'] else 'no'} |")
    print(f"| {m} | operating point: **{v2['operating_point']}** | | | | | | | |")
