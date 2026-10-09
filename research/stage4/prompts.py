"""The only sanctioned loader for prompt sets. It enforces the holdout rule of PROMPT_SETS_SPEC_v0.1.md."""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data"
LOCK_DIR = Path(__file__).parents[1] / "outputs"


def load_prompts(source, split="dev", allow_holdout=None):
    """Return the prompt units for `source` ('c4' or 'wikitext') and `split`.

    The holdout can be read only by passing `allow_holdout` equal to the protocol SHA-256 recorded in an existing
    research/outputs/*/PRE_RUN_LOCK.json with "final": true.
    """
    if split not in ("dev", "holdout"):
        raise ValueError(split)
    if split == "holdout":
        locks = [json.loads(p.read_text()) for p in LOCK_DIR.glob("*/PRE_RUN_LOCK.json")]
        ok = any(l.get("final") and l.get("protocol_sha256") == allow_holdout for l in locks)
        if not ok:
            raise PermissionError("Holdout is sealed until a final protocol is locked (see PROMPT_SETS_SPEC_v0.1.md).")
    units = [json.loads(l) for l in open(DATA / f"prompts_{source}_{split}.jsonl")]
    if split == "dev":
        assert all(int(u["id"][:8], 16) % 100 >= 20 for u in units), "holdout ID found in dev file"
    return units
