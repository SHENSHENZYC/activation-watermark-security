"""Builds POWER_PILOT_REPORT_v0.1.md from outputs/study3_pilot_v0.1/results.json. No number is typed by hand.

Written before the pilot's outcomes were read (2026-09-30); the prose in PROSE is added after reading them and quotes
numbers only through the fields of results.json.
Run: .venv/bin/python research/study3_pilot/make_report.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "research" / "outputs" / "study3_pilot_v0.1"
R = json.loads((OUT / "results.json").read_text())
V = json.loads((OUT / "VALIDATION.json").read_text())
CANDS = ["S1", "S2", "S3", "S4"]
NAMES = {"S1": "S1 raw cosine", "S2": "S2 standardised cosine", "S3": "S3 gradient score",
         "S4": "S4 standardised gradient score"}
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
WORKING = ["0.35", "0.5", "0.7"]


def rng(per):
    v = list(per.values())
    return f"{min(v):.0f}–{max(v):.0f}"


def table_rule():
    s = R["selection"]
    rows = ["| Candidate | FPR check (400 texts × 4 keys; pass if 0.3–2.5%) | Score (mean over ρ 0.35/0.50/0.70 of median TPR, %) |",
            "|---|---|---|"]
    for c in CANDS:
        f = R["fpr_check"][c]
        rows.append(f"| {NAMES[c]} | {f['rate_pct']:.2f}% ({'pass' if f['pass'] else 'FAIL'}) | {R['score'][c]:.1f} |")
    rows.append("")
    rows.append(f"**Implementation check:** {'pass' if s['implementation_check_pass'] else 'FAIL'}. "
                f"**Top score:** {s['top_score']:.1f}; within the 2.0-point tie margin: {', '.join(s['within_tie_margin'])}. "
                f"**Primary (by the rule): {NAMES.get(s['primary'], 'none')}.** **Viability:** {s['viability']}.")
    return "\n".join(rows)


def table_levels(block, fmt, title_note):
    rows = [f"| Candidate | " + " | ".join(f"ρ = {l}" + (" (descriptive)" if l == "0.25" else "") for l in LEVELS) + " |",
            "|---|" + "---|" * len(LEVELS)]
    for c in CANDS:
        cells = []
        for l in LEVELS:
            e = R[block][c][l]
            cells.append(fmt(e))
        rows.append(f"| {NAMES[c]} | " + " | ".join(cells) + " |")
    return title_note + "\n\n" + "\n".join(rows)


def table_pooled():
    rows = ["| Candidate | texts per test | " + " | ".join(f"ρ = {l}" for l in LEVELS) + " | unwatermarked (FPR) |",
            "|---|---|" + "---|" * (len(LEVELS) + 1)]
    for c in CANDS:
        for n in ["4", "16"]:
            e = R["pooled"][c][n]
            cells = [f"{e['tpr'][l]['median']:.0f} [{rng(e['tpr'][l]['per_key'])}]" for l in LEVELS]
            rows.append(f"| {NAMES[c]} | {n} ({e['tpr']['0.5']['batches_per_key']} per key) | " + " | ".join(cells)
                        + f" | {e['fpr_pct']:.1f}% |")
    return "\n".join(rows)


def build(prose=""):
    g = R["guard"]
    t = V["checks"]["6_timing"]
    parts = [
        "# Study 3 power pilot v0.1 — report",
        "",
        f"Date: 2026-09-30 (Milestone 5). Spec: [`POWER_PILOT_SPEC_v0.1.md`](POWER_PILOT_SPEC_v0.1.md), FIXED before any "
        f"statistic on watermarked texts (commit `{g['commit'][:7]}`; spec SHA-256 `{g['spec_sha256'][:12]}…`, script "
        f"`{g['script_sha256'][:12]}…`). Validation: [`../outputs/study3_pilot_v0.1/VALIDATION.json`]"
        f"(../outputs/study3_pilot_v0.1/VALIDATION.json) (all pass: {V['all_pass']}). Results: "
        "[`../outputs/study3_pilot_v0.1/results.json`](../outputs/study3_pilot_v0.1/results.json). **Built by** "
        "`make_report.py`; no number is typed by hand. Tuning keys 9001–9004 only; no study key, study-key text or "
        f"forgery was read. Exact key-resampling test with M = {R['M']} null keys, detection at p ≤ {R['alpha']}.",
        "",
        "## 1. Rule vs observed (spec: selection rule, fixed before the run)",
        "",
        table_rule(),
        "",
        "## 2. Tables",
        "",
        table_levels("tpr", lambda e: f"{e['median']:.0f} [{rng(e['per_key'])}]",
                     "### Table 1 — TPR at an exact 1% FPR, single texts (median over 4 tuning keys, % [min–max over keys])"),
        "",
        table_levels("auroc", lambda e: f"{e['median']:.3f} [{min(e['per_key'].values()):.3f}–{max(e['per_key'].values()):.3f}]",
                     "### Table 2 — AUROC of the key's statistic, watermarked vs the 400 unwatermarked texts (median over keys [min–max])"),
        "",
        table_levels("cross_key", lambda e: f"{e['rate_pct']:.1f}% (n = {e['n_tests']})",
                     "### Table 3 — Cross-key detection (text steered by one tuning key, tested with another; generic steering; about 1% expected by construction)"),
        "",
        "### Table 4 — Pooled tests: detection when *n* texts of one key are tested together (median over keys, % [min–max]), and on unwatermarked batches",
        "",
        table_pooled(),
        "",
        f"Coordinate-scale spread in the owner's reference set (max / median of the per-coordinate standard deviation): "
        f"activations {R['ref_scale_spread']['sd_a_max_over_median']:.1f}, gradients "
        f"{R['ref_scale_spread']['sd_g_max_over_median']:.1f}.",
        f"Timing: {t['s_per_text']:.2f} s per text (one forward and one backward pass, batch 1).",
        "",
        prose,
    ]
    (HERE / "POWER_PILOT_REPORT_v0.1.md").write_text("\n".join(parts).rstrip() + "\n")


def prose():
    P = json.loads((OUT / "posthoc_diagnostics.json").read_text())
    s, cf, cs = R["selection"], P["conditional_fpr"], P["s1_calibration_split"]
    tp = lambda c, l: R["tpr"][c][l]["median"]  # noqa: E731
    lo = lambda c: min(tp(c, l) for l in WORKING)  # noqa: E731
    hi = lambda c: max(tp(c, l) for l in WORKING)  # noqa: E731
    au = [R["auroc"][c][l]["median"] for c in ("S3", "S4") for l in LEVELS]
    ck = [R["cross_key"][c][l]["rate_pct"] for c in ("S3", "S4") for l in LEVELS]
    return "\n".join([
        "## 3. Reading",
        "",
        "### Pre-registered outcome (mechanical)",
        f"- **The implementation check fails for S1** ({R['fpr_check']['S1']['rate_pct']:.2f}% of "
        f"{R['fpr_check']['S1']['n_tests']:,} unwatermarked tests, below the 0.3% floor). S2, S3 and S4 pass "
        f"({R['fpr_check']['S2']['rate_pct']:.2f}%, {R['fpr_check']['S3']['rate_pct']:.2f}%, "
        f"{R['fpr_check']['S4']['rate_pct']:.2f}%). **By the rule, no primary is chosen.**",
        "- The viability line in §1 (\"not usable\") follows from \"no primary\", not from the TPRs; stated plainly, "
        f"S3 and S4 have median TPR ≥ 20% at every level (S3 {lo('S3'):.0f}–{hi('S3'):.0f}%, S4 {lo('S4'):.0f}–{hi('S4'):.0f}% "
        "at the three working levels).",
        "- **What the check did not foresee (my error, stated plainly):** it was meant to catch code bugs, and it "
        "pooled four fixed keys. A statistic can be exact on average over keys yet far from 1% for any one fixed key; "
        "S1 is such a statistic (below). The rule's wording (\"no candidate is chosen\") made one candidate's property "
        "block the choice among the others.",
        "",
        "### Diagnosis (written and run after the outcomes were read; exploratory)",
        "Script `posthoc_diag.py`; output [`../outputs/study3_pilot_v0.1/posthoc_diagnostics.json`]"
        "(../outputs/study3_pilot_v0.1/posthoc_diagnostics.json).",
        "1. **Not a feature bug.** On the calibration's own test split, S1 reproduces calibration v0.1's cosine AUROC "
        "exactly: " + ", ".join(f"ρ = {l}: {cs[l]['s1_auroc_mean_over_keys']:.3f} vs {cs[l]['calibration_dcos_true_key']:.3f}"
                                for l in LEVELS) + ".",
        "2. **Key resampling is exact on average over keys, not per key.** Over "
        f"{cf['S1']['n_keys']:,} fresh random keys, each tested on the {cf['S1']['n_texts']} unwatermarked texts, S1's "
        f"mean FPR is {cf['S1']['mean_pct']:.2f}%, but {100 * cf['S1']['share_keys_0']:.1f}% of keys never fire and "
        f"{100 * cf['S1']['share_keys_gt50']:.1f}% fire on more than half of the texts (max {cf['S1']['max_pct']:.0f}%). "
        "The raw activation mean is nearly the same for every text (coordinate-scale spread "
        f"{R['ref_scale_spread']['sd_a_max_over_median']:.0f}×), so a key's rank among the null keys is almost fixed: "
        "a given key either never or always fires. The four tuning keys are all in the first group.",
        "3. **Per-key FPR of the other candidates** (same diagnostic; mean, 95th percentile, max; share of keys above 5%): "
        + "; ".join(f"{NAMES[c]} {cf[c]['mean_pct']:.2f}%, {cf[c]['p95_pct']:.2f}%, {cf[c]['max_pct']:.2f}%, "
                    f"{100 * cf[c]['share_keys_gt5']:.1f}%" for c in ("S2", "S3", "S4")) + ". "
        "Centring and scaling each coordinate (S4) keeps every key's FPR near 1%; the raw gradient (S3) leaves a few keys "
        "well above it.",
        "",
        "### Evidence (tuning keys only)",
        f"- The **gradient statistics detect the watermark on single 256-token texts** at an exact 1% FPR: S3 median TPR "
        f"{lo('S3'):.0f}–{hi('S3'):.0f}% and S4 {lo('S4'):.0f}–{hi('S4'):.0f}% at ρ = 0.35–0.70, and "
        f"{tp('S3', '0.25'):.0f}% / {tp('S4', '0.25'):.0f}% at ρ = 0.25; AUROC {min(au):.3f}–{max(au):.3f}. Pooling 4 texts "
        "gives 100% for both at every level.",
        f"- The **cosines do not**: S1 0% everywhere; S2 {min(tp('S2', l) for l in WORKING):.0f}–"
        f"{max(tp('S2', l) for l in WORKING):.0f}%.",
        f"- **Key-specific:** texts steered by another tuning key are detected at {min(ck):.1f}–{max(ck):.1f}% by S3 and "
        "S4 (about 1% by construction), so these tests detect the key, not steering in general.",
        "",
        "### Inference (not established)",
        f"- On these tuning keys the gradient test detects where the authors' MLP could not (calibration v0.1 MLP AUROC "
        f"{cs['0.25']['calibration_mlp_faithful']:.2f} at ρ = 0.25 and {cs['0.35']['calibration_mlp_faithful']:.2f} at "
        "0.35). If this holds on study keys, the calibrations' \"no detectable-and-fluent window\" is a property of the "
        "probe detector, not of the watermark, and Study 1's forgeries will face a much stronger key-specific test.",
        "- Four tuning keys and 100 texts per key: these are design estimates, not study results.",
    ])


if __name__ == "__main__":
    build(prose())
