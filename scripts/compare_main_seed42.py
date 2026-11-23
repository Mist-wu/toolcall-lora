#!/usr/bin/env python3
"""Analyze a completed main-seed BFCL result without rerunning inference."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
from toolcall_lora.evaluate import published_bootstrap_indices

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--seed', type=int, choices=(42, 43, 44), default=42)
seed = parser.parse_args().seed
main = f'main-seed{seed}'
root = Path('results')
paths = {
    'baseline-1.5b': root / 'formal-baselines/baseline-1.5b',
    'baseline-7b': root / 'formal-baselines/baseline-7b',
    main: root / f'formal-{main}',
}
scores = {name: json.loads((path / 'bfcl.score.json').read_text())
          for name, path in paths.items()}
details = {name: {row['id']: row for row in map(json.loads,
           (line for line in (path / 'bfcl.score.details.jsonl').read_text().splitlines() if line.strip()))}
           for name, path in paths.items()}
categories = ('simple_python', 'multiple', 'parallel', 'parallel_multiple',
              'irrelevance', 'overall_subset')
comparisons = {}
for baseline in ('baseline-1.5b', 'baseline-7b'):
    comparisons[baseline] = {}
    for category in categories:
        selected = [row for row in details[main].values()
                    if category == 'overall_subset' or row['category'] == category]
        delta = [int(row['valid']) - int(details[baseline][row['id']]['valid'])
                 for row in selected]
        rng = random.Random(42)
        boot = sorted(sum(rng.choices(delta, k=len(delta))) / len(delta)
                      for _ in range(1000))
        low_i, high_i = published_bootstrap_indices(1000)['paired_comparison']
        comparisons[baseline][category] = {
            'n': len(delta),
            'baseline_accuracy': scores[baseline][category]['accuracy'],
            f'main_seed{seed}_accuracy': scores[main][category]['accuracy'],
            'delta_main_minus_baseline': sum(delta) / len(delta),
            'paired_bootstrap_ci95': [boot[low_i], boot[high_i]],
            'improved_cases': delta.count(1), 'regressed_cases': delta.count(-1),
        }
errors = {name: dict(Counter(row.get('official_error_type', row['errors'][0])
          for row in rows.values() if not row['valid']).most_common())
          for name, rows in details.items()}
output = {
    'scope': f'single main seed {seed}; not a three-seed aggregate',
    'bootstrap_seed': 42, 'resamples': 1000,
    'metric_boundary': scores[main]['data_manifest']['metric_boundary'],
    'comparisons': comparisons, 'checker_error_counts': errors,
    'sources': {name: {
        'path': str(path), 'dataset_sha256': scores[name]['dataset_sha256'],
        'predictions_sha256': scores[name]['predictions_sha256'],
        'details_sha256': hashlib.sha256((path / 'bfcl.score.details.jsonl').read_bytes()).hexdigest(),
    } for name, path in paths.items()},
}
out = paths[main]
(out / 'comparison.json').write_text(json.dumps(output, indent=2) + '\n')
lines = [f'# Seed {seed} BFCL comparison (interim)', '',
         f'Paired case bootstrap: 1,000 resamples, seed 42, published indices 25/975. Single-model score ci95 keeps indices 24/974. Deltas are main seed{seed} minus baseline. Five-category subset only; these are not full leaderboard scores or three-seed results.', '',
         f'| Baseline | Category | Cases | Baseline | Main seed{seed} | Delta (pp) | Paired 95% CI (pp) |',
         '|---|---|---:|---:|---:|---:|---:|']
for baseline, values in comparisons.items():
    for category, value in values.items():
        lo, hi = value['paired_bootstrap_ci95']
        lines.append(f"| {baseline} | {category} | {value['n']} | {value['baseline_accuracy']:.2%} | {value[f'main_seed{seed}_accuracy']:.2%} | {100*value['delta_main_minus_baseline']:+.2f} | [{100*lo:+.2f}, {100*hi:+.2f}] |")
lines += ['', '## Checker diagnostics', '',
          'Counts retain the exact checker/parser labels. A no-match or wrong-count error does not uniquely identify a semantic cause; no forced seven-way attribution or human labels are inferred.', '',
          f'| Error | Baseline 1.5B | Baseline 7B | Main seed{seed} |',
          '|---|---:|---:|---:|']
for label in sorted({label for counts in errors.values() for label in counts}):
    counts = [errors[name].get(label, 0) for name in paths]
    lines.append(f'| `{label}` | {counts[0]} | {counts[1]} | {counts[2]} |')
heldout = json.loads((out / 'heldout.score.json').read_text())
lines += ['', f'This seed improves irrelevance while losing overall and parallel accuracy; it does not catch the 7B baseline. The training source is the authorized Glaive fallback, not xLAM. The {heldout["overall_subset"]["accuracy"]:.2%} Glaive held-out result is separate and has limited independence because agent review found semantic near-duplicates across splits. Agent negative-label review also found one clear mislabel and two uncertain cases among 50; this is not human-gold validation. Public BFCL pretraining contamination remains possible. Training data and completed measurements are unchanged.', '',
          f'Reproduce this small CPU analysis: `python3 scripts/compare_main_seed42.py --seed {seed}`. Remaining seeds, exploratory ablations and final error analysis are still required.']
(out / 'comparison.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({key: values['overall_subset'] for key, values in comparisons.items()}))
