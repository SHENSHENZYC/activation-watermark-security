"""EXPLORATORY (added after the v0.3 run; not pre-registered): does perplexity-based fluency admit repetitive text?

Motivation: the pre-registered sample (Route B, key 1001, rho = 0.50, layer 1) is visibly degenerate yet below the
fluency bar, because repetition lowers perplexity. Diagnostic, chosen after seeing that sample:
  rep3(text) = 1 - distinct word 3-grams / all word 3-grams (lower-cased, whitespace words);
  a text is "repetitive" if rep3 > the 95th percentile of its key-level's oracle texts (mirrors the fluency rule).
FA_nr = share of texts accepted AND fluent AND not repetitive; median over 8 keys. Descriptive only; no rule uses it.
Writes research/outputs/study1_v0.3/report/exploratory_repetition.{json,md}.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D3, D2 = ROOT / "study1_v03" / "data", ROOT / "study1_v02" / "data"
OUT = ROOT / "outputs" / "study1_v0.3" / "report"
res = json.loads((ROOT / "outputs" / "study1_v0.3" / "results.json").read_text())
KEYS, LEVELS, TAG = list(range(1001, 1009)), ["0.35", "0.5", "0.7"], {"0.35": "035", "0.5": "050", "0.7": "070"}
CONDS = ["oracle", "random"] + [f"{v}_{r}_n{n}" for v in ("v03", "v02") for r in "AB" for n in (64, 256)]


def rep3(t):
    w = t.lower().split()
    g = list(zip(w, w[1:], w[2:]))
    return 1 - len(set(g)) / len(g) if g else 0.0


def load(s, lv, c):
    t, S2 = f"k{s}_r{TAG[lv]}", json.loads((D2 / f"K_k{s}_r{TAG[lv]}_summary.json").read_text())
    if c in ("oracle", "random"):
        return json.loads((D2 / f"K_{t}_{c}.json").read_text()), S2[f"scores_{c}"], S2[f"ppl_{c}"], S2
    v, r, n = c.split("_")
    if v == "v03":
        a = json.loads((D3 / f"K_{t}_v03.json").read_text())["attacks"][f"{r}_{n}"]
        return json.loads((D3 / f"K_{t}_forge3_{r}_{n}.json").read_text()), a["scores"], a["ppl"], S2
    return json.loads((D2 / f"K_{t}_forge_{r}_{n}.json").read_text()), S2[f"scores_forge_{r}_{n}"], S2[f"ppl_forge_{r}_{n}"], S2


out, md = {"note": __doc__.strip().splitlines()[0], "levels": {}}, []
md.append("| ρ | condition | FA (pre-registered) | FA and not repetitive | share of FA texts that are repetitive | median rep3 |")
md.append("|---|---|---|---|---|---|")
for lv in LEVELS:
    L = {}
    for c in CONDS:
        fa, fanr, share, med = [], [], [], []
        for i, s in enumerate(KEYS):
            txt, sc, pp, S2 = load(s, lv, c)
            orc = [rep3(x) for x in json.loads((D2 / f"K_k{s}_r{TAG[lv]}_oracle.json").read_text())]
            rcut, pcut = np.quantile(orc, 0.95), res["levels"][lv]["fluent_cut_per_key"][i]
            r = np.array([rep3(x) for x in txt])
            f = (np.asarray(sc) > S2["threshold"]) & (np.asarray(pp, dtype=np.float64) <= pcut)
            fa.append(f.mean())
            fanr.append((f & (r <= rcut)).mean())
            share.append((f & (r > rcut)).sum() / max(f.sum(), 1))
            med.append(np.median(r))
        assert float(np.median(fa)) == res["levels"][lv][c]["FA"]["median"], (lv, c)  # ties back to the locked FA
        L[c] = {"FA_median": float(np.median(fa)), "FA_not_repetitive_median": float(np.median(fanr)),
                "repetitive_share_of_FA_median": float(np.median(share)), "rep3_median": float(np.median(med)),
                "FA_not_repetitive_per_key": [float(x) for x in fanr]}
        md.append(f"| {lv} | {c} | {100 * L[c]['FA_median']:.1f} | {100 * L[c]['FA_not_repetitive_median']:.1f} | "
                  f"{100 * L[c]['repetitive_share_of_FA_median']:.1f} | {L[c]['rep3_median']:.3f} |")
    out["levels"][lv] = L
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "exploratory_repetition.json").write_text(json.dumps(out, indent=1))
(OUT / "exploratory_repetition.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
