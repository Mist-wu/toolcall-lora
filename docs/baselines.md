# E2 baseline sources and comparison contract

Source comparison refreshed 2026-11-04 23:30 UTC. Formal local baselines are complete: 1.5B 927/1240 (74.76%), 7B 1071/1240 (86.37%); actual results are in `results/formal-baselines/`.

| Source | Verified fact | Use |
|---|---|---|
| [Qwen2.5 1.5B model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) | Native chat template and tool-call schema; Apache-2.0 | Base 1.5B model and formatter |
| [Qwen2.5 tokenizer config](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/blob/989aa7980e4cf806f80c7fef2b1adb7bc71aa306/tokenizer_config.json) | Structured `tool_calls` emits `<tool_call>` JSON | Actual tokenizer masking integration test |
| [APIGen/xLAM data card](https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k) | CC-BY-4.0, 60k generated examples, gated acceptance | Primary source; separate dev/test |
| [Glaive data card](https://huggingface.co/datasets/glaiveai/glaive-function-calling-v2) | Apache-2.0, ungated; system/chat string format | Explicit fallback, not equivalent xLAM reproduction |
| [Official BFCL V4](https://gorilla.cs.berkeley.edu/leaderboard.html) | Page currently names evaluation commit `f7cf735` / package `2025.12.17` | Published scores need version/category alignment |
| [Official BFCL checker](https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval) | Allowed argument alternatives and parallel matching differ from plain JSON equality | Actual official package checker, not reimplementation |
| [BFCL package](https://pypi.org/project/bfcl-eval/2026.3.23/) | Pinned release used here, bundled data and checker from one distribution | 1,240 selected cases; per-file hashes in manifest |

The current official website's pinned release differs from this repository's pinned `2026.3.23` package. Therefore the comparison starts with **our own frozen 1.5B and 7B baselines on exactly the same data, prompt and checker as adapters**. Do not silently copy published aggregate scores into a five-category table. The retrieved current 109-row overall CSV contains **no Qwen2.5 model row**, so matching published 1.5B and 7B targets are unavailable in that snapshot. This does not assert absence from every historical table/paper. The exact snapshots and hashes are in `results/source-comparison/receipt.json`; no leaderboard number is invented or used to overwrite the frozen local baselines.

Pinned training model revision: `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
Pinned 7B evaluation revision: `a09a35458c702b33eeacc393d103063234e8bc28`.
Pinned xLAM revision: `26d14ebfe18b1f7b524bd39b404b50af5dc97866`.
Pinned Glaive revision: `e7f4b6456019f5d8bcb991ef0dd67d8ff23221ac`.

## Actual published-table reconciliation (2026-11-04 23:30 UTC)

Downloaded the public page, its `index_main.js` and the `data_overall.csv` loaded by `init("overall")`. The saved page explicitly names evaluation commit `f7cf7359b7ac615a0b294831c5ba2bc95ee4a000` / package `2025.12.17`, whereas E2 pins `2026.3.23`. Published overall is an **unweighted broader-category average**, including live/multi-turn/web-search/memory categories; E2 is a **1,240-case five-category micro-average**. These aggregates are not interchangeable even for a matching checkpoint. Matching Qwen2.5 rows are absent from this particular current CSV.

For context only, that CSV reports xLAM-2-1b-fc-r (FC) overall30.44% and non-live AST69.04%. This is a different trained model, a current leaderboard entry rather than an original xLAM-paper result, and not E2's selected-category micro-average. E2 uses Glaive, not xLAM/APIGen training, so no xLAM-paper numerical reproduction claim is made. The useful quantitative comparison is the frozen local baseline versus adapters under the same evaluation protocol. Do not infer a pipeline defect from disagreement with a nonmatching published aggregate or rerun completed experiments merely to match it.

Reproduce the source inspection without any model execution:

```sh
curl -fsSL https://gorilla.cs.berkeley.edu/leaderboard.html
curl -fsSL https://gorilla.cs.berkeley.edu/index_main.js
curl -fsSL https://gorilla.cs.berkeley.edu/data_overall.csv
```

For the frozen observation, inspect `results/source-comparison/bfcl-data_overall.csv` with Python `csv.DictReader` and search its `Model` column case-insensitively for `qwen2.5`; the saved result is zero of109 rows. Future website changes do not replace the collected snapshot. All three source files are saved with URL/size/SHA256 provenance.

Success is reliable paired measurement, not a predetermined gain. Report negative results and type/format errors. BFCL irrelevance scoring uses the native tag parser's notion of a valid call; this is explicitly named in score records. The strict held-out JSON metric is intentionally stricter than the official BFCL checker.
