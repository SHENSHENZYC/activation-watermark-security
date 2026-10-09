"""Study 1 input validation (protocol §11). NO study, tuning or control keys are used with the model, and NO detection
or attack statistic is computed on model outputs. Statistical code is checked on synthetic Gaussian data only.

Run: .venv/bin/python research/study1/validate_inputs.py qwen|llama  -> research/outputs/study1_v0.1/<model>/INPUT_VALIDATION.json
"""
import ast
import json
import time
from pathlib import Path

import numpy as np
import torch
from scipy import stats

import attack
import core
import detect

import sys  # noqa: E402

MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen"
core.configure(MODEL)
OUT = core.ROOT / "research" / "outputs" / "study1_v0.1" / MODEL
res = {"model": MODEL}


def check(name, cond, **info):
    res[name] = {"pass": bool(cond), **info}
    print(("PASS " if cond else "FAIL ") + name, info if info else "")


# 1. pools
pools = core.assign_pools()
check("pools_sizes", all(len(pools[p]) == core.POOL_SIZES[p] for p in core.POOL_ORDER),
      sizes={p: len(pools[p]) for p in core.POOL_ORDER})
ids = [u["id"] for p in core.POOL_ORDER for u in pools[p]]
check("pools_disjoint_dev_only", len(ids) == len(set(ids)) and all(int(i[:8], 16) % 100 >= 20 for i in ids))
try:
    core.load_prompts("c4", "holdout")
    check("holdout_sealed", False)
except PermissionError:
    check("holdout_sealed", True)

# 2. keys
d, k = 1536, core.n_support(1536)
ks = [core.make_key(s, d, 5.0) for s in core.STUDY_KEY_SEEDS]
check("key_reproducible", torch.equal(ks[0], core.make_key(core.STUDY_KEY_SEEDS[0], d, 5.0)))
check("key_support_and_range", all(int((v != 0).sum()) == k and float(v.abs().max()) <= 5.0 for v in ks), k=k)
seed_sets = [set(core.STUDY_KEY_SEEDS), set(core.TUNING_KEY_SEEDS), set(core.RANDOM_CONTROL_SEEDS), {core.VALIDATION_KEY_SEED}]
check("seed_sets_disjoint", sum(len(s) for s in seed_sets) == len(set().union(*seed_sets)))
null = core.null_keys(d, 1.0).numpy()
check("null_keys_count", null.shape == (core.N_NULL_KEYS, d), shape=list(null.shape))

# 3. exact p-values on synthetic data (null: vectors independent of the key)
rng = np.random.default_rng(1)
N = 4000
x = rng.standard_normal((N, d))
ps = np.array([detect.pvalues(x[i:i + 1], core.make_key(10_000_000 + i, d, 5.0).numpy(), null)[1][0] for i in range(N)])
check("pvalue_grid", np.allclose(ps * 1000, np.round(ps * 1000)))
fpr = float((ps <= 0.01).mean())
lo, hi = stats.binom.ppf([0.001, 0.999], N, 0.01) / N
check("pvalue_null_fpr_at_1pct", lo <= fpr <= hi, fpr=fpr, band=[float(lo), float(hi)])
check("pvalue_null_uniform_ks", stats.kstest(ps, "uniform").pvalue > 0.001, ks_p=float(stats.kstest(ps, "uniform").pvalue))
v0 = core.make_key(10_000_000, d, 5.0).numpy()
xa = rng.standard_normal((200, d)) + 5.0 * v0 / np.linalg.norm(v0)
check("pvalue_power_sanity_synthetic", detect.accept_rate(detect.pvalues(xa, v0, null)[1]) > 0.5)

# 4. attack estimator on synthetic planted data (code correctness only)
L = 28
ref = rng.standard_normal((2000, L, d)).astype(np.float32)
plant = core.make_key(20_000_000, d, 5.0).numpy()
obs = rng.standard_normal((1024, L, d)).astype(np.float32)
obs[:, 14] += 0.3 * plant / np.abs(plant).max()
lh, vh, _ = attack.estimate(obs, ref, k, 5.0)
cos = float(vh @ plant / (np.linalg.norm(vh) * np.linalg.norm(plant)))
check("attack_recovers_planted_synthetic", lh == 14 and cos > 0.9, layer_hat=lh, cos=round(cos, 3))
check("attack_norm_rule", abs(np.linalg.norm(vh) - 5.0 * np.sqrt(k / 3)) < 1e-3)

# 5. attack module isolation: imports only numpy, never core/keys
tree = ast.parse(Path(attack.__file__).read_text())
imports = {n.names[0].name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) and hasattr(n, "names")}
imports |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
check("attack_imports_numpy_only", imports <= {"numpy"}, imports=sorted(i for i in imports if i))

# 6. lock enforcement: runner refuses without a lock
import run_study1  # noqa: E402

try:
    run_study1.check_lock()
    check("runner_refuses_without_lock", False)
except (FileNotFoundError, AssertionError):
    check("runner_refuses_without_lock", True)

# 7. model: hooks, shapes, timing (validation key only; no detection statistics)
tok, model = core.load_model()
dm = model.config.hidden_size
vkey = core.make_key(core.VALIDATION_KEY_SEED, dm, 5.0)
enc = tok("The history of the printing press shows that", return_tensors="pt").to(core.device())
with torch.no_grad():
    base = model(**enc).logits.float()
    h = model.model.layers[core.LAYER].register_forward_hook(core.AddVector(vkey.to(core.device(), model.dtype)))
    steered = model(**enc).logits.float()
    h.remove()
    restored = model(**enc).logits.float()
check("hook_changes_logits", (steered - base).abs().max().item() > 1e-3)
check("hook_removal_restores", (restored - base).abs().max().item() < 1e-4)
prompts = [u["prompt"] for u in pools["T"][:16]]
torch.mps.synchronize()
t = time.perf_counter()
texts = core.generate(tok, model, prompts, key=vkey, seed=0, batch_size=16)
torch.mps.synchronize()
t_gen = (time.perf_counter() - t) / 16
t = time.perf_counter()
f = core.reencode_features(tok, model, texts)
t_feat = (time.perf_counter() - t) / 16
t = time.perf_counter()
g = core.score_gradients(tok, model, texts)
t_grad = (time.perf_counter() - t) / 16
check("feature_shape", f.shape == (16, model.config.num_hidden_layers, dm) and np.isfinite(f).all(), shape=list(f.shape))
e = core._encode(tok, texts[:2])
n_content = int(e["content_mask"][0].sum())
check("content_tokens_le_256_bos_excluded", n_content <= core.NEW_TOKENS and n_content >= 200, n_content=n_content,
      has_bos=bool(e["attention_mask"][0].sum() != e["content_mask"][0].sum()))
check("grad_shape_finite", g.shape == (16, dm) and np.isfinite(g).all() and (np.abs(g).sum(1) > 0).all())
K = len(core.STUDY_KEY_SEEDS)
n_gen = K * 1024 + K * 200 + 400 + 3000 + K * 4 * 200 + K * 2 * 200
n_feat, n_grad = n_gen + 1000, 1000 + 1000 + K * 200 + K * 6 * 200
hours = (n_gen * t_gen + n_feat * t_feat + n_grad * t_grad) / 3600
check("timing_projection", hours <= 72, n_gen=n_gen, sec_per_gen=round(t_gen, 3), sec_per_feat=round(t_feat, 3),
      sec_per_grad=round(t_grad, 3), projected_hours=round(hours, 1))

OUT.mkdir(parents=True, exist_ok=True)
res["all_pass"] = all(v["pass"] for v in res.values() if isinstance(v, dict))
(OUT / "INPUT_VALIDATION.json").write_text(json.dumps(res, indent=2))
print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAILED")
