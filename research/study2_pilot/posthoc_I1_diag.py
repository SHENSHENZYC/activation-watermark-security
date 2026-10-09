"""Study 2 pilot v0.1 — exploratory diagnosis of check I1 AFTER the run (labelled; not part of the fixed spec).
On check I1's 25 texts (key 9001, rho 0.50), compares the editor's finite-difference sum at several steps s, in bf16 and
float32, with the autograd derivative in bf16 (I1's reference) and in float32. Writes outputs/study2_pilot_v0.1/
posthoc_I1_diag.json. Run: .venv/bin/python research/study2_pilot/posthoc_I1_diag.py"""
import json, sys, time
from pathlib import Path
import numpy as np
import torch
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scrub_core as SC
import scrub_pilot as SP
from scrub_core import PP, core

wm, _ = SP.tuning_sets()
idx = [i for i, x in enumerate(wm) if x["key"] == 9001 and x["rho"] == 0.50]
refs = np.load(SP.DATA / "refs.npz")
w = SP.tuning_key(9001, 0.50) / refs["att_sd14"]
wh = w / np.linalg.norm(w)
G16 = np.load(SP.DATA / "G_orig_wm.npy")[idx]
auto16 = G16 @ wh
out = {"n": len(idx), "auto_bf16": auto16.tolist(), "fd": {}}

def fd_sums(tok, model, ed, s_list):
    res = {}
    for s in s_list:
        vals, t0 = [], time.time()
        for i in idx:
            ids = tok(wm[i]["text"], add_special_tokens=False)["input_ids"][:SC.NEW_TOKENS]
            wt = torch.tensor(wh, dtype=torch.float32)
            H = ed._passes([ids, ids], [s * wt, -s * wt], SC.LAYER)
            vals.append(float(((ed._gather(H[0], ids)[0] - ed._gather(H[1], ids)[0]) / (2 * s)).sum()))
        res[str(s)] = {"values": vals, "s_per_text": (time.time() - t0) / len(idx)}
    return res

tok, m16 = SC.load_base()
ed16 = SC.Editor(tok, m16)
out["fd"]["bf16"] = fd_sums(tok, m16, ed16, [0.5, 1.0, 2.0, 4.0])
del ed16, m16; SC.free()
from transformers import AutoModelForCausalLM
m32 = AutoModelForCausalLM.from_pretrained(core.MODEL_ID, revision=core.REVISION, dtype=torch.float32).to(SC.dev()).eval()
for p_ in m32.parameters():
    p_.requires_grad_(False)
g32 = []
for i in idx:
    enc = core._encode(tok, [wm[i]["text"]]).to(SC.dev()); cm = enc.pop("content_mask")
    b = torch.zeros(1, 1, SC.D, device=SC.dev(), dtype=torch.float32, requires_grad=True)
    hd = m32.model.layers[SC.LAYER].register_forward_hook(PP._hook(b))
    try:
        ll = PP._loglik(m32, enc, cm); ll.backward()
    finally:
        hd.remove()
    g32.append(b.grad[0, 0].detach().cpu().numpy().astype(np.float64))
auto32 = np.stack(g32) @ wh
out["auto_fp32"] = auto32.tolist()
ed32 = SC.Editor(tok, m32)
out["fd"]["fp32"] = fd_sums(tok, m32, ed32, [0.25, 0.5, 1.0, 2.0])
summ = {"auto_bf16_vs_fp32": {"r": float(np.corrcoef(auto16, auto32)[0, 1]), "slope": float(np.polyfit(auto32, auto16, 1)[0])}}
for prec, d in out["fd"].items():
    for s, v in d.items():
        f = np.array(v["values"])
        summ[f"{prec} s={s}"] = {"r_vs_auto_bf16": float(np.corrcoef(f, auto16)[0, 1]), "r_vs_auto_fp32": float(np.corrcoef(f, auto32)[0, 1]),
                                 "slope_vs_auto_fp32": float(np.polyfit(auto32, f, 1)[0]), "s_per_text": v["s_per_text"]}
out["summary"] = summ
(SP.OUT / "posthoc_I1_diag.json").write_text(json.dumps(out, indent=1))
for k, v in summ.items():
    print(k, {a: round(b, 4) for a, b in v.items()})
