#!/usr/bin/env python3
"""Stage or execute E2's actual post-loss remainder; allocate no runtime."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / 'results/recovery-04'
VARIANT = 'n10000-r16-neg0-seed42'
ORIGINAL = ROOT / 'results/formal-ablations' / VARIANT
REFERENCE = ROOT / 'results/formal-error-analysis/bfcl.evaluation.jsonl'
PARTIAL = ORIGINAL / 'bfcl.predictions.partial-608.jsonl'
REMAINING = ['n10000-r16-neg10', 'n10000-r64-neg0', 'n10000-r64-neg10']


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    rows, previous = read_rows(REFERENCE), read_rows(PARTIAL)
    # Exact prefix and complete batches let the resumed greedy inference retain
    # the original remaining batch composition instead of resampling cases.
    assert len(rows) == 1240 and len(previous) == 608
    assert [r['id'] for r in previous] == [r['id'] for r in rows[:608]]
    STAGE.mkdir(exist_ok=True)
    write_rows(STAGE / 'bfcl.remaining.jsonl', rows[608:])
    receipt = json.loads((ORIGINAL / 'adapter-receipt.json').read_text())
    plan = {
        'status': 'prepared_not_executed', 'owner': 'Mac',
        'adapter_destination': receipt['destination'],
        'data_destination': 'gdrive:exp/runs/E2/E2-glaive-data-20261104',
        'reference_sha256': sha(REFERENCE), 'cached_predictions_sha256': sha(PARTIAL),
        'cached_cases': 608, 'remaining_bfcl_cases': len(rows[608:]),
        'remaining_heldout_cases': 2000, 'remaining_training_configs': REMAINING,
        'seeds': [42], 'scope': 'single-seed exploratory ablations',
        'inference': {'model': 'Qwen/Qwen2.5-1.5B-Instruct',
                      'revision': '989aa7980e4cf806f80c7fef2b1adb7bc71aa306',
                      'backend': 'transformers', 'profile': 'l4', 'batch_size': 4,
                      'max_new_tokens': 512, 'accelerator_to_restore': 'A100 40GB'},
        'cache_provenance': 'Original run E2-main-resume-20261104-03, source 04506d9; snapshot recovered at 2026-11-05 00:48 UTC. Its inference did not finish, so no original completed inference metadata/timing is claimed.',
        'completed_reused': 'Both baselines, main seeds42/43/44, both rank8 variants, rank16/no-negative training.',
        'human_validation_complete': False, 'human_validation_required': False,
    }
    (STAGE / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    print(json.dumps(plan, indent=2))


def execute():
    os.chdir(ROOT)
    plan = json.loads((STAGE / 'plan.json').read_text())
    settings = json.loads(Path(os.environ['E2_ENV_FILE']).read_text())
    for key in ('RCLONE_CONFIG', 'RCLONE_HEADER'):
        os.environ[key] = settings[key]
    run_id = os.environ['EXPERIMENT_RUN_ID']
    os.environ['EXP_CHECKPOINT_SYNC'] = json.dumps([
        sys.executable, '-m', 'exp_common.checkpoint', '--source', '{source}',
        '--experiment', '{experiment}', '--run-id', '{run_id}', '--receipt', '{receipt}',
    ])
    from toolcall_lora.checkpoint import format_hook, require_formal_persistence
    require_formal_persistence()
    artifacts = Path('/content/e2-artifacts')
    adapter = artifacts / VARIANT / 'adapter'
    data = Path('/content/data/e2-glaive')
    subprocess.run(['rclone', 'copy', plan['adapter_destination'], str(adapter)], check=True)
    subprocess.run(['rclone', 'copy', plan['data_destination'], str(data)], check=True)
    assert json.loads((adapter / 'request.json').read_text()) == json.loads((ORIGINAL / 'request.json').read_text())
    for name in ('train.json', 'request.json', 'env.txt'):
        shutil.copy2(adapter / name, adapter.parent / name)
    reference = Path('data/bfcl/evaluation.jsonl')
    reference.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REFERENCE, reference)
    score = json.loads((ROOT / 'results/formal-main-seed42/bfcl.score.json').read_text())
    Path(str(reference) + '.manifest.json').write_text(json.dumps(score['data_manifest'], indent=2) + '\n')

    def cli(*args):
        subprocess.run([sys.executable, '-m', 'toolcall_lora.cli', *map(str, args)], check=True)

    def predict(dataset, output):
        cfg = plan['inference']
        cli('predict', '--data', dataset, '--model', cfg['model'], '--revision', cfg['revision'],
            '--adapter', adapter, '--output', output, '--backend', cfg['backend'],
            '--profile', cfg['profile'], '--batch-size', cfg['batch_size'],
            '--max-new-tokens', cfg['max_new_tokens'])

    remaining = artifacts / f'{VARIANT}-bfcl.remaining.predictions.jsonl'
    predict(STAGE / 'bfcl.remaining.jsonl', remaining)
    merged = artifacts / f'{VARIANT}-bfcl.predictions.jsonl'
    previous, new = read_rows(PARTIAL), read_rows(remaining)
    assert [r['id'] for r in new] == [r['id'] for r in read_rows(STAGE / 'bfcl.remaining.jsonl')]
    write_rows(merged, previous + new)
    metadata = json.loads(Path(str(remaining) + '.metadata.json').read_text())
    metadata.update(examples=1240, recovery={
        'plan': plan, 'original_predictions': str(PARTIAL.relative_to(ROOT)),
        'new_predictions_sha256': sha(remaining),
        'timing_boundary': 'started_at/finished_at describe only the 632 newly inferred cases',
    })
    Path(str(merged) + '.metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    for dataset, name in ((reference, 'bfcl'), (data / 'test.jsonl', 'heldout')):
        predictions = artifacts / f'{VARIANT}-{name}.predictions.jsonl'
        if name == 'heldout':
            predict(dataset, predictions)
        result = artifacts / f'{VARIANT}-{name}.score.json'
        cli('score', '--data', dataset, '--predictions', predictions, '--output', result,
            '--label', 'n10000-r16-neg0', '--seed', 42)
        destination = ROOT / 'results/formal-ablations' / VARIANT
        for source, target in ((predictions, f'{name}.predictions.jsonl'),
                               (Path(str(predictions) + '.metadata.json'), f'{name}.predictions.jsonl.metadata.json'),
                               (result, f'{name}.score.json'),
                               (result.with_suffix('.details.jsonl'), f'{name}.score.details.jsonl')):
            shutil.copy2(source, destination / target)
        subprocess.run(format_hook(destination, run_id + '-' + VARIANT + '-results', STAGE / (name + '.drive-receipt.json')), check=True)
    for name in REMAINING:
        subprocess.run([sys.executable, 'scripts/run_campaign.py', '--stage', 'train', '--run', name,
                        '--seeds', '42', '--data', str(data), '--artifacts', str(artifacts)], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'run'])
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else execute()
