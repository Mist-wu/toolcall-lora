"""CUDA training/inference entrypoints; import heavy dependencies lazily."""
from __future__ import annotations
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import math
import re
import uuid
import time
from .data import read_jsonl, write_jsonl, add_negatives, encode_supervised
from .tool_format import chat_messages, normalize_tools
from .checkpoint import persist_checkpoint


def environment(config):
    import importlib.metadata
    packages = {}
    for name in ["torch", "transformers", "peft", "accelerate", "datasets", "vllm", "bfcl-eval"]:
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: pass
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    revision = commit.stdout.strip() if commit.returncode == 0 else os.environ.get("EXPERIMENT_COMMIT", "unknown")
    is_dirty = bool(dirty.stdout) if dirty.returncode == 0 else os.environ.get("EXPERIMENT_DIRTY", "false").lower() in {"true","1"}
    result = {"config": config, "versions": packages, "git_commit": revision, "dirty": is_dirty, "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    import torch
    result.update({"cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name() if torch.cuda.is_available() else None})
    return result


def load_config(path):
    return json.loads(Path(path).read_text())


def train(config, data_dir, output_dir, resume=None):
    import torch
    import numpy as np
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, TrainerCallback
    from peft import LoraConfig, get_peft_model
    seed = config["seed"]
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    if not torch.cuda.is_available():
        raise RuntimeError("Formal training must run on Colab GPU, not the 2GB coordinator")
    if not os.environ.get("EXP_CHECKPOINT_SYNC"):
        raise RuntimeError("Formal training requires EXP_CHECKPOINT_SYNC for verified checkpoint persistence")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cfg = dict(config)
    cfg["smoke"] = False
    request = out / "request.json"
    if request.exists() and json.loads(request.read_text()) != cfg:
        raise ValueError("Existing run directory uses a different configuration")
    if resume and not request.exists():
        raise ValueError("Cannot validate checkpoint configuration without request.json")
    if resume and not (Path(resume) / "complete.json").is_file():
        raise ValueError("Checkpoint lacks a completed-save marker; do not resume a partial write")
    if resume and os.environ.get("EXP_CHECKPOINT_SYNC"):
        persist_checkpoint(resume,out)
    request.write_text(json.dumps(cfg, indent=2) + "\n")
    metadata = environment(cfg)
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=config.get("model_revision"))
    tokenizer.pad_token = tokenizer.eos_token
    rows = read_jsonl(Path(data_dir) / "train.jsonl")
    random.Random(config["data_seed"]).shuffle(rows)
    size = config["train_size"]
    if size != "all" and size > len(rows): raise ValueError("Requested size exceeds leakage-free training pool")
    rows = rows if size == "all" else rows[:size]
    selected_positive_examples = len(rows)
    rows = add_negatives(rows, config["negative_fraction"], config["data_seed"])
    manifest_path = Path(data_dir) / "manifest.json"
    metadata["data_manifest"] = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"fixture":True,"reason":"no data manifest"}
    metadata["selected_positive_examples"] = selected_positive_examples
    metadata["input_examples_with_negatives"] = len(rows)
    dev = read_jsonl(Path(data_dir) / "dev.jsonl")
    random.Random(config["data_seed"]).shuffle(dev)
    dev = dev[:config.get("eval_size", len(dev))]
    encoded = [encode_supervised(tokenizer, r, config["max_length"]) for r in rows]
    encoded_dev = [encode_supervised(tokenizer, r, config["max_length"]) for r in dev]
    dataset = [r for r in encoded if r is not None]
    evalset = [r for r in encoded_dev if r is not None]
    if not dataset or not evalset: raise ValueError("All examples exceeded max_length")
    profile = config["device_profile"]
    bf16 = profile != "t4" and torch.cuda.is_available()
    if bf16 and not torch.cuda.is_bf16_supported(): raise RuntimeError("Selected profile requires bf16; choose t4 for Turing")
    dtype = torch.bfloat16 if bf16 else torch.float16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(config["model"], revision=config.get("model_revision"), torch_dtype=dtype, attn_implementation="sdpa")
    model = get_peft_model(model, LoraConfig(r=config["lora_rank"], lora_alpha=config["lora_alpha"], lora_dropout=0.05, target_modules="all-linear", bias="none", task_type="CAUSAL_LM"))
    model.config.use_cache = False
    model.enable_input_require_grads()
    batch = 2 if profile == "t4" else 4
    accumulation = 16 if profile == "t4" else 8
    def collate(examples):
        length = max(len(e["input_ids"]) for e in examples)
        return {key: torch.tensor([e[key] + [tokenizer.pad_token_id if key == "input_ids" else -100 if key == "labels" else 0] * (length - len(e[key])) for e in examples]) for key in ["input_ids", "attention_mask", "labels"]}
    args = TrainingArguments(output_dir=str(out / "checkpoints"), per_device_train_batch_size=batch, per_device_eval_batch_size=1, gradient_accumulation_steps=accumulation, learning_rate=2e-4, lr_scheduler_type="cosine", warmup_ratio=0.03, num_train_epochs=config.get("epochs", 2), max_steps=-1, bf16=bf16, fp16=not bf16 and torch.cuda.is_available(), gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False}, logging_steps=10, logging_nan_inf_filter=False, save_steps=100, eval_strategy="steps", eval_steps=100, save_total_limit=2, report_to="none", seed=seed, data_seed=config["data_seed"], remove_unused_columns=False, dataloader_num_workers=0, label_names=["labels"])
    class FiniteLoss(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kwargs):
            for name in ["loss", "eval_loss", "grad_norm"]:
                if name in (logs or {}) and not math.isfinite(logs[name]):
                    raise FloatingPointError(f"Non-finite {name} at step {state.global_step}; refusing further training")
        def on_save(self, args, state, control, **kwargs):
            checkpoint = Path(args.output_dir) / f"checkpoint-{state.global_step}"
            required = ["adapter_model.safetensors", "optimizer.pt", "scheduler.pt", "trainer_state.json"]
            if not all((checkpoint / name).is_file() for name in required):
                raise RuntimeError("Trainer checkpoint files incomplete; not publishing a resume marker")
            temporary = checkpoint / "complete.json.tmp"
            short_name=re.sub(r"[^A-Za-z0-9_-]","-",config.get("run_name","run"))[:30]
            checkpoint_id=f"E2-{short_name}-s{seed}-step{state.global_step}-{uuid.uuid4().hex[:12]}"
            with temporary.open("w") as handle:
                json.dump({"global_step":state.global_step,"files":required,"seed":seed,"checkpoint_id":checkpoint_id,"training_run_id":os.environ.get("EXPERIMENT_RUN_ID")}, handle)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.replace(checkpoint / "complete.json")
            if os.environ.get("EXP_CHECKPOINT_SYNC"):
                persist_checkpoint(checkpoint,out)
    trainer = Trainer(model=model, args=args, train_dataset=dataset, eval_dataset=evalset, data_collator=collate, callbacks=[FiniteLoss()])
    metrics = trainer.train(resume_from_checkpoint=resume).metrics
    trainer.save_model(str(out / "adapter"))
    tokenizer.save_pretrained(str(out / "adapter"))
    metadata.update({"finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "metrics": metrics, "train_examples": len(dataset), "dev_examples": len(evalset), "dropped_overlength_train": len(encoded)-len(dataset), "dropped_overlength_dev": len(encoded_dev)-len(evalset), "adapter_path": str(out / "adapter"), "seed": seed, "status": "train_complete"})
    (out / "train.json").write_text(json.dumps(metadata, indent=2) + "\n")
    # uv-created environments need not ship pip; write installed distribution versions.
    import importlib.metadata
    (out / "env.txt").write_text("\n".join(sorted(f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions())) + "\n")
    return metadata


def predict(rows, model_id, output, adapter=None, batch_size=4, max_new_tokens=512, backend="transformers", profile="l4", model_revision=None):
    from transformers import AutoTokenizer
    revisions = {"Qwen/Qwen2.5-1.5B-Instruct":"989aa7980e4cf806f80c7fef2b1adb7bc71aa306","Qwen/Qwen2.5-7B-Instruct":"a09a35458c702b33eeacc393d103063234e8bc28"}
    model_revision = model_revision or revisions.get(model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=model_revision)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    prompts = [tokenizer.apply_chat_template(row.get("messages") or chat_messages(row["query"], row["tools"]), tools=normalize_tools(row["tools"]), tokenize=False, add_generation_prompt=True) for row in rows]
    metadata = environment({"model": model_id, "model_revision": model_revision, "adapter": adapter, "backend": backend, "max_new_tokens": max_new_tokens, "profile": profile})
    if metadata["gpu"] is None: raise RuntimeError("Model inference belongs on Colab GPU")
    if backend == "vllm":
        from vllm import LLM, SamplingParams
        from vllm.lora.request import LoRARequest
        llm = LLM(model=model_id, revision=model_revision, dtype="float16" if profile == "t4" else "bfloat16", enable_lora=bool(adapter), max_lora_rank=64, max_model_len=4096, gpu_memory_utilization=0.88)
        generated = llm.generate(prompts, SamplingParams(temperature=0, max_tokens=max_new_tokens), lora_request=LoRARequest("e2", 1, adapter) if adapter else None)
        predictions = [{"id": row["id"], "text": gen.outputs[0].text, "output_tokens": len(gen.outputs[0].token_ids)} for row, gen in zip(rows, generated)]
        write_jsonl(output, predictions)
    else:
        import torch
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(model_id, revision=model_revision, torch_dtype=torch.float16 if profile == "t4" else torch.bfloat16, device_map="auto", attn_implementation="sdpa")
        if adapter:
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, adapter)
        model.eval()
        predictions = []
        for start in range(0, len(rows), batch_size):
            chunk = tokenizer(prompts[start:start+batch_size], return_tensors="pt", padding=True, truncation=False).to(model.device)
            if chunk.input_ids.shape[1] + max_new_tokens > model.config.max_position_embeddings: raise ValueError("Evaluation prompt exceeds model context; do not silently truncate")
            with torch.inference_mode():
                answer = model.generate(**chunk, do_sample=False, max_new_tokens=max_new_tokens, pad_token_id=tokenizer.pad_token_id)
            for row, tokens in zip(rows[start:start+batch_size], answer[:, chunk.input_ids.shape[1]:]):
                predictions.append({"id": row["id"], "text": tokenizer.decode(tokens, skip_special_tokens=True), "output_tokens": int((tokens != tokenizer.pad_token_id).sum())})
            write_jsonl(output, predictions)
    metadata["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    metadata["examples"] = len(predictions)
    Path(str(output) + ".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata
