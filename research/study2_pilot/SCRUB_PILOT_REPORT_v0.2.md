# Study 2 scrubbing pilot — report v0.2 (edit component; tuning keys only)

Spec: [`SCRUB_PILOT_SPEC_v0.2.md`](SCRUB_PILOT_SPEC_v0.2.md) (FIXED 2026-10-01, before any v0.2 edit). Results: [`../outputs/study2_pilot_v0.2/results.json`](../outputs/study2_pilot_v0.2/results.json). **Built by `make_report_pilot_v02.py`; every number comes from the outputs.** v0.1's paraphrase results stand ([`SCRUB_PILOT_REPORT_v0.1.md`](SCRUB_PILOT_REPORT_v0.1.md)). Scope: tuning keys only.

## 1. Checks

Validation: 3 of 3 passed (float32 editor against float32 autograd: r = 0.99997). Run commit `f350d69`.

| check | rule | observed | verdict |
|---|---|---|---|
| I1 contributions (float32 editor) | r ≥ 0.99; per-token Spearman ≥ 0.8 | r = 0.9998 (slope 0.996); per-token 1.00 | **PASS** |
| I2 edits act on the key (0% → 5%) | E-true more negative than E-rand, p < 0.01 | p = 1.6e-67; median change -0.0702 vs -0.0220 | **PASS** |
| I3 bookkeeping | exact counts; drift ≤ 2% | {'true': True, 'est': True, 'rand': True}; drift ok: True | **PASS** |
| I5′ Study 2 time (revised scope) | ≤ 30 h | 24.3 h | **PASS** |

### Projection (I5′)

| part | value |
|---|---|
| paraphrase qwen h | 3.76 |
| qwen attempts per original P2 | 1.64 |
| paraphrase phi h | 10.14 |
| phi attempts per original P2 | 1.64 |
| edits true h | 2.31 |
| edits est h | 2.31 |
| edits rand h | 0.98 |
| scoring h | 4.61 |
| estimate layer scales h | 0.17 |
| total h | 24.28 |

## 2. Edits with the float32 editor (medians over the 4 tuning keys, %)

| arm and budget | ρ | detected before | detected after | scrub success [keys ≥ 50%] | all quality conditions | perplexity ok | seq-rep ok | length ok | meaning ok | length ratio | perplexity ratio | cosine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E-true 2% | 0.25 | 88.0 | 54.0 | 46.0 [2] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.38 | 0.99 |
| E-true 2% | 0.35 | 100.0 | 68.0 | 32.0 [2] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.38 | 0.99 |
| E-true 2% | 0.5 | 96.0 | 82.0 | 18.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.32 | 0.99 |
| E-true 2% | 0.7 | 96.0 | 78.0 | 16.0 [1] | 96.0 | 96.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.29 | 0.99 |
| E-true 5% | 0.25 | 88.0 | 6.0 | 92.0 [4] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.91 | 0.98 |
| E-true 5% | 0.35 | 100.0 | 20.0 | 80.0 [4] | 98.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.91 | 0.98 |
| E-true 5% | 0.5 | 96.0 | 44.0 | 54.0 [2] | 98.0 | 98.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.76 | 0.98 |
| E-true 5% | 0.7 | 96.0 | 44.0 | 22.0 [1] | 76.0 | 76.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.65 | 0.97 |
| E-true 10% | 0.25 | 88.0 | 0.0 | 84.0 [4] | 84.0 | 86.0 | 100.0 | 100.0 | 98.0 | 1.00 | 3.24 | 0.96 |
| E-true 10% | 0.35 | 100.0 | 0.0 | 66.0 [4] | 68.0 | 72.0 | 100.0 | 100.0 | 98.0 | 1.00 | 3.12 | 0.95 |
| E-true 10% | 0.5 | 96.0 | 8.0 | 40.0 [2] | 56.0 | 58.0 | 100.0 | 100.0 | 98.0 | 1.00 | 2.88 | 0.95 |
| E-true 10% | 0.7 | 96.0 | 10.0 | 6.0 [1] | 8.0 | 8.0 | 100.0 | 100.0 | 92.0 | 1.00 | 2.39 | 0.93 |
| E-est 2% | 0.25 | 88.0 | 64.0 | 36.0 [1] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.39 | 0.99 |
| E-est 2% | 0.35 | 100.0 | 88.0 | 12.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.39 | 0.99 |
| E-est 2% | 0.5 | 96.0 | 92.0 | 8.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.33 | 0.99 |
| E-est 2% | 0.7 | 96.0 | 92.0 | 4.0 [1] | 96.0 | 98.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.25 | 0.99 |
| E-est 5% | 0.25 | 88.0 | 50.0 | 50.0 [2] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.91 | 0.98 |
| E-est 5% | 0.35 | 100.0 | 70.0 | 30.0 [1] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.86 | 0.98 |
| E-est 5% | 0.5 | 96.0 | 84.0 | 16.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.74 | 0.98 |
| E-est 5% | 0.7 | 96.0 | 80.0 | 4.0 [1] | 76.0 | 76.0 | 100.0 | 100.0 | 98.0 | 1.00 | 1.64 | 0.97 |
| E-est 10% | 0.25 | 88.0 | 22.0 | 60.0 [4] | 86.0 | 86.0 | 100.0 | 100.0 | 100.0 | 1.00 | 3.19 | 0.96 |
| E-est 10% | 0.35 | 100.0 | 38.0 | 46.0 [2] | 74.0 | 76.0 | 100.0 | 100.0 | 100.0 | 1.00 | 3.00 | 0.95 |
| E-est 10% | 0.5 | 96.0 | 68.0 | 10.0 [1] | 58.0 | 60.0 | 100.0 | 100.0 | 98.0 | 1.00 | 2.77 | 0.95 |
| E-est 10% | 0.7 | 96.0 | 64.0 | 2.0 [1] | 16.0 | 16.0 | 100.0 | 100.0 | 96.0 | 1.00 | 2.42 | 0.95 |
| E-rand 2% | 0.25 | 88.0 | 76.0 | 24.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.32 | 1.00 |
| E-rand 2% | 0.35 | 100.0 | 94.0 | 6.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.31 | 1.00 |
| E-rand 2% | 0.5 | 96.0 | 96.0 | 4.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.29 | 0.99 |
| E-rand 2% | 0.7 | 96.0 | 92.0 | 8.0 [0] | 96.0 | 96.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.25 | 0.99 |
| E-rand 5% | 0.25 | 88.0 | 64.0 | 36.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.77 | 0.99 |
| E-rand 5% | 0.35 | 100.0 | 90.0 | 10.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.77 | 0.99 |
| E-rand 5% | 0.5 | 96.0 | 92.0 | 8.0 [0] | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.65 | 0.98 |
| E-rand 5% | 0.7 | 96.0 | 92.0 | 4.0 [1] | 72.0 | 72.0 | 100.0 | 100.0 | 100.0 | 1.00 | 1.58 | 0.98 |
| E-rand 10% | 0.25 | 88.0 | 46.0 | 48.0 [2] | 94.0 | 94.0 | 100.0 | 100.0 | 100.0 | 1.00 | 2.95 | 0.97 |
| E-rand 10% | 0.35 | 100.0 | 64.0 | 30.0 [1] | 88.0 | 90.0 | 100.0 | 100.0 | 100.0 | 1.00 | 2.76 | 0.97 |
| E-rand 10% | 0.5 | 96.0 | 82.0 | 12.0 [0] | 76.0 | 76.0 | 100.0 | 100.0 | 98.0 | 1.00 | 2.60 | 0.96 |
| E-rand 10% | 0.7 | 96.0 | 76.0 | 0.0 [1] | 14.0 | 14.0 | 100.0 | 100.0 | 100.0 | 1.00 | 2.29 | 0.95 |

- E-true: 2.60 s per text; peak 9.1 GB; stalled 1; attacker's objective (median) 0: +2.66, 2%: +1.71, 5%: +1.14, 10%: +0.35.
- E-est: 2.59 s per text; peak 9.1 GB; stalled 1; attacker's objective (median) 0: +0.36, 2%: -0.12, 5%: -0.59, 10%: -0.94.
- E-rand: 1.10 s per text; peak 9.1 GB; stalled 1.

## 3. Float32 editor (v0.2) vs bfloat16 editor (v0.1), same budgets: scrub success / detected after (%)

| method | ρ | v0.2 success | v0.1 success | v0.2 detected after | v0.1 detected after |
|---|---|---|---|---|---|
| E-true 2% | 0.25 | 46.0 | 52.0 | 54.0 | 48.0 |
| E-true 2% | 0.35 | 32.0 | 32.0 | 68.0 | 68.0 |
| E-true 2% | 0.5 | 18.0 | 20.0 | 82.0 | 80.0 |
| E-true 2% | 0.7 | 16.0 | 16.0 | 78.0 | 78.0 |
| E-true 5% | 0.25 | 92.0 | 92.0 | 6.0 | 8.0 |
| E-true 5% | 0.35 | 80.0 | 86.0 | 20.0 | 14.0 |
| E-true 5% | 0.5 | 54.0 | 56.0 | 44.0 | 42.0 |
| E-true 5% | 0.7 | 22.0 | 20.0 | 44.0 | 46.0 |
| E-true 10% | 0.25 | 84.0 | 86.0 | 0.0 | 0.0 |
| E-true 10% | 0.35 | 66.0 | 72.0 | 0.0 | 0.0 |
| E-true 10% | 0.5 | 40.0 | 38.0 | 8.0 | 6.0 |
| E-true 10% | 0.7 | 6.0 | 12.0 | 10.0 | 12.0 |
| E-est 2% | 0.25 | 36.0 | 28.0 | 64.0 | 72.0 |
| E-est 2% | 0.35 | 12.0 | 14.0 | 88.0 | 86.0 |
| E-est 2% | 0.5 | 8.0 | 10.0 | 92.0 | 90.0 |
| E-est 2% | 0.7 | 4.0 | 6.0 | 92.0 | 90.0 |
| E-est 5% | 0.25 | 50.0 | 44.0 | 50.0 | 56.0 |
| E-est 5% | 0.35 | 30.0 | 32.0 | 70.0 | 68.0 |
| E-est 5% | 0.5 | 16.0 | 16.0 | 84.0 | 82.0 |
| E-est 5% | 0.7 | 4.0 | 4.0 | 80.0 | 80.0 |
| E-est 10% | 0.25 | 60.0 | 68.0 | 22.0 | 22.0 |
| E-est 10% | 0.35 | 46.0 | 42.0 | 38.0 | 34.0 |
| E-est 10% | 0.5 | 10.0 | 12.0 | 68.0 | 62.0 |
| E-est 10% | 0.7 | 2.0 | 4.0 | 64.0 | 66.0 |
| E-rand 2% | 0.25 | 24.0 | 20.0 | 76.0 | 80.0 |
| E-rand 2% | 0.35 | 6.0 | 4.0 | 94.0 | 96.0 |
| E-rand 2% | 0.5 | 4.0 | 2.0 | 96.0 | 98.0 |
| E-rand 2% | 0.7 | 8.0 | 2.0 | 92.0 | 94.0 |
| E-rand 5% | 0.25 | 36.0 | 34.0 | 64.0 | 66.0 |
| E-rand 5% | 0.35 | 10.0 | 18.0 | 90.0 | 82.0 |
| E-rand 5% | 0.5 | 8.0 | 6.0 | 92.0 | 94.0 |
| E-rand 5% | 0.7 | 4.0 | 4.0 | 92.0 | 92.0 |
| E-rand 10% | 0.25 | 48.0 | 58.0 | 46.0 | 34.0 |
| E-rand 10% | 0.35 | 30.0 | 32.0 | 64.0 | 62.0 |
| E-rand 10% | 0.5 | 12.0 | 12.0 | 82.0 | 76.0 |
| E-rand 10% | 0.7 | 0.0 | 0.0 | 76.0 | 80.0 |

v0.1's E-rand used a different random stream and 2% rounds, so its rows differ by chance as well.

## 4. Scrub success per key (%)

| method | ρ | 9001 | 9002 | 9003 | 9004 |
|---|---|---|---|---|---|
| E-true 2% | 0.25 | 36.0 | 56.0 | 36.0 | 84.0 |
| E-true 2% | 0.35 | 12.0 | 52.0 | 8.0 | 52.0 |
| E-true 2% | 0.5 | 0.0 | 32.0 | 4.0 | 44.0 |
| E-true 2% | 0.7 | 0.0 | 84.0 | 4.0 | 28.0 |
| E-true 5% | 0.25 | 88.0 | 96.0 | 88.0 | 96.0 |
| E-true 5% | 0.35 | 60.0 | 96.0 | 64.0 | 96.0 |
| E-true 5% | 0.5 | 44.0 | 92.0 | 16.0 | 64.0 |
| E-true 5% | 0.7 | 20.0 | 92.0 | 8.0 | 24.0 |
| E-true 10% | 0.25 | 88.0 | 88.0 | 76.0 | 80.0 |
| E-true 10% | 0.35 | 64.0 | 72.0 | 68.0 | 60.0 |
| E-true 10% | 0.5 | 28.0 | 68.0 | 52.0 | 16.0 |
| E-true 10% | 0.7 | 8.0 | 76.0 | 4.0 | 0.0 |
| E-est 2% | 0.25 | 16.0 | 56.0 | 28.0 | 44.0 |
| E-est 2% | 0.35 | 8.0 | 36.0 | 0.0 | 16.0 |
| E-est 2% | 0.5 | 0.0 | 20.0 | 4.0 | 12.0 |
| E-est 2% | 0.7 | 0.0 | 52.0 | 0.0 | 8.0 |
| E-est 5% | 0.25 | 32.0 | 84.0 | 40.0 | 60.0 |
| E-est 5% | 0.35 | 12.0 | 60.0 | 16.0 | 44.0 |
| E-est 5% | 0.5 | 0.0 | 44.0 | 4.0 | 28.0 |
| E-est 5% | 0.7 | 0.0 | 80.0 | 4.0 | 4.0 |
| E-est 10% | 0.25 | 56.0 | 88.0 | 64.0 | 56.0 |
| E-est 10% | 0.35 | 24.0 | 76.0 | 36.0 | 56.0 |
| E-est 10% | 0.5 | 4.0 | 76.0 | 0.0 | 16.0 |
| E-est 10% | 0.7 | 0.0 | 68.0 | 4.0 | 0.0 |
| E-rand 2% | 0.25 | 12.0 | 32.0 | 20.0 | 28.0 |
| E-rand 2% | 0.35 | 4.0 | 8.0 | 0.0 | 8.0 |
| E-rand 2% | 0.5 | 0.0 | 8.0 | 0.0 | 12.0 |
| E-rand 2% | 0.7 | 0.0 | 36.0 | 0.0 | 16.0 |
| E-rand 5% | 0.25 | 24.0 | 48.0 | 28.0 | 44.0 |
| E-rand 5% | 0.35 | 8.0 | 12.0 | 4.0 | 20.0 |
| E-rand 5% | 0.5 | 0.0 | 16.0 | 0.0 | 16.0 |
| E-rand 5% | 0.7 | 0.0 | 56.0 | 0.0 | 8.0 |
| E-rand 10% | 0.25 | 44.0 | 72.0 | 32.0 | 52.0 |
| E-rand 10% | 0.35 | 12.0 | 48.0 | 12.0 | 52.0 |
| E-rand 10% | 0.5 | 4.0 | 32.0 | 0.0 | 20.0 |
| E-rand 10% | 0.7 | 0.0 | 64.0 | 0.0 | 0.0 |

## 5. Stricter quality readings (scrub success, median %)

| method | ρ | human 95th pct (primary) | model-text 95th pct | human median |
|---|---|---|---|---|
| E-true 2% | 0.25 | 46.0 | 20.0 | 46.0 |
| E-true 2% | 0.35 | 32.0 | 12.0 | 30.0 |
| E-true 2% | 0.5 | 18.0 | 4.0 | 14.0 |
| E-true 2% | 0.7 | 16.0 | 14.0 | 14.0 |
| E-true 5% | 0.25 | 92.0 | 0.0 | 66.0 |
| E-true 5% | 0.35 | 80.0 | 2.0 | 36.0 |
| E-true 5% | 0.5 | 54.0 | 0.0 | 6.0 |
| E-true 5% | 0.7 | 22.0 | 4.0 | 4.0 |
| E-true 10% | 0.25 | 84.0 | 0.0 | 2.0 |
| E-true 10% | 0.35 | 66.0 | 0.0 | 2.0 |
| E-true 10% | 0.5 | 40.0 | 0.0 | 2.0 |
| E-true 10% | 0.7 | 6.0 | 0.0 | 0.0 |
| E-est 2% | 0.25 | 36.0 | 12.0 | 34.0 |
| E-est 2% | 0.35 | 12.0 | 4.0 | 12.0 |
| E-est 2% | 0.5 | 8.0 | 4.0 | 6.0 |
| E-est 2% | 0.7 | 4.0 | 4.0 | 4.0 |
| E-est 5% | 0.25 | 50.0 | 4.0 | 36.0 |
| E-est 5% | 0.35 | 30.0 | 2.0 | 16.0 |
| E-est 5% | 0.5 | 16.0 | 0.0 | 4.0 |
| E-est 5% | 0.7 | 4.0 | 0.0 | 0.0 |
| E-est 10% | 0.25 | 60.0 | 0.0 | 8.0 |
| E-est 10% | 0.35 | 46.0 | 0.0 | 0.0 |
| E-est 10% | 0.5 | 10.0 | 0.0 | 0.0 |
| E-est 10% | 0.7 | 2.0 | 0.0 | 0.0 |
| E-rand 2% | 0.25 | 24.0 | 12.0 | 24.0 |
| E-rand 2% | 0.35 | 6.0 | 4.0 | 6.0 |
| E-rand 2% | 0.5 | 4.0 | 4.0 | 4.0 |
| E-rand 2% | 0.7 | 8.0 | 8.0 | 6.0 |
| E-rand 5% | 0.25 | 36.0 | 6.0 | 28.0 |
| E-rand 5% | 0.35 | 10.0 | 0.0 | 6.0 |
| E-rand 5% | 0.5 | 8.0 | 0.0 | 4.0 |
| E-rand 5% | 0.7 | 4.0 | 0.0 | 0.0 |
| E-rand 10% | 0.25 | 48.0 | 0.0 | 10.0 |
| E-rand 10% | 0.35 | 30.0 | 0.0 | 2.0 |
| E-rand 10% | 0.5 | 12.0 | 0.0 | 0.0 |
| E-rand 10% | 0.7 | 0.0 | 0.0 | 0.0 |

## 6. Samples (ρ = 0.50, the first text of keys 9001 and 9002)

**Key 9001, original** (p = 0.001):

>  bring back my 'Great Indian Food Tasting'!" he says.  "I've been doing it for years, but I'm starting up again after having a baby," he adds, 'And I think I can make some wonderful food, too.' He's already thinking about an apricot pie, carrot cake, lamb curry, and more. And that sounds like fun.  For those who are interested, you may find out more about the event at http://www.cafezine.ca/2013/04/tasty-things/ and also see images of his work (and links) on facebook at www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 pm this coming Saturday, April 19th at The Cafe Zine, which is located just off St James Street near the City Centre Market. If you're not familiar with 

**E-true 5%** (p = 0.001):

>  bring back my 'Great Indian Boy Tasting'!" he says.  "I've been doing it for years, but I'm starting now again after having a baby," he adds, 'And I think I can make some money food, too.' He's already sold about an apricot pie, carrot cake, lamb curry, and more. And that sounds like fun.  For those who are interested, you may find that more of the restaurant at http://www.cafezine.ca/2013/04/tasty-things/ and also see images of his work (and links) on Pinterest at www.facebook.com/kpknknnn5j86.  "Indian cuisine Tasting" will be held at 7 pm this coming Saturday, April 19th at The Cafe Zine, which is located just off St James Street near the City Centre Market. If you're not familiar with Z

**E-true 10%** (p = 0.042):

>  bring back my 'Great Indian Boy Tasting'!" he says.  "I've been doing it for years, but I'm starting now again after having a baby," he adds, 'And I think I can make some money food, too.' He's already sold about an apricot every, carrot cake, blue curry, and more. And that sounds like fun.  For those who are interested, you may find that more of the restaurant at the://www.cafezine.ca/2013/04/tasty-things/ and also see his of his work (and links) on Pinterest at www.facebook.com/kpknknnn5j86.  "Indian cuisine Tasting" by be held at 7 pm this coming Saturday, April 19th at The Cafe Zine, which is located just off St James Street near the City Centre Station. If you're not familiar with Z, w

**E-est 5%** (p = 0.001):

>  bring back my 'Great Indian Food Tasting'!" he says.  "I've been doing it for years, but I'm starting up again after having a baby," he adds, 'And I need I can make some wonderful food, because.' He's already thinking about an apricot dish, carrot cake, lamb curry, and more. And that sounds like fun.  For those who are interested, you should find out more about the event at http://www.cafezine.ca/2013/04/tasty-things/ and also see images of his menu (and maybe) on facebook at www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 pm this coming Saturday, April 19th at The Cafe Zine, and is a just off St James Street near the City Centre Market. If you're not able with them,

**E-est 10%** (p = 0.001):

>  bring back my 'Great Indian Food Tasting'!" he says.  "I've been doing it for years, but I'm starting up again after this a baby," he adds, 'And I need I can make some wonderful food, because.' He's already thinking about an apricot dish, carrot salad, lamb curry, and more. And that sounds like fun.  For those who can interested, you should find out more about the event at http://www.cafezine.ca/2013/04/tasty-things/ and if see images of his menu (and maybe) on facebook at www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 pm at coming Saturday, April 19th at The Cafe Zine, and is a just under St James Street near the new Centre Market. If you're not able with them, the

**E-rand 5%** (p = 0.001):

>  bring back my 'Great Depression Food Tasting'!"    says.  "I've been doing it for years, but I'm starting up again after having a baby," he adds, 'And I think it can make an wonderful food, too.' He's already thinking about an apricot pie, carrot cake, lamb curry, and an. And that sounds like fun.  For those who are interested, you may find out more about the event at http://www.cafezine.ca/2013/04/tasty-things/ and also see this of his work (and links) on facebook at www.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 pm this coming Saturday, April 19th at The Cafe Zine, which is located just off St James Street near the City Centre Market. If you're not familiar with t

**E-rand 10%** (p = 0.001):

>  bring them my 'Great Depression Food Tasting'!"    says.  "I've been doing it for years, so I'm starting up a after having a baby," he adds, 'And I think it can make an wonderful food, and.' He's already thinking about an apricot pie, carrot cake, lamb curry, and an. And that sounds like fun.  For those who are interested, you may be out more about the event at www://www.cafezine.ca/2013/04/tasty-things/ and also see this of his talk (and links) on facebook at https.facebook.com/kpknknnn5j86.  "Indian Food Tasting" will be held at 7 p this coming Saturday, April 19th at The Cafe Zine, which is located just a St James Street near the City Centre and. If you're not familiar with them, they ha

**Key 9002, original** (p = 0.179):

>  The site also allows users to ask questions about their experience with the company or government agency, such as why they are dissatisfied, how long it takes them to get an answer, and whether they will complain again in the future. - Reclamos.cl: Reclamos.cl es un sitio web que usa una herramienta para crear y publicar los calificaciones de satisfacción del consumidor chileno. La página también permite a los usuarios preguntar por su experiencia con el empresa o gobierno estatal, como por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que la compañía o el gobierno central se les olvide, y si no, ¿serán conscientes de que la compañía o el gobierno cent

**E-true 5%** (p = 0.633):

>  The site also allows users to ask questions about their specific with the company or organization agency, providing as why they are dissatisfied, how long it takes them to get the answer, and whether they will return again in the future. - Reclamos.cl: Reclamos.cl operates un sitio web que fue una herramienta popular crear y publicar los calificaciones de satisfacción del consumidor chileno. La página también permite a los usuarios preguntar por su experiencia con el empresa o gobierno estatal, como por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que la compañía o el gobierno no se les olvide, y si no, ¿serán conscientes de que la compañía o el gobie

**E-true 10%** (p = 0.853):

>  The site also allows users to track questions about their specific with the company or organization agency, providing as why they are dissatisfied, how long it takes them to get the answer, and whether they will return again in the future. - Reclamos.cl: Reclamos.cl operates un as web que fue una herramienta popular crear y publicar los calificaciones de satisfacción del consumidor chileno. La página también permite a los usuarios preguntar por su servicio con el empresa o organiz estatal, incl por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que repet compañía o el gobierno no se les olvide, y si no, ¿serán conscientes de que no compañía o el gobiern

**E-est 5%** (p = 0.393):

>  The site also allows users to ask questions about their concerns with the company or government officials, receive as pollution they are dissatisfied, how long it takes them to get an answer, and whether they will complain again in the future. - Reclamos.cl: Reclamos.cl aims un sitio web que usa una herramienta para crear y publicar los calificaciones de satisfacción del consumidor chileno. The página también permite a los usuarios preguntar por su experiencia con el comerc o gobierno estatal, como por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que la compañía o el gobierno no se les olvide, y si reg, ¿serán conscientes de que la compañía o el gobie

**E-est 10%** (p = 0.692):

>  The site also allows users to ask questions about their concerns with the company or government officials, receive as pollution they are dissatisfied, etc long it takes them to resolve an answer, and whether they will be again if the future. - Reclamos.cl: Reclamos.cl aims un sitio web que usa tecnología herramienta para crear y publicar los calificaciones de satisfacción del consumidor chileno. The página también permite a los usuarios preguntar por su experiencia con el comerc o con estatal, como tiempo qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que la compañía o el gobierno no se les olvide, y si reg, ¿serán conscientes de que la compañía o el go

**E-rand 5%** (p = 0.051):

>  The site also allows users to ask questions and their experience with the company or other agency, such as why they are dissatisfied, how long it will them to get the answer, and whether they have complain again in the future. - Reclamos.cl: Reclamos.cl es un sitio web en usa c herramienta para crear y publicar los calificaciones de satisfacción del consumidor chileno. La página también permite a los usuarios preguntar por su experiencia con el empresa o gobierno estatal, como por qué están descontentos, cómo larga tarda en responderles y si estarán conscientes de que la compañía o el gobierno central se les olvide, y si van, ¿serán conscientes de que la compañía o el gobierno central no le

**E-rand 10%** (p = 0.215):

>  The site also serves users to ask questions and their experience with the program or other agency, such as what they are dissatisfied, how long it will them to get the answer, and whether they have complain again in the future. - Reclamos.cl: Reclamos.cl es un sitio web en usa c herramienta para la y publicar los calificaciones de satisfacción del consumidor chileno. It página también permite a los usuarios preguntar por su experiencia con la empresa o otras estatal, como por qué están descontentos, cómo larga tarda para responderles y si estarán conscientes de que la compañía o el gobierno volver se les olvide, y si van, ¿serán conscientes de que la compañía o el gobierno central no les ol
