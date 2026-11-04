# E2 cost ledger

The original formal run `E2-formal-baselines-20261104-01` used the coordinator-assigned NVIDIA L4 session `exp-preflight-l4`. That session disappeared from actual assignments; the cause and exact end time are unknown. Local Mac agents are requesting a replacement GPU. No paid provider API calls have been made for E2. Exact per-experiment CU attribution is unavailable; concurrent account-wide usage is not an E2-specific measurement.

| Phase | GPU | Start UTC | End UTC | Wall duration | CU attributable | API USD | Result |
|---|---|---|---|---|---|---:|---|
| Formal Qwen2.5 1.5B, 1,240 BFCL cases | NVIDIA L4 | 2026-11-04 11:42:50 | 2026-11-04 11:55:37 | 767 s | Not available | 0 | Complete; 74.76% subset micro-accuracy |
| Original Qwen2.5 7B inference | NVIDIA L4 | No completed inference metadata | Unknown; last snapshot 2026-11-04 12:18:14 | Unknown | Not available | 0 | Interrupted; 698/1,240 predictions recovered |
| Remaining 542 Qwen2.5 7B cases | Replacement GPU pending | Not started | — | — | — | 0 | Recovery prepared; no completed result claimed |
| Main LoRA seeds 42,43,44 | Replacement GPU pending | Not started | — | — | — | 0 | Continues after data and 7B recovery |

The 1.5B timestamps come from `results/formal-baselines/baseline-1.5b/predictions.jsonl.metadata.json`. The interval excludes scoring and the verified Drive copy at 11:55:44–11:55:56 UTC. The original wrapper started at 11:42:43 UTC. `results/formal-baselines/handoff-status.json` is a historical snapshot, not evidence that the original session remains active. Add the replacement session's actual allocation, inference, training and release timestamps when observed; no purchase or spending ceiling was added.

The manual's roughly ten-hour E2 estimate is unvalidated for the full eight-configuration, three-seed campaign. The fixed Glaive preparation supplies 18,547 training positives, so the 30k configuration is unavailable. Record measured training duration and retained sequence counts before forecasting the remaining campaign.

Recovery allocation requests for L4 and A100 were refused; H100 was rejected for missing quota/entitlement. No new E2 assignment was created. Account-wide balance fell from 189.21 to 187.69 CU across the observed request interval, with 7 existing assignments and an unchanged 18.65 CU/hour rate; the 1.52 CU difference is not attributed to E2. See `results/formal-baselines/recovery-allocation.json`.
