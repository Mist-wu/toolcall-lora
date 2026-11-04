#!/usr/bin/env python3
"""Seven evidence-based BFCL error categories; never reruns the official checker."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from toolcall_lora.tool_format import parse_tool_calls

out = Path('results/formal-error-analysis')
reference = out / 'bfcl.evaluation.jsonl'
refs = {r['id']: r for r in map(json.loads, reference.read_text().splitlines())}
paths = {b: Path('results/formal-baselines') / b for b in ('baseline-1.5b', 'baseline-7b')}
paths.update({f'main-seed{s}': Path(f'results/formal-main-seed{s}') for s in (42, 43, 44)})
labels = ('wrong_function', 'missing_argument', 'wrong_type', 'wrong_value',
          'extra_call', 'missed_call', 'false_call')
rules = {
    'wrong_function': 'Official wrong_func_name, or parsed equal-count response whose function-name multiset differs from the reference. Unequal-count name mismatches are not forced into function substitution.',
    'missing_argument': 'Official missing_required or missing_optional. This means a benchmark-expected parameter, not necessarily a schema-required parameter.',
    'wrong_type': 'Official type_error:* diagnostic.',
    'wrong_value': 'Official value_error:* diagnostic.',
    'extra_call': 'Parsed response has more calls than reference, with at least one expected call. Irrelevance calls use false_call instead.',
    'missed_call': 'Parsed response has fewer calls than reference, including zero. Count deficit is not proof of a semantic reason.',
    'false_call': 'Parsed call on a zero-call irrelevance reference.',
}
models = {}
cases = []
for name, path in paths.items():
    predictions_path = path / ('predictions.jsonl' if name.startswith('baseline') else 'bfcl.predictions.jsonl')
    predictions = {r['id']: r for r in map(json.loads, predictions_path.read_text().splitlines())}
    details_path = path / 'bfcl.score.details.jsonl'
    details = [json.loads(l) for l in details_path.read_text().splitlines()]
    counts = Counter({label: 0 for label in labels})
    unresolved = Counter()
    category_counts = {}
    failures = 0
    for row in details:
        if row['valid']:
            continue
        failures += 1
        wanted = refs[row['id']]['ground_truth']
        expected_names = [next(iter(call)) for call in wanted]
        official = row.get('official_error_type') or (row['errors'][0] if row['errors'] else 'unspecified')
        evidence = set()
        record = {'model': name, 'id': row['id'], 'category': row['category'],
                  'official_error_type': official, 'official_errors': row['errors'],
                  'expected_count': len(wanted), 'expected_names': expected_names}
        try:
            calls = parse_tool_calls(predictions[row['id']]['text'])
        except ValueError as error:
            record.update(parse_error=str(error), actual_count=None)
            unresolved['parse_error'] += 1
        else:
            actual_names = [c['name'] for c in calls]
            record.update(actual_count=len(calls), actual_names=actual_names)
            if not wanted and calls:
                evidence.add('false_call')
            elif len(calls) > len(wanted):
                evidence.add('extra_call')
            elif len(calls) < len(wanted):
                evidence.add('missed_call')
            if official.endswith(':wrong_func_name') or (len(calls) == len(wanted) and Counter(actual_names) != Counter(expected_names)):
                evidence.add('wrong_function')
            if official.endswith((':missing_required', ':missing_optional')):
                evidence.add('missing_argument')
            if official.startswith('type_error:'):
                evidence.add('wrong_type')
            if official.startswith('value_error:'):
                evidence.add('wrong_value')
            if not evidence:
                unresolved[official] += 1
        record['evidence_labels'] = sorted(evidence)
        counts.update(evidence)
        category_counts.setdefault(row['category'], Counter()).update(evidence)
        cases.append(record)
    score = json.loads((path / 'bfcl.score.json').read_text())
    models[name] = {'cases': len(details), 'failed_cases': failures,
                    'evidence_case_counts': dict(counts), 'unresolved_case_counts': dict(unresolved),
                    'by_category': {k: dict(v) for k, v in category_counts.items()},
                    'dataset_sha256': score['dataset_sha256'],
                    'reference_sha256_matches_score': hashlib.sha256(reference.read_bytes()).hexdigest() == score['dataset_sha256'],
                    'predictions_path': str(predictions_path),
                    'predictions_sha256': hashlib.sha256(predictions_path.read_bytes()).hexdigest(),
                    'details_path': str(details_path),
                    'details_sha256': hashlib.sha256(details_path.read_bytes()).hexdigest()}
summary = {'scope': 'Completed main seeds and baselines, five-category BFCL subset; ablations pending',
           'rules': rules, 'models': models,
           'counting': 'Per-failed-case evidence, potentially multilabel, not an exhaustive seven-way partition or semantic root-cause annotation. Unresolved cases are retained, not assigned by guesswork. The official checker stops at a diagnostic, so argument counts are lower bounds.',
           'reference': str(reference), 'reference_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
           'reviewer_type': 'agent', 'human_validation_complete': False, 'human_validation_required': False,
           'limitations': 'No human labels or new judge ratings. Parser count deficits are observable behavior, not proof of why the model erred. BFCL pretraining contamination and Glaive negative-label noise/near-duplicates remain possible. No training data or official metrics changed.'}
(out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(out / 'cases.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in cases))
lines = ['# BFCL seven-category evidence analysis', '', summary['scope'], '', summary['counting'], '',
         '| Evidence category | ' + ' | '.join(models) + ' |',
         '|---|' + '---:|' * len(models)]
for label in labels:
    lines.append('| ' + label + ' | ' + ' | '.join(str(m['evidence_case_counts'][label]) for m in models.values()) + ' |')
for title, key in [('All failed cases', 'failed_cases')]:
    lines.append('| ' + title + ' | ' + ' | '.join(str(m[key]) for m in models.values()) + ' |')
lines += ['| Unresolved (including parser failures) | ' + ' | '.join(str(sum(m['unresolved_case_counts'].values())) for m in models.values()) + ' |', '', '## Definitions', '']
lines += [f'- **{k}**: {v}' for k, v in rules.items()]
lines += ['', '## Interpretation', '',
          'The main models show much more call omission than the baselines; the seven-way table separates count direction using actual parsed outputs rather than guessing from wrong_count alone. It does not attribute the regression causally to negative training before ablations finish. Missing-parameter/type/value counts only describe errors exposed by the official checker, not all latent errors.', '',
          'Ambiguous same-name, same-count parallel no-match cases remain unresolved rather than being declared value errors. Parser failures remain outside the seven labels, not automatically counted as missed calls. Full per-case evidence and unresolved checker labels are in `cases.jsonl` and `summary.json`.', '',
          summary['limitations'], ' Agent review is accepted, not human-gold validation; human_validation_complete=false and human_validation_required=false.', '',
          'Reproduce this small CPU analysis: `python3 scripts/analyze_bfcl_errors.py`. The saved reference file is the original 1,240-case prepared BFCL evaluation, with its SHA256 compared to each score provenance. No checker/inference rerun.']
(out / 'report.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({n: {'counts': m['evidence_case_counts'], 'unresolved': m['unresolved_case_counts'], 'reference_match': m['reference_sha256_matches_score']} for n, m in models.items()}, indent=2))
