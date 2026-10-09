"""Scratch: verify pinned paraphraser weights against the Stage 4 manifests, then time paraphrasing
on pool F texts (unwatermarked reference set). Timing only: no detector or key statistic is computed."""
import hashlib, json, os, sys, time, subprocess
import torch
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModelForCausalLM

ROOT = "<repository>"
MODELS = {
    "qwen": ("Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306", "qwen2.5-1.5b-instruct"),
    "phi": ("microsoft/Phi-3.5-mini-instruct", "2fe192450127e6a83f7441aef6e3ca586c338b77", "phi-3.5-mini-instruct"),
}
PROMPT = ("Paraphrase the following text. Keep all of its information and meaning, but change the wording "
          "and sentence structure. Reply with the paraphrase only.\n\nText:\n{text}")
MAX_NEW = 400


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def verify(key):
    rid, rev, man = MODELS[key]
    files = json.load(open(f"{ROOT}/research/stage4/outputs/model_manifest_{man}.json"))["files"]
    out = {}
    for fn, meta in files.items():
        if fn.endswith(".md") or fn in (".gitattributes", "LICENSE", "NOTICE.md", "sample_finetune.py"):
            continue
        p = hf_hub_download(rid, fn, revision=rev)
        want = meta["sha256"] if isinstance(meta, dict) else meta
        got = sha256(p)
        out[fn] = got == want
        assert got == want, (fn, got, want)
    return out


def footprint_gb():
    r = subprocess.run(["footprint", str(os.getpid())], capture_output=True, text=True).stdout
    for line in r.splitlines():
        if "phys_footprint:" in line:
            return line.split(":")[1].strip()
    return "?"


def run(key, texts):
    rid, rev, _ = MODELS[key]
    tok = AutoTokenizer.from_pretrained(rid, revision=rev)
    t = time.time()
    model = AutoModelForCausalLM.from_pretrained(rid, revision=rev, dtype=torch.bfloat16).to("mps").eval()
    load_s = time.time() - t
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    def enc(batch):
        msgs = [[{"role": "user", "content": PROMPT.format(text=x)}] for x in batch]
        s = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in msgs]
        return tok(s, return_tensors="pt", padding=True).to("mps")

    res = {"load_s": round(load_s, 1), "unbatched": [], "batched": {}}
    torch.manual_seed(0)
    for x in texts[:3]:
        inp = enc([x])
        t = time.time()
        with torch.inference_mode():
            o = model.generate(**inp, max_new_tokens=MAX_NEW, do_sample=True, temperature=0.7, top_p=0.9)
        torch.mps.synchronize()
        dt = time.time() - t
        new = o[0, inp["input_ids"].shape[1]:]
        n_new = int((new != tok.pad_token_id).sum())
        out = tok.decode(new, skip_special_tokens=True)
        res["unbatched"].append({"s": round(dt, 1), "new_tokens": n_new, "tok_per_s": round(n_new / dt, 1),
                                 "in_words": len(x.split()), "out_words": len(out.split())})
        res.setdefault("sample_out", out[:600])
    for bs in (4, 8):
        batch = texts[3:3 + bs]
        inp = enc(batch)
        t = time.time()
        with torch.inference_mode():
            o = model.generate(**inp, max_new_tokens=MAX_NEW, do_sample=True, temperature=0.7, top_p=0.9)
        torch.mps.synchronize()
        dt = time.time() - t
        outs = [tok.decode(r[inp["input_ids"].shape[1]:], skip_special_tokens=True) for r in o]
        res["batched"][bs] = {"s": round(dt, 1), "s_per_text": round(dt / bs, 1),
                              "out_words": [len(z.split()) for z in outs]}
    res["footprint"] = footprint_gb()
    del model
    torch.mps.empty_cache()
    return res


if __name__ == "__main__":
    key = sys.argv[1]
    texts = json.load(open(f"{ROOT}/research/study1_v02/data/S_F_van.json"))
    print(key, "verify", verify(key), flush=True)
    print(key, json.dumps(run(key, texts), indent=1), flush=True)
