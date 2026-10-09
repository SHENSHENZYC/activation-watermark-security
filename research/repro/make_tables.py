"""Build the pilot report tables from research/outputs/repro_v0.1/*.json (numbers are never retyped)."""
import json
from pathlib import Path

O = Path(__file__).resolve().parents[1] / "outputs" / "repro_v0.1"
ppl = json.loads((O / "addendum_quality_ppl.json").read_text())
DET = ["mlp_faithful", "mlp_strong", "linear", "mass_mean", "dcos_true_key"]
lines = ["| Model | α | ‖v‖ / median ‖h‖ | " + " | ".join(DET) + " | Reproduces (rule) | Median PPL (unsteered text) |",
         "|---" * (len(DET) + 5) + "|"]
for m in ("qwen", "llama"):
    r = json.loads((O / f"results_{m}.json").read_text())
    meta = r["meta"]
    for a in meta["alphas"]:
        tag = f"a{int(a)}"
        s = r["summary"][f"cont_{tag}"]
        rho = a * meta["key_norm_per_alpha1"] / meta["act_norm_median_unsteered"]
        ok = s["mlp_faithful"]["auroc"] >= 0.95
        lines.append(f"| {m} | {int(a)} | {rho:.0%} | " + " | ".join(f"{s[d]['auroc']:.2f}" for d in DET)
                     + f" | {'yes' if ok else 'no'} | {ppl[f'{m}_{tag}']['median']:.1f} (vs {ppl[f'{m}_van']['median']:.1f}) |")
    assert len(r["per_key"]) == 6 and all(len(v) == 4 for v in r["per_key"].values())
print("\n".join(lines))
