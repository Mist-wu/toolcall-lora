#!/usr/bin/env python3
"""Compare the completed formal baselines with paired case bootstrap intervals."""
import json
from pathlib import Path
import random
from toolcall_lora.evaluate import published_bootstrap_indices

root = Path('results/formal-baselines')
scores = [json.loads((root / label / 'bfcl.score.json').read_text())
          for label in ('baseline-1.5b', 'baseline-7b')]
details = [{row['id']: row for row in map(json.loads,
           (line for line in (root / label / 'bfcl.score.details.jsonl').read_text().splitlines() if line.strip()))}
           for label in ('baseline-1.5b', 'baseline-7b')]
comparisons = {}
for category in ('simple_python', 'multiple', 'parallel', 'parallel_multiple', 'irrelevance', 'overall_subset'):
    selected = [row for row in details[0].values()
                if category == 'overall_subset' or row['category'] == category]
    differences = [int(details[1][row['id']]['valid']) - int(row['valid']) for row in selected]
    rng = random.Random(42)
    boot = sorted(sum(rng.choices(differences, k=len(differences))) / len(differences)
                  for _ in range(1000))
    low_i, high_i = published_bootstrap_indices(1000)['paired_comparison']
    comparisons[category] = {
        'n': len(differences), 'accuracy_1_5b': scores[0][category]['accuracy'],
        'accuracy_7b': scores[1][category]['accuracy'],
        'delta_7b_minus_1_5b': sum(differences) / len(differences),
        'paired_bootstrap_ci95': [boot[low_i], boot[high_i]],
        'improved_cases': differences.count(1), 'regressed_cases': differences.count(-1),
    }
output = {'status': 'completed_baseline_comparison', 'bootstrap_seed': 42, 'resamples': 1000,
          'comparisons': comparisons,
          'prediction_hashes': [score['predictions_sha256'] for score in scores],
          'metric_boundary': scores[0]['data_manifest']['metric_boundary']}
(root / 'comparison.json').write_text(json.dumps(output, indent=2) + '\n')
lines = ['# Completed formal baseline comparison', '',
         'The intervals below bootstrap paired case outcomes (1,000 resamples, seed 42, published indices 25/975). Single-model score ci95 keeps indices 24/974. These are five-category subset results, not the full BFCL leaderboard score.', '',
         '| Category | Cases | 1.5B | 7B | 7B minus 1.5B | Paired 95% CI |',
         '|---|---:|---:|---:|---:|---:|']
for category, value in comparisons.items():
    low, high = value['paired_bootstrap_ci95']
    lines.append(f"| {category} | {value['n']} | {value['accuracy_1_5b']:.2%} | {value['accuracy_7b']:.2%} | {100*value['delta_7b_minus_1_5b']:+.2f} pp | [{100*low:+.2f}, {100*high:+.2f}] pp |")
lines += ['', 'The interrupted 7B baseline combines 698 saved L4 cases with the remaining cases generated on a shared A100, using the same pinned model, BF16 precision, Transformers backend and generation settings. GPU sharing and this recovery boundary are recorded in metadata. These timings are not a throughput comparison. No LoRA gain is claimed by this baseline table.']
(root / 'comparison.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(comparisons['overall_subset']))
