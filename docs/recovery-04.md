# E2 Mac continuation after the 2026-11-05 runtime loss

Mac owns continuation from 2026-11-05 10:45 JST. The server coordinator has
finished/stopped; the old Colab session is absent. Recovery is prepared, not
executed. At the latest direct observation the shared balance is 0 CU with no
assignments. Use a newly available A100 40GB runtime for the commands below;
allocation/recharge is outside this entrypoint.

## Actual remaining work

| Component | Completed and reused | Remaining |
|---|---|---|
| Baselines | Both 1,240-case BFCL evaluations | None |
| Main | Seeds 42/43/44, training and BFCL/held-out evaluation | None |
| Rank8 exploratory | neg0 and neg10 seed42, training and both evaluations | None |
| Rank16/neg0 exploratory | Training and exported adapter; first 608 BFCL predictions | 632 BFCL predictions, full scoring after merge, 2,000 held-out predictions/scoring |
| Rank16/neg10 exploratory | No completed training | Seed42 training and both evaluations |
| Rank64/neg0, rank64/neg10 exploratory | No completed training | Both seed42 trainings and both evaluations |
| Analysis | Main three-seed, rank8 paired contrasts and seven-label error evidence | Incorporate newly completed rank16/rank64 evidence and final synthesis |

This is 3 missing trainings and 12,352 missing inference cases. The 30k
configuration is separately unavailable because the frozen training split has
only 18,547 unique positives. Single-seed ablations remain exploratory;
development-selected confirmatory contrasts, if any, require seeds43/44.
Existing agent review is accepted; human_validation_complete=false and
human_validation_required=false. New human labels/retest are not requested.

## Recovery payload prepared on Mac

`python3 scripts/resume_remaining_ablations.py prepare` generated
`results/recovery-04/plan.json` and `bfcl.remaining.jsonl` from the actual saved
1,240-case reference and 608 cached predictions. Cached IDs match the exact
first 608 IDs, a whole number of original four-example batches. The missing
632 cases retain the original order and batch composition. The plan records
source/cache hashes, frozen model revision, dtype profile/backend and the actual
saved adapter/data destinations. No partial predictions were scored.

The existing `recover_formal.py` / `resume_formal.py` target the earlier baseline
or main-seed42 failure, so do **not** invoke those for this recovery. The new
entrypoint restores the already trained rank16/neg0 adapter, infers only the
missing BFCL suffix, combines cached/new predictions with segmented timing
provenance, then evaluates held-out and invokes the three still-untrained
configurations explicitly. It never enters main/rank8 training or evaluation.
The inference/checker implementation is byte-identical to source04506d9.

## Run after compute is available

Stage this committed source, the existing shared `exp_common` package and the
private E2 rclone configuration/environment file in the new Colab runtime.
Use the common runner with a new run ID and the actual foreground output client.
From the staged repository directory:

```sh
export PATH="/content/e2-tools/bin:$PATH"
export HF_HOME=/content/hf
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export E2_ENV_FILE=/content/e2-experiment-env.json
# EXPERIMENT_RUN_ID and PYTHONPATH including exp_common are set by the common runner.
bash scripts/colab_bootstrap.sh
/content/e2-venv/bin/python scripts/resume_remaining_ablations.py run
```

Keep the prior `l4` software profile (bf16, batch4) on A100, as used by the
original recorded requests; the profile label is not an assertion of accelerator
identity. The new metadata records actual hardware. The final adapter receipt
only establishes the earlier successful rclone copy; no new download/integrity
check has been performed on Mac. Actual restore will occur in the run above.

Outputs use `/content/e2-artifacts`. Rank16/neg0 collected results go directly
into `results/formal-ablations/n10000-r16-neg0-seed42/`, with a Drive copy after
each completed dataset. Later configurations follow `run_campaign.py`'s existing
collection/checkpoint workflow. Collect their complete raw predictions, metadata,
scores, details and training/environment/adapter receipts into their existing
per-variant result directories before extending comparisons and error analysis.
If another interruption occurs, inspect actual newly saved outputs/checkpoints
and resume only their missing portion; this entrypoint describes the specific
currently observed 608-case boundary, not a general restart-everything command.

## Timing evidence

Completed rank8 training took45m30s (neg0) and50m27s (neg10); rank16/neg0 took
45m03s. The rank8 BFCL passes took27m18s and25m32s, and held-out passes19m48s
and20m00s. These were shared A100 wall timings, not isolated throughput tests.
If the missing runs had the same timings, remaining work would be about5–5.5
A100 hours, plus runtime setup/model downloads/copies. Rank64 training and
inference have not been measured, so this is a conditional planning scenario,
not a completion deadline or upper bound. No CU invoice can be inferred from
shared-account balance differences.

Local validation covered real cached/reference ID alignment and count, preserved
batch boundaries, generated missing-case inputs, Python syntax and unchanged
inference/checker source. No GPU execution or new model results are claimed.
