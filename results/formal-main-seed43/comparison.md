# Seed 43 BFCL comparison (interim)

Paired case bootstrap: 1,000 resamples, seed 42. Deltas are main seed43 minus baseline. Five-category subset only; these are not full leaderboard scores or three-seed results.

| Baseline | Category | Cases | Baseline | Main seed43 | Delta (pp) | Paired 95% CI (pp) |
|---|---|---:|---:|---:|---:|---:|
| baseline-1.5b | simple_python | 400 | 84.00% | 85.00% | +1.00 | [-2.50, +4.50] |
| baseline-1.5b | multiple | 200 | 83.00% | 56.00% | -27.00 | [-34.50, -20.00] |
| baseline-1.5b | parallel | 200 | 65.50% | 0.00% | -65.50 | [-72.50, -59.00] |
| baseline-1.5b | parallel_multiple | 200 | 62.50% | 1.50% | -61.00 | [-68.00, -54.50] |
| baseline-1.5b | irrelevance | 240 | 70.42% | 88.33% | +17.92 | [+12.92, +23.75] |
| baseline-1.5b | overall_subset | 1240 | 74.76% | 53.79% | -20.97 | [-24.03, -17.98] |
| baseline-7b | simple_python | 400 | 95.50% | 85.00% | -10.50 | [-14.00, -7.00] |
| baseline-7b | multiple | 200 | 95.50% | 56.00% | -39.50 | [-46.50, -32.50] |
| baseline-7b | parallel | 200 | 90.00% | 0.00% | -90.00 | [-94.00, -85.50] |
| baseline-7b | parallel_multiple | 200 | 86.50% | 1.50% | -85.00 | [-89.50, -80.00] |
| baseline-7b | irrelevance | 240 | 60.42% | 88.33% | +27.92 | [+22.50, +33.33] |
| baseline-7b | overall_subset | 1240 | 86.37% | 53.79% | -32.58 | [-35.65, -29.27] |

## Checker diagnostics

Counts retain the exact checker/parser labels. A no-match or wrong-count error does not uniquely identify a semantic cause; no forced seven-way attribution or human labels are inferred.

| Error | Baseline 1.5B | Baseline 7B | Main seed43 |
|---|---:|---:|---:|
| `false_call` | 69 | 95 | 27 |
| `multiple_function_checker:wrong_count` | 4 | 2 | 73 |
| `parallel_function_checker_no_order:cannot_find_match` | 102 | 30 | 2 |
| `parallel_function_checker_no_order:wrong_count` | 38 | 15 | 395 |
| `parse_error` | 7 | 2 | 3 |
| `simple_function_checker:missing_optional` | 35 | 1 | 17 |
| `simple_function_checker:missing_required` | 5 | 0 | 2 |
| `simple_function_checker:wrong_count` | 3 | 0 | 4 |
| `simple_function_checker:wrong_func_name` | 1 | 1 | 1 |
| `type_error:nested` | 4 | 5 | 4 |
| `type_error:simple` | 1 | 0 | 1 |
| `value_error:list/tuple` | 10 | 3 | 8 |
| `value_error:others` | 12 | 3 | 16 |
| `value_error:string` | 22 | 12 | 20 |

This seed improves irrelevance while losing overall and parallel accuracy; it does not catch the 7B baseline. The training source is the authorized Glaive fallback, not xLAM. The 94.65% Glaive held-out result is separate and has limited independence because agent review found semantic near-duplicates across splits. Agent negative-label review also found one clear mislabel and two uncertain cases among 50; this is not human-gold validation. Public BFCL pretraining contamination remains possible. Training data and completed measurements are unchanged.

Reproduce this small CPU analysis: `python3 scripts/compare_main_seed42.py --seed 43`. Remaining seeds, exploratory ablations and final error analysis are still required.
