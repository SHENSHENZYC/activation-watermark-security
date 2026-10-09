"""T3 — forging the trained probe without the key (§5.2): (a) per strength and route, Study 1 v0.2's plain acceptance at
n = 64 / 256 / 1,024 beside v0.4's fluent, non-repetitive acceptance (FA) at n = 64 / 256 with the F1 bar and verdict, the
oracle and random-key controls and the F3 reading; (b) Route A's key recovery in v0.2 (R1) and what the repetition
condition changed for v0.3's Route B forgeries at ρ = 0.70. Reads study1_v0.2, study1_v0.3 and study1_v0.4 results.json;
re-computes every median from the per-key rates, re-derives L1, R1, G1, the v0.4 F1 and F3 verdicts and v0.2's
'practical' verdicts from the rules, and asserts them; writes build/T3a.md, build/T3b.md and build/values_tab3.json.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

V = C.Values("tab3")
r2 = C.load(C.OUT / "study1_v0.2" / "results.json")
r3 = C.load(C.OUT / "study1_v0.3" / "results.json")
r4 = C.load(C.OUT / "study1_v0.4" / "results.json")
assert r3["integrity"]["pass"] is True and r4["integrity"]["pass"] is True
LEVELS = ["0.25", "0.35", "0.5", "0.7"]
LATE = ["0.35", "0.5", "0.7"]
T = lambda rho: rho.replace(".", "")  # noqa: E731


def chk(d):
    """A {per_key, median, ci95} summary: the median is the median of the per-key rates (re-counted)."""
    assert len(d["per_key"]) == 8 and abs(float(np.median(d["per_key"])) - d["median"]) < 1e-12
    assert d["ci95"][0] <= d["median"] <= d["ci95"][1]
    return d


# ---------------------------------------------------------------- v0.2: gates, L1, R1, R2 'practical'
g1 = 100 * r2["G1_pooled_FPR_A2"]
assert r2["gates"]["G1"] is (0.3 <= g1 <= 2.5)
V.set("t3_v02_G1_pct", C.f1(g1))
V.set("t3_v02_human_fpr_pct", C.f1(100 * r2["human_FPR_A2"]))
cosA_all, hitsA_all = [], []
for rho in LEVELS:
    L = r2["levels"][rho]
    for c in ("oracle", "random") + tuple(f"forge_{r}_n{n}" for r in "AB" for n in (64, 256, 1024)):
        chk(L[c])
    assert L["rules"]["L1_working_watermark"] is (L["oracle"]["median"] >= 0.20), rho
    rec = L["recovery"]
    r1_ok = any(rec[n]["median_cos_A"] >= 0.9 and rec[n]["layer_hits_A"] >= 7 for n in rec)
    assert (not r1_ok) == L["rules"]["R1"].endswith("fails at this budget"), rho
    for route in "AB":
        verdict = L["rules"]["R2"][route]
        prac = [n for n in (64, 256, 1024) if L[f"forge_{route}_n{n}"]["median"] >= 0.5 * L["oracle"]["median"]
                and L[f"forge_{route}_n{n}"]["ci95"][0] > L["random"]["ci95"][1]]
        if "practical (n=" in verdict:
            assert verdict.endswith(f"practical (n={prac[0]})"), (rho, route, verdict, prac)
        else:
            assert not prac or "inconclusive" in verdict or "not practical" in verdict, (rho, route)
        V.set(f"t3_v02_R2_{route}_{T(rho)}", verdict.replace("(descriptive) ", ""))
        for n in (64, 256, 1024):
            V.set(f"t3_v02_{route}_n{n}_acc_{T(rho)}", C.pct(L[f"forge_{route}_n{n}"]["median"]))
    assert L["rules"]["R3_generic_steering_suffices"] is (L["random"]["median"] >= 0.5 * L["oracle"]["median"]), rho
    V.set(f"t3_v02_L1_{T(rho)}", "pass" if L["rules"]["L1_working_watermark"] else "fail")
    V.set(f"t3_v02_R1_{T(rho)}", L["rules"]["R1"].replace("(descriptive) ", ""))
    V.set(f"t3_v02_R3_{T(rho)}", "yes" if L["rules"]["R3_generic_steering_suffices"] else "no")
    V.set(f"t3_v02_oracle_acc_{T(rho)}", C.pct(L["oracle"]["median"]))
    V.set(f"t3_v02_random_acc_{T(rho)}", C.pct(L["random"]["median"]))
    V.set(f"t3_v02_random_acc_ci_{T(rho)}", C.pct_ci(L["random"]))
    for n in (64, 256, 1024):
        V.set(f"t3_v02_A_cos_n{n}_{T(rho)}", C.f2(rec[str(n)]["median_cos_A"]))
        V.set(f"t3_v02_A_hits_n{n}_{T(rho)}", rec[str(n)]["layer_hits_A"])
        cosA_all.append(rec[str(n)]["median_cos_A"])
        hitsA_all.append(rec[str(n)]["layer_hits_A"])
V.set("t3_v02_A_cos_max", C.f2(max(cosA_all)))
V.set("t3_v02_A_hits_max", max(hitsA_all))
V.set("t3_v02_B_n64_acc_min_late", C.pct(min(r2["levels"][r]["forge_B_n64"]["median"] for r in LATE)))
V.set("t3_v02_B_n64_acc_max_late", C.pct(max(r2["levels"][r]["forge_B_n64"]["median"] for r in LATE)))


# ---------------------------------------------------------------- v0.4: F1 and F3 re-derived
def f1_verdict(L, route):
    bar, ru = 0.5 * L["oracle"]["FA"]["median"], L["random"]["FA"]["ci95"][1]
    sets = {n: L[f"v04_{route}_n{n}"]["FA"] for n in (64, 256)}
    prac = [n for n, s in sets.items() if s["median"] >= bar and s["ci95"][0] > ru]
    if prac:
        return f"practical (n={prac[0]})"
    if all(s["ci95"][1] < bar for s in sets.values()):
        return "not practical"
    return "inconclusive"


rows_a = []
for rho in LATE:
    L = r4["levels"][rho]
    for c in ("oracle", "random") + tuple(f"{v}_{r}_n{n}" for v in ("v02", "v03", "v04") for r in "AB" for n in (64, 256)):
        chk(L[c]["FA"])
        chk(L[c]["acceptance"])
    bar = 0.5 * L["oracle"]["FA"]["median"]
    for route in "AB":
        assert f1_verdict(L, route) == L["rules"]["F1"][route], (rho, route)
    assert L["rules"]["F3_fluent_generic_steering_suffices"] is (L["random"]["FA"]["median"] >= bar), rho
    t = T(rho)
    V.set(f"t3_v04_oracle_FA_{t}", C.pct(L["oracle"]["FA"]["median"]))
    V.set(f"t3_v04_oracle_FA_ci_{t}", C.pct_ci(L["oracle"]["FA"]))
    V.set(f"t3_v04_oracle_acc_{t}", C.pct(L["oracle"]["acceptance"]["median"]))
    V.set(f"t3_v04_random_FA_{t}", C.pct_ci(L["random"]["FA"]))
    V.set(f"t3_v04_random_FA_hi_{t}", C.pct(L["random"]["FA"]["ci95"][1]))
    V.set(f"t3_v04_bar_{t}", C.pct(bar))
    V.set(f"t3_v04_F3_{t}", "yes" if L["rules"]["F3_fluent_generic_steering_suffices"] else "no")
    L2 = r2["levels"][rho]
    rows_a.append([rho, "oracle (true key, true layer)", "—", f"{C.pct(L2['oracle']['median'])} / — / —", C.pct_ci(L["oracle"]["FA"]), "—", "ceiling", "—"])
    rows_a.append([rho, "random key (generic steering)", "—", f"{C.pct(L2['random']['median'])} / — / —", C.pct_ci(L["random"]["FA"]), "—",
                   f"F3 generic steering suffices: {'yes' if L['rules']['F3_fluent_generic_steering_suffices'] else 'no'}", "—"])
    for route, name in (("A", "Route A: key recovery (activation mean)"), ("B", "Route B: footprint imitation")):
        plain = " / ".join(C.pct(L2[f"forge_{route}_n{n}"]["median"]) for n in (64, 256, 1024))
        fa64, fa256 = L[f"v04_{route}_n64"]["FA"], L[f"v04_{route}_n256"]["FA"]
        rows_a.append([rho, name, L2["rules"]["R2"][route].replace("(descriptive) ", ""), plain, f"{C.pct_ci(fa64)} / {C.pct_ci(fa256)}", C.pct(bar),
                       L["rules"]["F1"][route], C.f3(L["attacks"][f"{route}_n256"]["median_cos_true"])])
        for n in (64, 256):
            V.set(f"t3_v04_{route}_n{n}_FA_{t}", C.pct_ci(L[f"v04_{route}_n{n}"]["FA"]))
            V.set(f"t3_v04_{route}_n{n}_FA_med_{t}", C.pct(L[f"v04_{route}_n{n}"]["FA"]["median"]))
            V.set(f"t3_v04_{route}_n{n}_FA_lo_{t}", C.pct(L[f"v04_{route}_n{n}"]["FA"]["ci95"][0]))
            V.set(f"t3_v04_{route}_n{n}_FA_hi_{t}", C.pct(L[f"v04_{route}_n{n}"]["FA"]["ci95"][1]))
            V.set(f"t3_v04_{route}_n{n}_acc_{t}", C.pct(L[f"v04_{route}_n{n}"]["acceptance"]["median"]))
# descriptive 0.25 row (L1 fails there; v0.2 only)
L025 = r2["levels"]["0.25"]
rows_a.insert(0, ["0.25", "oracle (true key, true layer); descriptive, L1 fails", "—", f"{C.pct(L025['oracle']['median'])} / — / —", "—", "—", "watermark not working (L1)", "—"])
C.write_table("T3a", ["ρ", "texts", "v0.2 R2 verdict (plain acceptance)", "v0.2 plain acceptance at n = 64 / 256 / 1,024 (%)",
                      "v0.4 FA at n = 64 / 256 (%) [95% CI]", "F1 bar: half the oracle FA (%)", "v0.4 F1 verdict", "Route vector's cosine with the key (v0.4, n = 256)"],
              rows_a, "Forging the owner's trained probe without the key (Study 1 v0.2 and v0.4; medians over 8 keys)",
              ["Plain acceptance: the probe accepts the text at its 1% threshold (v0.2's rule). FA (v0.4's rule): accepted and no less fluent and no more "
               "repetitive than the key's own genuine watermarked texts (perplexity and seq-rep-4 at most their 95th percentiles). F1 practical: at some n the "
               "median FA reaches half the oracle's and its lower bound exceeds the random key's upper bound; not practical: both n's upper bounds fall below "
               "the bar; otherwise inconclusive. v0.2's R2 uses plain acceptance with the same practical clause. The random-key row's verdict is F3."])

# ---------------------------------------------------------------- (b) recovery in v0.2 and the v0.3 repetition note
rows_b = []
for rho in LEVELS:
    rec = r2["levels"][rho]["recovery"]
    rows_b.append([rho, "Route A key recovery (v0.2)", " / ".join(C.f2(rec[str(n)]["median_cos_A"]) for n in (64, 256, 1024)),
                   " / ".join(str(rec[str(n)]["layer_hits_A"]) for n in (64, 256, 1024)), r2["levels"][rho]["rules"]["R1"].replace("(descriptive) ", "")])
for n in (64, 256):
    s3 = r4["levels"]["0.7"][f"v03_B_n{n}"]
    s2 = r4["levels"]["0.7"][f"v02_B_n{n}"]
    rows_b.append(["0.7", f"v0.3 Route B forgeries, n = {n}: perplexity-only FA → FA with the repetition term; share above the repetition bar",
                   f"{C.pct(s3['FA_ppl_only_median'])} → {C.pct(s3['FA']['median'])}", C.pct(s3["repetitive_share_median"]),
                   f"v0.3 F1 Route B at 0.70: {r3['levels']['0.7']['rules']['F1']['B']}; F3 at 0.70 under v0.3's rule: {'yes' if r3['levels']['0.7']['rules']['F3_fluent_generic_steering_suffices'] else 'no'}"])
    V.set(f"t3_v03_B_n{n}_FA_ppl_only_07", C.pct(s3["FA_ppl_only_median"]))
    V.set(f"t3_v03_B_n{n}_FA_07", C.pct(s3["FA"]["median"]))
    V.set(f"t3_v03_B_n{n}_rep_share_07", C.pct(s3["repetitive_share_median"], 0))
    V.set(f"t3_v02_B_n{n}_rep_share_07", C.pct(s2["repetitive_share_median"], 0))
for rho in LATE:
    V.set(f"t3_v03_F1_B_{T(rho)}", r3["levels"][rho]["rules"]["F1"]["B"])
    V.set(f"t3_v03_F1_A_{T(rho)}", r3["levels"][rho]["rules"]["F1"]["A"])
    V.set(f"t3_v03_F3_{T(rho)}", "yes" if r3["levels"][rho]["rules"]["F3_fluent_generic_steering_suffices"] else "no")
V.set("t3_v03_rep_share_07_min", C.pct(min(r4["levels"]["0.7"][f"v03_B_n{n}"]["repetitive_share_median"] for n in (64, 256)), 0))
V.set("t3_v03_rep_share_07_max", C.pct(max(r4["levels"]["0.7"][f"v03_B_n{n}"]["repetitive_share_median"] for n in (64, 256)), 0))
V.set("t3_v04_B_fluent_share_05_07_min", C.pct(min(r4["levels"][r][f"v04_B_n{n}"]["fluent_share_median"] for r in ("0.5", "0.7") for n in (64, 256)), 0))
V.set("t3_v04_B_fluent_share_05_07_max", C.pct(max(r4["levels"][r][f"v04_B_n{n}"]["fluent_share_median"] for r in ("0.5", "0.7") for n in (64, 256)), 0))
V.set("t3_v04_B_acc_05_07_min", C.pct(min(r4["levels"][r][f"v04_B_n{n}"]["acceptance"]["median"] for r in ("0.5", "0.7") for n in (64, 256))))
C.write_table("T3b", ["ρ", "quantity", "median cos(v̂, v) at n = 64 / 256 / 1,024 (or FA, %)", "layer = 14 (keys of 8) at n = 64 / 256 / 1,024 (or share, %)", "verdict"],
              rows_b, "Key recovery by the activation-mean estimator (Study 1 v0.2, rule R1) and what the repetition condition changed for v0.3's Route B forgeries at ρ = 0.70 (re-scored in v0.4)",
              ["R1 asks for a median cosine of at least 0.9 with the layer found for at least 7 of 8 keys at some n ≤ 1,024. 'Share above the repetition bar' is the median over keys of the share of a condition's texts whose seq-rep-4 exceeds the key-level oracle's 95th percentile."])
p = V.save()
print("T3 written; values:", p.name, len(V.d))
