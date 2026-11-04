"""Strict held-out JSON metric and official BFCL checker adapter."""
from __future__ import annotations
import collections
import json
import random
import statistics
from types import SimpleNamespace
from .tool_format import parse_tool_calls


def exact_calls(expected, actual):
    # Preserve JSON types: Python equality would treat True == 1 as equivalent.
    def bag(calls):
        return collections.Counter(json.dumps(c, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")) for c in calls)
    return bag(expected) == bag(actual)


def error_labels(expected, actual):
    if exact_calls(expected, actual):
        return []
    if not expected and actual:
        return ["false_call"]
    if expected and not actual:
        return ["missed_call"]
    labels = set()
    if len(actual) > len(expected): labels.add("extra_call")
    if len(actual) < len(expected): labels.add("missing_call")
    remaining = list(actual)
    for wanted in expected:
        candidates = [got for got in remaining if got["name"] == wanted["name"]]
        if not candidates:
            labels.add("wrong_function")
            continue
        # Exact match first handles duplicate parallel calls without order dependence.
        got = next((x for x in candidates if exact_calls([wanted], [x])), candidates[0])
        remaining.remove(got)
        for key, value in wanted["arguments"].items():
            if key not in got["arguments"]:
                labels.add("missing_argument")
            elif type(value) != type(got["arguments"][key]):
                labels.add("wrong_type")
            elif value != got["arguments"][key]:
                labels.add("wrong_value")
        if set(got["arguments"]) - set(wanted["arguments"]): labels.add("extra_argument")
    return sorted(labels or {"wrong_value"})


def bootstrap_accuracy(values, seed=42, resamples=1000):
    if not values: raise ValueError("Cannot evaluate empty data")
    rng = random.Random(seed)
    estimates = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(resamples))
    return {"accuracy": statistics.mean(values), "n": len(values), "ci95": [estimates[int(0.025 * (resamples - 1))], estimates[int(0.975 * (resamples - 1))]], "bootstrap_seed": seed, "resamples": resamples}


def score_prediction(row, text):
    try:
        calls = parse_tool_calls(text)
    except ValueError as error:
        return {"id": row["id"], "valid": False, "errors": ["parse_error"], "detail": str(error)}
    if row.get("benchmark") == "bfcl":
        if row["category"] == "irrelevance":
            return {"id": row["id"], "valid": not calls, "errors": [] if not calls else ["false_call"], "metric": "bfcl_irrelevance_qwen_tag_parser"}
        from bfcl_eval.constants.enums import Language
        from bfcl_eval.eval_checker.ast_eval.ast_checker import ast_checker, MODEL_CONFIG_MAPPING
        # The official checker only reads underscore_to_dot for this registry key.
        # Qwen permits dotted function names, so preserve them exactly.
        MODEL_CONFIG_MAPPING["e2-qwen"] = SimpleNamespace(underscore_to_dot=False)
        result = ast_checker(row["function"], [{c["name"]: c["arguments"]} for c in calls], row["ground_truth"], Language.PYTHON, row["category"], "e2-qwen")
        return {"id": row["id"], "valid": bool(result["valid"]), "errors": result.get("error", []), "official_error_type":result.get("error_type"), "metric": "official_bfcl_ast_checker_qwen_tag_parser"}
    return {"id": row["id"], "valid": exact_calls(row["calls"], calls), "errors": error_labels(row["calls"], calls), "metric": "strict_order_invariant_json_exact_match"}


def score_all(rows, predictions):
    by_id = {p["id"]: p for p in predictions}
    if len(by_id) != len(predictions): raise ValueError("Duplicate prediction IDs")
    if set(by_id) != {r["id"] for r in rows}: raise ValueError("Prediction IDs must exactly cover evaluation split")
    scored = [{**score_prediction(row, by_id[row["id"]]["text"]), "category": row.get("category", "heldout_test")} for row in rows]
    categories = sorted({r["category"] for r in scored})
    summary = {cat: bootstrap_accuracy([int(r["valid"]) for r in scored if r["category"] == cat]) for cat in categories}
    summary["overall_subset"] = bootstrap_accuracy([int(r["valid"]) for r in scored])
    return scored, summary
