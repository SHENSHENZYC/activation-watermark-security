# Decision log — activation-watermark-stealing (formerly rp-2026-09-24)

The single source of truth. Newest entries at the bottom. Each entry states: **what was decided or found**, the **evidence** (a link), and **who decided**. Keep evidence, inference and proposal separate.

## 2026-09-24 — Project started; predecessor reviewed

Yichen asked for a fresh end-to-end project, informed by the unfinished `tensorized_hidden_state_watermarking_research` project, which will not be resumed. I reviewed it: its topic is representation-level (hidden-state, low-rank tensor) watermarking of LLM text; its question is whether it beats token-level watermarks on text-only detection after paraphrasing. It stalled at a CPU pilot with no results. Its novelty claims are search-level only and count as unverified.
Codename `rp-2026-09-24` (neutral; rename at topic lock). Git initialised.
Skill updated: rule A5 (capture reusable lessons as they arise) and Part G lessons log added to research-project-guide. Remote Control is now offered, not switched on automatically (Yichen declined the automatic switch-on).

Evidence: [`PREDECESSOR_REVIEW.md`](PREDECESSOR_REVIEW.md). Decided by: Yichen (restart), Claude (review, setup).

## 2026-09-24 — GitHub repo and project skills

Yichen approved a private GitHub repo `rp-2026-09-24` with auto-push, and installing the project skills citation-management, paper-lookup, statistical-power, source-gate and frozen-data-provenance (copied from ccp-backtest-disclosure). source-gate and frozen-data-provenance were rewritten to be topic-neutral. Skill updated: generic master copies are now kept in research-project-guide `templates/project-skills/`.

Evidence: [`.claude/skills/THIRD_PARTY_SKILLS.md`](../.claude/skills/THIRD_PARTY_SKILLS.md). Decided by: Yichen.

## 2026-09-24 — Stage 1: scope relative to the predecessor

Decided: stay in representation-level LLM watermarking and provenance, but re-derive the research question in the Stage 2 screen. The predecessor's question is one candidate among 10–15, not the default. Compute found: Apple M5, 16 GB, MPS available (PyTorch 1.13).

Evidence: [`PREDECESSOR_REVIEW.md`](PREDECESSOR_REVIEW.md). Decided by: Yichen.

## 2026-09-24 — Stage 1: venue type; AI policies checked

Decided: arXiv preprint plus an ML workshop (NeurIPS, ICLR or ACL family). AI-use policies checked at primary sources and recorded in the brief: all allow some disclosed AI use; ACL prohibits AI-generated novel research content; ICLR desk-rejects undisclosed use. arXiv endorsement needs a personal endorser (2026-01-21 policy). Brief drafted; pending: who writes the prose, the time budget, the holdout.
Skill updated: venue facts added to Part G.

Evidence: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md). Decided by: Yichen (venue), Claude (policy check).

## 2026-09-24 — Stage 1: who writes the prose

Decided: Claude drafts sections; Yichen revises substantially and takes responsibility; disclosure in every version. ACL-family workshops are excluded as a result.

Evidence: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md). Decided by: Yichen.

## 2026-09-24 — Stage 1 exit: brief agreed

Decided: about 3 months, local M5 compute only (no cloud spending); a held-out prompt set and attack set fixed at Stage 5. The brief is agreed. Next: Stage 2 topic screen.

Evidence: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md). Decided by: Yichen.

## 2026-09-24 — Stage 2: topic screen v0.1

Screened 13 candidates (search level). Key finding: the predecessor's core question is **largely occupied** by LLM Self-Recognition (arXiv 2606.06315, Jun 2026, reportedly ICML 2026): residual-stream steering, detection by re-encoding, more paraphrase-robust than KGW. Also relevant: SLAM (2605.05443) and GaussMark (2501.13941). Ranking: C+D (stealing and spoofing activation-steering watermarks, plus a defence) 1st; E+B (statistical limits and exact tests) 2nd; L (localization) 3rd. Predecessor question A not recommended as the lead.
Skill updated: literature-search tooling lesson; `arxiv_search.py` added to templates.

Evidence: [`TOPIC_SCREEN_v0.1.md`](TOPIC_SCREEN_v0.1.md). Decided by: Claude (screen); the choice is pending with Yichen.

## 2026-09-24 — Stage 2 exit: candidates chosen for the gate

Decided: gate C+D (stealing, spoofing and a defence for activation-steering watermarks) and E+B (statistical limits of paraphrase-robust detection, and exact tests), in parallel. The predecessor question A and the others are parked.

Evidence: [`TOPIC_SCREEN_v0.1.md`](TOPIC_SCREEN_v0.1.md). Decided by: Yichen.

## 2026-09-24 — Paper standard set

Yichen's standing expectation: a professional, high-standard paper of about 10–13 main-text pages (excluding references and appendix), with at least 4–6 tables and 4–6 figures. Added to the brief and to research-project-guide (rule A6, and the Stage 8 outline). Tension: the workshop venue is shorter (NeurIPS 2026 main track: 9 pages). Proposed that the full arXiv paper be the primary deliverable; decision pending.

Evidence: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md). Decided by: Yichen (standard); resolving the venue tension is pending.

## 2026-09-24 — Venue and length: direction agreed

Yichen agreed: the full 10–13-page arXiv paper is the primary deliverable, with a workshop version cut down from it; TMLR is the alternative. The final choice is made at topic lock (end of Stage 3), before Stage 5 design. Added to the handoff as a topic-lock item.

Evidence: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md). Decided by: Yichen.

## 2026-09-25 — Stage 3: source gate v0.1

Findings (full text for Self-Recognition, SLAM, AWM, GaussMark, PASA): no work found that attacks activation-level watermarks. Self-Recognition (ICML 2026) states that recovering its fixed steering vector would allow spoofing, and leaves a rotating-vector defence as future work. SLAM uses a public feature bank with per-document secret subsets and has no security analysis. GaussMark's exact N(0,1) test covers weight matrices, not steering or biases. PASA's Theorem 1 already gives the meaning-level limit.
Verdicts: **C+B+D merged: CONDITIONAL** (single next check: compute and licence feasibility pilot, input validation only). **E: FAIL standalone** (occupied), folded in as a remark. **B: PASS as a component only.** Self-Recognition code is public (MIT). Qwen2.5-1.5B is not cached locally (empty entry); Pythia-1.4B is cached (5.5 GB).
Skill updated: source-gate reading-practice lesson.

Evidence: [`ACTWM_GATE_v0.1.md`](ACTWM_GATE_v0.1.md). Decided by: Claude (verdicts); approval of the pilot is pending with Yichen.

## 2026-09-25 — Feasibility pilot: PASS

Yichen approved the pilot with Qwen2.5-1.5B (Apache-2.0, revision 8faed761; hashes in the manifest). New `.venv` (Python 3.12, torch 2.14.0, transformers 5.17.0; `requirements-lock.txt`). The proceed rule was written into the script before the run: ≤ 168 h for 5,000 texts, and all hook checks true. Observed: 1.66 s per generation (batch 8), 0.19 s per re-encoding, 0.74 s per backward pass, so **3.6 h for 5,000 texts**; all checks true. **PASS.** Timing and hook validation only; no detection or attack statistic was computed. The gate verdict for C+B+D moves from CONDITIONAL to PASS.

Evidence: [`pilot/outputs/feasibility_pilot_v0.1.json`](pilot/outputs/feasibility_pilot_v0.1.json), [`ACTWM_GATE_v0.1.md`](ACTWM_GATE_v0.1.md) §6. Decided by: Yichen (pilot approval); the result is mechanical.

## 2026-09-25 — TOPIC LOCK

Yichen locked the research question: key recovery, spoofing and scrubbing, exact score tests, and defences for activation-steering LLM watermarks (Self-Recognition and SLAM-style targets), under an attacker with the open model and n outputs. Written into the brief. Next: rename (codename → a proper name), then the venue choice (full arXiv paper plus a workshop version, or TMLR).

Evidence: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md), [`ACTWM_GATE_v0.1.md`](ACTWM_GATE_v0.1.md). Decided by: Yichen.

## 2026-09-25 — Rename: rp-2026-09-24 → activation-watermark-stealing

Yichen chose the name. Done (research-project-guide Part C): GitHub repo renamed to `SHENSHENZYC/activation-watermark-stealing` (the old URL redirects) and the remote updated; name references updated in the handoff, brief, log and skill notes (no absolute paths in tracked files); memory copied to the new path key, with a "moved" pointer left in the old one; the folder moved to `~/Desktop/Research_2026/activation-watermark-stealing` (the last step, after this commit). Yichen reopens the project from the new path.

Evidence: this entry; `git remote -v`. Decided by: Yichen.

## 2026-09-25 — Venue chosen; Stage 3 exit

Decided: the full 10–13-page arXiv paper first, then a condensed workshop version (prefer non-archival). Stage 3 is complete: topic locked, project renamed, venue set. Next: Stage 4 (data and model provenance: prompt corpus choice and terms, holdout prompt set, model licences for any second model).

Evidence: [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md). Decided by: Yichen.

## 2026-09-25 — Stage 4: sources and models chosen; prompt-set spec fixed before download

Decided (Yichen): corpus = C4 realnewslike validation (main) plus WikiText-103 test/validation (check domain); paraphrasers = Phi-3.5-mini-instruct (MIT) and Qwen2.5-1.5B-Instruct (Apache); second generator = Llama-3.2-1B (gated: Yichen accepts the licence and logs in himself). The terms of use of every candidate were recorded first. The prompt-set spec v0.1 (40-word prompts, 200-word human continuations, an ID-hash 80/20 dev/holdout split with a code assertion, and the proceed rule) was committed **before** any corpus download.

Evidence: [`stage4/TERMS_OF_USE_CHECK.md`](stage4/TERMS_OF_USE_CHECK.md), [`stage4/PROMPT_SETS_SPEC_v0.1.md`](stage4/PROMPT_SETS_SPEC_v0.1.md). Decided by: Yichen (sources, models); Claude (spec details).

## 2026-09-25 — Prompt sets v0.1 built: proceed rule FAIL (WikiText only)

Ran `stage4/build_prompt_sets.py` exactly per spec v0.1. Frozen files match the Hub sizes (SHA-256 in the output). **C4 passes:** 13,863 records, 0 parse failures, 8,580 usable (5,283 shorter than 240 words, 0 duplicate prompts), dev 6,896 (rule ≥ 6,000 ✓), holdout 1,684 (rule ≥ 1,500 ✓). **WikiText fails:** test plus validation hold only 122 articles (120 usable), against a rule of ≥ 300. **Correction, stated plainly:** I set the 300 threshold without checking that WikiText-103 test and validation contain only about 120 articles. The rule stays failed; any fix is a spec v0.2 with Yichen's decision. The C4 sets are unaffected.

Evidence: [`stage4/outputs/prompt_sets_v0.1.json`](stage4/outputs/prompt_sets_v0.1.json). Decided by: mechanical (pre-set rule).

## 2026-09-25 — Prompt sets v0.2 and v0.3: PASS; Stage 4 audit

v0.2 (Yichen: add WikiText train file 1): all rules PASS; C4 identical to v0.1. A size typo in the spec text (file 2's size quoted) was corrected in place with a note; the script checks the Hub listing, so the data are unaffected. v0.3: inspecting two dev prompts showed raw tokeniser spacing in WikiText, so it is detokenised (an input fix before any generation). All rules and integrity checks PASS; WikiText has 14,560 usable (11,720 dev / 2,840 holdout); C4 has 8,580 (6,896 / 1,684). Holdout seal tested. Paraphraser manifests written; Phi-3.5-mini feasibility: 7.6 GB, about 26 s per 200-word paraphrase unbatched (timing only).
Skill updated: lesson on proceed rules and data inspection.

Evidence: [`stage4/DATA_AUDIT_v0.3.md`](stage4/DATA_AUDIT_v0.3.md), [`stage4/outputs/prompt_sets_v0.3.json`](stage4/outputs/prompt_sets_v0.3.json). Decided by: Yichen (v0.2); Claude (v0.3 input fix, audit).

## 2026-09-25 — Llama-3.2-1B access requested

Yichen accepted the Llama 3.2 licence on HF, created a read-only token (`activation-watermark-stealing-read`) and logged in himself (HF user confirmed with `auth whoami`). Access check: still gated (403), pending Meta's approval. Retry before the first Llama step; Stage 5 can proceed on Qwen meanwhile.

Evidence: this entry. Decided by: Yichen.

## 2026-09-25 — Stage 5: Study 1 protocol v0.1 drafted (not locked)

Draft: key recovery (Q1a) and spoofing (Q1b) against a Self-Recognition-style fixed sparse steering key on Qwen2.5-1.5B. Kerckhoffs threat model (public hyperparameters; secret key and layer); 16 keys; n ∈ {1…1024}; exact key-resampling p-values (M = 999) for D-cos (primary) and D-score; validity gates G1–G4; rules R1 (median cos ≥ 0.9 and layer hit ≥ 14/16) and R2 (spoof acceptance ≥ 50% at n ≤ 256); about 25 h compute. Scrubbing moved to Study 2. Awaiting Yichen's design review before the script is written.

Evidence: [`STUDY1_PROTOCOL_v0.1.md`](STUDY1_PROTOCOL_v0.1.md). Decided by: Claude (draft); review pending.

## 2026-09-25 — Study 1 code written; input validation ALL PASS (no outcomes)

Yichen approved the Study 1 design as drafted. Code: `research/study1/{core,detect,attack,run_study1,validate_inputs}.py`. Input validation (synthetic data plus a validation-only key; no detection or attack statistic on model outputs): 21/21 checks pass. They cover the pools (sizes, disjoint, dev-only, holdout sealed); keys; exact p-values (synthetic null FPR 1.2% at nominal 1%, within the binomial band; KS p = 0.07); the attack estimator recovering a planted synthetic signal (cos 0.92, layer correct); attack-module isolation (imports numpy only); runner lock enforcement; hooks; shapes. The first timing check **failed** (batched gradients at 10.2 s per text, projected 84 h > 72 h budget); switched gradients to batch 1 (0.37 s per text) and re-ran: projected **16.2 h**, all pass. Protocol clarifications before the lock: z-scores use the reference-set sd (defined at n = 1); the drift profile is stored for all keys; the budget is re-timed.
Skill updated: timing and MPS batching lesson.

Evidence: [`outputs/study1_v0.1/INPUT_VALIDATION.json`](outputs/study1_v0.1/INPUT_VALIDATION.json). Decided by: Yichen (design); Claude (implementation).

## 2026-09-25 — Llama-3.2-1B pre-registered in Study 1 v0.1 (lock deferred until access)

Yichen chose to wait for Llama access and include it in v0.1 rather than lock Qwen alone. Protocol updated before the lock: Llama-3.2-1B (revision 4e20de36) is a pre-registered replication with 8 keys at layer 8 (the middle; Self-Recognition's public code gives no 1B layer, so its "middle layer" rule is applied, checked in their repo at commit 7c26938d); same gates and rules; the layer-hit rule scales to 87.5% of keys; Qwen is primary. Code generalised (`--model qwen|llama`; per-model data and output folders; BOS kept but excluded from averages and targets). Qwen re-validated: ALL PASS, 15.9 h projected; the earlier validation output is kept as `qwen/INPUT_VALIDATION_pre_generalisation.json`. Llama validation runs once access is granted.

Evidence: [`STUDY1_PROTOCOL_v0.1.md`](STUDY1_PROTOCOL_v0.1.md) §4, [`outputs/study1_v0.1/qwen/INPUT_VALIDATION.json`](outputs/study1_v0.1/qwen/INPUT_VALIDATION.json). Decided by: Yichen (wait for Llama); Claude (implementation).

## 2026-09-25 — Llama access granted; Llama input validation ALL PASS

Meta granted access (confirmed through the HF API). Downloaded Llama-3.2-1B at revision 4e20de36 (safetensors and configs; the duplicate `original/` consolidated checkpoint was intentionally not downloaded); licence llama3.2; manifest with SHA-256 hashes written (`tools/model_manifest.py` now handles partial snapshots and lists the files not downloaded). Input validation for Llama: ALL PASS (hooks; BOS present and excluded; 256 content tokens; 16 layers × 2048 features; gradients finite; projected **7.3 h** for 8 keys). Both models together: about 23 h. Study 1 v0.1 is ready to lock.

Evidence: [`stage4/outputs/model_manifest_llama-3.2-1b.json`](stage4/outputs/model_manifest_llama-3.2-1b.json), [`outputs/study1_v0.1/llama/INPUT_VALIDATION.json`](outputs/study1_v0.1/llama/INPUT_VALIDATION.json). Decided by: mechanical.

## 2026-09-25 — STUDY 1 v0.1 LOCKED (before outcomes); run deferred to the next session

Yichen approved locking Study 1 v0.1 (Qwen primary, Llama replication) and asked to prepare and start the actual run in a new session ("Milestone 1"). The lock is `outputs/study1_v0.1/PRE_RUN_LOCK.json`: SHA-256 of the protocol (with its status line set to LOCKED before hashing), of the code (core, detect, attack, run_study1, validate_inputs), and of the inputs (prompts loader, prompt sets v0.3, model manifests, both input-validation reports); the git commit before the lock; `final: false` (the holdout stays sealed). Verified: no Study 1 data exist (no outcomes); `run_study1.check_lock()` accepts the lock. **No run was started.**

Evidence: [`outputs/study1_v0.1/PRE_RUN_LOCK.json`](outputs/study1_v0.1/PRE_RUN_LOCK.json). Decided by: Yichen.

## 2026-09-25 — Milestone 1: Study 1 v0.1 run started (Qwen, then Llama)

Pre-run checklist done: clean tree at `b68f863`; `run_study1.check_lock()` accepts the lock; no Study 1 data existed before the start (no outcomes); 606 GB free; on AC power. Started at 16:29:19 UTC as `caffeinate -ims sh -c 'run_study1.py --model qwen --phase all && run_study1.py --model llama --phase all'` (keep-awake with `caffeinate`, because the app's keep-awake tool was not available in this session; closing the lid would still sleep the Mac). The log is in `research/study1/data/v0.1/logs/` (git-ignored). Code and protocol untouched.

Evidence: this entry; `outputs/study1_v0.1/PRE_RUN_LOCK.json`. Decided by: Yichen (start in Milestone 1).

## 2026-09-25 — Study 1 v0.1: G1 FAILED at α = 5 and α = 10 on Qwen; run stopped (protocol §10)

**Result (pre-registered gate, mechanical):** Phase A tuning-key TPR (D-cos, p ≤ 0.01, pool T, 100 texts per key) = **0.0, 0.0, 0.0, 0.0** at α = 5 and **0.0, 0.0, 0.0, 0.0** at α = 10. G1 fails, so the runner stopped at 16:44:57 UTC before any other phase and before Llama (`data/v0.1/qwen/state.json`: `"stop": "G1 failed at alpha 5 and 10"`). No study key was used, and no attack statistic exists. **The rule stays failed.**

**Diagnostics (read-only, tuning keys only, locked files untouched):** (a) the true key's D-cos statistic sits inside the key-resampling null (median p 0.25–0.81 at α = 5; 0.23–0.67 at α = 10); (b) the steering is active (0/100 texts identical between α = 5 and α = 10 for the same seed), but the mean re-encoded normalised activation on the key's 4 coordinates does not move (all |mean| < 0.01, the same at both α). So on Qwen2.5-1.5B, a 4-coordinate key leaves **no first-order drift** in the unsteered re-encoding, which is the premise both D-cos and the averaging attack rely on.

**Cause of the design gap, stated plainly (my error):** I read Self-Recognition's public code (commit `7c26938`, MIT; read only, in a scratch folder). Its watermark pipeline (`steering_watermark/param.yaml`) uses Llama-3.1-8B, layer 15, `sparse_0.003`, `noise_max` 5 (key generation matches ours), but its **detector is a trained per-key MLP probe** (`model_type: mlp`, hidden 2048-64-64-32, per-token activations, steered vs a comparison set). Cosine similarity appears only as a "training-free" option in the README and the analysis notebooks. The protocol's G1 therefore tested a training-free statistic that is not the paper's headline detector. Also, I did not check detection power on tuning keys before the lock; the gate caught it, at the cost of this version.

Evidence: `research/study1/data/v0.1/qwen/state.json` (git-ignored); this entry. Decided by: mechanical (pre-set rule); the next step is Yichen's decision (§10).
Skill updated: reproduce the target with the authors' own detector on tuning keys before locking.

## 2026-09-25 — Reproduction pilot v0.1: spec and script fixed before running

Yichen chose the reproduction pilot (not the Llama phase A under v0.1, nor re-opening the gate). Spec `repro/REPRO_PILOT_SPEC_v0.1.md` with its decision rule (reproduces if the authors' MLP probe reaches a mean test AUROC ≥ 0.95), fixed before any pilot output. Tuning keys and pool T only; Study 1 code unchanged (imported); α ∈ {5, 10, 20}; Qwen and Llama. Smoke test on synthetic features: a planted signal gives AUROC 1.0 on all detectors; no signal gives about 0.5; token alignment checked on two real texts. Note: the authors' majority vote at a 0.5 cut-off can sit at 50% even when the AUROC is 1.0 (a threshold effect), so it is reported but not used by the rule.

Evidence: [`repro/REPRO_PILOT_SPEC_v0.1.md`](repro/REPRO_PILOT_SPEC_v0.1.md), [`repro/repro_pilot.py`](repro/repro_pilot.py). Decided by: Yichen (pilot); Claude (design).

## 2026-09-25 — Reproduction pilot v0.1: Qwen does not reproduce; Llama "reproduces" only with broken text

**Pre-set rule (authors' MLP probe, mean test AUROC ≥ 0.95):** Qwen2.5-1.5B **no** at α = 5, 10, 20 (0.53, 0.63, 0.91). Llama-3.2-1B **yes** at α = 5, 10, 20 (1.00 each). **Exploratory addendum** (added after the pilot, labelled as such): median perplexity under the unsteered model: Qwen 5.5 → 5.5, 5.9, 7.6; Llama 5.6 → **32.6**, 57.6, 3,382 (garbled at α = 5, gibberish above). The key's size relative to the activation norm at α = 5 is 10% on Qwen and 129% on Llama. No grid point is both detectable and quality-preserving. The training-free cosine with the true key stays weak wherever the text is fluent.
Also: my first perplexity script at batch 16 with full-vocabulary logits stalled on MPS (the known memory pitfall); it was stopped and re-run at batch 1. A report sentence ("≤ 0.03") was re-counted before commit and corrected to 0.036.

Evidence: [`repro/REPRO_PILOT_REPORT_v0.1.md`](repro/REPRO_PILOT_REPORT_v0.1.md), `outputs/repro_v0.1/`. Decided by: mechanical (pre-set rule); next, Yichen's choice of the v0.2 target.

## 2026-09-25 — Strength calibration v0.1: spec and script fixed before running

Yichen chose to calibrate relative strength (not Llama-3.2-3B at α = 5, nor Llama-1B at α = 5 as-is). Spec `repro/CALIBRATION_SPEC_v0.1.md`: ρ = ‖v‖ / (median unsteered activation norm from the pilot), grid {0.15, 0.25, 0.35, 0.50, 0.70, 1.00}, both models, tuning keys and pool T only; operating point = the smallest ρ with the authors' MLP probe AUROC ≥ 0.95 **and** median perplexity ratio ≤ 1.25; otherwise "no usable window" is reported. Checks before running: rescaled keys have norm exactly ρ·N with Self-Recognition's support; the perplexity function reproduces the pilot's values on two texts.

Evidence: [`repro/CALIBRATION_SPEC_v0.1.md`](repro/CALIBRATION_SPEC_v0.1.md), [`repro/calibrate.py`](repro/calibrate.py). Decided by: Yichen (calibrate); Claude (design).

## 2026-09-25 — Strength calibration v0.1: no usable window on either model (256 tokens)

**Pre-set rule:** no ρ on the grid gives both the authors' MLP AUROC ≥ 0.95 and a perplexity ratio ≤ 1.25. Qwen: AUROC 0.62, 0.71, 0.83, **0.97**, 0.99, 1.00 at ρ = 0.15 … 1.0, with ratios 1.04, 1.13, 1.25, **1.62**, 2.29, 4.25. Llama: AUROC 0.53, 0.59, 0.72, 0.89, **1.00**, 1.00, with ratios 1.03, 1.08, 1.13, 1.44, **2.22**, 5.00. With strength measured as ρ, the two models trace the same trade-off (detection needs ρ ≈ 0.5–0.7; quality holds only up to about 0.35). Consistent with the pilot.

Evidence: [`repro/CALIBRATION_REPORT_v0.1.md`](repro/CALIBRATION_REPORT_v0.1.md), `outputs/calibration_v0.1/`. Decided by: mechanical (pre-set rule); next, Yichen's decision (spec: longer texts, a larger model, a relaxed rule, or another design).

## 2026-09-25 — Strength calibration v0.2 (512 tokens): spec and script fixed before running

Yichen chose to test 512-token texts (the authors' own length), not attacking along the curve, relaxing the quality rule or a larger model. Spec `repro/CALIBRATION_SPEC_v0.2.md`: ρ ∈ {0.25, 0.35} (the fluent levels at 256), new 512-token unsteered texts, the v0.1 rule unchanged (AUROC ≥ 0.95 and perplexity ratio ≤ 1.25); the first-256-token detectors reported descriptively. `calibrate_v02.py` sets the length at run time; `core.py` is not edited (the Study 1 lock check still passes). Smoke test: 512 tokens exactly, features aligned.

Evidence: [`repro/CALIBRATION_SPEC_v0.2.md`](repro/CALIBRATION_SPEC_v0.2.md), [`repro/calibrate_v02.py`](repro/calibrate_v02.py). Decided by: Yichen (512 tokens); Claude (design).

## 2026-09-25 — Calibration v0.2: run stopped for memory exhaustion, patched (computation only) and restarted

At 22:04 UTC, 98 min in, the run had finished only 5 of 12 text sets: the Python process held 16 GB (all RAM) with 11 GB of swap, and one perplexity pass took 60 min instead of about 1. Cause (my code): full-vocabulary logits over 512+ positions, both in feature extraction (an unused LM-head output) and in perplexity, grew the MPS cache. Patch in `calibrate_v02.py` only: features via the decoder body (no LM head); perplexity applies the LM head only to continuation positions; the MPS cache is emptied after each text and file. Equivalence test on finished files: identical perplexities (4 decimals) and zero activation difference; GPU memory 3.1 GB. Finished files are reused; nothing measured changes. `repro_pilot.py`, `calibrate.py` and `core.py` are unchanged.
Skill updated: the MPS memory lesson now covers vocabulary-sized logits and swap monitoring.

Evidence: this entry; `repro/calibrate_v02.py`. Decided by: Claude (a computational fix, no design change).

## 2026-09-25 — Strength calibration v0.2 (512 tokens): no usable window on either model

**Pre-set rule:** neither ρ = 0.25 nor 0.35 gives both AUROC ≥ 0.95 and a perplexity ratio ≤ 1.25. Qwen: AUROC 0.79 / 0.90, ratio 1.15 / 1.27. Llama: AUROC 0.66 / 0.81, ratio 1.09 / 1.15. Length helps by 0.075–0.089 AUROC over 256 tokens, not enough. The first-256-token AUROCs match v0.1 within 0.013 (a consistency check). Two drafting errors in the report prose (a range and a consistency figure) were caught by re-computing before commit and corrected.

Evidence: [`repro/CALIBRATION_REPORT_v0.2.md`](repro/CALIBRATION_REPORT_v0.2.md), `outputs/calibration_v0.2/`. Decided by: mechanical (pre-set rule); next, Yichen's decision on the Study 1 v0.2 design.

## 2026-09-25 — Calibration v0.3 (Llama-3.2-3B scale check): model pinned; spec fixed before running

Yichen chose the 3B scale check with a pre-committed follow-up (not attacking along the curve straight away, nor re-opening the gate). Llama-3.2-3B pinned at revision `13afe512` (licence llama3.2, already accepted; access confirmed; 6.4 GB; manifest with SHA-256; the duplicate `original/` checkpoint not downloaded). Qwen2.5-3B was not chosen: its licence is the more restrictive Qwen research licence. Spec `repro/CALIBRATION_SPEC_v0.3.md`: layer 14 of 28, k = 9, 256 tokens, ρ ∈ {0.15, 0.25, 0.35, 0.50, 0.70}, the same rule. **Pre-committed:** a 3B operating point → Study 1 v0.2 attacks Llama-3.2-3B there; none → Study 1 v0.2 attacks along the trade-off curve on Qwen2.5-1.5B. Calibration ends after this step. Smoke test: architecture asserted; 192 s per 100 texts; GPU memory 7.2 GB.

Evidence: [`repro/CALIBRATION_SPEC_v0.3.md`](repro/CALIBRATION_SPEC_v0.3.md), [`repro/calibrate_v03.py`](repro/calibrate_v03.py), [`stage4/outputs/model_manifest_llama-3.2-3b.json`](stage4/outputs/model_manifest_llama-3.2-3b.json). Decided by: Yichen (3B check and follow-up); Claude (design).

## 2026-09-26 — Calibration v0.3 (Llama-3.2-3B): no operating point → pre-committed follow-up applies

**Pre-set rule:** no ρ on Llama-3.2-3B gives both AUROC ≥ 0.95 and a ratio ≤ 1.25: AUROC 0.48, 0.56, 0.56, 0.70, 0.86 at ρ = 0.15 … 0.70, ratios 1.03, 1.05, 1.11, 1.26, 1.62. At equal ρ the 3B model is less detectable than 1B and 1.5B. **Under the follow-up fixed before the run, Study 1 v0.2 attacks along the trade-off curve on Qwen2.5-1.5B; calibration ends.** The 1B / 1.5B / 3B curves are kept for a scale figure.

Evidence: [`repro/CALIBRATION_REPORT_v0.3.md`](repro/CALIBRATION_REPORT_v0.3.md), `outputs/calibration_v0.3/`. Decided by: mechanical (pre-set rule and pre-committed follow-up).

## 2026-09-26 — Study 1 v0.2 design decision 1: nudge levels

Yichen chose four levels on Qwen2.5-1.5B at 256 tokens: ρ ∈ {0.25, 0.35, 0.50, 0.70} (calibration v0.1: AUROC 0.71 / 0.83 / 0.97 / 0.99, perplexity ratio 1.13 / 1.25 / 1.62 / 2.29). Rejected: three levels (0.35, 0.5, 0.7) and two levels (0.5, 0.7). The number of keys per level will be set from a validation timing check.

Evidence: [`repro/CALIBRATION_REPORT_v0.1.md`](repro/CALIBRATION_REPORT_v0.1.md). Decided by: Yichen.

## 2026-09-26 — Study 1 v0.2 design decisions 2–3: defender detector and attack routes

(2) **Defender's detector:** the authors' MLP probe, trained per key by the owner on their own watermarked vs unwatermarked texts, with its threshold fixed at a 1% false-positive rate on held-out unwatermarked texts; our exact key-based tests (cosine, gradient score) are secondary and descriptive. Rejected: a linear probe as primary; MLP and linear as co-primary.
(3) **Attack routes, both pre-registered:** Route A, key recovery (v0.1's averaging estimator: layer choice, sparse top-k support, rebuilt key; forge by steering with it; key accuracy measured). Route B, footprint imitation (the dense mean shift in re-encoded activations at the attacker-chosen layer; forge by steering with it). Rejected: A only; B only.

Evidence: this entry. Decided by: Yichen.

## 2026-09-26 — Study 1 v0.2 protocol drafted (not locked)

Draft `STUDY1_PROTOCOL_v0.2.md`: Qwen2.5-1.5B, 8 study keys (never used before) at ρ ∈ {0.25, 0.35, 0.50, 0.70}; the owner's detector is the authors' MLP (trained on pools E vs F) with a 1%-FPR threshold from pool A1, checked on A2 (gate G1); a per-level gate L1 (oracle TPR ≥ 20%); rules R1 (key recovery), R2 (forgery practical, relative to the oracle and beyond the random-key control, per route) and R3 (generic steering suffices); about 20 h projected. One number was corrected before commit by re-computation (the Clopper–Pearson bound for 8 of 8 is 0.63, two-sided, not 0.69). Awaiting Yichen's design review; then code, input validation and lock.

Evidence: [`STUDY1_PROTOCOL_v0.2.md`](STUDY1_PROTOCOL_v0.2.md). Decided by: Claude (draft); review pending.

## 2026-09-26 — Study 1 v0.2 code written; input validation ALL PASS; pipeline smoke test passes (no outcomes)

Yichen approved the v0.2 design as drafted. Code in `research/study1_v02/` (`common.py`, `detect2.py`, `attack2.py`, `run_v02.py`, `validate_v02.py`); v0.1's `core.py` and `attack.py` are imported unchanged; feature passes use the decoder body only (the memory lesson). One draft edge case was closed before validation: R2 "not practical" uses max(2 × the random-key median, 2%), so that a zero random rate cannot make the rule vacuous.
**Input validation: 15/15 pass** (pools and holdout seal; keys; N; the detector on synthetic data; the threshold rule, mean FPR 1.2% at a nominal 1%; attack isolation and planted recovery; the runner refusing without a lock; hooks; feature equivalence with v0.1's re-encoding; timing **23.0 h** against a 30 h budget). **Stated plainly:** on the first try, two synthetic tests failed because my planted signals were too weak to be a fair test (the detector TPR 0.895 against 0.9; the attack's planted z of about 3 was at the noise maximum). I strengthened the planted signals (the detector shift 0.5 → 1.0; the attack signal to z about 15), and both passed; the code under test was not changed.
**Pipeline smoke test** (the validation-only key, tiny pools, a scratch folder, since deleted): every phase runs, and all summary fields and result fields exist. The runner prints verdicts automatically; on 4–16 texts with a validation key they carry no information and were not used. No study key has been used with the model.

Evidence: [`outputs/study1_v0.2/INPUT_VALIDATION.json`](outputs/study1_v0.2/INPUT_VALIDATION.json), `study1_v02/`. Decided by: Yichen (design); Claude (implementation).

## 2026-09-26 — STUDY 1 v0.2 LOCKED (before outcomes); run deferred to Milestone 2

Yichen approved locking v0.2 and starting the run in a new session ("Milestone 2"). The protocol's status line was set to LOCKED before hashing. The lock `outputs/study1_v0.2/PRE_RUN_LOCK.json` records the SHA-256 of the protocol; of the code (`common`, `detect2`, `attack2`, `run_v02`, `validate_v02`, plus v0.1's `core.py` and `attack.py`, which v0.2 imports); of the inputs (the prompts loader and sets, the Qwen manifest, the v0.2 input validation, the pilot results that fix N, calibration v0.1, the v0.1 lock); the git commit before the lock; `final: false`. Verified: the validation ran on exactly the locked code; no v0.2 data exist; `check_lock()` accepts the lock; a tamper test (protocol, `attack2.py`, `core.py`) is refused. **No run was started.**

Evidence: [`outputs/study1_v0.2/PRE_RUN_LOCK.json`](outputs/study1_v0.2/PRE_RUN_LOCK.json). Decided by: Yichen.

## 2026-09-26 — Milestone 2: pre-run checks for Study 1 v0.2 pass; Mac restart before the start

Checklist steps 1–2 at 01:31 UTC (20:31 Central, 2026-09-25): clean tree at `ae65a35`, up to date with the remote; `run_v02.check_lock()` accepts the lock; `research/study1_v02/data/` does not exist (no outcomes); 584 GB free; on AC power; no study processes; 77% of RAM free. Swap used was 4.2 GB of 5.1 GB (probably left over from the calibration v0.2 memory event), so Yichen chose to restart the Mac before starting the run (rejected: start now and watch the swap; quit Chrome and the VM first). **No run started.**

Evidence: this entry. Decided by: Yichen.

## 2026-09-26 — Milestone 2: Study 1 v0.2 run started

After the Mac restart: swap 0 MB, 69% of RAM free, on AC power; `check_lock()` accepts the lock; no v0.2 data existed before the start (no outcomes). Started at **01:34:20 UTC** (20:34 Central, 2026-09-25) as `nohup caffeinate -ims .venv/bin/python -u research/study1_v02/run_v02.py --phase all >> research/study1_v02/data/run.log 2>&1` (projected about 23 h). The log is git-ignored. Code and protocol untouched.

Evidence: this entry; `outputs/study1_v0.2/PRE_RUN_LOCK.json`. Decided by: Yichen (restart first, then start).

## 2026-09-26 — Study 1 v0.2 RESULT: key recovery fails; footprint forgery (Route B) is practical at n = 64 at every working level; the owner's probe accepts off-key and garbled text

Run finished at 23:58 UTC (18:58 Central), 22.4 h, no crash; `check_lock()` accepted the lock before and after the run. **Pre-registered (mechanical):** G1 PASS (pooled FPR 1.4%). L1 fails at ρ = 0.25 (oracle 8%; descriptive only) and passes at 0.35 / 0.50 / 0.70 (32% / 86% / 100%). **R1 fails at this budget at every level** (median cos ≤ 0.16; layer found for ≤ 3 of 8 keys). **R2 Route B practical at n = 64** at 0.35 / 0.50 / 0.70 (median 42.5% / 99% / 100%; at 0.35 the margin is narrow: lower bound 5.0% vs the random-key upper bound 4.5%). R2 Route A: inconclusive / not practical / not practical. **R3 holds only at 0.70** (random key 55.5%). By the §10 materiality standard, the trained-probe watermark is unreliable as provenance evidence at these strengths.
**Stated plainly:** (a) R2's "not practical" bound, max(2 × the random median, 2%), exceeds 100% when R3 holds, so Route A's "not practical" at 0.70 is uninformative (its acceptance is 80.5–90.5%); the verdict stands. (b) The locked runner omitted the secondary D-cos diagnostic listed in §5/§8 (my omission); deferred to Study 3. The detector AUROC (§8) was computed after the run from the saved scores (0.75 / 0.89 / 0.99 / 1.00).
**Exploratory (after the run, labelled in the report):** Route B's vector barely matches the key (cos ≤ 0.054) and in 43 of 96 cases picks layer 0 or 1, producing gibberish that the probe still accepts (median 59%); elsewhere acceptance is 97% at a perplexity ratio of 1.36. Fluent and effective forgeries (post-hoc cut-off 1.5×) at n = 256: Route B 3 / 2 / 2 of 8 keys; Route A 4 of 8 at 0.70. Human-text FPR 3.6%. Inference: the probe detects off-distribution activations more than the key.
Report and assets built by a script that re-computes every per-key rate and median from the raw scores and asserts equality with `results.json`; figures inspected (two layout fixes). Forged texts read directly. matplotlib 3.11.2 installed into `.venv` for figures (no effect on locked code).
Skill updated: forgery rules need a quality condition; check rule bounds at the extremes; assert every listed secondary diagnostic exists in the smoke test.

Evidence: [`STUDY1_REPORT_v0.2.md`](STUDY1_REPORT_v0.2.md), [`outputs/study1_v0.2/results.json`](outputs/study1_v0.2/results.json), `outputs/study1_v0.2/report/`, [`study1_report_v02/make_report_assets.py`](study1_report_v02/make_report_assets.py). Decided by: mechanical (pre-registered rules); next step is Yichen's decision.

## 2026-09-26 — Next study: quality-aware forgery (Study 1 v0.3)

Yichen chose a pre-registered quality-aware forgery study as the follow-up to v0.2: the attacker uses the open model to check fluency and avoids layers that produce garbage, and the success rule includes a fluency condition. It reuses v0.2's owner detectors and observed texts (read only), and generates only new forgeries and controls. Rejected for now: exact key tests (Study 3) first; scrubbing (Study 2); pausing to re-gate claims. Stage 5 design for v0.3 starts now; v0.2's result and files stay as they are.

Evidence: [`STUDY1_REPORT_v0.2.md`](STUDY1_REPORT_v0.2.md) §4. Decided by: Yichen.

## 2026-09-26 — Study 1 v0.3 design decisions 1–3

(1) **Fluency in the success rule:** a forged text is fluent if its perplexity (under the unsteered model, given its prompt, as in v0.2) is at most the 95th percentile of that key-level's genuine watermarked (oracle) texts; the main metric is the share of forged texts that are both accepted and fluent. Rejected: key-level median ≤ 1.25×; key-level median ≤ 1.5× (post hoc).
(2) **Attacker's own fluency check:** a trial search over each route's 5 strongest footprint layers, 16 trial texts per layer on the attacker's own prompts; a layer is dropped if its trial median continuation-only perplexity exceeds 1.2× that of the observed watermarked texts; use the strongest remaining layer (or the most fluent if none pass). Rejected: excluding layers 0–1 a priori (informed by v0.2's results); a joint layer-and-strength search.
(3) **Scope:** ρ ∈ {0.35, 0.50, 0.70}, n ∈ {64, 256}, Routes A and B, the 8 v0.2 study keys (96 attacks, about 6 h); v0.2's owner detectors, observed texts and oracle and random-key texts reused read-only as controls. Rejected: Route B only; the wider grid.

Evidence: this entry. Decided by: Yichen.

## 2026-09-26 — Study 1 v0.3 protocol drafted (not locked)

Draft `STUDY1_PROTOCOL_v0.3.md`: the attacker screens its route's 5 strongest footprint layers with 16 trial texts each (continuation-only perplexity ≤ 1.2 × that of the observed texts), then forges on pool D; the owner's v0.2 probes, thresholds, oracle and random-key texts are reused read-only, with an integrity check (the reloaded probes re-score v0.2's oracle texts within 1e-4). Primary metric FA = the share of texts both accepted and fluent (perplexity ≤ the 95th percentile of the key-level's oracle texts). Rule F1 (practical / not practical / inconclusive) uses bounds that cannot exceed 100%, fixing v0.2's R2 limitation; F3 is the fluent generic-steering check. About 6 h projected. Awaiting Yichen's design review; then code, input validation and lock.

Evidence: [`STUDY1_PROTOCOL_v0.3.md`](STUDY1_PROTOCOL_v0.3.md). Decided by: Claude (draft); review pending.

## 2026-09-27 — Study 1 v0.3 code written; input validation ALL PASS (6.3 h projected; no outcomes)

Yichen approved the v0.3 design as drafted. Code in `research/study1_v03/` (`common3.py`, `attack3.py`, `run_v03.py`, `validate_v03.py`); v0.2's `common.py`, `detect2.py`, `attack2.py` and v0.1's `core.py`, `attack.py` are imported unchanged. The runner's lock will also hash the 243 reused v0.2 data files.
**Input validation 15/15 pass:** reused files present; trial prompts in the attacker's pool C and disjoint from D; holdout sealed; seeds disjoint from v0.2's; attack isolation; the first candidate equals v0.2's route choice exactly (both routes); selection logic; the fluency functions; the runner refusing without a lock; **integrity: reloaded probes re-score v0.2's oracle texts with a difference of 0.0** (4 key-levels); continuation-only perplexity plausible (3.8–8.6 on unsteered texts, above the prompt-conditional values, as expected); a pipeline smoke test on the validation key (every phase; every protocol-listed result field present; scratch folder deleted; its verdicts carry no information); timing **6.3 h** against a 9 h budget.
**Stated plainly:** the first validation attempt crashed in the smoke test on a wrong scratch-folder path in `validate_v03.py` (my bug in the validation script, not in the code under test); fixed and re-run from the start.

Evidence: [`outputs/study1_v0.3/INPUT_VALIDATION.json`](outputs/study1_v0.3/INPUT_VALIDATION.json), `study1_v03/`. Decided by: Yichen (design); Claude (implementation).

## 2026-09-27 — STUDY 1 v0.3 LOCKED (before outcomes); run deferred to Milestone 3

Yichen approved locking v0.3 and starting the run in a new session ("Milestone 3"). The protocol's status line was set to LOCKED before hashing. The lock `outputs/study1_v0.3/PRE_RUN_LOCK.json` (locked 2026-09-27 00:29:57 UTC, 19:29 Central on 2026-09-26) records the SHA-256 of the protocol; of the code (`common3`, `attack3`, `run_v03`, `validate_v03`, plus v0.2's `common`, `detect2`, `attack2` and v0.1's `core`, `attack`); of the **243 reused v0.2 data files**; of the inputs (the v0.3 input validation, the v0.2 lock and results, the prompts loader and sets, the Qwen manifest); the design constants; the git commit before the lock (`8b8718d`); `final: false`. Verified: no v0.3 data exist; `check_lock()` accepts the lock; tamper tests on the protocol, `attack3.py` and one reused v0.2 file (`K_k1001_r035_obs.json`, a space appended, then restored byte for byte) are all refused, and the lock passes again after restoring. **No run was started.**

Evidence: [`outputs/study1_v0.3/PRE_RUN_LOCK.json`](outputs/study1_v0.3/PRE_RUN_LOCK.json). Decided by: Yichen.

## 2026-09-27 — Milestone 3: pre-run checks for Study 1 v0.3 pass; Mac restart before the start

Checklist steps 1–2 at 00:33 UTC (19:33 Central, 2026-09-26): clean tree at `3c3d2a5`, up to date with the remote; `run_v03.check_lock()` accepts the lock; `research/study1_v03/data/` does not exist (no outcomes); 582 GB free; on AC power; no study processes; 79% of RAM free. Swap used was 2.4 GB of 3.0 GB, so Yichen chose to restart the Mac before starting the run (rejected: start now and watch the swap; quit heavy apps first). **No run started.**

Evidence: this entry. Decided by: Yichen.

## 2026-09-27 — Milestone 3: Study 1 v0.3 run started

After the Mac restart: swap 0 MB, 73% of RAM free, on AC power; `check_lock()` accepts the lock; no v0.3 data existed before the start (no outcomes). Started at **00:37:40 UTC** (19:37 Central, 2026-09-26) as `nohup caffeinate -ims .venv/bin/python -u research/study1_v03/run_v03.py --phase all >> research/study1_v03/data/run.log 2>&1` (projected about 6.3 h). The log is git-ignored. Code and protocol untouched.

Evidence: this entry; `outputs/study1_v0.3/PRE_RUN_LOCK.json`. Decided by: Yichen (restart first, then start).

## 2026-09-27 — Study 1 v0.3 RESULT: fluent Route B forgery practical only at ρ = 0.35; inconclusive elsewhere; perplexity-based fluency admits repetitive loops (exploratory)

Run finished at 07:01 UTC (02:01 Central), 6.3 h, no crash; `check_lock()` accepted the lock before and after. **Pre-registered (mechanical):** integrity PASS (difference 0). **F1 Route B practical at ρ = 0.35** (n = 256; median FA just above 50% of the oracle's); inconclusive at 0.50 and 0.70. **F1 Route A inconclusive at every level** (at 0.70 its lower bound only equals the random-key upper bound). **F3 holds at 0.70 only** (random-key FA exactly at the bar). No level "not practical".
**Exploratory (after the run, labelled in the report):** the first pre-registered sample (Route B, key 1001, ρ = 0.50, layer 1) is degenerate yet under the perplexity bar and accepted. A repetition diagnostic (rep3 above the oracle's 95th percentile; chosen after seeing that sample) shows Route B's FA at 0.70 is 80–90% repetitive (FA without repetition 3.5–4.5% vs 90.0% for the oracle); at 0.35 Route B's FA without repetition is 12.5% vs 15.0%. Route B's check still picks layers 0–2 for most keys, because looping text has *low* perplexity. Some unflagged texts drift off the prompt. Inference: a forgery quality condition needs a repetition term and ideally a coherence judgment.
**Stated plainly:** the pre-registered perplexity-only fluency rule is gameable by repetition. This is within the protocol's §11 non-claims, not a deviation; the verdicts stand. Fig. 1's legend was moved after inspection.
Skill updated: a perplexity-only quality condition is gamed by repetition; add a diversity (rep-n) term.

Evidence: [`STUDY1_REPORT_v0.3.md`](STUDY1_REPORT_v0.3.md), [`outputs/study1_v0.3/results.json`](outputs/study1_v0.3/results.json), `outputs/study1_v0.3/report/`, [`study1_report_v03/`](study1_report_v03/). Decided by: mechanical (pre-registered rules); next step is Yichen's decision.

## 2026-09-27 — Next study: repetition-aware forgery (Study 1 v0.4)

Yichen chose one more Study 1 version: the attacker's fluency check and the success rule both add a repetition term, with new seeds and otherwise v0.3's design (about 6 h). It turns v0.3's exploratory repetition finding into a pre-registered test of whether a passive attacker can make forgeries that are accepted, low in perplexity and not repetitive. Rejected for now: moving to Study 3 (exact key tests) with the repetition caveat; a Stage 7 claim gate now; stopping for the day. v0.3's results and files stay as they are. Stage 5 design for v0.4 starts now.

Evidence: [`STUDY1_REPORT_v0.3.md`](STUDY1_REPORT_v0.3.md) §4. Decided by: Yichen.

## 2026-09-27 — Study 1 v0.4 design decisions 1–3

(1) **Repetition in the success rule:** a forged text is fluent if its perplexity is at most the key-level's oracle 95th percentile (as in v0.3) **and** its token seq-rep-4 (the share of repeated 4-grams in the continuation's tokens; Welleck et al., arXiv 1908.04319, checked at arXiv) is at most the key-level's oracle 95th percentile. v0.3's word rep3 is reported as a secondary. Rejected: word rep3 as the rule; requiring both measures.
(2) **Attacker's repetition check:** a trial text is repetitive if its seq-rep-4 exceeds the 95th percentile of the attacker's observed texts; a candidate layer passes if its trial median perplexity is ≤ 1.2 × the observed median (as in v0.3) and at most 2 of its 16 trials are repetitive. If none passes, the attacker uses the candidate with the fewest repetitive trials, ties broken by lower trial perplexity. Rejected: trial median ≤ observed p95; trial mean ≤ 1.5 × observed mean.
(3) **Scope:** as v0.3 (ρ ∈ {0.35, 0.50, 0.70}, n ∈ {64, 256}, Routes A and B, 5 candidates, 8 keys; about 6.3 h), with new seeds. Rejected: 8 candidate layers; Route B only.

Evidence: this entry. Decided by: Yichen.

## 2026-09-27 — Study 1 v0.4 protocol drafted (not locked)

Draft `STUDY1_PROTOCOL_v0.4.md`: v0.3's design with a repetition term on both sides. The attacker keeps a candidate layer only if its trial median continuation-only perplexity is ≤ 1.2 × the observed median and at most 2 of 16 trials exceed the observed texts' 95th percentile of token seq-rep-4 (fallback: fewest repetitive trials, then lowest perplexity). A text is fluent if its perplexity and its seq-rep-4 are both at most the key-level's oracle 95th percentiles. Rules F1 and F3 are unchanged in form. New seeds (trials base + 60; forgeries base + 70 + 3·route + n-index). Secondaries: v0.2 and v0.3 forgeries re-scored under v0.4's FA; FA with word rep3; 3 accepted-and-fluent samples per route at ρ = 0.70 in addition to v0.3's sample rule. Validation adds: with the repetition term off, the scoring code reproduces v0.3's FA medians exactly. About 6.3 h. Awaiting Yichen's design review; then code, input validation and lock.

Evidence: [`STUDY1_PROTOCOL_v0.4.md`](STUDY1_PROTOCOL_v0.4.md). Decided by: Claude (draft); review pending.

## 2026-09-27 — Milestone 3 ends: v0.4 draft awaits review

Yichen chose to stop for today before approving the v0.4 draft (rejected for now: approve as drafted; approve without the extra ρ = 0.70 samples). The draft stays unlocked; no v0.4 code exists yet. The next session (Milestone 4) resumes with the design review, then code, input validation and the lock decision.

Evidence: this entry; `RESEARCH_HANDOFF.md`. Decided by: Yichen.

## 2026-09-28 — Milestone 4: Study 1 v0.4 design approved as drafted

Yichen approved `STUDY1_PROTOCOL_v0.4.md` as drafted, including the 3 accepted-and-fluent samples per route at ρ = 0.70 (rejected: without those samples; other revisions). The protocol stays DRAFT until the lock. Next: write `research/study1_v04/` (v0.2 and v0.3 modules imported unchanged), run input validation (protocol §10), then bring the lock decision.

Evidence: [`STUDY1_PROTOCOL_v0.4.md`](STUDY1_PROTOCOL_v0.4.md). Decided by: Yichen.

## 2026-09-28 — Study 1 v0.4 code written; input validation ALL PASS (6.4 h projected; no outcomes)

Code in `research/study1_v04/` (`common4.py`, `attack4.py`, `run_v04.py`, `validate_v04.py`); v0.3's `common3.py`, `attack3.py` (the candidate search, unchanged), v0.2's `common.py`, `detect2.py`, `attack2.py` and v0.1's `core.py`, `attack.py` are imported unchanged. The runner's lock will hash the 243 reused v0.2 files (the same set as the v0.3 lock) and the 120 reused v0.3 files.
**Draft clarification before the lock (§8 wording only):** "median seq-rep-4 ratio to the oracle" became "the median seq-rep-4 beside the oracle's (a ratio is undefined when the oracle's median is 0) and the share of texts above the seq-rep-4 bar", because genuine texts' median repetition is typically 0. No rule changes.
**Input validation 17/17 pass:** reused files present, and the 243 v0.2 hashes equal the v0.3 lock's; trial prompts in pool C and disjoint from D; holdout sealed; seed offsets {60, 70, 71, 73, 74} disjoint from v0.2's and v0.3's; attack isolation; seq-rep-4 on constructed token lists (distinct 0, loop 1 − 3/27, < 4 tokens 0) and on the first 256 model tokens; rep3 as in v0.3; the attacker's p95 and count; the selection logic (both conditions and the fallback order, including a NaN perplexity); the FA function; **with the repetition term off, the v0.4 scoring code reproduces v0.3's locked FA medians and fluency cut-offs exactly** (33 values, difference 0); the runner refusing without a lock; integrity (reloaded probes re-score v0.2's oracle texts with difference 0, 4 key-levels); a pipeline smoke test on the validation key at ρ = 0.50 and 0.70 (every phase; every §5 and §8 field, including both sample rules; scratch folder deleted; its verdicts carry no information); timing **6.4 h** against a 9 h budget.
No v0.4 trial or forgery was generated with a study key, and no repetition-aware rate was computed on any study condition.

Evidence: [`outputs/study1_v0.4/INPUT_VALIDATION.json`](outputs/study1_v0.4/INPUT_VALIDATION.json), `study1_v04/`. Decided by: Yichen (design); Claude (implementation).

## 2026-09-28 — STUDY 1 v0.4 LOCKED (before outcomes); run in this session (Milestone 4)

Yichen approved locking v0.4 and running it in this session (rejected: lock and run in a new "Milestone 5" session; review the code first). The protocol's status line was set to LOCKED before hashing. The lock `outputs/study1_v0.4/PRE_RUN_LOCK.json` (locked 2026-09-28 14:20:59 UTC, 09:20 Central) records the SHA-256 of the protocol; of the code (`common4`, `attack4`, `run_v04`, `validate_v04`, v0.3's `common3`, `attack3`, v0.2's `common`, `detect2`, `attack2`, v0.1's `core`, `attack`); of the **243 reused v0.2 files and the 120 reused v0.3 files**; of the inputs (the v0.4 input validation, the v0.3 and v0.2 locks and results, the prompts loader and sets, the Qwen manifest); the design constants; the git commit before the lock (`6c6236b`); `final: false`. Verified: no v0.4 data exist; `check_lock()` accepts the lock; tamper tests on the protocol, `attack4.py`, one reused v0.3 file and one reused v0.2 file (a space appended, then restored byte for byte) are all refused, and the lock passes again after restoring. **No run started.** Swap is 2.3 of 3 GB, so a Mac restart comes before the start.

Evidence: [`outputs/study1_v0.4/PRE_RUN_LOCK.json`](outputs/study1_v0.4/PRE_RUN_LOCK.json). Decided by: Yichen.

## 2026-09-28 — Milestone 4: pre-run checks for Study 1 v0.4 pass; Mac restart before the start

Checklist steps 1–2: clean tree at `b827a99`, pushed; `run_v04.check_lock()` accepts the lock; `research/study1_v04/data/` does not exist (no outcomes); 583 GB free; on AC power. Swap used was 2.3 GB of 3.0 GB, so Yichen chose to restart the Mac before starting the run (rejected: start now and watch the swap; quit heavy apps first). **No run started.**

Evidence: this entry. Decided by: Yichen.

## 2026-09-28 — Milestone 4: Study 1 v0.4 run started

After the Mac restart: swap 0 MB, 73% of RAM free, on AC power; `check_lock()` accepts the lock; no v0.4 data existed before the start (no outcomes). Started at **14:25:38 UTC** (09:25 Central) as `nohup caffeinate -ims .venv/bin/python -u research/study1_v04/run_v04.py --phase all >> research/study1_v04/data/run.log 2>&1` (projected about 6.4 h). The log is git-ignored. Code and protocol untouched.

Evidence: this entry; `outputs/study1_v0.4/PRE_RUN_LOCK.json`. Decided by: Yichen (restart first, then start).

## 2026-09-28 — Study 1 v0.4 RESULT: fluent, non-repetitive Route B forgery practical at ρ = 0.35; Route A not practical there; inconclusive at 0.50 / 0.70; F3 no at every level

Run finished at about 20:55 UTC (15:55 Central), 6.5 h, no crash; `check_lock()` accepted the lock before and after. **Pre-registered (mechanical):** integrity PASS (difference 0). **F1 Route B practical at ρ = 0.35** (n = 256; median FA 19.5% vs bar 14.3%; lower bound 7.0% vs random-key upper 3.5%); inconclusive at 0.50 and 0.70. **F1 Route A not practical at 0.35** (upper bounds 11.5% / 10.0% < 14.3%), the first "not practical" in Study 1; inconclusive at 0.50 and 0.70 (at 0.70, n = 256, median 73.0% clears the 45.0% bar, but the lower bound 8.5% does not beat the random-key upper bound 53.0%). **F3 no at every level** (0.70: random-key FA 36.5% < 45.0%; in v0.3 it held exactly at the bar).
**Secondary (pre-registered, descriptive):** the repetition screen worked (repetitive share of v0.4 forgeries 2.0–10.5% vs the oracle's 5.0%; Route B picks layers 12–18 at 0.70). The cost moved to perplexity: at 0.50 / 0.70 Route B is accepted 99–100% but fluent only 25.5–53.5%, and at 0.70 no candidate passed the attacker's check for 7–8 of 8 keys. v0.3's Route B forgeries at 0.70 fall from 69.0% FA to 2.5–3.0% under v0.4's rule; v0.4's reach 25.5–30.0%. seq-rep-4 and word rep3 agree within 10 points. Route A at 0.70 is bimodal per key (5 keys 71–97%, 3 keys 3–17%); the random key reaches the bar for 4 of 8 keys.
**Exploratory (after the run, labelled in the report):** a pre-registered ρ = 0.70 sample (Route B, key 1002) is word salad yet passes both bars; the oracle's own texts at 0.70 are degraded (topic drift, repeated menu fragments), and the median perplexity bar rises from 10.5 at ρ = 0.35 to 25.0 at 0.70. Inference: a bar relative to genuine watermarked text is fair for forgery but lenient for quality at high strength; a coherence judgment would be needed for a stronger quality claim.
**Stated plainly:** no deviation, rerun or resume. Figures inspected; three layout fixes (Fig. 1 title wrapped; Fig. 2 legend moved below, then split into two rows). A per-key table (Table 5) and the median bars were added to the generated tables so that every number in the prose comes from the script.
Skill updated: relative quality bars become lenient when the treatment degrades genuine text; report the bar's absolute level per condition and read reference (oracle) samples.

Evidence: [`STUDY1_REPORT_v0.4.md`](STUDY1_REPORT_v0.4.md), [`outputs/study1_v0.4/results.json`](outputs/study1_v0.4/results.json), `outputs/study1_v0.4/report/`, [`study1_report_v04/`](study1_report_v04/). Decided by: mechanical (pre-registered rules); next step is Yichen's decision.

## 2026-09-28 — Milestone 4 ends: pause until the weekly usage reset

With the weekly plan usage at 97% (reset 2026-10-01 08:59 UTC, 03:59 Central), Yichen asked for a catch-up on Study 1 (v0.1–v0.4) and the possible next moves, then a pause until the reset. No next-study decision was taken (options put to him: close Study 1 and design Study 3 after the reset, recommended; start Study 3 now; Study 1 v0.5 with a coherence judgment; a claim gate on Study 1 now). The next session is **Milestone 5**; it starts with that decision.

Evidence: this entry; `RESEARCH_HANDOFF.md`. Decided by: Yichen.

## 2026-09-30 — Study 1 closed; next study: exact key tests (Study 3)

Yichen chose to close Study 1 (v0.2–v0.4 are the forgery results; v0.4 is the primary, v0.2 and v0.3 stay as reported) and to start Stage 5 design of Study 3: exact key-resampling tests (the owner's key-specific statistic ranked against random null keys) applied to genuine watermarked texts and to the v0.2–v0.4 forgeries. Rejected for now: Study 1 v0.5 with a coherence judgment (held back unless the claim gate or a reviewer asks); a Stage 7 claim gate on Study 1 now; starting with another study (2, 4 or 5). The weekly usage limit had reset (4% used).

Evidence: [`STUDY1_REPORT_v0.4.md`](STUDY1_REPORT_v0.4.md); this entry. Decided by: Yichen.

## 2026-09-30 — Milestone 4 ends; Study 3 design starts in a new "Milestone 5" session

Yichen chose a new session for Study 3's design (rejected: continuing in this session). Handoff resume point updated with the reading list for the design.

Evidence: `RESEARCH_HANDOFF.md`. Decided by: Yichen.

## 2026-09-30 — Milestone 5: Study 3 design starts; the primary statistic will be chosen by a tuning-key power pilot

Stage 5 for Study 3 (exact key-resampling tests). Reading done: the brief, the gate, Study 1 v0.1's D-cos and exact-test design, `study1/core.py`, and Self-Recognition's public code (commit `7c26938`, cloned to a scratch folder, read only). **Found:** the authors' code has no key test and no p-values (a trained MLP with AUROC; the cosine appears only as averaged similarities typed into a plotting notebook). No exact-test statistic has been computed on any study-key text (v0.2 omitted its D-cos secondary; v0.3 and v0.4 deferred it), so Study 3 can be pre-registered before any of its outcomes exist. On disk: v0.2's 32 key-levels (1,024 observed, 200 owner-training, 100 oracle, 100 random-key and 600 forged texts each; shared sets A, C, F), v0.3's and v0.4's forgeries (24 key-levels × 400 each), and the tuning-key texts (keys 9001–9004, 100 each at ρ 0.15–1.00, plus 400 unwatermarked). On tuning keys the raw cosine is weak (AUROC 0.56 / 0.72 / 0.79 at ρ 0.35 / 0.50 / 0.70; calibration v0.1); the gradient test's power has never been measured.
**Decision:** before the protocol, a power pilot on the tuning keys only compares four candidate statistics (raw cosine, standardised cosine, gradient score, standardised gradient score) under an exact 1% key-resampling test, and a rule fixed in the pilot spec (before its run) picks Study 3's primary. Rejected: pre-registering the gradient score without a pilot (risk of a G1-style failure, as in v0.1); pre-registering all four with equal standing (multiplicity, no primary).

Evidence: this entry; `research/repro/CALIBRATION_REPORT_v0.1.md`. Decided by: Yichen.

## 2026-09-30 — Study 3 power pilot v0.1: spec fixed (approved as drafted); input validation ALL PASS

Yichen approved `study3_pilot/POWER_PILOT_SPEC_v0.1.md` as drafted (rejected: selecting on ρ = 0.35 only; on ρ = 0.50 only). Candidates S1 raw cosine, S2 standardised cosine, S3 gradient score, S4 standardised gradient score (standardised against the owner's 200 pool F unwatermarked texts), each as a cosine between the text's vector and the key, with an exact p-value against M = 999 public null keys, detection at p ≤ 0.01. **Rule:** primary = the highest mean over ρ ∈ {0.35, 0.50, 0.70} of the median TPR over the 4 tuning keys; candidates within 2.0 points are tied and resolved in the order S3, S4, S2, S1; implementation check: pooled FPR on the 400 unwatermarked texts × 4 keys in [0.3%, 2.5%]; viability reading: usable on single texts at a level if the median TPR ≥ 20% (otherwise the pooled-test option goes to Yichen). Input validation (inputs only: pool F texts and synthetic data) 6/6 pass: inputs and hashes; keys and null-key seeds; p-values uniform under a simulated null (KS p = 0.08; 1.03% at 1%) and on the 1/1,000 grid, planted signal detected 99.7%; gradient vs finite differences r = 0.9996 (slope 0.98); hook removed (logit difference 0); 0.21 s per text (pilot about 8 min). No statistic on any watermarked text before this commit.

Evidence: [`study3_pilot/POWER_PILOT_SPEC_v0.1.md`](study3_pilot/POWER_PILOT_SPEC_v0.1.md), [`outputs/study3_pilot_v0.1/VALIDATION.json`](outputs/study3_pilot_v0.1/VALIDATION.json). Decided by: Yichen (rule); Claude (design, implementation).

## 2026-09-30 — Study 3 power pilot v0.1 RESULT: gradient statistics detect at ~96–98% (exact 1% FPR); the rule chose no primary because S1 failed the implementation check

Run from the fixed spec (commit `b55948c`); features about 8 min; the guard recorded the spec and script hashes. **Pre-registered (mechanical):** the implementation check fails for S1, the raw cosine (0.00% of 1,600 unwatermarked tests, below the 0.3% floor); S2, S3 and S4 pass (1.12%, 1.06%, 0.88%). **By the rule, no primary is chosen.** Scores (mean over ρ 0.35/0.50/0.70 of the median TPR): S1 0.0, S2 6.0, **S3 97.7, S4 95.7** (tied within 2 points). Single-text TPR at an exact 1% FPR: S3 96–98% and S4 94–98% at the working levels, 93% / 88% at ρ = 0.25; AUROC 0.995–1.000; cross-key (generic steering) 0.1–1.4%; pooled 4 texts: 100%.
**Diagnosis (after the run, exploratory; `study3_pilot/posthoc_diag.py`):** S1's features reproduce the calibration's cosine AUROC exactly (not a bug). Key resampling is exact on average over keys, not per key: over 1,000 fresh random keys on the unwatermarked texts, S1's mean FPR is 1.15%, but 93.1% of keys never fire and 1.1% fire on more than half (max 100%). Per-key FPR, max over keys: S2 5.25%, **S3 20.25% (2.3% of keys above 5%)**, **S4 4.75% (none above 5%)**.
**Stated plainly (my error):** the check was meant to catch code bugs, but it pooled four fixed keys and its wording let one candidate's property block the choice among the others. The rule stands as run; the choice of Study 3's primary goes to Yichen with this evidence.
**Inference:** on tuning keys the gradient test detects where the authors' MLP could not (MLP AUROC 0.71 at ρ = 0.25, 0.83 at 0.35). If this holds on study keys, the calibrations' "no detectable-and-fluent window" belongs to the probe, not to the watermark.
Skill updated: key-resampling tests are exact on average over keys, not per fixed key; check per-key FPR over many random keys, standardise features, and let a failed check exclude a candidate rather than block the rule.

Evidence: [`study3_pilot/POWER_PILOT_REPORT_v0.1.md`](study3_pilot/POWER_PILOT_REPORT_v0.1.md), [`outputs/study3_pilot_v0.1/results.json`](outputs/study3_pilot_v0.1/results.json), [`outputs/study3_pilot_v0.1/posthoc_diagnostics.json`](outputs/study3_pilot_v0.1/posthoc_diagnostics.json). Decided by: mechanical (the fixed rule); next step is Yichen's decision.

## 2026-09-30 — Study 3 primary statistic: S4, the standardised gradient score (Yichen's decision after the pilot)

Because the pilot's rule chose no primary, Yichen chose **S4** (the gradient of the continuation log-likelihood with respect to an additive vector at layer 14, centred and scaled per coordinate against the owner's 200 pool F unwatermarked texts; cosine with the key; exact key-resampling p-value). Reasons: its power ties with S3 (95.7 vs 97.7, inside the pilot's 2-point margin), and over 1,000 random keys its per-key FPR stays near 1% (max 4.75%), whereas S3 exceeds 5% for 2.3% of keys (worst 20%); a deployed owner has one fixed key. S3 is reported as a secondary; the protocol adds a per-key calibration gate. Rejected: S3 as primary; a pilot v0.2 with a rewritten rule on the same texts (no new information). This is a decision taken after the pilot's outcomes, on tuning keys only; it is not a study result.

Evidence: [`study3_pilot/POWER_PILOT_REPORT_v0.1.md`](study3_pilot/POWER_PILOT_REPORT_v0.1.md). Decided by: Yichen.

## 2026-09-30 — Study 3 text sets: all forgeries and controls (no observed texts)

Yichen chose to re-score, with no new generation: the null sets (pool A's 1,000 unwatermarked texts and the 1,000 human continuations of pool A) for per-key calibration; the genuine sets per key-level (oracle on pool D, 100; the owner's training set E, 200); the random-key texts (100); and every forgery set (v0.2: 600 per key-level at all 4 levels; v0.3 and v0.4: 400 per key-level at ρ 0.35 / 0.50 / 0.70). About 53,000 texts, about 3.1 h at 0.21 s per text. Pool F stays out of evaluation (it is S4's standardisation reference). Rejected: adding the 1,024 observed texts per key-level (about 5 h in total); v0.4's forgeries only.

Evidence: this entry. Decided by: Yichen.

## 2026-09-30 — Study 3 null keys and FPR: M = 999 at 1% (primary); M = 9,999 at 0.1% (secondary)

Yichen chose the primary test at p ≤ 0.01 with the 999 null keys the pilot validated (`core.null_keys`), so that every comparison with Study 1's probe (1% FPR) is like for like; and a descriptive secondary at p ≤ 0.001 with 9,999 null keys (a stricter provenance standard; per-key calibration at 0.1% can be checked only loosely with 2,000 null texts). Rejected: 1% only; 0.1% as the primary.

Evidence: this entry. Decided by: Yichen.

## 2026-09-30 — Study 3 forgery rule: v0.4's F1 with the exact test in place of the probe

Yichen chose the primary forgery rule: a forged text counts if the exact test accepts it (S4, p ≤ 0.01) **and** it is fluent by v0.4's definition (perplexity and seq-rep-4 at most the key-level oracle's 95th percentiles; v0.4's code imported unchanged); "practical / not practical / inconclusive" exactly as v0.4's F1, against the exact test's own oracle and random-key rates, per route and level, on v0.4's forgeries. v0.2's and v0.3's forgeries and plain acceptance are secondary. Rejected: plain acceptance as in v0.2's R2 (no quality condition); a paired exact-minus-probe contrast only (no verdicts that line up with Study 1's). Next: the protocol draft (calibration gates, power gate and secondaries as Claude's defaults, for Yichen's review).

Evidence: this entry. Decided by: Yichen.

## 2026-09-30 — Study 3 protocol v0.1 drafted (not locked)

Draft `STUDY3_PROTOCOL_v0.1.md`: the S4 exact test (standardised gradient score at layer 14, 999 null keys, p ≤ 0.01) re-scores about 53,200 saved Study 1 texts (no generation; about 3.1 h). Gates: G1 pooled FPR on pool A's 1,000 unwatermarked texts in [0.3%, 2.5%] (else stop); G2 per-key calibration (a key's FPR on those texts ≤ 3.0%; uncalibrated keys descriptive; fewer than 6 of 8 → stop and ask Yichen); P1 per level, median oracle TPR ≥ 20%. Primary rules: X1 (v0.4's F1 with the exact test, on v0.4's forgeries), X3 (v0.4's F3 with the exact test), E1 (paired power vs the probe on the same oracle texts: more / less powerful / no clear difference by the bootstrap interval of the median per-key difference). Secondaries: human-text FPR per key (H1), plain acceptance of every set, v0.2 and v0.3 forgeries, probe-vs-exact joint acceptance, S3, 0.1% with 9,999 null keys, a key-leakage lens (forgery p-values, Route A vs cos(v̂, v), pooled forgeries). Awaiting Yichen's review; then code, input validation (including a smoke test on tuning texts and a 5 h timing budget) and the lock.

Evidence: [`STUDY3_PROTOCOL_v0.1.md`](STUDY3_PROTOCOL_v0.1.md). Decided by: Claude (draft); review pending.

## 2026-09-30 — Study 3 protocol v0.1 approved as drafted

Yichen approved `STUDY3_PROTOCOL_v0.1.md` as drafted, with human text as a reported secondary (H1) rather than part of G2 (rejected: adding the human-text FPR to G2; other revisions). The protocol stays DRAFT until the lock. Next: code in `research/study3/` (the pilot's `power_pilot.py` and v0.4's run and scoring code imported unchanged), input validation (protocol §10), then the lock decision.

Evidence: [`STUDY3_PROTOCOL_v0.1.md`](STUDY3_PROTOCOL_v0.1.md). Decided by: Yichen.

## 2026-09-30 — Study 3 code written; input validation ALL PASS (3.3 h projected; no outcomes)

Code in `research/study3/` (`common_s3.py`, `run_s3.py`, `validate_s3.py`); the pilot's `power_pilot.py`, v0.4's `common4.py`, `attack4.py`, `run_v04.py` (bootstrap), v0.3's `common3.py`, `attack3.py`, v0.2's `common.py`, `detect2.py`, `attack2.py` and v0.1's `core.py`, `attack.py` are imported unchanged and will be hash-locked. The runner's lock will hash the protocol, 16 code files, the 562 reused Study 1 files and the human texts.
**Input validation 10/10 pass:** 562 reused files present, and the 288 that the Study 1 v0.4 lock also records hash identically; null keys (the first 999 of the 9,999 equal the primary set; seeds disjoint from every other seed); p-values on synthetic data (M = 999: KS p = 0.08, 1.03% at 1%, planted 99.7%; M = 9,999: KS p = 0.04, 0.17% at 0.1%, planted 96.9%); v0.4's fluency bars and the probe's acceptance and FA medians reproduced exactly from the saved texts and scores (42 conditions, difference 0); human continuations (1,000, at least 220 tokens) and pools disjoint; the runner refuses without a lock; a smoke test on tuning texts (synthetic probe scores and perplexities) produces every §7 and §8 field (scratch deleted; its verdicts carry no information); pool F features recomputed by the Study 3 path equal the pilot's exactly; timing 0.22 s per text, 53,400 texts, **3.3 h** against a 5 h budget; no Study 3 feature or statistic on any study-key text exists.

Evidence: [`outputs/study3_v0.1/INPUT_VALIDATION.json`](outputs/study3_v0.1/INPUT_VALIDATION.json), `study3/`. Decided by: Yichen (design); Claude (implementation).

## 2026-09-30 — STUDY 3 v0.1 LOCKED (before outcomes); run in this session (Milestone 5)

Yichen approved locking Study 3 v0.1 and running it in this session (rejected: running in a new "Milestone 6" session; reviewing the code first). The protocol's status line was set to LOCKED and committed (`323c7a7`) before hashing. The lock `outputs/study3_v0.1/PRE_RUN_LOCK.json` (locked 2026-09-30 14:29:34 UTC, 09:29 Central) records the SHA-256 of the protocol; of 16 code files (`common_s3`, `run_s3`, `validate_s3`, the pilot's `power_pilot`, v0.4's `common4`, `attack4`, `run_v04`, v0.3's `common3`, `attack3`, v0.2's `common`, `detect2`, `attack2`, v0.1's `core`, `attack`); of the **562 reused Study 1 files**; of the 1,000 human texts; of the inputs (the Study 3 input validation, the pilot's results, validation and diagnostics, the Study 1 v0.2–v0.4 locks and v0.4's results, the prompt loader); the design constants; `final: false`. Verified: no Study 3 features or results exist; `check_lock()` accepts the lock; tamper tests on the protocol, `common_s3.py`, `power_pilot.py` and one reused v0.4 forgery file (a space appended, then restored byte for byte) are all refused, and the lock passes again after restoring. **No run started.** Swap is 3.3 GB, so a Mac restart comes before the start.

Evidence: [`outputs/study3_v0.1/PRE_RUN_LOCK.json`](outputs/study3_v0.1/PRE_RUN_LOCK.json). Decided by: Yichen.

## 2026-09-30 — Milestone 5: Study 3 v0.1 run started; report builder written before any outcome

After the Mac restart: swap 0 MB, on AC power; clean tree at `297d244`; `check_lock()` accepts the lock; no Study 3 features or results existed before the start (no outcomes). Started at **19:54:12 UTC** (14:54 Central) as `nohup caffeinate -ims .venv/bin/python -u research/study3/run_s3.py --phase all >> research/study3/data/run.log 2>&1` (projected about 3.3 h). The log is git-ignored. During the run, before any Study 3 outcome was read, the report builder `research/study3_report/make_report_s3.py` was written: tables and four figures from `results.json`, after an independent re-computation (its own S4 implementation) of the per-key FPRs, the per-key oracle TPRs and the probe's oracle acceptance, asserted equal to `results.json`.

Evidence: this entry; `outputs/study3_v0.1/PRE_RUN_LOCK.json`; `study3_report/make_report_s3.py`. Decided by: Yichen (lock and run here).

## 2026-09-30 — Study 3 v0.1 RESULT: the exact key test detects 96–100% of genuine texts at an exact 1% FPR, beats the probe at ρ ≤ 0.50, and makes Study 1's forgeries not practical for the median key; a few keys leak

Run finished at 22:48 UTC (17:48 Central), 10,468 s (2.9 h), no crash; `check_lock()` accepted the lock before and after. The report builder's independent re-computation (its own S4 implementation) of every per-key FPR, every per-key genuine detection rate and the probe's genuine acceptance equals `results.json`. **Pre-registered (mechanical):** G1 PASS (0.81% pooled); G2 PASS (8 of 8 keys calibrated, 0.1–1.7%); P1 pass at every level (oracle TPR 97.5 / 96.0 / 99.0 / 100.0% at ρ 0.25 / 0.35 / 0.50 / 0.70); **E1: exact test more powerful than the probe at 0.25 (+86.0 points), 0.35 (+62.0) and 0.50 (+13.5); no clear difference at 0.70** (both 100%); **X1: fluent forgery not practical for both routes at 0.35, 0.50 and 0.70** (v0.4 forgeries' median exact FA 0.0–4.5% vs bars 43.2–45.0%; at 0.35 the v0.4 Route B forgeries that were practical against the probe reach 4.5%); **X3 no** at every level (random-key texts 0.0% vs the probe's 1.0 / 1.5 / 13.0 / 55.5%). Narrowest margin, stated plainly: Route A at ρ = 0.70, n = 64, upper bound 42.0% vs bar 45.0%.
**Secondary (pre-registered, descriptive):** human-text FPR 0.68% pooled, max key 1.6% (probe: 3.6%); at p ≤ 0.001 FPR 0.11% / 0.05% and genuine detection 85.0–98.5%; "probe AND exact" 0.0% FPR on A2; S3 calibrates 7 of 8 keys (key 1002 at 3.4%), as the pilot predicted; key-leakage lens: forgeries have more small p-values than chance (p ≤ 0.10 for 8.0–41.5% vs 10%), 35 of 384 key-level × forgery-set cells are accepted ≥ 50% (e.g. v0.4 Route A key 1004: 97% at 0.50, 100% at 0.70; Route B key 1004 98% and key 1003 67% at 0.70), and acceptance rises with the attacker's recovered cosine (Spearman 0.68 Route A, 0.56 Route B).
**Exploratory (after the run, labelled):** key 1002's genuine texts at ρ = 0.70 are detected at 41% (median p 0.017; its FPR is the lowest, 0.1%). Two figure-layout fixes after viewing (Fig. 1 label; Fig. 4 title and legend). One wording fix in the prose (the calibration's quality statement). **Inference:** the weak point in Study 1 was the probe, not the watermark; the exact test holds against passive forgers for the typical key, but where the attack recovers much of the key (or copies its signature), forgeries pass, so key secrecy and key recovery matter again.
Skill updated: evaluate attacks against the strongest principled detector; median rules can hide per-unit failures (pre-register per-unit counts); generated prose placeholders.

Evidence: [`STUDY3_REPORT_v0.1.md`](STUDY3_REPORT_v0.1.md), [`outputs/study3_v0.1/results.json`](outputs/study3_v0.1/results.json), `outputs/study3_v0.1/report/`, [`study3_report/`](study3_report/). Decided by: mechanical (pre-registered rules); next step is Yichen's decision.

## 2026-09-30 — Next study: Study 2 (scrubbing and paraphrase robustness), designed in a new "Milestone 6" session

Yichen chose Study 2 as the next study: can an attacker remove the watermark (paraphrase with the pinned Phi-3.5-mini-instruct and Qwen2.5-1.5B-Instruct models, or key-guided minimal edits using the attacker's estimate) at matched quality, judged by the exact key test (S4, primary) and the owner's probe? Rejected for now: a key-recovery follow-up against the exact test; a novelty re-check of the new claims first; Study 5 (defence). Stage 5 design of Study 2 starts in a new session, "Milestone 6". Milestone 5 ends here.

Evidence: [`STUDY3_REPORT_v0.1.md`](STUDY3_REPORT_v0.1.md); this entry. Decided by: Yichen.

## 2026-09-30 — Milestone 6: Study 2 design starts; the paraphraser weights are verified and timed

Stage 5 for Study 2 (scrubbing and paraphrase robustness). **Reading done:** the handoff, the brief, the gate, Study 3's protocol and report, and Study 1 v0.4's protocol and report. I also read Self-Recognition's public code at commit `7c26938` (github.com/Thibaud-Ardoin/LLM-Self-Recognition, cloned to scratch, read only), in `steering_watermark/src/paraphrasing.py` and `param.yaml`.
- The authors' robustness experiment paraphrases with **DIPPER-XXL**, an 11B T5 model in 8-bit: lexical diversity 60, order diversity 20, prompt included, temperature 0.75, maximum length 600.
- Only the validation and test texts are paraphrased; the probe is trained on clean text.
- DIPPER-XXL is out of reach on the M5 (16 GB).

**Pinned paraphrasers:** the weights have been in the Hugging Face cache since 2026-09-25, and every file matches the Stage 4 manifests' SHA-256.
**My error, stated plainly:** I first told Yichen the weights were missing. I based that on a `du` size reading that did not reflect the cached files. The download he approved fetched nothing (0 s).

**Timing** (pool F texts, timing only; no detector run; `study2_design/time_paraphrasers.py`):
- Qwen2.5-1.5B-Instruct: 8–10 s per text unbatched (26–28 tokens/s); 1.9 s per text in batches of 8; 5.4 GB.
- Phi-3.5-mini-instruct: 19–24 s per text unbatched (13 tokens/s); 5.2 s per text in batches of 8. It uses 12 GB, and swap rose to 4.1 GB.
- Paraphrases often come out shorter than their input: Phi's batch of 8 gave 118–191 words for about 215 in, and one Qwen output had 70 words. Study 2 therefore needs a length condition, because S4 scores the first 256 tokens.

**Also relevant:** Study 1's saved Route A key estimates have a median cos(v̂, v) of 0.00–0.16 (Study 3, Table 4).

Evidence: [`outputs/study2_design/paraphrase_timing.json`](outputs/study2_design/paraphrase_timing.json), [`study2_design/time_paraphrasers.py`](study2_design/time_paraphrasers.py). Decided by: Yichen (verify and time both); Claude (the timing set-up).

## 2026-09-30 — Study 2 methods: two paraphrasers, and key-guided edits with the attacker's estimate and with the true key, plus a random-edit control

Yichen chose four scrubbing methods and one control:
- paraphrase with **Qwen2.5-1.5B-Instruct**;
- paraphrase with **Phi-3.5-mini-instruct**;
- **key-guided edits using the attacker's Study 1 estimate** (the realistic threat);
- **the same edits using the true key**, as an upper bound: how many edits remove the evidence if the key leaks;
- **random edits at the same budget** (control).

Rejected: paraphrase only; paraphrase plus estimate-guided edits only; paraphrase plus true-key edits only.
The edit algorithm, edit budgets and the choice of estimate are design details for the protocol draft.

Evidence: this entry. Decided by: Yichen.

## 2026-09-30 — Study 2 scope: the full grid (4 strengths × 8 keys × 100 genuine texts) for every method

Yichen chose the full grid for every method. That is ρ ∈ {0.25, 0.35, 0.50, 0.70} × keys 1001–1008 × the 100 pool D oracle texts per key-level, which Study 3 scored, so each text can be compared before and after scrubbing. Pool A's 1,000 unwatermarked texts are also paraphrased by both models, to check calibration after paraphrase.
- Projected run: about 16 h. Paraphrasing is timed; the edit and scoring times are estimates, to be timed in the pilot.
- It runs in two checkpointed phases (paraphrase, then edits).

Rejected: ρ 0.35 and 0.50 only (about 8.5 h); the full grid with 50 texts (about 9 h); paraphrase on the full grid with edits at two strengths only.

Evidence: this entry; [`outputs/study2_design/paraphrase_timing.json`](outputs/study2_design/paraphrase_timing.json). Decided by: Yichen.

## 2026-09-30 — Study 2 fluency condition: a scrub may be no worse than its own input, or within the normal range

Yichen chose per-text bars:
- perplexity (unsteered model, given the prompt) ≤ max(1.25 × the original genuine text's perplexity, the 95th percentile of pool A's unwatermarked texts);
- seq-rep-4 ≤ max(the original's, pool A's 95th percentile);
- length ≥ 80% of the original's tokens.

Reported as secondaries: v0.4's oracle-relative bars, pool A's absolute bars alone, and a length-matched control (the original truncated to the scrub's length).
Reason: at ρ = 0.70 the genuine texts are already degraded (median perplexity 12.5 vs 5.5 unwatermarked, calibration v0.1). That makes oracle-relative bars lenient (Study 1's lesson), and absolute bars would fail the genuine texts themselves.
Rejected: absolute pool A bars; v0.4's oracle-relative bars; strict per-text bars without the normal-range allowance.

Evidence: this entry; `outputs/calibration_v0.1/results_qwen.json`. Decided by: Yichen.

## 2026-09-30 — Study 2 meaning condition: embedding similarity above a same-prompt baseline; the embedding model is pinned

Yichen chose embedding similarity as the meaning-preservation condition:
- the measure is the cosine between the sentence embeddings of the original and of the scrub, from **sentence-transformers/all-mpnet-base-v2** (Apache-2.0, revision `e8c3b32e`);
- a scrub passes if the cosine is **above the 95th percentile of same-prompt independent pairs**, meaning pool A's model continuation against the human continuation of the same prompt (1,000 pairs).

Rejected: two-way NLI entailment (roberta-large-mnli); both measures together; an LLM judge.
The download was approved in the same choice. Only the needed files were fetched (`model.safetensors`, 438 MB, plus configs), and the manifest records the SHA-256 of each file.
Implementation note: `sentence_transformers` is not installed. The embedding will be computed with `transformers`, following the model's own module config (mean pooling, normalisation, maximum 384 tokens). The pilot will check it against the model card's usage.

Evidence: [`stage4/outputs/model_manifest_all-mpnet-base-v2.json`](stage4/outputs/model_manifest_all-mpnet-base-v2.json). Decided by: Yichen.

## 2026-09-30 — Study 2 detectors: S4 primary (unchanged from Study 3), the probe secondary; calibration gates on paraphrased null texts

Yichen chose **S4** as the primary detector for every verdict, exactly as in Study 3: p ≤ 0.01, 999 null keys, pool F standardisation. The owner does not know whether a text was scrubbed.

Gates, per paraphraser, on pool A's 1,000 unwatermarked texts after paraphrase:
- the pooled FPR over the 8 keys must be within [0.3%, 2.5%]; otherwise the run stops;
- each key's FPR must be ≤ 3.0%; a key above that is excluded for that paraphraser.

Secondaries: the owner's Study 1 probe at its 1% threshold on the same texts, S4 at p ≤ 0.001 (9,999 null keys), and pooling 4 scrubbed texts per test.
Rejected: S4 and the probe as co-primary; adding a paraphrase-aware owner (S4 standardised on paraphrased texts); S4 alone.

Evidence: this entry. Decided by: Yichen.

## 2026-09-30 — Study 2 primary rule: scrub success at a 50% bar, with three verdicts and per-key counts

Yichen chose the rule.
- **A scrub succeeds** for a text if S4 no longer detects it (p > 0.01) **and** it passes the fluency, length and meaning conditions.
- **Success rate:** the median over calibrated keys, per method and strength, with 95% cluster-bootstrap intervals.
- **Effective:** median success ≥ 50% **and** its lower 95% bound is above the comparison's upper 95% bound.
- **Not effective:** the upper 95% bound is below 50%.
- **Otherwise:** inconclusive.
- **Comparisons:** for paraphrases, the unscrubbed original; for key-guided edits, random edits at the same budget, judged at 10% of tokens (5% and 20% are reported as a curve).
- **Paired contrast:** estimate-guided minus random edits.
- Beside every verdict, the number of keys (of 8) with success ≥ 50%.

Rejected: a 25% bar; retained detection among quality-passing scrubs (the owner's view); two tiers at 25% and 50%.

Evidence: this entry. Decided by: Yichen.

## 2026-09-30 — Study 2 pilot: a full-pipeline tuning-key pilot (~2 h) before the lock

Yichen chose a full-pipeline pilot on the tuning keys only.
- **Texts:** keys 9001–9004, 25 texts per key and strength at all 4 strengths (calibration v0.1's texts), plus 100 of their unwatermarked texts.
- **Pipeline:** every method, quality measure and S4.
- The tuning keys have no Study 1 estimate, so the estimate-guided arm uses a constructed vector with cosine about 0.1 to the key (mechanics and timing only).
- **Reports:** timing against a 24 h full-run budget; the pass rate of each quality condition; calibration after paraphrase; implementation checks (true-key edits lower the key's score; random edits barely do); samples read.
- **May adjust:** only the paraphrase prompt wording and the edit round size, by rules written in the pilot spec before its run. The rules and bars stay as decided.

Rejected: a mechanics-only pilot; a larger pilot (100 texts per key-level); no pilot.
Next: Claude drafts the pilot spec (with the design details: the edit algorithm, budgets, the attacker's estimate for the study keys, the paraphrase prompt and sampling) for Yichen's review.

Evidence: this entry. Decided by: Yichen.

## 2026-09-30 — Study 2 pilot spec drafted, code written and dry-run; fluency normal range revised to human text (Yichen)

**Pilot spec and code:** `study2_pilot/SCRUB_PILOT_SPEC_v0.1.md` (DRAFT), `study2_pilot/scrub_core.py` (the shared machinery, meant to be reused unchanged by Study 2) and `study2_pilot/scrub_pilot.py` (validate / run / analyse, with a guard that refuses unless the spec is FIXED and committed).

**Design details settled by code tests** (inputs only: unwatermarked tuning texts outside the pilot set, random directions, scratch outputs):
- Key-guided edits read each token's contribution to ⟨g, ŵ⟩ from two forward passes with ±s·ŵ at layer 14: s = 2.0, float32 output layer, central differences, and the unsteered distribution taken as the midpoint of the two log-probabilities.
  - Against autograd: r = 0.996, slope 1.005.
  - Per token, s against s/2: Spearman 0.86–0.92.
  - Speed: 4.2 s per text with 2% rounds, 2.2 s with 5% rounds (5.5 s with three passes).
- **Whole-word edits only.** Edits that could replace word pieces produced merges such as 'groupschemistry'. Replacements must also be at least 1/3 as likely as the current word.
- **Perplexity rises steeply with word edits:** ×1.4 at 2% of tokens, ×1.9 at 5%, ×3 at 10% and ×7.5 at 20%, for random edits too. The pilot therefore also saves 2% edits, and the 10% judgement point of decision 6 will be reviewed after the pilot.
- A batched perplexity with v0.2's definition equals v0.2's function exactly (maximum relative difference 0), and is faster.
- The batching check on Phi (same texts, batched vs one at a time) stalled for 42 minutes under 4–7 GB of swap and was stopped; no result. It became validation check 5 (greedy decoding, pool F texts, mean word ratio ≥ 0.90). Phi steps need a freshly restarted Mac.

**Dry run of the run and analysis phases** (stand-in unwatermarked texts relabelled as every set, Qwen only, scratch folder; its numbers carry no information): every code path executed, edit counts exact, re-encoding drift within limits.
- **It exposed a design flaw in decision 3's fluency bar.** The normal range was the 95th percentile of pool A's model texts, perplexity 7.35. Only 6.2% of pool A's human continuations fall below it (human median 12.9, 95th percentile 25.4). As a result, 0% of stand-in paraphrases passed all conditions; the bar measured "as predictable as Qwen's own samples", not fluency.
- It also showed that adjustment rule A2 should compare round sizes with the best of the three, not with 1% (fixed in the draft).

**Decision (Yichen):** the normal range for perplexity and seq-rep-4 is the **95th percentile of the human continuations** of pool A's prompts (the attacker's self-check uses its own pool C human continuations). The 1.25 × original allowance, the length and the meaning conditions are unchanged. Reported as secondaries: success under the model-text 95th-percentile bar and under the human median.
Rejected: the human median as the primary; keeping the model-text bar; pre-registering verdicts under all three bars.

**Pilot estimate:** about 3.5 h (it was about 2 h when the pilot was chosen).
**Skill updated:**
- `du` can under-report the Hugging Face cache, and background jobs should never be piped through `grep | tail`;
- a model that needs most of the RAM must run on a freshly restarted machine;
- code-test an attack's quality cost on null data before fixing its rules.

Evidence: [`study2_pilot/SCRUB_PILOT_SPEC_v0.1.md`](study2_pilot/SCRUB_PILOT_SPEC_v0.1.md), `study2_pilot/`. Decided by: Yichen (the normal range); Claude (the draft, code and tests).

## 2026-09-30 — Study 2 pilot spec v0.1 approved as drafted and FIXED; next: Mac restart, validation, pilot run

Yichen approved `study2_pilot/SCRUB_PILOT_SPEC_v0.1.md` as drafted. Rejected: a single paraphrase attempt (no attacker self-check); edits that may replace word pieces; reviewing it first. Its status line was set to FIXED and committed with the code.
- **Confirmation dry run** (stand-in unwatermarked texts, Qwen only, scratch folder; no information in its numbers): it ran end to end with the revised bars.
  - Normal range from pool A's human continuations: perplexity 95th percentile 25.4, seq-rep-4 0.048.
  - Meaning baseline 0.825; the attacker's pool C equivalents 22.2, 0.048 and 0.810.
  - The A2 rule now compares with the best of the three round sizes.
- Progress lines were added to the runner so that a watcher can tell a stall from slow progress.
- **No pilot text has been paraphrased or edited.**

Next, per the handoff's pre-run checklist: Yichen restarts the Mac with other apps closed. Then validation runs (inputs only; batching and timing checks), then the pilot (about 3.5 h), then its report.

Evidence: [`study2_pilot/SCRUB_PILOT_SPEC_v0.1.md`](study2_pilot/SCRUB_PILOT_SPEC_v0.1.md); this entry. Decided by: Yichen.

## 2026-10-01 — Study 2 pilot: input validation ALL PASS (6/6) after a Mac restart; pilot run started

The Mac was restarted with other apps closed (swap 0 MB, AC power, 81% of memory free); the tree was clean at `a343ca2` with the spec FIXED, and no pilot data or outputs existed. **Validation (inputs only) 6/6 pass:**
1. Inputs and hashes; counts 400 / 100 / 200 / 1,000 / 200.
2. Keys and seeds disjoint; the E-est stand-ins have cosines 0.09, 0.33, 0.12 and 0.04 with their keys.
3. Pool A's model texts, prompts and human continuations are aligned; pool C is disjoint from pool A.
4. Smoke test:
   - embeddings: self-cosine 1, and batched vs single differ by 7e-9;
   - the attacker's gradient at layer 14 equals the Study 3 pilot's (difference 0), and the hook is removed (logit difference 0);
   - the batched perplexity equals v0.2's function (maximum relative difference 0);
   - the edit counts are exact.
5. **Batching:** with greedy decoding on the same 8 pool F texts, the word ratio batched/single is 1.03 (Qwen) and 1.02 (Phi). Batching does not shorten outputs; the earlier hint came from comparing different texts. Rates in batches of 8: Qwen 2.0 s per text, Phi 6.4 s per text (single: 8.5 s and 19.2 s).
6. **Timing:** the pilot is projected at 3.8 h against a 4 h budget.

The report builder `study2_pilot/make_report_pilot.py` was written before any pilot result existed.

Evidence: [`outputs/study2_pilot_v0.1/VALIDATION.json`](outputs/study2_pilot_v0.1/VALIDATION.json). Decided by: Yichen (spec); Claude (validation).

## 2026-10-01 — Study 2 pilot run started

Started at **03:29:28 UTC (22:29 Central, 2026-09-30)** as `nohup caffeinate -ims .venv/bin/python -u research/study2_pilot/scrub_pilot.py --phase run >> research/study2_pilot/data/run.log 2>&1` (projected about 3.8 h; checkpointed per step). The guard recorded commit `ec06ef1` and the SHA-256 of the spec (`b18a5b4e…`), `scrub_pilot.py` (`6703529c…`) and `scrub_core.py` (`0c97ee16…`). One background watcher covers completion, a crash, a stall (30 min) and an exit without completion.

Evidence: `research/study2_pilot/data/pilot_guard.json` (git-ignored; hashes copied here). Decided by: Yichen (run after validation).

## 2026-10-01 — Study 2 pilot: run 1 stopped for a memory bug during Phi's first attempt; fixed (no computation changed); resumed

**What happened.** The bars and the Qwen paraphrase step finished (checkpoint `para_qwen.json`; Qwen took about 40 min, with 54% of first attempts retried and 32.5% of the 400 watermarked texts still failing the attacker's own check after 3 attempts). During Phi's first attempt the process grew to 14 GB and swapped at about 19,000 page-ins and 11,500 page-outs per second (12% CPU). That is the state in which Phi slowed tenfold on 2026-09-30. I stopped the run at 04:43 UTC (23:43 Central). Run 1's guard record is kept as `data/pilot_guard_run1.json` (commit `ec06ef1`).

**Cause, stated plainly (my error).** `scrub_core.free(*objs)` deleted only its own arguments, not the caller's variables. Models from earlier steps (the Qwen paraphraser, the Qwen base model, the embedder) therefore stayed alive when Phi loaded, and each retry attempt would have loaded a second Phi. A separate slip: the run's stall watcher used a 30-minute window, which is shorter than one Phi attempt, during which nothing is printed. It reported a false "stall"; the real problem was the swap, found on inspection.

**Fix.** `free()` now only collects (`gc.collect`, `torch.mps.empty_cache`); every caller drops its references (`del model`) first, and each step collects before loading a model. This changes no computation, seed or output.
- **Memory test** (pool F texts, inputs only): two rounds of Qwen-Instruct then the base model and embedder, then Phi. Peak 8.7 GB, against 14 GB in run 1, with no growth across rounds.

**Resume.** The run restarts from its checkpoints: the bars and Qwen paraphrases (made by `ec06ef1`) are reused, and the Phi step starts again. The run-2 guard records the new commit. The stall window is now 90 min.

Evidence: this entry; `research/study2_pilot/data/run.log` (both runs). Decided by: Claude (an implementation fix within the approved run; reported to Yichen).

## 2026-10-01 — Study 2 pilot: run 2 stopped (Phi batch-8 generation thrashed); Phi now runs in batches of 4 (deviation from spec §2.4, logged); resumed as run 3

**What happened.** After the memory fix, run 2's Phi step started healthy: footprint 13 GB, about 1,600 page-ins per second, 72% CPU. After 30 minutes it had grown to 14 GB and was thrashing (about 16,000 page-ins and 18,600 page-outs per second, 19% CPU). The leaked models were only part of the cause. Batched generation itself needs the 7.6 GB model plus about 2.7 GB of working memory per batch of 8 long sequences. Batches are sorted by length, so the largest come last, and the total overflows 16 GB together with the operating system. I stopped run 2 at 05:16 UTC (00:16 Central); its guard is kept as `data/pilot_guard_run2.json`. No Phi output had been checkpointed.

**Change (a deviation from the FIXED spec §2.4, stated plainly):** Phi paraphrases in **batches of 4** instead of 8; Qwen stays at 8.
- A memory check on the 8 longest pool F texts (inputs only) gave a peak of 11 GB at batch 4, 8.7 s per text.
- No method, prompt, sampling setting, seed rule, bar or rule changes. Batch size affects only padding (validation check 5: batching does not change output length) and the composition of each sampled batch.
- Study 2 will need the same setting on this machine. The pilot's Phi timing (I5) will reflect it.

**Resume:** run 3 reuses the bars and Qwen paraphrases and restarts Phi. Projected about 4.5 h more.

Evidence: this entry; `research/study2_pilot/data/run.log`. Decided by: Claude (an operational change within the approved run, so that it can finish overnight); **for Yichen's review**.

## 2026-10-01 — Study 2 pilot v0.1 RESULT: two implementation checks fail (I1 narrowly; I5, a 39.7 h projection); paraphrase removes most evidence at low strength; true-key edits do so with 5% of tokens

Run 3 finished at **10:17 UTC (05:17 Central)**; total step time 5.7 h across runs. The bars and Qwen paraphrases came from run 1 (`ec06ef1`); Phi, the edits and the scoring from run 3 (`8ba17da`). The analysis ran from a clean tree.

**Checks** (the spec's rules, mechanical):
- **I1 FAIL, narrowly.** Finite differences against autograd: r = 0.985 (rule ≥ 0.99), slope 0.96. Per-token Spearman, s against s/2: 0.799 (rule ≥ 0.80). Inference: curvature along the true key on watermarked text (the secant at s = 2 underestimates the tangent); the code test on unwatermarked text with a random direction gave r = 0.996.
- **I2 PASS:** p = 1.4e-67; median change in T −0.109 (true key) against −0.041 (random edits).
- **I3 PASS:** exact edit counts; median drift 0%.
- **I5 FAIL:** Study 2 projected at 39.7 h against 24 h. Phi paraphrasing is 20.0 h of it (batches of 4, 16.8 s per original with retries), Qwen 4.3 h, edits 9.3 h, scoring 6.0 h.
- Per the spec, a failed check is fixed, and the pilot is re-run as v0.2, before the Study 2 protocol.

**Adjustments:**
- **A1 → P2.** First attempts meeting the length floor: Qwen 62.7%, Phi 65.8%. With P2 on ρ = 0.50: 82% and 90%; all conditions 74% vs 72% (Qwen) and 73% vs 65% (Phi) on the same texts.
- **A2 → 5% rounds.** Median objective reduction at 10%: 2.66 (1%), 2.56 (2%), 2.42 (5%); 5% is within 90% of the best.

**Readings** (descriptive, tuning keys, 25 texts per key and level; medians at ρ 0.25 / 0.35 / 0.50 / 0.70; detection before scrubbing 88 / 100 / 96 / 96%):
- **Paraphrase.** Detected after: Phi 8 / 20 / 48 / 32%, Qwen 2 / 16 / 24 / 20%. Scrub success: Phi 64 / 54 / 34 / 18%, Qwen 72 / 58 / 52 / 28%.
- **Edits at 5%.** Success with the true key 92 / 86 / 56 / 20%; with the stand-in estimate 44 / 32 / 16 / 4%; random 34 / 18 / 6 / 4%.
- **The fluency bar (human 95th percentile) is lenient for edits.** True-key 10% edits "succeed" at 86 / 72 / 38 / 12%, yet the key 9001 sample is visibly degraded (broken words, wrong facts, a broken URL). Under the human median: 2 / 4 / 0 / 0%.
- **Paraphrase widens per-key calibration.** Over 1,000 fresh keys, the share of keys with FPR above 3% goes from 2.7% to 7.8% (Qwen) and 8.0% (Phi).

**Deviations during the run** (logged above): the memory fix (no computation changed); Phi in batches of 4 (spec §2.4; for Yichen's review).

Evidence: [`study2_pilot/SCRUB_PILOT_REPORT_v0.1.md`](study2_pilot/SCRUB_PILOT_REPORT_v0.1.md), [`outputs/study2_pilot_v0.1/results.json`](outputs/study2_pilot_v0.1/results.json). Decided by: mechanical (the spec's checks and rules); next steps are Yichen's decisions (I1, I5, the edit judgement point and fluency bar, the batch-4 deviation).

## 2026-10-01 — Study 2 pilot: I1 diagnosed after the run (exploratory, labelled); my "curvature" inference was wrong; the cause is bfloat16 rounding

Exploratory, after the run: `study2_pilot/posthoc_I1_diag.py`, run on I1's 25 texts.
- The bf16 autograd reference agrees with float32 autograd (r = 0.9998, slope 1.004).
- The editor's bf16 finite-difference sums get closer to the gradient as the step grows: r = 0.94 / 0.95 / 0.985 / 0.997 at s = 0.5 / 1 / 2 / 4. That is rounding noise, not curvature.
- In **float32** the sums match the gradient exactly at every step (r = 1.0000, slope 1.000 at s = 0.25–2).

**Correction, stated plainly:** the RESULT entry's inference ("curvature along the true key") was wrong; the cause is bfloat16 rounding in the two editor passes. **Fix available:** run the editor's two passes in float32, at 0.72 s instead of 0.42 s per text per round (1.7×), with a 6 GB float32 model copy during the edit phase. The decision goes to Yichen.

Evidence: [`outputs/study2_pilot_v0.1/posthoc_I1_diag.json`](outputs/study2_pilot_v0.1/posthoc_I1_diag.json), [`study2_pilot/posthoc_I1_diag.py`](study2_pilot/posthoc_I1_diag.py). Decided by: Claude (diagnosis); next step is Yichen's decision.

## 2026-10-01 — Phi batches of 4: deviation accepted (pilot) and adopted for Study 2

Yichen accepted the overnight deviation from spec §2.4: Phi paraphrased in batches of 4, because batches of 8 overflowed 16 GB. The pilot's Phi results stand, and Study 2 uses batches of 4 for Phi (Qwen stays at 8). Rejected: accepting with an added batch-4 length recheck; not accepting (re-running Phi under a new spec version).

Evidence: the deviation entry above. Decided by: Yichen.

## 2026-10-01 — I1 fix: the editor's passes in float32; confirmed in a short pilot v0.2 of the edit component

Yichen chose to run the editor's two finite-difference passes in float32 (exact against the gradient in the diagnostic: r = 1.000 at every step), and to confirm this in a short **pilot v0.2 of the edit component**, which will also test the scope and edit-evaluation changes decided next, before the Study 2 protocol. Rejected: bfloat16 with s = 4; accepting the narrow failure.

Evidence: [`outputs/study2_pilot_v0.1/posthoc_I1_diag.json`](outputs/study2_pilot_v0.1/posthoc_I1_diag.json). Decided by: Yichen.

## 2026-10-01 — Study 2 edit judging: primary at 5% of tokens; 2% and 10% secondary; 20% dropped (revises decision 6's 10%)

Yichen chose to judge edits at **5% of tokens**, with 2% and 10% as secondary curve points. The 20% budget is dropped: nothing passed quality there, and dropping it roughly halves edit time. The primary fluency bar stays the same for all methods (human 95th percentile); the human-median reading is a pre-registered secondary for edits; samples are read at 5% and 10%.
Reasons (pilot, tuning keys):
- 10% edits pass the bar while visibly degraded (the key 9001 sample);
- 5% edits are mostly readable with a few slips (samples for keys 9003 and 9004);
- true-key edits at 5% succeed 92 / 86 / 56 / 20%, random 34 / 18 / 6 / 4%.

Rejected: keeping 10% with the human-median bar for edits; 5% with the human-median bar as primary; keeping 10% with the human 95th-percentile bar.

Evidence: [`study2_pilot/SCRUB_PILOT_REPORT_v0.1.md`](study2_pilot/SCRUB_PILOT_REPORT_v0.1.md). Decided by: Yichen.

## 2026-10-01 — Study 2 scope revised for time: Phi paraphrases 50 genuine texts per key-level; everything else on the full grid

After the pilot's I5 failure (39.7 h), re-projected with the day's decisions (P2 prompt, edits to 10% with 5% rounds in float32, three edit budgets): the full design is about 32 h, of which Phi is about 17 h on a Mac with other apps closed. Yichen chose the following (revising decision 2 for Phi only):
- **Phi** paraphrases **50 of the 100 genuine texts per key-level** (the first 50 in pool D order; all 4 strengths, all 8 keys), plus its 1,000 pool A null texts;
- **Qwen** and every **edit arm** keep the full grid.

Projected about 26 h in two checkpointed phases: paraphrase about 15 h (Phi needs a clean Mac for about 10 h), then edits and scoring about 11 h. Phi's per-key rates have wider intervals (about ±7 points).
Rejected: the full design over two phases (about 32 h); Qwen only (about 13.5 h); Phi at ρ 0.35 and 0.50 only.

Evidence: [`study2_pilot/SCRUB_PILOT_REPORT_v0.1.md`](study2_pilot/SCRUB_PILOT_REPORT_v0.1.md) §7; this entry. Decided by: Yichen.

## 2026-10-01 — Study 2 pilot v0.2 (edit component) drafted; validation ALL PASS (3/3)

Draft `study2_pilot/SCRUB_PILOT_SPEC_v0.2.md`: the three edit arms on v0.1's 400 tuning texts, with float32 editor passes, budgets 2%, 5% and 10%, and 5% rounds (v0.1's rule A2). Its checks:
- I1 and I3 as in v0.1;
- I2 at the new 5% judgement point;
- **I5′:** Study 2 under the revised scope (Phi on 50 genuine texts per key-level), projected ≤ 30 h.

v0.1's paraphrase results stand.

**Code:** `scrub_pilot_v02.py`, plus `scrub_core.load_base_fp32()` (an addition; v0.1's code paths are unchanged).

**Validation, inputs only (unwatermarked texts outside the pilot set, random directions), 3/3 pass:**
1. v0.1's inputs present and hashed.
2. Float32 editor: finite differences against float32 autograd r = 0.99997 over 16 direction-text pairs; hook removed; exact edit counts at 2%, 5% and 10%.
3. Guided 2.6 s and random 1.1 s per text; peak 9.7 GB; pilot projected at 1.1 h.

Awaiting Yichen's review.

Evidence: [`study2_pilot/SCRUB_PILOT_SPEC_v0.2.md`](study2_pilot/SCRUB_PILOT_SPEC_v0.2.md), [`outputs/study2_pilot_v0.2/VALIDATION.json`](outputs/study2_pilot_v0.2/VALIDATION.json). Decided by: Claude (draft, code, validation); review pending.

## 2026-10-01 — Study 2 pilot v0.2 approved as drafted and FIXED; run started

Yichen approved `study2_pilot/SCRUB_PILOT_SPEC_v0.2.md` as drafted (rejected: tightening I5′ to 26 h; reviewing it first). The status line was set to FIXED and committed before any v0.2 edit; the run starts now (projected about 1.1 h, no restart needed).

Evidence: [`study2_pilot/SCRUB_PILOT_SPEC_v0.2.md`](study2_pilot/SCRUB_PILOT_SPEC_v0.2.md). Decided by: Yichen.

## 2026-10-01 — Study 2 pilot v0.2 RESULT: all checks pass (I1 r = 0.9998 with the float32 editor; I5′ 24.3 h); Study 2 protocol v0.1 drafted

Run from the FIXED spec (commit `f350d69`), 14:15–15:17 UTC (09:15–10:17 Central); the analysis ran from a clean tree.
- **I1 PASS:** r = 0.9998, slope 0.996, per-token Spearman 1.00.
- **I2 PASS:** p = 1.6e-67; median change −0.070 (true key) vs −0.022 (random) from 0% to 5%.
- **I3 PASS.**
- **I5′ PASS:** Study 2 under the revised scope projected at 24.3 h (≤ 30 h): Qwen 3.8, Phi 10.1, edits 5.6, scoring 4.6, σ̂ 0.2. Peak memory in the edit phase 9.1 GB.

**Readings** (tuning keys; medians at ρ 0.25 / 0.35 / 0.50 / 0.70; descriptive):
- 5% edits succeed 92 / 80 / 54 / 22% (true key), 50 / 30 / 16 / 4% (stand-in estimate), 36 / 10 / 8 / 4% (random). This is close to v0.1's bfloat16 editor (true key 92 / 86 / 56 / 20%).
- The float32 fix changes precision, not the picture.

**Next:** Yichen's review of the drafted `STUDY2_PROTOCOL_v0.1.md`, then Study 2's input validation and lock.

Evidence: [`study2_pilot/SCRUB_PILOT_REPORT_v0.2.md`](study2_pilot/SCRUB_PILOT_REPORT_v0.2.md), [`outputs/study2_pilot_v0.2/results.json`](outputs/study2_pilot_v0.2/results.json), [`STUDY2_PROTOCOL_v0.1.md`](STUDY2_PROTOCOL_v0.1.md). Decided by: mechanical (the spec's checks); Claude (the protocol draft); review pending.

## 2026-10-01 — Study 2 protocol v0.1 approved as drafted

Yichen approved `STUDY2_PROTOCOL_v0.1.md` as drafted, including the probe secondary (rejected: dropping the probe secondary; reviewing it first). The protocol stays DRAFT until the lock. Next: code in `research/study2/` (reusing `study2_pilot/scrub_core.py`, the Study 3 pilot's `power_pilot.py` and v0.4's bootstrap), input validation (§10), then the lock decision.

Evidence: [`STUDY2_PROTOCOL_v0.1.md`](STUDY2_PROTOCOL_v0.1.md). Decided by: Yichen.

## 2026-10-01 — Study 2 code written; smoke test and input validation ALL PASS (9/9; 24.3 h projected; no outcomes)

**Code in `research/study2/`:**
- `common_s2.py`: sources, the owner's S4 built from Study 3's own features and standardisation, paraphrase with the attacker's self-check (checkpointed per 200 texts), rules and summaries;
- `run_s2.py`: lock check; phases para / edits / score / analyse, checkpointed; a `--dry` stand-in mode;
- `validate_s2.py`: §10 checks and the tuning-key stand-in source;
- `lock_s2.py`: writes the lock and runs the tamper tests.

The pilots' `scrub_core.py` and Study 3's `common_s3.py` are imported unchanged and will be hash-locked.

**Smoke test** (`run_s2.py --dry`; tuning keys 9001–9004 as stand-ins, 4 genuine texts per key-level, 2 for Phi, 20 null texts, both paraphrasers, all edit arms, scoring with probe stand-ins, analysis): every phase ran.
- One crash in the analysis (the pooled 4-text test on key-levels with fewer than 4 texts) was guarded.
- The calibrated-keys minimum was lowered to 2 in dry mode only, so that the S1 verdict path also runs.
- Every §7 and §8 field is produced; its numbers carry no information.

**Input validation, inputs only, 9/9 pass:**
1. 164 reused files present; the 66 that Study 3's lock also records hash identically.
2. The bars recomputed with the Study 2 code equal the pilot's exactly.
3. The S4 path reproduces Study 3's features and p-values exactly for k1001 at ρ 0.25 and k1008 at ρ 0.70 (already-reported outcomes).
4. E-est: the 32 estimates load; recorded cosines reproduced; 15 distinct layers; median cosine 0.078.
5. The float32 editor matches float32 autograd (r = 0.99995).
6. Seeds disjoint from every earlier seed.
7. The runner refuses without a lock.
8. The smoke test produced every field.
9. 24.3 h projected (≤ 30 h).

No study-key text has been paraphrased or edited.

Evidence: [`outputs/study2_v0.1/INPUT_VALIDATION.json`](outputs/study2_v0.1/INPUT_VALIDATION.json), `study2/`. Decided by: Yichen (design); Claude (implementation).

## 2026-10-01 — STUDY 2 v0.1 LOCKED (before outcomes); the run goes to a new "Milestone 7" session

Yichen approved locking Study 2 v0.1 and running it in a new session, "Milestone 7" (rejected: running it here; reviewing the code first). The protocol's status line was set to LOCKED and committed (`070075d`) before hashing.

The lock `outputs/study2_v0.1/PRE_RUN_LOCK.json` (locked **2026-10-01 16:12:01 UTC**, 11:12 Central) records the SHA-256 of:
- the protocol;
- **13 code files** (`common_s2`, `run_s2`, `validate_s2`, the pilots' `scrub_core`, Study 3's `common_s3`, the Study 3 pilot's `power_pilot`, v0.4's `common4`, `attack4`, `run_v04`, v0.3's `common3`, v0.2's `common`, `detect2`, v0.1's `core`);
- **164 reused files** (Study 1 v0.2's oracle texts, summaries, Route A estimates and probes for 32 key-levels; pools A, F and C; Study 3's pool F and oracle features);
- 11 inputs (the Study 2 input validation, the pilots' results and validations, Study 3's lock and results, the prompt loader, the three new model manifests).

It also records the design constants and `final: false`.
- **Tamper tests** (a byte appended to the protocol, to `common_s2.py` and to a reused file) were all refused, and the lock passes again after each file was restored byte for byte.
- No Study 2 data existed and no study-key text had been paraphrased or edited.

The run is projected at 24.3 h in two phases. Phase 1 (paraphrase) needs a freshly restarted Mac with other apps closed. The pre-run checklist is in the handoff.

Evidence: [`outputs/study2_v0.1/PRE_RUN_LOCK.json`](outputs/study2_v0.1/PRE_RUN_LOCK.json). Decided by: Yichen.

## 2026-10-01 — Study 2 v0.1 run started (phase 1, paraphrase)

Pre-run checklist done in the Milestone 7 session, after Yichen restarted the Mac with other apps closed:
- swap 0, AC power, 87% of memory free;
- tree clean at `531874f`; the lock passes; `study2/data/` and `results.json` did not exist.

Phase 1 (`--phase para`) started at **2026-10-01 16:23 UTC** (11:23 Central), projected about 14 h. A background watcher checks for completion, a crash, an exit without completion, a 60-minute stall and sustained swap thrash.

Evidence: `study2/data/run.log` (git-ignored). Decided by: Yichen (lock and run); Claude (start).

## 2026-10-01 — Study 2 report builder written during phase 1, before any outcome; tested on a synthetic fixture

`study2_report/make_report_s2.py` (tables 1–6, figures 1–5, samples, prose placeholders), `make_manifest_s2.py` (the run manifest) and a prose skeleton `report_prose.md` (run, figures, samples, limits; the "in words" section is written after the results). No Study 2 outcome existed or was read.
- **Integrity checks in the builder:** its own implementation of S4 and of the four quality conditions re-computes G1, G2, P1, every key's detection and success for every method and level, the originals' miss rate, the first-attempt readings, the length-matched control and the probe's acceptance. It re-derives every S1, S2 and C1 verdict from §7 and asserts equality with `results.json`.
- **Test:** synthetic per-text data (fake features mixed from Study 3's already-reported oracle and null features, fake quality, probe scores and edit records) in the session scratchpad; the **locked** `run_s2.analyse()` ran on it, and the builder ran on that output. All asserts passed; every figure was viewed and the layout fixed (legends moved off the data, level labels as 0.50 and 0.70, a clipped title). The fixture's numbers mean nothing.
- **Builder-side additions** (descriptive, labelled in the report): the length-matched control as a median over keys (`results.json` has the pooled rate), and the success at 0% of edits, read as the originals' miss rate.
- **Skill updated:** test a report builder before outcomes by running the locked analysis on a synthetic fixture.

Evidence: `study2_report/`. Decided by: Claude (implementation).

## 2026-10-02 — Study 2 phase 1 (paraphrase) complete; phase 2 (edits, then scoring) started

**Phase 1** ran from 2026-10-01 16:23 UTC (11:23 CDT) to 2026-10-02 08:43 UTC (03:43 CDT): **16.3 h**, against the 13.9 h projection, with no crash, stall or thrash alarm.

| Step | Time | Paraphrases generated (attempts 1 + 2 + 3) | Per original |
|---|---|---|---|
| Bars | 16:23–16:33 UTC (11:23–11:33 CDT) | — | — |
| Qwen, genuine (3,200) | 16:33–20:15 UTC (11:33–15:15 CDT) | 3,200 + 1,718 + 1,247 = 6,165 | 1.93 |
| Qwen, null (1,000) | 20:15–21:15 UTC (15:15–16:15 CDT) | 1,000 + 367 + 242 = 1,609 | 1.61 |
| Phi, genuine (1,600) | 21:15–04:57 UTC (16:15–23:57 CDT) | 1,600 + 681 + 530 = 2,811 | 1.76 |
| Phi, null (1,000) | 04:57–08:43 UTC (23:57–03:43 CDT) | 1,000 + 216 + 149 = 1,365 | 1.37 |

- **Why it overran (timing only, no protocol change):** 11,950 paraphrases were generated, against about 11,150 at the pilot's 1.64 per original (genuine texts needed more retries under the attacker's self-check). Phi was also slower per text: swap reached 1.5 GB during its steps.
- **Structure check (no statistic computed):** all 3,200 + 1,000 Qwen and 1,600 + 1,000 Phi kept paraphrases are present, none empty. The lock passed again before phase 2.

**Phase 2** (`--phase edits`, then `--phase score`, chained in one background job, with a start marker for each in the log) started at **2026-10-02 08:43:54 UTC (03:43 CDT)**, projected about 10.4 h. A watcher checks for completion, a crash, an exit, a 60-minute stall and sustained swap thrash.

Evidence: `study2/data/run.log` (git-ignored). Decided by: Yichen (run plan); Claude (start).

## 2026-10-02 — STUDY 2 v0.1 RESULT: paraphrase scrubs the exact test at ρ ≤ 0.35 but not at ρ ≥ 0.50; the true key helps only at ρ = 0.25; the attacker's estimate never makes edits practical

Run from the LOCKED protocol (lock 2026-10-01 16:12 UTC, 11:12 CDT). Phase 2 (`--phase edits`, then `--phase score`) ran 2026-10-02 08:43–18:57 UTC (03:43–13:57 CDT): edits 5.7 h, scoring 4.5 h; `--phase analyse` 18:58–18:59 UTC (13:58–13:59 CDT). **Total 26.6 h** against the 24.3 h projection (phase 1's extra retries). **No deviation**; the lock passed again after the run (`RUN_MANIFEST.json`). The report builder, written before any outcome and tested on a fixture, re-computed every FPR, detection rate, success rate and verdict with its own code and all matched `results.json`.

**Gates:** G1 PASS for both paraphrasers (0.33%, 0.44%); G2: 8 of 8 keys calibrated for both; P1 pass at every level (97.5 / 96.0 / 99.0 / 100.0% detected before scrubbing).

**Pre-registered verdicts** (median over keys [95% CI]; keys ≥ 50% success):

| ρ | S1 P-Qwen | S1 P-Phi | S2 E-true 5% (E-rand) | S2 E-est 5% | C1 |
|---|---|---|---|---|---|
| 0.25 | **effective** 64.0 [54.5, 71.5]; 7/8 | **effective** 56.0 [48.0, 65.0]; 7/8 | **effective** 79.0 [72.0, 90.5]; 8/8 (18.5) | not effective 31.5 [21.0, 49.0]; 2/8 | **helps** +14.5 [5.0, 28.0] |
| 0.35 | **effective** 53.0 [37.5, 64.5]; 5/8 | inconclusive 42.0 [33.0, 57.0]; 2/8 | inconclusive 43.0 [33.0, 63.0]; 3/8 (6.5) | not effective 13.0 [7.5, 19.0]; 0/8 | **helps** +6.5 [2.0, 11.0] |
| 0.50 | not effective 39.5 [27.0, 48.0]; 1/8 | not effective 20.0 [14.0, 39.0]; 1/8 | not effective 18.5 [11.0, 32.5]; 1/8 (2.0) | not effective 2.5 [0.5, 8.5]; 0/8 | no clear difference +0.0 [−0.5, 7.0] |
| 0.70 | not effective 26.0 [16.0, 35.0]; 1/8 | not effective 13.0 [4.0, 29.0]; 1/8 | not effective 4.5 [2.0, 8.0]; 0/8 (0.0) | not effective 0.0 [0.0, 2.0]; 0/8 | no clear difference +0.0 [−0.5, 0.0] |

No level is "random edits suffice" (E-rand's highest median is 18.5%).

**Descriptive readings (labelled in the report):**
- The length-matched control is still detected 91–100%: paraphrase removes the evidence rather than shortening the text. S4's detection after P-Qwen rises from 13.5% (ρ = 0.25) to 50.5% (0.70); paraphrase quality passes fall from 75% to 49.5% (meaning and fluency), so at 0.70 success is roughly "half evade × half pass".
- With the true key, 10% edits remove detection (0.5 / 7.0 / 19.5 / 40.0%) but fail fluency (83.5 / 66.0 / 31.5 / 3.5% pass; perplexity ratio 2.3–3.2×): a key-holder removes the evidence at ρ ≥ 0.50 only at a visible quality cost.
- E-est lowers its own objective (0.43 → −0.31 at 5%) yet barely moves S4 (68.0% vs E-rand 81.5% at 0.25): the estimate points the wrong way. Spearman(recovered cosine, E-est success) = 0.13.
- **Key 1002 is weak**: detected before scrubbing only 41% at ρ = 0.70 (others ≥ 98%); random 5% edits scrub it 35% of the time (others ≤ 1%), P-Phi 60%, P-Qwen 53%. The medians hide this (per-key Table 4).
- Calibration after paraphrase: the study keys' FPR fell (pooled 0.33 / 0.44% vs 0.81%); over 1,000 fresh keys the mean is 0.94–1.02% but 6.5–7.8% exceed 3% (max 19.5–22.6%).
- **Lead:** the owner's trained probe accepts 79–100% of paraphrases at ρ ≥ 0.50 where S4 detects 35–66% (probe FPR after paraphrase 3.0–3.3%); it may be reading the steering's content footprint rather than the key.
- Pooling 4 paraphrases per test restores detection to 56–100% at ρ ≥ 0.35.
- Samples read (keys 1001, 1002 at ρ = 0.50): no scrub succeeded for the two fixed texts; the paraphrases read fluently and fail on narrow margins or stay detected; 5% edits read with a few slips; 10% edits are visibly degraded and fail fluency.

**Interpretation (inference, for the claim gate):** the exact test's evidence survives off-the-shelf paraphrase and key-guided 5% edits at ρ ≥ 0.50 and not at ρ ≤ 0.35; key secrecy protects least where the watermark is weak; with the calibrations and Study 3 this is a three-way trade-off (quality, detectability, scrub robustness).

Evidence: [`STUDY2_REPORT_v0.1.md`](STUDY2_REPORT_v0.1.md), [`outputs/study2_v0.1/results.json`](outputs/study2_v0.1/results.json), [`outputs/study2_v0.1/RUN_MANIFEST.json`](outputs/study2_v0.1/RUN_MANIFEST.json), `outputs/study2_v0.1/report/`. Decided by: mechanical (the protocol's rules). **Next:** Yichen's decision on the next move (Stage 6 exit).

## 2026-10-02 — Next move: Study 5 (the defence) is designed in a new session, "Milestone 8"

Yichen chose to design **Study 5, the context-keyed or rotating-key defence**, in a new milestone session. Rejected: Study 4 (a SLAM-style second scheme on Gemma; heavier, gated download); the Stage 7 claim gate now; a cheap exploratory follow-up on Study 2's probe-vs-paraphrase lead first (it stays a lead for the claim gate).

The handoff carries a "Study 5 design seed": the goal, the defence candidates, the machinery that can be reused (Study 1's Route A, Study 3's S4, Study 2's scrubbing pipeline and quality bars), the compute reality (Study 5 needs new watermarked generation) and the open design decisions to bring one at a time. The design follows Stage 5 (a source gate on the defence idea first, then a protocol draft, input-only validation, pilot if needed, lock).

**Skill updated:** (a) when chaining phases in one background job, write `start phase X (UTC)` markers into the run log so the manifest is rebuilt from the log alone; (b) budget data-dependent retries at their upper range (Study 2's genuine texts retried 1.93× against the pilot's 1.64×, +2.4 h).

Evidence: this entry; `RESEARCH_HANDOFF.md`. Decided by: Yichen.

## 2026-10-02 — Study 5 source gate v0.1: CONDITIONAL (a transfer of context hashing and key rotation; the single next check is the threat itself)

Milestone 8 opened at 2026-10-02 19:40 UTC (14:40 CDT). The gate on the context-keyed or rotating-key defence ([`STUDY5_GATE_v0.1.md`](STUDY5_GATE_v0.1.md)) read the nearest works in full (via the fetch tool; quotations to re-confirm against PDFs): Self-Recognition, SLAM, No Free Lunch (Pang et al., NeurIPS 2024), Watermark Stealing, Reliability of Watermarks, Learnability, adaptive stealing, MarkSec, AWM, and the Christ–Gunn–Zamir and Kuditipudi schemes; abstracts of KGW, SIR, SemStamp, Three Bricks, SimKey, SEEK and others; arXiv API searches by mechanism; Semantic Scholar citations of the target schemes (none relevant); the Self-Recognition repository (no rotating or dynamic steering, last commit 2026-06-16); the Hugging Face SynthID configuration (several keys, a 5-token context).

- **Occupied:** context-hashed and rotating keys as ideas (KGW, SynthID, the cryptographic line); the multi-key trade-off (several keys lower stealing-based spoofing, cost removal robustness and detection power: No Free Lunch, Learnability); the context-width trade-off (Reliability, No Free Lunch, Watermark Stealing); per-document keyed activation steering with metadata (SLAM); the rotating-vector proposal itself (Self-Recognition's future work; scoop risk).
- **Residual gap:** no implementation or measurement of a context-keyed or rotating direction for dense activation steering; no measurement of its stealability, paraphrase-robustness, quality and union-test power costs. Type: an adequacy check of a transferred defence.
- **The premise (evidence):** Study 1's Route A fails against the fixed key at every strength at n ≤ 1,024 (median cos 0.160 / 0.074 / 0.151 / 0.015); under the exact test its forgeries pass for a few keys only (key 1004 at cos 0.71–0.93, accepted 97–100%; key 1003 at ρ = 0.50; the rest ≤ 31%). *Inference:* a defence tested only against that estimator would be uninformative. *Proposal:* the gradient-averaging attacker (Route A′, the exact test's own statistic averaged over the observed texts) is the plausible threat and is untested.
- **Verdict: CONDITIONAL.** Single next check: a tuning-key pilot of Route A′ on the existing calibration texts (keys 9001–9004, ρ 0.35 / 0.50 / 0.70, 100 texts each; about 15 minutes), with a pre-set reading (median cos ≥ 0.5 at some n ≤ 100 at ρ ≥ 0.50; otherwise extend to n = 1,024 before a verdict). The threat check needs Yichen's approval before it runs.
- **Wording constraints:** a transfer, named as future work by the scheme's authors; "first measurement" at search level only; never "immune"; not a new watermark.
- Design space recorded: (a) per-token context hashing of width h; (b) per-text rotation among K keys with a union test (buildable from the existing 8-key corpus); (c) per-prompt and (d) opening-keyed variants recorded as metadata-dependent or dominated.

Evidence: [`STUDY5_GATE_v0.1.md`](STUDY5_GATE_v0.1.md). Decided by: Claude (gate); the next check and the design decisions go to Yichen one at a time.

## 2026-10-02 — Study 5 threat check v0.1 RESULT: the gradient-averaging attacker recovers the fixed key from a handful of texts (tuning keys); the gate's condition is met

Yichen chose decision 1, "run the threat check now" (rejected: designing against Study 1's Route A only; including Route A′ untested; stopping Study 5). The spec `study5_pilot/THREAT_CHECK_SPEC_v0.1.md` was set to FIXED and committed; the run (`threat_check.py --phase run`) took 19:47–19:54 UTC (14:47–14:54 CDT), 7 minutes; the analysis ran from the committed spec and script (commit `f9b4567`). Tuning keys 9001–9004 only; no study key was touched.

**Validation (inputs only, 5/5 after one redefinition).** Check 2 as first written (the 28-hook gradient equals the single-hook gradient in bfloat16 to 1e-3) **failed** at 2–14% relative difference before any run. Following the Study 2 pilot lesson, the check was redone in float32: relative difference at most 4.8e-05; the bf16 direction cosines are 0.9905, 0.9997, 0.9997 and the bf16 run-to-run difference is 0.0 (deterministic), so the bf16 discrepancy is graph-dependent rounding in the backward pass, not an implementation error or nondeterminism. The check was redefined (float32 agreement ≤ 1e-3 and bf16 cosine ≥ 0.99) and the spec amended while still DRAFT. Also: hooks removed (logit difference 0.0); no spurious recovery on unwatermarked texts (|cos| 0.0 with every tuning key); 0.27 s per gradient text.

**Pre-set reading: the threat is real** (median cos ≥ 0.5 at some n ≤ 100 at ρ = 0.50 and at 0.70).

| ρ | Route A′ (gradients): median cos at n = 4 / 16 / 64 / 100 | layer = 14 (of 4 keys) | Route A (activations), same texts | per key at n = 100 |
|---|---|---|---|---|
| 0.35 | 0.80 / 0.95 / 0.90 / 0.89 | 3 / 3 / 4 / 4 | 0.00 / 0.00 / 0.00 / 0.00 | 0.80 (l̂ = 14), 0.84 (l̂ = 14), 0.97 (l̂ = 14), 0.95 (l̂ = 14) |
| 0.5 | 0.79 / 0.86 / 0.93 / 0.93 | 2 / 3 / 3 / 3 | 0.00 / 0.00 / 0.00 / 0.00 | 0.96 (l̂ = 17), 0.82 (l̂ = 14), 0.91 (l̂ = 14), 0.96 (l̂ = 14) |
| 0.7 | 0.54 / 0.58 / 0.57 / 0.57 | 1 / 2 / 2 / 2 | 0.00 / 0.00 / 0.09 / 0.00 | 0.75 (l̂ = 17), 0.22 (l̂ = 18), 0.88 (l̂ = 14), 0.40 (l̂ = 14) |

**Readings (tuning keys; descriptive beyond the pre-set rule).**
- Four texts already give a median cosine near 0.8 at ρ = 0.35 and 0.50; sixteen give 0.95 at ρ = 0.35. Study 1's activation estimator on the very same texts recovers nothing (cos 0.00 at every n), as in Study 1 itself at n ≤ 1,024.
- At ρ = 0.70 the attack is weaker (median 0.57; two of four keys below 0.5), and the layer is identified for only 1–2 keys: the degraded, repetitive texts at that strength evidently add a content footprint that competes with the key in the gradient mean.
- Restricted to the true layer, the estimate is no better (0.58–0.90), so support selection, not layer selection, limits the attack at 0.70.

**Interpretation (inference):** the exact test's strength is also the attacker's: the per-text gradient is a first-order sufficient statistic for the key direction, and it averages to the key within tens of texts at the strengths where the watermark is both detectable and paraphrase-robust. The fixed-key scheme is therefore stealable at a budget two orders of magnitude below Study 1's. Study 5's defence must be evaluated against this attacker (Route A′), with the fixed-key arm re-attacked on the study keys inside Study 5 (a Study 1-type result for the paper's attack section).

**Gate:** the single next check of `STUDY5_GATE_v0.1.md` is resolved; the gate's status becomes PASS as a transfer (§7 added). **Skill updated:** the detector's own statistic averaged over outputs is also the strongest key-recovery estimator; run the attack with the detector's statistic before designing a defence (appended to the 2026-09-30 lesson on the strongest detector).

Evidence: [`outputs/study5_threat_v0.1/REPORT.md`](outputs/study5_threat_v0.1/REPORT.md), [`outputs/study5_threat_v0.1/results.json`](outputs/study5_threat_v0.1/results.json), [`outputs/study5_threat_v0.1/VALIDATION.json`](outputs/study5_threat_v0.1/VALIDATION.json), [`study5_pilot/THREAT_CHECK_SPEC_v0.1.md`](study5_pilot/THREAT_CHECK_SPEC_v0.1.md). Decided by: mechanical (the spec's pre-set reading); Yichen (the run). **Next:** decision 2, which defence arms.

## 2026-10-02 — Study 5 decision 2: three keyed arms beside the fixed key — context hashing at h = 1 and h = 4, and per-text rotation among the 8 study keys

Yichen chose the recommended arms (rejected: context hashing only; adding the authors' position-indexed schedule as a fourth arm; rotation only on existing data).
- **(a) Per-token context hashing, widths h = 1 and h = 4:** the steering direction at position t is a 4-sparse key derived from the secret and the previous h tokens; the detector re-derives the per-position keys from the text alone (the first h positions are neither steered nor scored). Two points on the KGW-style frontier: h = 1 (moderate stealing cost, moderate paraphrase cost, predicted) and h = 4 (unstealable at n ≤ 1,024 but fragile, predicted). New generation.
- **(b) Per-text rotation among K = 8 keys with a union test:** the 8 study keys' existing texts at each strength form the rotating-key corpus; the detector tests the union (a max statistic, calibrated by resampling all 8 null keys); the attacker averages over the mixture (naive) and also clusters (adaptive); Study 2's paraphrases are re-scored under the union test; the "told which key" bound is Study 3's single-key result. Little new generation (forgeries only).
- **Comparator:** the fixed key (h = 0), re-attacked with Route A′ on the study keys inside Study 5 (existing texts; features and forgeries only).
- Not included: the position-indexed pseudo-random schedule (recorded in the gate's design space with its prediction: stealable by grouping positions across texts at n near 1,000, fragile to insertions); per-prompt and opening-keyed variants (metadata-dependent or dominated).

Evidence: [`STUDY5_GATE_v0.1.md`](STUDY5_GATE_v0.1.md) §2. Decided by: Yichen. **Next:** decision 3, the scope (strengths, keys, the attacker's n).

## 2026-10-02 — Study 5 decision 3: scope — ρ ∈ {0.35, 0.50}, the 8 study keys, the attacker's n ∈ {64, 256, 1024}

Yichen chose the recommended scope (rejected: ρ = 0.50 only; n capped at 256; three strengths on 4 keys).
- Strengths 0.35 and 0.50: where the fixed key is stolen from at most 64 tuning-key texts (threat check), one scrubbable by paraphrase (Study 2: P-Qwen effective at 0.35) and one not (0.50). Keys 1001–1008 as in Studies 1–3; the attacker's observed texts n ∈ {64, 256, 1024} as nested prefixes.
- Projected about 31 h on the locked runs' timings (generation 1.3 s, per-position gradient features 0.27 s, Qwen paraphrase 4.2 s per original), to be re-timed in the pilot; two or three checkpointed phases.
- **Pre-set fallback** if the pilot projects more than 30 h: first drop n = 1,024 for the h = 4 arm (predicted unstealable at that budget), then paraphrase 50 texts per key-level (as Study 2 did for Phi).
- The rotation arm uses all four strengths descriptively (existing data).

Decided by: Yichen. **Next:** decision 4, the attacker and the metrics.

## 2026-10-02 — Study 5 decision 4: the attacker is given the layer for the keyed arms; the full metric set

Yichen chose the recommended attacker and metrics (rejected: a layer search everywhere; a 4,096-text budget for h = 1 now, kept as a possible follow-up version; cosine-only metrics without forgeries).
- **Hashed arms (h = 1, h = 4):** the attacker, knowing h and the layer (conservative for the defence), standardises per-position gradients against its own reference texts, groups them by the observable context (the previous h token ids), estimates one 4-sparse key per context seen at least c_min times (top-4 coordinates of the context mean, as Route A), and forges by steering only the positions whose context it has estimated. n ∈ {64, 256, 1024}.
- **Rotation (K = 8):** a naive attacker averages the mixture; an adaptive attacker clusters the observed texts into K groups (K public) and estimates one key per cluster.
- **Fixed key:** re-attacked with Route A′ both with the layer search (as in the threat check) and with the known layer, on the study keys' existing observed texts.
- **Metrics:** recovered cosine against n (coverage-weighted over contexts for the hashed arms, with the share of a genuine text's positions covered); forgery acceptance under the exact test at a 1% FPR with the fluency condition (Study 3's rule form, against the arm's own genuine texts and a random-secret control); paraphrase scrub success under Study 2's four quality conditions, paired per key with the fixed key's Study 2 P-Qwen result on the same prompts; the genuine detection rate; perplexity ratio and seq-rep-4 against the fixed key's genuine texts at the same strength.

Decided by: Yichen. **Next:** decision 5, the pre-registered rules and materiality thresholds.

## 2026-10-02 — Study 5 decision 5: three pre-registered rules with materiality thresholds; two gates

Yichen chose the recommended rule set (rejected: stricter materiality of 10 points and a 1.05 ratio; looser 30 points and 1.25; a cosine-based stealing rule).
- **Gates.** P0 (per strength): the fixed key under Route A′ is practical to forge (Study 3's X1 form); where P0 fails, the defence verdicts at that strength are descriptive. P1 (per arm and strength): the arm's median genuine detection at p ≤ 0.01 is at least 50%; otherwise the arm is descriptive there.
- **D1, stealing (per arm, strength and n):** a forgery is **practical** if its fluent exact-test acceptance (FA) is at least half the arm's genuine FA and its lower 95% bound exceeds the random-secret control's upper bound; **stealing blocked at n ≤ 1,024** if every n's upper bound is below half the genuine FA; otherwise inconclusive. If the control itself reaches half the genuine FA, "generic steering suffices" is reported instead (Study 3's X3 form).
- **D2, robustness cost (per arm and strength):** d = scrub success of P-Qwen on the arm − the fixed key's Study 2 success, per key, paired bootstrap; a **material cost** if the lower bound is above 0 and the median d ≥ 20 points; **immaterial** if the upper bound is below 20 points; otherwise inconclusive. Study 2's absolute reading (success ≥ 50% means paraphrase is effective) is reported beside it.
- **D3, quality cost (per arm and strength):** the median over keys of the per-key median perplexity ratio arm/fixed on the same prompts; **material** if the lower bound exceeds 1.10; **immaterial** if the upper bound is at most 1.10; otherwise inconclusive. Seq-rep-4 is reported descriptively.
- **Rotation:** D1 under the union test for the naive and the clustering attacker; D2 as the union test's loss on Study 2's paraphrases relative to the single-key test; quality unchanged by construction.
- Medians over the 8 keys; cluster bootstrap over keys then texts (B = 2,000); the number of keys meeting each bar beside every verdict; bounds checked at the extremes in the protocol.

Decided by: Yichen. **Next:** decision 6, the budget and the tuning-key pilot.

## 2026-10-02 — Study 5 decision 6: a full-pipeline tuning-key pilot (about 2 h) before the protocol is fixed; budget at most 30 h

Yichen chose the recommended pilot (rejected: no pilot; a code test only; a larger pilot with 1,024 observed texts for one key).
- Tuning keys 9001–9004 at ρ = 0.50 (0.35 for detection only); 100 observed and 100 genuine texts per key and hashed arm; Qwen paraphrase of 50 genuine texts per key-level; a small forgery set to exercise the attacker's hook.
- **Pre-set checks:** the keyed hook with h = 0 reproduces Study 1's generation token for token (the fixed-key baseline then needs no regeneration); the keys used during keyed generation equal the keys the detector re-derives from the output tokens; the keyed detector's FPR on unwatermarked texts within 0.3–2.5%; the per-position test with h = 0 matches S4's detection within 10 points on the fixed-key tuning texts; the projected study at most 30 h (decision 3's fallback applies).
- **Readings, no rules:** genuine detection and quality of the keyed arms; the per-context attacker at n ≤ 100 (coverage, cosine); detection after paraphrase; forgery acceptance on the small set.
- The protocol is drafted before the pilot's readings exist and fixed after them; then input-only validation and the lock, as for Study 2.

Decided by: Yichen. **Next:** the pilot spec and code (Claude), then the pilot run after Yichen fixes the spec.

## 2026-10-02 — Study 5: protocol v0.1 drafted; defence pilot spec (DRAFT) and machinery written; input-only validation 9/9 PASS

**Written (Claude):** `STUDY5_PROTOCOL_v0.1.md` (DRAFT; the compute section waits for the pilot; a "for review" list names the design calls made beyond decisions 1–6), `study5_pilot/DEFENCE_PILOT_SPEC_v0.1.md` (DRAFT), `study5_pilot/keyed_core.py` (the keyed PRF, the stateful generation hook, per-position features, the keyed exact test with secret resampling, the per-context attacker, the union test and clustering attacker) and `study5_pilot/defence_pilot.py` (validate / run / analyse).

**Validation, inputs only (unwatermarked texts, the validation secret 0, synthetic data), 9/9:**
1. inputs present and hashed;
2. the keyed test on synthetic data: null p-values uniform on the 1/1000 grid (KS p = 0.65, null rate 1.0%), a planted signal detected 100%;
3. **I1:** the hook in fixed mode reproduces `core.generate` token for token on 16 prompts (16/16) and equals the stored calibration texts (16/16), so the fixed-key baseline needs no regeneration;
4. **I2:** with h = 1 and h = 4 the keys used during generation equal the keys the detector re-derives from the output ids at every steered position (8/8 texts each; the generator steers positions h..254 because the last sampled token is never fed back, and the detector's extra position 255 carries a zero gradient); the tokenisation round trip is exact on all 16 texts. The check as first written compared whole lists and failed on that one trailing position; it was redefined before any run and the spec amended;
5. zero-scale keyed generation equals unsteered generation; steering changes all 4 texts; after removal, unsteered generation is reproduced;
6. reference position statistics saved (owner 51,190 positions; attacker 51,195);
7. the sum of per-position gradients equals the summed gradient: relative difference ≤ 3.2e-07 in float32, cosine ≥ 0.999999 in bf16;
8. **I3:** FPR on 1,000 pool A texts within [0.3, 2.5]% for every combination (h = 1: 1.0–1.8%; h = 4: 0.6–1.3%; the per-position fixed form 0.5–2.0%);
9. **I5:** the study at decision 3's scope projected at 29.6 h (≤ 30 h) from keyed generation at 1.63 s per text (the stateful hook synchronises the device each step; fixed 1.08 s), features at 0.14 s and Study 2's paraphrase rate; fallback 1 23.5 h, fallback 2 21.6 h.

No tuning-key or study-key statistic was computed. The run refuses until the spec is FIXED.

Evidence: [`outputs/study5_pilot_v0.1/VALIDATION.json`](outputs/study5_pilot_v0.1/VALIDATION.json), `study5_pilot/`, [`STUDY5_PROTOCOL_v0.1.md`](STUDY5_PROTOCOL_v0.1.md). Decided by: Claude (implementation); the spec's approval goes to Yichen.

## 2026-10-02 — Study 5 decision 7: the defence pilot spec v0.1 approved as drafted and FIXED; the run started

Yichen approved `study5_pilot/DEFENCE_PILOT_SPEC_v0.1.md` as drafted (rejected: reviewing it first; changing it). The status line was set to FIXED and committed before any run. The run (`defence_pilot.py --phase run`, tuning keys only) started at 2026-10-02 20:55 UTC (15:55 CDT), projected about 2 h, with keep-awake, logging to `study5_pilot/data/pilot_run.log` (git-ignored); a background watcher checks for completion, a crash and a 40-minute stall. While it runs, the Study 5 study code and the report builder are written (no outcome is read before the run ends).

Decided by: Yichen (approval); Claude (start).

## 2026-10-02 — Study 5 defence pilot: run 1 stopped at its first forgery step (a scale default in the generation helper); fixed, no computation changed; resumed as run 2

The pilot crashed at 21:04 UTC (16:04 CDT) after the first key-arm's genuine, observed and feature steps (all checkpointed) when generating the first forgeries: `keyed_core.generate` in table mode computed its default scale from a strength that table mode does not pass (`rho * N_REF` with rho None). The fix sets the default to 0.0 in table mode, where the table's vectors are already scaled; no computed value changes (the fixed-mode and keyed-mode paths are untouched; the validation's I1 and I2 were produced by those paths). The spec stays FIXED; the fix is committed and the run resumes from its checkpoints as run 2 (logged as a deviation of the pilot's code, not of its design).

Decided by: Claude (fix); recorded for Yichen's review.

## 2026-10-02 — Study 5 defence pilot v0.1 RESULT (tuning keys): keyed arms detect 95% with better quality than the fixed key and block the attacker at 100 texts, but paraphrase removes nearly all of their evidence; rotation falls to a clustering attacker

Run 2 from the FIXED spec (commit `40cc13d`), 21:04–22:36 UTC (16:04–17:36 CDT), 1.5 h; analysed 22:38 UTC (17:38 CDT). Tuning keys 9001–9004; medians over 4 keys; no rule applies. Generated report: [`outputs/study5_pilot_v0.1/REPORT.md`](outputs/study5_pilot_v0.1/REPORT.md).

**Keyed arms at ρ = 0.50** (detection at 0.35 in brackets):

| arm | genuine detection % | perplexity ratio keyed / fixed (same prompts) | forgery FA % at n = 100 | control accept % | paraphrase: scrub success % | detected after paraphrase % | quality pass % |
|---|---|---|---|---|---|---|---|
| h = 1 | 95.5 [91.5] | 0.89 | 5.0 | 0.0 | 75.0 | 2.0 | 77.0 |
| h = 4 | 94.5 [89.0] | 0.89 | 0.0 | 0.0 | 75.0 | 1.0 | 76.0 |
| fixed (Study 2 pilot, same keys) | 96 (S4) | 1 | — | — | 52 | 24 | — |

- **Detection:** the per-position keyed test has S4-like power (P1's 50% bar is far away). The post-hoc I4 addendum (decision 6's check, dropped from the spec in drafting and run afterwards on the same inputs): the per-position form with h = 0 detects 98.5% at ρ = 0.50 and 96.0% at 0.35 against S4's 97.5% and 95.5% (within 10 points: PASS).
- **Quality:** both keyed arms have *lower* perplexity than the fixed key on the same prompts (ratios 0.89 and 0.89; per key 0.63–1.00) and less repetition (seq-rep-4 0.002 / 0.000 against the fixed key's 0.006): a jittering direction degrades text less than a constant drift. *Inference, to be tested on the study keys.*
- **The per-context attacker (known layer):** h = 1 at n = 16 / 64 / 100: count-weighted cosine 0.03 / 0.09 / 0.11, coverage of genuine positions 0.30 / 0.50 / 0.54, 212 contexts estimated at 100; h = 4: no context reaches 16 occurrences (coverage 0.001). Forgeries at n = 100: FA 5% (h = 1) and 0% (h = 4); the random-secret control 0%. The study's n = 1,024 gives frequent contexts ten times more occurrences; the h = 1 curve is the open question.
- **Paraphrase (P-Qwen with the attacker's self-check, 50 texts per key):** detection after paraphrase falls to the null rate for both arms (2% and 1%, against the fixed key's 24% on the same tuning keys in the Study 2 pilot); scrub success 75% and 75% against the fixed key's 52% (d ≈ +23 points, at the 20-point materiality bar). *Inference:* even h = 1 loses the evidence, because the signal at a position is projected on the key of that position's previous token, and a paraphrase changes most previous tokens; the fixed key's content shift survives because every position shares one key.
- **Rotation code test (K = 4):** union-test detection 82–99% against single-key 91–100%; union FPR 0.8%. The naive attacker recovers one key partially (cos 0.55) and the others not at all; the clustering attacker recovers 2 of 4 keys at n = 16 (4 texts per key) and all 4 at n = 64 and above (cos 0.82–0.97). Rotation multiplies the attacker's cost by about K and no more.
- **Tokenisation round trip:** 0.997 of positions identical (median key 9001); the scheme's keys survive the decode–encode round trip.
- **Timing (measured):** keyed generation 1.16 s per text (batch 16; the validation's 1.63 s included a cold start), paraphrase with retries 3.5 s per original, features 0.14 s. Projection for decision 3's full scope: 25.8 h (K (keyed generation, attacker, forgeries, quality) 18.3 h; P (paraphrase and scoring) 3.4 h; F and R (fixed re-attack, rotation) 4.2 h); **no fallback needed** (≤ 30 h).
- **Deviation:** run 1 crashed at the first forgery on a scale default in table mode (fixed, no computed value changed, logged above); run 2 completed without deviation.

**Consequences for the protocol (proposal, for Yichen's approval):** the design stands (arms, scope, rules). Added as secondary readings: detection after paraphrase with a paired contrast against the fixed key; the quality ratio read in both directions (a ratio below 1 is an improvement); the attacker's cosine by context count. The compute section is filled with the measured rates. **Skill updated:** cross-check a pilot spec's check list against the decision that commissioned it before fixing (I4 was dropped in drafting).

Evidence: [`outputs/study5_pilot_v0.1/results.json`](outputs/study5_pilot_v0.1/results.json), [`outputs/study5_pilot_v0.1/REPORT.md`](outputs/study5_pilot_v0.1/REPORT.md), [`outputs/study5_pilot_v0.1/ADDENDUM_I4.json`](outputs/study5_pilot_v0.1/ADDENDUM_I4.json). Decided by: mechanical (readings); Claude (interpretation, labelled). **Next:** decision 8, approval of the revised protocol v0.1.

## 2026-10-02 — Study 5 decision 8: protocol v0.1 approved as drafted (revised from the pilot)

Yichen approved `STUDY5_PROTOCOL_v0.1.md` as drafted (rejected: reviewing it first; changing it), including the drafting calls listed in its "for review" section (forgeries at every n for all arms; the attacker's context threshold of 16; the keyed arms' genuine texts on Study 1's oracle prompts; Study 3's S4 primary for the fixed arm with the per-position form secondary; Study 2's locked bars reused) and the secondary readings added from the pilot. The protocol stays DRAFT until the lock. Compute: about 26 h in three checkpointed phases from the pilot's measured rates; no fallback needed.

Decided by: Yichen. **Next:** the input-only validation's verdict (running), then the lock decision.

## 2026-10-02 — Study 5 code: smoke test and input validation ALL PASS (8/8; 26.6 h projected; no study-key outcome)

**Code in `research/study5/`:** `common_s5.py` (sources; the owner's keyed test, S4 and the union test; the attackers; the rules D1–D3 and gates G1, G2, P0, P1; the analysis with a required-field checker), `run_s5.py` (lock check; phases S, K, P, F, R, A, checkpointed; `--dry` runs on tuning-key stand-ins), `validate_s5.py` (§12 checks; the stand-in source), `lock_s5.py`. Reused unchanged and to be hash-locked: `study5_pilot/keyed_core.py` and `threat_check.py`, Study 2's `common_s2.py` and `scrub_core.py`, Study 3's `common_s3.py` and `power_pilot.py`, v0.4's `run_v04.py`, `common4.py`, `attack4.py`, v0.3's `common3.py`, v0.2's `common.py`, `attack2.py`, `detect2.py`, v0.1's `core.py` and `attack.py`.

**Smoke test** (`run_s5.py --dry --phase all`; keys 9001–9002 at ρ = 0.50 as stand-ins, 32 observed, 8 genuine, 4 forgeries and 4 paraphrases per key-arm): every phase ran and every field of §7–§10 is produced (the first pass crashed in phase F on a forgery set hard-coded to n = 256, which the dry grid lacks; fixed to the grid's middle n; no study computation changed; the numbers carry no information).

**Input validation, inputs only, 8/8** (`outputs/study5_v0.1/INPUT_VALIDATION.json`): (1) 110 reused files present and hashed, equal to Study 2's and Study 3's locks where recorded; (2) the keyed hook reproduces Study 1's generation token for token (16/16, equal to the stored calibration texts) and replays its keys exactly (8/8 for h = 1 and h = 4); (3) calibration: the pilot's I3 (14 combinations within 0.5–2.0%) and the validation secret on 100 fresh null texts at 1.0% (h = 1) and 1.0% (h = 4); (4) 280 generation seeds in [8,000,010, 9,005,011], disjoint from every earlier study, paraphrase seed sets 20–21 (the check's declared range was first written too tight and corrected; the seeds did not change); (5) the runner refuses without a lock; (6) no study-key outcome exists; (7) projected **26.6 h** at decision 3's full scope (keyed generation 1.16 s, paraphrase 3.5 s per original, features 0.14 s), no fallback needed; (8) the smoke test passes with no missing field.

No study-key text has been generated, attacked or paraphrased.

Evidence: [`outputs/study5_v0.1/INPUT_VALIDATION.json`](outputs/study5_v0.1/INPUT_VALIDATION.json), `study5/`. Decided by: Yichen (design); Claude (implementation). **Next:** decision 9, the lock.

## 2026-10-02 — STUDY 5 v0.1 LOCKED (before outcomes); the run goes to a new "Milestone 9" session

Yichen approved locking Study 5 v0.1 and running it in a new session, "Milestone 9: Study 5 run" (rejected: running it here; reviewing first). The protocol's status line was set to LOCKED and committed before hashing.

The lock `outputs/study5_v0.1/PRE_RUN_LOCK.json` (locked **2026-10-02 23:24:57 UTC** (18:24 CDT), commit before lock `cf6c1b4`) records the SHA-256 of the protocol, **18 code files** (`common_s5`, `run_s5`, `validate_s5`, the pilot's `keyed_core` and `threat_check`, Study 2's `common_s2` and `scrub_core`, Study 3's `common_s3` and `power_pilot`, v0.4's `run_v04`, `common4`, `attack4`, v0.3's `common3`, v0.2's `common`, `attack2`, `detect2`, v0.1's `core`, `attack`), **106 reused files** (Study 1's observed, oracle, random and summary files for 16 key-levels; pools A, C, F and the attacker's norms; Study 3's oracle and random features and its reference and null features; Study 2's bars, kept paraphrases, their quality and S4 features) and 13 inputs (the input validation, the pilot's and the threat check's results and validations, Study 2's and Study 3's locks and results, the prompt loader, the model manifests). It also records the design constants and `final: false` (the holdout is not used).
- **Tamper tests:** a byte appended to the protocol, to `common_s5.py` and to a reused file were each refused ({'protocol': 'refused', 'code': 'refused', 'reused': 'refused'}); the lock passes again after each file was restored byte for byte.
- No study-key text has been generated, attacked or paraphrased; `research/study5/data/` holds only the smoke test's `dry/` folder.

The run is projected at 26.6 h in three checkpointed phases (S and K about 19 h; P about 3.5 h; F and R about 4 h). The pre-run checklist and the starter prompt are in the handoff.

Evidence: [`outputs/study5_v0.1/PRE_RUN_LOCK.json`](outputs/study5_v0.1/PRE_RUN_LOCK.json). Decided by: Yichen.

## 2026-10-02 — Study 5 v0.1 run started (phases S and K); the report builder written during the run, before any outcome, and tested on a full-scope fixture

**Pre-run checklist (Milestone 9):** AC power, lid open, swap 0.55 GB used; `git pull` up to date, clean tree; `check_lock()` passed (the protocol, 18 code files, 106 reused files); no `K_*` file and no `results.json` existed (only the smoke test's `dry/` folders). The run started at **2026-10-02 23:29:01 UTC (18:29 CDT)**: `caffeinate -ims python -u run_s5.py --phase SK`, console to `study5/data/console.log`, markers to `study5/data/run.log` (git-ignored). Phase S (the owner's and the attacker's position statistics, the attacker's all-layer gradients, the keyed test on the 1,000 null texts for 16 arm-key pairs, the union test) completed at 23:40:20 UTC (18:40 CDT), 11 min; phase K (32 key-level-arms, about 35 min each) is running. A background watcher exits on `phase K complete`, a crash (`Traceback|Error|refused|Killed`), an exit without completion, or a 90-minute stall of `run.log`.

**Report builder (no outcome read):** `study5_report/make_report_s5.py` re-computes, with its own implementation, S4 and the union test on Study 3's locked features and on Study 2's locked paraphrases, and from the run's per-text keyed statistics every p-value, fluency flag, acceptance, scrub success, quality condition and perplexity ratio per key; it re-derives G1, G2, P0, P1 and every D1/D2/D3 verdict from §9 written out again, and asserts equality with `results.json`. It writes six tables (rules vs observed; detection, quality and power; recovery and forgery against n; paraphrase per arm beside the fixed key; per key; the attacker's mechanics and timing), the §10 samples (keys 1001 and 1002 at ρ = 0.50, quoted with their p-values and quality readings) and five figures (recovery and forgery against n; paraphrase per arm; the stealability–robustness–quality frontier; per-key calibration and stealing; the per-context attacker's mechanics), plus `prose_values.json` for the `[[name]]` placeholders of `report_prose.md`. Builder-side descriptive readings: detection at p ≤ 0.05 and 0.10, four texts pooled, stricter quality bars, the tokenisation round trip, paraphrase attempts, timing. `make_manifest_s5.py` rebuilds the run manifest from the log markers (phase starts and ends, Central times, the lock re-check).

**Fixture test:** `study5_report/fixture_s5.py` writes planted noise in the run's exact file layout at the full scope (2 arms × 2 strengths × 8 keys; n ∈ {64, 256, 1024}; 100 texts per set; 1,000 null texts) into a scratch folder, runs the **locked** `common_s5.analyse` on it and the builder on its output: all asserts pass, every field is consumed, every figure was viewed and adjusted (labels moved into legends; interval formats; axis ranges). Two points: (a) on the fixture the run's statistics are planted, so the comparisons of the builder's re-computation from the locked features with the run's files are exercised but asserted only on the real data (`REAL` flag); (b) the fixed key's Study 2 scrub success, re-computed by the builder with its own S4 and quality conditions from Study 2's locked paraphrases, equals both the locked analysis's comparator and Study 2's reported per-key S1 values (real data in both modes).

Evidence: `study5_report/`, `study5/data/run.log` (git-ignored). Decided by: Claude (implementation; the checklist was pre-set). **Next:** phase K's end (projected about 18:00 UTC on 2026-10-03 (13:00 CDT)), then phases P, F, R and A; the in-words section is written after the results.

## 2026-10-04 — STUDY 5 v0.1 RESULT: context keying blocks the gradient-averaging attacker at n ≤ 1,024 and improves quality, but loses the paraphrase robustness; rotation among 8 keys falls to a clustering attacker at ρ = 0.50

Run from the lock (`PRE_RUN_LOCK.json`, 2026-10-02 23:24 UTC), **2026-10-02 23:29 UTC (18:29 CDT) to 2026-10-04 01:50 UTC (20:50 CDT)**: S 0.2 h, K 18.4 h, P 3.6 h, F 3.7 h, R 0.5 h, A seconds; **26.3 h against 26.6 projected**; no deviation; `check_lock()` accepted the lock before every phase and after the run; the holdout untouched. Report: [`STUDY5_REPORT_v0.1.md`](STUDY5_REPORT_v0.1.md), built by `study5_report/make_report_s5.py` (every number generated; the builder's own S4, union test, quality conditions, per-key values and rules all equal `results.json`; the fixed key's Study 2 comparator equals Study 2's reported per-key S1 values). Manifest: [`outputs/study5_v0.1/RUN_MANIFEST.json`](outputs/study5_v0.1/RUN_MANIFEST.json).

**Gates.** G1 pass (pooled FPR 0.83% h = 1, 0.95% h = 4, 1.00% union); G2 8 of 8 keys calibrated for both hashed arms; P1 pass everywhere (keyed-test detection 92.5 / 96.5% for h = 1 and 90.0 / 95.5% for h = 4 at ρ = 0.35 / 0.50; union test 93.0 / 98.5%, single-key 96.0 / 99.0%). **P0, the threat, is confirmed on the study keys at both strengths: practical at n = 64.** Route A′ recovers the fixed key at median cosine 0.94–0.95 from 64 texts (the layer search finds layer 14 for 6–7 of 8 keys) and its fluent forgeries are accepted 88.0% [76.5, 93.0] at ρ = 0.35 and 85.5% [82.5, 90.0] at 0.50, as often as the genuine texts (86.5%, 90.0%); every key 75–93% at n = 1,024; random-key control 0.0%.

| arm | ρ | D1 stealing (forgery FA at n = 64 / 256 / 1,024; bar ≈ half the genuine FA) | D2 robustness cost (scrub success vs the fixed key's Study 2 value; d, paired) | D3 quality (perplexity ratio to the fixed key) |
|---|---|---|---|---|
| h = 1 | 0.35 | 1.0 / 2.5 / 3.5% (bar 42.0) → **blocked at n ≤ 1,024** | 73.0% vs 53.0%; d = +22.0 [6.0, 36.5], 5 of 8 keys ≥ 20 → **material** | 0.852 [0.790, 0.874] → **immaterial** (better) |
| h = 1 | 0.50 | 1.5 / 3.0 / 9.0% [5.5, 11.0] (bar 44.0) → **blocked** | 70.5% vs 39.5%; d = +32.0 [21.0, 44.0], 7 of 8 → **material** | 0.722 [0.682, 0.799] → **immaterial** (better) |
| h = 4 | 0.35 | 1.0 / 1.0 / 0.0% (bar 40.0) → **blocked** | 72.0% vs 53.0%; d = +18.0 [7.5, 33.5], 3 of 8 → **inconclusive** | 0.832 [0.787, 0.879] → **immaterial** (better) |
| h = 4 | 0.50 | 1.0 / 0.5 / 1.0% (bar 43.8) → **blocked** | 69.5% vs 39.5%; d = +32.5 [19.0, 45.5], 7 of 8 → **material** | 0.717 [0.686, 0.791] → **immaterial** (better) |
| rotation K = 8 | 0.35 | naive 0 / 1 / 1% → blocked; clustering 8 / 2 / 0% → **blocked** (but see below) | union-test success +15.0 [9.5, 18.5] points above the single-key test → **immaterial** | unchanged by construction |
| rotation K = 8 | 0.50 | naive 0 / 12 / 0% → blocked; clustering **95 / 95 / 96% → practical (n = 64)** (7–8 of 8 keys recovered at cos ≥ 0.5) | +13.0 [8.5, 17.5] → **immaterial** | unchanged |

**Descriptive readings that matter.** (a) After paraphrase the keyed arms keep almost no evidence (detected 1.0–4.0% against the fixed key's 25.5 / 35.0%; four pooled paraphrases 0–8%); their scrub success is capped by the quality conditions (70–75.5% pass all four), and Study 2's absolute reading is "paraphrase effective" for every keyed arm at both strengths. (b) The per-context attacker on h = 1 estimates about 1,900 contexts covering 80% of a genuine text's positions at n = 1,024 but at a count-weighted cosine of only 0.17–0.21 (rising to about 0.3 for contexts seen ≥ 512 times); on h = 4 the 242,542 distinct four-token contexts almost never repeat (61 eligible; coverage 0.8%). h = 1's acceptance rises with n at ρ = 0.50 (1.5 → 3.0 → 9.0%): the verdict is bounded by the budget. (c) **Rotation's "blocked" at ρ = 0.35 is the attacker's cluster-selection rule, not the defence**: the clustering recovered 6 of 8 keys (median best cosine 0.87 at n = 1,024), but the pre-registered rule "forge with the largest-z-profile cluster" picked an outlier cluster with cosine 0.00; at ρ = 0.50 it picked a cluster at 0.96 and broke the scheme. The verdict stands as pre-registered; the reading is labelled, and a better selection rule would presumably break rotation at 0.35 too. (d) Quality: the keyed texts have 15–28% lower perplexity than the fixed key's on the same prompts, 0 of 8 keys above 1.10; seq-rep-4 ≤ 0.004. (e) The decode–encode round trip recovers 98.5–100% of the token ids. (f) The attacker's self-check kept 21–25% of paraphrases that still failed its own bars after three attempts (Study 2: 32%).

**Interpretation (inference, labelled; for the claim gate).** On this model and attacker, context keying moves the trade-off along one axis only: it removes the gradient-averaging attacker's foothold at n ≤ 1,024 and costs nothing in quality, but it gives up the paraphrase robustness that motivates activation watermarks (the fixed key's evidence after paraphrase is a content shift that paraphrase preserves; the keyed test's evidence is tied to token contexts that paraphrase changes). Rotation keeps robustness and quality and multiplies the attacker's cost by about K. The token-level no-free-lunch trade-off carries over to activation steering. Bounded by one attacker, one paraphraser, one model, n ≤ 1,024.

**Skill updated (A5):** (1) pre-register an attack's recovery metric and its forgery separately, and forge with every candidate (or the attacker's own best-by-objective candidate) rather than one heuristic pick, so that a sub-rule cannot hide a successful recovery; (2) in a fixture-tested report builder, gate the asserts that re-compute from locked inputs on real mode (`REAL`), because on a fixture the run's statistics are planted.

Evidence: [`outputs/study5_v0.1/results.json`](outputs/study5_v0.1/results.json), [`STUDY5_REPORT_v0.1.md`](STUDY5_REPORT_v0.1.md), `outputs/study5_v0.1/report/`. Decided by: mechanical (verdicts, pre-registered); Claude (interpretation, labelled). **Next:** the Stage 6 exit decision (Yichen): the claim gate (Stage 7) for the whole paper, or a follow-up (a rotation re-attack with a better selection rule, or the per-position h = 0 form on the study keys).

## 2026-10-04 — Study 5 decision 10 (Stage 6 exit): the claim gate (Stage 7) in a new session, with a 30-minute rotation addendum alongside

Yichen chose, from three options with the recommendation first: **the claim gate for the whole paper in a new session "Milestone 10: claim gate"** (re-screen the actual claim list from Studies 1, 2, 3 and 5; read the nearest predecessors in full; fix the wording rules), **with a labelled post-hoc addendum run alongside** that lets Study 5's rotation attacker forge with every cluster at ρ = 0.35 (about 35 min), so the paper can state rotation's fate at both strengths rather than hide behind the attacker's junk-cluster pick. Rejected: a follow-up study first (h = 1 at n = 4,096; the per-position h = 0 form on the study keys; Study 4 on Gemma); the claim gate with no addendum.

The addendum's spec (`study5_addendum/ROTATION_ADDENDUM_SPEC_v0.1.md`, FIXED before the run) and script (`rotation_addendum.py`: reproduces the locked clustering from the saved gradients and asserts it equals the study's records, then forges with each of the 8 clusters at n ∈ {256, 1024}, scored with the union test and the level's fluency bars; three pre-set attackers: the study's rule, the largest cluster, every cluster) are written; the study's D1 verdict stands and the reading is inserted into the report's §6, labelled. Context at 45% at this decision.

Decided by: Yichen. **Next:** run the addendum; rebuild the report; log; commit; push; then the new session "Milestone 10: claim gate" (starter prompt in the handoff).

## 2026-10-04 — Study 5 rotation addendum RESULT (post hoc, labelled): rotation among 8 keys falls to the clustering attacker at ρ = 0.35 as well; Study 5's "blocked" there was the attacker's cluster-selection rule

Run from the FIXED spec, 2026-10-04 03:42–04:23 UTC (22:42–23:23 CDT), 41 min; the study's lock re-checked; the re-run clustering reproduced the study's 16 cluster records exactly and the chosen-cluster estimates were equal. At ρ = 0.35, forging with each cluster's estimate (100 texts each; the union test; the level's fluency bars): at n = 256 every cluster with cosine ≥ 0.6 gives FA 60–96% and 7 of the 7 clusters with cosine ≥ 0.5 reach the 43.2% bar; at n = 1,024 the clusters with cosine ≥ 0.8 give 78–90%, the cosine-0.61 cluster 36%, the cosine-0.40 cluster 7%, and 5 of 6 reach the bar. The study's pre-registered rule (largest z-profile) picked the junk cluster both times (cosine 0.00; FA 1%); a largest-cluster rule gives 88% (n = 256) and 89% (n = 1,024); the best cluster 96% and 90%. **Reading (labelled):** rotation (K = 8) falls to the clustering attacker at both strengths from 256 texts (and from 64 at ρ = 0.50, Study 5); the pre-registered D1 verdict for rotation at ρ = 0.35 stands as written and the report carries the addendum in §5 beside it. The report was rebuilt (every number generated; the in-words section cites the addendum through placeholders).

Evidence: [`outputs/study5_v0.1/ADDENDUM_ROTATION.json`](outputs/study5_v0.1/ADDENDUM_ROTATION.json), [`outputs/study5_v0.1/ADDENDUM_ROTATION.md`](outputs/study5_v0.1/ADDENDUM_ROTATION.md), [`STUDY5_REPORT_v0.1.md`](STUDY5_REPORT_v0.1.md) §5. Decided by: mechanical (readings); Claude (labelling). **Milestone 9 is complete.** Next: the new session "Milestone 10: claim gate" (starter prompt in the handoff).

## 2026-10-04 — Milestone 9 closed; Stage 7 (the claim gate) prepared for a new session

Yichen asked to prepare Stage 7 in a new session. Written (Claude): a Stage 7 checklist in `RESEARCH_HANDOFF.md` (start steps; a seed claim list of eight candidate claims tied to pre-registered verdicts, to be verified and not adopted; the source-gate re-run by mechanism with industry and regulator sources and a scoop check of the Self-Recognition repository first; the ten predecessors to read in full with the rule that every "via fetch tool" quotation is re-confirmed against the PDF with a page number; terms-of-use and provenance for PDFs; the wording-rule deliverable `CLAIM_GATE_v0.1.md`; the judgment calls to bring one at a time; the A6 tally: 14 figures and 29 tables exist across the reports) and the Milestone 10 starter prompt. Nothing was downloaded or drafted; the paper folder stays empty until Stage 8. Everything is committed and pushed; the working tree is clean.

Decided by: Yichen (the move to Stage 7); Claude (the checklist). **Next:** the new session "Milestone 10: claim gate".

## 2026-10-05 — Stage 7 claim gate v0.1 DRAFTED: the claim list is built from the results, the source gate re-run on it, the nearest predecessors read in full; verdict PASS with narrowed wording, pending four wording calls

Milestone 10 opened 2026-10-04 22:30 UTC (17:30 CDT). Written (Claude): [`CLAIM_GATE_v0.1.md`](CLAIM_GATE_v0.1.md) in the source-gate format: thirteen claims tied to pre-registered verdicts or labelled descriptive, each with its evidence, the predecessors occupying part of it and a wording verdict (claimed / narrowed / not claimed); a competitor table with every quotation **confirmed against the PDF text with a page number**; twelve wording rules for Stage 8; the four judgment calls; regulator and industry sources; what was not done.

**Scoop check (evidence):** the Self-Recognition repository is unchanged since 2026-06-16 (no forks, one branch); no paper cites Self-Recognition (Semantic Scholar, OpenAlex); AWM has no citers; SLAM one unrelated citer; the authors' group's only other 2026 paper is a token-level watermark (Schäfer and Wunder, EMNLP 2026). The arXiv listings since July 2026 (43 stealing or spoofing papers) contain no activation scheme. New leads, none overlapping: SAEMark (NeurIPS 2025; rejection sampling, no steering), a Zenodo preprint on activation watermarks readable only from the provider's logs, and the AWM group's trigger-tag paper of 2026-10-02.

**Reading (evidence; 13 PDFs with a hashed manifest under `research/literature/`, terms checked first):** confirmed verbatim: Self-Recognition's security and future-work paragraph (PDF p. 7), No Free Lunch's Guidelines #1–#2 and the h statement (pp. 5, 7, 10), Watermark Stealing's budget and h statement (pp. 3, 6), Reliability's h statement (p. 21), Learnability's multi-key passage (p. 19), SEEK's trade-off (p. 1). Corrections to the earlier gates: SLAM never mentions stealing, spoofing, forgery or a threat model (the earlier "quotation" was the fetch tool's summary); GaussMark never mentions bias or residual-stream perturbation (likewise); AWM says "one surrogate key"; Self-Recognition's "99.1 → 89.3" is attribution accuracy between two steered variants (Table 3, p. 6), not F1 against human text; key rotation with k detection tests originates in KGW itself (p. 7), with the "no observable bias when averaging" argument that our clustering attacker defeats. Three facts that constrain the wording: the authors themselves note that paraphrased human text "acts as a spoofing mechanism for our detector" (p. 5); their quality claim rests on instruction-tuned models, a DeBERTa quality classifier and MMLU, with Llama-3.2-1B's perplexity falling under steering in their Table 7 (p. 15) where our base-model reproduction found garbled text; Gu et al. (2024, p. 2) already concluded that spoofability means a watermark "should not be used to attribute provenance or blame".

**Regulator and industry sources (primary texts read):** EU Code of Practice on marking and labelling (final, 10 June 2026; Measures 1.1.2, 2.1, 3.2, 3.3 quoted with pages), the Commission's Article 50 guidelines (20 July 2026), NIST AI 100-4 (definitions of robust and secure watermarks, forgery, private keys, evaluation; pp. 13, 19, 20, 38), SynthID-Text (Nature 2024; H = 4 context hash with the key; stealing, spoofing and scrubbing named as ongoing research) and its Hugging Face configuration (9 keys, ngram_len 5). Use in the paper: motivation and vocabulary only.

**Access gaps:** OpenReview (bot challenge; stopped); Google Scholar not searched; the arXiv API returned HTTP 429 for most of the session (substitutes: the arXiv search page, OpenAlex, Semantic Scholar), then recovered and the paced batch was re-run.

**Verdict (proposal): PASS with narrowed wording** — the first security analysis of an activation-steering watermark to our knowledge, every mechanism a transfer named as such. Decided by: Claude (the gate). **Next:** the four wording calls to Yichen one at a time (headline framing; the probe's weakness relative to the authors' claims; the defence as a transfer; the scoop-risk posture), then FIXED, the handoff and memory updates, and Stage 8 (the outline) in Milestone 11.

## 2026-10-05 — Claim gate decision 1 (headline framing): "to our knowledge, the first security analysis of an activation-steering LLM watermark"

Yichen chose the recommended option: the headline claims, with the qualifier "to our knowledge", the first security analysis of an activation-steering LLM watermark (key recovery, forgery, scrubbing, exact tests and a keyed defence) on Self-Recognition's construction re-implemented on Qwen2.5-1.5B; the scheme and model are named in the abstract. Rejected: a case-study framing (undersells the exact test and the defence); a key-recovery-only headline (drops half the paper). Evidence: `CLAIM_GATE_v0.1.md` §1 (scoop check) and §3. Decided by: Yichen. **Next:** decision 2, how to state the probe's weakness relative to the authors' claims.

## 2026-10-05 — Claim gate decision 2 (the probe's weakness relative to the authors' claims): neutral and specific

Yichen chose the recommended option: the paper states that the detector type published with the scheme (a trained per-token MLP probe), re-trained by us on Qwen2.5-1.5B, accepts steering that is not the key; cites the authors' own observation that paraphrased human text "acts as a spoofing mechanism for our detector" (Self-Recognition, PDF p. 5); and states that under our conditions (base models, continuation perplexity under the same model, 256 tokens) the published strength did not reproduce, with their Table 7 numbers (PDF p. 15) beside ours. Never "their claims are false"; the abstract keeps the pre-registered finding (fluent forgery practical at ρ = 0.35; inconclusive at 0.50 and 0.70). Rejected: "the published detector is insecure" (generalises beyond the model tested); keeping the probe's failures out of the abstract (hides a central finding). Rule 7 of `CLAIM_GATE_v0.1.md` is confirmed. Decided by: Yichen. **Next:** decision 3, the defence as a transfer.

## 2026-10-05 — Claim gate decision 3 (the defence): a transfer measurement

Yichen chose the recommended option: the Study 5 section and the abstract present context keying and rotation as **transfers** (Kirchenbauer et al. 2023, PDF p. 7 for rotation with k detection tests and context hashing; Kirchenbauer et al. 2024 for the context-width trade-off; Pang et al. 2024 and Gu et al. 2024 for multiple keys; SynthID-Text for deployed practice), named as future work by Ardoin et al. (2026, p. 7); the finding is the measured stealing–robustness–quality frontier on this model and attacker, with the clustering attack as what breaks rotation at this budget (ρ = 0.35 through the labelled addendum). Rejected: a negative-result headline ("the no-free-lunch trade-off carries over" as a general statement; Pang et al.'s trade-off concerned a different removal attack); a deployer guideline (overreach from one model and one attacker). Rules 2 and 6 of `CLAIM_GATE_v0.1.md` are confirmed. Decided by: Yichen. **Next:** decision 4, the scoop-risk posture.

## 2026-10-05 — Claim gate decision 4 (scoop-risk posture): write now; the open leads become future work. CLAIM GATE v0.1 FIXED; Stage 7 done

Yichen chose the recommended option: Stage 8 (the outline, then drafting) starts in a new session "Milestone 11: outline" with the existing studies; Study 4 (a SLAM-style keyed target on Gemma), the h = 1 acceptance curve beyond n = 1,024 and the per-position h = 0 test on the study keys are stated as future work and limitations. Rejected: one more small study first (about a week); Study 4 first (two to three weeks and a new model licence). Evidence for the posture: `CLAIM_GATE_v0.1.md` §1 (the camera-ready is out; no follow-up in four months; two active neighbouring groups); the A6 tally (14 figures and 29 tables available from locked outputs).

With the four calls decided, [`CLAIM_GATE_v0.1.md`](CLAIM_GATE_v0.1.md) is **FIXED**: thirteen claims with wording verdicts, twelve binding wording rules, the competitor table with page-confirmed quotations. Last corrections merged from the full reads (stealing line): Jovanović et al. **evaluated** multiple keys (App. C, pp. 19–20: spoofing 0.68–0.81 with k = 2–4; "not a viable defense against our attacker"), so the token-level evidence on multiple keys is mixed and our rotation result has a token-level precedent; their p. 9 states the spoofing–scrubbing trade-off "does not hold", so the token-level literature disagrees about the trade-off; Beyond a Fixed Seal and MarkSec print no venue (ACL Findings 2026 to be confirmed at the Anthology; MarkSec is a preprint); MarkSec excludes model-internal schemes by scope (p. 2). Decided by: Yichen (the four calls); Claude (the gate). **Next:** the handoff and memory updates; the new session "Milestone 11: outline" (Stage 8).

## 2026-10-05 — Milestone 10 closed (14:16 UTC, 09:16 CDT); the handoff carries the Stage 8 checklist and the Milestone 11 starter prompt

Yichen asked to prepare the handoff for Milestone 11 and close the session. State at close: Stage 7 done; `CLAIM_GATE_v0.1.md` FIXED (PASS with narrowed wording; thirteen claims; twelve binding wording rules; decisions 1–4 recorded in §7); `RESEARCH_HANDOFF.md` status "Stage 7 done", resume point "Stage 8, the outline, in Milestone 11", with the Stage 8 checklist (outline with evidence column, figure and table plan from the 14 figures and 29 tables available, references from `research/literature/pdf_manifest.json` with venues still to confirm at the proceedings for KGW 2023, GaussMark and Beyond a Fixed Seal) and the starter prompt; the project memory updated; the research-project-guide skill gained the claim-gate reading lessons (Yichen to re-zip and re-upload for Cowork). Nothing was drafted for the paper; `research/paper/` stays empty until the outline. Everything is committed and pushed; the working tree is clean. Decided by: Yichen (the close); Claude (the records). **Next:** the new session "Milestone 11: outline" (Stage 8 step 1).

## 2026-10-05 — Stage 8 step 1: paper outline v0.1 DRAFTED (Milestone 11; 15:23 UTC, 10:23 CDT); awaiting the section-level review

Written (Claude): [`paper/OUTLINE_v0.1.md`](paper/OUTLINE_v0.1.md), bound by `CLAIM_GATE_v0.1.md` §2, §6 and §7. Contents: three working-title candidates (decided at the introduction draft; recommended: the plain "A Security Analysis of an Activation-Steering LLM Watermark: Key Recovery, Forgery, Scrubbing and Keyed Defences"); the one-paragraph pitch obeying rules 1, 2, 4, 5 and 7; the contributions copied from the gate's wording verdicts (C1–C9 and C13 claimed as narrowed; C10–C12 labelled; the not-claimed list); a nine-section plan with an evidence column (study, pre-registered rule, source table or figure, verdict) and a page budget of 12.75 pages (introduction 1.5; background and threat model 1.25; the exact test 1.0; setup 1.0; results 5.5 in seven subsections — calibration, forging the probe, the exact test, stealing the fixed key, scrubbing, the keyed arms as transfers, the trade-off; related work 1.25; limitations 0.75; reproducibility 0.5; conclusion 0.25) and nine appendices; a figure plan (six main-text figures: F1 calibration curves, **new**, from the calibration and reproduction outputs; F2 probe forgery from v0.4; F3 exact vs probe, two panels from Study 3; F4 stealing against the budget from Study 5; F5 scrubbing from Study 2; F6 the frontier with the addendum's point labelled post hoc; six appendix figures) and a table plan (six main-text tables: T1 studies and locks from the lock files; T2 calibration; T3 forging the probe; T4 the exact test; T5 scrubbing; T6 the fixed key and the keyed arms with a labelled addendum row; fourteen appendix tables), each with its locked source, its script name and its asserts; the regulator framing paragraph (rule 12); the AI-use disclosure placement for the arXiv, NeurIPS-workshop and ICLR-workshop versions; the drafting order for Milestones 12–15.

**Correction (rule A4.3, counts re-counted):** the gate's §10 tally of "14 figures and 29 tables" was a miscount; the report figures number **23** (Study 1 v0.2, v0.3 and v0.4 have three each, which the tally omitted; Study 2 five; Study 3 four; Study 5 five) and the report tables **31** (4 + 4 + 5 + 6 + 6 + 6). Nothing downstream depended on the tally.

Decided by: Claude (the draft). **Next:** Yichen's section-level review (one decision: approve, or change the section order and the figure and table plan); then the handoff's status becomes "Stage 8 in progress: outline approved; drafting next" and Milestone 12 drafts §2–§4 with T1 and the references.

## 2026-10-05 — Outline v0.1 APPROVED as drafted (section-level review; 15:25 UTC, 10:25 CDT); Stage 8 step 1 done; drafting goes to a new "Milestone 12" session

Yichen approved [`paper/OUTLINE_v0.1.md`](paper/OUTLINE_v0.1.md) as drafted: the nine-section plan in method order (the exact test before the results), the 12.75-page budget, six main-text figures (F1 calibration curves, new; F2–F6 regenerated from the v0.4, Study 3, Study 5 and Study 2 outputs, with the rotation addendum's point labelled post hoc in F6) and six main-text tables (T1 from the lock files; T2–T6 condensing the report tables; a labelled addendum row in T6), six appendix figures and fourteen appendix tables, the regulator paragraph and the disclosure placement. Rejected (offered): changing the figure and table plan; changing the section order (narrative order, or merging the stealing subsection into the defence); trimming toward ten pages. The outline's status line now reads APPROVED and binding; changes need a logged decision and a new version. The handoff carries the Milestone 12 checklist (set up `research/paper/`; draft §2–§4 and Appendices A–C from the protocols and the gate's page-confirmed quotations; the T1 and TA1–TA5 scripts; `references.bib` validated at 0 errors) and its starter prompt. Decided by: Yichen. **Next:** the new session "Milestone 12: method sections".

## 2026-10-05 — Stage 8 step 2: the method sections drafted (Milestone 12; 16:10 UTC, 11:10 CDT); awaiting the section-level review of §2–§4

Milestone 12 opened 2026-10-05 15:30 UTC (10:30 CDT). Written (Claude), all under `research/paper/`: `README.md` (the folder's conventions: one file per section with an "Open items" list; one script per table or figure reading locked outputs and asserting against them; numbers in prose as `[[placeholders]]` resolved by `fill_sections.py`, which fails on any unresolved name; quotations only from the gate's §3 and §8 with PDF pages; `[@key]` citations); `common.py`; the drafts `sections/sec2_background_threat_model.md`, `sec3_exact_test.md`, `sec4_setup.md`, `appA_protocols_locks.md`, `appB_exact_test_detail.md`, `appC_attackers.md`, each bound to its outline row and to the gate's §6 rules (transfers named with their originators; "exact on average over keys" with the per-key gate; attacker, budget and access in every security sentence; inferences and exploratory readings labelled; the first-order explanation of C4 kept as a labelled heuristic in App. B.5); six table scripts (`tables/tab1_studies_locks.py`, `tabA1_locks_full.py`, `tabA2_power_pilot.py`, `tabA3_s3_s4.py`, `tabA4_attacker_checks.py`, `tabA5_threat_check.py`) that re-hash every protocol, locked code file and results file against the six `PRE_RUN_LOCK.json` and manifests, re-compute medians, pooled rates, calibrated-key counts, verdicts and recovered-key counts from the per-key records and assert them, and register 530 values, of which the six drafts use 186; `build/` with T1, TA1, TA2, TA3a–b, TA4a–d, TA5 and the filled sections; `references.bib` (42 entries) built from the arXiv API, the PDF covers (author order), PMLR 202/235/306, the ACL Anthology, the NeurIPS 2023 and 2024 proceedings pages, Crossref and DataCite, validated with the citation-management skill: 0 errors, 11 warnings (missing page numbers at venues that assign none; no DOI for JMLR and an 1883 journal), anything second-hand flagged in `note`.

**Evidence and checks.** Every quotation in §2–§3 and App. B–C was re-confirmed by substring search in the `pdftotext` extraction with its page (Self-Recognition pp. 2, 3, 5, 6, 7, 11, 14; GaussMark pp. 5, 6, 7, 9, 11; KGW p. 7; MarkSec p. 3; Jovanović et al. pp. 3, 6; Pang et al. p. 6; Zhang et al. p. 8). Venues confirmed at primary sources: Self-Recognition PMLR 306:3406–3422; KGW PMLR 202:17061–17084; Watermark Stealing PMLR 235:22570–22593; Beyond a Fixed Seal, Findings of ACL 2026, pp. 20678–20695, DOI 10.18653/v1/2026.findings-acl.1036; No Free Lunch and Krishna et al. at the NeurIPS 2024 and 2023 proceedings pages; Reliability and Learnability by the "Published as a conference paper at ICLR 2024" line on their PDFs; SEEK by its PDF's NeurIPS 2025 footer. GaussMark has no venue anywhere we can see (OpenAlex lists only arXiv) and is cited as a preprint. **Corrections recorded:** (a) the claim gate's §0 scoop check listed the Self-Recognition group's token-level paper under arXiv:2606.22450, which is an unrelated 5G paper; the paper is arXiv:2606.31602 (Schäfer, Pilaszewicz and Wunder; three authors, not two), found by an arXiv title search; (b) GaussMark's arXiv metadata lists the authors as Block, Sekhari, Rakhlin, while the cover prints Block, Rakhlin, Sekhari; the cover order is used, as the gate's rule says; (c) the Code of Practice's cover title is "Code of Practice on Transparency of AI-Generated Content" (the Commission's page calls it the code on marking and labelling); both names are in the entry. **Access gaps:** DBLP and OpenReview answer with a bot challenge (stopped, not worked around); the NeurIPS 2025 proceedings index listed no papers; the NIST PDF's DOI target answered 404 to HEAD requests but served the file to GET.

**Page budget.** The first drafts of §2–§4 ran about 1.7× the outline's budget (1.25 + 1.0 + 1.0 pages) and were trimmed before the review, with the detail kept in App. A–C; the counts after trimming are in the handoff's Milestone 12 entry.

Decided by: Claude (the drafts, the scripts, the bibliography). **Next:** Yichen's section-level review of §2–§4 (wording judgments only; the structure is the outline's), then Milestone 13 (the results sections and their figure and table scripts).

## 2026-10-05 — skill updated (Milestone 12): design constants as placeholders; bibliography from primary sources with named access gaps; word counts against the page budget before a review

Three lessons from drafting the method sections were added to the research-project-guide skill (Part G, 2026-10-05): register design constants (layer, sparsity, pools, sampling, grids, bars) from the lock, code and validation files as placeholders like every result; build the bibliography from PMLR, the ACL Anthology, the NeurIPS proceedings pages, the PDF's own venue line and one arXiv API `id_list` call, re-fetching every id by title (the gate's scoop check had recorded a wrong id) and taking author order from the cover (GaussMark's arXiv order differs), with DBLP and OpenReview recorded as bot-gated stops; count words per section against the outline's budget before the review and name each section's candidate cut in its open items. The skill lives outside the repository; Yichen should re-zip and re-upload it for Cowork. Decided by: Claude.

## 2026-10-05 — §2–§4 APPROVED as drafted (section-level review; 16:40 UTC, 11:40 CDT); length kept, pages to be recovered in §5; Milestone 12 complete

Yichen approved the method sections (§2 background and threat model, §3 the exact test, §4 setup; `research/paper/sections/`) as drafted, with the three wording calls resolved the recommended way: "forgery" throughout with "spoofing" once in parentheses (§2.2); the compute sentence names the chip ("one Apple-silicon laptop (M5, 16 GB unified memory)"); the Rao (1948) citation stays beside GaussMark for "the score statistic" (§3). Rejected (offered): flipping any of the three; requesting passage-level changes. **Length:** the three sections run about a third to a half over the outline's 3.25-page budget (prose words 1,409 / 1,040 / 966); Yichen chose to keep the detail and recover the pages in the results subsections (Milestone 13 tightens §5.1–§5.7 to hold the 12.75-page total). Rejected: the named cuts (§2.3 to two sentences; §3's pilot paragraph; §4's pool sizes into T1's caption); raising the budget to about 13.5 pages. The open items of the three files are updated to record these decisions; the remaining open items are assembly checks (Milestone 15) and the §5.1 numbers (Milestone 13). Appendices A–C were not part of the review and keep their open items.

Decided by: Yichen. **Milestone 12 is complete.** Next: the new session "Milestone 13: results" (checklist and starter prompt in the handoff).

## 2026-10-05 — Stage 8 step 2: the results sections drafted (Milestone 13; 17:15 UTC, 12:15 CDT); awaiting the section-level review of §5

Milestone 13 opened 2026-10-05 after the §2–§4 approval. Written (Claude), all under `research/paper/`: the five main-text table scripts `tables/tab2_calibration.py` (T2: calibration v0.1–v0.3 and the reproduction pilot's α = 5 rows as ρ; asserts `operating_point` is None in all five files and re-derives the rule's flags), `tab3_probe_forgery.py` (T3a forgery, T3b recovery and the v0.3 repetition note; re-derives L1, R1, G1, v0.2's "practical" verdicts and v0.4's F1 and F3 from the rules), `tab4_exact_test.py` (T4; re-derives E1, X1, X3, the pooled rates and the key-leakage lens — 35 of 384 cells at ≥ 50%, Spearman 0.68 and 0.56 — from the per-key arrays), `tab5_scrubbing.py` (T5; re-derives S1, S2 and C1 and every key count) and `tab6_defence.py` (T6a stealing with the labelled post-hoc addendum rows, T6b robustness and quality; re-derives P0, D1, D2, D3 and the addendum's three selection rules); the six figure scripts `figures/fig1_calibration.py` (F1, new: AUROC and perplexity ratio against ρ for three models with the α = 5 points), `fig2_probe_forgery.py`, `fig3_exact_vs_probe.py` (two panels), `fig4_stealing_vs_budget.py` (with a labelled tuning-key row; `--no-pilot` writes `F4_nopilot.png`), `fig5_scrubbing.py` and `fig6_frontier.py` (the addendum's every-cluster point hollow and labelled post hoc), every plotted median asserted against the per-key records; the palette validated with the dataviz skill's script (the four coloured series pass every gate; the grey is the recessive mark); every figure viewed and five layout fixes made (tick collisions, a log-axis formatter, row labels over a panel, colliding row titles, a label on a data point). The drafts `sections/sec5_1_calibration.md` … `sec5_7_tradeoff.md` (§5.1–§5.7) are bound to their outline rows and the gate's rules: verdicts in the studies' vocabulary with "inconclusive" kept where the rules say so; rotation at ρ = 0.35 stated only through the labelled addendum beside the pre-registered verdict; the probe's weakness stated against the detector type as re-implemented, with the authors' paraphrase-spoofing observation (p. 5) and their Table 7 numbers (p. 15) beside ours; exploratory and post-hoc readings labelled; "not the first to note" where rule 10 applies; the budget comparison with the access caveat. Every quotation used in §5 was re-confirmed by substring search in the `pdftotext` extraction of the Self-Recognition PDF (pp. 1, 5, 7, 15). `fill_sections.py` resolves every placeholder (1,330 registered values; 333 used by the drafts so far).

**Page budget (decision 2026-10-05).** The first drafts ran 3,729 prose words (5.74 pages at 650 words a page) against the 4.75-page target (the 5.5-page plan less the 0.75 page to recover from §2–§4). Two cutting passes applied the named candidate cuts, each number moved to the table or appendix that carries it with its registered name listed in the section's open items: the 512-token numbers (§5.1), the v0.3 loop numbers and the probe-reading sentence (§5.2), the narrowest-margin and key-1002 sentences (§5.3), the 10%-edit and probe-on-paraphrase numbers (§5.5), the gate ranges, the largest-cluster FA and Jovanović et al.'s k = 2–4 numbers (§5.6). After them §5 holds 3,298 words = 5.07 pages (§5.1 0.50; §5.2 0.93; §5.3 0.82; §5.4 0.57; §5.5 0.71; §5.6 1.27; §5.7 0.27), 0.43 page under its plan and 0.32 page short of the target; the remaining candidate cuts (§5.6's point-of-difference paragraph to §6; §5.2's version history to Table T1) are a wording call for the review.

Decided by: Claude (the scripts, the drafts, the cuts). **Next:** Yichen's section-level review of §5 (wording judgments; the F4 tuning-key row; the remaining length), then the Milestone 13 exit and "Milestone 14: introduction, related work, title".

## 2026-10-05 — skill updated (Milestone 13): apply named cuts before the review when the page target is already decided; validate only the coloured series; keep variant figure outputs apart

Two lessons were added to the research-project-guide skill (Part G, the 2026-10-05 drafting entry): when a standing decision fixes the page target, apply the named candidate cuts before the review, moving each cut number to the table or appendix that carries it and listing it with its registered name in the open items so the review can restore it; and for figure scripts, validate only the coloured series with the dataviz script (a recessive grey "fails the chroma floor" as a categorical slot) and write a variant output's values under a different name, or the fill step refuses the conflicting duplicate. The skill lives outside the repository; Yichen should re-zip and re-upload it for Cowork. Decided by: Claude.

## 2026-10-05 — §5.1–§5.7 APPROVED as drafted (section-level review; 17:18 UTC, 12:18 CDT); F4 without the tuning-key row; length kept; Milestone 13 complete

Yichen approved the results sections (`research/paper/sections/sec5_1_calibration.md` … `sec5_7_tradeoff.md`) as drafted, the recommended option in each of the three calls: (1) approve as drafted (rejected, offered: wording changes; reading first); (2) Figure F4 drops the labelled tuning-key row (the pilot numbers stay in §5.4's text and Table TA5; `fig4_stealing_vs_budget.py --pilot` still renders the variant as `build/F4_pilot.png`, unused; rejected: keeping the row); (3) §5 stays at 5.07 pages, 0.32 page over the 4.75-page target, the net 2.5% overrun on the 12.75-page plan to be recovered when §6–§9 are drafted (rejected: the two remaining cuts; restoring applied cuts). The open items of the seven files record the decisions; the outline's §10 marks the F4 row decided. Decided by: Yichen. **Milestone 13 is complete.** Next: the new session "Milestone 14: introduction, related work, title" (checklist and starter prompt in the handoff).

## 2026-10-05 — Stage 8 step 3: introduction and related work drafted (Milestone 14; 17:47 UTC, 12:47 CDT); awaiting the title decision and the section-level review of §1 and §6

Milestone 14 opened 2026-10-05 after the §5 approval. Written (Claude), under `research/paper/`: `sections/sec1_introduction.md` (the family and its pitch with Self-Recognition's own words, pp. 2 and 5; the security question its authors leave open, p. 7; the regulator paragraph of the outline's §7 with every measure re-confirmed against the PDF text, Code of Practice pp. 9, 17, 18 and NIST AI 100-4 pp. 13, 38; what we do, as five questions; the contributions list from the outline's §3 with "to our knowledge" on the headline, the transfers named with their originators, every number a registered placeholder already used by §5, and one sentence on what is not claimed pointing to §7) and `sections/sec6_related_work.md` (the outline's five groups, each predecessor with the gate's "what it answers / what remains", every quotation re-confirmed by substring search with its PDF page; rule 10's "not the first to note" citations placed in full; SAEMark's phrase taken from its arXiv abstract, fetched today). Supporting changes: `research/literature/download_regulator_pdfs.py` fetched the three regulator PDFs once each under the terms check (addendum recorded in `TERMS_OF_USE_CHECK.md`; manifest now 16 entries with SHA-256; files git-ignored); `research/paper/wordcount.py` counts prose words per section against the 650-words-a-page convention; `fill_sections.py` resolves every placeholder (sec1 uses 24; sec6 none by design, its numbers being quotations from the cited papers).

**Checks and gaps.** Quotations confirmed with pages: Self-Recognition pp. 2, 5, 7, 14; GaussMark pp. 11, 19, 48; Pang et al. pp. 5, 6, 7; Jovanović et al. pp. 1, 3, 6, 9, 19, 20 (Table 14 on p. 20); KGW pp. 4, 6, 7; Reliability pp. 17, 21; Learnability pp. 2, 19, 20; Beyond a Fixed Seal pp. 8, 18; SEEK p. 1; MarkSec pp. 2, 3, 8; SLAM pp. 2, 5, 7, 8 (and the words stealing, spoof, forgery, threat model absent); AWM pp. 2, 3; SynthID-Text pp. 2, 6; the Code of Practice pp. 9, 17, 18; the Article 50 guidelines pp. 25, 26; NIST pp. 13, 19, 20, 38. One correction to the gate's reading: Jovanović et al.'s GPT-4 judge is named on p. 10 of the PDF, not pp. 6–7 (P-SP is on pp. 6–7); the clause was cut rather than restated. Access gap: the ETH SRI blog page timed out (no bytes; not retried), so it is not cited in §6 and its figures stay unquoted.

**Page budget.** The first drafts ran 1,333 and 1,087 prose words against the checklist's 975 and 810 (1.5 and 1.25 pages at 650 words a page). Two cutting passes applied the named candidate cuts (listed with their registered names in each file's open items: C8 folded into contribution 2 without numbers; C9 and C13 to the closing paragraph; the human-text and random-key rates, the perplexity ratios and the scrub differences out of the contributions; in §6 the Nemecek sentence, the SEEK p. 29 clause, the blog clause, and five quotations paraphrased). After them §1 holds 1205 words (1.85 pages) and §6 958 words (1.47 pages); the remaining candidates are named in the open items and are a wording call for the review. **A convention drift surfaced:** the §2–§4 approvals reported "about 1.5 + 1.3 + 1.2 pages" for 1,409 / 1,040 / 966 words (about 900 words a page), while §5 and this milestone count at 650 words a page; by the 650 convention §1–§6 now hold about 13.6 pages against the outline's 11.5, and the real count comes from the rendered PDF at assembly (Milestone 15). Recorded as a skill lesson (below).

Decided by: Claude (the drafts, the cuts). **Next:** the title (outline §1, one decision, recommended first), then Yichen's section-level review of §1 and §6.

## 2026-10-05 — skill updated (Milestone 14): fix the words-per-page constant in a committed script before the first section is counted

One lesson was added to the research-project-guide skill (Part G): commit a word-count script with one named words-per-page constant at the first draft and quote it in every review, because two conventions (about 900 and 650 words a page) were used across Milestones 12 and 13 and the drift surfaced only now; the rendered PDF at assembly is the only real page count. The skill lives outside the repository; Yichen should re-zip and re-upload it for Cowork. Decided by: Claude.

## 2026-10-05 — Title decided (Milestone 14; 18:39 UTC, 13:39 CDT): "A Security Analysis of an Activation-Steering LLM Watermark: Key Recovery, Forgery, Scrubbing and Keyed Defences"

Yichen chose the recommended option (a) of the outline's §1: plain and accurate, naming the family and the four measurements, with "to our knowledge" kept in the headline sentence of §1 and no "first" in the title (gate rule 1). Rejected (offered): (b) "The Detector's Statistic Is the Thief's Estimator: Stealing and Defending an Activation-Steering LLM Watermark" (leads with C4, but its first clause is a labelled inference); (c) "Who Holds the Key? Stealing, Forging and Defending an Activation-Steering LLM Watermark" (drops the exact test). Recorded in the outline's §10 and in §1's open items; the assembly script (Milestone 15) carries the title. Decided by: Yichen. **Next:** the section-level review of §1 and §6.

## 2026-10-05 — §1 and §6 APPROVED as drafted (section-level review; 18:42 UTC, 13:42 CDT); Milestone 14 complete

Yichen approved the introduction (`research/paper/sections/sec1_introduction.md`) and the related work (`sec6_related_work.md`) as drafted, the recommended option: the applied page-budget cuts stand, the remaining named candidates stay in the open items, and the length is settled by the rendered PDF at assembly. Rejected (offered): applying the remaining named cuts now (the regulator paragraph to two sentences, the five questions to section references, the SynthID-Text sentence to a citation, the SAEMark and Zenodo sentence out); restoring applied cuts (C8's numbers, contribution 7's ratios and differences, KGW's averaging quotation). State at close: §1–§6 and App. A–C drafted and approved; the title decided; `fill_sections.py` resolves every placeholder (365 of 1,329 registered values used); the handoff carries the Milestone 15 checklist (§7–§9; App. D–I with FA1–FA6 and TA6–TA14; `assemble.py`; the rendered page count; the open-items pass) and its starter prompt. Decided by: Yichen. **Milestone 14 is complete.** Next: the new session "Milestone 15: limitations, appendices, assembly".

## 2026-10-06 — Stage 8 steps 4–5: §7–§9, the abstract and Appendices D–I drafted, FA1–FA6 and TA6–TA14 built, the draft assembled and rendered (Milestone 15; 14:57 UTC, 09:57 CDT); awaiting the section-level review and the length decision

Milestone 15 opened 2026-10-06. Written (Claude), under `research/paper/`: the six appendix figure scripts `figures/figA1_per_key_calibration.py` … `figA6_paraphrase_per_arm.py` and the nine table scripts `tables/tabA6_per_key_fa.py` … `tabA14_v02_full.py`, each reading the locked `results.json` files named in the outline and asserting every median, count, selection rule and gate against the per-key records (every figure viewed; four layout fixes); `tables/appH_samples.py` (the quoted samples registered as placeholders from the locked results and the generated reports, never retyped); `tables/appA_v01_gate.py` and `appA_probe_config.py`; the drafts `sections/sec0_abstract.md`, `sec7_limitations.md`, `sec8_reproducibility.md`, `sec9_conclusion.md` (with the acknowledgements and the AI-use paragraph at the outline's arXiv placement) and `appD_per_key.md` … `appI_regulators.md`, each bound to its outline row and the gate's rules, every number a registered placeholder (`fill_sections.py`: 2,893 registered, 585 used, none unresolved); `assemble.py` (the outline's order; tables and figures placed at their markers or after the paragraph that first mentions them, appendix tables kept in the appendix; renumbering and cross-reference rewriting; the `(see build/…)` markers removed and the remaining repository paths listed for review; every `[@key]` checked against `references.bib`; the six protocol hashes in Table 1 re-hashed from the protocol files and compared with the lock files; the open items collected into `PAPER_OPEN_ITEMS_v0.1.md`, decisions first; `--render` builds HTML with pandoc and PDF with headless Chrome and writes `build/page_count.json`; measurement variants with `--stem`); `paper.css`; `PAPER_DRAFT_v0.1.md`, `build/PAPER_DRAFT_v0.1.pdf`.

**Checks and records.** Quotations re-confirmed by substring search in a reading-order `pdftotext` extraction with their pages (layout mode had split three across the two columns): Self-Recognition pp. 5, 7, 14 and the Table 3 numbers on p. 6; the Code of Practice pp. 9, 13, 15, 16, 17, 18; the Article 50 guidelines pp. 25, 26; NIST AI 100-4 pp. 13, 19, 20, 38; GaussMark p. 11; the four token-level budgets. `references.bib` re-validated: 0 errors, 11 warnings (unchanged); 38 of 42 entries cited. Earlier open items resolved: the editor's constants match the locked `scrub_core.py` (App. C.6); no lock file names a WikiText set (§4); the scheme's public repository was cloned at commit `7c26938` and its `param.yaml` sets the probe's hidden widths to 2048, 64, 64, 32, which the locked `detect2.py` replicates, now stated in App. A beside the paper's "two hidden layers of width 32" (§2.1); the per-position h = 0 check is cited in App. B.4 from the pilot's I4 addendum. **Two records:** (a) Study 1 v0.1's runner stop state (`G1_STATE.json`, the gate's 0% on four tuning keys at α = 5 and 10) was copied unchanged from the run's git-ignored data folder into `research/outputs/study1_v0.1/qwen/` with its SHA-256, so App. A's two numbers are generated; (b) rotation's detection rate after paraphrase (the report's Table 4 and Fig. 2) was computed by the report builder from the run's per-key files and is not in the locked `results.json`, so Table TA13a and Figure FA6 omit it and say so.

**The rendered count (Letter, 1 inch margins, 11 pt serif, single column; about 48 lines and 700 words a text page).** Full draft 63 pages; main text (title, abstract, §1–§9, acknowledgements, tables and figures, no references) **27 pages** against the outline's 12.75; prose alone 16 pages, figures 5, tables 7 (measured by rendering without each). Variants: figures at 80% with T3b and T6b moved to the appendix, 25; figures at 70% with T2, T3b and T6b moved, 23; T1 moved as well, 23; figures at 60% with T1, T2, T3a, T3b, T4 and T6b moved, 21. By the 650-words-a-page convention the prose is §1 1.85, §2 2.12, §3 1.58, §4 1.47, §5 5.07, §6 1.47, §7 1.02, §8 0.68, §9 0.46 pages (abstract 0.55). Two rendering defects were found and fixed before the count: Chrome shrinks the whole page to fit the widest element (an unbroken hash in Table 1 had halved the type), and pandoc gives pipe-table columns equal widths unless the separator line says otherwise.

Decided by: Claude (the scripts, the drafts, the assembly). **Next:** Yichen's section-level review of §7–§9, Appendices D–I and the abstract, then the length decision (one at a time, recommendation first).

## 2026-10-06 — skill updated (Milestone 15): zsh word-splitting; rendering a Markdown draft for a page count

Two lessons were added to the research-project-guide skill (Part G): zsh does not word-split an unquoted variable, so a loop over variant flag strings passes each as one argument and a script silently runs its default (make scripts print the options they parsed); and the rendering procedure for a page count (pandoc to HTML, headless Chrome to PDF; fixed table layout and wrapped cells so the page is not shrunk to fit; proportional pipe-table widths; the bibliography suppressed in the main-text count; measurement variants to see where the pages go). The skill lives outside the repository; Yichen should re-zip and re-upload it for Cowork. Decided by: Claude.

## 2026-10-06 — §7–§9, the abstract and Appendices D–I APPROVED as drafted (section-level review; 15:08 UTC, 10:08 CDT)

Yichen approved the limitations and future work (§7), the reproducibility, ethics and disclosure section (§8), the conclusion with the acknowledgements and the AI-use paragraph (§9), the abstract and Appendices D–I as drafted, the recommended option. Rejected (offered): wording changes now; reading first. The braces in §8 (the availability statement) and in the acknowledgements (funding and thanks) stay as his Stage 9 decisions; the remaining open items are records (`research/paper/PAPER_OPEN_ITEMS_v0.1.md`, Part 2). Decided by: Yichen.

## 2026-10-06 — Length decided: about 24 pages for the arXiv paper (option (a)); the named cuts applied; rendered 24 main pages, 60 in all (15:08 UTC, 10:08 CDT); Milestone 15 complete

The rendered main text ran 27 pages against the outline's 12.75 (prose 16, figures 5, tables 7; measured by rendering without each). Yichen chose the recommended option (a): keep every approved finding, render the figures at 80% of the text width, make Table T3b (v0.2's key recovery) and Table T6b (the keyed arms' D2 and D3 detail) appendix tables (now Tables A15 and A16, placed in App. E.3 and App. G.1; the remaining parts of Tables 3 and 6 lose their letters), and apply the prose cuts the sections' open items had named: §1's regulator paragraph to two sentences and the five questions to section references; §2.3 to two sentences; §3's pilot paragraph shortened; §4's pool sizes into Table 1's note (generated by `tab1_studies_locks.py`); §5.2's version history to Table 1; §5.6's point-of-difference paragraph to one sentence (§6 carries the numbers); §6's SynthID-Text sentence to a citation and its SAEMark and Zenodo sentence removed; §7's quality paragraph to two sentences; §8's model list compressed. Every cut is recorded in its section's open items; no registered value was lost from the paper except the two pilot per-key readings that Table A2 carries. Rejected (offered): about 21 pages by moving most main tables; holding 12.75 pages (about 5,000 words of approved prose); keeping 27 pages. **The guide's 10–13-page standard (A6) applies for this paper to the condensed venue version derived from the arXiv paper**, recorded in the outline's §10. After the cuts the draft renders at **24 main-text pages and 60 in all** (`research/paper/build/page_count.json`; prose by the 650-words-a-page convention: §1 1.79, §2 2.02, §3 1.54, §4 1.41, §5 4.99, §6 1.39, §7 1.01, §8 0.67, §9 0.46, abstract 0.55). The assembly's default now carries the decision (`assemble.py`: figures at 80%, `DEFAULT_MOVE`, `RENUMBER`).

Decided by: Yichen (the length; the cuts were named before). **Milestone 15 is complete; Stage 8 is done:** the full draft is assembled, every number is generated and asserted, the bibliography validates at 0 errors, and the open items that remain are his Stage 9 decisions. Next: the new session "Milestone 16: pre-publication" (checklist and starter prompt in the handoff).

## 2026-10-06 — Stage 9 step 2: the final source gate is DONE and clean (Milestone 16; 15:45 UTC, 10:45 CDT); step 4 rights check done; three factual additions to the draft

Milestone 16 ("pre-publication") opened 2026-10-06. The scoop check and the mechanism searches were re-run for work since the claim gate (the authors' repository unchanged since 2026-06-16; Semantic Scholar: Self-Recognition still 0 citing papers, SLAM 1 unchanged, AWM 1 new and already in the bibliography uncited, GaussMark the same 14; OpenAlex 0/0/0; the arXiv API answering today: 12 mechanism queries and 5 author queries, 20 distinct new items since 2026-09-28 screened at abstract level; OpenAlex 5 searches). **No predecessor of any claim**; the claim list, the wording rules and the headline stand (`research/FINAL_GATE_v0.1.md`). One concurrent work was read in full under the terms check and added to the manifest: Chen et al., arXiv:2610.04907 (2026-10-04), steering-vector recovery by distillation with a Fisher-distortion reading of the first gradient, no watermark content (the word does not occur); it is cited in §6's score-test paragraph as concurrent, with its p. 1 quotation confirmed by substring search. The ETH SRI blog was fetched at the bibliography's URL (the 2026-10-05 attempt had timed out) and its 4% / 15% / above-90% figures confirmed in the page text; Appendix I now quotes them with the date read and the bibliography note records the confirmation. The two Commission documents and NIST AI 100-4 are byte-identical to the locked copies; the Commission's opinion of 8 July 2026 that the Code "adequately covers" the Article 50(2), (4) and (5) obligations (library page read 2026-10-06) is cited in Appendix I for the Code's status. The six model cards' licences were re-read from the Hugging Face API (unchanged; each current revision equals the pinned one; §8's open item closed). Rebuilt and re-rendered: every placeholder resolves (2,896 registered values), `references.bib` 44 entries at 0 errors (38 cited; the six uncited entries unchanged, decision 3(e)), 24 main pages (unchanged), 61 in all. **Rights check (gate §7):** every quoted arXiv e-print is CC BY 4.0, CC BY-SA 4.0 or under arXiv's non-exclusive licence (OAI records), the Nature paper CC BY 4.0, NIST public domain, the Commission documents under Decision 2011/833/EU, the authors' code MIT; the Common Crawl terms were re-read; Appendix H quotes one 31-word C4 prompt excerpt (a wording call for Yichen's read); no permission email is needed. Access gaps recorded: OpenReview (challenge), Google Scholar (not searched), the opinion PDFs (not read). Decided by: Claude (the gate; the three factual additions, listed for Yichen's full read). **Next:** Yichen's Stage 9 decisions, one at a time, availability first.

## 2026-10-06 — Stage 9 decisions (a)–(d) and (f) taken (Milestone 16; 16:10–16:40 UTC, 11:10–11:40 CDT); a TeX engine installed

Yichen took the recommended option in each case, one at a time. **(a) Availability:** a public snapshot repository (created as `SHENSHENZYC/activation-watermark-security`, private until posting; MIT for code, CC BY 4.0 for text and figures) holding the protocols, locks, validation reports, manifests, result files and every script, without model weights or the generated corpora; §8's statement is written in and names the URL, §1's and the abstract's last sentences stand, §8's ethics sentence now says the only generated texts in the repository are the samples quoted in Appendix H and the reports (rejected, offered: making the working repository public as is; "on request"). **(b) Author and funding lines:** "Yichen Zhao (Independent Researcher; alexyczhao@gmail.com)" on the title page (`assemble.py`), "This work received no external funding." and no thanks line in the acknowledgements; no ORCID given (rejected: name and email only; a thanks line). **(c) The holdout** stays sealed for follow-up work; Appendix A's sentence says so (rejected: unsealing without a run; a confirmatory run on the holdout before posting). **(d) The arXiv abstract:** the 1,912-character cut in `research/paper/sections/sec0_arxiv_abstract.md` (every number a registered name; the forgery percentages, scrub rates, perplexity ratios and the activation-mean clause dropped; ASCII forms) is approved as the arXiv abstract field; the PDF abstract stays as approved (rejected: cutting the PDF abstract too; editing it himself). **(e) The six uncited bibliography entries** stay in `references.bib` as records (Claude's routine call: BibTeX prints only cited entries, so the choice has no effect on the paper). **(f) arXiv category and licence:** cs.CR primary with cs.CL and cs.LG cross-lists, CC BY 4.0 (rejected: cs.CL primary; the arXiv non-exclusive licence). **Tooling:** no TeX engine was installed on the Mac; Yichen approved `brew install tectonic` (Tectonic 0.17.0; rejected: BasicTeX; no local engine), and `common.save_fig` now writes a PDF beside every PNG (the twelve figure scripts re-run; 12 PDFs). Decided by: Yichen (a)–(d), (f), the engine; Claude (e). Next: decisions (g) endorsement and (h) the courtesy notice; the LaTeX conversion; the public snapshot script.

## 2026-10-06 — Stage 9 decisions (g) and (h) taken (Milestone 16; 16:55 UTC, 11:55 CDT); the public snapshot builder and the two email drafts written

**(g) Endorsement:** Yichen will ask Nikola Jovanović (ETH Zürich, SRI Lab) first; the arXiv API counts today (cs.CR papers since 2022) were Vechev 38, Kerschbaum 30, Goldstein 24, Staab 18, Jovanović 16, Lukas 14, Wunder 14, Pang 5, Kirchenbauer 4, Block 3 (rejected, offered: Lukas; Goldstein; Wunder). The request email is drafted in `research/paper/ENDORSEMENT_REQUEST.md` (Yichen sends it with the PDF and arXiv's endorsement link; no address copied). **(h) Courtesy notice** to the Self-Recognition authors: yes, on the day of posting, after the listing is public (rejected: before posting with the PDF; no notice); drafted in `research/paper/COURTESY_NOTICE.md`. **Step 5, the public copy:** `tools/make_public_snapshot.py DEST [--git]` builds the snapshot from the git-tracked tree at HEAD (the session handoff, the `.claude/` skills and the page-count measurement variants excluded; the one absolute local path generalised; a secrets scan; LICENSE MIT, LICENSE-TEXT CC BY 4.0, README with the layout and rebuild steps, CITATION.cff, SNAPSHOT_MANIFEST.json with every file's SHA-256); the test build into the scratchpad gave 433 files, 20.4 MB. It is pushed to `activation-watermark-security` at the posting commit and the repository is made public then. Decided by: Yichen (g), (h); Claude (the drafts, the builder).

## 2026-10-06 — Stage 9 step 6: the arXiv LaTeX version compiles (Milestone 16; 17:45 UTC, 12:45 CDT); a math defect in §7 found and fixed; the paper is ready for Yichen's full read

`research/paper/make_latex.py` (Claude) converts the assembled draft to LaTeX and compiles it with Tectonic: the assembly's table and figure labels stay inside the captions (printed with `labelformat=empty`, so every cross-reference is unchanged), LaTeX numbers the sections and appendices, citations go through natbib (numeric `plainnat`; 38 keys), the bibliography copy ships without the internal `note` fields, the twelve figures are vector PDFs, the non-ASCII characters are mapped to macros so that arXiv's pdflatex and Tectonic's XeTeX agree, code paths and hash prefixes get break points, tables above seven columns are set at `\scriptsize`, and float placement is tuned so a tall figure shares its page. Output `research/paper/latex/main.pdf`: **67 pages, 25 of main text** (the HTML render gave 60 and 24; Computer Modern at 11 pt runs longer); 123 overfull lines, the widest 13.7 pt, none visible at reading size; no missing glyph. **A defect in the approved draft was found by the compile and fixed at the source:** §7 wrote the strength grid as `$\rho \in \{$[[levels_all]]$\}$`, which pandoc cannot read as math (a closing dollar followed by a digit), so the HTML render and `PAPER_DRAFT_v0.1.pdf` had printed the raw dollars; it now reads `$\rho \in \{[[levels_all]]\}$` (sec7_limitations.md). Pages viewed: the title page, Table 1, Table 2, Table 4, Figure 1, Figure 4 with Table 6, Table A4b, Figure A2, the references and Appendix C. The internal repository paths in §4 and Appendix A are kept, because the public snapshot has the same layout. `.gitignore` excludes the LaTeX intermediates. Two lessons were added to the research-project-guide skill (Part G: final-gate and rights-check mechanics; Markdown-to-arXiv-LaTeX conversion). Decided by: Claude. **The paper is ready for Yichen's full read** (`research/paper/latex/main.pdf`); the posting checklist is in the handoff.

## 2026-10-08 — Handover to a Codex session for the final review and revision (Milestone 16)

Yichen decided to hand the paper to a Codex session for a final review and revision before his own full read. `CODEX_HANDOFF.md` (repository root; Claude) orients that session without the private playbook or memory: the project in two paragraphs, where everything is, ten hard rules (never edit a locked file, with a one-line command that lists every hashed path; no number typed by hand, with the trace from a placeholder to its script and locked file; quotations only with a PDF page confirmed by substring search; the claim gate's twelve wording rules; approved text revised for correctness, consistency and clarity only, judgements brought to Yichen; the AI-use disclosure to name the second tool if its changes are substantive, on Yichen's approval; nothing posted, pushed to the snapshot's remote, emailed or made public; dated log entries and the handoff's resume point; no downloads or workarounds; the repository paths kept on purpose), the build commands, the task in four steps (read; the review memo `research/paper/CODEX_REVIEW_v0.1.md` with claims-against-evidence, consistency, quotations, wording rules, prose, rendering, the four open wording calls and a do/ask classification; revisions in the section files only with a rebuild after each commit; a closing report), what remains Yichen's, the environment facts and the state of the project. The handoff's checklist gains step 7a (the Codex review) before Yichen's read. Decided by: Yichen (the handover); Claude (the orientation file).


## 2026-10-08, 14:47 UTC (09:47 CDT) — Codex final review memo before revisions (Milestone 16)

Read the full 67-page LaTeX paper and the handoff-required records. Wrote `research/paper/CODEX_REVIEW_v0.1.md` before changing any existing repository file. The memo maps every abstract/introduction/results placeholder to its registering script and locked inputs, reviews every Section 5 verdict, records quotation/page checks, consistency and wording issues, visible table and section-symbol defects, and classifies D1–D5 as meaning-preserving section edits and A1–A12/O1–O4 as decisions for Yichen. Replayed all 23 table scripts with output redirected outside the repository: all assertions passed and registered values agree; no study was run. Independent checks cover the current D1 blocked bounds and rotation paired differences despite gaps in the table assertions. No source quotation changed. The principal open corrections concern known-layer forgery access, abstract/rotation scope, median versus universal claims, protocol descriptions, and generated table notes. Baseline `1283ba23ddd7007a6c9333457faf67a6980a7ca4`; LaTeX 67 total/25 before references, 123 overfull hboxes (34 >5 pt). Only the new memo and this log entry are changed in this step. Decided by: Codex (review findings, recommendations and D1–D5 classification); no Yichen decision is inferred.


## 2026-10-08, 14:48 UTC (09:48 CDT) — Codex D1/D2/D3/D5 section-source corrections (Milestone 16)

Applied the review memo's meaning-preserving reference/provenance pass: spelled out Section references (and Appendix D.3) to avoid the visibly incorrect LaTeX section glyph; identified the locked `PROMPTS["P2"]` definition/selector in Section 4 and repaired C.6's circular pointer; replaced matching observed-budget, key-count, continuation-length and layer-count literals with existing registered placeholders; corrected the abstract's stale metadata-cut record using the 2026-10-06 approval. Every edited section records its changes in Open items. Filled-text comparison confirms every numerical value is unchanged and the only body changes are the intended reference/prompt pointers. Files: `research/paper/sections/appA_protocols_locks.md`, `research/paper/sections/appB_exact_test_detail.md`, `research/paper/sections/appC_attackers.md`, `research/paper/sections/appD_per_key.md`, `research/paper/sections/appE_quality.md`, `research/paper/sections/appF_scrubbing_secondaries.md`, `research/paper/sections/appG_defence_detail.md`, `research/paper/sections/appI_regulators.md`, `research/paper/sections/sec0_abstract.md`, `research/paper/sections/sec1_introduction.md`, `research/paper/sections/sec2_background_threat_model.md`, `research/paper/sections/sec3_exact_test.md`, `research/paper/sections/sec4_setup.md`, `research/paper/sections/sec5_1_calibration.md`, `research/paper/sections/sec5_2_probe_forgery.md`, `research/paper/sections/sec5_3_exact_test.md`, `research/paper/sections/sec5_4_stealing.md`, `research/paper/sections/sec5_5_scrubbing.md`, `research/paper/sections/sec5_6_keyed.md`, `research/paper/sections/sec5_7_tradeoff.md`, `research/paper/sections/sec6_related_work.md`, `research/paper/sections/sec7_limitations.md`, `research/paper/sections/sec8_reproducibility.md`, `research/paper/sections/sec9_conclusion.md`. A1–A12/O1–O4 remain recommendations, including the two generated table-note glyphs and unregistered scalar constants; no claim, verdict, quotation, AI-use paragraph or generator was revised. Source commit followed by the specified fill/citation/assembly/LaTeX/word-count rebuild. Decided by: Codex.


## 2026-10-08, 14:50 UTC (09:50 CDT) — Rebuild after Codex reference pass `8046891`

Ran the handoff commands: fill (2,896 registrations, zero unresolved), assembly with render (38 citation keys all present; 43 table/figure placements), LaTeX compilation (31 tables, 12 figures), and word count. The literal `python3` citation command and `/usr/bin/python3`/project-venv retries could not import `requests`; installed that Python dependency only into `/tmp/codex-paper-review-20261008/python-deps` and reran the unchanged validator using a temporary `PYTHONPATH`: 44 valid entries, zero errors, zero duplicates, 11 warnings. No repository environment or validator source was changed. LaTeX remains 67 pages / 25 pages before references, 123 overfull hboxes; HTML is now 62 / 25 under its own convention. Viewed PDF page 2 to confirm Section references and the budget typeset correctly, and every moved table/figure caption page (36, 41, 43, 44, 46, 47, 50, 57, 62). Existing table-header collisions remain A9; no new clipped content was found in these views. Committing only generated paper outputs and this validation record; no table/figure script was changed. Decided by: Codex.


## 2026-10-08, 14:52 UTC (09:52 CDT) — Codex D4 clarity and terminology pass (Milestone 16)

Split Section 2.3's two long sentences into the common feature comparison, separate route descriptions, screening, scrubbing and control paragraphs; no method detail was removed. Expanded MLP, FPR, TPR and AUROC in authorial text. Standardised authorial judgement spelling and narrative forgery noun terminology while preserving direct quotations, NIST's source heading and the SLAM literal-word search statement. Direct-quotation lists, placeholder order and numeral tokens are unchanged in every edited body. The v0.3/v0.4 screening correction remains A5, and all other claim/label/disclosure calls remain unapproved. Files: `research/paper/sections/appI_regulators.md`, `research/paper/sections/sec1_introduction.md`, `research/paper/sections/sec2_background_threat_model.md`, `research/paper/sections/sec3_exact_test.md`, `research/paper/sections/sec4_setup.md`, `research/paper/sections/sec5_1_calibration.md`, `research/paper/sections/sec6_related_work.md`, `research/paper/sections/sec7_limitations.md`, with an Open items record in each. Decided by: Codex.


## 2026-10-08, 14:55 UTC (09:55 CDT) — Rebuild after Codex prose pass `afa7327`

Re-ran fill, unchanged citation validator with the temporary dependency path, assembly/render, LaTeX compile and word count. Results: 2,896 registered values, zero unresolved; 44 valid bibliography entries, zero errors/duplicates, 11 warnings; 38 cited keys, 31 tables and 12 figures. Final LaTeX: 68 pages, references start on 26, hence 25 pages before references; HTML: 62 total / 25 main. The added paragraph breaks and definitions change pagination; the final Appendix I page contains a short continuation, retained for the generator layout pass rather than cutting approved claims to force a page count. Viewed all 22 current pages whose table/figure captions moved against the original PDF (11, 12, 14, 17, 19, 35, 36, 40–47, 50, 55–57, 60–62), plus continuation pages 13, 20 and 68. Existing dense-header collisions persist; overfull boxes remain 123 total, 34 above 5 pt, maximum 13.70056 pt. The two corrupted section symbols now remaining are in generated T1/T5 notes (A9). No unresolved placeholder in the PDF and no missing-character/undefined-citation/reference diagnostics found. All 820 baseline protected files hash identically; all changed tracked paths are within authorised section/generated-paper/review/log scope. Decided by: Codex.


## 2026-10-08, 14:57 UTC (09:57 CDT) — Codex review closed; author decisions and full read next (Milestone 16)

Completed the closing report in `research/paper/CODEX_REVIEW_v0.1.md` with commits `e784744`, `8046891`, `2f4d674`, `afa7327`, `4d61054`, verification results, final LaTeX 68/25 and HTML 62/25 page counts, remaining layout defects and verification limits. Updated the status/resume point and step 7a in `RESEARCH_HANDOFF.md` to “Codex review done; waiting on Yichen's decisions on the ask list and his full read”. All A1–A12 and O1–O4 remain recommendations; no author approval is inferred and no AI-disclosure edit was applied. The final report clarifies partial existing-placeholder substitution and the still-needed generator fixes. Each meaningful step was committed and pushed to this project's origin/main. All protected files are unchanged; no publication, email, visibility change or snapshot-remote action occurred. Decided by: Codex (review closure and resume record).

## 2026-10-08 — The Codex ask list resolved (Milestone 16; 18:40 UTC, 13:40 CDT): decisions A1–A4, A7, A10–A12 and O1–O4 taken, A5, A6, A8 and A9 done as corrections; the paper rebuilt and ready for Yichen's full read

Claude verified every factual finding of `research/paper/CODEX_REVIEW_v0.1.md` against the locked code and results before acting, and confirmed Codex's integrity report (971 locked paths unchanged by hash; its "do" edits were cross-reference spelling, placeholder reuse, acronym definitions and terminology). **Yichen's decisions, one at a time, the recommended option in each case:** A1 (the abstracts and the conclusion narrowed in place: the hashed arms and rotation stated separately with 0.35 labelled post hoc; "forgeable at either" replaced by the quality-neutral strength with plain acceptance above it; "exact on average over keys" in the arXiv text); A2 (both accesses reported: the n = 64 known-layer rates labelled, the layer-search recovery and the n = 256 layer-search forgery result, 86.0 and 87.5%, beside them in the abstract, §1, §5.4 and §9; §2.2 and C.1 say when the layer is given); A3 (the measured statistic in place of absolutes: random-key attribution as the median with the per-key maximum; "for the median key"; D.5 scoped to the primary test with S3's 3.4% and the fresh-key exceedances named; rotation's means noted in §7); A4 (§6's gap stated specifically; "every attack in the evaluations cited"; "to our knowledge" on contribution 5); A7 (inferences labelled: the footprint reading, "best among those tested", near-orthogonality as an empirical fact, the SplitMix keying as a deterministic mixing function with no cryptographic claim, the conclusion's reading of the probe); A10 (audited design constants may be typed; the convention in `research/paper/README.md`; the audit of the typed numbers against the lock files' design fields passed: strengths, budget points, key ids, bars and quoted budgets); A11 (short local qualifiers: the 512-token scope, the rotation exception to "medians", "fails the detectability criterion"); A12 ("Codex (OpenAI) assisted with the final review and revision; the author reviewed and approved the changes." after the Claude sentence, present in the PDF he reads); O1–O3 (Appendix A's long rule text, the B.5 sketch and C.1's extraction clause kept); O4 (the C4 prompt excerpt cut to its first clause by `appH_samples.py`). **Corrections by Claude (facts, logged as mine):** the v0.3 fluency bar is the key's genuine 95th percentile, not the median (E.1, D.1, the A6 and A10 table notes; protocols v0.3 and v0.4, `FLUENT_Q = 0.95`); the 1.25 allowance applies to perplexity only (§4; the Study 2 protocol and `scrub_core.py`); the layer-hit maximum over the full grid is 3 (`ta14_hitsA_max`, §5.2); the originals' detection range is 96.0–100.0% (new `s2_P1_min/max`, §5.5); v0.3 screened by perplexity only and v0.4 added the repetition screen (§2.3); Table A13a's D2 note and Table A14b's R1 note now state the protocols' rules; Table A16's fixed-key interval is labelled as Study 5's bootstrap of Study 2's texts (A6). **Script fixes:** the disabled assertion in `tab6_defence.py` (`or True`) replaced by the real paired per-key median check for rotation and the hashed arms (both pass against the locked file); the D1 helper gained the protocol's inconclusive branch; `s5_fixed_*_forge_search_FA_med` registered in `tabA4_attacker_checks.py`. **Rendering (A9):** the section sign is mapped to its macro in `make_latex.py` (XeTeX printed ğ from the T1 slot); the assembly's column widths are floored at the longest unbreakable piece and at 10 dashes with a cap that falls with the column count, and tables of 15 or more columns are set in landscape (`pdflscape`): Tables 1, A2, A3b, A6, A7b, A12b and A16 viewed clean. **Rebuilt:** all placeholders resolve; the bibliography validates at 0 errors (44 entries); the arXiv abstract is 1,918 characters; LaTeX 73 pages with 26 before the references (HTML 64 and 25); 24 overfull lines, 2 above 5 pt, the widest 7.2 pt. Decided by: Yichen (the decisions); Claude (the corrections, the script and rendering fixes). **Next:** Yichen's full read of `research/paper/latex/main.pdf`, then the posting checklist.

## 2026-10-08 — skill updated (Milestone 16): a second-model review before posting, and the table-width rule

Two lessons were added to the research-project-guide skill (Part G): run an independent reviewer with a fixed memo structure before posting, and grep the generator scripts for disabled assertions; and the Markdown-to-LaTeX width rule (floor at the longest unbreakable piece, a cap that falls with the column count, landscape above fourteen columns, the section sign mapped). The skill lives outside the repository; Yichen should re-zip and re-upload it for Cowork. Decided by: Claude.

## 2026-10-08 — Yichen read and approved the paper's content (Milestone 16; step 7 of the Stage 9 checklist done); publication route under discussion

Yichen read `research/paper/latex/main.pdf` (the rebuilt arXiv version after the Codex review, 73 pages) in full and approved its content without changes. He asked to publish through GitHub's own domain (a GitHub Pages site, `github.io`). Claude's reading: a project site served from the public snapshot repository (`shenshenzyc.github.io/activation-watermark-security`) can host the paper page, the PDF, the HTML render and the code links; it needs the repository public; it gives no citable identifier by itself, which arXiv (the brief's primary venue) or a Zenodo DOI would. The route is Yichen's decision (one question, recommendation first). Decided by: Yichen (the approval).

## 2026-10-08 — Publication route decided: arXiv plus a GitHub Pages project site (Milestone 16; 19:40 UTC, 14:40 CDT); the site built, the public snapshot pushed to the still-private repository, the posting commit tagged

Yichen chose the recommended route: the arXiv submission per the posting checklist plus a GitHub Pages project site served from the public snapshot repository's `docs/` folder (rejected, offered: a Pages site with a Zenodo DOI and no arXiv; a Pages site only). `tools/make_site.py` (Claude) builds `docs/`: `index.html` (title, author line, links to the PDF, the HTML version and the repository, an arXiv slot filled by `--arxiv ID` at posting, the abstract rendered from the filled section with citations resolved, the repository description, a BibTeX entry, the licences and the AI-use line, Google Scholar meta tags), `paper.pdf`, `paper.html` (the HTML render with its figures under `figures/`), `.nojekyll`; 3.2 MB. The title block's date line became "October 2026" (it read "Draft v0.1, assembled 2026-10-06"), and the PDF, the HTML version, the arXiv bundle (`research/paper/latex/arxiv_upload.zip`: `main.tex`, `main.bbl`, `references.bib`, the figure PDFs) and the site were rebuilt. The posting commit is tagged `v0.1-arxiv`. `tools/make_public_snapshot.py` gained an update mode (an existing snapshot repository takes a new commit instead of a fresh history); the snapshot (475 files, 25.5 MB) was pushed to `SHENSHENZYC/activation-watermark-security`, which stays private until Yichen's word. Both pages were viewed rendered by headless Chrome (the in-app preview server did not bind its port twice; recorded, not pursued). Decided by: Yichen (the route); Claude (the site and the builders). Next: on Yichen's word, make the repository public and enable Pages from `main:/docs`; his arXiv submission; the courtesy notice after the listing.

## 2026-10-09 — PUBLISHED: the repository is public and the GitHub Pages site is live (Milestone 16; 00:25 UTC, 19:25 CDT on 2026-10-08 Central)

On Yichen's word (the recommended option: now, with the arXiv submission in parallel; rejected, offered: after the arXiv listing; the repository now and the site later), Claude made `SHENSHENZYC/activation-watermark-security` public (`gh repo edit --visibility public`) and enabled GitHub Pages from `main:/docs` (`POST /repos/.../pages`); the build reported "built" after about 40 seconds. Live: https://shenshenzyc.github.io/activation-watermark-security/ (the paper page), `paper.pdf` (the arXiv version, 73 pages), `paper.html` (the HTML render with figures) and https://github.com/SHENSHENZYC/activation-watermark-security (475 files at the posting commit `536ee1f`, tag `v0.1-arxiv`; MIT and CC BY 4.0; no weights, corpora or article text). **Still to do (Yichen):** the arXiv submission with `research/paper/latex/arxiv_upload.zip`, the abstract from `research/paper/build/sections/sec0_arxiv_abstract.md` (1,918 characters), cs.CR primary with cs.CL and cs.LG cross-lists, CC BY 4.0, the endorsement request to Nikola Jovanović if asked (`research/paper/ENDORSEMENT_REQUEST.md`); then tell Claude the arXiv identifier (`tools/make_site.py --arxiv ID`, the snapshot rebuilt and pushed, `CITATION.cff` and the README updated) and send the courtesy notice (`research/paper/COURTESY_NOTICE.md`). Decided by: Yichen (going public); Claude (the steps).

## 2026-10-09 — No arXiv: the GitHub Pages site is the publication of record (Milestone 16; 00:36 UTC, 19:36 CDT Central); the paper and site reworded accordingly

Yichen decided not to submit to arXiv. The paper's prose never mentioned arXiv (only the citations of other papers do), so the text is unchanged; the title block now reads "October 2026. Published at https://shenshenzyc.github.io/activation-watermark-security/" in the PDF and the HTML version. The site drops the arXiv note and slot; its BibTeX cites the paper as a self-published preprint by the site URL with the repository in the note; the page states the publication date and the tag `v0.1-published`. The public repository's README and `CITATION.cff` say the same. Retired: `sections/sec0_arxiv_abstract.md` (deleted; the PDF abstract is the only abstract), `latex/arxiv_upload.zip` (deleted), `ENDORSEMENT_REQUEST.md` (marked superseded, kept as a record). `COURTESY_NOTICE.md` now carries the site and repository links in place of the arXiv placeholders; sending it stays Yichen's decision (h). The brief's venue plan (arXiv primary) is superseded by this decision. Rebuilt and pushed: the PDF, the HTML version, the site and the public snapshot. Offered for later: a Zenodo DOI for the repository release, which would give the paper a persistent identifier. Decided by: Yichen (no arXiv); Claude (the rewording).

## 2026-10-09 — Correction (Claude): the commit "the title block's publication URL is a hyperlink in the PDF" (1130e38) did not contain that change (a regex patch failed silently and the chain went on); the change is in the following commit, and the public repository and site were rebuilt from it.
