# E2 current handoff

## Update 2026-11-04 15:22 UTC

Existing A100 foreground run continues: seed 42 reached step 1001/1288 and the output subscriber is active. Step 1000 copied to `gdrive:exp/runs/E2/E2-main-s42-step1000-996c08718538` (rclone exit 0); receipt `results/main-seed42-checkpoint-1000.receipt.json`. Its training-time 256-example dev loss at epoch 1.55 was 0.000523304333910346, not a final test result. The final E3 adapter remains pending. Continue polling using the commands below; do not resubmit.

## Update 2026-11-04 15:15 UTC

Existing A100 foreground run continues: seed 42 reached step 901/1288 and the real-output subscriber is active. Step 900 copied to `gdrive:exp/runs/E2/E2-main-s42-step900-998e5ec60d6d` (rclone exit 0); receipt `results/main-seed42-checkpoint-900.receipt.json`. The 256-example training-time dev loss at epoch 1.4 was 0.0006694518961012363, not a test result. The completed adapter for E3 is still pending. Continue polling below; do not resubmit.

## Update 2026-11-04 15:08 UTC

Existing foreground run is active; seed 42 reached step 809/1288 and `exp-iopub-e24.service` is active. Step 800 was copied to `gdrive:exp/runs/E2/E2-main-s42-step800-0257573cff50` (rclone exit 0); receipt `results/main-seed42-checkpoint-800.receipt.json`. The 256-example dev loss at epoch 1.24 was 0.0005717489402741194, a training-time measurement, not a final test metric. This checkpoint is not the final E3 adapter. Continue polling with the commands below; do not resubmit.

## Update 2026-11-04 15:01 UTC

The existing foreground run remains active; seed 42 reached step 713/1288 and `exp-iopub-e24.service` is active. Step 700 copied successfully to `gdrive:exp/runs/E2/E2-main-s42-step700-d6e9866b9bb3` at 15:00 UTC; receipt: `results/main-seed42-checkpoint-700.receipt.json`. This is a training checkpoint, not the final adapter for E3. Continue polling using the commands below; do not resubmit.

## Update 2026-11-04 14:55 UTC

The existing `E2-main-resume-20261104-03` foreground run remains active, with output at seed 42 step 626/1288; `exp-iopub-e24.service` is active. Step 600 copied successfully to `gdrive:exp/runs/E2/E2-main-s42-step600-483a953ed830` at 14:53 UTC; the actual receipt is `results/main-seed42-checkpoint-600.receipt.json`. This is a checkpoint, not the finished adapter required by E3. Continue polling with the commands below; do not resubmit.

## Update 2026-11-04 14:48 UTC

Existing foreground run `E2-main-resume-20261104-03` is running; output reached seed 42 step 536/1288, and `exp-iopub-e24.service` remains active. The step-500 checkpoint was copied to `gdrive:exp/runs/E2/E2-main-s42-step500-3f88f4ca1b6a` at 14:46 UTC (rclone exit status 0); receipt: `results/main-seed42-checkpoint-500.receipt.json`. This checkpoint is not the finished adapter; E3 still awaits seed 42 completion. Continue polling with the commands below, without resubmission.

## Update 2026-11-04 14:41 UTC

The existing `E2-main-resume-20261104-03` job remains running on `exp-e24-recovery-a100`: HTTP status reports running and its real output reached seed 42 step 440/1288. The server's `exp-iopub-e24.service` is active. The checkpoint-400 rclone copy completed successfully at 14:38:56 UTC; receipt is `results/main-seed42-checkpoint-400.receipt.json` and destination is `gdrive:exp/runs/E2/E2-main-s42-step400-93abe7d040e8`. This is a resume checkpoint, **not** a finished adapter; E3 still waits for the final seed42 adapter and train record. At 14:41 UTC `colab usage` reported shared account balance 157.48 CU and total rate 17.34 CU/h across four assignments, not E2-only spending.

Poll without starting a second job:

```sh
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/status.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/status-observed.json
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/output.log /srv/exp-runner/state/remote/E2-main-resume-20261104-03/output-observed.log
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed42/last-verified-checkpoint.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/checkpoint-observed.json
```

**Started 2026-11-04 23:30:16 JST: `E2-main-resume-20261104-03` is running in the actual Jupyter kernel foreground (PID 6202).** Runtime `exp-e24-recovery-a100`, endpoint `gpu-a100-s-ass1b0-kysuwtw187ve` (A100 40GB). E4's model has exited; E2 owns the GPU. The Mac client continues reading real IOPub output while root/e8 attach the server client. Local writes freeze only when root explicitly confirms the handoff.

## Current run and exact next action

Running run: **`E2-main-resume-20261104-03`**, source commit **`04506d9943f5d9835d97a5edc25d5f76ae60ab60`**. Local request: `artifacts/E2-main-resume-20261104-03/request.json`; remote source and foreground entrypoint are already uploaded. Independent `/content/e2-venv`, Glaive data, step 300 checkpoint, and pinned 1.5B weights are prepared. Actual IOPub progress reached step 366/1288 at 2026-11-04T14:36:05.001476+00:00, confirming continuation beyond checkpoint 300. The current main42 adapter estimate is 00:35–00:50 JST on 2026-11-05, subject to remaining evaluation/copy overhead.

Already submitted payload; do not submit it again:

```sh
bash scripts/resume_formal.sh gdrive:exp/runs/E2/E2-main-s42-step300-4478da60bce6
```

The payload resumes seed 42 at step 300, completes main seeds 42/43/44, then directly runs all six 10k variants at seed 42. The original two baselines are not rerun. Actual work is submitted to the existing Jupyter kernel foreground and the client continuously consumes real IOPub output. Root/e8 own server connection continuity after the Mac handoff; attach to the existing message/run, never submit another model.

Remote root: `/content/experiment-runs/E2-main-resume-20261104-03`. HTTP downloads work while the kernel is busy:

```sh
colab download -s exp-e24-recovery-a100 \
  /content/experiment-runs/E2-main-resume-20261104-03/status.json status.json
colab download -s exp-e24-recovery-a100 \
  /content/experiment-runs/E2-main-resume-20261104-03/output.log output.log
colab download -s exp-e24-recovery-a100 \
  /content/experiment-runs/E2-main-resume-20261104-03/kernel-client.json kernel-client.json
```

`kernel-client.json` records the executed message ID and connection-file path for attaching a real output client. Use official SSH for file packaging or runtime inspection while the kernel is busy; an extra `colab exec` waits behind the active foreground job. Do not stop the only output client before the server client has attached.

## Durable evidence and resume files

- Both formal BFCL subset baselines completed 1240 cases: 1.5B **74.758%** (95% CI 72.419–77.258), 7B **86.371%** (84.355–88.145). Paired overall difference **+11.613pp** [9.113,14.274]. **Negative result:** 7B irrelevance is 60.42%, versus 1.5B 70.42%; paired difference −10pp [−15.83,−4.17]. Raw results and comparison are in `results/formal-baselines/`.
- Drive baselines: `gdrive:exp/runs/E2/E2-formal-baselines-20261104-01-baseline-1.5b` and `gdrive:exp/runs/E2/E2-formal-recovery-20261104-02-baseline-7b`.
- Fixed Glaive split: train 18547/dev 2003/test 2000, saved at `gdrive:exp/runs/E2/E2-glaive-data-20261104`. Native runtime path `/content/data/e2-glaive`.
- Latest recovered main checkpoint: `gdrive:exp/runs/E2/E2-main-s42-step300-4478da60bce6`; downloaded complete model/optimizer/scheduler/RNG/TrainerState(global_step 300). Matching request: `gdrive:exp/runs/E2/E2-formal-recovery-20261104-02-main-seed42-config/request.json`.
- Current local training output will be `/content/e2-artifacts/main-seed42`. Latest durable checkpoint receipt: `last-verified-checkpoint.json` there; checkpoints save every 100 optimizer steps. New saves include `request.json`; final adapter exports include `train.json`, `env.txt`, and `request.json`.
- E3 needs `/content/e2-artifacts/main-seed42/adapter` after seed 42 completes. Its Drive destination will be in the current workspace's `results/main-seed42.adapter-receipt.json`; matching training evidence is `results/main-seed42.train.json`. No final adapter exists yet.

## Scope, limits, and historical failures

Main requires seeds 42/43/44. Six 10k rank/negative variants first run seed 42 only and remain **single-seed exploratory**. Stable main-conclusion contrasts receive 43/44 only after selection on development data, never test scores. New train records include the most recent fixed 256-example dev loss and its evaluation step. The 30k variant remains blocked by only 18547 unique training positives. All 50 human negative-audit verdicts in `results/negative-audit/` are null; do not mark human review completed.

The earlier `exp-preflight-l4` and `exp-e4-qwen` runtimes disappeared; causes were not established. `E2-formal-recovery-20261104-02` is historical, not running. The follow-on `E2-exploratory-ablations-20261104-01` upload failed before execution; no separate follow-on process should be resumed. The new payload chains ablations directly.

Pinned stack: Python 3.12, torch 2.6.0+cu124, Transformers 4.51.3, PEFT 0.15.2, Accelerate 1.6.0, datasets 3.5.0, BFCL 2026.3.23. Private runtime files are `/content/e2-experiment-env.json` and `/content/e2-rclone.conf`; normal copies use `gdrive:exp/runs` with the existing quota header. Earlier shared throughput was about 4.2s/optimizer step; do not promise all seeds before bedtime or treat shared/resumed timings as a throughput benchmark. CU snapshots in `results/formal-baselines/usage-snapshots.jsonl` are account-wide, not E2-only charges.

Actual foreground receipt: `results/resume-03-kernel-client.json`. Message ID `4344e714-5beab0aa0d35eec67cb710a4_9905_1`; connection file `/root/.local/share/jupyter/runtime/kernel-66b45375-3f56-45c3-aedf-6272148d3275.json`. This identifies the existing execution for a subscribing output client, not a command to execute twice. Current request/status copies are `results/resume-03-request.json` and `results/resume-03-status.json`.
