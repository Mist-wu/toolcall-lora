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


def published_bootstrap_indices(resamples=1000):
    """Two published percentile conventions. Do not collapse them.

    single_model_accuracy uses floor(0.025*(resamples-1)) and floor(0.975*(resamples-1)):
    indices 24 and 974 when resamples is 1000. That is score JSON ci95.
    paired_comparison uses floor(0.025*resamples) and floor(0.975*resamples):
    indices 25 and 975 when resamples is 1000. Comparison scripts apply those
    indices to paired case differences or within-case seed means, in their
    existing ID order. A training-seed t interval is a third estimand.
    """
    if resamples < 1:
        raise ValueError("Bootstrap resamples must be positive")
    return {
        "single_model_accuracy": [int(0.025 * (resamples - 1)), int(0.975 * (resamples - 1))],
        "paired_comparison": [int(0.025 * resamples), int(0.975 * resamples)],
    }


def bootstrap_accuracy(values, seed=42, resamples=1000):
    if not values: raise ValueError("Cannot evaluate empty data")
    rng = random.Random(seed)
    estimates = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(resamples))
    indices = published_bootstrap_indices(resamples)
    single = indices["single_model_accuracy"]
    paired = indices["paired_comparison"]
    return {
        "accuracy": statistics.mean(values),
        "n": len(values),
        "estimand": "single_model_accuracy",
        "ci95": [estimates[single[0]], estimates[single[1]]],
        "ci95_indices": single,
        "paired_comparison_indices": paired,
        "same_resamples_at_paired_comparison_indices": [estimates[paired[0]], estimates[paired[1]]],
        "index_conventions": {
            "single_model_accuracy": "floor(0.025*(resamples-1)) and floor(0.975*(resamples-1)); published score field ci95",
            "paired_comparison": "floor(0.025*resamples) and floor(0.975*resamples); published paired-difference scripts. Those scripts resample paired case differences or within-case seed means in their existing ID order, not this single-model vector.",
        },
        "bootstrap_seed": seed,
        "resamples": resamples,
    }


_MISSING = object()


def apply_bfcl_checker(checker, mapping, language, row, calls):
    """Reuse a compatible registry entry, otherwise install one and always restore it."""
    key = "e2-qwen"
    previous = mapping.get(key, _MISSING)
    compatible = previous is not _MISSING and getattr(previous, "underscore_to_dot", None) is False
    if not compatible:
        mapping[key] = SimpleNamespace(underscore_to_dot=False)
    try:
        return checker(
            row["function"],
            [{call["name"]: call["arguments"]} for call in calls],
            row["ground_truth"],
            language,
            row["category"],
            key,
        )
    finally:
        if previous is _MISSING:
            mapping.pop(key, None)
        else:
            mapping[key] = previous


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
        # Qwen permits dotted function names, so the temporary entry keeps them exactly.
        # A foreign entry is restored even when the checker raises.
        result = apply_bfcl_checker(ast_checker, MODEL_CONFIG_MAPPING, Language.PYTHON, row, calls)
        return {"id": row["id"], "valid": bool(result["valid"]), "errors": result.get("error", []), "official_error_type":result.get("error_type"), "metric": "official_bfcl_ast_checker_qwen_tag_parser"}
    return {"id": row["id"], "valid": exact_calls(row["calls"], calls), "errors": error_labels(row["calls"], calls), "metric": "strict_order_invariant_json_exact_match"}


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
