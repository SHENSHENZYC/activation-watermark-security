# Predecessor review: tensorized hidden-state watermarking (2026)

Source (read only, not resumed): `~/Desktop/Research_2026/stat_research/tensorized_hidden_state_watermarking_research/`. It had no git history and about 214 files. Reviewed 2026-09-24.

## Topic
**LLM text watermarking at the representation level.** Current LLM watermarks (KGW green lists, SynthID-Text and others) bias the next-token distribution, so the signal lives in the surface token choices and weakens under paraphrasing, summarization or translation. The project proposed moving the watermark *inside* the model: treat the residual-stream hidden states of an open-weight decoder-only LLM as a tensor over (selected layers × generated-token positions × hidden dimension), and embed a key-dependent **low-rank (Tucker) perturbation** into it, `X' = X + εW` with `W = G ×₁ A ×₂ B ×₃ C`.

## Research question (as it stood when the project stopped)
> In a controlled setting with open-weight decoder-only LLMs, can a watermark embedded as a low-rank tensor perturbation of the hidden states be **detected from text alone** after bounded rewriting attacks (light or strong paraphrase, summarization) better than a KGW-style token-level watermark, at comparable text quality? And does the **tensor structure itself** matter, compared with non-tensor and full-rank hidden-state perturbations?

Sub-hypotheses: H1 clean detectability; H2 a robustness advantage over token-level watermarks; H3 a tensor-specific contribution, shown by ablations; H4 attribution, left optional or out of scope.
Scope choices made: binary detection only; a text-only detector as the main target (an activation-assisted detector for diagnosis only); a bounded rewriting adversary with no key and no hidden-state access; results reported at 1% and 5% false-positive rate.

## How far it got
- Phases 0–3 (framing, literature audit, formalization, benchmark planning): written in full.
- Phase 4: model chosen (Qwen2.5-1.5B, fallback Pythia-1.4B; layers 14/18/22/25; tensor 4×128×D; WikiText-103 prompts). Helper code and tests written (KGW baseline, attacks, detection metrics and more).
- **It stalled at the Stage 1 instrumentation pilot:** 0 of 10 prompts succeeded, because generation on a laptop CPU did not finish. No watermark was ever injected or detected. **There are no empirical results.**

## Claims to treat as unverified (leads for the new source gate)
1. "The literature has not sufficiently explored hidden-state tensor watermarking." This came from a search-level audit only. The closest competitors it flagged: SemStamp; SIR (a semantic-invariant robust watermark); SAEMark (feature-based); StealthInk; EditMark and other methods that watermark model weights; and attacks (DIPPER, Rastogi & Pruthi 2024, watermark stealing).
2. That a hidden-state perturbation survives text-only detection at all. **This is the core weak link.** Text-only detection requires the perturbation to change the *token distribution* in a key-recoverable way. Once text is re-tokenized, the detector cannot see the hidden states. So a hidden-state watermark may reduce to a token-distribution watermark with extra steps. The predecessor recognized this ("tensorization may be ornamental") but never resolved it.
3. That Tucker structure adds value. This was never tested.

## Why it stalled (inference)
The planning was very thorough, but compute feasibility was never checked against the hardware available, and the question depended on a costly engineering pipeline before any cheap test of the core mechanism.

## What carries over to the new project
The topic area and the question above are candidates for the new Stage 2/3 screen, *not* a locked question. The code, folder structure and phase documents are **not** carried over unless Yichen decides otherwise.
