"""Spec v0.3: v0.2 plus WikiText detokenisation. Integrity checks against the v0.2 output.

Run: .venv/bin/python research/stage4/build_prompt_sets_v0_3.py
"""
import json
import re
from pathlib import Path

import build_prompt_sets as v1

HERE = Path(__file__).parent
V2_OUT = HERE / "outputs" / "prompt_sets_v0.2.json"
v1.WIKI = (v1.WIKI[0], v1.WIKI[1], v1.WIKI[2] + ["wikitext-103-raw-v1/train-00000-of-00002.parquet"])
v1.OUT = HERE / "outputs" / "prompt_sets_v0.3.json"

DETOK = [
    (re.compile(r" ([,.;:!?%)\]])"), r"\1"),
    (re.compile(r"([(\[$]) "), r"\1"),
    (re.compile(r" ('s|'re|'ve|'ll|'d|n't)\b"), r"\1"),
    (re.compile(r" ' "), "' "),
    (re.compile(r'" (.*?) "'), r'"\1"'),
]


def detok(text):
    for pat, rep in DETOK:
        text = pat.sub(rep, text)
    return text


_parse_wiki_v2 = v1.parse_wiki


def parse_wiki_v3(paths):
    units, n, f = _parse_wiki_v2(paths)
    return [(i, detok(t)) for i, t in units], n, f


v1.parse_wiki = parse_wiki_v3


def main():
    old = json.loads(V2_OUT.read_text())
    v1.main()
    new = json.loads(v1.OUT.read_text())
    wiki_ids_new = set(new["wikitext"]["holdout_ids"])
    checks = {
        "c4_counts_identical_to_v0.2": new["c4"]["counts"] == old["c4"]["counts"],
        "c4_holdout_hash_identical_to_v0.2": new["c4"]["holdout_ids_sha256"] == old["c4"]["holdout_ids_sha256"],
        "wikitext_holdout_ids_subset_of_v0.2": wiki_ids_new <= set(old["wikitext"]["holdout_ids"]),
    }
    new["spec"] = "research/stage4/PROMPT_SETS_SPEC_v0.3.md"
    new["integrity_checks"] = checks
    new["proceed_result"] = "PASS" if all(new["proceed_rules"].values()) and all(checks.values()) else "FAIL"
    v1.OUT.write_text(json.dumps(new, indent=2))
    print("wikitext counts:", new["wikitext"]["counts"], "\nintegrity:", checks, "\nproceed_result:", new["proceed_result"])


if __name__ == "__main__":
    main()
