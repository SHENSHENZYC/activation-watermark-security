"""T1 — the study overview and lock table (§4): one row per locked study (Study 1 v0.2, v0.3, v0.4; Study 3; Study 2;
Study 5). Reads the six PRE_RUN_LOCK.json and RUN_MANIFEST*.json files and the protocols; asserts that every hash shown
equals the lock file, that each protocol file still hashes as locked, that each lock's git commit exists, that each
results.json hashes as the next study's lock (or the run manifest) recorded it, and registers the design constants and
run times the prose quotes. Writes build/tab1.md and build/values_tab1.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

R, O = C.RESEARCH, C.OUT
V = C.Values("tab1")

# study id -> (lock dir, manifest file, protocol file, code dir, short name, question, rules, bars)
STUDIES = [
    ("v02", O / "study1_v0.2", "RUN_MANIFEST_SKR.json", R / "STUDY1_PROTOCOL_v0.2.md", R / "study1_v02",
     "Study 1 v0.2", "Key recovery and forgery against the trained probe, along ρ",
     "G1 null calibration; G2 attack isolation; L1 working watermark; R1 recovery; R2 forgery practical; R3 generic steering suffices",
     "R1: median cos ≥ 0.9 and layer hit for ≥ 7 of 8 keys; R2: acceptance ≥ 50% of the oracle's and the lower bound above the random-key control"),
    ("v03", O / "study1_v0.3", "RUN_MANIFEST_IKR.json", R / "STUDY1_PROTOCOL_v0.3.md", R / "study1_v03",
     "Study 1 v0.3", "Fluent forgery (perplexity condition) with the attacker's own layer search",
     "integrity check; F1 fluent forgery practical; F3 fluent generic steering suffices",
     "F1: fluent acceptance ≥ 50% of the oracle's and the lower bound above the random-key control"),
    ("v04", O / "study1_v0.4", "RUN_MANIFEST_IKR.json", R / "STUDY1_PROTOCOL_v0.4.md", R / "study1_v04",
     "Study 1 v0.4", "Fluent, non-repetitive forgery (perplexity and seq-rep-4 conditions on both sides)",
     "integrity check; F1; F3",
     "F1 as v0.3 with the repetition term"),
    ("s3", O / "study3_v0.1", "RUN_MANIFEST.json", R / "STUDY3_PROTOCOL_v0.1.md", R / "study3",
     "Study 3", "The exact key test: power, per-key calibration, Study 1's forgeries re-scored",
     "G1 pooled FPR; G2 per-key calibration; P1 working test; X1 forgery practical; X3 generic steering; E1 power against the probe; H1 human text",
     "G1: pooled FPR in [0.3, 2.5]%; G2: per-key FPR ≤ 3%; P1: TPR ≥ 20%; X1: exact-FA ≥ 50% of the oracle's"),
    ("s2", O / "study2_v0.1", "RUN_MANIFEST.json", R / "STUDY2_PROTOCOL_v0.1.md", R / "study2",
     "Study 2", "Scrubbing under the exact test at matched quality: paraphrase and key-guided edits",
     "G1, G2 per paraphraser; P1; S1 paraphrase effective; S2 edits effective; C1 the estimate helps",
     "S1, S2: success ≥ 50% and the lower bound above the comparator (the originals' miss rate; random edits)"),
    ("s5", O / "study5_v0.1", "RUN_MANIFEST.json", R / "STUDY5_PROTOCOL_v0.1.md", R / "study5",
     "Study 5", "Context-keyed (h = 1, 4) and rotating (K = 8) directions against the gradient-averaging attacker",
     "G1, G2; P0 the threat; P1 usability; D1 stealing; D2 robustness cost; D3 quality cost",
     "D1: FA ≥ 50% of the arm's genuine FA; D2: 20 points of scrub success; D3: perplexity ratio 1.10"),
]

# where each study's results.json hash was recorded by a later lock (or by its own manifest)
RESULTS_HASH_RECORDED_IN = {
    "v02": (O / "study1_v0.3" / "PRE_RUN_LOCK.json", "input_sha256", "research/outputs/study1_v0.2/results.json"),
    "v03": (O / "study1_v0.4" / "PRE_RUN_LOCK.json", "input_sha256", "research/outputs/study1_v0.3/results.json"),
    "v04": (O / "study3_v0.1" / "PRE_RUN_LOCK.json", "input_sha256", "research/outputs/study1_v0.4/results.json"),
    "s3": (O / "study2_v0.1" / "PRE_RUN_LOCK.json", "input_sha256", "research/outputs/study3_v0.1/results.json"),
    "s2": (O / "study2_v0.1" / "RUN_MANIFEST.json", "results_sha256", None),
    "s5": (O / "study5_v0.1" / "RUN_MANIFEST.json", "results_sha256", None),
}


def run_seconds(man):
    return float(man.get("total_seconds", man.get("seconds")))


def design_levels(lock, code_dir):
    d = lock["design"]
    return d.get("levels_rho") or d.get("levels")


def n_grid(sid, lock, code_dir):
    d = lock["design"]
    if sid == "v02":
        return (C.const_from_code(code_dir / "common.py", "N_GRID"), C.const_from_code(code_dir / "common.py", "FORGE_N"))
    if sid in ("v03", "v04"):
        return (None, d["forge_n"])
    if sid == "s5":
        return (d["n_grid"], d["n_grid"])
    return (None, None)


rows, total_s = [], 0.0
for sid, odir, mfile, proto, code_dir, name, question, rules, bars in STUDIES:
    lock = C.load(odir / "PRE_RUN_LOCK.json")
    man = C.load(odir / mfile)
    # --- integrity: the protocol file still hashes as locked; the manifest's lock copy agrees; the commit exists
    assert C.sha256(proto) == lock["protocol_sha256"], f"{name}: protocol file changed since the lock"
    if "lock" in man:
        assert man["lock"]["protocol_sha256"] == lock["protocol_sha256"], f"{name}: manifest lock copy differs"
    if "protocol_sha256" in man:
        assert man["protocol_sha256"] == lock["protocol_sha256"], f"{name}: manifest protocol hash differs"
    assert C.git_commit_exists(lock["git_commit_before_lock"]), f"{name}: lock commit missing from the repository"
    assert lock["final"] is False and "LOCKED" in lock["status"], f"{name}: unexpected lock status"
    # --- the code files hashed in the lock still hash the same (locked code is never edited)
    for fn, h in lock["code_sha256"].items():
        p = (R / fn) if fn.startswith("research/") else (code_dir / fn)
        if not p.exists():                       # earlier-version files live in their own folders
            cands = list(R.glob(f"study*/{Path(fn).name}")) + list(R.glob(f"*/{Path(fn).name}"))
            cands = [c for c in cands if C.sha256(c) == h]
            assert cands, f"{name}: locked code file {fn} not found with hash {h[:12]}"
        else:
            assert C.sha256(p) == h, f"{name}: locked code file {fn} changed"
    # --- the results file hashes as a later lock (or the manifest) recorded
    res = odir / "results.json"
    src, field, key = RESULTS_HASH_RECORDED_IN[sid]
    rec = C.load(src)[field]
    rec = rec[key] if key else rec
    assert C.sha256(res) == rec, f"{name}: results.json differs from the hash recorded in {src.name}"
    secs = run_seconds(man)
    assert secs > 0
    total_s += secs
    levels = design_levels(lock, code_dir)
    keys = lock["design"].get("study_keys") or f"{min(lock['design']['keys'])}–{max(lock['design']['keys'])}"
    n_rec, n_forge = n_grid(sid, lock, code_dir)
    n_txt = ""
    if n_rec and n_forge and n_rec != n_forge:
        n_txt = f"recovery {{{', '.join(f'{n:,}' for n in n_rec)}}}; forgery {{{', '.join(f'{n:,}' for n in n_forge)}}}"
    elif n_forge:
        n_txt = "{" + ", ".join(f"{n:,}" for n in n_forge) + "}"
    else:
        n_txt = "Study 1's texts re-scored" if sid == "s3" else "Study 1's texts scrubbed"
    n_code, n_reused = len(lock["code_sha256"]), sum(len(v) for k, v in lock.items() if k.startswith("reused") and isinstance(v, dict))
    rows.append([name, question, rules, bars, f"{str(keys).replace('-', '–')}; ρ ∈ {{{', '.join(f'{x:.2f}' for x in levels)}}}", n_txt,
                 f"{C.utc_date(lock['locked_utc'])}; `{lock['protocol_sha256'][:12]}`", f"`{lock['git_commit_before_lock'][:8]}`",
                 C.f1(C.hours(secs)), f"`{res.relative_to(C.ROOT)}`"])
    # --- registered values
    V.set(f"t1_{sid}_lock_date", C.utc_date(lock["locked_utc"]))
    V.set(f"t1_{sid}_lock_stamp", C.utc_stamp(lock["locked_utc"]))
    V.set(f"t1_{sid}_hours", C.f1(C.hours(secs)))
    V.set(f"t1_{sid}_commit", lock["git_commit_before_lock"][:8])
    V.set(f"t1_{sid}_protocol_hash12", lock["protocol_sha256"][:12])
    V.set(f"t1_{sid}_n_code_files", n_code)
    V.set(f"t1_{sid}_n_reused_files", n_reused)
    V.set(f"t1_{sid}_levels", ", ".join(f"{x:.2f}" for x in levels))
    V.set(f"t1_{sid}_n_levels", len(levels))

# design constants shared by every study (from the v0.2 lock and code; the later locks reuse them unchanged)
l02 = C.load(O / "study1_v0.2" / "PRE_RUN_LOCK.json")
model_line = l02["model"]                      # 'Qwen/Qwen2.5-1.5B@<rev>; layer 14; k = 4; N = 56.90…'
mid, rest = model_line.split("@", 1)
rev = rest.split(";")[0]
manifest = C.load(R / "pilot" / "outputs" / "model_manifest_qwen2.5-1.5b.json")
assert manifest["model_id"] == mid and manifest["revision"] == rev, "model manifest and lock disagree"
V.set("model_id", mid)
V.set("model_revision8", rev[:8])
V.set("model_license", manifest["license"].split(" ")[0])
V.set("layer", int(rest.split("layer ")[1].split(";")[0]))
V.set("k_support", int(rest.split("k = ")[1].split(";")[0]))
N = float(rest.split("N = ")[1])
V.set("N_ref", C.f2(N))
V.set("d_model", C.const_from_code(R / "study1_v02" / "common.py", "D_MODEL"))
V.set("n_layers", C.const_from_code(R / "study1_v02" / "common.py", "N_LAYERS"))
V.set("study_keys", l02["design"]["study_keys"].replace("-", "–"))
V.set("n_keys", len(C.const_from_code(R / "study1_v02" / "common.py", "STUDY_KEYS")))
V.set("control_keys", l02["design"]["control_keys"].replace("-", "–"))
V.set("levels_all", ", ".join(f"{x:.2f}" for x in l02["design"]["levels_rho"]))
# the budget grids are quoted inside math in the prose, so no thousands separators here (the table formats its own)
V.set("n_grid_recovery", ", ".join(str(n) for n in C.const_from_code(R / "study1_v02" / "common.py", "N_GRID")))
V.set("n_grid_forgery", ", ".join(str(n) for n in C.const_from_code(R / "study1_v02" / "common.py", "FORGE_N")))
V.set("n_forge_texts", C.const_from_code(R / "study1_v02" / "common.py", "N_FORGE_TEXTS"))
V.set("fpr_nominal_pct", f"{100 * C.const_from_code(R / 'study1_v02' / 'common.py', 'FPR'):g}")
core = R / "study1" / "core.py"
V.set("new_tokens", C.const_from_code(core, "NEW_TOKENS"))
V.set("sparsity", C.const_from_code(core, "SPARSITY"))
V.set("n_null_keys", C.const_from_code(core, "N_NULL_KEYS"))
gen = Path(core).read_text()
import re  # noqa: E402
for nm, pat in (("temperature", r"temperature=([0-9.]+)"), ("top_p", r"top_p=([0-9.]+)"), ("top_k", r"top_k=(\d+)"), ("repetition_penalty", r"repetition_penalty=([0-9.]+)")):
    V.set(f"gen_{nm}", re.search(pat, gen).group(1))
# pools and prompt sets
iv = C.load(O / "study1_v0.2" / "INPUT_VALIDATION.json")["checks"]
sizes = iv["pools_sizes_disjoint_dev_only"]["sizes"]
for pool, n in sizes.items():
    V.set(f"pool_{pool}", f"{n:,}")
V.set("pool_A", f"{sizes['A1'] + sizes['A2']:,}")
ps = C.load(R / "stage4" / "outputs" / "prompt_sets_v0.3.json")
for corpus in ("c4", "wikitext"):
    counts = ps[corpus]["counts"]
    for split in ("dev", "holdout", "usable"):
        n = counts.get(split)
        if n is None:
            cands = [v for k, v in counts.items() if split in k and isinstance(v, int)]
            n = cands[0] if cands else None
        assert n is not None, f"prompt set count for {corpus} {split} not found: keys {list(counts)}"
        V.set(f"prompts_{corpus}_{split}", f"{n:,}")
    assert counts.get("dev", 0) + counts.get("holdout", 0) == counts.get("usable", counts.get("dev", 0) + counts.get("holdout", 0)), corpus
V.set("prompts_c4_records", f"{ps['c4']['records']:,}")
V.set("prompts_c4_parse_failures", ps["c4"]["parse_failures"])
assert ps["proceed_result"] == "PASS"
# the scrubbing quality bars (Study 2's input validation re-computed them and asserted them equal to the pilot's)
bars = C.load(O / "study2_v0.1" / "INPUT_VALIDATION.json")["checks"]["2_bars_equal_pilot"]
assert bars["pass"] is True and bars["max_abs_diff"] == 0.0
B = bars["bars"]
V.set("bar_human_p95_ppl", C.f1(B["A"]["ppl"]))
V.set("bar_human_p95_rep", C.f3(B["A"]["rep"]))
V.set("bar_cos_p95", C.f3(B["A"]["cos"]))
V.set("bar_attacker_p95_ppl", C.f1(B["C"]["ppl"]))
V.set("bar_attacker_p95_rep", C.f3(B["C"]["rep"]))
V.set("bar_attacker_cos_p95", C.f3(B["C"]["cos"]))
V.set("bar_model_p95_ppl", C.f1(B["A_model_p95"]["ppl"]))
V.set("bar_human_median_ppl", C.f1(B["A_human_median"]["ppl"]))
# run times
V.set("t1_total_hours", C.f1(C.hours(total_s)))
V.set("t1_n_studies", len(STUDIES))
torch_versions = {C.load(odir / mfile).get("torch") for _, odir, mfile, *_ in STUDIES} - {None}
V.set("torch_version", ", ".join(sorted(torch_versions)))

C.write_table("T1", ["Study", "Question", "Pre-registered rules", "Materiality bars", "Keys; strengths ρ", "Attacker budget n",
                     "Locked (UTC date); protocol SHA-256", "Commit", "Run (h)", "Results"], rows,
              "The six locked studies: question, pre-registered rules and bars, design, lock and run",
              ["Every hash shown equals the study's `PRE_RUN_LOCK.json`; the protocol files, the locked code files and the results files were re-hashed when this table was built and equal the locked values. Pilots and specifications are in Table TA1.",
               f"Prompt pools (C4 development units assigned once by hash rank; §4): A {V.d['pool_A']} (the owner's unwatermarked null texts and their human continuations; A1 for the probe's threshold, A2 for its false-positive check), B {V.d['pool_B']} (the attacker's observed texts), C {V.d['pool_C']} (the attacker's unwatermarked reference texts), D {V.d['pool_D']} (the evaluation prompts), E {V.d['pool_E']} and F {V.d['pool_F']} (the probe's training texts; the per-position statistics)."])
p = V.save()
print("T1 written; values:", p.name, len(V.d))
