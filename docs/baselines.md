# E2 baseline sources and comparison contract

Checked 2026-11-04. No formal model scores have been measured yet.

| Source | Verified fact | Use |
|---|---|---|
| [Qwen2.5 1.5B model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) | Native chat template and tool-call schema; Apache-2.0 | Base 1.5B model and formatter |
| [Qwen2.5 tokenizer config](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/989aa7980e4cf806f80c7fef2b1adb7bc71aa306/tokenizer_config.json) | Structured `tool_calls` emits `<tool_call>` JSON | Actual tokenizer masking integration test |
| [APIGen/xLAM data card](https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k) | CC-BY-4.0, 60k generated examples, gated acceptance | Primary source; separate dev/test |
| [Glaive data card](https://huggingface.co/datasets/glaiveai/glaive-function-calling-v2) | Apache-2.0, ungated; system/chat string format | Explicit fallback, not equivalent xLAM reproduction |
| [Official BFCL V4](https://gorilla.cs.berkeley.edu/leaderboard.html) | Page currently names evaluation commit `f7cf735` / package `2025.12.17` | Published scores need version/category alignment |
| [Official BFCL checker](https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval) | Allowed argument alternatives and parallel matching differ from plain JSON equality | Actual official package checker, not reimplementation |
| [BFCL package](https://pypi.org/project/bfcl-eval/2026.3.23/) | Pinned release used here, bundled data and checker from one distribution | 1,240 selected cases; per-file hashes in manifest |

The current official website's pinned release differs from this repository's pinned `2026.3.23` package. Therefore the comparison starts with **our own frozen 1.5B and 7B baselines on exactly the same data, prompt and checker as adapters**. Do not silently copy published aggregate scores into a five-category table. Before finalizing, inspect the published table for matching Qwen checkpoints/category values; if no matching 1.5B number exists, say unavailable rather than inventing a target. Explain version differences if keeping the current pin.

Pinned training model revision: `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
Pinned 7B evaluation revision: `a09a35458c702b33eeacc393d103063234e8bc28`.
Pinned xLAM revision: `26d14ebfe18b1f7b524bd39b404b50af5dc97866`.
Pinned Glaive revision: `e7f4b6456019f5d8bcb991ef0dd67d8ff23221ac`.

Success is reliable paired measurement, not a predetermined gain. Report negative results and type/format errors. BFCL irrelevance scoring uses the native tag parser's notion of a valid call; this is explicitly named in score records. The strict held-out JSON metric is intentionally stricter than the official BFCL checker.
