# Formal 1.5B baseline error analysis

The completed 1,240-case subset has **927 correct and 313 failed cases** (74.758%; bootstrap 95% CI 72.419–77.258%). Error labels below retain the official checker names; `false_call` and `parse_error` come from the native-Qwen parser/irrelevance path.

| Error label | Cases | Fraction of failures |
|---|---:|---:|
| `parallel_function_checker_no_order:cannot_find_match` | 102 | 32.59% |
| `false_call` | 69 | 22.04% |
| `parallel_function_checker_no_order:wrong_count` | 38 | 12.14% |
| `simple_function_checker:missing_optional` | 35 | 11.18% |
| `value_error:string` | 22 | 7.03% |
| `value_error:others` | 12 | 3.83% |
| `value_error:list/tuple` | 10 | 3.19% |
| `parse_error` | 7 | 2.24% |
| `simple_function_checker:missing_required` | 5 | 1.60% |
| `type_error:nested` | 4 | 1.28% |
| `multiple_function_checker:wrong_count` | 4 | 1.28% |
| `simple_function_checker:wrong_count` | 3 | 0.96% |
| `type_error:simple` | 1 | 0.32% |
| `simple_function_checker:wrong_func_name` | 1 | 0.32% |

The two parallel categories account for 144 failures across 400 cases. The official no-match and wrong-count labels together account for 140 of those failures. Only 7 of all 1,240 responses fail parsing (0.565%); syntactically valid output alone therefore does not establish correct tool selection or arguments. In irrelevance, 69 cases make an unwanted tool call and 2 fail parsing.

These are measured diagnostics, not a claim that any LoRA configuration improves them. The 7B run is incomplete, training has not begun, and semantic review of synthetic training negatives remains a human task.
