# Main BFCL: three training seeds

Official AST checker plus strict Qwen parser on five categories, not the full leaderboard. Authorized Glaive fallback, fixed data seed42.

| Category | Cases/seed | Seed42 | Seed43 | Seed44 | Mean | Sample SD (pp) | Seed t 95% CI |
|---|---:|---:|---:|---:|---:|---:|---|
| simple_python | 400 | 84.00% | 85.00% | 85.00% | 84.67% | 0.58 | [83.23%, 86.10%] |
| multiple | 200 | 57.50% | 56.00% | 71.50% | 61.67% | 8.55 | [40.43%, 82.90%] |
| parallel | 200 | 0.00% | 0.00% | 0.50% | 0.17% | 0.29 | [-0.55%, 0.88%] |
| parallel_multiple | 200 | 21.00% | 1.50% | 17.00% | 13.17% | 10.30 | [-12.42%, 38.75%] |
| irrelevance | 240 | 90.42% | 88.33% | 90.00% | 89.58% | 1.10 | [86.84%, 92.32%] |
| overall_subset | 1240 | 57.26% | 53.79% | 59.19% | 56.75% | 2.74 | [49.95%, 63.55%] |

## Paired changes versus fixed baselines

| Baseline | Category | Mean delta (pp) | Seed t 95% CI (pp) | Paired case 95% CI (pp), conditional on fitted seeds |
|---|---|---:|---|---|
| baseline-1.5b | simple_python | +0.67 | [-0.77, +2.10] | [-2.75, +4.25] |
| baseline-1.5b | multiple | -21.33 | [-42.57, -0.10] | [-28.17, -14.83] |
| baseline-1.5b | parallel | -65.33 | [-66.05, -64.62] | [-72.33, -58.50] |
| baseline-1.5b | parallel_multiple | -49.33 | [-74.92, -23.75] | [-55.50, -42.67] |
| baseline-1.5b | irrelevance | +19.17 | [+16.43, +21.91] | [+13.89, +24.72] |
| baseline-1.5b | overall_subset | -18.01 | [-24.81, -11.21] | [-21.02, -15.16] |
| baseline-7b | simple_python | -10.83 | [-12.27, -9.40] | [-14.33, -7.42] |
| baseline-7b | multiple | -33.83 | [-55.07, -12.60] | [-40.17, -28.00] |
| baseline-7b | parallel | -89.83 | [-90.55, -89.12] | [-93.67, -85.50] |
| baseline-7b | parallel_multiple | -73.33 | [-98.92, -47.75] | [-78.33, -67.50] |
| baseline-7b | irrelevance | +29.17 | [+26.43, +31.91] | [+23.75, +34.72] |
| baseline-7b | overall_subset | -29.62 | [-36.42, -22.82] | [-32.61, -26.51] |

All three main models underperform both baselines overall. Irrelevance improves, but parallel calling is almost absent. These results do not catch the 7B baseline and are not rerun away.

## Uncertainty and limitations

- Unclipped mean +/- t(0.975,df=2)*sample_sd/sqrt(3). Only three training seeds with fixed data; normal-seed assumption is weak and this is not data-sampling uncertainty.
- 1000 paired case resamples, RNG seed42, percentile indices25/975, conditional on these three fitted models. Resample shared case IDs, averaging seeds within each case; never treat 3720 seed-case outcomes as independent cases.
- Case and seed intervals measure different uncertainty; neither establishes uncontaminated generalization or isolated causal effects of negative training.
- Authorized Glaive fallback, not xLAM; 18547 selected positives, fixed data_seed42.
- Glaive semantic near-duplicates limit separate held-out independence.
- Agent negative review: one clear mislabel and two uncertain among50; not human-gold.
- Public BFCL pretraining contamination remains possible.
- Six single-seed exploratory ablations and final seven-category error analysis remain outstanding.

Agent review is accepted, not human validation; both human_validation_complete and human_validation_required remain false. No training data or completed evaluation outcomes were changed.

Reproduce this small CPU analysis: `python3 scripts/summarize_main_bfcl.py`. Full hashes and numerical precision are in `bfcl.summary.json`. E2 remains incomplete pending the remaining actual outputs and final analysis.
