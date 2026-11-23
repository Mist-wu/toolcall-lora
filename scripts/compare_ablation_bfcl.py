#!/usr/bin/env python3
"""Paired saved-outcome BFCL analysis for a completed exploratory rank pair."""
import argparse
import hashlib
import json
from pathlib import Path
from toolcall_lora.data import read_jsonl
from toolcall_lora.evaluate import paired_case_ci95

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rank', type=int, choices=(8, 16, 64), required=True)
rank = parser.parse_args().rank
root = Path('results')
neg0 = f'n10000-r{rank}-neg0-seed42'
neg10 = f'n10000-r{rank}-neg10-seed42'
paths = {
    neg0: root / 'formal-ablations' / neg0,
    neg10: root / 'formal-ablations' / neg10,
    'baseline-1.5b': root / 'formal-baselines/baseline-1.5b',
    'baseline-7b': root / 'formal-baselines/baseline-7b',
}
scores = {name: json.loads((path / 'bfcl.score.json').read_text())
          for name, path in paths.items()}
details = {name: {row['id']: row for row in read_jsonl(path / 'bfcl.score.details.jsonl')}
           for name, path in paths.items()}
categories = ('simple_python', 'multiple', 'parallel', 'parallel_multiple',
              'irrelevance', 'overall_subset')
pairs = [(neg10, neg0), (neg10, 'baseline-1.5b'), (neg10, 'baseline-7b')]
comparisons = []
for candidate, reference in pairs:
    values = {}
    for category in categories:
        selected = sorted(row['id'] for row in details[candidate].values()
                          if category == 'overall_subset' or row['category'] == category)
        differences = [int(details[candidate][key]['valid']) -
                       int(details[reference][key]['valid']) for key in selected]
        interval = paired_case_ci95(differences)
        values[category] = {
            'n': len(differences),
            'candidate_accuracy': scores[candidate][category]['accuracy'],
            'reference_accuracy': scores[reference][category]['accuracy'],
            'delta_candidate_minus_reference': sum(differences) / len(differences),
            'paired_case_bootstrap_ci95': interval,
            'improved_cases': differences.count(1),
            'regressed_cases': differences.count(-1),
        }
    comparisons.append({'candidate': candidate, 'reference': reference, 'categories': values})
sources = {}
for name, path in paths.items():
    prediction = path / ('predictions.jsonl' if name.startswith('baseline') else 'bfcl.predictions.jsonl')
    digest = hashlib.sha256(prediction.read_bytes()).hexdigest()
    sources[name] = {
        'path': str(path), 'dataset_sha256': scores[name]['dataset_sha256'],
        'predictions_sha256': digest,
        'predictions_hash_matches_score': digest == scores[name]['predictions_sha256'],
        'details_sha256': hashlib.sha256((path / 'bfcl.score.details.jsonl').read_bytes()).hexdigest(),
    }
requests = {name: json.loads((paths[name] / 'request.json').read_text()) for name in (neg0, neg10)}
limitations = (
    'Exploratory seed42 only, not a confirmatory rank/negative-fraction effect or a best-run selection. '
    'The rank pair shares10k positives, data_seed42, model revision, rank/alpha and two-epoch request. '
    'Adding negatives changes total examples10,000 to11,111 and optimizer steps624 to694, so this is '
    'the executed training-policy contrast, not a fixed-token/step-budget causal effect. '
    'Paired percentile case bootstrap is conditional on these fitted models, not training-seed uncertainty; '
    'within-category resampling is used for each category and unstratified shared-case resampling for overall. '
    'Case order is lexicographic ID; paired-difference indices 25/975 of 1000 resamples, seed42. '
    'Single-model score ci95 keeps the other published indices 24/974. '
    'No held-out score is inferred here. BFCL pretraining contamination and Glaive label noise/near-duplicates '
    'remain limitations. Agent review, not human-gold validation; no completed measurements changed.'
)
output = {
    'scope': f'BFCL five-category subset, exploratory matched rank{rank} seed42 pair and frozen baselines',
    'metric_boundary': scores[neg10]['data_manifest']['metric_boundary'],
    'bootstrap_seed': 42, 'resamples': 1000, 'comparisons': comparisons,
    'sources': sources, 'requests': requests, 'limitations': limitations,
    'reviewer_type': 'agent', 'human_validation_complete': False, 'human_validation_required': False,
}
out = root / 'formal-ablation-comparisons'
out.mkdir(exist_ok=True)
(out / f'rank{rank}.bfcl.json').write_text(json.dumps(output, indent=2) + '\n')
lines = [f'# Rank{rank} BFCL exploratory comparison', '', limitations, '',
         f'All deltas are `{neg10}` minus the reference; these are not full leaderboard scores.', '',
         '| Reference | Category | Cases | Reference | Neg10 | Delta (pp) | Paired95% CI (pp) | Improved / regressed |',
         '|---|---|---:|---:|---:|---:|---:|---:|']
for pair in comparisons:
    for category, value in pair['categories'].items():
        lo, hi = value['paired_case_bootstrap_ci95']
        lines.append(f"| {pair['reference']} | {category} | {value['n']} | {value['reference_accuracy']:.2%} | {value['candidate_accuracy']:.2%} | {100*value['delta_candidate_minus_reference']:+.2f} | [{100*lo:+.2f}, {100*hi:+.2f}] | {value['improved_cases']} / {value['regressed_cases']} |")
lines += ['', f'Reproduce: `python3 scripts/compare_ablation_bfcl.py --rank {rank}`. Source hashes/configurations are in the adjacent JSON.']
(out / f'rank{rank}.bfcl.md').write_text('\n'.join(lines) + '\n')
print(json.dumps([{p['reference']: p['categories']['overall_subset']} for p in comparisons], indent=2))
