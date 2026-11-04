# Tool-calling LoRA: Qwen2.5 1.5B versus 7B

E2 measures native Qwen tool calling with LoRA and the official BFCL AST checker: **all three main seeds lose overall accuracy versus both baselines: 56.75% mean, 2.74 pp sample SD.** Training uses the authorized Glaive fallback, not xLAM. All main-seed evaluations are collected. E2 remains incomplete: exploratory ablations and final error analysis are still pending.

| BFCL category | Qwen2.5 1.5B | Qwen2.5 7B | LoRA seed42 | LoRA seed43 | LoRA seed44 | LoRA mean |
|---|---:|---:|---:|---:|---:|---:|
| simple_python (400) | 84.00% | 95.50% | 84.00% | 85.00% | 85.00% | 84.67% |
| multiple (200) | 83.00% | 95.50% | 57.50% | 56.00% | 71.50% | 61.67% |
| parallel (200) | 65.50% | 90.00% | 0.00% | 0.00% | 0.50% | 0.17% |
| parallel_multiple (200) | 62.50% | 86.50% | 21.00% | 1.50% | 17.00% | 13.17% |
| irrelevance (240) | 70.42% | 60.42% | 90.42% | 88.33% | 90.00% | 89.58% |
| Micro-average (1,240) | **74.76%** | **86.37%** | **57.26%** | **53.79%** | **59.19%** | **56.75%** |

- Seed42 overall: **710/1,240**, bootstrap 95% CI **54.68%–60.00%**; paired change versus 1.5B **−17.50 pp** [−20.56, −14.68]. This is not a three-seed conclusion.
- Irrelevance improves **+20.00 pp** [14.58, 25.42] versus 1.5B, while parallel accuracy falls to **0/200**. The negative transfer is retained, not rerun away.
- Seed43 overall: **667/1,240**, bootstrap 95% CI **51.13%–56.53%**; paired changes **−20.97 pp** [−24.03, −17.98] versus 1.5B and **−32.58 pp** [−35.65, −29.27] versus 7B. These remain individual seed results, not a three-seed aggregate.
- Seed44 overall: **734/1,240**, case-bootstrap 95% CI **56.53%–61.85%**. Main three-seed mean **56.75%**, seed-t 95% CI **49.95%–63.55%** (df2, weak normal-seed assumption). Mean deltas are **−18.01 pp** versus 1.5B and **−29.62 pp** versus 7B. Paired case-bootstrap CIs conditional on these fitted models are **[−21.02, −15.16]** and **[−32.61, −26.51]** pp, distinct from seed uncertainty; the 3,720 seed-case outcomes are not independent cases.
- Glaive held-out: seed42 **94.50%**, seed43 **94.65%**, seed44 **94.80%** (each 2,000 cases). Three-seed mean **94.65%**, sample SD **0.15 pp**; seed-t 95% CI **[94.28%, 95.02%]**. Case-bootstrap CI conditional on fitted models is **[93.62%, 95.65%]**, distinct from seed uncertainty. This is separate JSON exact match, not BFCL. Agent-observed semantic near-duplicates limit test independence; high accuracy does not establish uncontaminated generalization. [Full held-out summary](results/formal-main-summary/heldout.summary.md), reproduced with `python3 scripts/summarize_main_heldout.py`.

Raw outputs: [seed42](results/formal-main-seed42/), [seed43](results/formal-main-seed43/), [seed44](results/formal-main-seed44/). [Three-seed summary](results/formal-main-summary/bfcl.summary.md) retains per-category uncertainty and source hashes; reproduce with `python3 scripts/summarize_main_bfcl.py`. Individual paired analyses use `python3 scripts/compare_main_seed42.py --seed 43` (default42; seed44 also available). These are small saved-outcome analyses, not inference reruns.

1.5B bootstrap 95% CI: **72.42%–77.26%**. 7B bootstrap 95% CI: **84.35%–88.15%**. The paired difference is **+11.61 percentage points**, 95% CI **[+9.11, +14.27]**. These are measured five-category subset results, not full leaderboard scores. The completed main BFCL campaign does not establish overall LoRA gains or catch the 7B baseline. Raw responses and score provenance are saved with verified Drive copies.

On the 240 irrelevance cases, 7B is **10.00 percentage points worse** than 1.5B, with paired 95% CI **[-15.83, -4.17]**. This negative result is retained alongside the higher overall score.

## Current execution

Server Pi owns execution. The existing A100 foreground run is `E2-main-resume-20261104-03` on `exp-e24-recovery-a100`, source commit `04506d9943f5d9835d97a5edc25d5f76ae60ab60`. All main training and both evaluations per seed are collected. The six exploratory variants continue in that same pipeline, starting with n10000-r8-neg0 seed42. Do not submit it again. Read [HANDOFF.md](HANDOFF.md) for the latest checkpoint and download commands.

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
