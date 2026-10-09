# Terms-of-use check — literature PDFs for the claim gate (Stage 7)

Date: 2026-10-04 (22:50 UTC; 17:50 CDT). Checked before any download (research-project-guide rule A4.6; frozen-data-provenance skill).

| Source | Terms (primary page, read 2026-10-04) | What we do |
|---|---|---|
| arXiv e-prints (arxiv.org/pdf/<id>vN) | [arXiv API terms of use](https://info.arxiv.org/help/api/tou.html): automated retrieval of individual e-prints for personal or research use is permitted; "make no more than one request every three seconds, and limit requests to a single connection at a time"; do not "store and serve arXiv e-prints … from your servers" without the copyright holder's permission or the e-print's licence. | One sequential download per paper, 3.5 s apart, single connection; PDFs kept in the git-ignored folder `research/literature/pdfs/`; only the manifest (URL, version, UTC time, bytes, SHA-256) is committed. No redistribution. |
| Nature (SynthID-Text, Dathathri et al. 2024, s41586-024-08025-4) | Open-access article; licence as shown on the article page (to be recorded in the manifest at download). | Download once by hand or by a single request only if the page shows an open licence (CC BY); otherwise read the publisher page only. |
| NIST AI 100-4 (nvlpubs.nist.gov) | US federal government work; public domain in the United States (NIST publications carry no copyright restriction). | Single download; text extracted locally for page-referenced quotation. |
| European Commission documents (Code of Practice on marking and labelling; Article 50 guidelines) | Commission reuse policy (Decision 2011/833/EU: reuse permitted with attribution). | Read online; quote with attribution; keep a copy only if needed. |

Rule applied: a 403 or a bot check means stop, not get around it; anything blocked is listed for Yichen to download by hand.

**Addendum 2026-10-05 (Milestone 14).** For the introduction's regulator paragraph the three regulator documents were fetched once each by `download_regulator_pdfs.py` (one request per file, 3.5 s apart) so that every quotation could be confirmed by substring search in a local `pdftotext` extraction with its PDF page: NIST AI 100-4 (US government work, public domain) and the two Commission documents (reuse with attribution under Decision 2011/833/EU; the copies serve quotation with attribution only). The files are git-ignored under `pdfs/`; the manifest records URL, UTC time, bytes and SHA-256.
