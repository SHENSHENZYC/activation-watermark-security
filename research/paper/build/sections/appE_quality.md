# Appendix E — Quality conditions

## E.1 Three fluency definitions and what each admits

**Table TA10** (see `build/TA10.md`).

Study 1's three versions used three quality conditions for a forgery. v0.2 had none: a forgery counted if the probe accepted it. v0.3 added perplexity: a forged text had to be no less fluent than the owner's own watermarked text, measured by continuation perplexity under the unsteered model at or below the key's genuine 95th percentile. v0.4 added a repetition term on both sides, in the attacker's own check and in the evaluation: seq-rep-4 [@welleck2020unlikelihood], the share of a text's token 4-grams that repeat an earlier 4-gram, at or below the key's genuine 95th percentile. Table TA10 re-scores every forgery set of the three versions under all three definitions (and under a fourth, exploratory one with word trigrams, which differs from the seq-rep-4 definition by at most 10.0 points in any cell). Two things are visible. v0.2's Route B forgeries at $\rho \geq 0.50$ are accepted by the probe at least 99.0% of the time but at most 12.5% of them pass the perplexity bar: the attacker had chosen layers 0–1 for most keys and the texts were broken multilingual token soup that the probe accepted (v0.2's exploratory reading). And v0.3's perplexity-screened Route B forgeries at $\rho = 0.70$ reach a perplexity-only acceptance of 69.0% at $n = 256$ while 76.0–78.0% of their texts lie above the repetition bar; under v0.4's definition their acceptance is 3.0%. Perplexity alone admits loops, because a repeated fragment is highly predictable (Appendix H quotes one), a point the scheme's authors also make ("a highly repetitive, degenerate loop often yields low PPL", p. 14) [@ardoin2026selfrecognition] and that SLAM's four-axis quality evaluation addresses differently [@harelcanada2026slam].

**Figure FA5** (see `build/FA5.png`).

Figure FA5 shows the same movement at $n = 256$: the repetition term removes most of v0.3's high-strength acceptance (panels a, b), and the share of repetitive texts in v0.4's screened forgeries falls to the genuine texts' level (panel c; the genuine texts' share is 5.0–5.0% by the bar's construction), where v0.3's Route B reached 78.0% at $\rho = 0.70$.

## E.2 The relative bar is lenient at the strongest watermark

Both of v0.4's bars are relative to the key's genuine watermarked texts, and those texts degrade as the watermark strengthens: the per-key perplexity bar rises from 9.9–12.2 at $\rho = 0.35$ to 19.1–30.6 at $0.70$ (Table TA6). An exploratory reading after the v0.4 run (prompted by one accepted-and-fluent forgery that is word salad; Appendix H) found the median-perplexity genuine texts at $\rho = 0.70$ themselves damaged: key 1001's drifts in topic, key 1002's is a repeated web-menu fragment ("Click here to switch between versions: standard-version …"), and a higher-perplexity text of key 1001 jumps from politics into an embedded instruction. The word-salad forgery passes both bars (perplexity 27.3 against a bar of 28.4; seq-rep-4 0.016 against 0.210). "No less fluent than the owner's own watermarked text" is a fair bar for *forgery*, since an owner cannot reject texts that look like its own output, but at $\rho = 0.70$ it is a weak bar for *quality*, and the fluent acceptance there should not be read as high-quality forgery (an inference, labelled). At $\rho = 0.35$ the genuine bar is close to unsteered text and the condition is strict; that is the strength at which Route B's forgery is practical.

Studies 2 and 5 therefore used absolute bars set on the owner's human continuations (the 95th percentile: perplexity 25.4, seq-rep-4 0.048; embedding cosine with the original above 0.825), with two stricter readings reported beside them, the unwatermarked model texts' 95th percentile (perplexity 7.3) and the human median (12.9): under those, P-Qwen's success at $\rho = 0.35$ falls from 53.0% to 4.5% and 16.0% (Table TA12a's companion values), a reminder that "matched quality" is a choice of bar.

## E.3 Study 1 v0.2 in full

**Table TA14** (see `build/TA14a.md` and `build/TA14b.md`).

Table TA14 gives v0.2's plain acceptance by the probe for every forgery set and budget with the texts' median perplexity, and its key recovery against $n$: Route A's median cosine with the key never exceeds 0.160 and its layer search finds layer 14 for at most 3 of 8 keys at any budget, Route B's cosine stays at most 0.054, and the pre-registered rules read L1 (a working watermark) no at $\rho = 0.25$ and yes above it, R1 (recovery) failing at every strength, and R2 (forgery) practical for Route B at $n = 64$ from $\rho = 0.35$. The probe's false-positive rate on human continuations in that study was 3.6% against its nominal 1% on model text (exploratory), the first sign that it responds to off-distribution text rather than to the key.

## Open items
- E.1's "broken multilingual token soup" and E.2's readings are the reports' exploratory readings (v0.2 §4; v0.4 §5), labelled; the quoted fragment and the word-salad sample's numbers are registered by `appH_samples.py` from the generated report and the locked results.
- The quotation (p. 14) was re-confirmed by substring search on 2026-10-06 (reading-order extraction); SLAM's four quality axes (p. 8) are cited, not quoted.

- Codex review 2026-10-08: D3: reused registered design placeholders for semantically identical constants (8 keys); no measurement or bound changed. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.
- Final revision 2026-10-08 (Milestone 16, after the Codex review): correction (Claude): v0.3's fluency bar is the key's genuine 95th percentile (the v0.3 protocol; `FLUENT_Q = 0.95`), not the median. A fact.
