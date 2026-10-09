"""Build SCRUB_PILOT_REPORT_v0.1.md from the pilot's locked outputs (results.json, VALIDATION.json).

Every number in the report comes from those files; prose numbers are [[name]] placeholders filled here, and the script
fails if any placeholder is left unresolved. Written before any pilot result existed (2026-10-01).
Run: .venv/bin/python research/study2_pilot/make_report_pilot.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "research" / "outputs" / "study2_pilot_v0.1"
REPORT = HERE / "SCRUB_PILOT_REPORT_v0.1.md"
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
BUDGETS = ["2%", "5%", "10%", "20%"]
ARMS = ["true", "est", "rand"]
ARM_NAME = {"true": "E-true (true key)", "est": "E-est (stand-in estimate)", "rand": "E-rand (random edits)"}


def load(p):
    return json.loads(Path(p).read_text())


def f1(x):
    return "—" if x is None else f"{x:.1f}"


def f2(x):
    return "—" if x is None else f"{x:.2f}"


def pf(ok):
    return "**PASS**" if ok else "**FAIL**"


def method_table(R, names, label):
    rows = [f"| {label} | ρ | detected before | detected after | scrub success [keys ≥ 50%] | all quality conditions | "
            "perplexity ok | seq-rep ok | length ok | meaning ok | length ratio | perplexity ratio | cosine |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in names:
        for rho in LEVELS:
            m = R["methods"][n][rho]
            rows.append(f"| {n} | {rho} | {f1(m['detected_before']['median'])} | {f1(m['detected_after']['median'])} | "
                        f"{f1(m['success']['median'])} [{m['keys_success_ge_50']}] | {f1(m['pass']['all']['median'])} | "
                        f"{f1(m['pass']['ppl']['median'])} | {f1(m['pass']['rep']['median'])} | "
                        f"{f1(m['pass']['len']['median'])} | {f1(m['pass']['cos']['median'])} | "
                        f"{f2(m['median_len_ratio'])} | {f2(m['median_ppl_ratio'])} | {f2(m['median_cos'])} |")
    return "\n".join(rows)


def per_key_table(R, names):
    rows = ["| method | ρ | 9001 | 9002 | 9003 | 9004 |", "|---|---|---|---|---|---|"]
    for n in names:
        for rho in LEVELS:
            pk = R["methods"][n][rho]["success"]["per_key"]
            rows.append(f"| {n} | {rho} | " + " | ".join(f1(pk[k]) for k in ("9001", "9002", "9003", "9004")) + " |")
    return "\n".join(rows)


def main():
    R = load(OUT / "results.json")
    V = load(OUT / "VALIDATION.json")
    models = sorted({k.split()[0][2:] for k in R["methods"] if k.startswith("P-")})
    P = {}                                                     # placeholder values
    chk = R["checks"]
    P.update({"i1_r": f"{chk['I1']['r']:.4f}", "i1_slope": f"{chk['I1']['slope']:.3f}",
              "i1_tok": f"{chk['I1']['per_token_spearman_median']:.2f}",
              "i2_p": f"{chk['I2']['wilcoxon_p']:.1e}", "i2_true": f"{chk['I2']['median_change_true']:+.4f}",
              "i2_rand": f"{chk['I2']['median_change_rand']:+.4f}",
              "i5_total": f"{chk['I5']['projection']['total_h']:.1f}", "i5_budget": f"{chk['I5']['budget_h']:.0f}",
              "a2_choice": f"{100 * R['rule_A2']['chosen_round_frac']:.0f}%",
              "bar_ppl": f"{R['bars']['A']['ppl']:.1f}", "bar_rep": f"{R['bars']['A']['rep']:.3f}",
              "bar_cos": f"{R['bars']['A']['cos']:.3f}", "bar_model_ppl": f"{R['bars']['A_model_p95']['ppl']:.2f}",
              "bar_human_med": f"{R['bars']['A_human_median']['ppl']:.1f}",
              "c_ppl": f"{R['bars']['C']['ppl']:.1f}", "c_cos": f"{R['bars']['C']['cos']:.3f}",
              "hours": f"{sum(R['times_s'].values()) / 3600:.1f}", "commit": R["guard"].get("commit", "")[:7],
              "n_val_pass": str(sum(c["pass"] for c in V["checks"].values())), "n_val": str(len(V["checks"]))})
    a1 = R["rule_A1"]
    P["a1_shares"] = ", ".join(f"{m} {100 * v:.1f}%" for m, v in a1["first_attempt_length_share"].items())
    P["a1_verdict"] = "switched to P2" if a1["switch_to_P2"] else "kept P1"

    L = []
    L.append("# Study 2 scrubbing pilot — report v0.1 (tuning keys only)\n")
    L.append("Spec: [`SCRUB_PILOT_SPEC_v0.1.md`](SCRUB_PILOT_SPEC_v0.1.md) (FIXED 2026-09-30, before any pilot text was "
             "paraphrased or edited). Results: [`../outputs/study2_pilot_v0.1/results.json`](../outputs/study2_pilot_v0.1/"
             "results.json); validation: [`../outputs/study2_pilot_v0.1/VALIDATION.json`](../outputs/study2_pilot_v0.1/"
             "VALIDATION.json). **This file is built by `make_report_pilot.py`; every number comes from those files.** "
             "Scope: tuning keys 9001–9004 only; nothing here is a result about the study keys.\n")
    L.append("## 1. Run and checks\n")
    L.append("- Validation: [[n_val_pass]] of [[n_val]] checks passed (inputs only). The run used commit `[[commit]]`; "
             "total step time [[hours]] h.\n")
    L.append("| check | rule | observed | verdict |\n|---|---|---|---|")
    L.append(f"| I1 contributions | r ≥ 0.99; per-token Spearman ≥ 0.8 | r = [[i1_r]] (slope [[i1_slope]]); "
             f"per-token [[i1_tok]] | {pf(chk['I1']['pass'])} |")
    L.append(f"| I2 edits act on the key | E-true more negative than E-rand (p < 0.01) | p = [[i2_p]]; median change "
             f"[[i2_true]] vs [[i2_rand]] | {pf(chk['I2']['pass'])} |")
    L.append(f"| I3 bookkeeping | exact edit counts; median drift ≤ 2% | "
             f"{', '.join(f'{a}: {v}' for a, v in chk['I3']['n_diff_exact'].items())}; drift ok: "
             f"{chk['I3']['median_drift_le_2pct']} | {pf(chk['I3']['pass'])} |")
    L.append(f"| I5 Study 2 time | ≤ [[i5_budget]] h | [[i5_total]] h | {pf(chk['I5']['pass'])} |\n")
    L.append("Validation checks: " + "; ".join(f"{k} {'pass' if c['pass'] else 'FAIL'}" for k, c in V["checks"].items())
             + ".\n")
    L.append("## 2. Adjustments (rules fixed in the spec)\n")
    L.append("- **A1, paraphrase prompt:** first attempts meeting the length floor: [[a1_shares]] → [[a1_verdict]].")
    if a1["switch_to_P2"] and "paraphrase_P2" in R:
        for m, v in R["paraphrase_P2"].items():
            L.append(f"  - {m} with P2 (ρ = 0.50, 100 texts): first attempts meeting the length floor "
                     f"{100 * v['first_attempt_length_share']:.1f}%; all conditions {v['pass_rates_pct_P2']['all']:.1f}% "
                     f"vs P1 {v['pass_rates_pct_P1_same_texts']['all']:.1f}% on the same texts.")
    red = R["rule_A2"]["median_reduction_at_10pct"]
    L.append(f"- **A2, round size:** median reduction of the attacker's objective at 10%: "
             + ", ".join(f"{100 * float(k):.0f}% rounds {v:.3f}" for k, v in red.items()) + " → chosen [[a2_choice]].\n")
    L.append("## 3. Quality bars\n")
    L.append("- Normal range (pool A's human continuations, 95th percentile): perplexity [[bar_ppl]], seq-rep-4 "
             "[[bar_rep]]; meaning baseline (same-prompt pairs, 95th percentile) [[bar_cos]]. Attacker's pool C "
             "equivalents: perplexity [[c_ppl]], meaning [[c_cos]]. Stricter readings: the model-text 95th percentile "
             "[[bar_model_ppl]] and the human median [[bar_human_med]].\n")
    L.append("## 4. Paraphrase\n")
    names = [f"P-{m}" for m in models] + [f"P-{m} (first attempt)" for m in models]
    L.append("Medians over the 4 tuning keys, in %; detection = S4 at p ≤ 0.01; success = undetected and all four "
             "quality conditions pass.\n")
    L.append(method_table(R, names, "method") + "\n")
    for m in models:
        pa = R["paraphrase"][m]
        L.append(f"- {m}: attempts used {pa['attempts_used']}; kept attempts still failing the attacker's own check: "
                 f"{pa['kept_fails_attacker_check']}; {pa['paraphrase_s_per_original']:.1f} s per original "
                 f"(all attempts, 500 texts).")
    L.append("\n## 5. Edits\n")
    enames = [f"E-{a} {b}" for a in ARMS for b in BUDGETS]
    L.append(method_table(R, enames, "arm and budget") + "\n")
    for a in ARMS:
        e = R["edits"][a]
        extra = ""
        if "median_objective" in e:
            extra = "; attacker's objective (median) " + ", ".join(
                f"{'0' if k == '0' else f'{100 * float(k):.0f}%'}: {v:+.2f}" for k, v in e["median_objective"].items())
        L.append(f"- {ARM_NAME[a]}: {e['edit_s_per_text']:.2f} s per text; stalled texts {e['stalled']}; median "
                 f"re-encoding drift " + ", ".join(f"{100 * float(k):.0f}%: {100 * v:.2f}%"
                                                   for k, v in e["median_drift"].items()) + extra + ".")
    L.append("\n### Scrub success per key (%), all methods\n")
    L.append(per_key_table(R, names[:len(models)] + enames) + "\n")
    L.append("### Stricter quality readings (scrub success, median %)\n")
    rows = ["| method | ρ | human 95th pct (primary) | model-text 95th pct | human median |", "|---|---|---|---|---|"]
    for n in names[:len(models)] + enames:
        for rho in LEVELS:
            m = R["methods"][n][rho]
            rows.append(f"| {n} | {rho} | {f1(m['success']['median'])} | "
                        f"{f1(m['success_stricter_bars']['A_model_p95'])} | {f1(m['success_stricter_bars']['A_human_median'])} |")
    L.append("\n".join(rows) + "\n")
    L.append("## 6. Calibration after paraphrase (descriptive)\n")
    rows = ["| paraphraser | texts | pooled FPR, 4 tuning keys (%) | mean per-key FPR, 1,000 fresh keys (%) | "
            "share of fresh keys > 3% | max (%) |", "|---|---|---|---|---|---|"]
    for m, d in R["calibration_after_paraphrase"].items():
        for k, v in d.items():
            rows.append(f"| {m} | {k} | {f1(v['pooled_fpr_4_tuning_keys_pct'])} | {f2(v['fresh_keys_mean_fpr_pct'])} | "
                        f"{100 * v['fresh_keys_share_above_3pct']:.1f}% | {f1(v['fresh_keys_max_fpr_pct'])} |")
    L.append("\n".join(rows) + "\n")
    L.append("With 100 texts, one key's FPR moves in steps of 1 point, so the per-key spread is coarse; Study 2's "
             "binding gates use pool A's 1,000 texts.\n")
    L.append("## 7. Projected Study 2 run time (check I5)\n")
    rows = ["| part | hours |", "|---|---|"]
    for k, v in chk["I5"]["projection"].items():
        if k.endswith("_h"):
            rows.append(f"| {k[:-2].replace('_', ' ')} | {v:.1f} |")
    L.append("\n".join(rows) + "\n")
    L.append("## 8. Samples (ρ = 0.50, the first text of keys 9001 and 9002; edits at 10%)\n")
    for smp in R["samples"]:
        L.append(f"**Key {smp['key']}, original** (p = {smp['p_original']:.3f}):\n\n> " +
                 smp["original"][:700].replace("\n", " ") + "\n")
        for k in [f"P-{m}" for m in models] + [f"E-{a} 10%" for a in ARMS]:
            L.append(f"**{k}** (p = {smp['p_' + k]:.3f}):\n\n> " + smp[k][:700].replace("\n", " ") + "\n")
    # reading (inference, written after the run; every number is a placeholder filled from results.json)
    M = R["methods"]
    lv = lambda name, key, rho: f1(M[name][rho][key]["median"])  # noqa: E731
    for mname in ("P-phi", "P-qwen", "E-true 5%", "E-est 5%", "E-rand 5%", "E-true 10%", "E-rand 10%"):
        tag = mname.replace(" ", "_").replace("%", "").replace("-", "_").lower()
        P[f"{tag}_det"] = " / ".join(lv(mname, "detected_after", r) for r in LEVELS)
        P[f"{tag}_succ"] = " / ".join(lv(mname, "success", r) for r in LEVELS)
        P[f"{tag}_hmed"] = " / ".join(f1(M[mname][r]["success_stricter_bars"]["A_human_median"]) for r in LEVELS)
    P["det_before"] = " / ".join(lv("P-phi", "detected_before", r) for r in LEVELS)
    cal = R["calibration_after_paraphrase"]
    P["cal_orig_share"] = f"{100 * cal['qwen']['original']['fresh_keys_share_above_3pct']:.1f}%"
    P["cal_q_share"] = f"{100 * cal['qwen']['paraphrased']['fresh_keys_share_above_3pct']:.1f}%"
    P["cal_p_share"] = f"{100 * cal['phi']['paraphrased']['fresh_keys_share_above_3pct']:.1f}%"
    P["cal_q_max"] = f1(cal["qwen"]["paraphrased"]["fresh_keys_max_fpr_pct"])
    P["cal_p_max"] = f1(cal["phi"]["paraphrased"]["fresh_keys_max_fpr_pct"])
    P["phi_h"] = f"{chk['I5']['projection']['paraphrase_phi_h']:.1f}"
    L.append("## 9. Reading (inference, after the run; tuning keys only)\n")
    L.append("Values are medians over the 4 tuning keys at ρ = 0.25 / 0.35 / 0.50 / 0.70, in %. Before any scrub, S4 "
             "detects [[det_before]].\n")
    L.append("- **Paraphrase removes most of the evidence at low strength.** Detected after paraphrase: Phi "
             "[[p_phi_det]], Qwen [[p_qwen_det]]. Scrub success (undetected and all quality conditions): Phi "
             "[[p_phi_succ]], Qwen [[p_qwen_succ]]. Stronger watermarks survive paraphrase more often, but their "
             "paraphrases also fail the quality conditions more often.")
    L.append("- **Knowing the key matters for edits.** At 5% of tokens, success is [[e_true_5_succ]] with the true "
             "key, [[e_est_5_succ]] with the stand-in estimate (cosine about 0.04–0.33) and [[e_rand_5_succ]] with "
             "random edits. Random 10% edits already lower detection to [[e_rand_10_det]].")
    L.append("- **The fluency bar is lenient for edits.** Under the primary bar (human 95th percentile), true-key "
             "10% edits succeed at [[e_true_10_succ]], but the sample for key 9001 is visibly degraded (broken words, "
             "wrong facts, a broken URL). Under the human median the same edits succeed at [[e_true_10_hmed]]; at 5% "
             "edits, [[e_true_5_hmed]]. Perplexity alone does not separate a 10%-edited text from fluent writing.")
    L.append("- **Paraphrase widens per-key calibration.** Over 1,000 fresh keys, the share with FPR above 3% rises "
             "from [[cal_orig_share]] (original texts) to [[cal_q_share]] (Qwen paraphrases) and [[cal_p_share]] (Phi); "
             "the worst key reaches [[cal_q_max]]% and [[cal_p_max]]% (100 texts, coarse). Study 2's per-key gate on "
             "1,000 paraphrased pool A texts matters.")
    L.append("- **Study 2 as designed does not fit the time budget:** [[i5_total]] h projected against [[i5_budget]] h, "
             "of which Phi paraphrasing is [[phi_h]] h (batches of 4; frequent retries).\n")
    L.append("**Not established:** anything about the study keys; robustness of these readings beyond 25 texts per "
             "key and level; whether a coherence judgment would agree with the perplexity bars.\n")
    text = "\n".join(L)
    for k, v in P.items():
        text = text.replace(f"[[{k}]]", v)
    left = re.findall(r"\[\[[a-z0-9_]+\]\]", text)
    if left:
        sys.exit(f"unresolved placeholders: {sorted(set(left))}")
    REPORT.write_text(text)
    print(f"wrote {REPORT.name} ({len(text)} chars)")


if __name__ == "__main__":
    main()
