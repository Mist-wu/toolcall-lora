# Seed 42 BFCL comparison (interim)

Paired case bootstrap: 1,000 resamples, seed 42. Deltas are main seed42 minus baseline. Five-category subset only; these are not full leaderboard scores or three-seed results.

| Baseline | Category | Cases | Baseline | Main seed42 | Delta (pp) | Paired 95% CI (pp) |
|---|---|---:|---:|---:|---:|---:|
| baseline-1.5b | simple_python | 400 | 84.00% | 84.00% | +0.00 | [-3.50, +3.75] |
| baseline-1.5b | multiple | 200 | 83.00% | 57.50% | -25.50 | [-33.00, -18.00] |
| baseline-1.5b | parallel | 200 | 65.50% | 0.00% | -65.50 | [-72.50, -59.00] |
| baseline-1.5b | parallel_multiple | 200 | 62.50% | 21.00% | -41.50 | [-49.50, -34.00] |
| baseline-1.5b | irrelevance | 240 | 70.42% | 90.42% | +20.00 | [+14.58, +25.42] |
| baseline-1.5b | overall_subset | 1240 | 74.76% | 57.26% | -17.50 | [-20.56, -14.68] |
| baseline-7b | simple_python | 400 | 95.50% | 84.00% | -11.50 | [-15.00, -8.00] |
| baseline-7b | multiple | 200 | 95.50% | 57.50% | -38.00 | [-45.00, -31.50] |
| baseline-7b | parallel | 200 | 90.00% | 0.00% | -90.00 | [-94.00, -85.50] |
| baseline-7b | parallel_multiple | 200 | 86.50% | 21.00% | -65.50 | [-72.00, -58.00] |
| baseline-7b | irrelevance | 240 | 60.42% | 90.42% | +30.00 | [+24.58, +35.83] |
| baseline-7b | overall_subset | 1240 | 86.37% | 57.26% | -29.11 | [-32.34, -25.81] |

## Checker diagnostics

Counts retain the exact checker/parser labels. A no-match or wrong-count error does not uniquely identify a semantic cause; no forced seven-way attribution or human labels are inferred.

| Error | Baseline 1.5B | Baseline 7B | Main seed42 |
|---|---:|---:|---:|
| `false_call` | 69 | 95 | 22 |
| `multiple_function_checker:wrong_count` | 4 | 2 | 74 |
| `parallel_function_checker_no_order:cannot_find_match` | 102 | 30 | 15 |
| `parallel_function_checker_no_order:wrong_count` | 38 | 15 | 341 |
| `parse_error` | 7 | 2 | 5 |
| `simple_function_checker:missing_optional` | 35 | 1 | 19 |
| `simple_function_checker:missing_required` | 5 | 0 | 2 |
| `simple_function_checker:wrong_count` | 3 | 0 | 5 |
| `simple_function_checker:wrong_func_name` | 1 | 1 | 0 |
| `type_error:nested` | 4 | 5 | 4 |
| `type_error:simple` | 1 | 0 | 1 |
| `value_error:dict_value` | 0 | 0 | 1 |
| `value_error:list/tuple` | 10 | 3 | 7 |
| `value_error:others` | 12 | 3 | 15 |
| `value_error:string` | 22 | 12 | 19 |

This seed improves irrelevance while losing overall and parallel accuracy; it does not catch the 7B baseline. The training source is the authorized Glaive fallback, not xLAM. The 94.5% Glaive held-out result is separate and has limited independence because agent review found semantic near-duplicates across splits. Agent negative-label review also found one clear mislabel and two uncertain cases among 50; this is not human-gold validation. Public BFCL pretraining contamination remains possible. Training data and completed measurements are unchanged.

Reproduce this small CPU analysis: `python3 scripts/compare_main_seed42.py`. Remaining seeds, exploratory ablations and final error analysis are still required.
