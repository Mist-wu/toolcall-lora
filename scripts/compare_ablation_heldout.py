#!/usr/bin/env python3
"""Compare completed exploratory Glaive held-out scores, never partial predictions."""
import argparse
import hashlib
import json
from pathlib import Path
import random
from toolcall_lora.evaluate import published_bootstrap_indices

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rank', type=int, choices=(8, 16, 64), required=True)
rank = parser.parse_args().rank
names = [f'n10000-r{rank}-neg{fraction}-seed42' for fraction in (0, 10)]
paths = {name: Path('results/formal-ablations') / name for name in names}
scores = {name: json.loads((path / 'heldout.score.json').read_text())
          for name, path in paths.items()}
details = {name: {row['id']: row for row in map(json.loads,
           (line for line in (path / 'heldout.score.details.jsonl').read_text().splitlines() if line.strip()))}
           for name, path in paths.items()}
reference, candidate = names
ids = sorted(details[candidate])
differences = [int(details[candidate][key]['valid']) - int(details[reference][key]['valid'])
               for key in ids]
rng = random.Random(42)
boot = sorted(sum(rng.choices(differences, k=len(ids))) / len(ids) for _ in range(1000))
low_i, high_i = published_bootstrap_indices(1000)['paired_comparison']
limitations = (
    'Exploratory seed42 only; paired case uncertainty is conditional on the fitted models, '
    'not training-seed uncertainty or a fixed-step-budget causal effect. Both use10k positives '
    'and two-epoch requests, but negatives increase total examples and optimizer steps. '
    'No frozen baseline held-out result exists, so no baseline delta is claimed. '
    'Glaive is the authorized synthetic fallback, not xLAM; agent review found semantic '
    'near-duplicates across splits and negative-label noise, so these high scores do not '
    'establish uncontaminated generalization. Agent review is not human-gold validation. '
    'No model/checker reruns or metric/training-data changes.'
)
result = {
    'scope': f'Exploratory rank{rank} seed42 Glaive held-out matched pair, not BFCL',
    'metric': 'Strict order-invariant JSON exact match, preserving duplicate calls and types',
    'reference': reference, 'candidate': candidate, 'n': len(ids),
    'individual': {name: scores[name]['overall_subset'] for name in names},
    'correct': {name: sum(int(row['valid']) for row in details[name].values()) for name in names},
    'delta_candidate_minus_reference': sum(differences) / len(ids),
    'paired_case_bootstrap_ci95': [boot[low_i], boot[high_i]],
    'bootstrap': 'Estimand: paired case difference in lexicographic ID order. 1000 resamples, RNG seed42, published indices 25/975. Single-model score ci95 keeps indices 24/974.',
    'improved_cases': differences.count(1), 'regressed_cases': differences.count(-1),
    'sources': {}, 'limitations': limitations,
    'reviewer_type': 'agent', 'human_validation_complete': False, 'human_validation_required': False,
}
for name, path in paths.items():
    digest = hashlib.sha256((path / 'heldout.predictions.jsonl').read_bytes()).hexdigest()
    result['sources'][name] = {
        'path': str(path), 'dataset_sha256': scores[name]['dataset_sha256'],
        'predictions_sha256': digest,
        'predictions_hash_matches_score': digest == scores[name]['predictions_sha256'],
        'details_sha256': hashlib.sha256((path / 'heldout.score.details.jsonl').read_bytes()).hexdigest(),
    }
out = Path('results/formal-ablation-comparisons')
out.mkdir(exist_ok=True)
(out / f'rank{rank}.heldout.json').write_text(json.dumps(result, indent=2) + '\n')
lines = [f'# Rank{rank} Glaive held-out exploratory pair', '', result['metric'] + '.', '',
         '| Configuration | Correct / cases | Accuracy | Case-bootstrap95% CI |',
         '|---|---:|---:|---:|']
for name in names:
    metric = scores[name]['overall_subset']
    lo, hi = metric['ci95']
    lines.append(f"| {name} | {result['correct'][name]} / {metric['n']} | {metric['accuracy']:.2%} | [{lo:.2%}, {hi:.2%}] |")
lines += ['', f"Neg10 minus neg0: **{100*result['delta_candidate_minus_reference']:+.2f}pp**, paired95% CI **[{100*boot[low_i]:+.2f},{100*boot[high_i]:+.2f}]pp**; {result['improved_cases']} improved/{result['regressed_cases']} regressed.",
          '', limitations, '', result['bootstrap'] + '.', '',
          f'Reproduce: `python3 scripts/compare_ablation_heldout.py --rank {rank}`. Full precision and source hashes are in the adjacent JSON.']
(out / f'rank{rank}.heldout.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({key: result[key] for key in ('n', 'correct', 'delta_candidate_minus_reference',
                 'paired_case_bootstrap_ci95', 'improved_cases', 'regressed_cases')}, indent=2))
