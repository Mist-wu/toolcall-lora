#!/usr/bin/env python3
"""Continue the full main LoRA configuration for three seeds on prepared data."""
import json
import os
from pathlib import Path
import subprocess
import sys

settings=json.loads(Path(os.environ.get("E2_ENV_FILE", "/content/experiment-env.json")).read_text())
for name in ["RCLONE_CONFIG","RCLONE_HEADER"]:
    os.environ[name]=settings[name]
os.environ["EXP_CHECKPOINT_SYNC"]=json.dumps([sys.executable,"-m","exp_common.checkpoint","--source","{source}","--experiment","{experiment}","--run-id","{run_id}","--receipt","{receipt}"])
from toolcall_lora.checkpoint import require_formal_persistence
require_formal_persistence()
subprocess.run([sys.executable,"scripts/run_campaign.py","--stage","train","--run","main","--seeds","42","43","44","--data","/content/data/e2-glaive","--artifacts","/content/e2-artifacts"],check=True)
