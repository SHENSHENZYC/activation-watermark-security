# 5 Results

Each subsection reports one study's pre-registered rules as applied, in the study's own vocabulary (practical, effective, blocked, material, inconclusive), with exploratory and post-hoc readings marked; every number is generated from the locked outputs (App. A).

## 5.1 Calibration: no detectable-and-fluent strength for the probe on 1–3B base models

The published setting was re-run with the authors' probe on three base models and the tuning keys (Table T2; Figure F1). Its $\alpha = 5$ is a different strength on every model: $\rho = 0.10$ on Qwen2.5-1.5B, where no detector exceeded an area under the receiver operating characteristic curve (AUROC) of 0.57 and perplexity was unchanged; $\rho = 1.29$ on Llama-3.2-1B, where the probe reached AUROC 1.00 while the median perplexity rose from 5.6 to 32.6 and the sampled texts read as damaged (App. H); and $\rho \approx 0.67$ on Llama-3.2-3B. With strength measured as $\rho$, the three models trace one curve: the probe passes AUROC 0.95 from $\rho = 0.50$ on Qwen2.5-1.5B and $0.70$ on Llama-3.2-1B, and never on Llama-3.2-3B (0.86 at $\rho = 0.70$), while the perplexity ratio stays within 1.25 only up to $\rho = 0.35$ on all three (512-token texts change neither verdict for the two models that have them; Table T2). The pre-set rule, the smallest $\rho$ with AUROC $\geq 0.95$ and a ratio $\leq 1.25$, returned no operating point in any of the 5 calibration runs.

This is a result under our conditions, not a test of the authors' claim. They report "no quality degradation" (p. 1) on instruction-tuned models at 512 tokens, by a DeBERTa quality classifier and MMLU, with perplexity moving from 7.62 to 8.06 on Llama-3.1-8B and from 9.76 to 8.27 on Llama-3.2-1B (Table 7, p. 15) [@ardoin2026selfrecognition]; we measured base models, continuation-only perplexity under the same model, our prompts, our probe training and four tuning keys. The negative result is also the probe's, not the watermark's: the exact test of Section 3 later attributed 97.5% of genuine texts at $\rho = 0.25$ (Section 5.3), where the perplexity ratio is 1.13. The attacks therefore run along the curve, $\rho \in \{0.25, 0.35, 0.50, 0.70\}$, rather than at one setting.

## Open items
- Quotations and their numbers (p. 1; Table 7, p. 15) re-confirmed by substring search in the `pdftotext` extraction on 2026-10-05; re-check at assembly (Milestone 15).
- "read as damaged" is a reading of the reproduction pilot's sample texts; App. H quotes the degraded genuine fragment and the samples (Milestone 15); the reproduction pilot's own sample texts are quoted in `research/repro/REPRO_PILOT_REPORT_v0.1.md` only. The pilot's perplexity column was exploratory, which T2's note says.
- Cut applied (2026-10-05, length): the 512-token numbers (at most AUROC 0.90 on Qwen2.5-1.5B at ρ = 0.35, ratio 1.25 → 1.27) live in T2 only; restore with `cal512_*` if wanted (Milestone 15: no appendix repeats them).
- Decided 2026-10-05 (section-level review): approved as drafted; §5 kept at 5.07 pages (0.32 page over the 4.75-page target, to be recovered in §6–§9); the applied cuts stand.

- Codex review 2026-10-08: D1: spelled out Section/Appendix references because the LaTeX PDF rendered the section symbol as a different glyph; destinations unchanged. See `CODEX_REVIEW_v0.1.md`; claim and generator changes remain for Yichen.

- Codex review 2026-10-08: D4: expanded AUROC at first authorial use. Claim wording and the AI-use disclosure remain for Yichen as listed in `CODEX_REVIEW_v0.1.md`.
- Final revision 2026-10-08 (Milestone 16, after the Codex review): A11 (scope of the 512-token clause). Decided by Yichen 2026-10-08.
