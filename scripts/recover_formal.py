#!/usr/bin/env python3
"""Recover the lost E2 runtime: remaining 7B cases, then real main training."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from toolcall_lora.data import read_jsonl, write_jsonl


def cli(*args):
    subprocess.run([sys.executable, '-m', 'toolcall_lora.cli', *map(str, args)], check=True)


def persist(source, name, receipt):
    subprocess.run([
        sys.executable, '-m', 'exp_common.checkpoint', '--source', str(source),
        '--experiment', 'E2', '--run-id', name, '--receipt', str(receipt),
    ], check=True)


def prepare_data():
    data = Path('/content/data/e2-glaive')
    if not (data / 'manifest.json').exists():
        cli('prepare-glaive', '--output', data)
    persist(data, 'E2-glaive-data-20261104', root / 'glaive-data.drive-receipt.json')
    (root / 'glaive-manifest.json').write_text((data / 'manifest.json').read_text())
    return data


root = Path('results/formal-baselines')
root.mkdir(parents=True, exist_ok=True)
settings = json.loads(Path(os.environ.get('E2_ENV_FILE', '/content/experiment-env.json')).read_text())
for key in ('RCLONE_CONFIG', 'RCLONE_HEADER'):
    os.environ[key] = settings[key]
run_id = os.environ['EXPERIMENT_RUN_ID']
with ThreadPoolExecutor(max_workers=1) as pool:
    data_future = pool.submit(prepare_data)
    bfcl = root / 'bfcl.jsonl'
    cli('prepare-bfcl', '--output', bfcl)
    rows = read_jsonl(bfcl)
    output = root / 'baseline-7b'
    partial = output / 'predictions.partial-698.jsonl'
    previous = {row['id']: row for row in read_jsonl(partial)}
    remaining_rows = [row for row in rows if row['id'] not in previous]
    remaining_data = root / 'bfcl.remaining.jsonl'
    write_jsonl(remaining_data, remaining_rows)
    remaining_predictions = output / 'predictions.remaining.jsonl'
    print(f'Resuming formal 7B: {len(previous)} saved cases, {len(remaining_rows)} remaining; 1.5B already complete', flush=True)
    cli('predict', '--data', remaining_data, '--model', 'Qwen/Qwen2.5-7B-Instruct',
        '--output', remaining_predictions, '--batch-size', 2, '--max-new-tokens', 512)
    combined = {**previous, **{row['id']: row for row in read_jsonl(remaining_predictions)}}
    predictions = output / 'predictions.jsonl'
    write_jsonl(predictions, [combined[row['id']] for row in rows])
    metadata = json.loads(Path(str(remaining_predictions) + '.metadata.json').read_text())
    metadata['examples'] = len(rows)
    metadata['recovery'] = {
        'previous_run_id': 'E2-formal-baselines-20261104-01',
        'previous_source_commit': '00932e411fc6a6441c1512955ffadecc90c41f27',
        'previous_predictions': str(partial),
        'previous_predictions_sha256': hashlib.sha256(partial.read_bytes()).hexdigest(),
        'previous_examples': len(previous), 'new_examples': len(remaining_rows),
        'timing_boundary': 'started_at/finished_at cover only the recovered cases',
    }
    Path(str(predictions) + '.metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    cli('score', '--data', bfcl, '--predictions', predictions,
        '--output', output / 'bfcl.score.json', '--label', 'baseline-7b')
    persist(output, run_id + '-baseline-7b', root / 'baseline-7b.drive-receipt.json')
    data_future.result()
(root / 'status.json').write_text(json.dumps({
    'status': 'baselines_complete', 'cases_per_model': len(rows), 'formal': True,
    'baseline_1_5b_source': 'E2-formal-baselines-20261104-01',
    'baseline_7b_recovery_run': run_id,
    'training_data_source': 'glaiveai/glaive-function-calling-v2',
    'training_data_path': '/content/data/e2-glaive',
}, indent=2) + '\n')
persist(root, run_id + '-baselines', root.parent / 'baselines.drive-receipt.json')
subprocess.run(['bash', 'scripts/formal_train.sh'], check=True)
