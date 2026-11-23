#!/usr/bin/env python3
"""Continue the full main LoRA configuration for three seeds on prepared data."""
import subprocess
import sys
from toolcall_lora.checkpoint import configure_colab_persistence

configure_colab_persistence()
subprocess.run([sys.executable,"scripts/run_campaign.py","--stage","train","--run","main","--seeds","42","43","44","--data","/content/data/e2-glaive","--artifacts","/content/e2-artifacts"],check=True)
