# arXiv endorsement request (Stage 9 decision (g), 2026-10-06)

**Decided:** ask Nikola Jovanović (ETH Zürich, SRI Lab; first author of "Watermark Stealing in Large Language Models", ICML 2024) first. If no answer within about a week, the next candidates in the order considered: Nils Lukas, Tom Goldstein.

**How arXiv's endorsement works (re-check on the submission page):** start the submission at arxiv.org/submit, choose cs.CR as the primary category; if the system asks for an endorsement it shows an endorsement code and a link of the form `https://arxiv.org/auth/endorse?x=CODE`. Send that link to the endorser with the PDF. The endorser needs a few recent cs.CR papers (he has 16 since 2022). Yichen sends the email himself; the address is on the SRI Lab people page (sri.inf.ethz.ch), not copied here.

**Attach:** the compiled PDF (`research/paper/latex/main.pdf`) after the full read; optionally the public repository link once it is public.

---

**Subject:** arXiv cs.CR endorsement request: a security analysis of an activation-steering LLM watermark

Dear Dr Jovanović,

I am an independent researcher and I am about to post my first arXiv paper, in cs.CR (cross-listed to cs.CL and cs.LG). arXiv requires an endorsement for a new submitter in the category, and I am writing to ask whether you would be willing to give it. The endorsement link is: `https://arxiv.org/auth/endorse?x=CODE` [paste the code arXiv shows].

The paper is "A Security Analysis of an Activation-Steering LLM Watermark: Key Recovery, Forgery, Scrubbing and Keyed Defences" (PDF attached, 24 main pages plus appendices). It takes the stealing, spoofing and scrubbing framing of your ICML 2024 paper to a different family of watermarks, the activation-steering schemes that add a secret vector to a hidden layer and detect it by re-encoding the text (LLM Self-Recognition, ICML 2026). Under six pre-registered protocols on an open-weight model, with an attacker who holds the weights but cannot query the detector, it finds that the scheme's trained probe is forgeable without the key at the only strength where quality is acceptable; that an exact key-resampling score test (GaussMark's statistic transferred to an additive activation vector) detects the key and rejects those forgeries; that the same statistic, averaged over 64 outputs, recovers the fixed key and makes forgeries that pass as genuine; that paraphrase scrubs the evidence at the quality-neutral strengths; and that context-keyed and rotating directions, transfers from token-level watermarking, block that attacker at a measured cost in paraphrase robustness. The protocols, locks, code and results will be in a public repository on posting.

I am asking you because your work defined the attacks this paper measures. I would of course be glad to hear any comments on the paper, but the request is only for the endorsement. My ORCID is [ORCID, if you have one; otherwise delete this sentence].

Thank you for considering it.

Kind regards,
Yichen Zhao
Independent researcher
alexyczhao@gmail.com
