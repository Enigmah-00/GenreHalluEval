"""Test the notebook's merge_lora_checkpoint() on a tiny LLaMA saved with un-merged LoRA layers (the way
BanglaLLM/bangla-llama-13b-instruct-v0.1 is stored). Needs torch, transformers and safetensors (CPU is enough).

Usage: python src/bench/test_lora_merge.py <project_root> <empty_test_dir>
Checks:
 1. loading the un-merged checkpoint directly reports the linear weights as missing (the bug);
 2. after merging, nothing is missing and every weight equals base + (alpha / r) * B @ A;
 3. the merged model gives the same logits as a model built from the true weights;
 4. a wrong rank stops with a clear message.
"""
import ast
import json
import shutil
import sys
from pathlib import Path

import torch
from transformers import LlamaConfig, LlamaForCausalLM

root, T = Path(sys.argv[1]), Path(sys.argv[2])
shutil.rmtree(T, ignore_errors=True)
T.mkdir(parents=True)

# ---- take merge_lora_checkpoint() from the generated notebook, exactly as it runs on Kaggle ----
nb = json.loads((root / "notebooks/benchmark_one_llm.ipynb").read_text(encoding="utf-8"))
src = next("".join(c["source"]) for c in nb["cells"] if "def merge_lora_checkpoint" in "".join(c["source"]))
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "merge_lora_checkpoint")


class Stop(Exception):
    pass


ns = dict(json=json, Path=Path, shutil=shutil, Stop=Stop, mem_report=lambda where: None)
exec(compile(ast.Module(body=[fn], type_ignores=[]), "<merge_lora_checkpoint>", "exec"), ns)
merge = ns["merge_lora_checkpoint"]

# ---- a tiny LLaMA and its "true" weights ----
torch.manual_seed(2026)
cfg = LlamaConfig(hidden_size=64, intermediate_size=128, num_hidden_layers=2, num_attention_heads=4,
                  num_key_value_heads=4, vocab_size=120, max_position_embeddings=128, tie_word_embeddings=False)
true_model = LlamaForCausalLM(cfg).to(torch.float16).eval()
true_sd = {k: v.clone() for k, v in true_model.state_dict().items()}
R, ALPHA = 8, 16
PROJ = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")

# ---- save it the broken way: base_layer + lora_A + lora_B, in two .bin shards with an index ----
bad = {}
for k, v in true_sd.items():
    mod = k[: -len(".weight")]
    if k.endswith(".weight") and mod.rsplit(".", 1)[-1] in PROJ:
        a = torch.randn(R, v.shape[1]) * 0.05
        b = torch.randn(v.shape[0], R) * 0.05
        base = v.float() - (ALPHA / R) * (b @ a)
        bad[mod + ".base_layer.weight"] = base.to(torch.float16)
        bad[mod + ".lora_A.default.weight"] = a.to(torch.float16)
        bad[mod + ".lora_B.default.weight"] = b.to(torch.float16)
    else:
        bad[k] = v
for i in range(cfg.num_hidden_layers):
    bad[f"model.layers.{i}.self_attn.rotary_emb.inv_freq"] = torch.ones(8)
ckpt = T / "unmerged"
ckpt.mkdir()
keys = sorted(bad)
halves = {"pytorch_model-00001-of-00002.bin": keys[: len(keys) // 2], "pytorch_model-00002-of-00002.bin": keys[len(keys) // 2:]}
# keep each module's three LoRA parts in one shard, as in the real checkpoint
for k in list(halves["pytorch_model-00002-of-00002.bin"]):
    if ".lora_" in k or ".base_layer" in k:
        stem = k.rsplit(".", 3)[0] if ".lora_" in k else k.rsplit(".", 2)[0]
        if any(x.startswith(stem + ".") for x in halves["pytorch_model-00001-of-00002.bin"]):
            halves["pytorch_model-00002-of-00002.bin"].remove(k)
            halves["pytorch_model-00001-of-00002.bin"].append(k)
weight_map = {}
for name, ks in halves.items():
    torch.save({k: bad[k] for k in ks}, ckpt / name)
    weight_map.update({k: name for k in ks})
(ckpt / "pytorch_model.bin.index.json").write_text(json.dumps({"metadata": {"total_size": 1}, "weight_map": weight_map}))
cfg.save_pretrained(ckpt)

# 1. the bug: plain loading reports the linear weights as missing
_, info = LlamaForCausalLM.from_pretrained(ckpt, output_loading_info=True)
missing = [k for k in info["missing_keys"] if not k.endswith("inv_freq")]
assert len(missing) == len(PROJ) * cfg.num_hidden_layers, missing
print(f"1 ok: plain loading leaves {len(missing)} linear weights missing (random)")

# 2. merge, then nothing is missing and the weights match
dropped = []
out = merge(lambda f: str(ckpt / f), T / "merged", r=R, alpha=ALPHA, drop=dropped.append, part_bytes=20_000)
n_parts = len(list(Path(out).glob("model-part-*.safetensors")))
assert n_parts > 2, n_parts                     # written in several small parts, not one per shard
model, info = LlamaForCausalLM.from_pretrained(out, output_loading_info=True, torch_dtype=torch.float16)
assert not [k for k in info["missing_keys"] if not k.endswith("inv_freq")], info["missing_keys"]
assert not info["unexpected_keys"], info["unexpected_keys"]
worst = max((model.state_dict()[k].float() - v.float()).abs().max().item() for k, v in true_sd.items())
assert worst < 2e-3, worst
assert len(dropped) == 2
print(f"2 ok: merged checkpoint ({n_parts} parts) loads with no missing keys; largest weight difference {worst:.1e}")

# 3. same logits
ids = torch.tensor([[1, 5, 9, 33, 7, 2]])
with torch.no_grad():
    d = (model.float()(ids).logits - true_model.float()(ids).logits).abs().max().item()
assert d < 1e-2, d
print(f"3 ok: logits match the true model (max difference {d:.1e})")

# 4. a wrong rank stops
try:
    merge(lambda f: str(ckpt / f), T / "merged_wrong", r=R * 2, alpha=ALPHA)
    raise AssertionError("a wrong rank did not stop")
except Stop as e:
    print("4 ok: wrong rank stops:", str(e)[:70])
print("all LoRA-merge checks passed")
