# Seed 44 BFCL comparison (interim)

Paired case bootstrap: 1,000 resamples, seed 42. Deltas are main seed44 minus baseline. Five-category subset only; these are not full leaderboard scores or three-seed results.

| Baseline | Category | Cases | Baseline | Main seed44 | Delta (pp) | Paired 95% CI (pp) |
|---|---|---:|---:|---:|---:|---:|
| baseline-1.5b | simple_python | 400 | 84.00% | 85.00% | +1.00 | [-2.25, +4.50] |
| baseline-1.5b | multiple | 200 | 83.00% | 71.50% | -11.50 | [-18.50, -5.00] |
| baseline-1.5b | parallel | 200 | 65.50% | 0.50% | -65.00 | [-72.00, -58.00] |
| baseline-1.5b | parallel_multiple | 200 | 62.50% | 17.00% | -45.50 | [-52.50, -38.00] |
| baseline-1.5b | irrelevance | 240 | 70.42% | 90.00% | +19.58 | [+14.17, +25.42] |
| baseline-1.5b | overall_subset | 1240 | 74.76% | 59.19% | -15.56 | [-18.71, -12.82] |
| baseline-7b | simple_python | 400 | 95.50% | 85.00% | -10.50 | [-14.00, -7.00] |
| baseline-7b | multiple | 200 | 95.50% | 71.50% | -24.00 | [-30.50, -18.00] |
| baseline-7b | parallel | 200 | 90.00% | 0.50% | -89.50 | [-93.50, -85.00] |
| baseline-7b | parallel_multiple | 200 | 86.50% | 17.00% | -69.50 | [-76.00, -62.50] |
| baseline-7b | irrelevance | 240 | 60.42% | 90.00% | +29.58 | [+24.17, +35.42] |
| baseline-7b | overall_subset | 1240 | 86.37% | 59.19% | -27.18 | [-30.32, -24.19] |

## Checker diagnostics

Counts retain the exact checker/parser labels. A no-match or wrong-count error does not uniquely identify a semantic cause; no forced seven-way attribution or human labels are inferred.

| Error | Baseline 1.5B | Baseline 7B | Main seed44 |
|---|---:|---:|---:|
| `false_call` | 69 | 95 | 23 |
| `multiple_function_checker:wrong_count` | 4 | 2 | 41 |
| `parallel_function_checker_no_order:cannot_find_match` | 102 | 30 | 10 |
| `parallel_function_checker_no_order:wrong_count` | 38 | 15 | 355 |
| `parse_error` | 7 | 2 | 3 |
| `simple_function_checker:missing_optional` | 35 | 1 | 18 |
| `simple_function_checker:missing_required` | 5 | 0 | 2 |
| `simple_function_checker:wrong_count` | 3 | 0 | 6 |
| `simple_function_checker:wrong_func_name` | 1 | 1 | 1 |
| `type_error:nested` | 4 | 5 | 4 |
| `type_error:simple` | 1 | 0 | 1 |
| `value_error:list/tuple` | 10 | 3 | 7 |
| `value_error:others` | 12 | 3 | 16 |
| `value_error:string` | 22 | 12 | 19 |

This seed improves irrelevance while losing overall and parallel accuracy; it does not catch the 7B baseline. The training source is the authorized Glaive fallback, not xLAM. The 94.80% Glaive held-out result is separate and has limited independence because agent review found semantic near-duplicates across splits. Agent negative-label review also found one clear mislabel and two uncertain cases among 50; this is not human-gold validation. Public BFCL pretraining contamination remains possible. Training data and completed measurements are unchanged.

Reproduce this small CPU analysis: `python3 scripts/compare_main_seed42.py --seed 44`. Remaining seeds, exploratory ablations and final error analysis are still required.
