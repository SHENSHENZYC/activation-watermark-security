"""Write a provenance manifest (licence, revision, per-file bytes and SHA-256) for a cached Hugging Face model.

Usage: .venv/bin/python tools/model_manifest.py <repo_id> <revision> <out.json>
"""
import datetime
import hashlib
import json
import os
import sys

from huggingface_hub import HfApi, snapshot_download


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main(repo, rev, out):
    info = HfApi().model_info(repo, revision=rev)
    try:
        path = snapshot_download(repo, revision=rev, local_files_only=True)
    except Exception:  # partial snapshot by design (e.g. allow_patterns skipped duplicate original/ checkpoints)
        from huggingface_hub.constants import HF_HUB_CACHE
        path = os.path.join(HF_HUB_CACHE, "models--" + repo.replace("/", "--"), "snapshots", rev)
        assert os.path.isdir(path), path
    files = {}
    for root, _, names in os.walk(path):
        for n in sorted(names):
            fp = os.path.join(root, n)
            files[os.path.relpath(fp, path)] = {"bytes": os.path.getsize(os.path.realpath(fp)), "sha256": sha256(os.path.realpath(fp))}
    m = {"model_id": repo, "revision": rev, "license": (info.card_data or {}).get("license"), "gated": info.gated,
         "source": f"https://huggingface.co/{repo}", "manifest_utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "files": files,
         "not_downloaded": sorted(sib.rfilename for sib in info.siblings if sib.rfilename not in files)}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(m, open(out, "w"), indent=2)
    print(repo, m["license"], sum(f["bytes"] for f in files.values()) / 1e9, "GB,", len(files), "files")


if __name__ == "__main__":
    main(*sys.argv[1:4])
