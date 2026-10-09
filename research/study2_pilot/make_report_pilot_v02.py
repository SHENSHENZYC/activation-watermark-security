"""Build SCRUB_PILOT_REPORT_v0.2.md from pilot v0.2's outputs (results.json, VALIDATION.json); every number comes from
those files. Written before any v0.2 result existed (2026-10-01).
Run: .venv/bin/python research/study2_pilot/make_report_pilot_v02.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_report_pilot as M1  # noqa: E402  (v0.1's table helpers)

ROOT = HERE.parents[1]
OUT = ROOT / "research" / "outputs" / "study2_pilot_v0.2"
REPORT = HERE / "SCRUB_PILOT_REPORT_v0.2.md"
LEVELS = M1.LEVELS
ARMS = ["true", "est", "rand"]
BUDGETS = ["2%", "5%", "10%"]


def main():
    R = json.loads((OUT / "results.json").read_text())
    V = json.loads((OUT / "VALIDATION.json").read_text())
    c = R["checks"]
    f1, pf = M1.f1, M1.pf
    L = ["# Study 2 scrubbing pilot — report v0.2 (edit component; tuning keys only)\n",
         "Spec: [`SCRUB_PILOT_SPEC_v0.2.md`](SCRUB_PILOT_SPEC_v0.2.md) (FIXED 2026-10-01, before any v0.2 edit). Results: "
         "[`../outputs/study2_pilot_v0.2/results.json`](../outputs/study2_pilot_v0.2/results.json). **Built by "
         "`make_report_pilot_v02.py`; every number comes from the outputs.** v0.1's paraphrase results stand "
         "([`SCRUB_PILOT_REPORT_v0.1.md`](SCRUB_PILOT_REPORT_v0.1.md)). Scope: tuning keys only.\n",
         "## 1. Checks\n",
         f"Validation: {sum(x['pass'] for x in V['checks'].values())} of {len(V['checks'])} passed (float32 editor "
         f"against float32 autograd: r = {V['checks']['2_float32_editor']['r_fd_vs_fp32_autograd']:.5f}). Run commit "
         f"`{R['guard']['commit'][:7]}`.\n",
         "| check | rule | observed | verdict |", "|---|---|---|---|",
         f"| I1 contributions (float32 editor) | r ≥ 0.99; per-token Spearman ≥ 0.8 | r = {c['I1']['r']:.4f} "
         f"(slope {c['I1']['slope']:.3f}); per-token {c['I1']['per_token_spearman_median']:.2f} | {pf(c['I1']['pass'])} |",
         f"| I2 edits act on the key (0% → 5%) | E-true more negative than E-rand, p < 0.01 | p = {c['I2']['wilcoxon_p']:.1e}; "
         f"median change {c['I2']['median_change_true']:+.4f} vs {c['I2']['median_change_rand']:+.4f} | {pf(c['I2']['pass'])} |",
         f"| I3 bookkeeping | exact counts; drift ≤ 2% | {c['I3']['n_diff_exact']}; drift ok: {c['I3']['median_drift_le_2pct']} | "
         f"{pf(c['I3']['pass'])} |",
         f"| I5′ Study 2 time (revised scope) | ≤ {c['I5prime']['budget_h']:.0f} h | "
         f"{c['I5prime']['projection']['total_h']:.1f} h | {pf(c['I5prime']['pass'])} |\n",
         "### Projection (I5′)\n", "| part | value |", "|---|---|"]
    for k, v in c["I5prime"]["projection"].items():
        L.append(f"| {k.replace('_', ' ')} | {v:.2f} |")
    L.append("\n## 2. Edits with the float32 editor (medians over the 4 tuning keys, %)\n")
    names = [f"E-{a} {b}" for a in ARMS for b in BUDGETS]
    L.append(M1.method_table(R, names, "arm and budget") + "\n")
    for a in ARMS:
        e = R["edits"][a]
        obj = ""
        if "median_objective" in e:
            obj = "; attacker's objective (median) " + ", ".join(
                f"{'0' if k == '0' else f'{100 * float(k):.0f}%'}: {v:+.2f}" for k, v in e["median_objective"].items())
        L.append(f"- E-{a}: {e['edit_s_per_text']:.2f} s per text; peak {e['peak_gb']:.1f} GB; stalled {e['stalled']}" + obj + ".")
    L.append("\n## 3. Float32 editor (v0.2) vs bfloat16 editor (v0.1), same budgets: scrub success / detected after (%)\n")
    rows = ["| method | ρ | v0.2 success | v0.1 success | v0.2 detected after | v0.1 detected after |", "|---|---|---|---|---|---|"]
    for n in names:
        if n not in R["v01_bf16_same_budgets"]:
            continue
        for rho in LEVELS:
            m2 = R["methods"][n][rho]
            m1 = R["v01_bf16_same_budgets"][n][rho]
            rows.append(f"| {n} | {rho} | {f1(m2['success']['median'])} | {f1(m1['success'])} | "
                        f"{f1(m2['detected_after']['median'])} | {f1(m1['detected_after'])} |")
    L.append("\n".join(rows) + "\n")
    L.append("v0.1's E-rand used a different random stream and 2% rounds, so its rows differ by chance as well.\n")
    L.append("## 4. Scrub success per key (%)\n")
    L.append(M1.per_key_table(R, names) + "\n")
    L.append("## 5. Stricter quality readings (scrub success, median %)\n")
    rows = ["| method | ρ | human 95th pct (primary) | model-text 95th pct | human median |", "|---|---|---|---|---|"]
    for n in names:
        for rho in LEVELS:
            m = R["methods"][n][rho]
            rows.append(f"| {n} | {rho} | {f1(m['success']['median'])} | {f1(m['success_stricter_bars']['A_model_p95'])} | "
                        f"{f1(m['success_stricter_bars']['A_human_median'])} |")
    L.append("\n".join(rows) + "\n")
    L.append("## 6. Samples (ρ = 0.50, the first text of keys 9001 and 9002)\n")
    for s in R["samples"]:
        L.append(f"**Key {s['key']}, original** (p = {s['p_original']:.3f}):\n\n> " + s["original"][:700].replace("\n", " ") + "\n")
        for a in ARMS:
            for b in ("5%", "10%"):
                k = f"E-{a} {b}"
                L.append(f"**{k}** (p = {s['p_' + k]:.3f}):\n\n> " + s[k][:700].replace("\n", " ") + "\n")
    REPORT.write_text("\n".join(L))
    print(f"wrote {REPORT.name}")


if __name__ == "__main__":
    main()
