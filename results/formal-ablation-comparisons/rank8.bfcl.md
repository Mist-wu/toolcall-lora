# Rank8 BFCL exploratory comparison

Exploratory seed42 only, not a confirmatory rank/negative-fraction effect or a best-run selection. The rank pair shares10k positives, data_seed42, model revision, rank/alpha and two-epoch request. Adding negatives changes total examples10,000 to11,111 and optimizer steps624 to694, so this is the executed training-policy contrast, not a fixed-token/step-budget causal effect. Paired percentile case bootstrap is conditional on these fitted models, not training-seed uncertainty; within-category resampling is used for each category and unstratified shared-case resampling for overall. Case order is lexicographic ID; indices25/975 of1000 resamples, seed42. No held-out score is inferred here. BFCL pretraining contamination and Glaive label noise/near-duplicates remain limitations. Agent review, not human-gold validation; no completed measurements changed.

All deltas are `n10000-r8-neg10-seed42` minus the reference; these are not full leaderboard scores.

| Reference | Category | Cases | Reference | Neg10 | Delta (pp) | Paired95% CI (pp) | Improved / regressed |
|---|---|---:|---:|---:|---:|---:|---:|
| n10000-r8-neg0-seed42 | simple_python | 400 | 87.50% | 86.75% | -0.75 | [-2.75, +1.50] | 8 / 11 |
| n10000-r8-neg0-seed42 | multiple | 200 | 89.00% | 85.50% | -3.50 | [-7.00, -0.50] | 3 / 10 |
| n10000-r8-neg0-seed42 | parallel | 200 | 74.50% | 69.50% | -5.00 | [-9.50, -1.00] | 5 / 15 |
| n10000-r8-neg0-seed42 | parallel_multiple | 200 | 69.00% | 71.50% | +2.50 | [-1.00, +6.50] | 10 / 5 |
| n10000-r8-neg0-seed42 | irrelevance | 240 | 0.00% | 87.08% | +87.08 | [+82.50, +91.25] | 209 / 0 |
| n10000-r8-neg0-seed42 | overall_subset | 1240 | 65.73% | 81.37% | +15.65 | [+13.23, +18.23] | 235 / 41 |
| baseline-1.5b | simple_python | 400 | 84.00% | 86.75% | +2.75 | [-0.75, +6.00] | 29 / 18 |
| baseline-1.5b | multiple | 200 | 83.00% | 85.50% | +2.50 | [-2.50, +7.50] | 16 / 11 |
| baseline-1.5b | parallel | 200 | 65.50% | 69.50% | +4.00 | [-1.00, +9.00] | 17 / 9 |
| baseline-1.5b | parallel_multiple | 200 | 62.50% | 71.50% | +9.00 | [+3.50, +14.50] | 26 / 8 |
| baseline-1.5b | irrelevance | 240 | 70.42% | 87.08% | +16.67 | [+11.25, +22.08] | 45 / 5 |
| baseline-1.5b | overall_subset | 1240 | 74.76% | 81.37% | +6.61 | [+4.44, +8.87] | 133 / 51 |
| baseline-7b | simple_python | 400 | 95.50% | 86.75% | -8.75 | [-12.00, -5.75] | 5 / 40 |
| baseline-7b | multiple | 200 | 95.50% | 85.50% | -10.00 | [-14.50, -5.50] | 3 / 23 |
| baseline-7b | parallel | 200 | 90.00% | 69.50% | -20.50 | [-26.50, -14.50] | 5 / 46 |
| baseline-7b | parallel_multiple | 200 | 86.50% | 71.50% | -15.00 | [-21.50, -8.50] | 9 / 39 |
| baseline-7b | irrelevance | 240 | 60.42% | 87.08% | +26.67 | [+20.83, +32.50] | 66 / 2 |
| baseline-7b | overall_subset | 1240 | 86.37% | 81.37% | -5.00 | [-7.42, -2.50] | 88 / 150 |

Reproduce: `python3 scripts/compare_ablation_bfcl.py --rank 8`. Source hashes/configurations are in the adjacent JSON.
