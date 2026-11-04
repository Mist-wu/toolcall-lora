# Main Glaive held-out: three training seeds

Separate order-invariant JSON exact match with duplicate calls/types retained; not BFCL AST accuracy or xLAM reproduction.

| Seed | Correct / cases | Accuracy | Case-bootstrap 95% CI |
|---|---:|---:|---|
| 42 | 1890 / 2000 | 94.50% | [93.40%, 95.55%] |
| 43 | 1893 / 2000 | 94.65% | [93.65%, 95.65%] |
| 44 | 1896 / 2000 | 94.80% | [93.75%, 95.75%] |

Mean **94.65%**, sample SD **0.15 pp**; seed-t 95% CI **[94.28%, 95.02%]** (df2).

Case-bootstrap CI conditional on these fitted models: **[93.62%, 95.65%]**.

## Uncertainty and limitations

- Unclipped mean +/- t(0.975,df=2)*sample_sd/sqrt(3); only three training seeds with fixed data. Normal-seed assumption is weak.
- 1000 resamples, RNG seed42, percentile indices25/975. Average the three model outcomes within each shared case, then resample cases. Conditional on fitted models; 6000 seed-case outcomes are not independent cases.
- Seed and case intervals describe different uncertainties, not a joint seed/data interval. No baseline held-out delta is claimed.
- Agent review found semantic near-duplicates across Glaive splits; high accuracy is not evidence of uncontaminated generalization.
- Synthetic Glaive source is the authorized fallback, not xLAM reproduction.
- Agent negative review found one clear mislabel and two uncertain cases among50, not human-gold validation.
- Ablations and final error analysis remain incomplete; no training data or original scores changed.

Agent review is accepted; human_validation_complete=false and human_validation_required=false. Agent findings are not human-gold metrics.

Reproduce this small CPU analysis: `python3 scripts/summarize_main_heldout.py`. Source hashes and full precision are in `heldout.summary.json`.
