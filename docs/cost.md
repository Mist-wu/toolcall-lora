# E2 cost ledger

The original formal run `E2-formal-baselines-20261104-01` used the coordinator-assigned NVIDIA L4 session `exp-preflight-l4`. That session disappeared from actual assignments; the cause and exact end time are unknown. Local Mac agents resumed E2 on E4's existing shared A100 without creating a new assignment. No paid provider API calls have been made for E2. Exact per-experiment CU attribution is unavailable; concurrent account-wide usage is not an E2-specific measurement.

| Phase | GPU | Start UTC | End UTC | Wall duration | CU attributable | API USD | Result |
|---|---|---|---|---|---|---:|---|
| Formal Qwen2.5 1.5B, 1,240 BFCL cases | NVIDIA L4 | 2026-11-04 11:42:50 | 2026-11-04 11:55:37 | 767 s | Not available | 0 | Complete; 74.76% subset micro-accuracy |
| Original Qwen2.5 7B inference | NVIDIA L4 | No completed inference metadata | Unknown; last snapshot 2026-11-04 12:18:14 | Unknown | Not available | 0 | Interrupted; 698/1,240 predictions recovered |
| Remaining 542 Qwen2.5 7B cases | Shared NVIDIA A100 | 2026-11-04 12:51:57 | 2026-11-04 13:16:17 | 1,460 s | Not separately attributable | 0 | Complete; merged 1,240-case accuracy 86.37% |
| Main LoRA seeds 42,43,44 | Shared NVIDIA A100 | Seed42 initialization 2026-11-04 13:17 | Running | Pending | Not separately attributable | 0 | Full main campaign in progress |

## Completed training/evaluation phases and latest usage (2026-11-04)

| Phase | GPU | Start UTC | End UTC | Wall duration | CU attributable | API USD |
|---|---|---|---|---:|---|---:|
| Seed43 BFCL inference, 1,240 cases | A100-SXM4-40GB | 17:57:02 | 18:12:07 | 905 s | Not separately attributable | 0 |
| Seed43 full two-epoch training | A100-SXM4-40GB | 16:22:06 | 17:56:39 | 5,673 s | Not separately attributable | 0 |
| Seed42 resumed training from step 300 | A100-SXM4-40GB | 14:30:53 | 15:43:24 | 4,351 s | Not separately attributable | 0 |
| Seed42 BFCL inference, 1,240 cases | A100-SXM4-40GB | 15:43:49 | 16:02:08 | 1,099 s | Not separately attributable | 0 |
| Seed42 Glaive held-out inference, 2,000 cases | A100-SXM4-40GB | 16:02:24 | 16:21:58 | 1,174 s | Not separately attributable | 0 |

Sources: `results/main-seed42.train.json` and `results/formal-main-seed42/{bfcl,heldout}.predictions.jsonl.metadata.json`. Wall durations are timestamp differences, not GPU kernel time. Trainer reports 4,302.3152 seconds for the resumed segment only; neither duration includes the earlier interrupted step0–300 training. The run retained all 20,608 training examples including negatives, with zero overlength drops. No full uninterrupted seed42 training duration or throughput is claimed. Metadata retains the shared-runtime warning.

Seed43 sources: `results/main-seed43.{train,request}.json` and `results/main-seed43.env.txt`. Its Trainer runtime is 5,625.1212 s, distinct from the 5,673 s timestamp interval including initialization/export overhead; 20,608 training examples were retained with zero overlength drops. Adapter copy completed at 17:56:58 UTC; `results/main-seed43.adapter-receipt.json` records the actual destination. These times are not an isolated throughput benchmark.

Latest observed account-wide snapshot at **17:57 UTC**: **102.51 CU** balance, **17.34 CU/hour**, **four assignments**. The 17:35:23 UTC snapshot was 108.35 CU. Earlier snapshots: 16:38 UTC 122.77 CU; 17:00 UTC 116.99 CU; 17:21:56 UTC 111.23 CU. These are concurrent account readings, not E2-only charges; no monetary CU conversion is inferred. Main seed43 training and BFCL inference are complete; BFCL timestamps come from `results/formal-main-seed43/bfcl.predictions.jsonl.metadata.json`. Held-out inference is underway; seed44 and exploratory variants are still outstanding. No purchase/recharge was made.

The 1.5B timestamps come from `results/formal-baselines/baseline-1.5b/predictions.jsonl.metadata.json`. The interval excludes scoring and the verified Drive copy at 11:55:44–11:55:56 UTC. The original wrapper started at 11:42:43 UTC. `results/formal-baselines/run-status-at-handoff.json` is historical; current recovery receipts are `recovery-request.json` and `recovery-status.json`. Add the replacement session's actual allocation, inference, training and release timestamps when observed; no purchase or spending ceiling was added.

The manual's roughly ten-hour E2 estimate is unvalidated for the expanded confirmation campaign. The fixed Glaive preparation supplies 18,547 training positives, so the 30k configuration is unavailable. Record measured training duration and retained sequence counts before forecasting the remaining campaign.

Recovery allocation requests for L4 and A100 were refused; H100 was rejected for missing quota/entitlement. No new E2 assignment was created. Account-wide balance fell from 189.21 to 187.69 CU across the observed request interval, with 7 existing assignments and an unchanged 18.65 CU/hour rate; the 1.52 CU difference is not attributed to E2. See `results/formal-baselines/recovery-allocation.json`.

Post-baseline account snapshot: 178.22 CU remaining, 18.49 CU/hour, 5 assignments at 2026-11-04T13:21:01.961798+00:00. Raw account snapshots are in `results/formal-baselines/usage-snapshots.jsonl`; these are not E2-only CU charges.

The corrected initial scope is main×3 plus six 10k ablations×1, not all six ablations×3. At the current shared throughput, main alone is roughly 4.5 training hours plus generation evaluation; the six exploratory variants add roughly 4.4 training hours plus evaluation. These are operational estimates, not measured completed-run costs. Development-selected confirmatory repeats are additional work only if those contrasts become main conclusions.
