# E2 handoff

Status: **formal 1.5B and 7B BFCL baselines running** in detached run `E2-formal-baselines-20261104-01` on `exp-preflight-l4`. AWS receipt directory: `/srv/exp-runner/state/remote/E2-formal-baselines-20261104-01`. Worktree: `toolcall-lora`. Heavy processes run in Colab, never on the 2GB coordinator. Scheduler root owns all GPU lifecycle.

## Ready

- Native Qwen protocol module `src/toolcall_lora/tool_format.py`, shared API with E3.
- xLAM conversion and strict grouped train/dev/test splits; public Glaive first-turn fallback.
- Assistant-only labels verified against actual Qwen tokenizer; no truncated target JSON.
- LoRA rank/negative/data-size matrix, checkpoint/resume, HF and optional vLLM inference.
- Official BFCL package integration tested against known answers from all five categories; 1,240 official bundled cases prepared under ignored `data/`.
- Exact JSON held-out scoring, seven error families plus parse/extra-argument diagnostics, bootstrap CIs, seed aggregation.
- Formal results remain distinct from implementation progress.

## Next commands

1. On Colab CPU, run `bash scripts/colab_bootstrap.sh`, then use `/content/e2-venv/bin/python` for all E2 commands (or activate that environment). Do not change the runtime's Python3.13/torch2.11 stack. The existing L4 already has the isolated environment; use it directly.
2. Check already-authorized HF token for xLAM. Run `python3 -m toolcall_lora.cli prepare --output data/xlam`. If gated access unavailable, use `prepare-glaive --output data/glaive` and keep the fallback label in every report. Never accept terms or harvest credentials automatically.
3. Run `python3 -m toolcall_lora.cli prepare-bfcl`; persist `data/*/manifest.json` and actual datasets to Drive. Stage training data on `/content` when a GPU session starts.
4. Adopt the already-running formal baseline job rather than launching it again. It writes `results/formal-baselines/<model>/bfcl.score.json` and prepares `/content/data/e2-glaive` in parallel. After successful completion, collect the official baseline outputs and the data manifest.
5. Run `scripts/run_campaign.py --stage train --run main --seeds 42 43 44 --data data/xlam --artifacts /content/e2-artifacts`. Then all ablations with `--run all`. Record timing/CU and check non-finite loss before expanding. Campaign's train completion is distinct from evaluation completion.
6. Review fixed negative-tool samples for semantic label noise, compare to correctly versioned public baselines, inspect seven error families, and create final report. All claims must retain model revisions, package version, actual train size, discarded overlength counts and confidence intervals.

## Final evidence contract

Create `results/formal-summary.json` only after actual runs. Fields: `experiment_id:"E2"`, `status:"formal_complete"`, `synthetic:false`, `smoke:false`, `baseline_sources_verified:true`, `negative_data_audit_complete:true`, `records:[...]`, `heldout_test_score_files:[...]`. Each record has `label`, `score_files` (BFCL only), and non-baseline records have `train_files`. Labels: `baseline-1.5b`, `baseline-7b`, `main`, `n10000-r8-neg0`, `n10000-r8-neg10`, `n10000-r16-neg0`, `n10000-r16-neg10`, `n10000-r64-neg0`, `n10000-r64-neg10`, `n30000-r16-neg10`. Train and score seed coverage is 42/43/44; deterministic baselines have null seed. Scores reference persistent raw prediction files and hashes. Independent held-out test must have at least 2,000 examples.

`run_campaign.py` automatically runs `scripts/collect_results.py`: it copies raw predictions into ignored `results/raw/`, rewrites score paths to portable relative locations, and builds `results/collected-results.tar.gz`. Download/extract that archive into the server repo after each phase so the coordinator's verifier can check raw hashes without a Colab Drive mount. Keep checkpoints on Drive. The collector also works independently: `python3 scripts/collect_results.py /content/e2-artifacts`. Run `python3 scripts/verify_completion.py` before reporting completion. Do not create formal-summary merely to satisfy the scheduler.

## Normal checkpoint persistence

Formal training uses local `/content/e2-artifacts/<config>-seed<seed>/` plus `EXP_CHECKPOINT_SYNC`, a JSON argv using `{source}`, `{run_id}`, `{receipt}`, `{experiment}`. The Trainer writes a complete marker after saving, then invokes the shared `exp_common.checkpoint` copy. Runtime rclone configuration is provided by root. Resume uses the completed checkpoint and preserves the last verified copy. The E3 comparison adapter contract is `/content/e2-artifacts/main-seed42/adapter`, with the exported Drive/AWS receipt supplied after completion.

## Remaining uncertainties

- xLAM is confirmed gated, but this subtask has not inspected private credentials or accepted its terms.
- The isolated Python3.12/torch2.6+cu124 stack is running on NVIDIA L4. Full training memory/performance is not yet measured.
- The official website names BFCL 2025.12.17, while this implementation pins 2026.3.23; align or explicitly document before comparing published numbers.
- Synthetic tool-swapped negatives can have semantic label noise; do not claim perfect negative labels.
- Full matrix may exceed the handout's GPU-hour estimate. No numerical gain is guaranteed.

## Current measured baseline and data

The 1.5B baseline completed all 1,240 official selected cases: micro-accuracy 0.7475806452, bootstrap 95% CI [0.7241935484, 0.7725806452]. Drive copy is verified at `gdrive:exp/runs/E2/E2-formal-baselines-20261104-01-baseline-1.5b`. The 7B baseline is still running. Public Glaive preparation produced train 18,547 / dev 2,003 / test 2,000; main uses all 18,547 positives. The 30k ablation is unavailable without additional valid data; never repeat examples and call that 30k.

Next direct GPU command after baseline completion: `bash scripts/formal_train.sh`. It runs main seeds 42, 43, 44 from `/content/data/e2-glaive`, with artifacts in `/content/e2-artifacts`, rclone configuration loaded privately from `/content/experiment-env.json`, and per-seed final adapter receipts under `results/`.
