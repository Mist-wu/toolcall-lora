# Tool-calling LoRA: Qwen2.5 1.5B versus 7B

E2 implements native Qwen tool-call training, separate development/test splits, and a five-category BFCL evaluation using the official AST checker. **Formal GPU experiments have not run; no measured accuracy or improvement is claimed.**

| Evidence | Current status |
|---|---|
| Core parser, split, masking and evaluation logic | Implemented with offline tests |
| Real Qwen tokenizer/template | Checked with pinned model tokenizer |
| BFCL package and data | `bfcl-eval==2026.3.23`, 1,240 cases in selected categories |
| LoRA training/ablation accuracy | Pending Colab GPU execution |

## Quick validation

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 scripts/verify_completion.py  # intentionally fails until formal evidence exists
```

The coordinator needs no torch dependency. All training, model inference and full dependency installs belong on Colab. Optional tests: `E2_TOKENIZER_TEST=1` enables a real-tokenizer check; `E2_TRAINING_TEST=1` enables two tiny random-model CPU steps plus checkpoint recovery. Tiny random-model output is test evidence only.

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

Glaive conversion extracts only the first complete user/function-call pair, never flattens context-dependent follow-ups, logs skipped formats, and records that it is a different training source. Do not report Glaive-trained results as xLAM results. Both paths create independent grouped train/dev/test splits (2,000 dev, 2,000 test); duplicate normalized questions never cross splits. The “60k main run” therefore means **all remaining training examples**, approximately 56k before deduplication/length filtering, not 60k plus leaked held-out records.

Colab currently supplies Python 3.13 and newer torch/CUDA packages. This repository's pinned stack uses a separate Python **3.12** environment; do not install NumPy 1.26 into the system Python 3.13. The bootstrap leaves Colab's default environment intact. BFCL's NumPy 1.26 requirement also needs the explicit pyarrow 19.0.1 pin; newer Arrow wheels may require NumPy 2.

## Run on an already-owned Colab GPU

Use the shared experiment-runner transport. This repository never creates or stops a Colab session. Stage data from Drive to `/content/data` before these commands. Point `--artifacts` at the run's persistent Drive directory; checkpoints and raw predictions are saved there, small scores are also copied to `results/`.

```sh
python3 scripts/run_campaign.py --stage baselines --data data/xlam \
  --artifacts /content/drive/MyDrive/exp/runs/e2/r01
python3 scripts/run_campaign.py --stage train --run main --seeds 42 43 44 \
  --data data/xlam --artifacts /content/drive/MyDrive/exp/runs/e2/r01
python3 scripts/run_campaign.py --stage train --run all --seeds 42 43 44 \
  --data data/xlam --artifacts /content/drive/MyDrive/exp/runs/e2/r01
```

`run all` includes the main configuration and six 10k rank/negative variants plus the 30k variant: **24 training runs**, with three seeds each. Completed matching training records are reused; incomplete runs resume the newest checkpoint after configuration validation. Evaluation is deterministically rerun rather than trusting partial files. Default inference is Transformers; `.[vllm]` plus `--backend vllm` enables batched vLLM inference. vLLM has separate CUDA compatibility requirements and must pass the GPU probe before selection.

For T4 use `--profile t4`: fp16 with Trainer loss scaling, microbatch 2 and accumulation 16. L4/A100 use bf16, microbatch 4 and accumulation 8. Overlength training examples are dropped and counted, never partially truncated into invalid target JSON. Development loss uses a fixed 256-example sample; test data is never used for early selection.

## Metric boundaries and completion

BFCL scores are the `simple_python`, `multiple`, `parallel`, `parallel_multiple`, and `irrelevance` subset using official checker code plus the strict native Qwen tag parser. This is **not the full published leaderboard aggregate**. The independent held-out source dataset uses strict, order-invariant JSON exact match, with duplicate calls and JSON types preserved. Reports never combine these two metrics.

Negative examples use name-disjoint donated tools from the training split only. Name-disjointness does not prove semantic irrelevance: examine a fixed sample before claiming negative-training gains and record the limitation. The original answer/tool descriptions can still reveal semantically equivalent tools. Label noise is not hidden.

`docs/baselines.md` defines sources and comparability. `docs/cost.md` records CU, GPU duration, storage and API use. Finalization requires all configured runs, three seeds, raw prediction provenance, independent held-out scores, source comparison and negative-data review. `scripts/verify_completion.py` rejects absent, synthetic or smoke results. Public benchmark contamination remains possible; held-out synthetic source data does not establish uncontaminated generalization.

See [HANDOFF.md](HANDOFF.md) for the exact next commands and current blockers.
