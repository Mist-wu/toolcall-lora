#!/usr/bin/env bash
set -euo pipefail
export HF_HOME=/content/hf
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
bash scripts/colab_bootstrap.sh
/content/e2-venv/bin/python scripts/recover_formal.py
