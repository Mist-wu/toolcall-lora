"""Strict held-out JSON metric and official BFCL checker adapter."""
from __future__ import annotations
import collections
import json
import random
import statistics
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


def _bootstrap_means(values, seed, resamples, mean=statistics.mean):
    if not values or resamples < 1:
        raise ValueError("Bootstrap requires observations and positive resamples")
    rng = random.Random(seed)
    return sorted(mean(rng.choices(values, k=len(values))) for _ in range(resamples))


def paired_case_ci95(values):
    """One difference or seed mean per case, in the report's original ID order."""
    # Integer case differences have exact sums; seed means retain the published rounding.
    mean = statistics.fmean if all(isinstance(v, int) for v in values) else statistics.mean
    estimates = _bootstrap_means(values, seed=42, resamples=1000, mean=mean)
    return [estimates[25], estimates[975]]


def bootstrap_accuracy(values, seed=42, resamples=1000):
    estimates = _bootstrap_means(values, seed, resamples)
    low, high = int(0.025 * (resamples - 1)), int(0.975 * (resamples - 1))
    return {
        "accuracy": statistics.mean(values),
        "n": len(values),
        "estimand": "single_model_accuracy",
        "ci95": [estimates[low], estimates[high]],
        "ci95_indices": [low, high],
        "bootstrap_seed": seed,
        "resamples": resamples,
    }


def score_prediction(row, text):
    try:
        calls = parse_tool_calls(text)
    except ValueError as error:
        return {"id": row["id"], "valid": False, "errors": ["parse_error"], "detail": str(error)}
    if row.get("benchmark") == "bfcl":
        if row["category"] == "irrelevance":
            return {"id": row["id"], "valid": not calls, "errors": [] if not calls else ["false_call"], "metric": "bfcl_irrelevance_qwen_tag_parser"}
        from bfcl_eval.constants.enums import Language
        from bfcl_eval.eval_checker.ast_eval.ast_checker import ast_checker
        # This official Qwen profile preserves dots in function names.
        result = ast_checker(row["function"], [{c["name"]: c["arguments"]} for c in calls],
                             row["ground_truth"], Language.PYTHON, row["category"], "Qwen/Qwen3-8B-FC")
        return {"id": row["id"], "valid": bool(result["valid"]), "errors": result.get("error", []), "official_error_type":result.get("error_type"), "metric": "official_bfcl_ast_checker_qwen_tag_parser"}
    errors = error_labels(row["calls"], calls)
    return {"id": row["id"], "valid": not errors, "errors": errors, "metric": "strict_order_invariant_json_exact_match"}


def score_all(rows, predictions):
    reference_ids = [row["id"] for row in rows]
    prediction_ids = [item["id"] for item in predictions]
    if len(reference_ids) != len(set(reference_ids)):
        raise ValueError("Duplicate reference IDs")
    if len(prediction_ids) != len(set(prediction_ids)):
        raise ValueError("Duplicate prediction IDs")
    if set(reference_ids) != set(prediction_ids):
        raise ValueError("Prediction IDs must exactly cover evaluation split")
    by_id = {item["id"]: item for item in predictions}
    scored = [{**score_prediction(row, by_id[row["id"]]["text"]), "category": row.get("category", "heldout_test")} for row in rows]
    categories = sorted({r["category"] for r in scored})
    summary = {cat: bootstrap_accuracy([int(r["valid"]) for r in scored if r["category"] == cat]) for cat in categories}
    summary["overall_subset"] = bootstrap_accuracy([int(r["valid"]) for r in scored])
    return scored, summary
