"""Strength calibration v0.1 (CALIBRATION_SPEC_v0.1.md): detectability and quality against relative strength rho.

Tuning keys only, pool T only. Reuses repro_pilot.py (features, detectors) and research/study1/core.py (keys, hook,
generation), both unchanged; the unsteered texts and features come from the pilot.
Run: .venv/bin/python research/repro/calibrate.py --model qwen|llama
"""
import argparse
import json
import time

import numpy as np
import torch

import repro_pilot as rp
import core  # noqa: E402  (path set by repro_pilot)

RHOS = [0.15, 0.25, 0.35, 0.50, 0.70, 1.00]
AUROC_MIN, PPL_RATIO_MAX = 0.95, 1.25
OUT = core.ROOT / "research" / "outputs" / "calibration_v0.1"
PILOT = core.ROOT / "research" / "outputs" / "repro_v0.1"


def scaled_key(s, d, rho, N):
    v = core.make_key(s, d, 1.0)
    return v * (rho * N / v.norm())


def tag(rho):
    return f"calib_r{int(round(rho * 100)):03d}"


def perplexities(tok, model, prompts, conts):
    dev, out = core.device(), []
    for p, c in zip(prompts, conts):
        ids, _, spans = rp.encode(tok, [p], [c], True)
        st, n = spans[0]
        with torch.no_grad():
            lg = model(input_ids=ids.to(dev)).logits[0, st - 1:st - 1 + n].float()
        out.append(float(torch.exp(torch.nn.functional.cross_entropy(lg, ids[0, st:st + n].to(dev)))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(core.MODELS), required=True)
    a = ap.parse_args()
    rhos = RHOS
    core.configure(a.model)
    data = rp.HERE / "data" / a.model
    pilot = json.loads((PILOT / f"results_{a.model}.json").read_text())
    N = pilot["meta"]["act_norm_median_unsteered"]
    ppl_van = json.loads((PILOT / "addendum_quality_ppl.json").read_text())[f"{a.model}_van"]["median"]
    t0 = time.time()
    pools = core.assign_pools()
    tok, model = core.load_model()
    d = model.config.hidden_size
    for rho in rhos:
        for i, s in enumerate(core.TUNING_KEY_SEEDS):
            prompts = [u["prompt"] for u in rp.key_prompts(pools, i)]
            ft, ff, fp = (data / f"texts_{tag(rho)}_k{s}.json", data / f"feats_cont_{tag(rho)}_k{s}.npz",
                          data / f"ppl_{tag(rho)}_k{s}.json")
            if not ft.exists():
                ft.write_text(json.dumps(core.generate(tok, model, prompts, key=scaled_key(s, d, rho, N),
                                                       layer=core.LAYER, seed=s)))
            conts = json.loads(ft.read_text())
            if not ff.exists():
                X, lens = rp.layer_tokens(tok, model, prompts, conts, False)
                np.savez(ff, X=X, lens=lens)
            if not fp.exists():
                fp.write_text(json.dumps(perplexities(tok, model, prompts, conts)))
        print(f"rho {rho}: generated, {time.time() - t0:.0f}s", flush=True)
    del model
    res = {"per_rho": {}, "per_key": {}}
    for rho in rhos:
        per, ppl = {}, []
        for s in core.TUNING_KEY_SEEDS:
            fs, fv = np.load(data / f"feats_cont_{tag(rho)}_k{s}.npz"), np.load(data / f"feats_cont_van_k{s}.npz")
            per[s] = rp.probe_one(fs["X"], fs["lens"], fv["X"], fv["lens"],
                                  scaled_key(s, d, rho, N).numpy())
            ppl += json.loads((data / f"ppl_{tag(rho)}_k{s}.json").read_text())
        summ = {det: float(np.mean([per[s][det]["auroc"] for s in per])) for det in per[core.TUNING_KEY_SEEDS[0]]}
        ratio = float(np.median(ppl)) / ppl_van
        res["per_key"][str(rho)] = per
        res["per_rho"][str(rho)] = {"auroc": summ, "ppl_median": float(np.median(ppl)), "ppl_ratio": ratio,
                                    "alpha_equiv": float(rho * N / np.mean([core.make_key(s, d, 1.0).norm()
                                                                            for s in core.TUNING_KEY_SEEDS])),
                                    "detectable": summ["mlp_faithful"] >= AUROC_MIN, "fluent": ratio <= PPL_RATIO_MAX}
        print(f"rho {rho}: mlp_faithful {summ['mlp_faithful']:.3f}, ppl ratio {ratio:.2f}", flush=True)
    ok = [float(r) for r, v in res["per_rho"].items() if v["detectable"] and v["fluent"]]
    res["operating_point"] = min(ok) if ok else None
    res["meta"] = {
        "spec_sha256": rp.sha(rp.HERE / "CALIBRATION_SPEC_v0.1.md"), "script_sha256": rp.sha(__file__),
        "pilot_script_sha256": rp.sha(rp.HERE / "repro_pilot.py"), "core_sha256": rp.sha(rp.HERE.parent / "study1" / "core.py"),
        "model": f"{core.MODEL_ID}@{core.REVISION}", "layer": core.LAYER, "N": N, "ppl_unsteered_median": ppl_van,
        "rhos": rhos, "rule": f"smallest rho with mlp_faithful AUROC >= {AUROC_MIN} and ppl ratio <= {PPL_RATIO_MAX}",
        "reused_unsteered_sha256": {p.name: rp.sha(p) for p in sorted(data.glob("texts_van_k*.json"))},
        "sample_texts": {str(r): json.loads((data / f"texts_{tag(r)}_k{core.TUNING_KEY_SEEDS[0]}.json").read_text())[0][:300]
                         for r in rhos},
        "seconds": round(time.time() - t0), "torch": torch.__version__,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"results_{a.model}.json").write_text(json.dumps(res, indent=2))
    print("operating point:", res["operating_point"], f"({res['meta']['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
