# Completed formal baseline comparison

The intervals below bootstrap paired case outcomes (1,000 resamples, seed 42). These are five-category subset results, not the full BFCL leaderboard score.

| Category | Cases | 1.5B | 7B | 7B minus 1.5B | Paired 95% CI |
|---|---:|---:|---:|---:|---:|
| simple_python | 400 | 84.00% | 95.50% | +11.50 pp | [+8.00, +15.25] pp |
| multiple | 200 | 83.00% | 95.50% | +12.50 pp | [+7.50, +17.50] pp |
| parallel | 200 | 65.50% | 90.00% | +24.50 pp | [+17.50, +31.50] pp |
| parallel_multiple | 200 | 62.50% | 86.50% | +24.00 pp | [+17.00, +31.00] pp |
| irrelevance | 240 | 70.42% | 60.42% | -10.00 pp | [-15.83, -4.17] pp |
| overall_subset | 1240 | 74.76% | 86.37% | +11.61 pp | [+9.11, +14.27] pp |

The interrupted 7B baseline combines 698 saved L4 cases with the remaining cases generated on a shared A100, using the same pinned model, BF16 precision, Transformers backend and generation settings. GPU sharing and this recovery boundary are recorded in metadata. These timings are not a throughput comparison. No LoRA gain is claimed by this baseline table.
