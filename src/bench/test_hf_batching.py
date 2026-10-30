"""Test the notebook's HFBackend batching on CPU with a tiny LLaMA: groups respect the token budget, a GPU
out-of-memory error splits the group and still answers every prompt, a single prompt that still does not fit is
recorded as an error, and the answers do not depend on how prompts were grouped.

Usage: python src/bench/test_hf_batching.py <project_root>     (needs torch and transformers)
"""
import ast
import json
import os
import sys
import time
from pathlib import Path

import torch
from transformers import BatchEncoding, LlamaConfig, LlamaForCausalLM

root = Path(sys.argv[1])
nb = json.loads((root / "notebooks/benchmark_one_llm.ipynb").read_text(encoding="utf-8"))
src = next("".join(c["source"]) for c in nb["cells"] if "class HFBackend" in "".join(c["source"]))
tree = ast.parse(src)
keep = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in ("result", "HFBackend")]
ns = dict(time=time, os=os, json=json, Path=Path)
exec(compile(ast.Module(body=keep, type_ignores=[]), "<backend>", "exec"), ns)
HFBackend = ns["HFBackend"]


class Tok:                                   # character-level stand-in for a tokenizer, left padding
    pad_token_id, chat_template = 0, None

    def __call__(self, text, add_special_tokens=True):
        return {"input_ids": [1] * add_special_tokens + [3 + ord(ch) % 100 for ch in text]}

    def pad(self, enc, return_tensors="pt"):
        seqs = enc["input_ids"]
        n = max(map(len, seqs))
        ids = [[0] * (n - len(s)) + s for s in seqs]
        mask = [[0] * (n - len(s)) + [1] * len(s) for s in seqs]
        return BatchEncoding({"input_ids": torch.tensor(ids), "attention_mask": torch.tensor(mask)})

    def decode(self, ids, skip_special_tokens=True):
        return " ".join(str(int(i)) for i in ids if int(i) != 0)


torch.manual_seed(2026)
model = LlamaForCausalLM(LlamaConfig(hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                                     num_attention_heads=4, num_key_value_heads=4, vocab_size=120,
                                     max_position_embeddings=512)).eval()
calls = []


def backend(batch, batch_tokens, oom_above=None):
    b = HFBackend.__new__(HFBackend)
    b.cfg, b.batch, b.batch_tokens, b.num_ctx, b.fmt, b.tok, b.torch = {}, batch, batch_tokens, 400, "alpaca", Tok(), torch
    real = model.generate

    class M:                                  # the model, with a simulated GPU limit
        device = model.device

        @staticmethod
        def generate(**kw):
            shape = tuple(kw["input_ids"].shape)
            calls.append(shape)
            if oom_above is not None and shape[0] * shape[1] > oom_above:
                raise torch.cuda.OutOfMemoryError("simulated")
            return real(**kw)
    b.model = M
    return b


prompts = ["x" * n for n in (5, 60, 12, 140, 33, 90, 7, 150, 70, 20)]
MAX_NEW = 4

# reference: one prompt at a time
calls.clear()
ref = backend(batch=1, batch_tokens=10_000).generate_batch(prompts, MAX_NEW)
assert all(r["status"] == "ok" for r in ref)

# 1. groups respect the token budget (batch x (longest prompt + new tokens) <= budget), unless a group has one prompt
calls.clear()
got = backend(batch=4, batch_tokens=400).generate_batch(prompts, MAX_NEW)
for bsz, length in calls:
    assert bsz == 1 or bsz * (length + MAX_NEW) <= 400 + 30, (bsz, length)   # +30: the alpaca wrapper tokens
assert [r["raw"] for r in got] == [r["raw"] for r in ref], "answers changed with grouping"
print(f"1 ok: {len(calls)} groups within the token budget; answers identical to one-at-a-time")

# 2. an out-of-memory error splits the group, and every prompt still gets an answer
calls.clear()
got = backend(batch=4, batch_tokens=10_000, oom_above=300).generate_batch(prompts, MAX_NEW)
assert all(r["status"] == "ok" for r in got), [r["status"] for r in got]
assert [r["raw"] for r in got] == [r["raw"] for r in ref]
print(f"2 ok: out-of-memory groups were split ({len(calls)} generate calls); all {len(got)} prompts answered")

# 3. a single prompt that still does not fit is recorded as an error (retried on resume), not a crash
b3 = backend(batch=4, batch_tokens=10_000, oom_above=100)
got = b3.generate_batch(prompts, MAX_NEW)
errs = [p for p, r in zip(prompts, got) if r["status"] == "error"]
assert errs and errs == [p for p in prompts if len(b3.ids(p)) > 100], [len(b3.ids(p)) for p in errs]
assert all(r["raw"] == q["raw"] for p, r, q in zip(prompts, got, ref) if p not in errs)
print(f"3 ok: {len(errs)} prompts too big even alone were marked 'error'; the others were answered")
print("all batching checks passed")
