# Study 5 defence pilot v0.1 — the keyed scheme's machinery on the tuning keys

Date: 2026-10-02. **Status:** FIXED (approved by Yichen 2026-10-02, decision 7; the run refuses unless this status line is present and the spec and code are committed).
Script: `research/study5_pilot/defence_pilot.py` (phases `validate` | `run` | `analyse`); machinery `keyed_core.py`. Outputs: `research/outputs/study5_pilot_v0.1/` (`VALIDATION.json`, `results.json`, `REPORT.md`). Decisions 1–6 of 2026-10-02 (`DECISION_LOG.md`).

## 1. Purpose
Prove the three new pieces of machinery before the Study 5 protocol is fixed, and read (without rules) the keyed arms' detection, quality, stealability and paraphrase robustness on the tuning keys: (i) keyed generation with a stateful hook; (ii) the per-position exact test with secret resampling; (iii) the per-context attacker. Also a code test of the rotation machinery (union test, clustering attacker) with K = 4 tuning keys.

## 2. The schemes (as the protocol will define them)
- **Fixed (h = 0):** Study 1's scheme (`core.make_key`, scaled to ρ · 56.90, added at every position, prompt included).
- **Context-hashed (h ∈ {1, 4}):** at continuation position t ≥ h (0-based), the key is a 4-sparse unit vector from a keyed PRF of the secret and the previous h token ids (splitmix64 mixing; support of 4 distinct coordinates; values uniform in [−1, 1), unit-normalised), scaled to ρ · 56.90. Positions t < h and the prompt are not steered. Decoding and sampling settings are Study 1's.
- **Detector:** per-position gradients of the continuation log-likelihood with respect to an additive vector at layer 14 (one backward pass), standardised per dimension with pooled position statistics of the owner's reference texts (pool F); S(x, m) = Σ_t ⟨x_t, v_m(c_t)⟩ over positions with a complete context; p = rank of S(x, secret) among 999 public null secrets (seed 20261002). For h = 0 the same form with the 999 public null keys.
- **Rotation:** one of K fixed keys per text; the union statistic U = max_k ⟨x, v_k⟩ on S4's transform; nulls = 999 disjoint groups of K public keys.

## 3. Data (tuning keys 9001–9004; no study key)
- Prompts: pool T's 100 prompts per tuning key (the calibration's), pool B's first 100 (observed texts), pool D's first 20 (forgeries and controls). Owner's reference pool F (200); the attacker's reference pool C (first 200) and its scale (`S_C_ref_norms`); pool A (1,000 unwatermarked texts) for calibration.
- Fixed-key comparators: the calibration texts `texts_calib_{r035,r050}_k900x.json` (same pool T prompts).
- Bars: Study 2's locked `bars.json` (owner A, attacker C).
- Secrets: the tuning key seeds; the validation-only secret 0; random-secret controls 5001–5004. Generation seeds 7,000,000 + …, disjoint from every earlier study.

## 4. Validation (inputs only; before the run)
1. Inputs present and hashed.
2. The PRF and the test on synthetic data: null p-values uniform on the 1/1000 grid (KS p > 0.01); a planted signal is detected (> 90%).
3. **I1 reproduction:** the hook in fixed mode reproduces `core.generate` token for token on 16 prompts (key 9001, ρ = 0.50, the calibration's seed); agreement with the stored calibration texts reported.
4. **I2 structure:** on 8 prompts with the validation secret, h = 1 and h = 4, the keys used during generation equal the keys the detector re-derives from the output ids at every steered position (the generator steers positions h..254: the last sampled token is never fed back, so position 255 has a detector key but no generation key; its gradient is zero); the tokenisation round trip (generated ids versus the detector's re-encoding) is reported.
5. The hook with zero scale reproduces unsteered generation; with ρ = 0.50 it changes the texts; after removal, unsteered generation is reproduced.
6. Reference position statistics (owner: pool F; attacker: pool C) are computed and saved.
7. The sum of the per-position gradients equals the summed gradient (`text_features`): relative difference ≤ 1e-3 in float32; cosine ≥ 0.99 in bfloat16.
8. **I3 calibration:** on 1,000 pool A texts, the keyed test's FPR at p ≤ 0.01 is within [0.3, 2.5]% for h = 1 and h = 4 with the validation secret and each tuning secret; the per-position fixed form likewise for the tuning directions.
9. **I5 timing:** the study (decision 3's scope) projected at most 30 h from the measured generation and feature rates and Study 2's paraphrase rate (4.2 s per original); the pre-set fallbacks' projections recorded.

## 5. Run (per arm h ∈ {1, 4} and tuning key; refuses unless FIXED)
- Genuine texts: 100 at ρ = 0.50 and 100 at ρ = 0.35 (pool T prompts); observed texts: 100 at ρ = 0.50 (pool B prompts); per-position features of all; p-values under the owner's keyed test.
- Quality: perplexity given the prompt and seq-rep-4 of the genuine texts and of the fixed-key calibration texts on the same prompts.
- Attacker: contexts seen at least c_min = 16 times among the observed texts; estimates at n ∈ {16, 64, 100}; count-weighted cosine with the true keys, coverage of the genuine texts' positions, the number of contexts.
- Forgeries: 20 texts steered by the n = 100 table; acceptance under the owner's test; fluency against the arm's genuine 95th percentiles (FA). Random-secret control: 20 texts with a control secret, scored under the true secret.
- Paraphrase: P-Qwen with the attacker's self-check (Study 2's §4.1, pool C bars) on the first 50 genuine texts at ρ = 0.50; the kept paraphrases scored under the keyed test and Study 2's four quality conditions (owner's pool A bars); success = not detected and all four pass.
- Rotation code test (K = 4, ρ = 0.50, the calibration texts' summed gradients from the threat check): union-test detection and FPR; the naive and the clustering attacker at n ∈ {16, 64, 100, 400}.

## 6. Readings (no rules; descriptive)
Detection per arm and strength; quality ratios; attacker cosine and coverage against n; forgery FA and control acceptance; paraphrase success, detection after paraphrase and quality pass, beside the fixed key's P-Qwen success at ρ = 0.50 on the tuning keys (Study 2 pilot); the rotation test; the timing projection.

## 7. Compute
About 2,000 keyed generations (about 35 min), about 2,500 feature passes (about 12 min), 400 paraphrases with retries (about 30 min), quality and scoring (about 10 min): **about 1.5–2 h**. One 1.5B model at a time; no restart needed.
