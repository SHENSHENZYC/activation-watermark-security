**T6b — The keyed arms' robustness cost (D2) and quality cost (D3) beside the fixed key (Study 5; medians over 8 keys; 100 paraphrases per key and strength)**

| arm | ρ | scrub success after P-Qwen (%) [95% CI] | the fixed key's on the same prompts and keys (Study 2's texts and rule; Study 5's bootstrap) (%) [95% CI] | d: paired difference (points) [95% CI] | keys ≥ 20 points | D2 verdict | detected after paraphrase (%) | perplexity ratio to the fixed key [95% CI] | keys > 1.10 | D3 verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| context-hashed, h = 1 | 0.35 | 73.0 [68.0, 78.0] | 53.0 [38.0, 64.5] | +22.0 [+6.0, +36.5] | 5 of 8 | material robustness cost | 3.0 | 0.852 [0.790, 0.874] | 0 of 8 | immaterial |
| context-hashed, h = 4 | 0.35 | 72.0 [67.5, 76.5] | 53.0 [38.0, 64.5] | +18.0 [+7.5, +33.5] | 3 of 8 | inconclusive | 1.0 | 0.832 [0.787, 0.879] | 0 of 8 | immaterial |
| rotation (K = 8), union test | 0.35 | 70.0 (Study 2's paraphrases under the union test) | 53.0 [38.0, 64.5] | +15.0 [+9.5, +18.5] | — | immaterial | — | unchanged by construction | — | not tested |
| context-hashed, h = 1 | 0.5 | 70.5 [66.5, 74.5] | 39.5 [26.0, 48.5] | +32.0 [+21.0, +44.0] | 7 of 8 | material robustness cost | 4.0 | 0.722 [0.682, 0.799] | 0 of 8 | immaterial |
| context-hashed, h = 4 | 0.5 | 69.5 [64.5, 74.5] | 39.5 [26.0, 48.5] | +32.5 [+19.0, +45.5] | 7 of 8 | material robustness cost | 1.5 | 0.717 [0.686, 0.791] | 0 of 8 | immaterial |
| rotation (K = 8), union test | 0.5 | 52.5 (Study 2's paraphrases under the union test) | 39.5 [26.0, 48.5] | +13.0 [+8.5, +17.5] | — | immaterial | — | unchanged by construction | — | not tested |

Scrub success is Study 2's definition (not attributed and the four quality conditions pass). D2: material if the median paired difference is at least 20 points with its lower bound above zero; immaterial if the upper bound is below 20; otherwise inconclusive. D3: immaterial if the median ratio and its upper bound are below 1.10. Rotation's texts are the fixed key's own texts, so its quality is unchanged by construction and its robustness reading is the union test's loss on Study 2's paraphrases.
