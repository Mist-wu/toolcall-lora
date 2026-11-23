#!/usr/bin/env python3
"""Summarize the three completed main BFCL seeds from saved scores/outcomes."""
import hashlib
import json
from pathlib import Path
import random
import statistics
from toolcall_lora.evaluate import published_bootstrap_indices

ROOT = Path('results')
SEEDS = (42, 43, 44)
CATEGORIES = ('simple_python', 'multiple', 'parallel', 'parallel_multiple',
              'irrelevance', 'overall_subset')
PATHS = {f'main-seed{s}': ROOT / f'formal-main-seed{s}' for s in SEEDS}
PATHS.update({b: ROOT / 'formal-baselines' / b
              for b in ('baseline-1.5b', 'baseline-7b')})
SCORES = {name: json.loads((p / 'bfcl.score.json').read_text())
          for name, p in PATHS.items()}
DETAILS = {name: {r['id']: r for r in map(json.loads,
           (line for line in (p / 'bfcl.score.details.jsonl').read_text().splitlines() if line.strip()))}
           for name, p in PATHS.items()}


def seed_summary(values):
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    half = 4.302652729911275 * sd / (3 ** 0.5)  # Student t, df=2
    return {'values': values, 'mean': mean, 'sample_sd': sd,
            'seed_t_ci95': [mean - half, mean + half]}


categories = {}
for category in CATEGORIES:
    ids = [i for i, r in DETAILS['main-seed42'].items()
           if category == 'overall_subset' or r['category'] == category]
    values = [SCORES[f'main-seed{s}'][category]['accuracy'] for s in SEEDS]
    comparisons = {}
    for baseline in ('baseline-1.5b', 'baseline-7b'):
        base = SCORES[baseline][category]['accuracy']
        per_case = [sum(int(DETAILS[f'main-seed{s}'][i]['valid']) for s in SEEDS) / 3
                    - int(DETAILS[baseline][i]['valid']) for i in ids]
        rng = random.Random(42)
        boot = sorted(statistics.mean(rng.choices(per_case, k=len(ids)))
                      for _ in range(1000))
        low_i, high_i = published_bootstrap_indices(1000)['paired_comparison']
        comparisons[baseline] = {
            'baseline_accuracy': base,
            'delta_main_minus_baseline': seed_summary([v - base for v in values]),
            'paired_case_bootstrap_ci95_conditional_on_three_seeds': [boot[low_i], boot[high_i]],
        }
    categories[category] = {'n_cases_per_seed': len(ids),
                            'main_accuracy': seed_summary(values),
                            'comparisons': comparisons}

output = {
    'scope': 'main seeds 42,43,44 BFCL only; ablations and held-out summary not included',
    'training_seeds': list(SEEDS), 'data_seed': 42,
    'metric_boundary': SCORES['main-seed42']['data_manifest']['metric_boundary'],
    'uncertainty': {
        'seed_t_ci95': 'Unclipped mean +/- t(0.975,df=2)*sample_sd/sqrt(3). Only three training seeds with fixed data; normal-seed assumption is weak and this is not data-sampling uncertainty.',
        'paired_case_bootstrap': 'Estimand: paired case difference conditional on these three fitted models. 1000 resamples, RNG seed42, shared case IDs in file order, seeds averaged within each case, published indices 25/975. Single-model score ci95 keeps the other published indices 24/974. Never treat 3720 seed-case outcomes as independent cases.',
        'interpretation': 'Case and seed intervals measure different uncertainty; neither establishes uncontaminated generalization or isolated causal effects of negative training.',
    },
    'categories': categories,
    'sources': {name: {'path': str(p), 'dataset_sha256': SCORES[name]['dataset_sha256'],
                       'predictions_sha256': SCORES[name]['predictions_sha256'],
                       'score_sha256': hashlib.sha256((p / 'bfcl.score.json').read_bytes()).hexdigest(),
                       'details_sha256': hashlib.sha256((p / 'bfcl.score.details.jsonl').read_bytes()).hexdigest()}
                for name, p in PATHS.items()},
    'reviewer_type': 'agent', 'human_validation_complete': False,
    'human_validation_required': False,
    'limitations': ['Authorized Glaive fallback, not xLAM; 18547 selected positives, fixed data_seed42.',
                    'Glaive semantic near-duplicates limit separate held-out independence.',
                    'Agent negative review: one clear mislabel and two uncertain among50; not human-gold.',
                    'Public BFCL pretraining contamination remains possible.',
                    'Six single-seed exploratory ablations and final seven-category error analysis remain outstanding.'],
}
out = ROOT / 'formal-main-summary'
out.mkdir(exist_ok=True)
(out / 'bfcl.summary.json').write_text(json.dumps(output, indent=2) + '\n')
lines = ['# Main BFCL: three training seeds', '',
         'Official AST checker plus strict Qwen parser on five categories, not the full leaderboard. Authorized Glaive fallback, fixed data seed42.', '',
         '| Category | Cases/seed | Seed42 | Seed43 | Seed44 | Mean | Sample SD (pp) | Seed t 95% CI |',
         '|---|---:|---:|---:|---:|---:|---:|---|']
for category, row in categories.items():
    s = row['main_accuracy']
    lo, hi = s['seed_t_ci95']
    values = ' | '.join(f'{v:.2%}' for v in s['values'])
    lines.append(f"| {category} | {row['n_cases_per_seed']} | {values} | {s['mean']:.2%} | {100*s['sample_sd']:.2f} | [{lo:.2%}, {hi:.2%}] |")
lines += ['', '## Paired changes versus fixed baselines', '',
          '| Baseline | Category | Mean delta (pp) | Seed t 95% CI (pp) | Paired case 95% CI (pp), conditional on fitted seeds |',
          '|---|---|---:|---|---|']
for baseline in ('baseline-1.5b', 'baseline-7b'):
    for category, row in categories.items():
        comp = row['comparisons'][baseline]
        s = comp['delta_main_minus_baseline']
        lo, hi = s['seed_t_ci95']
        clo, chi = comp['paired_case_bootstrap_ci95_conditional_on_three_seeds']
        lines.append(f"| {baseline} | {category} | {100*s['mean']:+.2f} | [{100*lo:+.2f}, {100*hi:+.2f}] | [{100*clo:+.2f}, {100*chi:+.2f}] |")
lines += ['', 'All three main models underperform both baselines overall. Irrelevance improves, but parallel calling is almost absent. These results do not catch the 7B baseline and are not rerun away.', '',
          '## Uncertainty and limitations', '']
lines += [f'- {v}' for v in output['uncertainty'].values()]
lines += [f'- {v}' for v in output['limitations']]
lines += ['', 'Agent review is accepted, not human validation; both human_validation_complete and human_validation_required remain false. No training data or completed evaluation outcomes were changed.', '',
          'Reproduce this small CPU analysis: `python3 scripts/summarize_main_bfcl.py`. Full hashes and numerical precision are in `bfcl.summary.json`. E2 remains incomplete pending the remaining actual outputs and final analysis.']
(out / 'bfcl.summary.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(categories['overall_subset'], indent=2))
