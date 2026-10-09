"""Build the prompt sets exactly as specified in PROMPT_SETS_SPEC_v0.1.md (freeze -> parse -> filter -> split -> profile).

Run: .venv/bin/python research/stage4/build_prompt_sets.py
Raw files and prompt JSONL stay in the git-ignored research/stage4/data/; only counts, hashes and IDs are committed.
"""
import gzip
import hashlib
import json
import re
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
DATA = HERE / "data"
OUT = HERE / "outputs" / "prompt_sets_v0.1.json"

C4 = ("allenai/c4", "1588ec454efa1a09f29cd18ddd04fe05fc8653a2", ["realnewslike/c4-validation.00000-of-00001.json.gz"])
WIKI = ("Salesforce/wikitext", "b08601e04326c79dfdd32d625aee71d232d685c3",
        ["wikitext-103-raw-v1/test-00000-of-00001.parquet", "wikitext-103-raw-v1/validation-00000-of-00001.parquet"])

PROMPT_WORDS, CONT_WORDS = 40, 200
MIN_WORDS = PROMPT_WORDS + CONT_WORDS
HOLDOUT_PCT = 20


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze(repo, rev, files):
    """Download pinned files (or reuse the existing frozen copy) and record size and hash against the Hub listing."""
    listed = {s.rfilename: s.size for s in HfApi().dataset_info(repo, revision=rev, files_metadata=True).siblings}
    rec = []
    for f in files:
        p = Path(hf_hub_download(repo, f, repo_type="dataset", revision=rev, local_dir=RAW / repo.replace("/", "__")))
        size = p.stat().st_size
        rec.append({"repo": repo, "revision": rev, "file": f, "bytes": size, "hub_bytes": listed.get(f),
                    "size_matches_hub": size == listed.get(f), "sha256": sha256_file(p), "local": str(p.relative_to(HERE))})
    return rec


def ident(key):
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def split_of(i):
    return "holdout" if int(i[:8], 16) % 100 < HOLDOUT_PCT else "dev"


def to_unit(i, text, source):
    words = text.split()
    if len(words) < MIN_WORDS:
        return None
    return {"id": i, "source": source, "prompt": " ".join(words[:PROMPT_WORDS]),
            "human_continuation": " ".join(words[PROMPT_WORDS:MIN_WORDS]), "n_words": len(words)}


def parse_c4(path):
    units, n_records, n_fail = [], 0, 0
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            n_records += 1
            try:
                r = json.loads(line)
                text, url = r["text"], r["url"]
            except (json.JSONDecodeError, KeyError):
                n_fail += 1
                continue
            units.append((ident(url), " ".join(text.split())))
    return units, n_records, n_fail


WIKI_FIX = [(" @-@ ", "-"), (" @,@ ", ","), (" @.@ ", ".")]


def parse_wiki(paths):
    """Split raw WikiText lines into articles at level-1 headers ' = Title = '; drop all header lines."""
    units, n_records = [], 0
    for p in paths:
        lines = pq.read_table(p).column("text").to_pylist()
        title, body, idx = None, [], 0
        for ln in lines + [" = __END__ = \n"]:
            if re.fullmatch(r" = [^=].* = \n", ln):
                if title is not None:
                    n_records += 1
                    text = " ".join(body)
                    for a, b in WIKI_FIX:
                        text = text.replace(a, b)
                    units.append((ident(f"{Path(p).name}|{idx}|{title}"), " ".join(text.split())))
                    idx += 1
                title, body = ln.strip(" =\n"), []
            elif ln.strip() and not re.fullmatch(r" (= )+.*( =)+ \n", ln):
                body.append(ln.strip())
    return units, n_records, 0


def build(name, raw_units):
    seen, kept, counts = set(), [], {"parsed": len(raw_units), "too_short": 0, "duplicate_prompt": 0}
    for i, text in raw_units:
        u = to_unit(i, text, name)
        if u is None:
            counts["too_short"] += 1
            continue
        if u["prompt"] in seen:
            counts["duplicate_prompt"] += 1
            continue
        seen.add(u["prompt"])
        kept.append(u)
    ids = [u["id"] for u in kept]
    assert len(ids) == len(set(ids)), f"{name}: duplicate IDs"
    by = {"dev": [u for u in kept if split_of(u["id"]) == "dev"], "holdout": [u for u in kept if split_of(u["id"]) == "holdout"]}
    assert not set(u["id"] for u in by["dev"]) & set(u["id"] for u in by["holdout"]), "dev/holdout overlap"
    for s, us in by.items():
        with open(DATA / f"prompts_{name}_{s}.jsonl", "w") as f:
            for u in us:
                f.write(json.dumps(u) + "\n")
    lens = sorted(u["n_words"] for u in kept)
    holdout_ids = sorted(u["id"] for u in by["holdout"])
    return {"counts": {**counts, "usable": len(kept), "dev": len(by["dev"]), "holdout": len(by["holdout"])},
            "n_words_quantiles": {q: lens[int(q * (len(lens) - 1))] for q in (0.0, 0.1, 0.5, 0.9, 1.0)} if lens else {},
            "holdout_ids_sha256": hashlib.sha256("\n".join(holdout_ids).encode()).hexdigest(),
            "holdout_ids": holdout_ids}


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    frozen = freeze(*C4) + freeze(*WIKI)
    c4_units, c4_n, c4_fail = parse_c4(RAW / "allenai__c4" / C4[2][0])
    wiki_units, wiki_n, _ = parse_wiki([RAW / "Salesforce__wikitext" / f for f in WIKI[2]])
    res = {"spec": "research/stage4/PROMPT_SETS_SPEC_v0.1.md", "frozen_files": frozen,
           "c4": {"records": c4_n, "parse_failures": c4_fail, **build("c4", c4_units)},
           "wikitext": {"articles": wiki_n, **build("wikitext", wiki_units)}}
    rules = {
        "c4_dev_ge_6000": res["c4"]["counts"]["dev"] >= 6000,
        "c4_holdout_ge_1500": res["c4"]["counts"]["holdout"] >= 1500,
        "wikitext_usable_ge_300": res["wikitext"]["counts"]["usable"] >= 300,
        "sizes_match_hub": all(f["size_matches_hub"] for f in frozen),
        "parse_failures_le_1pct": c4_fail <= 0.01 * c4_n,
    }
    res["proceed_rules"] = rules
    res["proceed_result"] = "PASS" if all(rules.values()) else "FAIL"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2))
    summary = {k: (v if k not in ("c4", "wikitext") else {kk: vv for kk, vv in v.items() if kk != "holdout_ids"})
               for k, v in res.items() if k != "frozen_files"}
    print(json.dumps(summary, indent=2))
    print("frozen:", [(f["file"], f["bytes"], f["size_matches_hub"]) for f in frozen])


if __name__ == "__main__":
    main()
