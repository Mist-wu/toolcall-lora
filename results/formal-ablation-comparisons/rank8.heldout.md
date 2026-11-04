# Rank8 Glaive held-out exploratory pair

Strict order-invariant JSON exact match, preserving duplicate calls and types.

| Configuration | Correct / cases | Accuracy | Case-bootstrap95% CI |
|---|---:|---:|---:|
| n10000-r8-neg0-seed42 | 1889 / 2000 | 94.45% | [93.40%, 95.55%] |
| n10000-r8-neg10-seed42 | 1883 / 2000 | 94.15% | [93.05%, 95.20%] |

Neg10 minus neg0: **-0.30pp**, paired95% CI **[-0.60,+0.00]pp**; 2 improved/8 regressed.

Exploratory seed42 only; paired case uncertainty is conditional on the fitted models, not training-seed uncertainty or a fixed-step-budget causal effect. Both use10k positives and two-epoch requests, but negatives increase total examples and optimizer steps. No frozen baseline held-out result exists, so no baseline delta is claimed. Glaive is the authorized synthetic fallback, not xLAM; agent review found semantic near-duplicates across splits and negative-label noise, so these high scores do not establish uncontaminated generalization. Agent review is not human-gold validation. No model/checker reruns or metric/training-data changes.

1000 paired case resamples, RNG seed42, lexicographic IDs, percentile indices25/975.

Reproduce: `python3 scripts/compare_ablation_heldout.py --rank 8`. Full precision and source hashes are in the adjacent JSON.
