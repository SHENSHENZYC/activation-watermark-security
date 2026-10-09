"""Owner-side detector for Study 1 v0.2 (protocol §5): the authors' MLP probe with a 1%-FPR threshold.

Replica of Self-Recognition's SimpleMLP and training loop (commit 7c26938, steering_watermark/src/ml_model.py and
param.yaml): d -> 2048 -> 64 -> 64 -> 32 -> 2, ReLU, softmax output, CrossEntropyLoss applied to it, Adam lr 1e-3,
batch 512, one epoch, raw activations, one sample per token.
"""
import numpy as np
import torch
from torch import nn

HIDDEN = (2048, 64, 64, 32)


class SimpleMLP(nn.Module):
    def __init__(self, d):
        super().__init__()
        sizes = [d, *HIDDEN, 2]
        layers = []
        for a, b in zip(sizes[:-1], sizes[1:]):
            layers += [nn.Linear(a, b), nn.ReLU()]
        self.net = nn.Sequential(*layers[:-1])

    def forward(self, x):
        return torch.softmax(self.net(x), 1)


def tokens(X, lens):
    """Flatten [n, T, d] padded activations to [sum(lens), d] float32 plus text ids."""
    rows = [X[j, :lens[j]] for j in range(len(lens))]
    return np.concatenate(rows).astype(np.float32), np.concatenate([np.full(len(r), j) for j, r in enumerate(rows)])


def train(Xpos, lpos, Xneg, lneg, device, seed=1, epochs=1, batch=512, lr=1e-3):
    P, _ = tokens(Xpos, lpos)
    Nn, _ = tokens(Xneg, lneg)
    X = torch.from_numpy(np.concatenate([P, Nn]))
    y = torch.from_numpy(np.concatenate([np.ones(len(P)), np.zeros(len(Nn))]).astype(np.int64))
    torch.manual_seed(seed)
    net = SimpleMLP(X.shape[1]).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    ce = nn.CrossEntropyLoss()
    net.train()
    for _ in range(epochs):
        perm = torch.randperm(len(X))
        for b0 in range(0, len(perm), batch):
            bi = perm[b0:b0 + batch]
            opt.zero_grad()
            ce(net(X[bi].to(device)), y[bi].to(device)).backward()
            opt.step()
    net.eval()
    return net


def score(net, X, lens, device, texts_per_chunk=64):
    """Text score = mean over tokens of P(watermarked). Works through texts in chunks to bound memory."""
    out = []
    with torch.no_grad():
        for c0 in range(0, len(lens), texts_per_chunk):
            T, tid = tokens(X[c0:c0 + texts_per_chunk], lens[c0:c0 + texts_per_chunk])
            p = net(torch.from_numpy(T).to(device))[:, 1].float().cpu().numpy()
            out += [p[tid == j].mean() if (tid == j).any() else np.nan for j in range(len(lens[c0:c0 + texts_per_chunk]))]
    return np.array(out)


def threshold(null_scores, fpr=0.01):
    """Accept if score > the (1 - fpr) quantile of the owner's own null scores (pool A1)."""
    return float(np.quantile(np.asarray(null_scores, dtype=np.float64), 1.0 - fpr))


def accept(scores, thr):
    return (np.asarray(scores) > thr).astype(float)
