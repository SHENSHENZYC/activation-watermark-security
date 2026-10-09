"""Build the Study 3 v0.1 report tables and figures from the locked outputs (numbers are never retyped).

Written during the run, before any Study 3 outcome was read (2026-09-30).
Reads research/outputs/study3_v0.1/results.json, the per-text features in research/study3/data/ (git-ignored), Study 1's
saved probe outputs, and Study 1 v0.2 / v0.4 results (the probe's verdicts on the same texts). Before writing anything
it re-computes, with its own implementation of the S4 test (not common_s3), the per-key FPRs on the model and human null
texts and the per-key oracle TPRs at every level, and the probe's per-key oracle acceptance from the raw scores, and
asserts that they equal results.json.
Writes to research/outputs/study3_v0.1/report/: tables.md, fig1_detection.png, fig2_forgeries.png,
fig3_calibration.png, fig4_leakage.png. Then assembles research/STUDY3_REPORT_v0.1.md from report_prose.md
(placeholders <<TABLE1>>, <<TABLES>>) if the prose exists.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "study1"))
import core  # noqa: E402  (keys only: make_key, null-key seeds)

RES = ROOT / "outputs" / "study3_v0.1" / "results.json"
D3S, D2 = ROOT / "study3" / "data", ROOT / "study1_v02" / "data"
OUT = ROOT / "outputs" / "study3_v0.1" / "report"
R02 = json.loads((ROOT / "outputs" / "study1_v0.2" / "results.json").read_text())
R04 = json.loads((ROOT / "outputs" / "study1_v0.4" / "results.json").read_text())
KEYS = list(range(1001, 1009))
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
LATE = ["0.35", "0.5", "0.7"]
TAG = {"0.25": "025", "0.35": "035", "0.5": "050", "0.7": "070"}
ROUTES = "AB"
N_REF, D = 56.90270233154297, 1536
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dc"
EXACT, PROBE = "#1baf7a", "#52514e"          # exact test: categorical slot 3 (aqua); probe: recessive gray (emphasis)
COL = {"A": "#2a78d6", "B": "#eb6834"}      # routes, as in the Study 1 reports (slots 1-2)

res = json.loads(RES.read_text())
P4, P3 = res["S4"], res["S3"]
CAL = [int(s) for s in P4["G2"]["calibrated_keys"]]


def jl(p):
    return json.loads(p.read_text())


# ---------------------------------------------------------------- independent re-computation (asserted)
def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def key_unit(seed):
    return unit(core.make_key(seed, D, 1.0).numpy().astype(np.float64))


NULL = np.stack([key_unit(core.NULL_KEY_SEED * 100000 + j) for j in range(999)])
Gf = np.load(D3S / "S_F_van.npz")["G"].astype(np.float64)
MU, SD = Gf.mean(0), np.maximum(Gf.std(0, ddof=1), 1e-12)


def s4_accept(name, seed):
    X = unit((np.load(D3S / f"{name}.npz")["G"].astype(np.float64) - MU) / SD)
    t, tn = X @ key_unit(seed), X @ NULL.T
    return ((1 + (tn >= t[:, None]).sum(1)) / 1000 <= 0.01).astype(float)


for s in KEYS:
    for nm, blk in (("S_A_van", "G2"), ("S_A_human", "H1")):
        got = 100 * s4_accept(nm, s).mean()
        assert abs(got - P4[blk]["per_key_fpr_pct"][str(s)]) < 1e-9, (nm, s, got)
for lv in LEVELS:
    pk = [float(s4_accept(f"K_k{s}_r{TAG[lv]}_oracle", s).mean()) for s in CAL]
    assert np.allclose(pk, P4["levels"][lv]["oracle"]["acceptance"]["per_key"], atol=1e-12), lv
    probe = [float((np.asarray(jl(D2 / f"K_k{s}_r{TAG[lv]}_summary.json")["scores_oracle"]) >
                    jl(D2 / f"K_k{s}_r{TAG[lv]}_summary.json")["threshold"]).mean()) for s in CAL]
    assert float(np.median(probe)) == P4["levels"][lv]["oracle"]["probe_acceptance_median"], lv
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- tables
def pct(x):
    return f"{100 * x:.1f}"


def ci(c):
    return f"[{pct(c[0])}, {pct(c[1])}]"


def cname(c):
    if c in ("oracle", "random", "E"):
        return {"oracle": "oracle (genuine, pool D)", "random": "random key (generic steering)",
                "E": "genuine, pool E (200)"}[c]
    v, r, n = c.split("_")
    return f"{v.replace('v0', 'v0.')} Route {r}, n = {n[1:]}"


def conds(lv):
    cs = ["oracle", "E", "random"] + [f"v02_{r}_n{n}" for r in ROUTES for n in (64, 256, 1024)]
    if lv in LATE:
        cs += [f"v0{v}_{r}_n{n}" for v in (3, 4) for r in ROUTES for n in (64, 256)]
    return cs


T = ["## Table 1 — Pre-registered rules vs observed (protocol §7), with Study 1's verdicts under the probe on the same texts\n"]
g1, g2 = P4["G1"], P4["G2"]
T.append(f"**G1** (pooled FPR on pool A's 1,000 unwatermarked texts × 8 keys, pass if {g1['range'][0]}–{g1['range'][1]}%): "
         f"{g1['pooled_fpr_pct']:.2f}% → **{'PASS' if g1['pass'] else 'FAIL'}**. **G2** (a key is calibrated if its FPR "
         f"≤ {g2['max_pct']}%): {g2['n_calibrated']} of 8 calibrated → **{'STOP' if g2['stop'] else 'PASS'}** "
         f"(per-key FPR: " + ", ".join(f"{s} {v:.1f}%" for s, v in g2["per_key_fpr_pct"].items()) + ").\n")
T.append("| ρ | P1 oracle TPR, exact (≥ 20%) | E1 exact − probe TPR, median [95% CI] | E1 verdict | X1 Route A (exact) | "
         "X1 Route B (exact) | X3 (exact) | Study 1 v0.4 F1 A / B (probe) | Study 1 v0.4 F3 (probe) |")
T.append("|---|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = P4["levels"][lv]
    e1 = L["E1"]
    x1 = L.get("X1", "n/a (no v0.4 forgeries at 0.25)")
    xa, xb = (x1["A"], x1["B"]) if isinstance(x1, dict) else (x1, x1)
    s1 = R04["levels"][lv]["rules"] if lv in LATE else None
    T.append(f"| {lv} | {pct(L['P1']['oracle_tpr_median'])}% ({'pass' if L['P1']['pass'] else 'fail'}) | "
             f"{100 * e1['median_diff_exact_minus_probe']:+.1f} {ci(e1['ci95'])} | {e1['verdict']} | {xa} | {xb} | "
             f"{'yes' if L['X3_fluent_generic_steering_suffices'] else 'no'} | "
             + (f"{s1['F1']['A']} / {s1['F1']['B']} | {'yes' if s1['F3_fluent_generic_steering_suffices'] else 'no'} |"
                if s1 else "— | — |"))
T.append("\nX1 and X3 use exact-FA: accepted by the exact test (S4, p ≤ 0.01) **and** fluent by v0.4's definition "
         "(perplexity and seq-rep-4 at most the key-level oracle's 95th percentiles). Forms as v0.4's F1 and F3; bar = 50% "
         "of the oracle's median exact-FA: " + "; ".join(f"ρ = {lv}: {pct(P4['levels'][lv]['X1_bar'])}%" for lv in LEVELS) + ".\n")

T.append("## Table 2 — Per-key false-positive rates at p ≤ 0.01 (%): S4 (primary) and S3 (secondary), on pool A's 1,000 "
         "unwatermarked model texts and its 1,000 human continuations\n")
T.append("| statistic | null set | " + " | ".join(str(s) for s in KEYS) + " | pooled | keys > 3.0% |")
T.append("|---|---|" + "---|" * (len(KEYS) + 2))
for nm, P in (("S4", P4), ("S3", P3)):
    for blk, lab in (("G2", "model"), ("H1", "human")):
        v = P[blk]["per_key_fpr_pct"]
        pooled = P["G1"]["pooled_fpr_pct"] if blk == "G2" else P["H1"]["pooled_fpr_pct"]
        T.append(f"| {nm} | {lab} | " + " | ".join(f"{v[str(s)]:.1f}" for s in KEYS) +
                 f" | {pooled:.2f} | {sum(v[str(s)] > 3.0 for s in KEYS)} |")
T.append(f"\nAt p ≤ 0.001 with 9,999 null keys (S4, secondary): pooled FPR {P4['alpha_0.001']['pooled_fpr_model_pct']:.2f}% "
         f"(model), {P4['alpha_0.001']['pooled_fpr_human_pct']:.2f}% (human). The owner's probe on the human continuations of "
         f"pool A2 (Study 1 v0.2): {100 * R02['human_FPR_A2']:.1f}% pooled.\n")

T.append("## Table 3 — Acceptance by the owner's probe and by the exact test on the same texts (median over calibrated keys, %; "
         "exact with 95% cluster-bootstrap CI), and fluent acceptance (FA, v0.4 definition)\n")
T.append("| ρ | texts | probe accepts | exact accepts [95% CI] | probe FA | exact FA [95% CI] | both accept | either accepts |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    L = P4["levels"][lv]
    for c in conds(lv):
        e = L[c]
        a = f"{pct(e['acceptance']['median'])} {ci(e['acceptance']['ci95'])}"
        if "exact_FA" in e:
            T.append(f"| {lv} | {cname(c)} | {pct(e['probe_acceptance_median'])} | {a} | {pct(e['probe_FA_median'])} | "
                     f"{pct(e['exact_FA']['median'])} {ci(e['exact_FA']['ci95'])} | {pct(e['both_acceptance_median'])} | "
                     f"{pct(e['either_acceptance_median'])} |")
        else:
            T.append(f"| {lv} | {cname(c)} | — | {a} | — | — | — | — |")
T.append("\nFPR of the joint detectors on pool A2 (the probe's own check set; median over calibrated keys): " + "; ".join(
    f"ρ = {lv}: both {pct(P4['levels'][lv]['A2_joint_fpr']['both_median'])}%, either "
    f"{pct(P4['levels'][lv]['A2_joint_fpr']['either_median'])}%" for lv in LEVELS) + ".\n")

T.append("## Table 4 — Key-leakage lens (secondary): forgeries' exact p-values, pooled tests, and the attacker's recovered "
         "cosine (median over calibrated keys, %)\n")
T.append("| ρ | forgeries | exact accepts (p ≤ 0.01) | p ≤ 0.05 | p ≤ 0.10 | 4 texts pooled: detected | at p ≤ 0.001 (M = 9,999) "
         "| median cos(v̂, v) |")
T.append("|---|---|---|---|---|---|---|---|")
LEAK = []
for lv in LEVELS:
    L = P4["levels"][lv]
    for c in [x for x in conds(lv) if x.startswith("v0")] + ["random", "oracle"]:
        e = L[c]
        cs = f"{np.median(e['cos_to_key_per_key']):.3f}" if "cos_to_key_per_key" in e else "—"
        T.append(f"| {lv} | {cname(c)} | {pct(e['acceptance']['median'])} | {pct(e['p_le_0.05_median'])} | "
                 f"{pct(e['p_le_0.10_median'])} | {pct(e['pooled4_detection_median'])} | "
                 f"{pct(e['acceptance_0.001_median'])} | {cs} |")
        if "cos_to_key_per_key" in e:
            LEAK += [(lv, c, x, y) for x, y in zip(e["cos_to_key_per_key"], e["acceptance_per_key"])]
for r in ROUTES:
    pts = [(x, y) for _, c, x, y in LEAK if c.split("_")[1] == r]
    rho_s, p_s = spearmanr([p[0] for p in pts], [p[1] for p in pts])
    T.append(f"\nRoute {r}: Spearman correlation between the attacker's cos(v̂, v) and the forgery's exact acceptance, over "
             f"all key-levels and forgery sets: {rho_s:.2f} (n = {len(pts)}; descriptive).")
T.append("")

T.append("## Table 5 — Secondary statistic S3 (unstandardised gradient) beside S4: headline numbers (median over the keys "
         "each statistic calibrates, %)\n")
T.append("| ρ | statistic | calibrated keys | oracle TPR | random-key acceptance | v0.4 B n=256 exact FA | X1 A | X1 B |")
T.append("|---|---|---|---|---|---|---|---|")
for lv in LEVELS:
    for nm, P in (("S4", P4), ("S3", P3)):
        if not P.get("levels"):
            T.append(f"| {lv} | {nm} | {P['G2']['n_calibrated']} | — | — | — | — | — |")
            continue
        L = P["levels"][lv]
        x1 = L.get("X1", "—")
        xa, xb = (x1["A"], x1["B"]) if isinstance(x1, dict) else (x1, x1)
        fb = pct(L["v04_B_n256"]["exact_FA"]["median"]) if "v04_B_n256" in L else "—"
        T.append(f"| {lv} | {nm} | {P['G2']['n_calibrated']} | {pct(L['oracle']['acceptance']['median'])} | "
                 f"{pct(L['random']['acceptance']['median'])} | {fb} | {xa} | {xb} |")
T.append("")

T.append("## Table 6 — Per-key exact acceptance (%, S4), keys in calibrated order; the probe's beside it\n")
T.append("| ρ | texts | detector | " + " | ".join(str(s) for s in CAL) + " |")
T.append("|---|---|---|" + "---|" * len(CAL))
for lv in LEVELS:
    for c in ["oracle", "random"] + (["v04_A_n256", "v04_B_n256"] if lv in LATE else ["v02_A_n256", "v02_B_n256"]):
        e = P4["levels"][lv][c]
        T.append(f"| {lv} | {cname(c)} | exact | " + " | ".join(f"{100 * x:.0f}" for x in e["acceptance"]["per_key"]) + " |")
T.append("")
tables = "\n".join(T) + "\n"
(OUT / "tables.md").write_text(tables)

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6})
rho = [float(v) for v in LEVELS]

# Fig 1: detection at an exact 1% FPR, genuine vs random-key texts, exact test vs probe
fig, ax = plt.subplots(figsize=(6.4, 4.4))
for c, ls, mk, lab in (("oracle", "-", "o", "genuine (oracle)"), ("random", "--", "s", "random key (generic steering)")):
    m = [100 * P4["levels"][lv][c]["acceptance"]["median"] for lv in LEVELS]
    lo = [100 * P4["levels"][lv][c]["acceptance"]["ci95"][0] for lv in LEVELS]
    hi = [100 * P4["levels"][lv][c]["acceptance"]["ci95"][1] for lv in LEVELS]
    ax.fill_between(rho, lo, hi, color=EXACT, alpha=0.12, linewidth=0)
    ax.plot(rho, m, ls, color=EXACT, lw=2, marker=mk, ms=7, label=f"exact test (S4): {lab}")
    pm = [100 * R02["levels"][lv][c]["median"] for lv in LEVELS]
    plo = [100 * R02["levels"][lv][c]["ci95"][0] for lv in LEVELS]
    phi = [100 * R02["levels"][lv][c]["ci95"][1] for lv in LEVELS]
    ax.fill_between(rho, plo, phi, color=PROBE, alpha=0.08, linewidth=0)
    ax.plot(rho, pm, ls, color=PROBE, lw=1.6, marker=mk, ms=7, mfc="white", label=f"owner's probe: {lab}")
ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.text(0.595, 2.5, "1% FPR", color=MUTED, fontsize=7.5, va="bottom", ha="center")
ax.set_xticks(rho)
ax.set_xlim(0.22, 0.78)
ax.set_ylim(-3, 104)
ax.set_xlabel("Watermark strength ρ = ‖v‖ / median activation norm")
ax.set_ylabel("Texts attributed to the key at a 1% FPR (%)")
ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
ax.set_title("Study 3: the exact key test vs the owner's probe on the same texts\n(median over keys, 95% CI; 256-token texts)",
             fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig1_detection.png", dpi=200)
plt.close(fig)

# Fig 2: forgeries and controls, probe vs exact acceptance (dumbbell), one panel per level
ROWS = ["oracle", "random", "v02_A_n256", "v02_B_n256", "v02_A_n1024", "v02_B_n1024", "v03_A_n256", "v03_B_n256",
        "v04_A_n256", "v04_B_n256"]
fig, axs = plt.subplots(1, 4, figsize=(10.5, 4.6), sharey=True)
for ax, lv in zip(axs, LEVELS):
    L = P4["levels"][lv]
    for i, c in enumerate(ROWS):
        if c not in L:
            continue
        p, e = 100 * L[c]["probe_acceptance_median"], 100 * L[c]["acceptance"]["median"]
        ax.plot([p, e], [i, i], color=GRID, lw=2.4, zorder=1)
        ax.scatter([p], [i], s=46, color="white", edgecolor=PROBE, linewidth=1.4, zorder=2,
                   label="owner's probe" if i == 0 else None)
        ax.scatter([e], [i], s=46, color=EXACT, edgecolor="white", linewidth=1.0, zorder=3,
                   label="exact test (S4)" if i == 0 else None)
    ax.axvline(1, color=MUTED, lw=1, ls=":")
    ax.set_xlim(-4, 104)
    ax.set_title(f"ρ = {lv}", fontsize=9, color=INK)
    ax.set_xlabel("accepted (%)")
axs[0].set_yticks(range(len(ROWS)), [cname(c) for c in ROWS], fontsize=7.5)
axs[0].invert_yaxis()
h, lab = axs[0].get_legend_handles_labels()
fig.legend(h, lab, frameon=False, fontsize=8, loc="lower center", ncol=2, bbox_to_anchor=(0.55, 0.0))
fig.suptitle("Study 1's genuine, random-key and forged texts: accepted by the owner's probe (hollow) vs the exact key test "
             "(filled); median over keys; dotted line = 1% FPR", fontsize=9, color=INK, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(OUT / "fig2_forgeries.png", dpi=200)
plt.close(fig)

# Fig 3: per-key calibration, S4 vs S3, model and human null texts
fig, ax = plt.subplots(figsize=(6.4, 3.6))
x = np.arange(len(KEYS))
for nm, P, col, off in (("S4 (primary)", P4, EXACT, -0.12), ("S3 (secondary)", P3, PROBE, 0.12)):
    for blk, filled, lab in (("G2", True, "model text"), ("H1", False, "human text")):
        v = [P[blk]["per_key_fpr_pct"][str(s)] for s in KEYS]
        ax.scatter(x + off, v, s=40, marker="o" if filled else "D", color=col if filled else "white", edgecolor=col,
                   linewidth=1.3, zorder=3, label=f"{nm}, {lab}")
ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.axhline(3, color=INK, lw=1, ls="--")
ax.text(len(KEYS) - 0.45, 3, "G2 bar 3%", color=INK, fontsize=7.5, va="bottom", ha="right")
ax.text(len(KEYS) - 0.45, 1, "nominal 1%", color=MUTED, fontsize=7.5, va="bottom", ha="right")
ax.set_xticks(x, [str(s) for s in KEYS])
ax.set_xlabel("study key")
ax.set_ylabel("false-positive rate at p ≤ 0.01 (%)")
ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
ax.set_title("Per-key calibration on 1,000 unwatermarked model texts and 1,000 human continuations", fontsize=9,
             color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig3_calibration.png", dpi=200)
plt.close(fig)

# Fig 4: key leakage, exact acceptance of forgeries against the attacker's cos(v_hat, v)
fig, ax = plt.subplots(figsize=(6.4, 4.8))
MK = {"v02": "o", "v03": "s", "v04": "D"}
for r in ROUTES:
    for v in MK:
        pts = [(a, b) for lv, c, a, b in LEAK if c.startswith(v) and c.split("_")[1] == r]
        if pts:
            ax.scatter([p[0] for p in pts], [100 * p[1] for p in pts], s=26, marker=MK[v], color=COL[r], alpha=0.75,
                       edgecolor="white", linewidth=0.6, label=f"Route {r}, {v.replace('v0', 'v0.')}")
ax.axhline(1, color=MUTED, lw=1, ls=":")
ax.set_xlabel("attacker's recovered cosine cos(v̂, v)")
ax.set_ylabel("forgeries accepted by the exact test (%)")
ax.legend(frameon=False, fontsize=7.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.16))
ax.set_title("Key leakage: forgeries accepted by the exact test vs the attacker's recovered cosine\n"
             "(one point per key-level and forgery set; all n and levels)", fontsize=9, color=INK, loc="left")
fig.tight_layout()
fig.savefig(OUT / "fig4_leakage.png", dpi=200)
plt.close(fig)
print("ok: integrity asserts passed; wrote", sorted(p.name for p in OUT.iterdir()))

# ---------------------------------------------------------------- values quoted in the prose ([[name]] placeholders)
import datetime as dt  # noqa: E402
import re  # noqa: E402

MAN = json.loads((ROOT / "outputs" / "study3_v0.1" / "RUN_MANIFEST.json").read_text())
end = dt.datetime.strptime(MAN["finished_utc"], "%Y-%m-%dT%H:%M:%SZ")
start = end - dt.timedelta(seconds=MAN["seconds"])
LV = {"0.25": "25", "0.35": "35", "0.5": "50", "0.7": "70"}
V = {"start_utc": start.strftime("%H:%M"), "start_ct": (start - dt.timedelta(hours=5)).strftime("%H:%M"),
     "end_utc": end.strftime("%H:%M"), "end_ct": (end - dt.timedelta(hours=5)).strftime("%H:%M"),
     "seconds": f"{MAN['seconds']:,.0f}", "hours": f"{MAN['seconds'] / 3600:.1f}",
     "g1": f"{g1['pooled_fpr_pct']:.2f}", "n_cal": str(g2["n_calibrated"]),
     "g2_min": f"{min(g2['per_key_fpr_pct'].values()):.1f}", "g2_max": f"{max(g2['per_key_fpr_pct'].values()):.1f}",
     "h1_pooled": f"{P4['H1']['pooled_fpr_pct']:.2f}", "h1_max": f"{max(P4['H1']['per_key_fpr_pct'].values()):.1f}",
     "probe_human": f"{100 * R02['human_FPR_A2']:.1f}",
     "fpr2_model": f"{P4['alpha_0.001']['pooled_fpr_model_pct']:.2f}",
     "fpr2_human": f"{P4['alpha_0.001']['pooled_fpr_human_pct']:.2f}"}
for lv, k in LV.items():
    L = P4["levels"][lv]
    V.update({f"tpr_exact_{k}": pct(L["oracle"]["acceptance"]["median"]),
              f"tpr_probe_{k}": pct(L["oracle"]["probe_acceptance_median"]),
              f"e1_{k}": f"{100 * L['E1']['median_diff_exact_minus_probe']:+.1f}",
              f"e1_ci_{k}": ci(L["E1"]["ci95"]), f"rnd_exact_{k}": pct(L["random"]["acceptance"]["median"]),
              f"rnd_probe_{k}": pct(L["random"]["probe_acceptance_median"]), f"bar_{k}": pct(L["X1_bar"]),
              f"oracle_fa_{k}": pct(L["oracle"]["exact_FA"]["median"]),
              f"tpr2_{k}": pct(L["oracle"]["acceptance_0.001_median"]),
              f"e_tpr_{k}": pct(L["E"]["acceptance"]["median"])})
V04 = [(lv, r, n) for lv in LATE for r in ROUTES for n in (64, 256)]
fa4 = {x: P4["levels"][x[0]][f"v04_{x[1]}_n{x[2]}"]["exact_FA"] for x in V04}
V["v04fa_max"] = pct(max(f["median"] for f in fa4.values()))
V["v04fa_min"] = pct(min(f["median"] for f in fa4.values()))
worst = max(V04, key=lambda x: fa4[x]["ci95"][1] / P4["levels"][x[0]]["X1_bar"])
V["x1_edge"] = (f"Route {worst[1]} at ρ = {worst[0]}, n = {worst[2]}: upper 95% bound {pct(fa4[worst]['ci95'][1])}% "
                f"against the bar {pct(P4['levels'][worst[0]]['X1_bar'])}%")
rx = [pct(P4["levels"][lv]["random"]["acceptance"]["median"]) for lv in LEVELS]
V["rnd_exact_all"] = (f"{rx[0]}% at all four levels" if len(set(rx)) == 1 else
                      ", ".join(f"{x}% at ρ = {lv}" for x, lv in zip(rx, LEVELS)))
V["b256_probe_fa_35"] = pct(P4["levels"]["0.35"]["v04_B_n256"]["probe_FA_median"])
V["b256_exact_fa_35"] = pct(P4["levels"]["0.35"]["v04_B_n256"]["exact_FA"]["median"])
V["both_max"] = pct(max(P4["levels"][lv]["A2_joint_fpr"]["both_median"] for lv in LEVELS))
V["either_min"] = pct(min(P4["levels"][lv]["A2_joint_fpr"]["either_median"] for lv in LEVELS))
V["either_max"] = pct(max(P4["levels"][lv]["A2_joint_fpr"]["either_median"] for lv in LEVELS))
V["s3_ncal"] = str(P3["G2"]["n_calibrated"])
w3 = max(P3["G2"]["per_key_fpr_pct"], key=lambda s: P3["G2"]["per_key_fpr_pct"][s])
V["s3_worst"] = f"key {w3} at {P3['G2']['per_key_fpr_pct'][w3]:.1f}%"
FORG = [(lv, c) for lv in LEVELS for c in conds(lv) if c.startswith("v0")]
p10 = [P4["levels"][lv][c]["p_le_0.10_median"] for lv, c in FORG]
V["p10_forg_min"], V["p10_forg_max"] = pct(min(p10)), pct(max(p10))
p10r = [P4["levels"][lv]["random"]["p_le_0.10_median"] for lv in LEVELS]
V["p10_rnd_min"], V["p10_rnd_max"] = pct(min(p10r)), pct(max(p10r))
for r in ROUTES:
    pts = [(x, y) for _, c, x, y in LEAK if c.split("_")[1] == r]
    V[f"spear_{r}"] = f"{spearmanr([q[0] for q in pts], [q[1] for q in pts])[0]:.2f}"
cells = [(lv, c, s, a) for lv, c in FORG for s, a in zip(CAL, P4["levels"][lv][c]["acceptance_per_key"])]
V["leak_n50"] = str(sum(a >= 0.5 for *_, a in cells))
V["leak_total"] = str(len(cells))
hi4 = [f"{c.split('_')[1]} key {s} at ρ = {lv} ({100 * a:.0f}%)" for lv, c, s, a in cells
       if c.startswith("v04") and c.endswith("n256") and a >= 0.5]
V["leak_v04_list"] = "; ".join(hi4) if hi4 else "none"
pool = [(P4["levels"][lv][c]["pooled4_detection_median"], lv, c) for lv, c in FORG]
pm = max(pool)
V["pool_forg_max"] = f"{pct(pm[0])}% ({cname(pm[2])} at ρ = {pm[1]})"
V["pool_forg_typ"] = pct(float(np.median([q[0] for q in pool])))
i1002 = CAL.index(1002)
V["k1002_tpr70"] = f"{100 * P4['levels']['0.7']['oracle']['acceptance']['per_key'][i1002]:.0f}"
V["k1002_fpr"] = f"{P4['G2']['per_key_fpr_pct']['1002']:.1f}"
Xo = unit((np.load(D3S / "K_k1002_r070_oracle.npz")["G"].astype(np.float64) - MU) / SD)   # exploratory, after the run
po = (1 + ((Xo @ NULL.T) >= (Xo @ key_unit(1002))[:, None]).sum(1)) / 1000
V["k1002_medp70"] = f"{np.median(po):.3f}"
V["others_tpr70_min"] = f"{100 * min(x for i, x in enumerate(P4['levels']['0.7']['oracle']['acceptance']['per_key']) if i != i1002):.0f}"

(OUT / "prose_values.json").write_text(json.dumps(V, indent=2, ensure_ascii=False))

# ---------------------------------------------------------------- assemble the report (only if the prose exists)
pf = Path(__file__).parent / "report_prose.md"
if not pf.exists():
    sys.exit("report_prose.md not written yet; assets only")
prose = pf.read_text()
for ph in ("<<TABLE1>>", "<<TABLES>>"):
    assert prose.count(ph) == 1, ph
missing = sorted(set(re.findall(r"\[\[(\w+)\]\]", prose)) - set(V))
assert not missing, f"unknown placeholders: {missing}"
prose = re.sub(r"\[\[(\w+)\]\]", lambda m: V[m.group(1)], prose)
t1, rest = tables.split("## Table 2", 1)
report = (prose.replace("<<TABLE1>>", t1.replace("## Table 1", "### Table 1").strip())
          .replace("<<TABLES>>", ("## Table 2" + rest).replace("## Table", "### Table").strip()))
(ROOT / "STUDY3_REPORT_v0.1.md").write_text(report)
print("wrote", ROOT / "STUDY3_REPORT_v0.1.md")
