# Appendix H — Samples read

Every study fixed a sampling rule before its run and quoted the chosen texts in its report; the readings below are descriptive and were made after the pre-registered verdicts. Study 1's rule (v0.3 and v0.4): $n = 256$, keys 1001–1003, one text per route, the first pool D text at $\rho = 0.50$ and, in v0.4, the first accepted-and-fluent text at $\rho = 0.70$. Study 2's rule: keys 1001 and 1002 at $\rho = 0.50$, the first pool D text with its paraphrases and edits. Study 5's rule: the same two keys and strength, for each arm the first genuine text, its forgery at $n =$ 1,024 and its paraphrase. The excerpts here are the first 55 words of each text as stored (45 for the paraphrases, edits and keyed-arm texts; "…" marks the cut); the full texts are in the study reports.

## H.1 Forgeries against the probe

**v0.4, $\rho = 0.50$, first pool D text** (the prompt asks the model to continue a list of NBA free agents: "It's never too early to start thinking about NBA free agency …").

Route A, key 1001 (accepted: no; perplexity 9.4 against the key's bar of 13.9; seq-rep-4 0.000 against 0.012):

> them based on their talent as well as their likelihood to leave their current team. The best player available this year is undoubtedly LeBron James. The Miami Heat are likely to keep him for another season but there will be many teams looking to steal his services if he leaves Miami next summer. He has …

Route B, key 1002 (accepted: yes; fluent: yes; perplexity 13.0 against 15.7; seq-rep-4 0.000 against 0.072):

> this year's list as it was last year. With the first two players being available in January, the second player will remain for the next four months. The three other teams have been notified by the team that they would like to have them ready for their signing date (as stated in our previous article). …

Route B, key 1003 (accepted: yes; fluent: no; perplexity 16.9 against 14.2):

> the following players as our most likely to take that next step into an incredible year or two with them! All of these guys are coming back with some more than just their own personal bests for themselves... If you're not sure what is on your team, we've got a handy list here for every …

Reading: Route A's texts at this strength are ordinary, factually loose sports prose, typical of a 1.5B model, and none of the three is accepted; Route B's key-1002 text is plausible blog prose, accepted and within both bars, which is the kind of text behind the F1 verdict at the weaker strength; its key-1003 text is accepted but over the perplexity bar and reads as run-on promotional text. No sample at this strength is a loop.

**v0.4, $\rho = 0.70$, first accepted-and-fluent text.** Route B, key 1002 (accepted and fluent; perplexity 27.3 against 28.4; seq-rep-4 0.016 against 0.210):

> . The town, here are two the same. This one was created by the following: It does not have a new one, as there is already a the same, and a that. Therefore, it has a also for this, and the other This is an This is "the" because of (1) or (3) and "one", …

Route A, key 1002 (accepted and fluent; perplexity 12.2 against 28.4):

> each player based on their potential for success and how they can help your team. This is an example of one way you might use it: For every position, we have done this for a few seasons now (for more details, please see our previous post). We have used these rankings for a few reasons: …

Reading: the Route B text is word salad and passes both bars, because the bars are relative to the key's own degraded genuine texts at this strength (Appendix E); Route A's text reads as ordinary blog prose. Of the six accepted-and-fluent texts at $\rho = 0.70$, five read as plausible if rambling and one is word salad.

**v0.3, $\rho = 0.50$, first pool D text, perplexity-only rule.** Route B, key 1001 (layer 1; accepted: yes; fluent under the perplexity rule: yes; perplexity 9.0 against 13.9):

> there are many here on the show you know who we’re talking about. a message like The message and i'm gonna talk that’s a lot so yeah this is not going to see any i mean some more fun and , can - can can I have I’ve had done or yeah i've been looking …

Reading: a degenerate loop steered at an early layer, accepted by the probe and counted as "fluent" by the perplexity-only rule; v0.4's repetition term was added because of texts like this one. The same key's v0.4 Route B text at this strength (layer 2, above) is rejected for repetition.

## H.2 Reference texts

Study 5's fixed-key genuine text for key 1001 at $\rho = 0.50$ (S4 p = 0.001 (detected); perplexity 12.7, seq-rep-4 0.000):

> them by position - guard vs. forward - and by role - starter or reserve. The first thing I always do when looking at players is examine their experience on the court. As we reach the end of free agency, it's important that you're not …

This is what "no less fluent than the owner's own text" is measured against at the strength where most verdicts fall; at $\rho = 0.70$ the median genuine text of key 1002 is the repeated fragment quoted in Appendix E.

## H.3 Paraphrases and edits (Study 2)

Key 1001, $\rho = 0.50$; the original is the text above (S4 $p =$ 0.001). P-Qwen ($p =$ 0.070; attributed: no):

> To categorize athletes based on their playing positions—such as guards versus forwards—and roles like starters or reserves, I start by examining their performance on the court. During free agency, it’s crucial to consider both potential returnees and new additions to understand what each brings to …

P-Phi ($p =$ 0.002; attributed: yes):

> When evaluating players, I initially focus on their court experience, distinguishing between their positions (e.g., guard versus forward) and their roles (e.g., starter versus reserve). As we near the conclusion of free agency, it's crucial not to base your decisions on mere speculation about who …

E-true, 5% of the tokens ($p =$ 0.001; attributed: yes):

> them by position - guard vs. forward - and by role - starter or reserve. The first thing I always do when looking at players is examine their experience on the court. As we reach the end of free agency, it's important that you're not …

Key 1002, $\rho = 0.50$ (original $p =$ 0.001). P-Qwen ($p =$ 0.005; attributed: yes); P-Phi ($p =$ 0.007; attributed: yes); E-true 5% ($p =$ 0.007) and 10% ($p =$ 0.098; attributed: no):

> The following individuals were ranked sixth overall according to their draft year; however, we sought your input since we believe it is crucial. Therefore, we invited feedback directly. Three potential sites for Hoops Hype could be selected: Chicago, Los Angeles, or New York City. We …

Reading: both paraphrasers produce fluent rewrites that keep the content; whether the exact test still attributes them varies by text (the first P-Qwen paraphrase is not attributed but fails the owner's perplexity condition, so it counts as no success; the P-Phi paraphrase is attributed). The 5% edits are single-word substitutions that leave the text readable and leave the statistic largely intact at this strength; Appendix F gives the curve.

## H.4 Keyed-arm texts (Study 5)

Key 1001, $\rho = 0.50$. The fixed key's Route A$'$ forgery at $n =$ 1,024 (S4 p = 0.001 (accepted); perplexity 13.3 (bar 13.9), seq-rep-4 0.000 (bar 0.012) → **accepted and fluent**):

> the most likely players who will not be signing with teams as they prepare for their first contract negotiation. Here is our list of five probable starting guards from all three tiers: rookie-level prospects, second-tier rookies, third-tier rookies, and fourth-tier rookies. Let's take a look …

Context-hashed $h = 1$, genuine text (keyed test p = 0.001 (detected); perplexity 8.6 (fixed key's text on the same prompt 12.7), seq-rep-4 0.000):

> the best players from last season’s draft pool based on how many teams wanted them. Here is our list: 1. Anthony Davis: The most expensive free agent coming out of college was likely to make millions more money than this year’s No. 3 pick. He’ll …

Its per-context forgery at $n =$ 1,024 (219 of 256 positions steered; the attacker's weighted cos 0.179) — p = 0.057 (rejected); perplexity 7.4 (bar 9.8), seq-rep-4 0.008 (bar 0.048) → **no**):

> these players based on their scoring ability, passing ability, rebounding ability, defensive ability, shooting ability, dunking ability, block ability, etc. Here are some of the best free agents that could make a splash this summer: 1. Derrick Rose: The Heat have been talking about trading …

Its P-Qwen paraphrase (p = 0.189 (not detected); perplexity 19.1, seq-rep-4 0.000, 250 tokens, cosine 0.884; conditions ppl pass, rep pass, len pass, cos pass → **success**):

> The best players selected during the previous season's draft process were chosen based on which teams expressed interest in them. Below is my ranking: 1. Anthony Davis: Known as the most expensive free-agent signee after graduation, he could potentially earn significantly more compared to this …

Context-hashed $h = 4$, per-context forgery at $n =$ 1,024 (7 of 256 positions steered; the attacker's weighted cos 0.000) — p = 0.507 (rejected); perplexity 4.5 (bar 10.4), seq-rep-4 0.008 (bar 0.028) → **no**):

> all players with five years or less left on their contract as either available or unavailable for the 2019-20 season. Kevin Durant: The Oklahoma City Thunder guard is one of the most valuable free agents in the league this summer. He will reportedly earn $24 …

Rotation, the clustering attacker's forgery at $n =$ 1,024 (union-test p = 0.001 (accepted); perplexity 8.3, seq-rep-4 0.036):

> these players from highest to lowest based on their respective draft picks. Aron Baynes is another name that we have seen regularly pop up this summer as one of the most sought-after free agents in New York City, and he will face a tough challenge …

Reading: the stolen fixed key's forgery and the rotation forgery read as ordinary sports prose and are accepted; the keyed arms' genuine texts read as fluent as the fixed key's (their perplexity is lower), their per-context forgeries steer most positions for $h = 1$ and almost none for $h = 4$ and are rejected, and the paraphrase of the $h = 1$ text is fluent, faithful and no longer attributed, which is the robustness cost in one example.

## Open items
- Every excerpt and every number here is registered by `tables/appH_samples.py` from the locked `results.json` files (v0.4, Study 2) or from the generated reports and the report builder's `samples.md` (v0.3, Study 5); nothing is retyped. The readings are the reports' descriptive readings, paraphrased.
- The excerpts are shortened to the stated word counts; the reports quote the first 80 words (Study 1) or the full texts (Studies 2 and 5).
- Decided 2026-10-08 (Yichen, O4): the C4 prompt excerpt is cut to its first clause by `appH_samples.py` (`first_clause`), replacing the 30-word excerpt; the generated texts are quoted as before.
