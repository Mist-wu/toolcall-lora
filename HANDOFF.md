# E2 handoff to server pi

## Update 2026-11-04 12:30 UTC: runtime disappeared

`colab download -s exp-preflight-l4 /content/experiment-runs/E2-formal-baselines-20261104-01/status.json /srv/exp-runner/state/remote/E2-formal-baselines-20261104-01/status-direct.json` returned `Session 'exp-preflight-l4' not found`. `colab ls` listed six other active sessions, not this one; the leases file still calls it active and is stale. The last successful status, from 12:18 UTC, was running. Cause and subsequent progress are unknown; do not present the 7B as complete. Drive lists only the 1.5B baseline directory under E2, not the Glaive dataset or 7B output. The unpersisted `/content/data/e2-glaive` is not accessible through the missing session.

Collected the actual completed 1.5B raw predictions, metadata and scoring details from Drive to `results/formal-baselines/baseline-1.5b/` using `rclone copy gdrive:exp/runs/E2/E2-formal-baselines-20261104-01-baseline-1.5b/ results/formal-baselines/baseline-1.5b/`. Preserved the 698-line 7B progress snapshot at `results/formal-baselines/baseline-7b/predictions.partial-698.jsonl`; it is incomplete and must not be scored as a full baseline. No complete 7B or training adapter was found.

Next: reconcile the stale session lease and obtain a replacement GPU when available. Reconstruct the same Glaive splits with the existing preparation code, and continue the missing 7B cases from the saved snapshot rather than repeating the completed 1.5B baseline; `runtime.predict` currently overwrites its output and does not resume, so explicitly handle the remaining rows and merge by case ID. Stage the private rclone environment and save the reconstructed dataset to Drive promptly. Then run the actual three-seed training and ablations. The commands and source run receipt below remain historical, not a currently running job.

Local execution is handed off to the server. **Do not resubmit the active baseline or start E2 training until the coordinator gives E2 GPU ownership after E1 retrieval and E4 Qwen.** Existing runtime `exp-preflight-l4` remains running; no session was created or stopped at this handoff.

## Actual state at 2026-11-04 21:20 JST

- Formal run: `E2-formal-baselines-20261104-01`; runtime source commit `00932e411fc6a6441c1512955ffadecc90c41f27`.
- AWS request: `/srv/exp-runner/state/remote/E2-formal-baselines-20261104-01/request.json`.
- Colab workspace: `/content/experiment-runs/E2-formal-baselines-20261104-01/workspace`.
- Wrapper status is `running`. Latest downloaded 7B predictions have **698/1,240** lines at 21:18:14 JST; these are an incomplete progress snapshot, not a scored result.
- **1.5B completed all 1,240 cases:** micro-accuracy **0.7475806452**, bootstrap 95% CI **[0.7241935484, 0.7725806452]**. The five-category official AST-checker subset is not the full BFCL leaderboard score.
- Completed 1.5B data is verified at `gdrive:exp/runs/E2/E2-formal-baselines-20261104-01-baseline-1.5b`. Local/server receipts are under `results/formal-baselines/`.
- Glaive data is prepared at **`/content/data/e2-glaive`**, outside the run workspace: train **18,547**, dev **2,003**, test **2,000**. Persist this directory before releasing the runtime. Its manifest is saved in `results/formal-baselines/glaive-manifest.json`.
- No formal LoRA training has started. No completed adapter exists yet.

## First commands on the coordinator

Run as `exp-runner`. Download status through the CLI's HTTP download path; prior `colab exec` websocket inspection disconnected while the detached experiment remained alive. The original submission timeout is not evidence that it failed, so do not submit another baseline.

```sh
export PATH=/srv/exp-runner/runtime/python/bin:/usr/local/bin:/usr/bin:/bin
export PYTHONPATH=/srv/exp-runner/app:/srv/exp-runner/app/common
export COLAB_PYTHON=/srv/exp-runner/runtime/python/bin/python
colab download -s exp-preflight-l4 \
  /content/experiment-runs/E2-formal-baselines-20261104-01/status.json \
  /srv/exp-runner/state/remote/E2-formal-baselines-20261104-01/status-direct.json
cat /srv/exp-runner/state/remote/E2-formal-baselines-20261104-01/status-direct.json
```

After the wrapper exits successfully, collect completed outputs:

```sh
python -m exp_common.collect --session exp-preflight-l4 \
  --run-id E2-formal-baselines-20261104-01 \
  --output-dir /srv/exp-runner/state/remote/E2-formal-baselines-20261104-01 \
  results/formal-baselines
```

The archive receipt is `collection.json` in that output directory. Extract `artifacts.tgz` into `/srv/exp-runner/repos/toolcall-lora` to retain raw responses, scores, metadata, and both model Drive receipts. The completed run's `results/formal-baselines/status.json` must show `baselines_complete`; score the 7B output only after it contains all 1,240 cases. The existing script already performs that scoring and normal Drive copy.

## Preserve the prepared Glaive data

Before releasing this runtime, run the following Python on Colab. It uses the existing private rclone configuration and quota header without displaying them; the destination is under the authorized `gdrive:exp/runs`. Download its receipt to the AWS run receipt directory afterwards.

```python
import json, os, subprocess
from pathlib import Path
workspace = Path('/content/experiment-runs/E2-formal-baselines-20261104-01/workspace')
settings = json.loads(Path('/content/experiment-env.json').read_text())
for key in ('RCLONE_CONFIG', 'RCLONE_HEADER'):
    os.environ[key] = settings[key]
os.environ['PYTHONPATH'] = str(workspace / '.experiment-common')
subprocess.run([
    '/content/e2-venv/bin/python', '-m', 'exp_common.checkpoint',
    '--source', '/content/data/e2-glaive', '--experiment', 'E2',
    '--run-id', 'E2-glaive-data-20261104',
    '--receipt', str(workspace / 'results/formal-baselines/glaive-data.drive-receipt.json')
], check=True)
```

Destination: `gdrive:exp/runs/E2/E2-glaive-data-20261104`. Keep its manifest and split files together. If the coordinator later assigns another runtime, restore that directory to `/content/data/e2-glaive` using the staged rclone environment.

## Three-seed training after GPU reassignment

The server repo contains `scripts/formal_train.sh` and `scripts/formal_train.py`; the currently running immutable baseline workspace predates these files. Submit the latest server repo through the existing common runner only once the coordinator schedules E2. Command payload:

```sh
bash scripts/formal_train.sh
```

It uses the prepared Glaive split, main configuration seeds **42, 43, 44**, and artifacts `/content/e2-artifacts`. It trains each seed, exports that adapter to Drive, evaluates the five BFCL categories and independent held-out test, then collects raw results. It loads `/content/experiment-env.json` privately and sets the ordinary `EXP_CHECKPOINT_SYNC` copy command. Complete checkpoints can be resumed; record actual retained examples and training durations.

The existing isolated environment is `/content/e2-venv` (Python 3.12, torch 2.6.0+cu124, Transformers 4.51.3, PEFT 0.15.2, Accelerate 1.6.0, datasets 3.5.0, BFCL 2026.3.23). On a newly assigned runtime, prepare it with `bash scripts/colab_bootstrap.sh`. The current baseline's environment must remain untouched until its process finishes.

**E3 adapter contract:** after seed 42 finishes, adapter `/content/e2-artifacts/main-seed42/adapter`; portable Drive destination is recorded by `results/main-seed42.adapter-receipt.json`. Send E3 that completed receipt and the matching `main-seed42.train.json`. No adapter was supplied at this handoff.

## Remaining work and limits

- Run main and six 10k rank/negative ablations with seeds 42/43/44. **The 30k ablation is blocked by only 18,547 unique training positives**; obtain additional valid licensed training data or document this unavailable condition, never repeat data and label it 30k.
- xLAM is gated; the current campaign explicitly uses public Glaive. Do not label its outcomes xLAM reproduction.
- Audit the fixed synthetic tool-swapped negative examples for semantic label noise; human review remains pending.
- Record BFCL package/version differences before comparing published leaderboard numbers. Report confidence intervals, per-seed results, failed runs and negative findings.
- Add `results/formal-summary.json` only after actual required coverage and analysis. Keep raw predictions, score hashes, independent held-out results, training records, adapter receipts and costs. The main result is not complete merely because both baselines finish.
