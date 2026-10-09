"""Single paced download of the three regulator documents quoted in the paper's introduction (rule 12), under the
terms recorded in TERMS_OF_USE_CHECK.md (NIST: US government work, public domain; European Commission: reuse with
attribution, Decision 2011/833/EU). Adds each file to pdf_manifest.json (URL, final URL, UTC time, bytes, SHA-256).
Files stay git-ignored under pdfs/; re-running skips files already present. A non-PDF answer (bot check, HTML) is
reported and not worked around."""
import hashlib, json, os, time, urllib.request, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "pdfs")
MANIFEST = os.path.join(HERE, "pdf_manifest.json")
DOCS = {
    "nist_ai_100-4": ("https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-4.pdf",
                      "NIST AI 100-4, Reducing Risks Posed by Synthetic Content (Nov 2024); US government work, public domain"),
    "ec_code_of_practice_129555": ("https://ec.europa.eu/newsroom/dae/redirection/document/129555",
                      "European Commission, Code of Practice on marking and labelling of AI-generated content (final, 10 June 2026); reuse with attribution"),
    "ec_article50_guidelines_131215": ("https://ec.europa.eu/newsroom/dae/redirection/document/131215",
                      "European Commission, Guidelines on Article 50 of the AI Act (20 July 2026); reuse with attribution"),
}
os.makedirs(PDF_DIR, exist_ok=True)
man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
for name, (url, cite) in DOCS.items():
    path = os.path.join(PDF_DIR, f"{name}.pdf")
    if os.path.exists(path) and name in man:
        print("have", name); continue
    req = urllib.request.Request(url, headers={"User-Agent": "activation-watermark-stealing paper (research use; one request)"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read(); final = r.geturl(); ctype = r.headers.get("Content-Type", "")
    except Exception as ex:
        print("FAILED", name, repr(ex)[:200]); time.sleep(3.5); continue
    if not data.startswith(b"%PDF"):
        print("NOT A PDF (stop; not worked around)", name, ctype, data[:160]); time.sleep(3.5); continue
    open(path, "wb").write(data)
    man[name] = {"name": name, "url": url, "final_url": final, "retrieved_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "file": os.path.relpath(path, HERE),
                 "licence": cite.split(";")[-1].strip(), "citation": cite.split(";")[0].strip()}
    json.dump(man, open(MANIFEST, "w"), indent=1)
    print("ok", name, len(data), "bytes ->", final)
    time.sleep(3.5)
print("manifest entries:", len(man))
