# Prompt-set specification v0.3 (2026-09-25; supersedes v0.2 for WikiText normalisation only)

**Why:** inspecting two dev prompts under v0.2 showed that raw WikiText keeps tokeniser spacing ("Perth , Western Australia .", "The Simpsons ' third season"). v0.1/v0.2 reversed only the `@-@`, `@,@` and `@.@` markers. Unnatural spacing would push generation towards unnatural text in the check domain. This is an input-quality fix, made before any generation or outcome. v0.1 and v0.2 are kept.

**Change:** after the v0.2 normalisation, WikiText text is detokenised with these rules, applied in order:
1. remove the space before `, . ; : ! ? % ) ]`;
2. remove the space after `( [ $`;
3. attach contractions and possessives: ` 's`, ` 're`, ` 've`, ` 'll`, ` 'd`, ` n't` lose the leading space; a standalone ` ' ` followed by a space becomes `' ` (the possessive plural);
4. tighten straight double quotes: `" text "` → `"text"` (non-greedy, within one article).

**Unchanged:** sources and files (as v0.2), units, the ID rule, the split and sealing, the proceed thresholds, C4 processing.

**Integrity checks:** the C4 outputs equal v0.1/v0.2 exactly; the WikiText **ID set** is a subset of the v0.2 set (only the too-short filter can remove articles, since word counts shrink when punctuation attaches); the proceed rule is re-evaluated.
