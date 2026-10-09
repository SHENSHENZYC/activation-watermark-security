"""FA1 — per-key calibration (Appendix D): each study key's false-positive rate at p ≤ 0.01 on 1,000 null texts, (a) for
the fixed key's exact test S4 on unwatermarked model text and on human continuations (Study 3) and on model text after
paraphrase by P-Qwen and P-Phi (Study 2), (b) for the keyed tests of the context-hashed arms (Study 5) beside S4; the
nominal 1% and the 3% per-key gate. Reads study3_v0.1, study2_v0.1 and study5_v0.1 results.json; asserts pooled rates
and the calibrated-key lists; writes build/FA1.png and build/values_figA1.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("figA1")
r3 = C.load(C.OUT / "study3_v0.1" / "results.json")
r2 = C.load(C.OUT / "study2_v0.1" / "results.json")
r5 = C.load(C.OUT / "study5_v0.1" / "results.json")
K = [str(k) for k in C.KEYS]


def series(block):
    v = [block["per_key_fpr_pct"][k] for k in K]
    return v


s4_model = series(r3["S4"]["G2"])
s4_human = series(r3["S4"]["H1"])
assert abs(np.mean(s4_model) - r3["S4"]["G1"]["pooled_fpr_pct"]) < 1e-9 and r3["S4"]["G2"]["n_calibrated"] == 8
qwen = series(r2["calibration"]["qwen"]["G2"])
phi = series(r2["calibration"]["phi"]["G2"])
assert r2["calibration"]["qwen"]["G2"]["n_calibrated"] == 8 and r2["calibration"]["phi"]["G2"]["n_calibrated"] == 8
h1 = series(r5["arms"]["h1"]["calibration"]["G2"])
h4 = series(r5["arms"]["h4"]["calibration"]["G2"])
assert r5["arms"]["h1"]["calibration"]["G2"]["n_calibrated"] == 8 and r5["arms"]["h4"]["calibration"]["G2"]["n_calibrated"] == 8
plt = C.fig_style()
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True)
x = np.arange(8)
ax = axs[0]
ax.scatter(x - 0.24, s4_model, s=42, marker="o", color=C.PAL["exact"], edgecolor="white", linewidth=0.8, zorder=3, label="S4, unwatermarked model text (Study 3, G2)")
ax.scatter(x - 0.08, s4_human, s=42, marker="D", color="white", edgecolor=C.PAL["exact"], linewidth=1.3, zorder=3, label="S4, human continuations (Study 3, H1)")
ax.scatter(x + 0.08, qwen, s=42, marker="s", color=C.PAL["qwen"], edgecolor="white", linewidth=0.8, zorder=3, label="S4 after P-Qwen paraphrase (Study 2)")
ax.scatter(x + 0.24, phi, s=42, marker="s", color=C.PAL["phi"], edgecolor="white", linewidth=0.8, zorder=3, label="S4 after P-Phi paraphrase (Study 2)")
ax.set_title("(a) the fixed key's exact test")
ax = axs[1]
ax.scatter(x - 0.2, s4_model, s=42, marker="o", color="white", edgecolor=C.INK, linewidth=1.2, zorder=3, label="S4, fixed key (Study 3, for reference)")
ax.scatter(x, h1, s=42, marker="^", color=C.PAL["h1"], edgecolor="white", linewidth=0.8, zorder=3, label="keyed test, h = 1 (Study 5)")
ax.scatter(x + 0.2, h4, s=42, marker="v", color=C.PAL["h4"], edgecolor="white", linewidth=0.8, zorder=3, label="keyed test, h = 4 (Study 5)")
ax.set_title("(b) the context-hashed arms' keyed tests")
for ax in axs:
    ax.axhline(1, color=C.MUTED, lw=1, ls=":")
    ax.axhline(3, color=C.INK, lw=1, ls="--")
    ax.text(-0.45, 3.05, "per-key gate G2: 3%", color=C.INK, fontsize=7.5, va="bottom", ha="left")
    ax.text(3.5, 3.05, "nominal 1% dotted", color=C.MUTED, fontsize=7.5, va="bottom", ha="center")
    ax.set_xticks(x, K)
    ax.set_xlabel("study key")
    ax.set_ylim(-0.15, 3.6)
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
axs[0].set_ylabel("false-positive rate at p ≤ 0.01 (%)")
fig.tight_layout()
C.save_fig(fig, "FA1")
for nm, v in (("s4_model", s4_model), ("s4_human", s4_human), ("qwen", qwen), ("phi", phi), ("h1", h1), ("h4", h4)):
    V.set(f"fa1_{nm}_max", C.f1(max(v)))
    V.set(f"fa1_{nm}_min", C.f1(min(v)))
    V.set(f"fa1_{nm}_above3", sum(x > 3 for x in v))
V.set("fa1_all_max", C.f1(max(max(v) for v in (s4_model, s4_human, qwen, phi, h1, h4))))
p = V.save()
print("FA1 written; values:", p.name, len(V.d))
