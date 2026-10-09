# Source gate v0.1 — activation-level watermarks: security (C+D) and statistics (E+B)

Date: 2026-09-25. **Stage 3.**
**Status:** **C+B+D (merged): PASS** after the feasibility pilot (2026-09-25, see §6); originally CONDITIONAL. **E: FAIL as a standalone paper** (occupied); its remaining piece becomes a section. **B: PASS only as a component** of C.
Search absence is not proof of novelty.

## 0. How this gate was run
- Full text read (arXiv HTML v1/v2/v3, 2026-09-24/25): Self-Recognition (2606.06315v1), SLAM (2605.05443v2), Activation Watermarking/AWM (2603.23171v3), GaussMark (2501.13941), PASA (2605.10977v2). Read through a summarizing fetch tool, and **all quotations below come from that tool**. Re-confirm them against the PDFs before any quotation goes into the paper.
- Abstract level: Watermarks in the Sand (2311.04378), RLCracker (2509.20924), MarkSec (2609.16681), the watermark-stealing line (2402.19361, 2604.10893), OpenStamp (2608.27899), MarkTune (2512.04044), the Cai/Su/Li statistics line (2404.01245, 2510.22007, 2608.14906), the optimal-watermark theory papers (2312.17295, 2505.08878, 2604.08759).
- arXiv API searches by mechanism (steering-vector recovery; activation + watermark + spoofing; SAE + watermark; white-box attacks). Semantic Scholar citations of Self-Recognition (1 citing paper, unrelated), SLAM (1, unrelated) and GaussMark (15; none is an attack on it).
- Industry and practitioner web search: no blog or report on attacking activation watermarks was found (the CMU PhD blog "No Free Lunch in LLM Watermarking" (2026) covers token watermarks, **to read at the next gate pass**).
- Code: Self-Recognition code is public (`Thibaud-Ardoin/LLM-Self-Recognition`, **MIT**, last pushed 2026-06-16). No public SLAM code was found. (`jbeliao/SLAM` is an unrelated 2019 repository.)

## 1. Candidate C+B+D (merged): security and exact testing of activation-steering watermarks

**One-sentence question.**
*Decision:* whether a provider or verifier can treat an activation-steering watermark (a fixed secret direction added to the residual stream during generation, detected by re-encoding the text with the same open model) as evidence of provenance.
*Information set:* the attacker has the public open-weight model, which the scheme's own white-box detector also requires, plus *n* watermarked outputs, but not the key vector or layer.
*Targets:* (i) how well the key can be recovered (cosine with the true direction) as a function of *n*; (ii) **spoofing**: human or other-model text accepted as watermarked at a fixed FPR; (iii) **scrubbing** at matched quality.
*Comparators:* the schemes' own detectors (classifier and cosine), and an **exact score test** (GaussMark-style, treating steering as a bias perturbation), which also serves as the principled detector.
*Failure mechanism:* a **fixed key direction produces a consistent first-order drift** in the re-encoded activations and in the per-text score vectors, so averaging over outputs should estimate the key. None of the nearest works analyses this.

### Competitor table
| Predecessor (link, version, access) | What it already answers | Remaining difference and qualification |
|---|---|---|
| Self-Recognition, Ardoin, Schäfer, Wunder, [2606.06315v1](https://arxiv.org/abs/2606.06315), ICML 2026 (per two secondary sources; confirm at the venue); full text read; code MIT | Fixed random sparse vector (99.7% sparse, α=5) at one middle layer, the same for every token and generation; re-encode detection; F1 99.1 → 89.3 under DIPPER; 1B–8B open models. **States:** "the security of the method relies on the secrecy of the steering configuration … if an attacker can recover the secret steering vector and target layer, the watermark could be trivially reproduce[d] to spoof". Proposes a rotating or pseudo-random vector as **future work**. | **No recovery attack, no sample complexity, no spoofing or scrubbing experiment, no defence implemented, no fixed-FPR or p-value reporting.** The authors *name* the risk. Our contribution would be to *measure and explain* it, which is meaningful but must go beyond "obviously a fixed vector leaks". **Scoop risk:** the same authors listed the rotating-vector defence as future work. |
| SLAM, Harel-Canada, Sahai, [2605.05443v2](https://arxiv.org/abs/2605.05443); full text read; no code found | Per-document HMAC selection of 7 features from a **public bank** of 104 SAE-derived linguistic phenomena (Gemma Scope); Stouffer z-test at about 2.3% FPR; Gemma-2 2B/9B; no threat model; "no explicit treatment of stealing, spoofing, or forgery". | The feature bank is public and only the per-document subset is secret, so a **union-steering spoof** (steer all bank features) plausibly passes detection. Untested. A second, structurally different target for the attack (keyed per document, unlike Self-Recognition). Gemma licence terms need checking. |
| AWM, Aremu, Ognev, Poppi, Lukas, [2603.23171v3](https://arxiv.org/abs/2603.23171); full text read | Secret Gaussian key directions in hidden states for **misuse monitoring**; adaptive attackers use surrogate keys; FPR calibrated on a benign set. Key recovery "not addressed". | A different use case (monitoring, not text provenance). A close methodological neighbour; must be cited. Its surrogate-key threat model is a useful template. |
| GaussMark, Block, Sekhari, Rakhlin, [2501.13941](https://arxiv.org/abs/2501.13941); full text read | Gaussian perturbation of **one MLP weight matrix**; test statistic ⟨ξ, ∇θ log p⟩/(σ‖∇θ log p‖), **exactly N(0,1) under H0**; rank-reduced variant; no key-recovery analysis; "no discussion of bias perturbation, residual stream modifications". | **B's gap:** extend the exact test to activation steering, viewed as a bias or additive-parameter perturbation. This is a **transfer**, and would be framed that way. The attack side (gradient averaging when the base model is public) may also apply to GaussMark served through an API. Open weights change the threat model; to analyse. |
| Watermark stealing (Jovanović et al. [2402.19361](https://arxiv.org/abs/2402.19361)); adaptive stealing [2604.10893](https://arxiv.org/abs/2604.10893); MarkSec [2609.16681](https://arxiv.org/abs/2609.16681); DITTO; RLCracker; SEEK (OpenReview) | Stealing, spoofing and scrubbing of **token-level** schemes (green lists and similar) from black-box outputs; unified evaluation protocols; defences with multiple keys. | Only token or semantic schemes. The **activation family has a different key object** (a direction in activation space, recoverable with white-box re-encoding), so the estimator, the sample complexity and the defence trade-off are new. The stealing *concept* is known, so the framing is "first security analysis of activation-level watermarks", not "first stealing attack". |

**Occupied.** The general concept of watermark stealing and spoofing; the observation that recovering the vector would allow spoofing (stated by Self-Recognition); exact Gaussian tests for weight perturbations (GaussMark).

**Residual gap.** No work (search level) measures whether activation-level watermark keys can be **recovered from outputs**, how many outputs that takes, or how effective spoofing and scrubbing then are at a fixed FPR. None implements and evaluates the **rotating or keyed-direction defence** or its cost in paraphrase robustness, or gives these schemes **exact p-values**. Type: an adequacy (security) check of a published method family, plus a statistical tool, plus a defence evaluation. Not a new watermark.

**Is it meaningful?** Yes, conditionally. If keys are recoverable from a modest *n*, then activation watermarks (an ICML 2026 method, SLAM, and in part AWM) **cannot serve as provenance evidence** without a defence, and the defence costs something measurable. If they are *not* recoverable, the paper gives the first positive security evidence for the family, plus exact tests. Either outcome changes what a deployer does. **Main risk:** a reviewer calls the fixed-vector attack obvious. Mitigations: (a) sample-complexity theory and the measured constants; (b) SLAM's structurally different keyed-per-document design; (c) exact tests; (d) the stealability–robustness frontier of the defence. Together these clear the "obvious" bar only if all four are delivered well.

**Feasibility (inference, to be checked).** The schemes run at 1–3B parameters: Self-Recognition includes Llama-3.2-1B; we can use Qwen2.5-0.5B/1.5B (Apache-2.0) if the Llama or Gemma licences are a problem. Needed operations: generation with a hook, a forward pass for re-encoding, and **one backward pass per text for the score test**. On an M5 with 16 GB and MPS, this is plausible for a 1B model, but **not measured**. The predecessor stalled here. Llama 3.2 and Gemma 2 are gated on Hugging Face under their own licences; accepting them is Yichen's action. The Self-Recognition code (MIT) gives an exact reproduction baseline.

**Fit with the paper standard (10–13 pages; 4–6 figures and 4–6 tables).** Plausible material: (1) the threat model and the estimator; (2) theory, meaning sample complexity and the exact test; (3) key-recovery curves against *n* for two or three schemes; (4) spoofing and scrubbing at fixed FPR; (5) the defence's stealability–robustness frontier; (6) paraphrase and quality interplay; (7) ablations over layer, sparsity, α and text length. That is enough for 5 or more figures and tables *if the results hold*.

**Verdict: CONDITIONAL.** Single next check: **a feasibility pilot**, as follows.
1. Confirm the licence route: Qwen2.5 (Apache) or the gated Llama 3.2.
2. On the M5, measure the time per 256-token steered generation, per re-encoding pass, and per backward pass, for a model of 0.5–1.5B parameters.
3. Reproduce the Self-Recognition steering and detection on a handful of prompts, **input validation only**: check that the hook works and that detection runs. No attack is run and no key recovery is attempted before a locked protocol.

Pass if the per-text cost allows about 5,000 generations plus re-encoding within about a week of machine time.

## 2. Candidate E: statistical limits of paraphrase-robust detection

**One-sentence question.** After a meaning-preserving attack, is detectable watermark evidence bounded by the key-conditional meaning-level distortion, so that hidden-state watermarks cannot beat semantic watermarks under paraphrase?

| Predecessor | What it already answers | Remaining difference |
|---|---|---|
| PASA, Ai & He, [2605.10977v2](https://arxiv.org/abs/2605.10977); full text read | Models semantic-invariant attacks as maps that preserve a semantic cluster, and gives the **optimal miss rate** β* = Σₖ(P(cluster k) − α)₊ under FA and distortion constraints. Detection capacity falls as robustness is made coarser. | Essentially the meaning-level limit, for token-sampling schemes. Nothing about *where* in the model the watermark sits, but the result depends only on the output distribution, so it covers activation schemes automatically. |
| Watermarks in the Sand, Zhang et al., [2311.04378](https://arxiv.org/abs/2311.04378) (abstract) | Strong watermarking is impossible under quality-oracle and perturbation-oracle assumptions. | The general impossibility is occupied. |
| RLCracker, [2509.20924](https://arxiv.org/abs/2509.20924) (abstract) | The paraphrase space as a KL ball; an adaptive robustness radius. | Worst-case robustness theory is occupied. |
| The optimal-watermarking line (Huang et al. 2023; Wouters 2024; Tsur et al. 2025; He et al. 2025 DAWA; Cai, Li, Su et al.) | Detection–distortion optimality at the token level. | The "location invariance" remark (power per unit of KL is the same wherever the perturbation sits, locally) is folklore-level: score-test noncentrality equals the Fisher information. |

**Occupied.** The core limit (PASA Theorem 1, together with data processing and "Watermarks in the Sand").
**Residual gap.** A short remark applying these results to activation watermarks, explaining why the paraphrase robustness of Self-Recognition and SLAM must come from semantic or structural shifts (content distortion). That's a **section**, not a paper.
**Verdict: FAIL as a standalone paper.** Fold the remark into C's discussion.

## 3. Candidate B: exact tests for activation-steering watermarks
Covered above. **PASS as a component only.** It is a clean transfer of GaussMark's exact N(0,1) test to steering, viewed as an additive-parameter perturbation, and it fixes Self-Recognition's missing FPR control. Too thin on its own; valuable inside C (the principled detector, and the lens through which key leakage is analysed).

## 4. Recommendation (proposal)
Lock the question as **C+B+D: "Stealing activation watermarks: key recovery, spoofing, exact tests and defences for activation-steering LLM watermarks"** (working title), **conditional on the feasibility pilot**. The pilot is Stage 4 work that needs no outcome data; it measures only speed and correctness of the hooks.

## 5. What was not done
- No PDF-level check of quotations (they come from the summarizing tool); re-confirm before citing.
- The CMU "No Free Lunch" blog, the SEEK OpenReview paper and DualGuard (ACL 2026) were not read.
- No experiment run; no model downloaded; no licence accepted.

## 6. Feasibility pilot result (2026-09-25): the condition is met
Script: [`pilot/feasibility_pilot.py`](pilot/feasibility_pilot.py); output: [`pilot/outputs/feasibility_pilot_v0.1.json`](pilot/outputs/feasibility_pilot_v0.1.json); model manifest with SHA-256 hashes: [`pilot/outputs/model_manifest_qwen2.5-1.5b.json`](pilot/outputs/model_manifest_qwen2.5-1.5b.json).
- Model: Qwen2.5-1.5B (Apache-2.0, not gated), revision `8faed761`, bf16 on MPS; torch 2.14.0, transformers 5.17.0; 28 layers, d=1536; key on layer 14 with 4 nonzero coordinates (0.3%), α=5, following Self-Recognition's `generate_noise`.
- Checks: steering changes the logits ✓; removing the hook restores them ✓; the gradient w.r.t. the additive vector is finite and nonzero ✓.
- Timing: steered 256-token generation takes 1.66 s per text at batch 8 (10.6 s at batch 1); re-encoding 0.19 s per text; backward pass 0.74 s per text. **Projected: 3.6 hours for 5,000 texts** (rule: ≤ 168 hours). **PASS.**
- No detection statistic, key-recovery estimate or attack was computed.
- Also noted from the public code: the Self-Recognition repository contains a `multibit_pipeline.py`, so multi-bit (candidate G) is partly under way by those authors.
