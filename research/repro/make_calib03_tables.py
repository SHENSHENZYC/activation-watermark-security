"""Scale table (256 tokens): Qwen2.5-1.5B and Llama-3.2-1B (calibration v0.1) vs Llama-3.2-3B (v0.3). Numbers never retyped."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "outputs"
runs = [("Llama-3.2-1B", R / "calibration_v0.1" / "results_llama.json"),
        ("Qwen2.5-1.5B", R / "calibration_v0.1" / "results_qwen.json"),
        ("Llama-3.2-3B", R / "calibration_v0.3" / "results_llama3b.json")]
res = {m: json.loads(p.read_text()) for m, p in runs}
rhos = ["0.15", "0.25", "0.35", "0.5", "0.7"]
assert all(all(r in v["per_rho"] for r in rhos) for v in res.values())
print("| ρ | " + " | ".join(f"{m}: AUROC / PPL ratio" for m, _ in runs) + " |")
print("|---" * (len(runs) + 1) + "|")
for r in rhos:
    cells = []
    for m, _ in runs:
        v = res[m]["per_rho"][r]
        cells.append(f"{v['auroc']['mlp_faithful']:.2f} / {v['ppl_ratio']:.2f}" + (" ✓" if v["detectable"] and v["fluent"] else ""))
    print(f"| {float(r):.2f} | " + " | ".join(cells) + " |")
print("| paper α = 5 is ρ ≈ | " + " | ".join(f"{5 * float(r) / res[m]['per_rho'][r]['alpha_equiv']:.2f}" for m, _ in runs for r in ["0.5"]) + " |")
print("| operating point | " + " | ".join(str(res[m]["operating_point"]) for m, _ in runs) + " |")
