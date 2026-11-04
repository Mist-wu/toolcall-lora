# E2 local recovery and execution

Local Mac agents own E2 execution; server pi is paused. **Formal recovery is running on the existing shared A100 session `exp-e4-qwen`.** L4/A100 allocation requests were refused and H100 lacked entitlement; no replacement assignment was created. Root authorized sharing E4's A100 after measuring 33,044 MiB free. Do not stop this runtime until E2 and E4 both finish.

- Run: `E2-formal-recovery-20261104-02`; source `0ac6399b38a1cf5bc6f3869fed4be70126cab23c`, clean at submission.
- Launch: 2026-11-04 12:51:14 UTC; wrapper status `running`, PID 9592.
- Local receipts: `artifacts/E2-formal-recovery-20261104-02/`; tracked copies `results/formal-baselines/recovery-request.json` and `recovery-status.json`.
- Remote: `/content/experiment-runs/E2-formal-recovery-20261104-02`.
- Independent E2 Python environment `/content/e2-venv`; private files `/content/e2-experiment-env.json` and `/content/e2-rclone.conf`. E4's environment and process are unchanged.
- Payload: remaining 542 7B cases, full merged 1,240-case scoring, then main seeds 42/43/44. GPU sharing is recorded in inference/training metadata; timings are not a throughput benchmark.

## Recovered evidence

The original run `E2-formal-baselines-20261104-01` used `exp-preflight-l4`. At 2026-11-04 12:30 UTC, that session was absent from actual Colab assignments and downloads returned `Session 'exp-preflight-l4' not found`. Its old lease and `running` status are historical. The disappearance cause and any later progress are unknown.

- **1.5B complete:** 1,240 official selected BFCL cases, micro-accuracy **0.7475806452**, bootstrap 95% CI **[0.7241935484, 0.7725806452]**. The raw predictions, metadata, score and details were recovered from Drive into `results/formal-baselines/baseline-1.5b/`.
- Verified 1.5B destination: `gdrive:exp/runs/E2/E2-formal-baselines-20261104-01-baseline-1.5b`; receipt `results/formal-baselines/baseline-1.5b.drive-receipt.json`. Do not repeat this completed baseline.
- **Historical 7B interruption:** `results/formal-baselines/baseline-7b/predictions.partial-698.jsonl` contains 698 of 1,240 cases, downloaded at 2026-11-04 12:18:14 UTC. Recovery has now completed those 542 cases and scored all 1,240: **86.37097%**, 95% CI **[84.35484%, 88.14516%]**. The final raw predictions and score are in `results/formal-baselines/baseline-7b/`; Drive copy `gdrive:exp/runs/E2/E2-formal-recovery-20261104-02-baseline-7b` completed at 13:16:40 UTC.
- The original Glaive split had **18,547 train / 2,003 dev / 2,000 test** examples. Its manifest survives at `results/formal-baselines/glaive-manifest.json`, but `/content/data/e2-glaive` was not persisted before the runtime disappeared. The same revision and seed were reconstructed on Mac and copied to `gdrive:exp/runs/E2/E2-glaive-data-20261104` at 12:46:27 UTC. The normal copy receipt is `results/formal-baselines/glaive-data.drive-receipt.json`; local files are `data/glaive/`.
- Main seed 42 began initialization at 13:17 UTC after both baseline copies completed. No completed adapter exists yet.

The original request remains at `/srv/exp-runner/state/remote/E2-formal-baselines-20261104-01/request.json`; copies of the request and last observed status are in `results/formal-baselines/`. These are provenance for the interrupted run, not current execution status.

## Recovery command

The already-running payload is below. Poll or collect its existing run ID; do not submit it again:

```sh
bash scripts/recover_formal.sh
```

The recovery entrypoint prepares Python 3.12, reconstructs and persists Glaive data, resumes the missing 7B cases without repeating 1.5B, and continues the main training campaign. The observed run and receipt paths are recorded above. Keep the original partial snapshot unchanged as provenance.

This shared runtime uses private `/content/e2-experiment-env.json`, `RCLONE_CONFIG=/content/e2-rclone.conf`, and the staged quota header. Credentials stay outside the repository and logs. Dataset, completed baseline, checkpoint and adapter copies use `gdrive:exp/runs`.

The pinned stack is an isolated `/content/e2-venv`: Python 3.12, torch 2.6.0+cu124, Transformers 4.51.3, PEFT 0.15.2, Accelerate 1.6.0, datasets 3.5.0, and BFCL 2026.3.23. `scripts/colab_bootstrap.sh` installs it without replacing Colab's default Python environment.

## Main three-seed training and E3 adapter

After data and baseline recovery, the direct continuation command is:

```sh
bash scripts/formal_train.sh
```

This uses `/content/data/e2-glaive`, main seeds **42, 43, 44**, and artifacts `/content/e2-artifacts`. Each seed trains, exports its adapter, and evaluates the five selected BFCL categories and independent held-out test. Normal checkpoint copies use `EXP_CHECKPOINT_SYNC`; completed checkpoints support resume. Record actual retained example counts and elapsed training time.

**E3 contract:** seed 42 adapter `/content/e2-artifacts/main-seed42/adapter`; its portable Drive destination is recorded in `results/main-seed42.adapter-receipt.json`. Send E3 the completed receipt and matching `main-seed42.train.json` when available. This is an expected output path, not a completed adapter claim.

## Remaining work and limitations

- Run main and six 10k rank/negative ablations with seeds 42/43/44. The **30k ablation is blocked by only 18,547 unique training positives**. Additional valid licensed data is required; repeating examples does not produce a 30k dataset.
- The campaign uses public Glaive because xLAM is gated. Do not describe its results as xLAM reproduction.
- Human review of the fixed synthetic tool-swapped negative sample remains pending; model-generated checks do not complete that review.
- These BFCL results use five single-turn categories and the official AST checker with the native Qwen parser. They are not the full published leaderboard aggregate. Record the BFCL package-version difference before comparing published numbers.
- Preserve raw predictions, score hashes, independent held-out results, per-seed records, adapter receipts, costs, failed runs and negative findings. Create `results/formal-summary.json` only after the actual required coverage and analysis.
