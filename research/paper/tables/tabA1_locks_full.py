"""TA1 — the full lock table (Appendix A): every protocol (LOCKED before outcomes), every fixed specification (pilots,
calibrations, the threat check, the addendum) and the prompt-set freeze, with the hash recorded at the time, the date,
the commit, the validation outcome, the run time and the outcome file. Asserts that every protocol and spec file still
hashes as its lock or run guard recorded (the status line set to LOCKED or FIXED is part of the hashed file), and that
validation files report all checks passed where they exist. Writes build/tabA1.md and build/values_tabA1.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

R, O = C.RESEARCH, C.OUT
V = C.Values("tabA1")


def n_checks(validation):
    """(passed, total, all_pass) over every check record in the file: a dict holding a boolean 'pass' (the v0.2+ layout
    is {'checks': {name: {'pass': bool, ...}}}; Study 1 v0.1's files hold the check records at other depths)."""
    found = []

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("pass"), bool):
                found.append(x["pass"])
                return
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(validation.get("checks", validation))
    return sum(found), len(found), validation.get("all_pass", validation.get("all_checks_pass", all(found) if found else None))


def row(item, kind, date, hash12, n_code, n_reused, commit, validation, run_h, outcome):
    return [item, kind, date, f"`{hash12}`" if hash12 else "—", n_code if n_code is not None else "—",
            n_reused if n_reused is not None else "—", f"`{commit[:8]}`" if commit else "—", validation,
            C.f1(run_h) if run_h else "—", outcome]


rows = []

# ---------------------------------------------------------------- the prompt-set freeze (Stage 4)
ps = C.load(R / "stage4" / "outputs" / "prompt_sets_v0.3.json")
spec = R / ps["spec"].split("research/")[1] if ps["spec"].startswith("research/") else R / "stage4" / "PROMPT_SETS_SPEC_v0.3.md"
assert spec.exists(), spec
rows.append(row("Prompt sets v0.3 (C4 realnewslike dev and holdout; WikiText-103)", "freeze (proceed rule PASS)", "2026-09-25", None, None,
                len(ps["frozen_files"]), None, f"proceed rules {len(ps['proceed_rules'])}: {ps['proceed_result']}", None,
                "`research/stage4/outputs/prompt_sets_v0.3.json`"))
assert ps["proceed_result"] == "PASS"
V.set("ta1_prompt_frozen_files", len(ps["frozen_files"]))

# ---------------------------------------------------------------- reproduction pilot and calibrations (specs fixed before runs; tuning keys)
for name, spec, outs, label in [
    ("Reproduction pilot v0.1 (the authors' probe at α = 5, 10, 20; Qwen2.5-1.5B and Llama-3.2-1B)", R / "repro" / "REPRO_PILOT_SPEC_v0.1.md",
     [O / "repro_v0.1" / "results_qwen.json", O / "repro_v0.1" / "results_llama.json"], "`research/outputs/repro_v0.1/`"),
    ("Calibration v0.1 (ρ grid, 256 tokens; two models)", R / "repro" / "CALIBRATION_SPEC_v0.1.md",
     [O / "calibration_v0.1" / "results_qwen.json", O / "calibration_v0.1" / "results_llama.json"], "`research/outputs/calibration_v0.1/`"),
    ("Calibration v0.2 (512 tokens; two models)", R / "repro" / "CALIBRATION_SPEC_v0.2.md",
     [O / "calibration_v0.2" / "results_qwen.json", O / "calibration_v0.2" / "results_llama.json"], "`research/outputs/calibration_v0.2/`"),
    ("Calibration v0.3 (Llama-3.2-3B)", R / "repro" / "CALIBRATION_SPEC_v0.3.md",
     [O / "calibration_v0.3" / "results_llama3b.json"], "`research/outputs/calibration_v0.3/`"),
]:
    metas = [C.load(p)["meta"] for p in outs]
    hs = {m["spec_sha256"] for m in metas}
    assert len(hs) == 1, f"{name}: the output files record different spec hashes"
    h = hs.pop()
    assert C.sha256(spec) == h, f"{name}: spec file changed since the run ({spec.name})"
    date = None
    for m in metas:
        for k in ("date_utc", "utc", "run_utc", "finished_utc"):
            if k in m:
                date = str(m[k])[:10]
    ops = [C.load(p).get("operating_point", "n/a") for p in outs]
    is_cal = "CALIBRATION" in spec.name
    rows.append(row(name, "spec fixed before the run", date or "2026-09-25", h[:12], 1, None, None,
                    f"detectable-and-fluent operating point: {', '.join('none' if o is None else str(o) for o in ops)}" if is_cal
                    else "the authors' probe did not reproduce on Qwen at α ≤ 20; on Llama-3.2-1B only with damaged text",
                    None, label))
    if is_cal:
        assert all(o is None for o in ops), f"{name}: an operating point exists"
V.set("ta1_calibration_operating_points_none", True)

# ---------------------------------------------------------------- Study 1 v0.1 (stopped at G1)
l = C.load(O / "study1_v0.1" / "PRE_RUN_LOCK.json")
assert C.sha256(R / "STUDY1_PROTOCOL_v0.1.md") == l["protocol_sha256"]
vq, vl = C.load(O / "study1_v0.1" / "qwen" / "INPUT_VALIDATION.json"), C.load(O / "study1_v0.1" / "llama" / "INPUT_VALIDATION.json")
pq, tq, aq = n_checks(vq)
pl, tl, al = n_checks(vl)
rows.append(row("Study 1 v0.1 (key recovery and spoofing; training-free cosine detector; stopped at gate G1)", "protocol LOCKED before outcomes",
                C.utc_date(l["locked_utc"]), l["protocol_sha256"][:12], len(l["script_sha256"]), None, l["git_commit_before_lock"],
                f"Qwen {pq}/{tq}, Llama {pl}/{tl} checks passed", None, "G1 failed (D-cos TPR 0% at α = 5, 10); `research/outputs/study1_v0.1/`"))
assert C.git_commit_exists(l["git_commit_before_lock"])
V.set("ta1_v01_lock_date", C.utc_date(l["locked_utc"]))

# ---------------------------------------------------------------- the six locked studies (as T1, with validation counts)
for name, odir, mfile, proto in [
    ("Study 1 v0.2 (recovery and forgery against the probe along ρ)", O / "study1_v0.2", "RUN_MANIFEST_SKR.json", R / "STUDY1_PROTOCOL_v0.2.md"),
    ("Study 1 v0.3 (fluent forgery; perplexity condition)", O / "study1_v0.3", "RUN_MANIFEST_IKR.json", R / "STUDY1_PROTOCOL_v0.3.md"),
    ("Study 1 v0.4 (fluent, non-repetitive forgery)", O / "study1_v0.4", "RUN_MANIFEST_IKR.json", R / "STUDY1_PROTOCOL_v0.4.md"),
    ("Study 3 (the exact key test)", O / "study3_v0.1", "RUN_MANIFEST.json", R / "STUDY3_PROTOCOL_v0.1.md"),
    ("Study 2 (scrubbing under the exact test)", O / "study2_v0.1", "RUN_MANIFEST.json", R / "STUDY2_PROTOCOL_v0.1.md"),
    ("Study 5 (context-keyed and rotating directions)", O / "study5_v0.1", "RUN_MANIFEST.json", R / "STUDY5_PROTOCOL_v0.1.md"),
]:
    l, m, iv = C.load(odir / "PRE_RUN_LOCK.json"), C.load(odir / mfile), C.load(odir / "INPUT_VALIDATION.json")
    assert C.sha256(proto) == l["protocol_sha256"], name
    p_, t_, a_ = n_checks(iv)
    assert a_ is True and p_ == t_, f"{name}: validation not all passed ({p_}/{t_})"
    secs = float(m.get("total_seconds", m.get("seconds")))
    n_reused = sum(len(v) for k, v in l.items() if k.startswith("reused") and isinstance(v, dict))
    dev = m.get("deviations")
    dev_txt = "" if not dev or dev == ["none"] else f"; deviations: {dev}"
    rows.append(row(name, "protocol LOCKED before outcomes", C.utc_date(l["locked_utc"]), l["protocol_sha256"][:12], len(l["code_sha256"]),
                    n_reused or None, l["git_commit_before_lock"], f"{p_}/{t_} checks passed{dev_txt}", C.hours(secs),
                    f"`{(odir / 'results.json').relative_to(C.ROOT)}`"))
    tag = odir.name.replace("study", "s").replace("_v0.", "").replace("1", "1v", 1) if odir.name.startswith("study1") else odir.name.split("_")[0]
    V.set(f"ta1_{odir.name}_checks", f"{p_}/{t_}")

# ---------------------------------------------------------------- fixed specifications with run guards (pilots, the threat check, the addendum)
def guard_row(name, spec, res_path, guard_key="guard", validation=None, run_h=None, outcome=None, kind="spec FIXED before the run (tuning keys)"):
    res = C.load(res_path)
    g = res[guard_key]
    h = g.get("spec_sha256") or g.get("sha256", {}).get(spec.name)
    assert h, f"{name}: no spec hash in the guard"
    assert C.sha256(spec) == h, f"{name}: spec changed since the run ({spec.name})"
    commit = g.get("commit")
    if commit:
        assert C.git_commit_exists(commit), f"{name}: guard commit missing"
    val_txt = "—"
    if validation is not None:
        vj = C.load(validation)
        p_, t_, a_ = n_checks(vj)
        assert a_ is True, f"{name}: validation not all passed"
        val_txt = f"{p_}/{t_} checks passed"
    elif "all_checks_pass" in res:
        ch = res.get("checks", {})
        val_txt = f"{sum(1 for c in ch.values() if isinstance(c, dict) and c.get('pass'))}/{len(ch)} checks passed" + ("" if res["all_checks_pass"] else " (one failed; see the spec's successor)")
    elif "validation_all_pass" in res:
        val_txt = "all validation checks passed" if res["validation_all_pass"] else "validation failed"
    date = g.get("utc", g.get("date_utc", ""))[:10] or None
    n_code = len(g["sha256"]) if isinstance(g.get("sha256"), dict) else (1 + ("script_sha256" in g) + ("core_sha256" in g))
    rows.append(row(name, kind, date or "—", h[:12], n_code, None, commit, val_txt, run_h, outcome or f"`{res_path.relative_to(C.ROOT)}`"))
    return res


r3p = guard_row("Study 3 power pilot v0.1 (statistics S1–S4; the selection rule)", R / "study3_pilot" / "POWER_PILOT_SPEC_v0.1.md",
                O / "study3_pilot_v0.1" / "results.json", validation=O / "study3_pilot_v0.1" / "VALIDATION.json",
                outcome="S1 fails the implementation check; no primary by the rule; S4 chosen by decision; `research/outputs/study3_pilot_v0.1/`")
rows[-1][2] = "2026-09-30"   # the guard records the commit, not a date; the lock of Study 3 the same day fixes it (results.json has no timestamp)
r2a = guard_row("Study 2 scrubbing pilot v0.1 (paraphrase, edits, bars, timing)", R / "study2_pilot" / "SCRUB_PILOT_SPEC_v0.1.md",
                O / "study2_pilot_v0.1" / "results.json", run_h=sum(C.load(O / "study2_pilot_v0.1" / "results.json").get("times_s", {}).values()) / 3600 or None,
                outcome="checks I1 and I5 failed (bf16 editor; time); fixed in v0.2; `research/outputs/study2_pilot_v0.1/`")
r2b = guard_row("Study 2 scrubbing pilot v0.2 (float32 editor; revised timing)", R / "study2_pilot" / "SCRUB_PILOT_SPEC_v0.2.md",
                O / "study2_pilot_v0.2" / "results.json", outcome="all checks pass; `research/outputs/study2_pilot_v0.2/`")
rt = guard_row("Study 5 threat check v0.1 (Route A′ on the tuning keys)", R / "study5_pilot" / "THREAT_CHECK_SPEC_v0.1.md",
               O / "study5_threat_v0.1" / "results.json", guard_key="run_guard", validation=O / "study5_threat_v0.1" / "VALIDATION.json",
               outcome="verdict: threat real; `research/outputs/study5_threat_v0.1/results.json`")
rows[-1][2] = "2026-10-02"
rp = guard_row("Study 5 defence pilot v0.1 (the keyed scheme's machinery; tuning keys)", R / "study5_pilot" / "DEFENCE_PILOT_SPEC_v0.1.md",
               O / "study5_pilot_v0.1" / "results.json", guard_key="run_guard", validation=O / "study5_pilot_v0.1" / "VALIDATION.json",
               run_h=C.load(O / "study5_pilot_v0.1" / "results.json")["run_guard"]["elapsed_s"] / 3600,
               outcome="rates for the Study 5 protocol; `research/outputs/study5_pilot_v0.1/`")
rows[-1][2] = "2026-10-02"
# the rotation addendum: post hoc, labelled; its spec is FIXED and its JSON names the spec
add = C.load(O / "study5_v0.1" / "ADDENDUM_ROTATION.json")
spec_add = R / "study5_addendum" / "ROTATION_ADDENDUM_SPEC_v0.1.md"
assert add["spec"] == spec_add.name and "**Status: FIXED**" in spec_add.read_text()
rows.append(row("Study 5 rotation addendum (every-cluster forging at ρ = 0.35)", "post hoc, labelled; spec FIXED before its run; not pre-registered",
                "2026-10-04", C.sha256(spec_add)[:12], 1, None, None, "n/a (exploratory)", None, "`research/outputs/study5_v0.1/ADDENDUM_ROTATION.json`"))

V.set("ta1_n_rows", len(rows))
V.set("ta1_n_locked_protocols", 7)        # v0.1–v0.4, Study 3, Study 2, Study 5
V.set("ta1_n_fixed_specs", 10)            # repro, calibrations ×3, power pilot, scrub pilots ×2, threat check, defence pilot, addendum
assert V.d["ta1_n_locked_protocols"] + V.d["ta1_n_fixed_specs"] + 1 == len(rows), (len(rows))

C.write_table("TA1", ["Item", "Kind", "Date (UTC)", "Protocol or spec SHA-256", "Code files hashed", "Reused files hashed", "Commit",
                      "Validation", "Run (h)", "Outcome"], rows,
              "Every pre-registered protocol, fixed specification and freeze of the project, in order",
              ["A protocol or specification is hashed with its status line set to LOCKED or FIXED; the runners refuse to start if any hash differs, and the hashes shown were re-computed from the files in the repository when this table was built. 'Reused files' are the earlier studies' locked data and outputs that a later lock hashes so that no reused input can change. Dates for the guarded specifications are the run dates recorded in the decision log where the output file records a commit but no timestamp."])
p = V.save()
print("TA1 written; rows:", len(rows), "values:", p.name, len(V.d))
