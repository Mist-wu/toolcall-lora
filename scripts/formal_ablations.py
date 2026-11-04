#!/usr/bin/env python3
"""After the main campaign, run the six predeclared exploratory ablations."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--after-run')
args = parser.parse_args()
root = Path('results');root.mkdir(exist_ok=True)
status_path = root / 'ablation-status.json'
def status(**fields):
    status_path.write_text(json.dumps(fields, indent=2) + '\n')

if args.after_run:
    status(state='waiting_for_main', main_run=args.after_run)
    main_status = Path('/content/experiment-runs') / args.after_run / 'status.json'
    while True:
        previous = json.loads(main_status.read_text())
        if previous['state'] != 'running':
            break
        time.sleep(30)
    if previous['state'] != 'succeeded':
        status(state='main_failed', main_run=args.after_run, returncode=previous.get('returncode'))
        raise SystemExit('Main campaign did not complete successfully; continue it before ablations')

settings = json.loads(Path(os.environ['E2_ENV_FILE']).read_text())
for key in ('RCLONE_CONFIG', 'RCLONE_HEADER'):
    os.environ[key] = settings[key]
os.environ['EXP_CHECKPOINT_SYNC'] = json.dumps([
    sys.executable, '-m', 'exp_common.checkpoint', '--source', '{source}',
    '--experiment', '{experiment}', '--run-id', '{run_id}', '--receipt', '{receipt}',
])
# Repoint the isolated editable package only after the earlier campaign has exited.
subprocess.run(['uv', 'pip', 'install', '--python', sys.executable, '--no-deps', '-e', '.'], check=True)
configs = [f'n10000-r{rank}-neg{negative}' for rank in (8, 16, 64) for negative in (0, 10)]
(root / 'ablation-plan.json').write_text(json.dumps({
    'scope': 'exploratory_single_seed', 'configs': configs, 'seeds': [42],
    'main_seeds': [42, 43, 44],
    'confirmation_rule': 'Only contrasts selected using development data receive seeds 43/44 before stable main-result claims; never select using test scores.',
    'development_metric': 'Most recent fixed-256-example development loss, with its actual evaluation step recorded in each train.json',
    'blocked': {'n30000-r16-neg10': 'Current training split has only 18547 unique positives'},
}, indent=2) + '\n')
completed = []
for name in configs:
    status(state='running', current=name, seed=42, completed=completed)
    subprocess.run([
        sys.executable, 'scripts/run_campaign.py', '--stage', 'train', '--run', name,
        '--seeds', '42', '--data', '/content/data/e2-glaive', '--artifacts', '/content/e2-artifacts',
    ], check=True)
    completed.append(name)
status(state='exploratory_ablations_complete', seeds=[42], completed=completed,
       confirmation='Development-selected contrasts require seeds 43/44 before stable claims',
       blocked_30k='Only 18547 unique training positives')
subprocess.run([
    sys.executable, '-m', 'exp_common.checkpoint', '--source', str(root), '--experiment', 'E2',
    '--run-id', os.environ['EXPERIMENT_RUN_ID'] + '-results',
    '--receipt', 'ablation-results.drive-receipt.json',
], check=True)
