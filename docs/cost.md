# E2 cost ledger

E2 uses the coordinator-assigned existing NVIDIA L4 session `exp-preflight-l4`; this repository has not created another session or made paid provider API calls. The active formal run is `E2-formal-baselines-20261104-01`. Exact per-experiment CU attribution is unavailable; do not infer it from concurrent account-wide usage.

| Phase | GPU | Start UTC | End UTC | Wall duration | CU attributable | API USD | Result |
|---|---|---|---|---|---|---:|---|
| Formal Qwen2.5 1.5B, 1,240 BFCL cases | NVIDIA L4 | 2026-11-04 11:42:50 | 2026-11-04 11:55:37 | 767 s | Not available | 0 | Complete; 74.76% subset micro-accuracy |
| Formal Qwen2.5 7B, 1,240 BFCL cases | NVIDIA L4 | Inference metadata pending completion | Running at 2026-11-04 12:18:14 | Pending | Not available | 0 | 698 prediction lines observed |
| Main LoRA seeds 42,43,44 | Not started | — | — | — | — | 0 | Queued after E1/E4 GPU priority |

Inference timestamps come from `results/formal-baselines/baseline-1.5b.score.json`; the progress snapshot is in `results/formal-baselines/handoff-status.json`. The 1.5B interval excludes scoring and its verified Drive copy (11:55:44–11:55:56 UTC). The wrapper started at 11:42:43 UTC. Account CU remains recorded by the common coordinator; no purchase or spending ceiling was added.

The manual's roughly ten-hour E2 estimate is unvalidated for the full eight-configuration, three-seed campaign. Current Glaive preparation supplies 18,547 training positives, so the 30k configuration is unavailable. Record measured training duration and retained sequence counts before forecasting the remaining campaign.
