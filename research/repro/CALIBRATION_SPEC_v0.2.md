# Strength calibration v0.2: do 512-token texts open a detectable and fluent window?

**Status:** spec fixed before any v0.2 run (2026-09-25). Input validation for Study 1 v0.2: tuning keys only, no claims about attacks.
**Why:** calibration v0.1 ([`CALIBRATION_REPORT_v0.1.md`](CALIBRATION_REPORT_v0.1.md)) found no ρ that is both detectable (authors' MLP AUROC ≥ 0.95) and fluent (perplexity ratio ≤ 1.25) at 256 tokens, on either model. The authors' own code generates 512 tokens (`param.yaml`, `max_new_tokens: 512`); more tokens per text give the probe more evidence at the same strength.
**Decided by:** Yichen (test 512 tokens); Claude (design). v0.1 and its results are unchanged.

## What changes from v0.1
- **Length:** 512 new tokens (min = max), for steered **and** unsteered texts. Everything else as in v0.1: Self-Recognition's sampling settings, tuning keys 9001–9004, pool T (key *i* uses prompts 100*i … 100*i+99), the per-key seed, ρ defined with the same N (the pilot's median unsteered activation norm), continuation-only features, the same detectors and the same 60/20/20 split by prompt.
- **Levels:** ρ ∈ {0.25, 0.35}, the two highest levels that were fluent at 256 tokens on both models.
- **New unsteered texts** at 512 tokens (same prompts and seeds); the perplexity ratio uses their median as the denominator.
- Implementation: `calibrate_v02.py` sets Study 1 `core`'s length constants to 512 at run time (the file is not edited) and reuses `repro_pilot.py` and `calibrate.py` unchanged.

## Operating-point rule (unchanged from v0.1, fixed before the run)
For each model, the operating point is the smallest ρ in {0.25, 0.35} with **both** the authors' MLP probe mean test AUROC ≥ 0.95 **and** median perplexity ratio ≤ 1.25. If neither qualifies, the model has no usable window at 512 tokens either, and the next step goes to Yichen.

## Also reported (descriptive)
- The same detectors applied to the **first 256 tokens** of the same 512-token texts (a within-text check of the length effect, comparable to v0.1).
- Per-key AUROCs, the other detectors, one sample text per level.

## Outputs
`research/outputs/calibration_v0.2/results_<model>.json`; texts and features in `research/repro/data/<model>/c2_*` (git-ignored).
