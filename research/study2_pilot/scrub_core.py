"""Study 2 scrubbing machinery (SCRUB_PILOT_SPEC_v0.1.md §2-3). The Study 2 runner is meant to import it unchanged.

Paraphrase with the attacker's self-check, key-guided and random token edits, the quality conditions, and the owner's
S4 test. Reused unchanged: the Study 3 pilot's power_pilot.py (text_features, transform, pvalues, null keys, unit, the
additive-vector hook and log-likelihood), Study 1 v0.2's common.py (perplexities), v0.4's common4.py (seqrep4) and
v0.1's core.py (encoding, keys, device).
"""
import difflib
import gc
import math
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "study1_v04"))
sys.path.insert(0, str(ROOT / "research" / "study3_pilot"))
import common4 as C4  # noqa: E402  (first: puts v0.3, v0.2 and v0.1 on sys.path)
from common4 import C2, core  # noqa: E402
import power_pilot as PP  # noqa: E402

LAYER, D, NEW_TOKENS = PP.LAYER, PP.D, core.NEW_TOKENS          # 14, 1536, 256
PARAPHRASERS = {"qwen": ("Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"),
                "phi": ("microsoft/Phi-3.5-mini-instruct", "2fe192450127e6a83f7441aef6e3ca586c338b77")}
MPNET = ("sentence-transformers/all-mpnet-base-v2", "e8c3b32edf5434bc2275fc9bab85f82640a19130")
_P = ("Paraphrase the following text. Keep all of its information and meaning, but change the wording and sentence "
      "structure. {length} Reply with the paraphrase only.\n\nText:\n{{text}}")
PROMPTS = {"P1": _P.format(length="Keep it about the same length."),
           "P2": _P.format(length="Your paraphrase must be at least as long as the original text.")}
GEN = dict(do_sample=True, temperature=0.7, top_p=0.9, max_new_tokens=400)
GREEDY = dict(do_sample=False, max_new_tokens=400)
BATCH_RATIO_MIN = 0.90
MAX_ATTEMPTS = 3
LEN_FLOOR, PPL_TOL, Q = 0.8, 1.25, 0.95
BUDGETS = (0.02, 0.05, 0.10, 0.20)
ROUND_FRAC = 0.02
N_CAND, TOPK_POOL, S_FD, MIN_GAP = 10, 40, 2.0, 2
PLAUS = math.log(3)    # a candidate must be at least 1/3 as likely as the current token (unsteered)
EMB_MAX = 384


def dev():
    return core.device()


def free():
    """Return freed GPU memory. Callers must first drop their own references (`del model`): a helper cannot delete
    the caller's variables, and models kept alive that way pushed the pilot into swap (2026-10-01)."""
    gc.collect()
    torch.mps.empty_cache()


def unit(x):
    return PP.unit(np.asarray(x, dtype=np.float64))


# ---------------------------------------------------------------- models
def load_base():
    """Qwen2.5-1.5B (pinned in core), parameters frozen: the owner's detector and the attacker's scoring model."""
    return PP.load()


def load_base_fp32():
    """Qwen2.5-1.5B (pinned in core) in float32, parameters frozen: the editor's passes (pilot v0.2 and Study 2), where
    bfloat16 rounding made per-token finite differences noisy (v0.1 check I1)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(core.MODEL_ID, revision=core.REVISION)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(core.MODEL_ID, revision=core.REVISION,
                                                 dtype=torch.float32).to(dev()).eval()
    for p_ in model.parameters():
        p_.requires_grad_(False)
    return tok, model


def load_paraphraser(name):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    rid, rev = PARAPHRASERS[name]
    tok = AutoTokenizer.from_pretrained(rid, revision=rev)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(rid, revision=rev, dtype=torch.bfloat16).to(dev()).eval()
    return tok, model


class Embedder:
    """all-mpnet-base-v2 sentence embeddings as its modules.json defines them: mean pooling over the attention mask,
    then L2 normalisation; at most 384 tokens; float32."""

    def __init__(self):
        from transformers import AutoModel, AutoTokenizer
        rid, rev = MPNET
        self.tok = AutoTokenizer.from_pretrained(rid, revision=rev)
        self.model = AutoModel.from_pretrained(rid, revision=rev, dtype=torch.float32).to(dev()).eval()

    def __call__(self, texts, bs=32):
        out = []
        for b0 in range(0, len(texts), bs):
            enc = self.tok(list(texts[b0:b0 + bs]), padding=True, truncation=True, max_length=EMB_MAX,
                           return_tensors="pt").to(dev())
            with torch.no_grad():
                h = self.model(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).float()
            e = torch.nn.functional.normalize((h * m).sum(1) / m.sum(1).clamp_min(1e-9), dim=-1)
            out.append(e.cpu().numpy().astype(np.float64))
        return np.concatenate(out, 0) if out else np.zeros((0, 768))


def cosines(E, a, b):
    return (E(a) * E(b)).sum(1)


# ---------------------------------------------------------------- paraphrase
def paraphrase(tok, model, texts, template, seed, batch_size, sort_by_length=True, gen=None):
    """One paraphrase per text (continuation only), sampled with GEN (or `gen`); batches of similar length."""
    outs = [None] * len(texts)
    order = sorted(range(len(texts)), key=lambda i: len(texts[i])) if sort_by_length else list(range(len(texts)))
    for b, b0 in enumerate(range(0, len(order), batch_size)):
        idx = order[b0:b0 + batch_size]
        conv = [[{"role": "user", "content": template.format(text=texts[i])}] for i in idx]
        enc = tok.apply_chat_template(conv, add_generation_prompt=True, padding=True, return_tensors="pt",
                                      return_dict=True).to(dev())
        torch.manual_seed(seed * 1_000_003 + b)
        with torch.inference_mode():
            o = model.generate(**enc, pad_token_id=tok.pad_token_id, **(gen or GEN))
        new = o[:, enc["input_ids"].shape[1]:]
        for j, i in enumerate(idx):
            outs[i] = tok.decode(new[j], skip_special_tokens=True).strip()
        torch.mps.empty_cache()
    return outs


# ---------------------------------------------------------------- quality (spec §3)
def n_tokens(tok, texts):
    return np.array([len(tok(t, add_special_tokens=False)["input_ids"]) for t in texts], dtype=np.int64)


def perplexities(tok, model, prompts, texts, bs=8):
    """v0.2's perplexity (common.perplexities: the continuation's first 256 tokens under the unsteered model, given its
    prompt; LM head applied only to continuation positions), computed in right-padded batches. Validation checks it
    against v0.2's function. A continuation with no tokens gets inf."""
    out = []
    for b0 in range(0, len(texts), bs):
        P = [tok(p, add_special_tokens=False)["input_ids"] for p in prompts[b0:b0 + bs]]
        Cc = [tok(c, add_special_tokens=False)["input_ids"][:NEW_TOKENS] for c in texts[b0:b0 + bs]]
        L = max(len(p) + len(c) for p, c in zip(P, Cc))
        ids = torch.full((len(P), L), tok.pad_token_id, dtype=torch.long)
        att = torch.zeros((len(P), L), dtype=torch.long)
        for i, (p, c) in enumerate(zip(P, Cc)):
            ids[i, :len(p) + len(c)] = torch.tensor(p + c)
            att[i, :len(p) + len(c)] = 1
        with torch.no_grad():
            hs = model.model(input_ids=ids.to(dev()), attention_mask=att.to(dev())).last_hidden_state
            for i, (p, c) in enumerate(zip(P, Cc)):
                if not c:
                    out.append(float("inf"))
                    continue
                lg = model.lm_head(hs[i, len(p) - 1:len(p) - 1 + len(c)]).float()
                out.append(float(torch.exp(torch.nn.functional.cross_entropy(lg, ids[i, len(p):len(p) + len(c)].to(dev())))))
        torch.mps.empty_cache()
    return out


def raw_quality(tok, model, E, prompts, texts, originals=None):
    """Per text: perplexity given the prompt (v0.2's definition, batched), seq-rep-4 (v0.4), token count, and the
    embedding cosine to the original (if given)."""
    q = {"ppl": np.array(perplexities(tok, model, list(prompts), list(texts)), dtype=np.float64),
         "rep": np.array(C4.seqrep4(tok, list(texts)), dtype=np.float64),
         "len": n_tokens(tok, texts)}
    if originals is not None:
        q["cos"] = cosines(E, list(texts), list(originals))
    return q


def bars(ref_quality, pair_cos, q=Q):
    """The normal range: perplexity and seq-rep-4 at quantile q (0.95) over reference texts (the human continuations of
    the prompts; decision of 2026-09-30, revising decision 3), and the cosine at 0.95 over same-prompt independent pairs
    (model text vs human continuation)."""
    return {"ppl": float(np.quantile(ref_quality["ppl"], q)), "rep": float(np.quantile(ref_quality["rep"], q)),
            "cos": float(np.quantile(pair_cos, Q))}


def conditions(orig, z, bar):
    """Spec §3: per-text pass/fail of the four quality conditions for scrubs z of originals orig (raw_quality dicts)."""
    olen = np.minimum(orig["len"], NEW_TOKENS)
    c = {"ppl": z["ppl"] <= np.maximum(PPL_TOL * orig["ppl"], bar["ppl"]),
         "rep": z["rep"] <= np.maximum(orig["rep"], bar["rep"]),
         "len": z["len"] >= LEN_FLOOR * olen,
         "cos": z["cos"] > bar["cos"]}
    c["all"] = c["ppl"] & c["rep"] & c["len"] & c["cos"]
    return c


def n_fail(c):
    return (~c["ppl"]).astype(int) + (~c["rep"]).astype(int) + (~c["len"]).astype(int) + (~c["cos"]).astype(int)


# ---------------------------------------------------------------- the owner's S4 test (unchanged from Study 3)
class Owner:
    def __init__(self, tok, model, ref_texts):
        G = self.grads(tok, model, ref_texts)
        self.ref = {"mu_g": G.mean(0), "sd_g": np.maximum(G.std(0, ddof=1), 1e-12)}
        self.nm = PP.null_matrix()

    @staticmethod
    def grads(tok, model, texts):
        return np.stack([PP.text_features(tok, model, t)[1] for t in texts]).astype(np.float64)

    def x(self, G):
        return PP.transform("S4", None, G, self.ref)

    def pvalues(self, G, key):
        X = self.x(G)
        return PP.pvalues(X @ unit(key), X @ self.nm.T)

    def stat(self, G, key):
        return self.x(G) @ unit(key)


def grad_at_layer(tok, model, text, layer):
    """As power_pilot.text_features' g, at any decoder layer (the attacker's scale for an estimate at its layer)."""
    enc = core._encode(tok, [text]).to(dev())
    cm = enc.pop("content_mask")
    b = torch.zeros(1, 1, D, device=dev(), dtype=torch.float32, requires_grad=True)
    hd = model.model.layers[layer].register_forward_hook(PP._hook(b))
    try:
        ll = PP._loglik(model, enc, cm)
        ll.backward()
    finally:
        hd.remove()
    g = b.grad[0, 0].detach().float().cpu().numpy().astype(np.float64)
    torch.mps.empty_cache()
    return g


# ---------------------------------------------------------------- edits (spec §2.2)
def token_classes(tok, vocab_rows):
    """Per vocabulary row: `word` = a whole alphabetic word with a leading space (e.g. 'Ġcat'); `boundary` = a token that
    cannot continue the previous word (a leading space or newline, or a first character that is not alphanumeric).
    Special, added and padding rows are neither."""
    word = np.zeros(vocab_rows, dtype=bool)
    boundary = np.zeros(vocab_rows, dtype=bool)
    names = tok.convert_ids_to_tokens(list(range(tok.vocab_size)))
    for i, t in enumerate(names):
        if t is None or i in tok.added_tokens_decoder:
            continue
        word[i] = t.startswith("Ġ") and len(t) > 1 and t[1:].isalpha()
        boundary[i] = t[0] in "ĠĊ" or not t[0].isalnum()
    return word, boundary


class Editor:
    def __init__(self, tok, model):
        self.tok, self.model = tok, model
        self.W = model.lm_head.weight.detach().float()           # float32 head: per-token differences are small
        word, boundary = token_classes(tok, self.W.shape[0])
        self.word, self.boundary = torch.tensor(word, device=dev()), torch.tensor(boundary, device=dev())
        self.pad = tok.pad_token_id
        self.plaus = PLAUS

    def _passes(self, seqs, vecs, layer):
        """Final hidden states for token lists (right-padded; causal, so valid positions are unaffected), each with its
        own additive vector at the output of decoder layer `layer`."""
        L = max(len(x) for x in seqs)
        ids = torch.full((len(seqs), L), self.pad, dtype=torch.long)
        att = torch.zeros((len(seqs), L), dtype=torch.long)
        for i, x in enumerate(seqs):
            ids[i, :len(x)] = torch.tensor(x)
            att[i, :len(x)] = 1
        add = torch.stack(vecs).view(len(seqs), 1, D).to(dev(), self.model.dtype)
        hd = self.model.model.layers[layer].register_forward_hook(core.AddVector(add))
        try:
            with torch.no_grad():
                return self.model.model(input_ids=ids.to(dev()), attention_mask=att.to(dev())).last_hidden_state
        finally:
            hd.remove()

    def _logits(self, h):
        lg = h[:-1].float() @ self.W.T                            # [T-1, V], float32
        return lg - torch.logsumexp(lg, -1, keepdim=True)        # log-probabilities

    def _gather(self, h, cur, cand=None):
        """h [T, d] final states of one sequence. Returns log p(cur[t+1] | cur[:t+1]) for t < T-1, and either the
        top-K pool with its log-probabilities (cand None) or the log-probabilities of the given ids [T-1, K]."""
        return self._from_lp(self._logits(h), cur, cand)

    @staticmethod
    def _from_lp(lp, cur, cand=None):
        tgt = torch.tensor(cur[1:], device=lp.device).unsqueeze(-1)
        lp_cur = lp.gather(1, tgt).squeeze(-1)
        if cand is None:
            tv, ti = torch.topk(lp, TOPK_POOL, dim=-1)
            return lp_cur, ti, tv
        return lp_cur, lp.gather(1, cand)

    def _valid(self, top, cur, last_ok=True, top_lp=None, lp_cur=None, plaus=None):
        """[T-1, K] mask over the unsteered top-K pool: position t = i + 1 is editable if its token is a whole word
        followed by a word boundary; a candidate must be a whole word other than the current token; the first N_CAND
        such candidates are kept."""
        c = torch.tensor(cur, device=dev())
        nxt = torch.full((len(cur) - 1,), bool(last_ok), device=dev())
        nxt[:-1] = self.boundary[c[2:]]
        pos_ok = self.word[c[1:]] & nxt
        ok = self.word[top] & (top != c[1:].unsqueeze(-1))
        plaus = PLAUS if plaus is None else plaus
        if top_lp is not None and np.isfinite(plaus):
            ok = ok & (top_lp >= lp_cur.unsqueeze(-1) - plaus)
        ok = ok & (ok.long().cumsum(-1) <= N_CAND)
        return ok & pos_ok.unsqueeze(-1)

    def run(self, texts, mode, direction=None, layer=LAYER, rng=None, round_frac=ROUND_FRAC, budgets=BUDGETS,
            batch=4):
        """Edit each text up to the largest budget, `batch` texts stepping together. mode 'guided' (direction w at
        `layer`) or 'random' (needs rng). Per text: the decoded text at each budget; for guided mode the attacker's
        objective sum_t c_t(x_t) before each round, and at each budget; bookkeeping (edits, rounds, stalls, drift)."""
        assert mode in ("guided", "random") and (mode == "random") == (rng is not None)
        what = torch.tensor(direction / np.linalg.norm(direction), dtype=torch.float32) if mode == "guided" else None
        out = []
        for b0 in range(0, len(texts), batch):
            st = []
            for t in texts[b0:b0 + batch]:
                ids = self.tok(t, add_special_tokens=False)["input_ids"]
                T = len(ids[:NEW_TOKENS])
                st.append({"orig": list(ids[:NEW_TOKENS]), "cur": list(ids[:NEW_TOKENS]), "tail": ids[NEW_TOKENS:],
                           "T": T, "edited": [], "marks": [math.ceil(f * T) for f in budgets],
                           "r": math.ceil(round_frac * T), "saved": {}, "obj": [], "obj_at": {}, "stalled_at": None,
                           "rounds": 0, "final_done": mode == "random",
                           "last_ok": not ids[NEW_TOKENS:] or bool(self.boundary[ids[NEW_TOKENS]].item())})
            while True:
                go = [s for s in st if s["stalled_at"] is None and len(s["edited"]) < s["marks"][-1]]
                fin = [s for s in st if not s["final_done"] and (s["stalled_at"] is not None
                                                                 or len(s["edited"]) >= s["marks"][-1])]
                if not go and not fin:
                    break
                self._round(go + fin, [False] * len(go) + [True] * len(fin), mode, what, layer, rng)
            for s in st:
                rec = {"T": s["T"], "rounds": s["rounds"], "stalled_at": s["stalled_at"], "edited": s["edited"],
                       "obj_rounds": s["obj"], "obj": {}, "texts": {}, "n_diff": {}, "drift": {}}
                for f, m in zip(budgets, s["marks"]):
                    seq = s["saved"].get(m, s["cur"])
                    txt = self.tok.decode(seq + s["tail"], skip_special_tokens=True)
                    reenc = self.tok(txt, add_special_tokens=False)["input_ids"][:NEW_TOKENS]
                    rec["texts"][str(f)] = txt
                    rec["n_diff"][str(f)] = int(sum(a != b for a, b in zip(seq, s["orig"])))
                    rec["drift"][str(f)] = 1 - difflib.SequenceMatcher(None, seq, reenc, autojunk=False).ratio()
                    if mode == "guided":
                        rec["obj"][str(f)] = s["obj"][s["obj_at"][m]] if m in s["obj_at"] else s["obj"][-1]
                if mode == "guided":
                    rec["obj"]["0"] = s["obj"][0]
                out.append(rec)
            torch.mps.empty_cache()
        return out

    def _round(self, states, final, mode, what, layer, rng):
        """One round. Guided: two passes (+s·ŵ, −s·ŵ); contributions are central differences, and the unsteered
        distribution used for candidates and plausibility is the midpoint of the two log-probabilities (error O(s²)).
        Random: one unsteered pass."""
        k = 2 if mode == "guided" else 1
        seqs, vecs = [], []
        for s in states:
            seqs += [s["cur"]] * k
            vecs += [S_FD * what, -S_FD * what] if mode == "guided" else [torch.zeros(D)]
        H = self._passes(seqs, vecs, layer)
        for j, (s, fin) in enumerate(zip(states, final)):
            cur, T = s["cur"], s["T"]
            if mode == "guided":
                lpp_all, lpm_all = self._logits(H[2 * j, :T]), self._logits(H[2 * j + 1, :T])
                lp0, top, top_lp = self._from_lp((lpp_all + lpm_all) / 2, cur)
                lpp, cpp = self._from_lp(lpp_all, cur, top)
                lpm, cpm = self._from_lp(lpm_all, cur, top)
                del lpp_all, lpm_all
                ok = self._valid(top, cur, s["last_ok"], top_lp, lp0, self.plaus)
                c_cur = (lpp - lpm) / (2 * S_FD)
                s["obj"].append(float(c_cur.sum()))
                if fin:
                    s["final_done"] = True
                    continue
                c_cand = torch.where(ok, (cpp - cpm) / (2 * S_FD), torch.full_like(cpp, float("inf")))
                best, arg = c_cand.min(-1)
                gain = (c_cur - best).cpu().numpy()
                ystar = top.gather(1, arg.unsqueeze(-1)).squeeze(-1).cpu().numpy()
                eligible = ok.any(-1).cpu().numpy() & (gain > 0)
                order = [int(i) for i in np.argsort(-np.where(eligible, gain, -np.inf)) if eligible[i]]
            else:
                if fin:
                    s["final_done"] = True
                    continue
                lp0, top, top_lp = self._gather(H[j, :T], cur)
                ok = self._valid(top, cur, s["last_ok"], top_lp, lp0, self.plaus)
                okc, topc = ok.cpu().numpy(), top.cpu().numpy()
                eligible = okc.any(-1)
                order = [int(i) for i in rng.permutation(T - 1) if eligible[i]]
            s["rounds"] += 1
            nxt = next(m for m in s["marks"] if m > len(s["edited"]))
            want = min(s["r"], nxt - len(s["edited"]))
            taken, picks = set(s["edited"]), []
            for i in order:                                       # i indexes logits; the edited token is cur[i + 1]
                if len(picks) == want:
                    break
                pos = i + 1
                if any(abs(pos - q) < MIN_GAP for q in taken):
                    continue
                if mode == "guided":
                    cur[pos] = int(ystar[i])
                else:
                    choices = topc[i][okc[i]]
                    cur[pos] = int(choices[rng.integers(len(choices))])
                taken.add(pos)
                picks.append(pos)
            s["edited"] += picks
            for m in s["marks"]:
                if len(s["edited"]) == m and m not in s["saved"]:
                    s["saved"][m] = list(cur)
                    s["obj_at"][m] = len(s["obj"])               # the next objective entry belongs to this text
            if not picks:
                s["stalled_at"] = len(s["edited"])
