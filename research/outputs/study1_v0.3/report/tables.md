## Table 1 — Pre-registered rules vs observed (protocol §7)

Integrity check (§3; reloaded v0.2 probes re-score v0.2's oracle texts within 0.0001): **PASS** (largest difference 0, 24 key-levels).

| ρ | Oracle FA (ceiling) | 50% of oracle | Random-key FA [95% CI] | F1 Route A | F1 Route B | F3 fluent generic steering suffices |
|---|---|---|---|---|---|---|
| 0.35 | 29.0% | 14.5% | 1.5% [0.0, 4.0] | inconclusive | practical (n=256) | no |
| 0.5 | 81.0% | 40.5% | 11.0% [6.0, 15.0] | inconclusive | inconclusive | no |
| 0.7 | 95.0% | 47.5% | 47.5% [25.0, 58.0] | inconclusive | inconclusive | yes |

F1 practical: at some n, median FA ≥ 50% of the oracle's median FA and its lower 95% bound > the random-key FA's upper 95% bound. Not practical: at both n, the upper 95% bound < 50% of the oracle's median FA. Otherwise inconclusive.

## Table 2 — Fluent acceptance (FA) and plain acceptance at the owner's 1%-FPR threshold (median over 8 keys, % [95% cluster-bootstrap CI]); median perplexity ratio to the key-level's oracle texts

| ρ | measure | Oracle | Random key | A n=64 | A n=256 | B n=64 | B n=256 |
|---|---|---|---|---|---|---|---|
| 0.35 | FA | 29.0 [15.0, 49.0] | 1.5 [0.0, 4.0] | 4.5 [2.0, 18.5] | 7.5 [2.5, 14.5] | 16.0 [2.5, 27.5] | 15.0 [6.5, 42.0] |
| | accepted | 32.0 | 1.5 | 9.5 | 7.5 | 20.5 | 19.0 |
| | fluent share | 95.0 | 94.5 | 98.0 | 99.5 | 80.0 | 79.5 |
| | ppl ratio | 1.00 | 1.02 | 0.93 | 0.91 | 1.03 | 1.16 |
| 0.5 | FA | 81.0 [68.5, 89.5] | 11.0 [6.0, 15.0] | 15.5 [4.5, 42.0] | 15.0 [5.5, 32.0] | 37.0 [15.5, 53.0] | 29.0 [11.0, 55.0] |
| | accepted | 86.0 | 13.0 | 21.0 | 20.5 | 58.5 | 62.0 |
| | fluent share | 95.0 | 92.5 | 100.0 | 98.5 | 71.5 | 67.5 |
| | ppl ratio | 1.00 | 1.02 | 0.82 | 0.82 | 0.99 | 1.01 |
| 0.7 | FA | 95.0 [93.0, 96.5] | 47.5 [25.0, 58.0] | 62.5 [23.5, 77.0] | 70.5 [58.0, 86.5] | 69.0 [49.5, 83.5] | 69.0 [56.5, 86.0] |
| | accepted | 100.0 | 55.5 | 75.5 | 83.0 | 94.0 | 95.0 |
| | fluent share | 95.0 | 91.5 | 97.0 | 100.0 | 75.0 | 80.0 |
| | ppl ratio | 1.00 | 1.00 | 0.53 | 0.63 | 0.90 | 0.71 |

## Table 3 — v0.2's forgeries (no fluency check) re-scored under FA, beside v0.3's (median over 8 keys, %)

| ρ | Route | n | v0.2 accepted | v0.2 FA | v0.3 accepted | v0.3 FA |
|---|---|---|---|---|---|---|
| 0.35 | A | 64 | 11.0 | 7.0 | 9.5 | 4.5 |
| 0.35 | A | 256 | 3.5 | 3.0 | 7.5 | 7.5 |
| 0.35 | B | 64 | 42.5 | 3.5 | 20.5 | 16.0 |
| 0.35 | B | 256 | 56.0 | 11.0 | 19.0 | 15.0 |
| 0.5 | A | 64 | 23.0 | 22.5 | 21.0 | 15.5 |
| 0.5 | A | 256 | 20.0 | 14.0 | 20.5 | 15.0 |
| 0.5 | B | 64 | 99.0 | 8.0 | 58.5 | 37.0 |
| 0.5 | B | 256 | 99.5 | 5.0 | 62.0 | 29.0 |
| 0.7 | A | 64 | 80.5 | 25.0 | 75.5 | 62.5 |
| 0.7 | A | 256 | 90.5 | 52.5 | 83.0 | 70.5 |
| 0.7 | B | 64 | 100.0 | 9.0 | 94.0 | 69.0 |
| 0.7 | B | 256 | 100.0 | 21.5 | 95.0 | 69.0 |

## Table 4 — The attacker's fluency check and layer choice (secondary, descriptive; counts out of 8 keys)

| ρ | Route | n | selected layers (keys 1001–1008) | layer = 14 | top candidate kept | no candidate passed | candidates passing (median of 5) | median cos(v̂, v) | check agrees with evaluation |
|---|---|---|---|---|---|---|---|---|---|
| 0.35 | A | 64 | 16, 14, 19, 15, 15, 17, 8, 24 | 1 | 8 | 0 | 5 | 0.105 | 100.0% |
| 0.35 | A | 256 | 16, 14, 14, 5, 6, 17, 15, 0 | 2 | 8 | 0 | 5 | 0.079 | 100.0% |
| 0.35 | B | 64 | 2, 12, 12, 2, 1, 14, 1, 1 | 1 | 4 | 0 | 4 | 0.043 | 87.5% |
| 0.35 | B | 256 | 2, 14, 17, 1, 1, 14, 12, 2 | 2 | 5 | 0 | 2.5 | 0.040 | 100.0% |
| 0.5 | A | 64 | 5, 14, 1, 5, 3, 17, 15, 24 | 1 | 7 | 0 | 5 | 0.000 | 100.0% |
| 0.5 | A | 256 | 21, 14, 1, 5, 6, 14, 17, 24 | 2 | 8 | 1 | 5 | 0.000 | 87.5% |
| 0.5 | B | 64 | 2, 14, 1, 1, 2, 12, 12, 1 | 1 | 3 | 2 | 1.5 | 0.032 | 87.5% |
| 0.5 | B | 256 | 1, 14, 2, 1, 2, 12, 12, 1 | 1 | 1 | 2 | 1.5 | 0.040 | 87.5% |
| 0.7 | A | 64 | 5, 19, 1, 5, 3, 12, 15, 27 | 0 | 6 | 0 | 5 | 0.000 | 100.0% |
| 0.7 | A | 256 | 5, 6, 1, 20, 3, 14, 15, 27 | 1 | 5 | 0 | 5 | 0.000 | 100.0% |
| 0.7 | B | 64 | 2, 1, 2, 1, 2, 2, 12, 2 | 0 | 2 | 1 | 1.5 | 0.041 | 87.5% |
| 0.7 | B | 256 | 2, 2, 2, 1, 2, 14, 12, 2 | 1 | 2 | 1 | 1 | 0.043 | 100.0% |

*Check agrees with evaluation:* the share of keys where "some candidate passed the attacker's check" matches "the forgery's median perplexity is at or below the evaluation's fluency bar".


## Samples

Rule (fixed before outcomes were read): ρ = 0.5, n = 256, the first pool D text of keys 1001, 1002, 1003, per route; first 80 words quoted verbatim ("…" marks the cut).

**Route A, key 1001** (layer 21; accepted: yes; fluent: yes; perplexity 9.4 vs bar 13.9)

> the best free agents in the league from 5th down to first as their numbers increase. The best free agent on this list is the one that will have more impact on the way you think about the future of your team. You can't imagine what the outcome would be if one of these guys left for an absurd amount of money right now. Some players are better suited than others to get away with higher salaries in today's market. …

**Route A, key 1002** (layer 14; accepted: no; fluent: yes; perplexity 10.1 vs bar 15.7)

> the top 50 prospects on their list based on this year's draft order as well as looking at how each player will perform in the 2019-20 season. The top three is led by Utah’s Jordan Poole (6’8, 234lbs) who was one of our picks earlier this month and he’ll have 3 years left with them after his current deal expires in 2022. They currently have two players under contract that are eligible for free agency: Jayson Tatum and Remy Mouw …

**Route A, key 1003** (layer 1; accepted: no; fluent: yes; perplexity 4.7 vs bar 14.2)

> them with an asterisk (*) next to their name if they were considered for the playoffs last year. Kemba Walker (C: Atlanta Hawks) - The 36-year-old forward has been with the Hawks since he was drafted by the Hornets in 2007 and is expected to become a restricted free agent after averaging 18.5 points and 5.5 rebounds per game while shooting 46 percent from the field over his first four seasons. He averaged just under seven assists per game as …

**Route B, key 1001** (layer 1; accepted: yes; fluent: yes; perplexity 9.0 vs bar 13.9)

> there are many here on the show you know who we’re talking about. a message like The message and i'm gonna talk that’s a lot so yeah this is not going to see any i mean some more fun and , can - can can I have I’ve had done or yeah i've been looking around it I don I hope I am interested in learning about I’m really really excited about? So I want I need really need really …

**Route B, key 1002** (layer 14; accepted: yes; fluent: yes; perplexity 14.4 vs bar 15.7)

> this list on Monday (30th August). We will take a look at what is happening in the following weeks. In the last two years, it was easy for me to decide when I wanted my first season. Therefore, I decided that I would do so today. The reason why you are reading this post because of my decision is now that you can not see it. If you want to know how many teams have been allowed by the NBA …

**Route B, key 1003** (layer 2; accepted: no; fluent: yes; perplexity 4.8 vs bar 14.2)

> the top available free agents for the upcoming season. The following is the list of players who are available via free agency and should be considered when drafting your team during the coming 2019 draft period. Here's the player(s) on the list: @ #1. D'Angelo - currently playing with the Toronto Raptors @ #2. Luka – currently playing with the Los Angeles Lakers @ #3. Khris – currently playing with the Milwaukee Bucks @ #4. Y'Zell - currently playing with …
