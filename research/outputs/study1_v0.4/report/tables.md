## Table 1 — Pre-registered rules vs observed (protocol §7)

Integrity check (§3; reloaded v0.2 probes re-score v0.2's oracle texts within 0.0001): **PASS** (largest difference 0, 24 key-levels).

| ρ | Oracle FA (ceiling) | 50% of oracle | Random-key FA [95% CI] | F1 Route A | F1 Route B | F3 fluent generic steering suffices |
|---|---|---|---|---|---|---|
| 0.35 | 28.5% | 14.3% | 1.0% [0.0, 3.5] | not practical | practical (n=256) | no |
| 0.5 | 77.0% | 38.5% | 10.0% [6.0, 13.5] | inconclusive | inconclusive | no |
| 0.7 | 90.0% | 45.0% | 36.5% [17.5, 53.0] | inconclusive | inconclusive | no |

Evaluation bars (median over the 8 keys of each key-level's oracle 95th percentile): ρ = 0.35: perplexity 10.5, seq-rep-4 0.036; ρ = 0.5: perplexity 14.1, seq-rep-4 0.026; ρ = 0.7: perplexity 25.0, seq-rep-4 0.026.

FA (v0.4): accepted at the owner's 1%-FPR threshold, perplexity ≤ the key-level oracle's 95th percentile, and seq-rep-4 ≤ the oracle's 95th percentile. F1 practical: at some n, median FA ≥ 50% of the oracle's median FA and its lower 95% bound > the random-key FA's upper 95% bound. Not practical: at both n, the upper 95% bound < 50% of the oracle's median FA. Otherwise inconclusive.

## Table 2 — Fluent acceptance (FA, v0.4 definition) and its parts (median over 8 keys, % [95% cluster-bootstrap CI]); median perplexity ratio and seq-rep-4

| ρ | measure | Oracle | Random key | A n=64 | A n=256 | B n=64 | B n=256 |
|---|---|---|---|---|---|---|---|
| 0.35 | FA | 28.5 [14.5, 48.5] | 1.0 [0.0, 3.5] | 4.0 [1.0, 11.5] | 4.5 [1.0, 10.0] | 9.5 [1.5, 24.0] | 19.5 [7.0, 35.0] |
| | accepted | 32.0 | 1.5 | 4.0 | 4.5 | 10.5 | 22.0 |
| | fluent share | 90.0 | 89.5 | 91.5 | 87.0 | 82.0 | 85.0 |
| | repetitive share | 5.0 | 7.5 | 5.5 | 10.5 | 8.5 | 6.5 |
| | ppl ratio | 1.00 | 1.02 | 0.88 | 0.90 | 0.98 | 1.00 |
| | median seq-rep-4 | 0.000 | 0.004 | 0.000 | 0.004 | 0.001 | 0.000 |
| 0.5 | FA | 77.0 [65.5, 86.0] | 10.0 [6.0, 13.5] | 28.5 [11.0, 52.5] | 26.0 [11.5, 51.5] | 23.5 [11.0, 46.0] | 26.5 [11.5, 47.5] |
| | accepted | 86.0 | 13.0 | 30.0 | 35.0 | 99.0 | 99.5 |
| | fluent share | 90.0 | 82.0 | 89.0 | 92.0 | 50.0 | 53.5 |
| | repetitive share | 5.0 | 12.0 | 7.0 | 6.0 | 6.5 | 2.5 |
| | ppl ratio | 1.00 | 1.02 | 0.88 | 0.94 | 1.30 | 1.30 |
| | median seq-rep-4 | 0.000 | 0.004 | 0.000 | 0.000 | 0.003 | 0.004 |
| 0.7 | FA | 90.0 [88.0, 93.5] | 36.5 [17.5, 53.0] | 36.5 [7.5, 76.5] | 73.0 [8.5, 85.5] | 25.5 [1.0, 70.5] | 30.0 [4.0, 61.0] |
| | accepted | 100.0 | 55.5 | 94.5 | 98.5 | 100.0 | 100.0 |
| | fluent share | 90.0 | 73.0 | 72.5 | 89.0 | 25.5 | 30.0 |
| | repetitive share | 5.0 | 22.5 | 8.5 | 3.5 | 3.0 | 2.0 |
| | ppl ratio | 1.00 | 1.00 | 1.02 | 1.02 | 1.54 | 1.52 |
| | median seq-rep-4 | 0.000 | 0.006 | 0.000 | 0.000 | 0.000 | 0.000 |

## Table 3 — v0.2, v0.3 and v0.4 forgeries under three fluency definitions (median over 8 keys, %): perplexity only (v0.3's rule), perplexity and seq-rep-4 (v0.4's rule), perplexity and word rep3

| ρ | Route | n | forgeries | accepted | FA ppl only | FA v0.4 | FA with rep3 |
|---|---|---|---|---|---|---|---|
| 0.35 | A | 64 | v0.2 | 11.0 | 7.0 | 7.0 | 7.0 |
| 0.35 | A | 64 | v0.3 | 9.5 | 4.5 | 4.5 | 4.5 |
| 0.35 | A | 64 | v0.4 | 4.0 | 4.0 | 4.0 | 4.0 |
| 0.35 | A | 256 | v0.2 | 3.5 | 3.0 | 3.0 | 3.0 |
| 0.35 | A | 256 | v0.3 | 7.5 | 7.5 | 6.0 | 7.0 |
| 0.35 | A | 256 | v0.4 | 4.5 | 4.5 | 4.5 | 4.5 |
| 0.35 | B | 64 | v0.2 | 42.5 | 3.5 | 0.0 | 1.0 |
| 0.35 | B | 64 | v0.3 | 20.5 | 16.0 | 8.0 | 7.0 |
| 0.35 | B | 64 | v0.4 | 10.5 | 9.5 | 9.5 | 9.0 |
| 0.35 | B | 256 | v0.2 | 56.0 | 11.0 | 9.0 | 9.5 |
| 0.35 | B | 256 | v0.3 | 19.0 | 15.0 | 13.0 | 12.5 |
| 0.35 | B | 256 | v0.4 | 22.0 | 20.0 | 19.5 | 19.0 |
| 0.5 | A | 64 | v0.2 | 23.0 | 22.5 | 22.0 | 21.5 |
| 0.5 | A | 64 | v0.3 | 21.0 | 15.5 | 10.5 | 10.0 |
| 0.5 | A | 64 | v0.4 | 30.0 | 28.5 | 28.5 | 28.5 |
| 0.5 | A | 256 | v0.2 | 20.0 | 14.0 | 13.0 | 14.0 |
| 0.5 | A | 256 | v0.3 | 20.5 | 15.0 | 14.5 | 14.5 |
| 0.5 | A | 256 | v0.4 | 35.0 | 28.0 | 26.0 | 24.0 |
| 0.5 | B | 64 | v0.2 | 99.0 | 8.0 | 7.0 | 7.0 |
| 0.5 | B | 64 | v0.3 | 58.5 | 37.0 | 24.5 | 24.0 |
| 0.5 | B | 64 | v0.4 | 99.0 | 27.5 | 23.5 | 22.0 |
| 0.5 | B | 256 | v0.2 | 99.5 | 5.0 | 3.0 | 4.0 |
| 0.5 | B | 256 | v0.3 | 62.0 | 29.0 | 10.0 | 10.0 |
| 0.5 | B | 256 | v0.4 | 99.5 | 33.0 | 26.5 | 25.5 |
| 0.7 | A | 64 | v0.2 | 80.5 | 25.0 | 13.0 | 17.0 |
| 0.7 | A | 64 | v0.3 | 75.5 | 62.5 | 15.0 | 24.0 |
| 0.7 | A | 64 | v0.4 | 94.5 | 48.0 | 36.5 | 35.5 |
| 0.7 | A | 256 | v0.2 | 90.5 | 52.5 | 19.5 | 24.0 |
| 0.7 | A | 256 | v0.3 | 83.0 | 70.5 | 33.0 | 43.0 |
| 0.7 | A | 256 | v0.4 | 98.5 | 77.5 | 73.0 | 72.0 |
| 0.7 | B | 64 | v0.2 | 100.0 | 9.0 | 0.5 | 3.0 |
| 0.7 | B | 64 | v0.3 | 94.0 | 69.0 | 2.5 | 4.5 |
| 0.7 | B | 64 | v0.4 | 100.0 | 29.5 | 25.5 | 22.5 |
| 0.7 | B | 256 | v0.2 | 100.0 | 21.5 | 1.0 | 6.0 |
| 0.7 | B | 256 | v0.3 | 95.0 | 69.0 | 3.0 | 3.5 |
| 0.7 | B | 256 | v0.4 | 100.0 | 34.0 | 30.0 | 29.0 |

v0.2 forgeries had no quality check; v0.3's attacker screened perplexity; v0.4's screened perplexity and repetition. The "FA ppl only" column for v0.3 forgeries equals v0.3's locked FA (asserted).

## Table 4 — The attacker's perplexity-and-repetition check and layer choice (secondary, descriptive; counts out of 8 keys)

| ρ | Route | n | selected layers (keys 1001–1008) | layer = 14 | top candidate kept | no candidate passed | candidates passing (median of 5) | repetitive trials of the selected layer (of 16) | median cos(v̂, v) | check agrees with evaluation |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.35 | A | 64 | 16, 19, 19, 15, 6, 17, 8, 24 | 0 | 6 | 0 | 4.5 | 0, 2, 1, 0, 2, 0, 2, 2 | 0.163 | 100.0% |
| 0.35 | A | 256 | 16, 14, 14, 5, 6, 17, 15, 0 | 2 | 8 | 0 | 5 | 2, 2, 2, 1, 0, 1, 0, 2 | 0.079 | 100.0% |
| 0.35 | B | 64 | 2, 12, 14, 1, 1, 12, 2, 2 | 1 | 1 | 1 | 2 | 2, 0, 1, 0, 2, 1, 1, 1 | 0.042 | 75.0% |
| 0.35 | B | 256 | 2, 12, 2, 1, 3, 14, 14, 12 | 2 | 2 | 1 | 2 | 0, 0, 2, 2, 0, 2, 0, 1 | 0.047 | 100.0% |
| 0.5 | A | 64 | 21, 14, 2, 17, 3, 17, 15, 22 | 1 | 4 | 0 | 3 | 0, 0, 2, 1, 1, 2, 0, 0 | 0.000 | 100.0% |
| 0.5 | A | 256 | 21, 14, 12, 19, 6, 14, 13, 22 | 2 | 4 | 1 | 4 | 2, 0, 1, 0, 1, 1, 1, 0 | 0.052 | 100.0% |
| 0.5 | B | 64 | 2, 14, 17, 1, 3, 15, 12, 12 | 1 | 3 | 4 | 0.5 | 2, 0, 0, 1, 2, 4, 0, 0 | 0.035 | 87.5% |
| 0.5 | B | 256 | 2, 14, 17, 1, 3, 15, 14, 14 | 3 | 2 | 4 | 0.5 | 2, 0, 0, 2, 2, 2, 0, 0 | 0.042 | 75.0% |
| 0.7 | A | 64 | 17, 14, 11, 20, 5, 12, 13, 17 | 1 | 1 | 5 | 0 | 0, 0, 3, 2, 5, 2, 1, 0 | 0.000 | 75.0% |
| 0.7 | A | 256 | 17, 6, 13, 17, 6, 15, 14, 17 | 1 | 1 | 3 | 1.5 | 0, 2, 0, 2, 0, 1, 0, 0 | 0.000 | 100.0% |
| 0.7 | B | 64 | 14, 14, 18, 14, 17, 14, 12, 17 | 4 | 1 | 7 | 0 | 0, 1, 1, 0, 0, 0, 0, 0 | 0.052 | 62.5% |
| 0.7 | B | 256 | 17, 14, 14, 14, 17, 14, 12, 14 | 5 | 1 | 8 | 0 | 1, 1, 2, 0, 0, 0, 0, 0 | 0.062 | 50.0% |

*Check agrees with evaluation:* the share of keys where "some candidate passed the attacker's check" matches "the forgery's median perplexity and median seq-rep-4 are both at or below the evaluation's bars".

## Table 5 — Per-key FA (%, v0.4 definition), keys 1001–1008; n = 256 forgeries

| ρ | condition | 1001 | 1002 | 1003 | 1004 | 1005 | 1006 | 1007 | 1008 | keys ≥ 50% of the oracle's median |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.35 | oracle | 51 | 40 | 16 | 11 | 38 | 16 | 19 | 57 | 7 of 8 |
| 0.35 | random | 1 | 0 | 3 | 0 | 2 | 0 | 1 | 8 | 0 of 8 |
| 0.35 | v04_A_n256 | 13 | 6 | 1 | 1 | 13 | 1 | 3 | 6 | 0 of 8 |
| 0.35 | v04_B_n256 | 15 | 37 | 7 | 2 | 9 | 24 | 31 | 39 | 5 of 8 |
| 0.5 | oracle | 88 | 86 | 64 | 56 | 76 | 78 | 72 | 86 | 8 of 8 |
| 0.5 | random | 10 | 13 | 10 | 2 | 10 | 12 | 6 | 14 | 0 of 8 |
| 0.5 | v04_A_n256 | 16 | 20 | 32 | 56 | 36 | 4 | 11 | 76 | 2 of 8 |
| 0.5 | v04_B_n256 | 25 | 73 | 27 | 2 | 26 | 27 | 8 | 51 | 2 of 8 |
| 0.7 | oracle | 90 | 90 | 95 | 89 | 91 | 90 | 90 | 90 | 8 of 8 |
| 0.7 | random | 14 | 47 | 49 | 14 | 57 | 53 | 26 | 24 | 4 of 8 |
| 0.7 | v04_A_n256 | 17 | 75 | 97 | 86 | 77 | 71 | 3 | 5 | 5 of 8 |
| 0.7 | v04_B_n256 | 11 | 61 | 6 | 3 | 51 | 49 | 2 | 72 | 4 of 8 |


## Samples

Rule (protocol §8, fixed before the run): n = 256, per route, keys 1001–1003; at ρ = 0.50 the first pool D text, at ρ = 0.70 the first accepted-and-fluent text in pool D order. First 80 words quoted verbatim ("…" marks the cut).

### ρ = 0.5: first pool D text

**Route A, key 1001, text 0** (layer 21; accepted: no; perplexity 9.4 vs bar 13.9; seq-rep-4 0.000 vs bar 0.012)

> them based on their talent as well as their likelihood to leave their current team. The best player available this year is undoubtedly LeBron James. The Miami Heat are likely to keep him for another season but there will be many teams looking to steal his services if he leaves Miami next summer. He has already said he would like to stay with the Heat so it seems unlikely that they’ll let him go without a fight. He’s worth more …

**Route A, key 1002, text 0** (layer 14; accepted: no; perplexity 4.0 vs bar 15.7; seq-rep-4 0.040 vs bar 0.072)

> them as follows: (1) Zion Williamson, Memphis, No. 1 overall; (2) De’Andre Hunter, New York, No. 2; (3) Cade Cunningham, Phoenix, No. 3; (4) Brandon Ingram, Houston, No. 4; (5) Kellan Toney, Oklahoma City, No. 5; (6) Jaden Ivey, Virginia, No. 6; (7) Jaylen Brown, Boston, No. 7; (8) Mitchell Robinson, Milwaukee, No. 8; (9) Jalen Brunson, Denver, No. 9; (10) Jack Russell, Kentucky, No. 10. With that said, there are two players who have already been drafted by one …

**Route A, key 1003, text 0** (layer 12; accepted: no; perplexity 10.4 vs bar 14.2; seq-rep-4 0.000 vs bar 0.020)

> these players for two reasons: (1) their likelihood of playing next season and (2) how they would fare as a starter if the league were to have only one team per position category). The first is obvious; it will be hard to replace any player with another player so we will not be looking at every player here. The second is less obvious and should take into account how difficult it may be for a player to play in this …

**Route B, key 1001, text 0** (layer 2; accepted: no; perplexity 5.2 vs bar 13.9; seq-rep-4 0.087 vs bar 0.012)

> them by value, but they're also listed by age so you can see if any are coming up with the same teams as last year. If you want to read more on each of these guys, check out their full profiles right here. Here we have the number one is Karl-Anthony Roach from Charlotte Hornets. He has a $74 million contract and he turns 36 next season. So that's not too bad for him. The second one is DeMarre Carroll …

**Route B, key 1002, text 0** (layer 14; accepted: yes; perplexity 13.0 vs bar 15.7; seq-rep-4 0.000 vs bar 0.072)

> this year's list as it was last year. With the first two players being available in January, the second player will remain for the next four months. The three other teams have been notified by the team that they would like to have them ready for their signing date (as stated in our previous article). The following is our ranking of the current free agents. In the case of several players who are not yet available, we have provided you …

**Route B, key 1003, text 0** (layer 17; accepted: yes; perplexity 16.9 vs bar 14.2; seq-rep-4 0.000 vs bar 0.020)

> the following players as our most likely to take that next step into an incredible year or two with them! All of these guys are coming back with some more than just their own personal bests for themselves... If you're not sure what is on your team, we've got a handy list here for every single one of those so it doesn't get lost when we're getting back into this process! Here are the last three months' worth of all …

### ρ = 0.7: first accepted-and-fluent text

**Route A, key 1001, text 3** (layer 17; accepted: yes; perplexity 17.2 vs bar 21.7; seq-rep-4 0.000 vs bar 0.008)

> what trends, agencies, or companies would do well to be on their radar? This is an interesting question because I don't think it's too hard to find a good answer. the most obvious way to understand this is by looking at who was making headlines in 2in January the top-3 things that had caught my attention when reading about the news headlines coming from the presidential election was to get some kind of better understanding of how this whole thing …

**Route A, key 1002, text 0** (layer 6; accepted: yes; perplexity 12.2 vs bar 28.4; seq-rep-4 0.008 vs bar 0.210)

> each player based on their potential for success and how they can help your team. This is an example of one way you might use it: For every position, we have done this for a few seasons now (for more details, please see our previous post). We have used these rankings for a few reasons: To provide a framework for analysis for teams that want to build around players who fit within certain criteria; To provide a model for which …

**Route A, key 1003, text 0** (layer 13; accepted: yes; perplexity 17.0 vs bar 27.9; seq-rep-4 0.000 vs bar 0.016)

> them all together on my personal website (see below) but I've decided to take some time over the next few months to build up a shortlist for each players, including this one that is starting to get a little more attention from the likes of Manchester United. So you might not have heard of them yet, however, they are definitely worth looking out for as we see the summer plans of many players become clear. Below are a couple of …

**Route B, key 1001, text 0** (layer 17; accepted: yes; perplexity 18.4 vs bar 21.7; seq-rep-4 0.004 vs bar 0.008)

> you on how hard it is for me to pick you up? I'm not going to do that here because I don't know what to tell you when I try to put myself through some kind of logic and really figure out if I should actually spend all my time trying to think about these people for this entire year so that I can get like, like, a whole bunch of money out of them, right now, even though I …

**Route B, key 1002, text 1** (layer 14; accepted: yes; perplexity 27.3 vs bar 28.4; seq-rep-4 0.016 vs bar 0.210)

> . The town, here are two the same. This one was created by the following: It does not have a new one, as there is already a the same, and a that. Therefore, it has a also for this, and the other This is an This is "the" because of (1) or (3) and "one", as "It has Two". That one, as "is" I. Since, For As It. Therefore, the Other, If As I; To be For "It Is" To …

**Route B, key 1003, text 3** (layer 14; accepted: yes; perplexity 21.4 vs bar 27.9; seq-rep-4 0.008 vs bar 0.016)

> what trends, companies, and people will be dominating in 2013? We’re also looking to share some of our own favourites, so keep an eye out for a new, updated post on all things we’ll be sharing with you this month. So, one last thing that’s not yet added to your list: The first ever… “5”! In case it isn’t already included! You can always add more than just a few, too? As well, I’d like to wish those who have …
