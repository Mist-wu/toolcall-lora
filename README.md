# Tool-calling LoRA: Qwen2.5 1.5B versus 7B

E2 implements native Qwen tool-call training, separate development/test splits, and a five-category BFCL evaluation using the official AST checker. **The 1.5B baseline completed all 1,240 cases at 74.76% micro-accuracy. The original L4 runtime is no longer accessible; 698/1,240 unscored 7B predictions were recovered. Local Mac agents are preparing recovery; LoRA training has not started.**

| BFCL category | Qwen2.5 1.5B | Qwen2.5 7B |
|---|---:|---:|
| simple_python (400) | 84.00% | Incomplete |
| multiple (200) | 83.00% | Incomplete |
| parallel (200) | 65.50% | Incomplete |
| parallel_multiple (200) | 62.50% | Incomplete |
| irrelevance (240) | 70.42% | Incomplete |
| Micro-average (1,240) | **74.76%** | Incomplete |

1.5B bootstrap 95% CI: **72.42%–77.26%**. These are measured five-category subset results; the 7B comparison and LoRA improvements are not yet available. Raw responses and score provenance are saved with verified Drive copies.

## Current execution

Local Mac agents own execution; server pi is paused. The original run `E2-formal-baselines-20261104-01` used `exp-preflight-l4`, which disappeared from actual Colab assignments. The cause and any progress beyond the recovered snapshot are unknown. The 1.5B raw responses and scores were recovered from Drive into `results/formal-baselines/baseline-1.5b/`. The 7B snapshot is `results/formal-baselines/baseline-7b/predictions.partial-698.jsonl`; it is not a complete result.

A replacement GPU is being requested. The recovery entrypoint `bash scripts/recover_formal.sh` prepares the isolated environment, generates the remaining 542 7B cases, merges by case ID, and scores all 1,240 cases. It reconstructs and persists the fixed Glaive split, then continues main LoRA seeds 42, 43, and 44. It does not repeat the completed 1.5B baseline. Runtime allocation, launch receipt, and completion remain pending until observed.

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

Glaive conversion extracts only the first complete user/function-call pair, never flattens context-dependent follow-ups, logs skipped formats, and records that it is a different training source. Do not report Glaive-trained results as xLAM results. Both paths create independent grouped train/dev/test splits; duplicate normalized questions never cross splits. The original Glaive preparation produced **18,547 train / 2,003 dev / 2,000 test** examples; its unpersisted runtime files must be reconstructed from the same revision and split seed. Main uses all 18,547 training positives before sequence-length filtering. The 30k variant needs additional valid data and is currently unavailable.

Colab currently supplies Python 3.13 and newer torch/CUDA packages. This repository's pinned stack uses a separate Python **3.12** environment; do not install NumPy 1.26 into the system Python 3.13. The bootstrap leaves Colab's default environment intact. BFCL's NumPy 1.26 requirement also needs the explicit pyarrow 19.0.1 pin; newer Arrow wheels may require NumPy 2.

## Run on an already-owned Colab GPU

Use the shared experiment-runner transport from the Mac. On the replacement GPU, after staging the private rclone environment, submit:

```sh
bash scripts/recover_formal.sh
```

After recovery, `bash scripts/formal_train.sh` is the direct command for the main three-seed campaign using `/content/data/e2-glaive`. Artifacts are written to `/content/e2-artifacts`; normal checkpoint callbacks copy completed checkpoints through the configured rclone remote, and final adapters are exported for E3. Small scores are also copied to `results/`. Existing 1.5B results must be reused rather than running the original two-model baseline script again.

The planned matrix contains main, six 10k rank/negative variants, and a 30k variant: **24 training runs** across three seeds. Current Glaive data supports main and the six 10k variants; the three 30k runs remain blocked by insufficient unique training data. Completed matching training records are reused; incomplete runs resume the newest checkpoint after configuration validation. Evaluation is deterministically rerun rather than trusting partial files. Default inference is Transformers; `.[vllm]` plus `--backend vllm` enables batched vLLM inference. The formal baseline uses Transformers; vLLM has not been used for these results.

For T4 use `--profile t4`: fp16 with Trainer loss scaling, microbatch 2 and accumulation 16. L4/A100 use bf16, microbatch 4 and accumulation 8. Overlength training examples are dropped and counted, never partially truncated into invalid target JSON. Development loss uses a fixed 256-example sample; test data is never used for early selection.

## Metric boundaries and completion

BFCL scores are the `simple_python`, `multiple`, `parallel`, `parallel_multiple`, and `irrelevance` subset using official checker code plus the strict native Qwen tag parser. This is **not the full published leaderboard aggregate**. The independent held-out source dataset uses strict, order-invariant JSON exact match, with duplicate calls and JSON types preserved. Reports never combine these two metrics.

Negative examples use name-disjoint donated tools from the training split only. Name-disjointness does not prove semantic irrelevance: examine a fixed sample before claiming negative-training gains and record the limitation. The original answer/tool descriptions can still reveal semantically equivalent tools. Label noise is not hidden.

`docs/baselines.md` defines sources and comparability. `docs/cost.md` records CU, GPU duration, storage and API use. Finalization requires all configured runs, three seeds, raw prediction provenance, independent held-out scores, source comparison and negative-data review. Completion requires actual formal results for the reported coverage. Public benchmark contamination remains possible; held-out synthetic source data does not establish uncontaminated generalization.

See [HANDOFF.md](HANDOFF.md) for the exact next commands and current blockers.
