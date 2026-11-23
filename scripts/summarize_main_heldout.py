#!/usr/bin/env python3
"""Summarize completed main Glaive held-out outcomes; no model execution."""
import hashlib
import json
from pathlib import Path
import statistics
from toolcall_lora.data import read_jsonl
from toolcall_lora.evaluate import paired_case_ci95

seeds = (42, 43, 44)
paths = {s: Path(f'results/formal-main-seed{s}') for s in seeds}
scores = {s: json.loads((p / 'heldout.score.json').read_text()) for s, p in paths.items()}
details = {s: {r['id']: r for r in read_jsonl(p / 'heldout.score.details.jsonl')}
           for s, p in paths.items()}
values = [scores[s]['overall_subset']['accuracy'] for s in seeds]
mean = statistics.mean(values)
sd = statistics.stdev(values)
half = 4.302652729911275 * sd / (3 ** 0.5)
per_case = [sum(int(details[s][i]['valid']) for s in seeds) / 3 for i in details[42]]
interval = paired_case_ci95(per_case)
result = {
    'scope': 'Main three-seed Glaive held-out JSON exact match; not BFCL or xLAM',
    'seeds': list(seeds), 'data_seed': 42, 'cases_per_seed': len(per_case),
    'individual': {str(s): scores[s]['overall_subset'] for s in seeds},
    'mean': mean, 'sample_sd': sd, 'seed_t_ci95': [mean - half, mean + half],
    'case_bootstrap_ci95_conditional_on_three_seeds': interval,
    'uncertainty': {
        'seed_t_ci95': 'Unclipped mean +/- t(0.975,df=2)*sample_sd/sqrt(3); only three training seeds with fixed data. Normal-seed assumption is weak. This is not the case-bootstrap interval.',
        'case_bootstrap': 'Estimand: within-case mean of the three fitted models, then resample cases. 1000 resamples, RNG seed42, file ID order, published indices 25/975. Per-seed score ci95 keeps the other published indices 24/974. 6000 seed-case outcomes are not independent cases.',
        'boundary': 'Seed and case intervals describe different uncertainties, not a joint seed/data interval. No baseline held-out delta is claimed.',
    },
    'sources': {str(s): {'path': str(p), 'dataset_sha256': scores[s]['dataset_sha256'],
                          'predictions_sha256': scores[s]['predictions_sha256'],
                          'score_sha256': hashlib.sha256((p / 'heldout.score.json').read_bytes()).hexdigest(),
                          'details_sha256': hashlib.sha256((p / 'heldout.score.details.jsonl').read_bytes()).hexdigest()}
                for s, p in paths.items()},
    'limitations': ['Agent review found semantic near-duplicates across Glaive splits; high accuracy is not evidence of uncontaminated generalization.',
                    'Synthetic Glaive source is the authorized fallback, not xLAM reproduction.',
                    'Agent negative review found one clear mislabel and two uncertain cases among50, not human-gold validation.',
                    'Ablations and final error analysis remain incomplete; no training data or original scores changed.'],
    'reviewer_type': 'agent', 'human_validation_complete': False,
    'human_validation_required': False,
}
out = Path('results/formal-main-summary')
out.mkdir(exist_ok=True)
(out / 'heldout.summary.json').write_text(json.dumps(result, indent=2) + '\n')
lines = ['# Main Glaive held-out: three training seeds', '',
         'Separate order-invariant JSON exact match with duplicate calls/types retained; not BFCL AST accuracy or xLAM reproduction.', '',
         '| Seed | Correct / cases | Accuracy | Case-bootstrap 95% CI |',
         '|---|---:|---:|---|']
for s in seeds:
    metric = scores[s]['overall_subset']
    correct = sum(r['valid'] for r in details[s].values())
    lo, hi = metric['ci95']
    lines.append(f"| {s} | {correct} / {metric['n']} | {metric['accuracy']:.2%} | [{lo:.2%}, {hi:.2%}] |")
lines += ['', f'Mean **{mean:.2%}**, sample SD **{100*sd:.2f} pp**; seed-t 95% CI **[{mean-half:.2%}, {mean+half:.2%}]** (df2).', '',
          f'Case-bootstrap CI conditional on these fitted models, indices 25/975: **[{interval[0]:.2%}, {interval[1]:.2%}]**.', '',
          '## Uncertainty and limitations', '']
lines += [f'- {v}' for v in result['uncertainty'].values()]
lines += [f'- {v}' for v in result['limitations']]
lines += ['', 'Agent review is accepted; human_validation_complete=false and human_validation_required=false. Agent findings are not human-gold metrics.', '',
          'Reproduce this small CPU analysis: `python3 scripts/summarize_main_heldout.py`. Source hashes and full precision are in `heldout.summary.json`.']
(out / 'heldout.summary.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({k: result[k] for k in ('mean', 'sample_sd', 'seed_t_ci95', 'case_bootstrap_ci95_conditional_on_three_seeds')}, indent=2))
