# Exploratory addendum (not in the spec): quality of pilot texts, perplexity under the unsteered model itself.
import json, sys, time, numpy as np, torch
sys.path.insert(0, "."); import repro_pilot as rp; import core
out = {}
for m in ("llama", "qwen"):
    core.configure(m); tok, model = core.load_model(); dev = core.device(); pools = core.assign_pools()
    for tag in ["van", "a5", "a10", "a20"]:
        t0 = time.time(); ppl = []
        for i, s in enumerate(core.TUNING_KEY_SEEDS):
            conts = json.load(open(f"data/{m}/texts_{tag}_k{s}.json")); prompts = [u["prompt"] for u in rp.key_prompts(pools, i)]
            for j in range(100):
                ids, att, spans = rp.encode(tok, [prompts[j]], [conts[j]], True)
                st, n = spans[0]
                with torch.no_grad():
                    lg = model(input_ids=ids.to(dev)).logits[0, st - 1:st - 1 + n].float()
                nll = torch.nn.functional.cross_entropy(lg, ids[0, st:st + n].to(dev))
                ppl.append(float(torch.exp(nll)))
        out[f"{m}_{tag}"] = {"median": float(np.median(ppl)), "p90": float(np.percentile(ppl, 90))}
        print(m, tag, "median ppl %.1f p90 %.1f (%.0fs)" % (np.median(ppl), np.percentile(ppl, 90), time.time() - t0), flush=True)
    del model
json.dump(out, open("../outputs/repro_v0.1/addendum_quality_ppl.json", "w"), indent=2)
