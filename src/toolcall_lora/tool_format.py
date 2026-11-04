"""Qwen native tool protocol shared with E3; never executes model output."""
from __future__ import annotations

import copy
import json
import re

TOOL_CALL_START = "<tool_call>"
TOOL_CALL_END = "</tool_call>"
_CALL = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"Non-finite JSON value: {value}")


def parse_tool_calls(text: str) -> list[dict]:
    """Parse complete Qwen tags; untagged prose is a no-call response."""
    matches = list(_CALL.finditer(text))
    if text.count(TOOL_CALL_START) != len(matches) or text.count(TOOL_CALL_END) != len(matches):
        raise ValueError("Unbalanced or nested tool_call tags")
    result = []
    for match in matches:
        call = json.loads(match.group(1), object_pairs_hook=_strict_object, parse_constant=_invalid_constant)
        if not isinstance(call, dict) or set(call) != {"name", "arguments"}:
            raise ValueError("Tool call must contain exactly name and arguments")
        if not isinstance(call["name"], str) or not call["name"].strip():
            raise ValueError("Tool name must be a nonempty string")
        if not isinstance(call["arguments"], dict):
            raise ValueError("Tool arguments must be an object, not encoded JSON")
        result.append(call)
    return result


def render_tool_calls(calls: list[dict]) -> str:
    text = "\n".join(TOOL_CALL_START + "\n" + json.dumps(c, ensure_ascii=False, allow_nan=False) + "\n" + TOOL_CALL_END for c in calls)
    parse_tool_calls(text)
    return text


def normalize_schema(schema: dict) -> dict:
    """Convert xLAM/BFCL Python-ish types to JSON Schema for the prompt only."""
    schema = copy.deepcopy(schema)
    aliases = {"int": "integer", "float": "number", "dict": "object", "list": "array", "tuple": "array", "str": "string", "bool": "boolean"}
    if isinstance(schema.get("type"), str):
        schema["type"] = aliases.get(schema["type"], schema["type"])
    if "properties" in schema:
        schema["properties"] = {k: normalize_schema(v) for k, v in schema["properties"].items()}
    if isinstance(schema.get("items"), dict):
        schema["items"] = normalize_schema(schema["items"])
    return schema


def normalize_tools(tools: list[dict]) -> list[dict]:
    result = []
    for tool in tools:
        fn = copy.deepcopy(tool.get("function", tool))
        if not isinstance(fn.get("name"), str):
            raise ValueError("Function name missing")
        params = fn.get("parameters", {"type": "object", "properties": {}})
        # Some APIGen exports use a direct name->schema map.
        if "type" not in params and "properties" not in params:
            params = {"type": "object", "properties": params, "required": list(params)}
        fn["parameters"] = normalize_schema(params)
        result.append({"type": "function", "function": fn})
    if len({t["function"]["name"] for t in result}) != len(result):
        raise ValueError("Duplicate tool names")
    return result


def chat_messages(query: str, tools: list[dict], calls: list[dict] | None = None) -> list[dict]:
    """Build native structured assistant tool_calls, as Qwen's template expects."""
    normalize_tools(tools)
    messages = [{"role": "user", "content": query}]
    if calls is not None:
        render_tool_calls(calls)
        if calls:
            messages.append({"role": "assistant", "content": "", "tool_calls": [{"type": "function", "function": c} for c in calls]})
        else:
            messages.append({"role": "assistant", "content": "I cannot complete this request with the available tools."})
    return messages
