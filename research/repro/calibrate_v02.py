"""Strength calibration v0.2 (CALIBRATION_SPEC_v0.2.md): the v0.1 calibration at 512 new tokens, rho in {0.25, 0.35}.

Tuning keys only, pool T only. Sets Study 1 core's length constants to 512 at run time (core.py is not edited) and
reuses repro_pilot.py and calibrate.py unchanged.
Run: .venv/bin/python research/repro/calibrate_v02.py --model qwen|llama
"""
import argparse
import json
import time

import numpy as np
import torch

import calibrate as c1
import repro_pilot as rp
import core

TOKENS = 512
RHOS = [0.25, 0.35]
FIRST = 256  # descriptive: detectors on the first 256 tokens of the same texts
OUT = core.ROOT / "research" / "outputs" / "calibration_v0.2"


def set_length(n):
    core.NEW_TOKENS = n
    core.GEN_KWARGS = dict(core.GEN_KWARGS, max_new_tokens=n, min_new_tokens=n)


class BodyOnly:
    """Wraps a causal LM so a forward pass runs only the decoder body (no vocabulary-sized logits). Used for feature
    extraction: repro_pilot.layer_tokens hooks model.model.layers[l] and calls model(...); outputs are unchanged."""

    def __init__(self, lm):
        self.model, self.config = lm.model, lm.config

    def __call__(self, **kw):
        return self.model(**kw)


def perplexities(tok, model, prompts, conts):
    """As calibrate.perplexities, but applies the LM head only to the continuation positions and frees the MPS cache
    after each text (full-vocabulary logits over 512+ positions exhausted memory)."""
    dev, out = core.device(), []
    for p, c in zip(prompts, conts):
        ids, _, spans = rp.encode(tok, [p], [c], True)
        st, n = spans[0]
        with torch.no_grad():
            h = model.model(input_ids=ids.to(dev)).last_hidden_state[0, st - 1:st - 1 + n]
            lg = model.lm_head(h).float()
            out.append(float(torch.exp(torch.nn.functional.cross_entropy(lg, ids[0, st:st + n].to(dev)))))
        del h, lg
        torch.mps.empty_cache()
    return out


def name(kind, tag, s):
    ext = "json" if kind in ("texts", "ppl") else "npz"
    return f"c2_{kind}_t{TOKENS}_{tag}_k{s}.{ext}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(core.MODELS), required=True)
    a = ap.parse_args()
    core.configure(a.model)
    set_length(TOKENS)
    data = rp.HERE / "data" / a.model
    N = json.loads((c1.PILOT / f"results_{a.model}.json").read_text())["meta"]["act_norm_median_unsteered"]
    t0 = time.time()
    pools = core.assign_pools()
    tok, model = core.load_model()
    d = model.config.hidden_size
    jobs = [("van", None)] + [(c1.tag(r).replace("calib_", ""), r) for r in RHOS]
    for tg, rho in jobs:
        for i, s in enumerate(core.TUNING_KEY_SEEDS):
            prompts = [u["prompt"] for u in rp.key_prompts(pools, i)]
            ft, ff, fp = data / name("texts", tg, s), data / name("feats", tg, s), data / name("ppl", tg, s)
            if not ft.exists():
                key = None if rho is None else c1.scaled_key(s, d, rho, N)
                ft.write_text(json.dumps(core.generate(tok, model, prompts, key=key, layer=core.LAYER, seed=s)))
            conts = json.loads(ft.read_text())
            if not ff.exists():
                X, lens = rp.layer_tokens(tok, BodyOnly(model), prompts, conts, False)
                np.savez(ff, X=X, lens=lens)
            if not fp.exists():
                fp.write_text(json.dumps(perplexities(tok, model, prompts, conts)))
            torch.mps.empty_cache()
        print(f"{tg}: generated, {time.time() - t0:.0f}s", flush=True)
    del model
    ppl_van = float(np.median(sum((json.loads((data / name("ppl", "van", s)).read_text()) for s in core.TUNING_KEY_SEEDS), [])))
    res = {"per_rho": {}, "per_key": {}, "per_rho_first256": {}}
    for tg, rho in jobs[1:]:
        per, per256, ppl = {}, {}, []
        for s in core.TUNING_KEY_SEEDS:
            fs, fv = np.load(data / name("feats", tg, s)), np.load(data / name("feats", "van", s))
            key = c1.scaled_key(s, d, rho, N).numpy()
            per[s] = rp.probe_one(fs["X"], fs["lens"], fv["X"], fv["lens"], key)
            per256[s] = rp.probe_one(fs["X"][:, :FIRST], np.minimum(fs["lens"], FIRST),
                                     fv["X"][:, :FIRST], np.minimum(fv["lens"], FIRST), key)
            ppl += json.loads((data / name("ppl", tg, s)).read_text())
        k0 = core.TUNING_KEY_SEEDS[0]
        summ = {det: float(np.mean([per[s][det]["auroc"] for s in per])) for det in per[k0]}
        summ256 = {det: float(np.mean([per256[s][det]["auroc"] for s in per256])) for det in per256[k0]}
        ratio = float(np.median(ppl)) / ppl_van
        res["per_key"][str(rho)] = per
        res["per_rho"][str(rho)] = {"auroc": summ, "ppl_median": float(np.median(ppl)), "ppl_ratio": ratio,
                                    "detectable": summ["mlp_faithful"] >= c1.AUROC_MIN, "fluent": ratio <= c1.PPL_RATIO_MAX}
        res["per_rho_first256"][str(rho)] = summ256
        print(f"rho {rho}: mlp_faithful {summ['mlp_faithful']:.3f} (first 256: {summ256['mlp_faithful']:.3f}), "
              f"ppl ratio {ratio:.3f}", flush=True)
    ok = [float(r) for r, v in res["per_rho"].items() if v["detectable"] and v["fluent"]]
    res["operating_point"] = min(ok) if ok else None
    res["meta"] = {
        "spec_sha256": rp.sha(rp.HERE / "CALIBRATION_SPEC_v0.2.md"), "script_sha256": rp.sha(__file__),
        "calibrate_v01_sha256": rp.sha(rp.HERE / "calibrate.py"), "pilot_script_sha256": rp.sha(rp.HERE / "repro_pilot.py"),
        "core_sha256": rp.sha(rp.HERE.parent / "study1" / "core.py"), "model": f"{core.MODEL_ID}@{core.REVISION}",
        "layer": core.LAYER, "N": N, "tokens": TOKENS, "rhos": RHOS, "ppl_unsteered_median": ppl_van,
        "rule": "smallest rho with mlp_faithful AUROC >= 0.95 and ppl ratio <= 1.25",
        "text_lengths_ok": all(len(json.loads((data / name("texts", tg, s)).read_text())) == rp.PER_KEY
                               for tg, _ in jobs for s in core.TUNING_KEY_SEEDS),
        "sample_texts": {tg: json.loads((data / name("texts", tg, core.TUNING_KEY_SEEDS[0])).read_text())[0][:400] for tg, _ in jobs},
        "seconds": round(time.time() - t0), "torch": torch.__version__,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"results_{a.model}.json").write_text(json.dumps(res, indent=2))
    print("operating point:", res["operating_point"], f"({res['meta']['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
