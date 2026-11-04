#!/usr/bin/env python3
"""Analyze completed seed-42 BFCL outputs without rerunning inference."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random

root = Path('results')
paths = {
    'baseline-1.5b': root / 'formal-baselines/baseline-1.5b',
    'baseline-7b': root / 'formal-baselines/baseline-7b',
    'main-seed42': root / 'formal-main-seed42',
}
scores = {name: json.loads((path / 'bfcl.score.json').read_text())
          for name, path in paths.items()}
details = {name: {row['id']: row for row in map(json.loads,
           (path / 'bfcl.score.details.jsonl').read_text().splitlines())}
           for name, path in paths.items()}
categories = ('simple_python', 'multiple', 'parallel', 'parallel_multiple',
              'irrelevance', 'overall_subset')
comparisons = {}
for baseline in ('baseline-1.5b', 'baseline-7b'):
    comparisons[baseline] = {}
    for category in categories:
        selected = [row for row in details['main-seed42'].values()
                    if category == 'overall_subset' or row['category'] == category]
        delta = [int(row['valid']) - int(details[baseline][row['id']]['valid'])
                 for row in selected]
        rng = random.Random(42)
        boot = sorted(sum(rng.choices(delta, k=len(delta))) / len(delta)
                      for _ in range(1000))
        comparisons[baseline][category] = {
            'n': len(delta),
            'baseline_accuracy': scores[baseline][category]['accuracy'],
            'main_seed42_accuracy': scores['main-seed42'][category]['accuracy'],
            'delta_main_minus_baseline': sum(delta) / len(delta),
            'paired_bootstrap_ci95': [boot[25], boot[975]],
            'improved_cases': delta.count(1), 'regressed_cases': delta.count(-1),
        }
errors = {name: dict(Counter(row.get('official_error_type', row['errors'][0])
          for row in rows.values() if not row['valid']).most_common())
          for name, rows in details.items()}
output = {
    'scope': 'single main seed 42; not a three-seed aggregate',
    'bootstrap_seed': 42, 'resamples': 1000,
    'metric_boundary': scores['main-seed42']['data_manifest']['metric_boundary'],
    'comparisons': comparisons, 'checker_error_counts': errors,
    'sources': {name: {
        'path': str(path), 'dataset_sha256': scores[name]['dataset_sha256'],
        'predictions_sha256': scores[name]['predictions_sha256'],
        'details_sha256': hashlib.sha256((path / 'bfcl.score.details.jsonl').read_bytes()).hexdigest(),
    } for name, path in paths.items()},
}
out = paths['main-seed42']
(out / 'comparison.json').write_text(json.dumps(output, indent=2) + '\n')
lines = ['# Seed 42 BFCL comparison (interim)', '',
         'Paired case bootstrap: 1,000 resamples, seed 42. Deltas are main seed42 minus baseline. Five-category subset only; these are not full leaderboard scores or three-seed results.', '',
         '| Baseline | Category | Cases | Baseline | Main seed42 | Delta (pp) | Paired 95% CI (pp) |',
         '|---|---|---:|---:|---:|---:|---:|']
for baseline, values in comparisons.items():
    for category, value in values.items():
        lo, hi = value['paired_bootstrap_ci95']
        lines.append(f"| {baseline} | {category} | {value['n']} | {value['baseline_accuracy']:.2%} | {value['main_seed42_accuracy']:.2%} | {100*value['delta_main_minus_baseline']:+.2f} | [{100*lo:+.2f}, {100*hi:+.2f}] |")
lines += ['', '## Checker diagnostics', '',
          'Counts retain the exact checker/parser labels. A no-match or wrong-count error does not uniquely identify a semantic cause; no forced seven-way attribution or human labels are inferred.', '',
          '| Error | Baseline 1.5B | Baseline 7B | Main seed42 |',
          '|---|---:|---:|---:|']
for label in sorted({label for counts in errors.values() for label in counts}):
    counts = [errors[name].get(label, 0) for name in paths]
    lines.append(f'| `{label}` | {counts[0]} | {counts[1]} | {counts[2]} |')
lines += ['', 'This seed improves irrelevance while losing overall and parallel accuracy; it does not catch the 7B baseline. The training source is the authorized Glaive fallback, not xLAM. The 94.5% Glaive held-out result is separate and has limited independence because agent review found semantic near-duplicates across splits. Agent negative-label review also found one clear mislabel and two uncertain cases among 50; this is not human-gold validation. Public BFCL pretraining contamination remains possible. Training data and completed measurements are unchanged.', '',
          'Reproduce this small CPU analysis: `python3 scripts/compare_main_seed42.py`. Remaining seeds, exploratory ablations and final error analysis are still required.']
(out / 'comparison.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({key: values['overall_subset'] for key, values in comparisons.items()}))
