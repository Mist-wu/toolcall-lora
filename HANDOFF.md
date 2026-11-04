# E2 handoff

Status: implementation and local validation; **formal experiments not started**. Worktree: `toolcall-lora`. Heavy processes run in Colab, never on the 2GB coordinator. Scheduler root owns all GPU lifecycle.

## Ready

- Native Qwen protocol module `src/toolcall_lora/tool_format.py`, shared API with E3.
- xLAM conversion and strict grouped train/dev/test splits; public Glaive first-turn fallback.
- Assistant-only labels verified against actual Qwen tokenizer; no truncated target JSON.
- LoRA rank/negative/data-size matrix, checkpoint/resume, HF and optional vLLM inference.
- Official BFCL package integration tested against known answers from all five categories; 1,240 official bundled cases prepared under ignored `data/`.
- Exact JSON held-out scoring, seven error families plus parse/extra-argument diagnostics, bootstrap CIs, seed aggregation.
- Formal completion verifier refuses missing results and smoke evidence.

## Next commands

1. On Colab CPU, install `python3 -m pip install -e '.[train,data,bfcl]'`; run `python3 -m unittest discover -s tests -v` and the real-tokenizer test. Freeze actual GPU environment after compatibility probe.
2. Check already-authorized HF token for xLAM. Run `python3 -m toolcall_lora.cli prepare --output data/xlam`. If gated access unavailable, use `prepare-glaive --output data/glaive` and keep the fallback label in every report. Never accept terms or harvest credentials automatically.
3. Run `python3 -m toolcall_lora.cli prepare-bfcl`; persist `data/*/manifest.json` and actual datasets to Drive. Stage training data on `/content` when a GPU session starts.
4. On the owned L4, run a two-step `train --smoke` with a separate output directory, then `scripts/run_campaign.py --stage baselines --data data/xlam --artifacts /content/drive/MyDrive/exp/runs/e2/r01` (substitute `data/glaive` if fallback).
5. Run `scripts/run_campaign.py --stage train --run main --seeds 42 43 44 --data data/xlam --artifacts /content/drive/MyDrive/exp/runs/e2/r01`. Then all ablations with `--run all`. Record timing/CU and check non-finite loss before expanding. Campaign's train completion is distinct from evaluation completion.
6. Review fixed negative-tool samples for semantic label noise, compare to correctly versioned public baselines, inspect seven error families, and create final report. All claims must retain model revisions, package version, actual train size, discarded overlength counts and confidence intervals.

## Final evidence contract

Create `results/formal-summary.json` only after actual runs. Fields: `experiment_id:"E2"`, `status:"formal_complete"`, `synthetic:false`, `smoke:false`, `baseline_sources_verified:true`, `negative_data_audit_complete:true`, `records:[...]`, `heldout_test_score_files:[...]`. Each record has `label`, `score_files` (BFCL only), and non-baseline records have `train_files`. Labels: `baseline-1.5b`, `baseline-7b`, `main`, `n10000-r8-neg0`, `n10000-r8-neg10`, `n10000-r16-neg0`, `n10000-r16-neg10`, `n10000-r64-neg0`, `n10000-r64-neg10`, `n30000-r16-neg10`. Train and score seed coverage is 42/43/44; deterministic baselines have null seed. Scores reference persistent raw prediction files and hashes. Independent held-out test must have at least 2,000 examples.

`run_campaign.py` automatically runs `scripts/collect_results.py`: it copies raw predictions into ignored `results/raw/`, rewrites score paths to portable relative locations, and builds `results/collected-results.tar.gz`. Download/extract that archive into the server repo after each phase so the coordinator's verifier can check raw hashes without a Colab Drive mount. Keep checkpoints on Drive. The collector also works independently: `python3 scripts/collect_results.py /content/drive/MyDrive/exp/runs/e2/r01`. Run `python3 scripts/verify_completion.py` before reporting completion. Do not create formal-summary merely to satisfy the scheduler.

## Remaining uncertainties

- xLAM is confirmed gated, but this subtask has not inspected private credentials or accepted its terms.
- Colab package/CUDA compatibility, GPU memory and full-run performance have not been measured.
- The official website names BFCL 2025.12.17, while this implementation pins 2026.3.23; align or explicitly document before comparing published numbers.
- Synthetic tool-swapped negatives can have semantic label noise; do not claim perfect negative labels.
- Full matrix may exceed the handout's GPU-hour estimate. No numerical gain is guaranteed.
