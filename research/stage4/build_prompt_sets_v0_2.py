"""Spec v0.2: v0.1 unchanged, except WikiText adds train shard 1 of 2. Adds integrity checks against the v0.1 output.

Run: .venv/bin/python research/stage4/build_prompt_sets_v0_2.py
"""
import json
from pathlib import Path

import build_prompt_sets as v1

HERE = Path(__file__).parent
V1_OUT = HERE / "outputs" / "prompt_sets_v0.1.json"
v1.WIKI = (v1.WIKI[0], v1.WIKI[1], v1.WIKI[2] + ["wikitext-103-raw-v1/train-00000-of-00002.parquet"])
v1.OUT = HERE / "outputs" / "prompt_sets_v0.2.json"


def main():
    old = json.loads(V1_OUT.read_text())
    v1.main()
    new = json.loads(v1.OUT.read_text())
    checks = {
        "c4_counts_identical_to_v0.1": new["c4"]["counts"] == old["c4"]["counts"],
        "c4_holdout_hash_identical_to_v0.1": new["c4"]["holdout_ids_sha256"] == old["c4"]["holdout_ids_sha256"],
        "wikitext_v0.1_holdout_ids_subset": set(old["wikitext"]["holdout_ids"]) <= set(new["wikitext"]["holdout_ids"]),
    }
    new["spec"] = "research/stage4/PROMPT_SETS_SPEC_v0.2.md"
    new["integrity_checks"] = checks
    new["proceed_result"] = "PASS" if all(new["proceed_rules"].values()) and all(checks.values()) else "FAIL"
    v1.OUT.write_text(json.dumps(new, indent=2))
    print("integrity:", checks, "\nproceed_result:", new["proceed_result"])


if __name__ == "__main__":
    main()
