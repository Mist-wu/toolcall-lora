#!/usr/bin/env python3
"""Resume the interrupted main seed42 from its actual Drive checkpoint."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

settings = json.loads(Path(os.environ['E2_ENV_FILE']).read_text())
for key in ('RCLONE_CONFIG', 'RCLONE_HEADER'):
    os.environ[key] = settings[key]
restored = Path('/content/e2-restored-checkpoint')
subprocess.run(['rclone', 'copy', sys.argv[1], str(restored)], check=True)
marker = json.loads((restored / 'complete.json').read_text())
step = marker['global_step']
out = Path('/content/e2-artifacts/main-seed42')
checkpoint = out / 'checkpoints' / f'checkpoint-{step}'
checkpoint.parent.mkdir(parents=True, exist_ok=True)
shutil.move(str(restored), str(checkpoint))
subprocess.run(['rclone', 'copyto',
    'gdrive:exp/runs/E2/E2-formal-recovery-20261104-02-main-seed42-config/request.json',
    str(out / 'request.json')], check=True)
data = Path('/content/data/e2-glaive')
if not (data / 'manifest.json').exists():
    subprocess.run(['rclone', 'copy', 'gdrive:exp/runs/E2/E2-glaive-data-20261104', str(data)], check=True)
print(f'Resuming formal main seed42 from durable step {step}; both baselines are already complete', flush=True)
subprocess.run(['bash', 'scripts/formal_train.sh'], check=True)
subprocess.run(['bash', 'scripts/formal_ablations.sh'], check=True)
