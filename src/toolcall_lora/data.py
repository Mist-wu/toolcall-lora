"""Data conversion, deterministic group splitting, and documented negatives."""
from __future__ import annotations
import hashlib
import json
import random
import ast
import re
from pathlib import Path
from .tool_format import normalize_tools, render_tool_calls


def read_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")


def convert_xlam(row):
    def decoded(value):
        return json.loads(value) if isinstance(value, str) else value
    tools = normalize_tools(decoded(row["tools"]))
    calls = decoded(row["answers"])
    if isinstance(calls, dict):
        calls = [calls]
    calls = [{"name": c["name"], "arguments": c["arguments"]} for c in calls]
    render_tool_calls(calls)
    names = {t["function"]["name"] for t in tools}
    if any(c["name"] not in names for c in calls):
        raise ValueError("Answer names a tool absent from the prompt")
    query = row["query"].strip()
    if not query:
        raise ValueError("Empty query")
    return {"id": str(row["id"]), "query": query, "tools": tools, "calls": calls, "source": "Salesforce/xlam-function-calling-60k", "negative": False}


def convert_glaive(row, index):
    """Extract first user/tool-call pair only; never flatten follow-up context."""
    decoder = json.JSONDecoder()
    text = row["system"]
    start = text.find("{")
    if start < 0: raise ValueError("No function schema")
    tools = []
    remainder = text[start:].strip()
    while remainder:
        item, consumed = decoder.raw_decode(remainder)
        tools.append(item)
        remainder = remainder[consumed:].strip()
    match = re.match(r"\s*USER:\s*(.*?)\n+ASSISTANT:\s*(.*?)\s*<\|endoftext\|>", row["chat"], re.DOTALL)
    if not match: raise ValueError("Unsupported Glaive first-turn format")
    query, answer = match.groups()
    if not answer.startswith("<functioncall>"):
        raise ValueError("No first-turn function call; keep positive pool separate")
    payload = answer.removeprefix("<functioncall>").strip()
    try: call = json.loads(payload)
    except json.JSONDecodeError: call = ast.literal_eval(payload)
    if isinstance(call["arguments"], str): call["arguments"] = json.loads(call["arguments"])
    normalized = convert_xlam({"id":f"glaive-{index}","query":query,"tools":tools,"answers":[call]})
    normalized["source"] = "glaiveai/glaive-function-calling-v2"
    return normalized


def query_key(row):
    # Duplicate questions stay in one split even if tool descriptions differ.
    return " ".join(row["query"].casefold().split())


def split_rows(rows, dev_size=2000, test_size=2000, seed=42):
    """Deduplicate exact question+tools examples, then split by normalized question."""
    if dev_size < 0 or test_size < 0:
        raise ValueError("Split counts must be nonnegative")
    unique = {}
    for row in rows:
        key = (query_key(row), json.dumps(row["tools"], sort_keys=True))
        if key in unique and unique[key]["calls"] != row["calls"]:
            raise ValueError("Conflicting answers for identical query and tools")
        unique.setdefault(key, row)
    groups = {}
    for row in unique.values():
        groups.setdefault(query_key(row), []).append(row)
    ordered = sorted(groups, key=lambda key: hashlib.sha256(f"{seed}:{key}".encode()).hexdigest())
    splits = {"dev": [], "test": [], "train": []}
    for key in ordered:
        target = "dev" if len(splits["dev"]) < dev_size else "test" if len(splits["test"]) < test_size else "train"
        splits[target].extend(groups[key])
    if not splits["train"] or len(splits["dev"]) < dev_size or len(splits["test"]) < test_size:
        raise ValueError("Insufficient unique data for requested train/dev/test split")
    ids = [row["id"] for part in splits.values() for row in part]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source IDs")
    return splits


def add_negatives(rows, fraction=0.1, seed=42):
    """Replace tools with unrelated names; synthetic negatives need quality review."""
    if not 0 <= fraction < 1:
        raise ValueError("Negative fraction must be in [0,1)")
    rng = random.Random(seed)
    result = list(rows)
    count = round(len(rows) * fraction / (1 - fraction))
    choices = list(rows)
    rng.shuffle(choices)
    names_by_id = {r["id"]: {t["function"]["name"] for t in normalize_tools(r["tools"])} for r in choices}
    for i in range(count):
        row = choices[i % len(choices)]
        source_names = names_by_id[row["id"]]
        donor = None
        for _ in range(1000):
            candidate = rng.choice(choices)
            if not source_names & names_by_id[candidate["id"]]:
                donor = candidate
                break
        if donor is None:
            raise ValueError("Cannot build non-overlapping negative tools")
        result.append({**row, "id": row["id"] + f"-negative-{i}", "tools": donor["tools"], "calls": [], "negative": True, "negative_donor": donor["id"], "quality_note": "Name-disjoint tools are not guaranteed semantically irrelevant; audit before conclusions."})
    rng.shuffle(result)
    return result


def encode_supervised(tokenizer, row, max_length=2048):
    """Mask all prompt tokens; reject overflow instead of truncating target JSON."""
    from .tool_format import chat_messages
    tools = normalize_tools(row["tools"])
    prompt = tokenizer.apply_chat_template(chat_messages(row["query"], tools), tools=tools, tokenize=False, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(chat_messages(row["query"], tools, row["calls"]), tools=tools, tokenize=False, add_generation_prompt=False)
    if not full.startswith(prompt):
        raise ValueError("Tokenizer template assistant prefix mismatch")
    # Require prefix token identity; special assistant delimiter gives stable boundary.
    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full, add_special_tokens=False)["input_ids"]
    if full_ids[:len(prompt_ids)] != prompt_ids:
        raise ValueError("Token boundary merges across assistant prefix")
    if len(full_ids) > max_length:
        return None
    labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
    if not any(label != -100 for label in labels):
        raise ValueError("No supervised tokens")
    return {"input_ids": full_ids, "attention_mask": [1] * len(full_ids), "labels": labels}
