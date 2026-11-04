# Tool-calling LoRA: Qwen2.5 1.5B versus 7B

E2 measures native Qwen tool calling with LoRA and the official BFCL AST checker: **completed main seed42 loses overall accuracy versus both baselines; the required three-seed campaign and ablations are still running.** Training uses the authorized Glaive fallback, not xLAM.

| BFCL category | Qwen2.5 1.5B | Qwen2.5 7B | 1.5B LoRA seed42 |
|---|---:|---:|---:|
| simple_python (400) | 84.00% | 95.50% | 84.00% |
| multiple (200) | 83.00% | 95.50% | 57.50% |
| parallel (200) | 65.50% | 90.00% | 0.00% |
| parallel_multiple (200) | 62.50% | 86.50% | 21.00% |
| irrelevance (240) | 70.42% | 60.42% | 90.42% |
| Micro-average (1,240) | **74.76%** | **86.37%** | **57.26%** |

- Seed42 overall: **710/1,240**, bootstrap 95% CI **54.68%–60.00%**; paired change versus 1.5B **−17.50 pp** [−20.56, −14.68]. This is not a three-seed conclusion.
- Irrelevance improves **+20.00 pp** [14.58, 25.42] versus 1.5B, while parallel accuracy falls to **0/200**. The negative transfer is retained, not rerun away.
- Glaive held-out: **1,890/2,000 = 94.50%** [93.40%, 95.55%], a separate JSON exact-match metric. Agent review found semantic near-duplicates across source splits, limiting test independence.

Raw seed42 outputs and reproducible paired analysis: [results/formal-main-seed42/](results/formal-main-seed42/). Run `python3 scripts/compare_main_seed42.py` to regenerate the comparison from saved outcomes (no inference).

1.5B bootstrap 95% CI: **72.42%–77.26%**. 7B bootstrap 95% CI: **84.35%–88.15%**. The paired difference is **+11.61 percentage points**, 95% CI **[+9.11, +14.27]**. These are measured five-category subset results, not full leaderboard scores. The seed42 comparison above does not establish stable LoRA gains. Raw responses and score provenance are saved with verified Drive copies.

On the 240 irrelevance cases, 7B is **10.00 percentage points worse** than 1.5B, with paired 95% CI **[-15.83, -4.17]**. This negative result is retained alongside the higher overall score.

## Current execution

Server Pi owns execution. The existing A100 foreground run is `E2-main-resume-20261104-03` on `exp-e24-recovery-a100`, source commit `04506d9943f5d9835d97a5edc25d5f76ae60ab60`. Seed42 training and both evaluations are collected; seed43 training, seed44 and the six exploratory variants continue in that same pipeline. Do not submit it again. Read [HANDOFF.md](HANDOFF.md) for the latest checkpoint and download commands.

Earlier L4/A100 runtimes disappeared for unknown reasons. Both baselines are now complete, including all 1,240 7B predictions; the historical 698-case partial file is not the final result. Historical recovery timings and the resumed seed42 segment are not uninterrupted throughput benchmarks. Actual metadata and attribution limits are in [docs/cost.md](docs/cost.md). The finished seed42 adapter and copy receipt are recorded in `results/main-seed42.adapter-receipt.json` for E3's separate comparison.

## Prepare data on Colab CPU

```sh
bash scripts/colab_bootstrap.sh
source /content/e2-venv/bin/activate
python3 -m toolcall_lora.cli prepare --output data/xlam
python3 -m toolcall_lora.cli prepare-bfcl
python3 -m toolcall_lora.cli matrix
```

xLAM is **gated (`auto`)**, verified from the Hugging Face API on 2026-11-04. Its terms need to have been accepted by the user; `HF_TOKEN` must stay out of logs/Git. The program does not accept terms or bypass the gate. If unavailable, use the specified public fallback:

```sh
python3 -m toolcall_lora.cli prepare-glaive --output data/glaive
```

Glaive conversion extracts only the first complete user/function-call pair, never flattens context-dependent follow-ups, logs skipped formats, and records that it is a different training source. Do not report Glaive-trained results as xLAM results. Both paths create grouped train/dev/test splits; identical normalized questions never cross splits, but this does not exclude semantic near-duplicates. The agent review found such cross-split similarities in Glaive. The original Glaive preparation produced **18,547 train / 2,003 dev / 2,000 test** examples; its prepared data is persisted at `gdrive:exp/runs/E2/E2-glaive-data-20261104`, with revision and split seed recorded in the manifest. Main uses all 18,547 training positives before sequence-length filtering. The 30k variant needs additional valid data and is currently unavailable.

Colab currently supplies Python 3.13 and newer torch/CUDA packages. This repository's pinned stack uses a separate Python **3.12** environment; do not install NumPy 1.26 into the system Python 3.13. The bootstrap leaves Colab's default environment intact. BFCL's NumPy 1.26 requirement also needs the explicit pyarrow 19.0.1 pin; newer Arrow wheels may require NumPy 2.

## Run on an already-owned Colab GPU

The current foreground pipeline is already running; observe it rather than submitting another command. For a clean reproduction, bootstrap the isolated environment, stage the private rclone configuration/header separately, and restore the pinned prepared data. From the repository workspace, use the direct campaign commands below. Do not use interactive Drive mounting or put credentials in source/result bundles.

After recovery, `bash scripts/formal_train.sh` is the direct command for the main three-seed campaign using `/content/data/e2-glaive`. Artifacts are written to `/content/e2-artifacts`; normal checkpoint callbacks copy completed checkpoints through the configured rclone remote, and final adapters are exported for E3. Small scores are also copied to `results/`. Existing 1.5B results must be reused rather than running the original two-model baseline script again.

The initial formal schedule is **main seeds 42/43/44 plus six 10k ablations at seed42** (9 training runs). The 10k variants are single-seed exploratory results, so they do not establish stable gains. Only contrasts selected using development data receive seeds43/44 before contributing stable main conclusions; never choose them using test scores. The 30k variant remains blocked by insufficient unique training data. The configuration catalog includes all seed files for later confirmation, but does not imply that every ablation runs three seeds. Completed matching training records are reused; incomplete runs resume the newest checkpoint after configuration validation. Do not rerun completed matching evaluations merely to test infrastructure; preserve their recorded provenance. Default inference is Transformers; `.[vllm]` plus `--backend vllm` enables batched vLLM inference. The formal baseline uses Transformers; vLLM has not been used for these results.

For T4 use `--profile t4`: fp16 with Trainer loss scaling, microbatch 2 and accumulation 16. L4/A100 use bf16, microbatch 4 and accumulation 8. Overlength training examples are dropped and counted, never partially truncated into invalid target JSON. Development loss uses a fixed 256-example sample; test data is never used for early selection.

## Metric boundaries and completion

BFCL scores are the `simple_python`, `multiple`, `parallel`, `parallel_multiple`, and `irrelevance` subset using official checker code plus the strict native Qwen tag parser. This is **not the full published leaderboard aggregate**. The separately held-out source dataset (with the independence limitation above) uses strict, order-invariant JSON exact match, with duplicate calls and JSON types preserved. Reports never combine these two metrics.

The accepted 50-example **agent**, not human, review is in `results/negative-audit/agent-review/`: 47 labels supported, one clear mislabel, two uncertain. No new human annotation or delayed retest is requested: `human_validation_complete=false`, `human_validation_required=false`. Agent ratings are not human-gold metrics, and existing training data/scores were not silently changed.

Negative examples use name-disjoint donated tools from the training split only. Name-disjointness does not prove semantic irrelevance: examine a fixed sample before claiming negative-training gains and record the limitation. The original answer/tool descriptions can still reveal semantically equivalent tools. Label noise is not hidden.

`docs/baselines.md` defines sources and comparability. `docs/cost.md` records CU, GPU duration, storage and API use. Finalization requires three seeds for main and any development-selected confirmatory contrasts, single-seed exploratory ablations clearly labeled, raw prediction provenance, separate held-out scores with independence limits disclosed, source comparison and negative-data review. Completion requires actual formal results for the reported coverage. Public benchmark contamination remains possible; held-out synthetic source data does not establish uncontaminated generalization.

See [HANDOFF.md](HANDOFF.md) for the exact next commands and current blockers.

The completed paired baseline analysis is [comparison.md](results/formal-baselines/comparison.md). Both models' raw predictions, scores and Drive receipts are retained.
