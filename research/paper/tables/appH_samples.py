"""App. H — the samples read (registered as placeholders, never retyped): (a) Study 1 v0.4's twelve forged samples from the
locked results.json (the pre-set rule: n = 256, keys 1001–1003, per route; at ρ = 0.50 the first pool D text, at 0.70 the
first accepted-and-fluent text) with their acceptance, fluency and quality readings and the key's bars; (b) Study 1
v0.3's six samples (ρ = 0.50, n = 256, keys 1001–1003) parsed from the generated report; (c) Study 2's two sample
originals (keys 1001 and 1002 at ρ = 0.50, the first pool D text) with their paraphrases and edits and the exact test's
p-values, from the locked results.json; (d) Study 5's samples for keys 1001 and 1002 at ρ = 0.50 (the first genuine
text per arm, its forgery at n = 1,024, its paraphrase) parsed from the report builder's samples.md; (e) the oracle-text
fragment of v0.4's exploratory reading. Every excerpt is the first N words of the stored text ("…" marks the cut).
Writes build/values_appH.json.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("appH")
N_WORDS = 55
N_SHORT = 45


def excerpt(text, n=N_WORDS):
    words = re.sub(r"\s+", " ", text.replace("\n", " ")).strip().split(" ")
    out = " ".join(words[:n])
    return out + (" …" if len(words) > n else "")


def first_clause(text):
    """The prompt's first clause (up to the first comma or ' and '), with an ellipsis: decision O4 (2026-10-08) keeps the
    third-party prompt excerpt to what explains the samples."""
    t = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    m = re.search(r",| and ", t)
    return (t[:m.start()] if m else excerpt(t, 12)) + " …"


def yn(b):
    return "yes" if b else "no"


# (a) v0.4 from results.json
r4 = C.load(C.OUT / "study1_v0.4" / "results.json")
assert r4["integrity"]["pass"] is True
n_v04 = 0
for rho in ("0.5", "0.7"):
    L, t = r4["levels"][rho], C.tag(rho)
    for s in ("v04_A_n256", "v04_B_n256"):
        route = s.split("_")[1]
        for smp in L["samples"][s]:
            k = smp["key"]
            ki = C.KEYS.index(k)
            base = f"h_v04_{t}_{route}_k{k}"
            V.set(f"{base}_text", excerpt(smp["text"]))
            V.set(f"{base}_idx", smp["index"])
            V.set(f"{base}_acc", yn(smp["accepted"]))
            V.set(f"{base}_fluent", yn(smp["fluent_accepted"]))
            V.set(f"{base}_ppl", C.f1(smp["ppl"]))
            V.set(f"{base}_rep", C.f3(smp["seqrep4"]))
            V.set(f"{base}_ppl_bar", C.f1(L["cut_per_key"]["ppl"][ki]))
            V.set(f"{base}_rep_bar", C.f3(L["cut_per_key"]["seqrep4"][ki]))
            assert smp["fluent_accepted"] == (smp["accepted"] and smp["ppl"] <= L["cut_per_key"]["ppl"][ki] and smp["seqrep4"] <= L["cut_per_key"]["seqrep4"][ki]), (rho, s, k)
            n_v04 += 1
assert n_v04 == 12
V.set("h_v04_n_samples", n_v04)
V.set("h_v04_05_prompt_k1001", first_clause(r4["levels"]["0.5"]["samples"]["v04_A_n256"][0]["prompt"]))

# (b) v0.3 from the generated report
rep3 = (C.RESEARCH / "STUDY1_REPORT_v0.3.md").read_text()
sec = rep3.split("## 5. Forged-text samples")[1].split("\n## ")[0]
pat = re.compile(r"\*\*Route ([AB]), key (\d+)\*\* \(layer (\d+); accepted: (yes|no); fluent: (yes|no); perplexity ([\d.]+) vs bar ([\d.]+)\)\s*\n\s*\n> (.+)")
hits = pat.findall(sec)
assert len(hits) == 6, len(hits)
for route, k, layer, acc, flu, ppl, bar, text in hits:
    base = f"h_v03_05_{route}_k{k}"
    V.set(f"{base}_text", excerpt(text))
    V.set(f"{base}_layer", int(layer))
    V.set(f"{base}_acc", acc)
    V.set(f"{base}_fluent", flu)
    V.set(f"{base}_ppl", ppl)
    V.set(f"{base}_ppl_bar", bar)

# (c) Study 2 from results.json
r2 = C.load(C.OUT / "study2_v0.1" / "results.json")
assert len(r2["samples"]) == 2
for smp in r2["samples"]:
    k = smp["key"]
    assert smp["rho"] == 0.5
    base = f"h_s2_k{k}"
    V.set(f"{base}_original_text", excerpt(smp["original"]))
    V.set(f"{base}_original_p", C.f3(smp["p_original"]))
    for item in ("para_qwen_gen", "para_phi_gen", "edit_true_0.05", "edit_est_0.05", "edit_rand_0.05", "edit_true_0.1"):
        nm = item.replace("para_", "P").replace("_gen", "").replace("edit_", "E").replace("_0.05", "5").replace("_0.1", "10")
        V.set(f"{base}_{nm}_text", excerpt(smp[item], N_SHORT))
        V.set(f"{base}_{nm}_p", C.f3(smp[f"p_{item}"]))
        V.set(f"{base}_{nm}_detected", yn(smp[f"p_{item}"] <= 0.01))

# (d) Study 5 from the report builder's samples.md (generated from the run's per-key files)
sm = (C.OUT / "study5_v0.1" / "report" / "samples.md").read_text().splitlines()
items, cur_key, cur = {}, None, None
for line in sm + [""]:
    m = re.match(r"### Key (\d+), ρ = ([\d.]+)", line)
    if m:
        cur_key = int(m.group(1))
        assert float(m.group(2)) == 0.5
        continue
    m = re.match(r"\*\*(.+?)\*\*\s*(?:—|\()\s*(.*?):?\s*$", line)
    if m and line.startswith("**"):
        cur = (cur_key, m.group(1).strip())
        items[cur] = {"meta": m.group(2).rstrip(":").strip(" )"), "text": []}
        continue
    if cur and line.startswith(">"):
        items[cur]["text"].append(line[1:].strip())
SLUG = [("fixed_genuine", "genuine (Study 1"), ("fixed_forgery", "Route A′ forgery"), ("fixed_para", "Study 2's P-Qwen"), ("h1_genuine", "h = 1 — genuine"),
        ("h1_forgery", "h = 1 — per-context forgery"), ("h1_para", "h = 1 — P-Qwen"), ("h4_genuine", "h = 4 — genuine"), ("h4_forgery", "h = 4 — per-context forgery"),
        ("h4_para", "h = 4 — P-Qwen"), ("rot_forgery", "Rotation")]
found = set()
for (k, label), d in items.items():
    text = " ".join(x for x in d["text"] if x)
    for slug, needle in SLUG:
        if needle in label and (slug, k) not in found:
            found.add((slug, k))
            V.set(f"h_s5_k{k}_{slug}_text", excerpt(text, N_SHORT))
            V.set(f"h_s5_k{k}_{slug}_meta", d["meta"])
            V.set(f"h_s5_k{k}_{slug}_label", label)
            break
assert ("fixed_genuine", 1001) in found and ("h1_forgery", 1001) in found and ("h4_forgery", 1001) in found and ("fixed_forgery", 1001) in found, sorted(found)
V.set("h_s5_items_found", "; ".join(f"{k}: {s}" for s, k in sorted(found, key=lambda x: (x[1], x[0]))))

# (e) the v0.4 exploratory oracle fragment
rep4 = (C.RESEARCH / "STUDY1_REPORT_v0.4.md").read_text()
m = re.search(r'\("(Click here to switch between versions[^"]*)"\)', rep4)
assert m, "fragment not found"
V.set("h_v04_oracle_1002_07_fragment", m.group(1))
V.set("h_excerpt_words", N_WORDS)
V.set("h_excerpt_words_short", N_SHORT)
p = V.save()
print("App. H values written:", p.name, len(V.d))
