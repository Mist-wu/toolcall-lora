#!/usr/bin/env bash
set -euo pipefail
export HF_HOME=/content/hf
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
uv pip install --python /content/e2-venv/bin/python --no-deps -e .
/content/e2-venv/bin/python scripts/formal_baselines.py
