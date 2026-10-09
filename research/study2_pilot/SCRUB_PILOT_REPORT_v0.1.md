# Study 2 scrubbing pilot — report v0.1 (tuning keys only)

Spec: [`SCRUB_PILOT_SPEC_v0.1.md`](SCRUB_PILOT_SPEC_v0.1.md) (FIXED 2026-09-30, before any pilot text was paraphrased or edited). Results: [`../outputs/study2_pilot_v0.1/results.json`](../outputs/study2_pilot_v0.1/results.json); validation: [`../outputs/study2_pilot_v0.1/VALIDATION.json`](../outputs/study2_pilot_v0.1/VALIDATION.json). **This file is built by `make_report_pilot.py`; every number comes from those files.** Scope: tuning keys 9001–9004 only; nothing here is a result about the study keys.

## 1. Run and checks

- Validation: 6 of 6 checks passed (inputs only). The run used commit `8ba17da`; total step time 5.7 h.

| check | rule | observed | verdict |
|---|---|---|---|
| I1 contributions | r ≥ 0.99; per-token Spearman ≥ 0.8 | r = 0.9849 (slope 0.961); per-token 0.80 | **FAIL** |
| I2 edits act on the key | E-true more negative than E-rand (p < 0.01) | p = 1.4e-67; median change -0.1092 vs -0.0413 | **PASS** |
| I3 bookkeeping | exact edit counts; median drift ≤ 2% | true: True, est: True, rand: True; drift ok: True | **PASS** |
| I5 Study 2 time | ≤ 24 h | 39.7 h | **FAIL** |

Validation checks: 1_inputs pass; 2_keys_seeds pass; 3_pools pass; 5_batching pass; 4_smoke pass; 6_timing pass.

## 2. Adjustments (rules fixed in the spec)

- **A1, paraphrase prompt:** first attempts meeting the length floor: qwen 62.7%, phi 65.8% → switched to P2.
  - qwen with P2 (ρ = 0.50, 100 texts): first attempts meeting the length floor 82.0%; all conditions 74.0% vs P1 72.0% on the same texts.
  - phi with P2 (ρ = 0.50, 100 texts): first attempts meeting the length floor 90.0%; all conditions 73.0% vs P1 65.0% on the same texts.
- **A2, round size:** median reduction of the attacker's objective at 10%: 1% rounds 2.661, 2% rounds 2.558, 5% rounds 2.423 → chosen 5%.

## 3. Quality bars

- Normal range (pool A's human continuations, 95th percentile): perplexity 25.4, seq-rep-4 0.048; meaning baseline (same-prompt pairs, 95th percentile) 0.825. Attacker's pool C equivalents: perplexity 22.2, meaning 0.810. Stricter readings: the model-text 95th percentile 7.35 and the human median 12.9.

## 4. Paraphrase

Medians over the 4 tuning keys, in %; detection = S4 at p ≤ 0.01; success = undetected and all four quality conditions pass.

| method | ρ | detected before | detected after | scrub success [keys ≥ 50%] | all quality conditions | perplexity ok | seq-rep ok | length ok | meaning ok | length ratio | perplexity ratio | cosine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P-phi | 0.25 | 88.0 | 8.0 | 64.0 [3] | 68.0 | 100.0 | 94.0 | 86.0 | 82.0 | 0.90 | 2.16 | 0.91 |
| P-phi | 0.35 | 100.0 | 20.0 | 54.0 [2] | 70.0 | 96.0 | 98.0 | 80.0 | 90.0 | 0.91 | 2.25 | 0.92 |
| P-phi | 0.5 | 96.0 | 48.0 | 34.0 [2] | 66.0 | 88.0 | 100.0 | 78.0 | 84.0 | 0.88 | 1.94 | 0.91 |
| P-phi | 0.7 | 96.0 | 32.0 | 18.0 [0] | 40.0 | 80.0 | 96.0 | 82.0 | 70.0 | 0.89 | 1.58 | 0.86 |
| P-qwen | 0.25 | 88.0 | 2.0 | 72.0 [3] | 72.0 | 100.0 | 100.0 | 86.0 | 80.0 | 0.95 | 2.03 | 0.91 |
| P-qwen | 0.35 | 100.0 | 16.0 | 58.0 [2] | 74.0 | 96.0 | 100.0 | 80.0 | 84.0 | 0.93 | 2.04 | 0.91 |
| P-qwen | 0.5 | 96.0 | 24.0 | 52.0 [2] | 68.0 | 98.0 | 100.0 | 82.0 | 82.0 | 0.93 | 1.69 | 0.90 |
| P-qwen | 0.7 | 96.0 | 20.0 | 28.0 [0] | 44.0 | 82.0 | 100.0 | 72.0 | 78.0 | 0.87 | 1.46 | 0.88 |
| P-phi (first attempt) | 0.25 | 88.0 | 6.0 | 46.0 [1] | 50.0 | 94.0 | 94.0 | 70.0 | 72.0 | 0.88 | 2.28 | 0.90 |
| P-phi (first attempt) | 0.35 | 100.0 | 22.0 | 34.0 [1] | 48.0 | 90.0 | 100.0 | 66.0 | 84.0 | 0.86 | 2.32 | 0.91 |
| P-phi (first attempt) | 0.5 | 96.0 | 46.0 | 28.0 [1] | 50.0 | 94.0 | 94.0 | 60.0 | 78.0 | 0.87 | 1.94 | 0.90 |
| P-phi (first attempt) | 0.7 | 96.0 | 34.0 | 6.0 [0] | 26.0 | 68.0 | 96.0 | 62.0 | 58.0 | 0.85 | 1.69 | 0.84 |
| P-qwen (first attempt) | 0.25 | 88.0 | 4.0 | 56.0 [3] | 56.0 | 94.0 | 100.0 | 66.0 | 72.0 | 0.90 | 2.07 | 0.90 |
| P-qwen (first attempt) | 0.35 | 100.0 | 16.0 | 42.0 [2] | 52.0 | 90.0 | 100.0 | 60.0 | 76.0 | 0.90 | 2.05 | 0.90 |
| P-qwen (first attempt) | 0.5 | 96.0 | 32.0 | 24.0 [1] | 48.0 | 78.0 | 100.0 | 64.0 | 72.0 | 0.88 | 1.91 | 0.90 |
| P-qwen (first attempt) | 0.7 | 96.0 | 24.0 | 10.0 [0] | 22.0 | 70.0 | 100.0 | 58.0 | 70.0 | 0.81 | 1.69 | 0.87 |

- phi: attempts used {'1': 216, '2': 111, '3': 73}; kept attempts still failing the attacker's own check: 157; 16.8 s per original (all attempts, 500 texts).
- qwen: attempts used {'1': 230, '2': 105, '3': 65}; kept attempts still failing the attacker's own check: 130; 3.5 s per original (all attempts, 500 texts).

## 5. Edits

| arm and budget | ρ | detected before | detected after | scrub success [keys ≥ 50%] | all quality conditions | perplexity ok | seq-rep ok | length ok | meaning ok | length ratio | perplexity ratio | cosine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E-true 2% | 0.25 | 88.0 | 48.0 | 52.0 [2] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.39 | 0.99 |
| E-true 2% | 0.35 | 100.0 | 68.0 | 32.0 [2] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.39 | 0.99 |
| E-true 2% | 0.5 | 96.0 | 80.0 | 20.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.33 | 0.99 |
| E-true 2% | 0.7 | 96.0 | 78.0 | 16.0 [1] | 96.0 | 98.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.29 | 0.99 |
| E-true 5% | 0.25 | 88.0 | 8.0 | 92.0 [4] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.89 | 0.99 |
| E-true 5% | 0.35 | 100.0 | 14.0 | 86.0 [4] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.91 | 0.98 |
| E-true 5% | 0.5 | 96.0 | 42.0 | 56.0 [2] | 98.0 | 98.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.76 | 0.98 |
| E-true 5% | 0.7 | 96.0 | 46.0 | 20.0 [1] | 72.0 | 72.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.64 | 0.97 |
| E-true 10% | 0.25 | 88.0 | 0.0 | 86.0 [4] | 86.0 | 88.0 | 100.0 | 100.0 | 100.0 | 1.00 | 3.18 | 0.96 |
| E-true 10% | 0.35 | 100.0 | 0.0 | 72.0 [4] | 72.0 | 80.0 | 100.0 | 100.0 | 98.0 | 1.00 | 3.13 | 0.95 |
| E-true 10% | 0.5 | 96.0 | 6.0 | 38.0 [1] | 46.0 | 50.0 | 100.0 | 100.0 | 96.0 | 1.00 | 2.93 | 0.95 |
| E-true 10% | 0.7 | 96.0 | 12.0 | 12.0 [1] | 16.0 | 16.0 | 100.0 | 100.0 | 88.0 | 1.00 | 2.38 | 0.94 |
| E-true 20% | 0.25 | 88.0 | 0.0 | 2.0 [0] | 2.0 | 2.0 | 100.0 | 100.0 | 88.0 | 1.00 | 7.16 | 0.92 |
| E-true 20% | 0.35 | 100.0 | 0.0 | 0.0 [0] | 0.0 | 0.0 | 100.0 | 100.0 | 92.0 | 1.00 | 7.31 | 0.90 |
| E-true 20% | 0.5 | 96.0 | 0.0 | 0.0 [0] | 0.0 | 0.0 | 100.0 | 100.0 | 82.0 | 1.00 | 6.32 | 0.88 |
| E-true 20% | 0.7 | 96.0 | 0.0 | 0.0 [0] | 0.0 | 0.0 | 100.0 | 100.0 | 74.0 | 1.00 | 4.48 | 0.87 |
| E-est 2% | 0.25 | 88.0 | 72.0 | 28.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.41 | 0.99 |
| E-est 2% | 0.35 | 100.0 | 86.0 | 14.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.38 | 0.99 |
| E-est 2% | 0.5 | 96.0 | 90.0 | 10.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.34 | 0.99 |
| E-est 2% | 0.7 | 96.0 | 90.0 | 6.0 [1] | 96.0 | 96.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.26 | 0.99 |
| E-est 5% | 0.25 | 88.0 | 56.0 | 44.0 [1] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.93 | 0.98 |
| E-est 5% | 0.35 | 100.0 | 68.0 | 32.0 [1] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.82 | 0.98 |
| E-est 5% | 0.5 | 96.0 | 82.0 | 16.0 [0] | 98.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.77 | 0.98 |
| E-est 5% | 0.7 | 96.0 | 80.0 | 4.0 [1] | 74.0 | 76.0 | 100.0 | 100.0 | 98.0 | 1.00 | 1.62 | 0.97 |
| E-est 10% | 0.25 | 88.0 | 22.0 | 68.0 [4] | 86.0 | 86.0 | 100.0 | 100.0 | 100.0 | 1.00 | 3.23 | 0.96 |
| E-est 10% | 0.35 | 100.0 | 34.0 | 42.0 [1] | 70.0 | 74.0 | 100.0 | 100.0 | 96.0 | 1.00 | 3.06 | 0.96 |
| E-est 10% | 0.5 | 96.0 | 62.0 | 12.0 [1] | 64.0 | 66.0 | 100.0 | 100.0 | 98.0 | 1.00 | 2.76 | 0.96 |
| E-est 10% | 0.7 | 96.0 | 66.0 | 4.0 [1] | 16.0 | 16.0 | 100.0 | 100.0 | 94.0 | 1.00 | 2.34 | 0.94 |
| E-est 20% | 0.25 | 88.0 | 8.0 | 2.0 [0] | 2.0 | 2.0 | 100.0 | 100.0 | 86.0 | 1.00 | 7.57 | 0.91 |
| E-est 20% | 0.35 | 100.0 | 10.0 | 2.0 [0] | 2.0 | 2.0 | 100.0 | 100.0 | 86.0 | 1.00 | 6.98 | 0.90 |
| E-est 20% | 0.5 | 96.0 | 28.0 | 0.0 [0] | 0.0 | 0.0 | 100.0 | 100.0 | 86.0 | 1.00 | 6.18 | 0.89 |
| E-est 20% | 0.7 | 96.0 | 34.0 | 0.0 [0] | 0.0 | 0.0 | 100.0 | 100.0 | 82.0 | 1.00 | 4.75 | 0.87 |
| E-rand 2% | 0.25 | 88.0 | 80.0 | 20.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.34 | 1.00 |
| E-rand 2% | 0.35 | 100.0 | 96.0 | 4.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.31 | 0.99 |
| E-rand 2% | 0.5 | 96.0 | 98.0 | 2.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.27 | 0.99 |
| E-rand 2% | 0.7 | 96.0 | 94.0 | 2.0 [0] | 94.0 | 98.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.25 | 0.99 |
| E-rand 5% | 0.25 | 88.0 | 66.0 | 34.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.82 | 0.99 |
| E-rand 5% | 0.35 | 100.0 | 82.0 | 18.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.77 | 0.99 |
| E-rand 5% | 0.5 | 96.0 | 94.0 | 6.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.69 | 0.98 |
| E-rand 5% | 0.7 | 96.0 | 92.0 | 4.0 [1] | 86.0 | 86.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.59 | 0.98 |
| E-rand 10% | 0.25 | 88.0 | 34.0 | 58.0 [2] | 90.0 | 92.0 | 100.0 | 100.0 | 100.0 | 1.00 | 2.94 | 0.98 |
| E-rand 10% | 0.35 | 100.0 | 62.0 | 32.0 [1] | 80.0 | 82.0 | 100.0 | 100.0 | 100.0 | 1.00 | 2.84 | 0.96 |
| E-rand 10% | 0.5 | 96.0 | 76.0 | 12.0 [0] | 66.0 | 66.0 | 100.0 | 100.0 | 100.0 | 1.00 | 2.62 | 0.96 |
| E-rand 10% | 0.7 | 96.0 | 80.0 | 0.0 [1] | 16.0 | 16.0 | 100.0 | 100.0 | 94.0 | 1.00 | 2.37 | 0.95 |
| E-rand 20% | 0.25 | 88.0 | 12.0 | 4.0 [0] | 6.0 | 6.0 | 100.0 | 100.0 | 100.0 | 1.00 | 6.26 | 0.93 |
| E-rand 20% | 0.35 | 100.0 | 24.0 | 0.0 [0] | 0.0 | 2.0 | 100.0 | 100.0 | 96.0 | 1.00 | 6.08 | 0.92 |
| E-rand 20% | 0.5 | 96.0 | 44.0 | 0.0 [0] | 0.0 | 0.0 | 100.0 | 100.0 | 90.0 | 1.00 | 5.38 | 0.92 |
| E-rand 20% | 0.7 | 96.0 | 48.0 | 0.0 [0] | 0.0 | 0.0 | 100.0 | 100.0 | 80.0 | 1.00 | 4.29 | 0.90 |

- E-true (true key): 4.07 s per text; stalled texts 4; median re-encoding drift 2%: 0.00%, 5%: 0.00%, 10%: 0.00%, 20%: 0.00%; attacker's objective (median) 0: +2.66, 2%: +1.73, 5%: +1.06, 10%: +0.24, 20%: -0.62.
- E-est (stand-in estimate): 4.07 s per text; stalled texts 4; median re-encoding drift 2%: 0.00%, 5%: 0.00%, 10%: 0.00%, 20%: 0.00%; attacker's objective (median) 0: +0.38, 2%: -0.14, 5%: -0.60, 10%: -1.08, 20%: -1.67.
- E-rand (random edits): 2.30 s per text; stalled texts 4; median re-encoding drift 2%: 0.00%, 5%: 0.00%, 10%: 0.00%, 20%: 0.00%.

### Scrub success per key (%), all methods

| method | ρ | 9001 | 9002 | 9003 | 9004 |
|---|---|---|---|---|---|
| P-phi | 0.25 | 36.0 | 64.0 | 64.0 | 64.0 |
| P-phi | 0.35 | 16.0 | 68.0 | 40.0 | 80.0 |
| P-phi | 0.5 | 8.0 | 68.0 | 12.0 | 56.0 |
| P-phi | 0.7 | 0.0 | 40.0 | 24.0 | 12.0 |
| P-qwen | 0.25 | 36.0 | 72.0 | 72.0 | 72.0 |
| P-qwen | 0.35 | 28.0 | 80.0 | 44.0 | 72.0 |
| P-qwen | 0.5 | 20.0 | 64.0 | 40.0 | 76.0 |
| P-qwen | 0.7 | 20.0 | 36.0 | 16.0 | 48.0 |
| E-true 2% | 0.25 | 40.0 | 64.0 | 32.0 | 80.0 |
| E-true 2% | 0.35 | 12.0 | 52.0 | 8.0 | 60.0 |
| E-true 2% | 0.5 | 4.0 | 44.0 | 4.0 | 36.0 |
| E-true 2% | 0.7 | 0.0 | 80.0 | 4.0 | 28.0 |
| E-true 5% | 0.25 | 92.0 | 100.0 | 92.0 | 92.0 |
| E-true 5% | 0.35 | 76.0 | 100.0 | 60.0 | 96.0 |
| E-true 5% | 0.5 | 44.0 | 92.0 | 20.0 | 68.0 |
| E-true 5% | 0.7 | 20.0 | 92.0 | 4.0 | 20.0 |
| E-true 10% | 0.25 | 88.0 | 100.0 | 80.0 | 84.0 |
| E-true 10% | 0.35 | 68.0 | 76.0 | 80.0 | 52.0 |
| E-true 10% | 0.5 | 36.0 | 64.0 | 40.0 | 16.0 |
| E-true 10% | 0.7 | 8.0 | 64.0 | 16.0 | 4.0 |
| E-true 20% | 0.25 | 8.0 | 0.0 | 0.0 | 4.0 |
| E-true 20% | 0.35 | 0.0 | 0.0 | 0.0 | 0.0 |
| E-true 20% | 0.5 | 0.0 | 4.0 | 0.0 | 0.0 |
| E-true 20% | 0.7 | 0.0 | 12.0 | 0.0 | 0.0 |
| E-est 2% | 0.25 | 20.0 | 44.0 | 20.0 | 36.0 |
| E-est 2% | 0.35 | 12.0 | 28.0 | 0.0 | 16.0 |
| E-est 2% | 0.5 | 0.0 | 16.0 | 4.0 | 16.0 |
| E-est 2% | 0.7 | 0.0 | 60.0 | 4.0 | 8.0 |
| E-est 5% | 0.25 | 32.0 | 84.0 | 48.0 | 40.0 |
| E-est 5% | 0.35 | 12.0 | 68.0 | 20.0 | 44.0 |
| E-est 5% | 0.5 | 0.0 | 48.0 | 0.0 | 32.0 |
| E-est 5% | 0.7 | 0.0 | 80.0 | 0.0 | 8.0 |
| E-est 10% | 0.25 | 52.0 | 92.0 | 68.0 | 68.0 |
| E-est 10% | 0.35 | 20.0 | 64.0 | 40.0 | 44.0 |
| E-est 10% | 0.5 | 4.0 | 76.0 | 4.0 | 20.0 |
| E-est 10% | 0.7 | 0.0 | 76.0 | 4.0 | 4.0 |
| E-est 20% | 0.25 | 4.0 | 0.0 | 0.0 | 4.0 |
| E-est 20% | 0.35 | 4.0 | 4.0 | 0.0 | 0.0 |
| E-est 20% | 0.5 | 0.0 | 4.0 | 0.0 | 0.0 |
| E-est 20% | 0.7 | 0.0 | 20.0 | 0.0 | 0.0 |
| E-rand 2% | 0.25 | 16.0 | 24.0 | 20.0 | 20.0 |
| E-rand 2% | 0.35 | 0.0 | 12.0 | 0.0 | 8.0 |
| E-rand 2% | 0.5 | 0.0 | 12.0 | 0.0 | 4.0 |
| E-rand 2% | 0.7 | 0.0 | 32.0 | 0.0 | 4.0 |
| E-rand 5% | 0.25 | 28.0 | 40.0 | 20.0 | 48.0 |
| E-rand 5% | 0.35 | 8.0 | 28.0 | 4.0 | 40.0 |
| E-rand 5% | 0.5 | 0.0 | 20.0 | 0.0 | 12.0 |
| E-rand 5% | 0.7 | 0.0 | 64.0 | 0.0 | 8.0 |
| E-rand 10% | 0.25 | 48.0 | 80.0 | 24.0 | 68.0 |
| E-rand 10% | 0.35 | 20.0 | 52.0 | 16.0 | 44.0 |
| E-rand 10% | 0.5 | 0.0 | 44.0 | 0.0 | 24.0 |
| E-rand 10% | 0.7 | 0.0 | 68.0 | 0.0 | 0.0 |
| E-rand 20% | 0.25 | 8.0 | 0.0 | 4.0 | 4.0 |
| E-rand 20% | 0.35 | 0.0 | 12.0 | 0.0 | 0.0 |
| E-rand 20% | 0.5 | 0.0 | 8.0 | 0.0 | 0.0 |
| E-rand 20% | 0.7 | 0.0 | 8.0 | 0.0 | 0.0 |

### Stricter quality readings (scrub success, median %)

| method | ρ | human 95th pct (primary) | model-text 95th pct | human median |
|---|---|---|---|---|
| P-phi | 0.25 | 64.0 | 2.0 | 14.0 |
| P-phi | 0.35 | 54.0 | 0.0 | 14.0 |
| P-phi | 0.5 | 34.0 | 0.0 | 6.0 |
| P-phi | 0.7 | 18.0 | 8.0 | 8.0 |
| P-qwen | 0.25 | 72.0 | 4.0 | 26.0 |
| P-qwen | 0.35 | 58.0 | 0.0 | 16.0 |
| P-qwen | 0.5 | 52.0 | 6.0 | 10.0 |
| P-qwen | 0.7 | 28.0 | 8.0 | 8.0 |
| E-true 2% | 0.25 | 52.0 | 22.0 | 52.0 |
| E-true 2% | 0.35 | 32.0 | 12.0 | 32.0 |
| E-true 2% | 0.5 | 20.0 | 4.0 | 12.0 |
| E-true 2% | 0.7 | 16.0 | 10.0 | 10.0 |
| E-true 5% | 0.25 | 92.0 | 2.0 | 66.0 |
| E-true 5% | 0.35 | 86.0 | 2.0 | 38.0 |
| E-true 5% | 0.5 | 56.0 | 0.0 | 6.0 |
| E-true 5% | 0.7 | 20.0 | 2.0 | 2.0 |
| E-true 10% | 0.25 | 86.0 | 0.0 | 2.0 |
| E-true 10% | 0.35 | 72.0 | 0.0 | 4.0 |
| E-true 10% | 0.5 | 38.0 | 0.0 | 0.0 |
| E-true 10% | 0.7 | 12.0 | 0.0 | 0.0 |
| E-true 20% | 0.25 | 2.0 | 0.0 | 0.0 |
| E-true 20% | 0.35 | 0.0 | 0.0 | 0.0 |
| E-true 20% | 0.5 | 0.0 | 0.0 | 0.0 |
| E-true 20% | 0.7 | 0.0 | 0.0 | 0.0 |
| E-est 2% | 0.25 | 28.0 | 12.0 | 26.0 |
| E-est 2% | 0.35 | 14.0 | 4.0 | 14.0 |
| E-est 2% | 0.5 | 10.0 | 0.0 | 8.0 |
| E-est 2% | 0.7 | 6.0 | 4.0 | 4.0 |
| E-est 5% | 0.25 | 44.0 | 4.0 | 28.0 |
| E-est 5% | 0.35 | 32.0 | 0.0 | 22.0 |
| E-est 5% | 0.5 | 16.0 | 0.0 | 4.0 |
| E-est 5% | 0.7 | 4.0 | 0.0 | 0.0 |
| E-est 10% | 0.25 | 68.0 | 0.0 | 4.0 |
| E-est 10% | 0.35 | 42.0 | 0.0 | 0.0 |
| E-est 10% | 0.5 | 12.0 | 0.0 | 0.0 |
| E-est 10% | 0.7 | 4.0 | 0.0 | 0.0 |
| E-est 20% | 0.25 | 2.0 | 0.0 | 0.0 |
| E-est 20% | 0.35 | 2.0 | 0.0 | 0.0 |
| E-est 20% | 0.5 | 0.0 | 0.0 | 0.0 |
| E-est 20% | 0.7 | 0.0 | 0.0 | 0.0 |
| E-rand 2% | 0.25 | 20.0 | 12.0 | 18.0 |
| E-rand 2% | 0.35 | 4.0 | 2.0 | 4.0 |
| E-rand 2% | 0.5 | 2.0 | 2.0 | 2.0 |
| E-rand 2% | 0.7 | 2.0 | 0.0 | 0.0 |
| E-rand 5% | 0.25 | 34.0 | 4.0 | 22.0 |
| E-rand 5% | 0.35 | 18.0 | 0.0 | 12.0 |
| E-rand 5% | 0.5 | 6.0 | 0.0 | 2.0 |
| E-rand 5% | 0.7 | 4.0 | 2.0 | 2.0 |
| E-rand 10% | 0.25 | 58.0 | 0.0 | 8.0 |
| E-rand 10% | 0.35 | 32.0 | 0.0 | 2.0 |
| E-rand 10% | 0.5 | 12.0 | 0.0 | 2.0 |
| E-rand 10% | 0.7 | 0.0 | 0.0 | 0.0 |
| E-rand 20% | 0.25 | 4.0 | 0.0 | 0.0 |
| E-rand 20% | 0.35 | 0.0 | 0.0 | 0.0 |
| E-rand 20% | 0.5 | 0.0 | 0.0 | 0.0 |
| E-rand 20% | 0.7 | 0.0 | 0.0 | 0.0 |

## 6. Calibration after paraphrase (descriptive)

| paraphraser | texts | pooled FPR, 4 tuning keys (%) | mean per-key FPR, 1,000 fresh keys (%) | share of fresh keys > 3% | max (%) |
|---|---|---|---|---|---|
| qwen | original | 0.5 | 0.97 | 2.7% | 7.0 |
| qwen | paraphrased | 1.8 | 1.09 | 7.8% | 42.0 |
| phi | original | 0.5 | 0.97 | 2.7% | 7.0 |
| phi | paraphrased | 0.8 | 1.07 | 8.0% | 25.0 |

With 100 texts, one key's FPR moves in steps of 1 point, so the per-key spread is coarse; Study 2's binding gates use pool A's 1,000 texts.

## 7. Projected Study 2 run time (check I5)

| part | hours |
|---|---|
| paraphrase qwen | 4.3 |
| paraphrase phi | 20.0 |
| edits true | 3.6 |
| edits est | 3.6 |
| edits rand | 2.0 |
| scoring | 6.0 |
| estimate layer scales | 0.2 |
| total | 39.7 |

## 8. Samples (ρ = 0.50, the first text of keys 9001 and 9002; edits at 10%)

**Key 9001, original** (p = 0.001):

>  bring back my 'Great Indian Food Tasting'!" he says.  "I've been doing it for years, but I'm starting up again after having a baby," he adds, 'And I think I can make some wonderful food, too.' He's already thinking about an apricot pie, carrot cake, lamb curry, and more. And that sounds like fun.  For those who are interested, you may find out more about the event at http://www.cafezine.ca/2013/04/tasty-things/ and also see images of his work (and links) on facebook at www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 pm this coming Saturday, April 19th at The Cafe Zine, which is located just off St James Street near the City Centre Market. If you're not familiar with 

**P-phi** (p = 0.001):

> "I'm rejuvenating my 'Great Indian Food Tasting' experience," he announces.  "After years of hosting, I'm reviving it post-childbirth, and I'm confident I'll whip up some amazing dishes," he remarks, pondering about items like apricot pie, carrot cake, and lamb curry. It sounds like a delightful experience.  For those curious, more information about the event is available at http://www.cafezine.ca/2013/04/tasty-things/, and images along with links to his work can be found on his facebook page at www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" is scheduled for 7 pm on April 19th at The Cafe Zine, situated off St James Street near the City Centre Market. Known for their diverse tea, coff

**P-qwen** (p = 0.001):

> He calls for "my Great Indian Food Tasting"!  "For years, I’ve been hosting these events, but now I’m bringing them back after becoming a dad," he declares. "I believe I can create amazing dishes." Already, he’s planning on trying his hand at apricot pie, carrot cake, lamb curry, and more. Sounds like a lot of fun!   If anyone wants more info about the upcoming event, they can visit http://www.cafezine.ca/2013/04/tasty-things/. Plus, there’ll be some pictures of his creations available on Facebook under the page name @kpknknnn5j86.  The Indian Food Tasting is scheduled to take place at 7 PM this Saturday, April 19th, at The Cafe Zine, located in the vicinity of St James Street near the City 

**E-true 10%** (p = 0.066):

>  bring back my 'Great Indian Boy Tasting'!" he says.  "I've been doing it for years, but I'm starting to again after having a baby," he adds, 'And I think I can make some money food, too.' He's already started about an apricot t, carrot cake, blue curry, and more. And that sounds like fun.  For those who are interested, you may find that more of the restaurant at one://www.cafezine.ca/2013/04/tasty-things/ and also see http of his work (and more) on Pinterest at www.facebook.com/kpknknnn5j86.  "Indian cuisine Tasting" will be held at 7 pm this Friday Saturday, April 19th at The Cafe Zine, which is located just off St James Street near the City Centre Hotel. If you're not familiar with our, T

**E-est 10%** (p = 0.001):

>  bring back my 'Great Indian Food Tasting'!" he says.  "I've been doing it for years, but I'm starting up again after this a lot," he adds, 'And I need I can make some wonderful food, because.' He's already thinking about an apricot dish, carrot cake, lamb curry, and more. And that sounds like fun.  For those who can interested, you should find out more about the event at http://www.cafezine.ca/2013/04/tasty-things/ and if see you of his menu (and maybe) on facebook you www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 pm in coming Saturday, April 19th at The Cafe Zine, and is FREE just bring St Mary Street near the City Centre Metro. If you're not able with them, they 

**E-rand 10%** (p = 0.001):

>  bring back my 'Great Indian Food Tasting'!" he said.  "I've been doing this for years, but I'm starting again again after having a baby," he adds, 'And I think I can be some wonderful food, too.' He's already thinking about an apricot pie, a cake, lamb chops, and more. The that sounds like fun.  For those who have interested, you may find out more about the event at www://www.cafezine.ca/2013/04/tasty-things/ and www see photos of his work (and links) on facebook at www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 pm this coming Saturday, May 19th at the Cafe Zine, at is located just a St Mary Street from the City Centre Market. If you're a familiar with them, they ha

**Key 9002, original** (p = 0.179):

>  The site also allows users to ask questions about their experience with the company or government agency, such as why they are dissatisfied, how long it takes them to get an answer, and whether they will complain again in the future. - Reclamos.cl: Reclamos.cl es un sitio web que usa una herramienta para crear y publicar los calificaciones de satisfacción del consumidor chileno. La página también permite a los usuarios preguntar por su experiencia con el empresa o gobierno estatal, como por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que la compañía o el gobierno central se les olvide, y si no, ¿serán conscientes de que la compañía o el gobierno cent

**P-phi** (p = 0.646):

> Reclamos.cl es una plataforma en línea que emplea una herramienta para recopilar y difundir las evaluaciones de clientes en Chile. La sección de la página facilita a los usuarios hacer preguntas sobre sus interacciones con las empresas o entidades gubernamentales, abordando sus sentimientos de insatisfacción, la duración del proceso de respuesta y la probabilidad de que opten por denunciar nuevamente en el futuro. Esta plataforma se destaca por mostrar los hallazgos de las investigaciones de la comunidad, específicamente, las razones de su insatisfacción, la velocidad de respuesta y su conciencia sobre la negligencia de la empresa o el gobierno central. Además, la plataforma permite a los us

**P-qwen** (p = 0.495):

> The site enables users to inquire about their interactions with companies or governmental agencies, including reasons for dissatisfaction, response times, and future complaint intentions. - Complaints.cl: This website uses a tool to collect consumer satisfaction ratings in Chile. It also offers users the chance to ask about their dealings with firms or state governments, such as the causes of their discontent, the duration of waiting periods before receiving answers, and if they plan to voice complaints in the future. For this situation, Complaints.cl serves as a platform that displays the findings from user investigations within the community (specifically, the reasons for dissatisfaction, 

**E-true 10%** (p = 0.839):

>  The site also allows users to track questions asked their specific with the company or organization agency, providing as why they are dissatisfied, how long it takes them to get their answer, and whether they will be again in the future. - Reclamos.cl: Reclamos.cl is un agency web que fue una herramienta para den y publicar los calificaciones de satisfacción del consumidor chileno. La página también permite a los usuarios preguntar por su experiencia con el empresa o instit estatal, incl por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que volver compañía o el gobierno no se comprom olvide, y si en, ¿serán conscientes de que la compañía o el gobierno 

**E-est 10%** (p = 0.837):

>  The site also allows users to ask questions about their concerns with the company or government officials, share as why they are dissatisfied, how and it takes them to get what answer, and so they will complain to in the future. - Reclamos.cl: Reclamos.cl aims un sitio web que usa una herramienta para crear y publicar los calificaciones de satisfacción del consumidor chileno. The página también permite a los usuarios preguntar por su experiencia con el empresa o con estatal, como por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que deben compañía o el gobierno volver se re olvide, y si no, ¿serán conscientes de que la compañía o el gobierno ol se ol o

**E-rand 10%** (p = 0.566):

>  The site will allows for to ask questions on their pet with a company or government agency, or as why a are dissatisfied, what long it takes them to get a answer, and whether they got complain again about the future. - Reclamos.cl: Reclamos.cl es una sitio web que usa una herramienta para crear y publicar comentarios calificaciones de satisfacción del consumidor chileno. La página también permite a los usuarios preguntar por su pregunta con el sitio o gobierno estatal, como por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que la compañía o el gobierno central se repet olvide, y si la, ¿serán conscientes de que volver compañía o el gobierno central se 

## 9. Reading (inference, after the run; tuning keys only)

Values are medians over the 4 tuning keys at ρ = 0.25 / 0.35 / 0.50 / 0.70, in %. Before any scrub, S4 detects 88.0 / 100.0 / 96.0 / 96.0.

- **Paraphrase removes most of the evidence at low strength.** Detected after paraphrase: Phi 8.0 / 20.0 / 48.0 / 32.0, Qwen 2.0 / 16.0 / 24.0 / 20.0. Scrub success (undetected and all quality conditions): Phi 64.0 / 54.0 / 34.0 / 18.0, Qwen 72.0 / 58.0 / 52.0 / 28.0. Stronger watermarks survive paraphrase more often, but their paraphrases also fail the quality conditions more often.
- **Knowing the key matters for edits.** At 5% of tokens, success is 92.0 / 86.0 / 56.0 / 20.0 with the true key, 44.0 / 32.0 / 16.0 / 4.0 with the stand-in estimate (cosine about 0.04–0.33) and 34.0 / 18.0 / 6.0 / 4.0 with random edits. Random 10% edits already lower detection to 34.0 / 62.0 / 76.0 / 80.0.
- **The fluency bar is lenient for edits.** Under the primary bar (human 95th percentile), true-key 10% edits succeed at 86.0 / 72.0 / 38.0 / 12.0, but the sample for key 9001 is visibly degraded (broken words, wrong facts, a broken URL). Under the human median the same edits succeed at 2.0 / 4.0 / 0.0 / 0.0; at 5% edits, 66.0 / 38.0 / 6.0 / 2.0. Perplexity alone does not separate a 10%-edited text from fluent writing.
- **Paraphrase widens per-key calibration.** Over 1,000 fresh keys, the share with FPR above 3% rises from 2.7% (original texts) to 7.8% (Qwen paraphrases) and 8.0% (Phi); the worst key reaches 42.0% and 25.0% (100 texts, coarse). Study 2's per-key gate on 1,000 paraphrased pool A texts matters.
- **Study 2 as designed does not fit the time budget:** 39.7 h projected against 24 h, of which Phi paraphrasing is 20.0 h (batches of 4; frequent retries).

**Not established:** anything about the study keys; robustness of these readings beyond 25 texts per key and level; whether a coherence judgment would agree with the perplexity bars.
