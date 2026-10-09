"""Strength calibration v0.3 (CALIBRATION_SPEC_v0.3.md): Llama-3.2-3B, 256 tokens, rho grid, tuning keys only.

Registers the model in Study 1 core at run time (core.py is not edited) and reuses repro_pilot.py, calibrate.py and
calibrate_v02.py (memory-safe features and perplexity) unchanged.
Run: .venv/bin/python research/repro/calibrate_v03.py
"""
import json
import time

import numpy as np
import torch

import calibrate as c1
import calibrate_v02 as c2
import repro_pilot as rp
import core

NAME = "llama3b"
MODEL = ("meta-llama/Llama-3.2-3B", "13afe5124825b4f3751f836b40dafda64c1ed062", 14, 0)  # repo, revision, layer, (no study keys)
RHOS = [0.15, 0.25, 0.35, 0.50, 0.70]
OUT = core.ROOT / "research" / "outputs" / "calibration_v0.3"


def fname(kind, tag, s):
    return f"c3_{kind}_{tag}_k{s}.{'json' if kind in ('texts', 'ppl') else 'npz'}"


def main():
    core.MODELS[NAME] = MODEL
    core.configure(NAME)
    data = rp.HERE / "data" / NAME
    data.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pools = core.assign_pools()
    tok, model = core.load_model()
    d = model.config.hidden_size
    assert d == 3072 and len(model.model.layers) == 28 and core.LAYER == 14 and core.n_support(d) == 9

    def run(tag, key_fn):
        for i, s in enumerate(core.TUNING_KEY_SEEDS):
            prompts = [u["prompt"] for u in rp.key_prompts(pools, i)]
            ft, ff, fp = data / fname("texts", tag, s), data / fname("feats", tag, s), data / fname("ppl", tag, s)
            if not ft.exists():
                ft.write_text(json.dumps(core.generate(tok, model, prompts, key=key_fn(s), layer=core.LAYER, seed=s)))
                torch.mps.empty_cache()
            conts = json.loads(ft.read_text())
            if not ff.exists():
                X, lens = rp.layer_tokens(tok, c2.BodyOnly(model), prompts, conts, False)
                np.savez(ff, X=X, lens=lens)
                torch.mps.empty_cache()
            if not fp.exists():
                fp.write_text(json.dumps(c2.perplexities(tok, model, prompts, conts)))
        print(f"{tag}: done, {time.time() - t0:.0f}s", flush=True)

    run("van", lambda s: None)
    v0 = np.load(data / fname("feats", "van", core.TUNING_KEY_SEEDS[0]))
    N = float(np.median(np.linalg.norm(np.concatenate([v0["X"][j, :v0["lens"][j]] for j in range(rp.PER_KEY)])
                                       .astype(np.float32), axis=1)))
    ppl_van = float(np.median(sum((json.loads((data / fname("ppl", "van", s)).read_text()) for s in core.TUNING_KEY_SEEDS), [])))
    print(f"N = {N:.3f}, unsteered median perplexity {ppl_van:.3f}", flush=True)
    for rho in RHOS:
        run(c1.tag(rho).replace("calib_", ""), lambda s, rho=rho: c1.scaled_key(s, d, rho, N))
    del model
    res = {"per_rho": {}, "per_key": {}}
    for rho in RHOS:
        tag = c1.tag(rho).replace("calib_", "")
        per, ppl = {}, []
        for s in core.TUNING_KEY_SEEDS:
            fs, fv = np.load(data / fname("feats", tag, s)), np.load(data / fname("feats", "van", s))
            per[s] = rp.probe_one(fs["X"], fs["lens"], fv["X"], fv["lens"], c1.scaled_key(s, d, rho, N).numpy())
            ppl += json.loads((data / fname("ppl", tag, s)).read_text())
        summ = {det: float(np.mean([per[s][det]["auroc"] for s in per])) for det in per[core.TUNING_KEY_SEEDS[0]]}
        ratio = float(np.median(ppl)) / ppl_van
        res["per_key"][str(rho)] = per
        res["per_rho"][str(rho)] = {"auroc": summ, "ppl_median": float(np.median(ppl)), "ppl_ratio": ratio,
                                    "alpha_equiv": float(rho * N / np.mean([core.make_key(s, d, 1.0).norm() for s in core.TUNING_KEY_SEEDS])),
                                    "detectable": summ["mlp_faithful"] >= c1.AUROC_MIN, "fluent": ratio <= c1.PPL_RATIO_MAX}
        print(f"rho {rho}: mlp_faithful {summ['mlp_faithful']:.3f}, ppl ratio {ratio:.3f}", flush=True)
    ok = [float(r) for r, v in res["per_rho"].items() if v["detectable"] and v["fluent"]]
    res["operating_point"] = min(ok) if ok else None
    res["meta"] = {
        "spec_sha256": rp.sha(rp.HERE / "CALIBRATION_SPEC_v0.3.md"), "script_sha256": rp.sha(__file__),
        "calibrate_v02_sha256": rp.sha(rp.HERE / "calibrate_v02.py"), "calibrate_v01_sha256": rp.sha(rp.HERE / "calibrate.py"),
        "pilot_script_sha256": rp.sha(rp.HERE / "repro_pilot.py"), "core_sha256": rp.sha(rp.HERE.parent / "study1" / "core.py"),
        "manifest_sha256": rp.sha(core.ROOT / "research" / "stage4" / "outputs" / "model_manifest_llama-3.2-3b.json"),
        "model": f"{core.MODEL_ID}@{core.REVISION}", "layer": core.LAYER, "k": core.n_support(d), "N": N,
        "ppl_unsteered_median": ppl_van, "rhos": RHOS, "tokens": core.NEW_TOKENS,
        "rule": "smallest rho with mlp_faithful AUROC >= 0.95 and ppl ratio <= 1.25",
        "sample_texts": {t: json.loads((data / fname("texts", t, core.TUNING_KEY_SEEDS[0])).read_text())[0][:300]
                         for t in ["van"] + [c1.tag(r).replace("calib_", "") for r in RHOS]},
        "seconds": round(time.time() - t0), "torch": torch.__version__,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"results_{NAME}.json").write_text(json.dumps(res, indent=2))
    print("operating point:", res["operating_point"], f"({res['meta']['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
