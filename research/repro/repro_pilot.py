"""Reproduction pilot v0.1 (REPRO_PILOT_SPEC_v0.1.md): is the Self-Recognition watermark detectable on our models?

Tuning keys only (9001-9004), pool T only. Reuses research/study1/core.py unchanged (keys, hook, generation settings).
Steps per model, each checkpointed under research/repro/data/<model>/ (git-ignored):
  gen    steered texts (alpha in ALPHAS) and paired unsteered texts, 100 prompts per key
  feats  per-token output of the steered layer for the continuation tokens, variants 'cont' and 'prompt'
  probe  per-key detectors -> research/outputs/repro_v0.1/results_<model>.json
Run: .venv/bin/python research/repro/repro_pilot.py --model qwen|llama
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "study1"))
import core  # noqa: E402  (unchanged Study 1 machinery)

ALPHAS = [5.0, 10.0, 20.0]
VARIANTS = ["cont", "prompt"]
PER_KEY = 100
SPLIT_SEED, N_TRAIN, N_VAL = 0, 60, 20
VOTE_FROM = 5  # authors' min_id_vote
OUT = core.ROOT / "research" / "outputs" / "repro_v0.1"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def key_prompts(pools, i):
    return pools["T"][i * PER_KEY:(i + 1) * PER_KEY]


# ------------------------------------------------------------------ generation
def gen(tok, model, pools, data):
    for i, s in enumerate(core.TUNING_KEY_SEEDS):
        prompts = [u["prompt"] for u in key_prompts(pools, i)]
        jobs = [("van", None)] + [(f"a{int(a)}", core.make_key(s, model.config.hidden_size, a)) for a in ALPHAS]
        for tag, key in jobs:
            f = data / f"texts_{tag}_k{s}.json"
            if f.exists():
                continue
            t0 = time.time()
            texts = core.generate(tok, model, prompts, key=key, layer=core.LAYER, seed=s)
            f.write_text(json.dumps(texts))
            print(f"gen {tag} k{s}: {time.time() - t0:.0f}s", flush=True)


# ------------------------------------------------------------------ features
def encode(tok, prompts, conts, with_prompt):
    has_bos = tok.bos_token_id is not None and tok("a")["input_ids"][0] == tok.bos_token_id
    bos = [tok.bos_token_id] if has_bos else []
    seqs, spans = [], []
    for p, c in zip(prompts, conts):
        pi = tok(p, add_special_tokens=False)["input_ids"] if with_prompt else []
        ci = tok(c, add_special_tokens=False)["input_ids"][:core.NEW_TOKENS]
        seqs.append(bos + pi + ci)
        spans.append((len(bos) + len(pi), len(ci)))
    L = max(map(len, seqs))
    ids = torch.full((len(seqs), L), tok.pad_token_id)
    att = torch.zeros((len(seqs), L), dtype=torch.long)
    for j, sq in enumerate(seqs):  # right padding: earlier positions are unaffected in a causal model
        ids[j, :len(sq)] = torch.tensor(sq)
        att[j, :len(sq)] = 1
    return ids, att, spans


def layer_tokens(tok, model, prompts, conts, with_prompt, batch_size=16):
    """[n, NEW_TOKENS, d] float16 activations of the steered layer's output on continuation tokens, plus lengths."""
    dev, d = core.device(), model.config.hidden_size
    X = np.zeros((len(conts), core.NEW_TOKENS, d), dtype=np.float16)
    lens = np.zeros(len(conts), dtype=np.int64)
    cap = {}
    hook = model.model.layers[core.LAYER].register_forward_hook(
        lambda m, i, o: cap.__setitem__("h", (o[0] if isinstance(o, tuple) else o).detach()))
    try:
        for b0 in range(0, len(conts), batch_size):
            ids, att, spans = encode(tok, prompts[b0:b0 + batch_size], conts[b0:b0 + batch_size], with_prompt)
            with torch.no_grad():
                model(input_ids=ids.to(dev), attention_mask=att.to(dev))
            h = cap["h"].float().cpu().numpy()
            for j, (st, n) in enumerate(spans):
                X[b0 + j, :n] = h[j, st:st + n]
                lens[b0 + j] = n
    finally:
        hook.remove()
    return X, lens


def feats(tok, model, pools, data):
    for i, s in enumerate(core.TUNING_KEY_SEEDS):
        prompts = [u["prompt"] for u in key_prompts(pools, i)]
        for tag in ["van"] + [f"a{int(a)}" for a in ALPHAS]:
            conts = json.loads((data / f"texts_{tag}_k{s}.json").read_text())
            for var in VARIANTS:
                f = data / f"feats_{var}_{tag}_k{s}.npz"
                if f.exists():
                    continue
                X, lens = layer_tokens(tok, model, prompts, conts, var == "prompt")
                np.savez(f, X=X, lens=lens)
        print(f"feats k{s} done", flush=True)


# ------------------------------------------------------------------ detectors
def auroc(pos, neg):
    s = np.concatenate([pos, neg])
    r = np.empty(len(s))
    order = np.argsort(s, kind="mergesort")
    r[order] = np.arange(1, len(s) + 1)
    for v in np.unique(s):  # average ranks over ties
        m = s == v
        r[m] = r[m].mean()
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def tokens(X, lens, idx):
    rows = [X[j, :lens[j]] for j in idx]
    tid = np.concatenate([np.full(len(r), k) for k, r in enumerate(rows)])
    return np.concatenate(rows).astype(np.float32), tid


class SimpleMLP(nn.Module):
    """Replica of the authors' SimpleMLP (softmax output; they apply CrossEntropyLoss to it)."""

    def __init__(self, d, hidden=(2048, 64, 64, 32)):
        super().__init__()
        sizes = [d, *hidden, 2]
        layers = []
        for a, b in zip(sizes[:-1], sizes[1:]):
            layers += [nn.Linear(a, b), nn.ReLU()]
        self.net = nn.Sequential(*layers[:-1])

    def forward(self, x):
        return torch.softmax(self.net(x), 1)


def train(net, Xtr, ytr, Xva, yva, epochs, loss_fn, pick_best, seed=1):
    dev = core.device()
    torch.manual_seed(seed)
    net = net.to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    Xtr_t, ytr_t = torch.from_numpy(Xtr), torch.from_numpy(ytr)
    Xva_t, yva_t = torch.from_numpy(Xva).to(dev), torch.from_numpy(yva).to(dev)
    best, best_state = np.inf, None
    for _ in range(epochs):
        net.train()
        perm = torch.randperm(len(Xtr_t))
        for b0 in range(0, len(perm), 512):
            bi = perm[b0:b0 + 512]
            opt.zero_grad()
            loss_fn(net(Xtr_t[bi].to(dev)), ytr_t[bi].to(dev)).backward()
            opt.step()
        if pick_best:
            net.eval()
            with torch.no_grad():
                vl = float(loss_fn(net(Xva_t), yva_t))
            if vl < best:
                best, best_state = vl, {k: v.clone() for k, v in net.state_dict().items()}
    if best_state is not None:
        net.load_state_dict(best_state)
    net.eval()
    return net


def p_steered(net, X, kind):
    with torch.no_grad():
        out = net(torch.from_numpy(X).to(core.device()))
        return (out[:, 1] if kind == "mlp" else torch.sigmoid(out[:, 0])).float().cpu().numpy()


def text_scores(tok_scores, tid, n):
    return np.array([tok_scores[tid == k].mean() for k in range(n)])


def vote_acc(p_pos, tid_pos, p_neg, tid_neg, n):
    pred_pos = [(p_pos[tid_pos == k][VOTE_FROM:] > 0.5).mean() > 0.5 for k in range(n)]
    pred_neg = [(p_neg[tid_neg == k][VOTE_FROM:] > 0.5).mean() > 0.5 for k in range(n)]
    return float((np.sum(pred_pos) + np.sum(~np.array(pred_neg))) / (2 * n))


def probe_one(Xs, ls, Xv, lv, key):
    rng = np.random.default_rng(SPLIT_SEED)
    perm = rng.permutation(PER_KEY)
    tr, va, te = perm[:N_TRAIN], perm[N_TRAIN:N_TRAIN + N_VAL], perm[N_TRAIN + N_VAL:]
    S = {part: tokens(Xs, ls, idx) for part, idx in (("tr", tr), ("va", va), ("te", te))}
    V = {part: tokens(Xv, lv, idx) for part, idx in (("tr", tr), ("va", va), ("te", te))}
    n_te = len(te)

    def xy(part):
        X = np.concatenate([S[part][0], V[part][0]])
        y = np.concatenate([np.ones(len(S[part][0])), np.zeros(len(V[part][0]))]).astype(np.int64)
        return X, y

    Xtr, ytr = xy("tr")
    Xva, yva = xy("va")
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    std = lambda X: ((X - mu) / sd).astype(np.float32)  # noqa: E731
    d = Xtr.shape[1]
    res = {}
    ce = nn.CrossEntropyLoss()
    bce = lambda o, y: nn.functional.binary_cross_entropy_with_logits(o[:, 0], y.float())  # noqa: E731
    models = {
        "mlp_faithful": (train(SimpleMLP(d), Xtr, ytr, Xva, yva, 1, ce, False), "mlp", lambda X: X),
        "mlp_strong": (train(SimpleMLP(d), std(Xtr), ytr, std(Xva), yva, 10, ce, True), "mlp", std),
        "linear": (train(nn.Linear(d, 1), std(Xtr), ytr, std(Xva), yva, 10, bce, True), "lin", std),
    }
    for name, (net, kind, tf) in models.items():
        ps, pv = p_steered(net, tf(S["te"][0]), kind), p_steered(net, tf(V["te"][0]), kind)
        res[name] = {"auroc": auroc(text_scores(ps, S["te"][1], n_te), text_scores(pv, V["te"][1], n_te)),
                     "vote_acc": vote_acc(ps, S["te"][1], pv, V["te"][1], n_te)}
    unit = lambda X: X / np.linalg.norm(X, axis=1, keepdims=True).clip(1e-6)  # noqa: E731
    w = unit(S["tr"][0]).mean(0) - unit(V["tr"][0]).mean(0)
    res["mass_mean"] = {"auroc": auroc(text_scores(unit(S["te"][0]) @ w, S["te"][1], n_te),
                                       text_scores(unit(V["te"][0]) @ w, V["te"][1], n_te))}
    vk = key / np.linalg.norm(key)
    res["dcos_true_key"] = {"auroc": auroc(text_scores(unit(S["te"][0]) @ vk, S["te"][1], n_te),
                                           text_scores(unit(V["te"][0]) @ vk, V["te"][1], n_te))}
    return res


def probe(model_name, d, data):
    out = {"per_key": {}, "summary": {}}
    for var in VARIANTS:
        for a in ALPHAS:
            tag = f"a{int(a)}"
            per = {}
            for s in core.TUNING_KEY_SEEDS:
                fs, fv = np.load(data / f"feats_{var}_{tag}_k{s}.npz"), np.load(data / f"feats_{var}_van_k{s}.npz")
                per[s] = probe_one(fs["X"], fs["lens"], fv["X"], fv["lens"], core.make_key(s, d, a).numpy())
            out["per_key"][f"{var}_{tag}"] = per
            out["summary"][f"{var}_{tag}"] = {det: {m: float(np.mean([per[s][det][m] for s in per]))
                                                    for m in per[core.TUNING_KEY_SEEDS[0]][det]}
                                              for det in per[core.TUNING_KEY_SEEDS[0]]}
            print(f"{var} {tag}: " + ", ".join(f"{k} {v['auroc']:.3f}" for k, v in out["summary"][f"{var}_{tag}"].items()),
                  flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(core.MODELS), required=True)
    a = ap.parse_args()
    core.configure(a.model)
    data = HERE / "data" / a.model
    data.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pools = core.assign_pools()
    tok, model = core.load_model()
    d = model.config.hidden_size
    gen(tok, model, pools, data)
    feats(tok, model, pools, data)
    del model
    van = np.load(data / f"feats_cont_van_k{core.TUNING_KEY_SEEDS[0]}.npz")
    norms = np.linalg.norm(np.concatenate([van["X"][j, :van["lens"][j]] for j in range(PER_KEY)]).astype(np.float32), axis=1)
    res = probe(a.model, d, data)
    res["meta"] = {
        "spec": "research/repro/REPRO_PILOT_SPEC_v0.1.md", "spec_sha256": sha(HERE / "REPRO_PILOT_SPEC_v0.1.md"),
        "script_sha256": sha(__file__), "core_sha256": sha(HERE.parent / "study1" / "core.py"),
        "model": f"{core.MODEL_ID}@{core.REVISION}", "layer": core.LAYER, "alphas": ALPHAS,
        "keys": core.TUNING_KEY_SEEDS, "key_norm_per_alpha1": float(np.mean([core.make_key(s, d, 1.0).norm() for s in core.TUNING_KEY_SEEDS])),
        "act_norm_median_unsteered": float(np.median(norms)), "act_norm_p90_unsteered": float(np.percentile(norms, 90)),
        "text_files_sha256": {p.name: sha(p) for p in sorted(data.glob("texts_*.json"))},
        "sample_texts": {tag: json.loads((data / f"texts_{tag}_k{core.TUNING_KEY_SEEDS[0]}.json").read_text())[0][:300]
                         for tag in ["van"] + [f"a{int(x)}" for x in ALPHAS]},
        "seconds": round(time.time() - t0), "torch": torch.__version__,
        "reproduces_rule": "MLP-faithful mean test AUROC >= 0.95",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"results_{a.model}.json").write_text(json.dumps(res, indent=2))
    print("done", a.model, res["meta"]["seconds"], "s", flush=True)


if __name__ == "__main__":
    main()
