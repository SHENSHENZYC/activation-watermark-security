# Study 5 threat check v0.1 — Route A′: gradient-averaging key recovery on the tuning keys

Date: 2026-10-02. **Status:** FIXED (approved by Yichen 2026-10-02, decision 1; the run refuses unless this status line is present and the file is committed).
Script: `research/study5_pilot/threat_check.py` (phases `validate` | `run` | `analyse`). Outputs: `research/outputs/study5_threat_v0.1/` (validation, `results.json`, `REPORT.md`). Why: the gate's single next check ([`../STUDY5_GATE_v0.1.md`](../STUDY5_GATE_v0.1.md) §1 and §5).

## 1. Question
Does an attacker with the open model recover the **fixed** steering key by averaging the exact test's own statistic (the gradient of the continuation log-likelihood with respect to an additive vector, at every layer, standardised against the attacker's own reference texts) over *n* observed watermarked texts? Study 1's Route A, the same estimator on mean activations, fails at *n* ≤ 1,024 (median cos ≤ 0.16 at every ρ).

## 2. Data (tuning keys only; no study key is touched)
- **Observed:** `research/repro/data/qwen/texts_calib_{r035,r050,r070}_k{9001..9004}.json`: 100 continuations of 256 tokens per key-level, generated under the tuning key at that ρ (calibration v0.2; already-reported inputs).
- **The attacker's reference:** the first 200 of Study 1 v0.2's pool C unwatermarked texts (`research/study1_v02/data/S_C_ref.json`); for the paired activation comparison, the first 200 rows of `S_C_ref_feats.npy`.
- **True keys:** `power_pilot.tuning_key(s, ρ)` at layer 14, used only to score estimates; the estimator never receives a key or the layer.

## 3. The attacker (Route A′)
- Per text, one forward and one backward pass with an additive zero vector at the output of **each of the 28 decoder layers**: the gradient at every layer, an array [28, 1536].
- **Estimator:** Study 1 v0.2's `attack2.route_a`, imported unchanged (z-scores against the reference with se = sd_ref · √(1/n + 1/m); the layer l̂ = argmax over layers of max |z|; the support = the 4 largest |z| at l̂; values = the mean difference on the support), fed gradient features in place of activation features. The scale is irrelevant to the cosine (unit reference norms).
- *n* ∈ {4, 16, 64, 100}: nested prefixes in file order.
- **Paired comparison, Route A:** the same estimator on activation features (`common.all_layer_means`) of the same texts, against the same 200 reference texts.
- **Descriptive:** the gradient estimate restricted to the true layer (support recovery given the layer).

## 4. Readings (pre-set before any outcome)
- Per key, level and *n*: cos(v̂, v) with the true key (irrespective of l̂), the support hit rate (of 4), whether l̂ = 14. Medians over the 4 keys.
- **The threat is real** if the median cos over the 4 tuning keys is ≥ 0.5 at some *n* ≤ 100 at ρ = 0.50 or ρ = 0.70.
- **Extend** (a v0.2 with 1,024 tuning-key texts per level, about 1.5 h of generation per level) if the median cos is < 0.5 at *n* = 100 at both levels.
- Everything else (which keys, which layers, the activation-versus-gradient contrast, ρ = 0.35) is descriptive.

## 5. Validation (inputs only, before the run)
1. Inputs present and hashed: 12 observed files of 100 texts, 2,000 pool C texts, the pool C features [2000, 28, 1536]; the tuning keys' norms (ρ · 56.90) and 4-coordinate supports.
2. The 28-hook gradient at layer 14 equals the power pilot's single-hook gradient (`text_features`) on 3 pool C texts: relative difference ≤ 1e-3 **with the model in float32**, and direction cosine ≥ 0.99 in bfloat16 (the bf16 gradients carry run-to-run noise of a few percent, recorded; first written as a bf16 relative difference ≤ 1e-3, which failed at 2–14% before any run and was redefined, logged 2026-10-02).
3. The hooks are removed: logits unchanged after a pass.
4. No spurious recovery: Route A′ with pool C texts 200–299 as "observed" and 0–199 as the reference gives |cos| ≤ 0.3 with every tuning key's direction at *n* = 100.
5. Timing: the projected run (1,200 gradient passes and the activation passes) ≤ 0.5 h.

## 6. Compute
About 1,500 forward-backward passes at about 0.2–0.3 s each (Study 3 pilot: 0.21 s) plus the batched activation passes: **10–15 minutes**. No restart needed (one 1.5B model in bf16).
