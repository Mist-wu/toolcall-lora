#!/usr/bin/env bash
# Isolate E2's validated stack from Colab Python3.13 / CUDA13 system packages.
set -euo pipefail
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --quiet --target /content/e2-tools uv==0.10.11
  export PATH="/content/e2-tools/bin:$PATH"
fi
if ! /content/e2-venv/bin/python -c 'import sys; assert sys.version_info[:2] == (3, 12)' >/dev/null 2>&1; then
  uv venv --python 3.12 /content/e2-venv
fi
uv pip install --python /content/e2-venv/bin/python -e "$repo_root[train,data,bfcl]"
uv pip check --python /content/e2-venv/bin/python
/content/e2-venv/bin/python -c 'import torch,transformers,pyarrow,numpy; print({"torch":torch.__version__,"cuda":torch.version.cuda,"transformers":transformers.__version__,"numpy":numpy.__version__,"pyarrow":pyarrow.__version__,"gpu_available":torch.cuda.is_available()})'
