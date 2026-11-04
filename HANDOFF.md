# E2 current handoff

## Update 2026-11-04 16:23 UTC: seed 42 held-out score collected

The existing run completed 2,000 Glaive held-out predictions for main seed42: **94.5%** accuracy, bootstrap 95% CI **93.4–95.55%**. Full predictions, metadata, score and details are in `results/formal-main-seed42/heldout.*`. This is a single-seed result on the Glaive test split, not xLAM or a three-seed aggregate; the separately documented semantic near-duplicates across Glaive splits limit the test's independence. The existing foreground pipeline and output subscriber remain active; continue the remaining main seeds and variants without resubmitting.

```sh
root=/content/e2-artifacts
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.predictions.jsonl" results/formal-main-seed42/heldout.predictions.jsonl
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.predictions.jsonl.metadata.json" results/formal-main-seed42/heldout.predictions.jsonl.metadata.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.score.json" results/formal-main-seed42/heldout.score.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.score.details.jsonl" results/formal-main-seed42/heldout.score.details.jsonl
```

## Update 2026-11-04 16:16 UTC

The existing foreground job remains running; main seed42 held-out inference advanced to **1472/2000** predictions. Preserved the unscored incomplete snapshot at `results/formal-main-seed42/heldout.predictions.partial-1472.jsonl`. Subscriber PID 82069 remains active. Use the held-out download command below to poll; collect complete predictions, metadata and score when available, and do not resubmit the ongoing seed43/44 and ablation pipeline.

## Update 2026-11-04 16:10 UTC

The existing foreground job remains active and seed42 held-out inference reached 840/2000 cases; saved the incomplete, unscored snapshot in `results/formal-main-seed42/heldout.predictions.partial-840.jsonl`. Subscriber PID 82069 remains active. Continue the same job and collect its full held-out score; do not resubmit.

The separately performed **agent**, not human, audit of the 50 fixed negative examples is preserved in `results/negative-audit/agent-review/`. It judged 47 tool choices irrelevant, one clearly mislabeled (`glaive-20088-negative-991`), and two uncertain; it also found semantic near-duplicates across the Glaive splits. These directed observations do not quantify overall label noise or prove BFCL leakage; disclose the limitations and do not change this run or its scores. The 50 actual human verdicts remain pending.

## Update 2026-11-04 16:04 UTC: seed 42 BFCL score collected

The existing run completed all 1,240 five-category BFCL cases for main seed42. Collected predictions, metadata, score, and case details in `results/formal-main-seed42/`. Measured accuracy **57.258%** (bootstrap 95% CI **54.677–60.0%**), versus the same-dataset 1.5B baseline **74.758%**; parallel accuracy **0/200**, versus baseline **65.5%**. This is a negative single-seed result, not the three-seed aggregate or full leaderboard. Irrelevance accuracy was 90.42%. Preserve these results rather than rerunning to improve them. Held-out inference is underway: saved an unscored 252/2000 snapshot to `results/formal-main-seed42/heldout.predictions.partial-252.jsonl`. The foreground job and output subscriber PID 82069 remain active; do not resubmit.

```sh
root=/content/e2-artifacts
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.predictions.jsonl" results/formal-main-seed42/bfcl.predictions.jsonl
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.predictions.jsonl.metadata.json" results/formal-main-seed42/bfcl.predictions.jsonl.metadata.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.score.json" results/formal-main-seed42/bfcl.score.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.score.details.jsonl" results/formal-main-seed42/bfcl.score.details.jsonl
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.predictions.jsonl" /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42-heldout.partial.jsonl
```

## Update 2026-11-04 15:57 UTC

The existing foreground run remains running; seed42 BFCL predictions reached **896/1240**. Saved the incomplete snapshot to `results/formal-main-seed42/bfcl.predictions.partial-896.jsonl`; it is not a score. `exp-iopub-e24.service` was no longer present and no matching subscriber process was found; the reason is unknown. Attached one real-output subscriber to the existing busy kernel (PID 82069, log `/srv/exp-runner/logs/exp-e24-recovery-a100-iopub.log`), without submitting another job:

```sh
setsid -f /srv/exp-runner/runtime/python/bin/python /srv/exp-runner/app/ops/attach_existing_output.py exp-e24-recovery-a100 </dev/null >>/srv/exp-runner/logs/exp-e24-recovery-a100-iopub.log 2>&1
```

Continue polling the existing output/status and collect the full BFCL score and held-out results when ready. Do not resubmit.

## Update 2026-11-04 15:50 UTC

The existing foreground run remains active and is evaluating the completed main seed42 adapter on BFCL. Downloaded a **partial 536/1240 prediction snapshot**, `results/formal-main-seed42/bfcl.predictions.partial-536.jsonl`; it is not a scored result. The real output subscriber remains active. Shared account usage at 15:50 UTC: 137.24 CU balance, 17.34 CU/h across four assignments (not E2-only cost). Collect full predictions and scores when complete; held-out evaluation and later seeds/ablations remain in the running pipeline.

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed42-bfcl.predictions.jsonl /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42-bfcl.partial.jsonl
```

## Update 2026-11-04 15:44 UTC: seed 42 adapter complete

Main seed 42 completed two epochs at 15:43:24 UTC (18,547 selected positives, 20,608 training examples including negatives); actual training record is `results/main-seed42.train.json`. Its adapter was copied successfully to `gdrive:exp/runs/E2/E2-main-resume-20261104-03-main-seed42-adapter` at 15:43:44 UTC; copy receipt `results/main-seed42.adapter-receipt.json`. The run has started inference/evaluation and remains active; these are not yet final BFCL or held-out scores. E3 can use this actual adapter for its separate comparison; E3 HANDOFF records the destination. Seeds 43/44 and six seed42 variants are still in the existing pipeline. Do not resubmit.

Collected with:

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed42/train.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42.train.json
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/workspace/results/main-seed42.adapter-receipt.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42.adapter-receipt.json
```

## Update 2026-11-04 15:37 UTC

Existing A100 foreground run continues at seed 42 step 1203/1288; its output subscriber is active. Step 1200 copied to `gdrive:exp/runs/E2/E2-main-s42-step1200-599d0b33cb61` (rclone exit 0); receipt `results/main-seed42-checkpoint-1200.receipt.json`. The 256-example training-time dev loss at epoch 1.86 was 0.0005691974656656384, not a final test metric. The completed E3 adapter is still pending; collect its receipt and train record when ready. Poll below without resubmitting.

## Update 2026-11-04 15:30 UTC

The existing A100 foreground run continues, reaching seed 42 step 1103/1288; the actual output subscriber is active. Step 1100 copied to `gdrive:exp/runs/E2/E2-main-s42-step1100-751e50e86d79` (rclone exit 0); receipt `results/main-seed42-checkpoint-1100.receipt.json`. Training-time 256-example dev loss at epoch 1.71 was 0.0006018654676154256, not a final test result. The finished E3 adapter remains pending. Poll using the commands below; do not resubmit.

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
