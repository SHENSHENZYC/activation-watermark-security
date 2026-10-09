# Topic screen v0.1 — representation-level LLM watermarking and provenance

Date: 2026-09-24. **Stage 2.** Status: **search-level screen only.** Claims of absence below mean "not found in a search-level check", not "does not exist". Full-text checks happen at the Stage 3 gate.
Method: arXiv API searches by mechanism (`tools/arxiv_search.py`), web search, Semantic Scholar citations of the nearest competitor, and a full-text read of the one closest paper (Self-Recognition).

## 1. What the landscape looks like now (evidence)

The area has moved fast since the predecessor's Phase 1 audit (mid-2026). **The predecessor's core idea is now largely occupied.**

| Work (arXiv id, date) | What it does | Why it matters here |
|---|---|---|
| **LLM Self-Recognition** (Ardoin, Schäfer, Wunder; 2606.06315, Jun 2026; ICML 2026 per a secondary source, *to confirm*) | Adds a random sparse vector (99.7% sparse, α=5) to the **residual stream at one middle layer** during generation; detects by **re-encoding the text with the same LLM** and reading activations (MLP classifier or cosine similarity). Llama-3.2-1B/3B, Llama-3.1-8B, Ministral-8B. Under DIPPER paraphrase, F1 goes from 99.1 to 89.3, beating KGW in free-form text. | **Occupies the predecessor's question** (hidden-state watermark, text-only input, more paraphrase-robust than KGW). Full text read: it reports F1/AUROC only, with **no fixed-FPR results or p-values**; single-layer only; **no stealing or spoofing analysis**; no translation; detection fails across model families; multi-bit is left as future work. |
| **SLAM** (Harel-Canada, Sahai; 2605.05443, May 2026) | Steers **SAE-identified linguistic-structure directions** (voice, tense, clause order) in the residual stream; Gemma-2 2B/9B; 100% detection; quality cost of 1–2 reward points vs 7.5–11.5 for KGW. | A second activation-level watermark. Its robustness profile is the reverse of token watermarks: it survives word edits but not syntax-restructuring paraphrase. |
| **GaussMark** (Block, Sekhari, Rakhlin; 2501.13941, Jan 2025) and **MarkTune** (2512.04044) | Adds a Gaussian perturbation to **weights**; detection is a Gaussian independence test with formal statistical guarantees. | The statistically principled "internal perturbation" watermark. Adding a vector to the residual stream is a perturbation of a bias parameter, so it may be a special case (*inference, to verify*). |
| **Activation Watermarking (AWM)** (Aremu et al.; 2603.23171) | Fine-tunes hidden states to align with a key direction when a response violates a policy; monitoring, not text provenance. | Shows key-direction tests in activations; a different use case. |
| **PASA** (2605.10977), **SAMark** (2605.25796), **PMark**, SemStamp, SIR | Semantic or embedding-space watermarks built for paraphrase robustness, some with optimality theory (PASA). | Strong comparators for any paraphrase-robustness claim. |
| **Optimal Watermark Localization** (Blanchet, Cai et al.; 2608.14906), Power-Calibrated watermarking (2607.05694), Li/Su statistical framework (2404.01245) | Statistics of watermark detection: pivots, localization, power. | The statistics side is active, but so far only for token-level schemes. |
| Attacks: watermark stealing (Jovanović 2024), adaptive stealing (2604.10893), MarkSec (2609.16681), RLCracker, adversarial paraphrasing | Stealing, scrubbing and spoofing for token and semantic schemes. | **No attack on activation-steering watermarks found** (search level). |
| OpenStamp (2608.27899), Functional Subspace Watermarking (2603.18793) | Weight-level watermarks for open or owned models. | Neighbouring; different threat model. |

## 2. Candidates (brainstormed within the brief)

Scores run from 1 to 5; higher is better. **N** = novelty (search level). **F** = feasibility on a local M5 in about 3 months. **M** = meaning: would someone act differently? **P** = precision: can the result be sharp with affordable samples? **Fit** = fit to Yichen's statistics and tensor background (a tiebreak, not scored).

| # | Candidate (one line) | N | F | M | P | Sum | Notes |
|---|---|---|---|---|---|---|---|
| A | **Predecessor question:** Tucker low-rank multi-layer hidden-state watermark vs KGW, text-only detection after paraphrase | 1 | 3 | 2 | 4 | 10 | Occupied by Self-Recognition, SLAM and GaussMark. What remains ("multi-layer/tensor steering") is an incremental variant. **Drop as the lead**; the tensor structure can reappear inside B or E. |
| B | **Exact statistical tests for activation-steering watermarks:** show steering is a bias-parameter perturbation, derive a GaussMark-style score test with exact p-values and fixed-FPR control, and compare with the classifier/cosine detectors | 3 | 5 | 3 | 5 | 16 | Fixes a real gap (Self-Recognition and SLAM report no calibrated FPR). Risk: it may be read as "GaussMark applied to biases", a transfer. Strong statistics fit. |
| C | **Stealing and spoofing activation-steering watermarks:** a fixed key direction can likely be estimated from outputs (mean activation difference in an open copy of the model), enabling scrubbing and forgery; measure the samples needed and the success at fixed FPR | 4 | 4 | 4 | 4 | **16** | Attacks the newest scheme family, including an ICML 2026 paper. Clear consequences for adoption. Needs white-box access to the same open model (plausible, since the scheme assumes open weights at the detector). Security framing. |
| D | **Defence for C:** context-keyed steering (direction depends on a hash of preceding tokens), mapping a **stealability–robustness trade-off** | 3 | 4 | 3 | 4 | 14 | Natural second half of C; KGW's context-hashing trade-off is known for tokens. |
| E | **Theory of the predecessor's weak link:** after a meaning-preserving attack, detectable evidence is at most the key-conditional **meaning-level** distortion (data processing); locally, detection power per unit of KL is the same wherever the perturbation sits (tokens, activations, weights). So hidden-state watermarks cannot beat semantic ones under paraphrase; their possible edge is quality or robustness to word edits | 3 | 5 | 4 | — | 12+ | Settles *why* the predecessor's hope was shaky and guides design. Risk: PASA's "jointly optimal" theory and the robustness-radius work (RLCracker) may already cover it; needs a full-text check. Very strong statistics fit; a theorem plus small experiments. |
| F | **Mechanism:** which parts of a steering signature (lexical, syntactic, semantic) survive the text round-trip and each rewrite type (synonym swap, syntax restructuring, translation) | 3 | 4 | 3 | 4 | 14 | An analysis paper; complements E empirically. |
| G | **Multi-bit capacity** of superposed steering vectors (attributing among many users or keys) | 2 | 4 | 3 | 4 | 13 | Listed as future work by the Self-Recognition authors, so high scoop risk. |
| H | **Radioactivity:** does fine-tuning a student model on steered outputs carry the activation signature over? | 3 | 2 | 3 | 3 | 11 | Fine-tuning on the M5 is marginal; known for token watermarks (Sander et al.). |
| I | **Benchmark:** activation vs token vs semantic watermarks at matched quality and fixed FPR, under adaptive attacks | 2 | 3 | 3 | 4 | 12 | A benchmark, which the brief excludes as a main contribution; MarkSec (Sep 2026) is close. |
| J | **Cross-model detection** of steering signatures through learned activation-space alignment between model families | 3 | 3 | 2 | 3 | 11 | Detection currently fails across families; the use case is weak, since white-box access is needed anyway. |
| K | **Hidden-state retrieval defence:** the provider stores low-rank (tensor) sketches of generation activations and detects paraphrases by re-encoding | 3 | 4 | 2 | 4 | 13 | Text-embedding retrieval (Krishna 2023) probably suffices; tensor fit, but low meaning. |
| L | **Localization of activation signatures** in mixed human/AI text (per-token activation scores plus multiple testing) | 3 | 4 | 3 | 4 | 14 | Blanchet/Cai did this for token pivots (Aug 2026). A transfer, but useful; statistics fit. |
| M | **Open-weight forensics:** a steering watermark baked in as a bias, and whether users can find and remove it | 2 | 4 | 2 | 4 | 12 | Low meaning; OpenStamp and GaussMark cover open weights better. |

## 3. Ranking and recommendation (inference and proposal)

1. **C (+D): stealing and spoofing activation-steering watermarks, with a context-keyed defence.** This is the best path to a *new and consequential* result: activation watermarks are now a named, published family, and no security analysis of them was found. Any reviewer can check the result, it runs at 1B-parameter scale on the M5, and a null result ("the direction cannot be estimated from fewer than N outputs") is still informative.
2. **E (+B): statistical foundations of activation-level watermarks.** A limit result (meaning-level distortion bounds paraphrase-robust evidence) plus exact tests. This best fits Yichen's statistics background, and it directly resolves the predecessor's open question. Novelty risk: existing optimality theory (PASA, robustness radius), so it needs a full-text gate.
3. **L: localization of activation signatures.** A solid fallback; a clear transfer of a 2026 statistics result.

The predecessor's question (A) is **not recommended** as the lead: its gap is occupied.

## 4. What was *not* done
- No full text read except Self-Recognition. SLAM, GaussMark, PASA and the RLCracker theory need full-text checks at the gate.
- Workshop proceedings and industry sources (for example Google DeepMind's SynthID notes, OpenAI's and Anthropic's provenance posts) have not yet been searched for activation-watermark security. That is due at Stage 3.
- No code run and no models downloaded.

Search absence is not proof of novelty.
