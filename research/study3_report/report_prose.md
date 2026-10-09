# Study 3 — report v0.1: exact key tests for an activation-steering watermark (Qwen2.5-1.5B)

Date: 2026-09-30 (Milestone 5). Protocol: [`STUDY3_PROTOCOL_v0.1.md`](STUDY3_PROTOCOL_v0.1.md) (LOCKED 2026-09-30 14:29 UTC, before outcomes). Lock: [`outputs/study3_v0.1/PRE_RUN_LOCK.json`](outputs/study3_v0.1/PRE_RUN_LOCK.json). Run manifest: [`outputs/study3_v0.1/RUN_MANIFEST.json`](outputs/study3_v0.1/RUN_MANIFEST.json). Results: [`outputs/study3_v0.1/results.json`](outputs/study3_v0.1/results.json). **This file is built by** `study3_report/make_report_s3.py`, **which inserts the tables and every number in the text from the locked outputs; no number is typed by hand.** Figures: `outputs/study3_v0.1/report/`.

## 1. Run
- Started [[start_utc]] UTC ([[start_ct]] Central) after a Mac restart (swap 0); finished [[end_utc]] UTC ([[end_ct]] Central); [[seconds]] s ([[hours]] h) against the 3.3 h projection. Phases F and R ran in one go, with no restart or crash.
- `check_lock()` accepted the lock before the start and again after the run (protocol, code, the 562 reused Study 1 files and the human texts unchanged). The holdout was not touched (`final: false`). No deviation from the protocol.
- The report builder re-computed, with its own implementation of the S4 test, every key's false-positive rate on the model and human null texts, every key's detection rate on genuine texts at every level, and the probe's acceptance of the genuine texts, and asserted that they equal `results.json` (all equal).

## 2. Pre-registered results (protocol §7)
<<TABLE1>>

**In words (evidence):**
- **G1 passes** ([[g1]]% pooled) and **G2 passes**: all [[n_cal]] keys are calibrated (per-key false-positive rates [[g2_min]]–[[g2_max]]%).
- **P1 passes at every level**, including ρ = 0.25, where the owner's probe failed Study 1's working-watermark gate.
- **E1: the exact test is more powerful than the probe at ρ = 0.25, 0.35 and 0.50.** The median per-key differences are [[e1_25]], [[e1_35]] and [[e1_50]] points (95% intervals [[e1_ci_25]], [[e1_ci_35]], [[e1_ci_50]]). At ρ = 0.70 there is **no clear difference**: both detect [[tpr_exact_70]]% of genuine texts (median).
- **X1: fluent forgery is not practical against the exact test, for both routes, at ρ = 0.35, 0.50 and 0.70.** The median exact fluent acceptance of v0.4's forgeries is [[v04fa_min]]–[[v04fa_max]]%, against bars of [[bar_35]]–[[bar_70]]%. At ρ = 0.35 the same v0.4 Route B forgeries (n = 256) were *practical* against the probe in Study 1 (fluent acceptance [[b256_probe_fa_35]]%); under the exact test they reach [[b256_exact_fa_35]]%.
- **X3: no, at every level.** Random-key texts are attributed to the key at a median of [[rnd_exact_all]], against the probe's [[rnd_probe_25]]%, [[rnd_probe_35]]%, [[rnd_probe_50]]% and [[rnd_probe_70]]% on the same texts.
- **Narrowest margin (stated plainly):** [[x1_edge]]. The verdict is "not practical" by the rule; the interval is wide because the per-key rates are bimodal (§4).
- **Materiality:** for the median key, fluent forgeries are accepted far below 50% of the genuine fluent rate ([[oracle_fa_35]]%, [[oracle_fa_50]]% and [[oracle_fa_70]]% at the three levels). By the pre-registered standard, the exact test keeps the watermark's value as provenance evidence against these passive forgers.

## 3. Figures and tables
![Figure 1 — detection at an exact 1% FPR, exact test vs probe](outputs/study3_v0.1/report/fig1_detection.png)

![Figure 2 — Study 1's texts accepted by the probe vs the exact test](outputs/study3_v0.1/report/fig2_forgeries.png)

![Figure 3 — per-key calibration](outputs/study3_v0.1/report/fig3_calibration.png)

![Figure 4 — key leakage: exact acceptance of forgeries vs the attacker's recovered cosine](outputs/study3_v0.1/report/fig4_leakage.png)

<<TABLES>>

## 4. Secondary results (pre-registered, descriptive)
- **Human text (H1):** pooled false-positive rate [[h1_pooled]]%, highest key [[h1_max]]%, no key above 3%. The owner's probe flagged [[probe_human]]% of human continuations in Study 1.
- **Stricter level (p ≤ 0.001, 9,999 null keys):** false-positive rate [[fpr2_model]]% on model text and [[fpr2_human]]% on human text; genuine texts detected at [[tpr2_25]]%, [[tpr2_35]]%, [[tpr2_50]]% and [[tpr2_70]]% at the four strengths.
- **Genuine texts of pool E** (200 per key-level): detected at [[e_tpr_25]]%, [[e_tpr_35]]%, [[e_tpr_50]]% and [[e_tpr_70]]%.
- **Probe and exact test combined:** requiring both flags [[both_max]]% of pool A2's unwatermarked texts at every level (requiring either: [[either_min]]–[[either_max]]%). "Both" inherits the probe's weak power at low strength, and "either" inherits the probe's acceptance of forgeries (Table 3), so neither beats the exact test alone.
- **S3 (unstandardised gradient):** [[s3_ncal]] of 8 keys calibrated ([[s3_worst]]), as the pilot's per-key diagnosis predicted; the verdicts are otherwise the same (Table 5).
- **Key-leakage lens:**
  - On average, forgeries carry a weak key-specific signal: [[p10_forg_min]]–[[p10_forg_max]]% of forgeries have p ≤ 0.10 (median over keys, per forgery set and level; 10% would be expected with no signal), against [[p10_rnd_min]]–[[p10_rnd_max]]% of random-key texts.
  - The signal is concentrated in a few keys: [[leak_n50]] of [[leak_total]] key-level × forgery-set cells have exact acceptance of 50% or more. For v0.4's forgeries at n = 256: [[leak_v04_list]].
  - Exact acceptance rises with the attacker's recovered cosine (Spearman [[spear_A]] for Route A, [[spear_B]] for Route B, over all key-levels and forgery sets; Figure 4). Route A forgeries pass mainly where the attack recovered much of the key; some Route B forgeries pass at a cosine near zero.
  - Pooling 4 forged texts per test detects a median of [[pool_forg_typ]]% of batches across forgery sets; the highest is [[pool_forg_max]].

## 5. After the run (exploratory, labelled)
- **Key 1002 at ρ = 0.70:** its genuine texts are detected at [[k1002_tpr70]]%, while every other key reaches at least [[others_tpr70_min]]%. Their p-values sit just above the cut-off (median [[k1002_medp70]]), and key 1002 also has the lowest false-positive rate ([[k1002_fpr]]%), so its test is conservative in both directions. Unexplained; it changes no verdict (the level's median detection is [[tpr_exact_70]]%).
- **Why some Route B forgeries pass (inference):** Route B does not estimate the key; it copies the average footprint of watermarked text, usually at another layer. For some keys that footprint evidently reproduces enough of the key's effect on the output distribution for the gradient test to see it, even though the copied vector points elsewhere (low cosine).
- **Figure layout, fixed after viewing:** Figure 1's "1% FPR" label was moved off the markers; Figure 4's title was shortened (it was clipped) and its legend moved below the plot (it covered points).

## 6. Reading (inference, not established)
- **The weak point in Study 1 was the detector, not the watermark.** Testing the key directly, the owner detects between [[tpr_exact_35]]% and [[tpr_exact_70]]% of genuine 256-token texts (median) at an exact 1% false-positive rate at every strength, including ρ = 0.25–0.35, where Study 1's calibration found the perplexity cost within its pre-set quality limit. The calibrations' "no detectable-and-fluent strength" was a limit of the probe.
- **Against Study 1's passive forgeries, the exact test holds for the median key,** and it rejects generic steering by construction. Study 1's one practical fluent forgery (v0.4 Route B at ρ = 0.35) is blocked.
- **The protection is only as good as the key's secrecy.** Where an attack recovered much of the key (Route A for key 1004 at high strength) or reproduced its signature (Route B for keys 1003, 1004 and 1006), forgeries passed for half or more of the texts. With at most 1,024 observed texts this is uncommon, but it happens, so key recovery matters again: it is now the route to beating the exact test.
- **For a deployer:** test the key, not the steering. The exact test has more power at low strength, a 1% false-positive rate checked per key, a lower false-positive rate on human text than the probe, and no acceptance of generic steering. Keep the key secret, and consider limiting what one key reveals across many texts (Study 5's rotating or context-keyed keys).
- **Not shown:** attackers who know the exact test and adapt to it; robustness to paraphrase or scrubbing (Study 2); other models, layers or text lengths.
