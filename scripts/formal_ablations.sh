#!/usr/bin/env bash
set -euo pipefail
export HF_HOME=/content/hf
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
/content/e2-venv/bin/python scripts/formal_ablations.py --after-run "$1"
