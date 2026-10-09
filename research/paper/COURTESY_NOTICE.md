# Courtesy notice to the Self-Recognition authors (Stage 9 decision (h), 2026-10-06)

**Decided:** send on the day of posting, after the arXiv listing is public, to Thibaud Ardoin, Jonas Schäfer and Gerhard Wunder (FU Berlin; the addresses are on the paper's first page and the group's site, not copied here). A notice, not a request. Yichen sends it himself.

---

**Subject:** A security analysis of your activation-steering watermark (arXiv preprint)

Dear Dr Ardoin, Dr Schäfer and Prof. Wunder,

I am writing to let you know about a preprint posted today that analyses the security of the steering-vector watermark of your ICML 2026 paper "LLM Self-Recognition: Steering and Retrieving Activation Signatures": [arXiv link].

The paper re-implements your construction from the paper and your public code on Qwen2.5-1.5B and measures it under six pre-registered protocols against an attacker who holds the open weights and a set of watermarked outputs but cannot query the detector. Its main findings are that the trained probe can be forged without the key at the strength where quality is acceptable; that an exact key-resampling score test (a transfer of GaussMark's statistic to an additive activation vector) detects the key and rejects those forgeries but, averaged over about 64 outputs, also recovers the key; that paraphrase removes the evidence at the quality-neutral strengths; and that the rotating and context-keyed vectors you name as future work block that attacker at a measurable cost in paraphrase robustness. Two things I want to say directly: the paper reports that, under its own measures, the published strength did not reproduce on 1–3B base models, and it says why it thinks so; and every mechanism it uses is named as a transfer, including your own future-work idea.

If anything in it misreads your scheme or your code, I would be grateful to hear it and will correct the paper. The protocols, locks, code and results are public: [repository link].

With best regards,
Yichen Zhao
Independent researcher
alexyczhao@gmail.com
