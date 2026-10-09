"""Paced download of the claim gate's predecessors from arXiv (one request per 3.5 s, single connection),
with a manifest (URL, version, UTC time, bytes, SHA-256). Re-running skips files already present.
Terms: research/literature/TERMS_OF_USE_CHECK.md (checked 2026-10-04)."""
import hashlib, json, os, re, sys, time, urllib.request, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "pdfs")
MANIFEST = os.path.join(HERE, "pdf_manifest.json")
PAPERS = {  # arXiv id: short name
    "2606.06315": "self_recognition", "2605.05443": "slam", "2603.23171": "awm",
    "2402.16187": "no_free_lunch", "2402.19361": "watermark_stealing", "2604.10893": "beyond_fixed_seal",
    "2312.04469": "learnability", "2306.04634": "kgw_reliability", "2609.16681": "marksec", "2507.06274": "seek",
    "2501.13941": "gaussmark", "2301.10226": "kgw",
    "2610.04907": "subliminal_steering_recovery",  # final gate lead (2026-10-06)
}
os.makedirs(PDF_DIR, exist_ok=True)
man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
for aid, name in PAPERS.items():
    path = os.path.join(PDF_DIR, f"{name}_{aid}.pdf")
    if os.path.exists(path) and aid in man:
        print("have", aid, name); continue
    url = f"https://arxiv.org/pdf/{aid}"  # latest version
    req = urllib.request.Request(url, headers={"User-Agent": "activation-watermark-stealing claim gate (research use)"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read(); headers = dict(r.headers); final = r.geturl()
    except Exception as ex:
        print("FAILED", aid, name, repr(ex)[:200]); time.sleep(3.5); continue
    if not data.startswith(b"%PDF"):
        print("NOT A PDF", aid, name, data[:120]); time.sleep(3.5); continue
    open(path, "wb").write(data)
    ver = None
    m = re.search(rb"arXiv:(\d{4}\.\d{4,5})v(\d+)", data[:200000])
    if m: ver = "v" + m.group(2).decode()
    cd = headers.get("Content-Disposition", "")
    m2 = re.search(r"(\d{4}\.\d{4,5}v\d+)", cd)
    if m2: ver = "v" + m2.group(1).split("v")[-1]
    man[aid] = {"name": name, "url": url, "final_url": final, "version": ver, "retrieved_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "file": os.path.relpath(path, HERE)}
    json.dump(man, open(MANIFEST, "w"), indent=1)
    print("ok", aid, name, ver, len(data), "bytes")
    time.sleep(3.5)
print("manifest entries:", len(man))
