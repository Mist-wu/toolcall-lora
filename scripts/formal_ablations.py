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

# Repoint the isolated editable package only after the earlier campaign has exited.
subprocess.run(['uv', 'pip', 'install', '--python', sys.executable, '--no-deps', '-e', '.'], check=True)
from toolcall_lora.checkpoint import configure_colab_persistence, format_hook
configure_colab_persistence()
configs = [f'n10000-r{rank}-neg{negative}' for rank in (8, 16, 64) for negative in (0, 10)]
(root / 'ablation-plan.json').write_text(json.dumps({
    'scope': 'exploratory_single_seed', 'configs': configs, 'seeds': [42],
    'main_seeds': [42, 43, 44],
    'confirmation_rule': 'Only contrasts selected using development data receive seeds 43/44 before stable main-result claims; never select using test scores.',
    'development_metric': 'development_evaluation records the most recent fixed-subset dev loss and its step. The adapter is saved at final_save_step.',
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
subprocess.run(format_hook(root, os.environ['EXPERIMENT_RUN_ID'] + '-results', 'ablation-results.drive-receipt.json'), check=True)
