# E2 formal experiment report — incomplete campaign

**Status (2026-11-04 23:22 UTC):** both baselines and all three main seeds are complete and collected. One of six exploratory ablations is fully collected; the second has completed training and is being evaluated in the original Colab pipeline. Four variants and final ablation comparisons remain unfinished. This is not an E2 completion claim.

## Question and main result

Can LoRA make Qwen2.5-1.5B-Instruct catch Qwen2.5-7B-Instruct at tool calling? **Not with the measured main configuration.** Across training seeds42/43/44, BFCL subset accuracy is **56.75% mean, 2.74 percentage-point sample SD**, versus **74.76%** for the unadapted 1.5B and **86.37%** for 7B. Retain this negative result; no completed experiment was rerun to remove the regression.

| BFCL category | Cases/seed | Base1.5B | Base7B | Main42 | Main43 | Main44 | Main mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| simple_python | 400 | 84.00% | 95.50% | 84.00% | 85.00% | 85.00% | 84.67% |
| multiple | 200 | 83.00% | 95.50% | 57.50% | 56.00% | 71.50% | 61.67% |
| parallel | 200 | 65.50% | 90.00% | 0.00% | 0.00% | 0.50% | 0.17% |
| parallel_multiple | 200 | 62.50% | 86.50% | 21.00% | 1.50% | 17.00% | 13.17% |
| irrelevance | 240 | 70.42% | 60.42% | 90.42% | 88.33% | 90.00% | 89.58% |
| Micro-average | 1,240 | 74.76% | 86.37% | 57.26% | 53.79% | 59.19% | 56.75% |

This is **five single-turn categories**, not a published full-leaderboard aggregate. Our frozen baselines and adapters use the same data, prompt/parser and checker. Published BFCL versions/category coverage differ; no matched published score or xLAM-paper target is substituted for a measured result. The actual published-table reconciliation is in [../docs/baselines.md](../docs/baselines.md) and [source-comparison/receipt.json](source-comparison/receipt.json): the retrieved current109-row table has no Qwen2.5 row. Matching targets are unavailable in that snapshot, not invented; this is not a claim about every historical table/paper. The published page names package2025.12.17 versus local2026.3.23, and its unweighted broader aggregate is not our five-category micro-average.

## Uncertainty

The main seed-t 95% CI is **49.95–63.55%**, using df2 and a weak normal-seed assumption. Mean changes versus the fixed baselines are:

| Reference | Mean delta (pp) | Seed-t 95% CI (pp) | Paired case-bootstrap 95% CI (pp), conditional on three fitted models |
|---|---:|---|---|
| Base1.5B | −18.01 | [−24.81, −11.21] | [−21.02, −15.16] |
| Base7B | −29.62 | [−36.42, −22.82] | [−32.61, −26.51] |

These are different uncertainties, not a joint seed/data interval. Case resampling averages the three model outcomes within each shared case; it does not treat 3,720 seed-case outcomes as independent cases. Bootstrap uses1,000 resamples and RNG seed42. Full precision, source hashes and per-category statistics: [formal-main-summary/bfcl.summary.json](formal-main-summary/bfcl.summary.json).

## Separate held-out result

Glaive test JSON exact match is **1,890/2,000 (94.50%)**, **1,893/2,000 (94.65%)**, **1,896/2,000 (94.80%)** for seeds42/43/44. Mean **94.65%**, sample SD **0.15 pp**, seed-t CI **[94.28%,95.02%]**. Separate case-bootstrap CI conditional on the models: **[93.62%,95.65%]**. This metric is order-invariant JSON exact match preserving duplicate calls/types, not BFCL AST accuracy. No baseline held-out delta is claimed. See [formal-main-summary/heldout.summary.md](formal-main-summary/heldout.summary.md).

**Agent review found semantic near-duplicates across Glaive splits.** High held-out accuracy does not establish independent or uncontaminated generalization and does not negate the BFCL regression.

## Design actually executed

- Authorized **Glaive fallback**, not xLAM reproduction: xLAM access was gated. Glaive revision `e7f4b6456019f5d8bcb991ef0dd67d8ff23221ac`, Apache-2.0; first complete user/function-call pair only. Normalized-query groups do not cross splits, but semantic near-duplicates can. Prepared train/dev/test sizes:18,547/2,003/2,000, data_seed42.
- Main uses18,547 positives and20,608 total examples including10% negatives; all retained, zero overlength drops. The requested60k is unavailable from this converted fallback; **30k ablation is unavailable**, not fabricated by duplication.
- Qwen2.5-1.5B-Instruct revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`; rank16/alpha32/dropout0.05, all linear layers, LR2e-4, cosine,3% warmup, two-epoch request, max length2048, effective batch32, bf16, assistant-only loss. Seeds42/43/44 share data_seed42. Actual GPU:A100-SXM4-40GB; historical `device_profile=l4` is a precision/batch profile, not GPU provenance.
- Native Qwen `<tool_call>` JSON and `apply_chat_template(..., tools=tools)`; shared formatter:[../src/toolcall_lora/tool_format.py](../src/toolcall_lora/tool_format.py). Official BFCL checker package2026.3.23 plus strict custom Qwen parser. Held-out metric is separate and stricter. Transformers inference, max512 new tokens, greedy generation; no vLLM result claimed.
- Runtime source commit `04506d9943f5d9835d97a5edc25d5f76ae60ab60`; isolated Python3.12/torch2.6.0+cu124/Transformers4.51.3/PEFT0.15.2/Accelerate1.6.0/datasets3.5.0. Actual per-run configuration/environment records are retained.

## Exploratory ablations: measured coverage only

| Configuration, seed42 | Training | BFCL | Glaive held-out |
|---|---|---:|---:|
| 10k, rank8/alpha16, no negatives | Complete | 815/1,240 =65.73% | 1,889/2,000 =94.45% |
| 10k, rank8/alpha16,10% negatives | Complete | 1,009/1,240 =81.37% | Running; not scored |
| 10k, rank16/alpha32, no negatives | Pending | — | — |
| 10k, rank16/alpha32,10% negatives | Pending | — | — |
| 10k, rank64/alpha128, no negatives | Pending | — | — |
| 10k, rank64/alpha128,10% negatives | Pending | — | — |
| 30k, rank16,10% negatives | Unavailable:18,547 unique train positives | — | — |

The completed rank8/no-negative run has parallel74.5%, parallel_multiple69%, but **irrelevance0/240**. Its empirical bootstrap irrelevance interval[0,0] is degenerate, not proof of zero population accuracy. Overall CI63.15–68.23%. Rank and data size also differ from main; this is not an isolated causal comparison of negatives. The matched rank8/10%-negative run reaches81.37% (case-bootstrap CI79.35–83.55%): simple86.75%, multiple85.5%, parallel69.5%, parallel_multiple71.5%, irrelevance209/240=87.08%. Versus no negatives, overall delta is+15.65pp, paired-case CI[+13.23,+18.23],235 improved/41 regressed. Irrelevance gains dominate; multiple and parallel decrease3.5pp and5pp. Versus frozen1.5B:+6.61pp[+4.44,+8.87]; versus7B:−5.00pp[−7.42,−2.50], so it does not catch7B. These exploratory single-seed results do not reverse the negative main three-seed result or establish a best configuration. Adding negatives also increases examples10,000→11,111 and steps624→694; this is a two-epoch training-policy contrast, not a fixed-budget causal effect. Saved analysis/configuration/source hashes:[formal-ablation-comparisons/rank8.bfcl.md](formal-ablation-comparisons/rank8.bfcl.md). Held-out is not inferred from BFCL. All six variants remain **single-seed exploratory**; no confirmation is selected using test scores, and no test-driven best-run claim is made. Actual plan:[formal-ablation-plan.json](formal-ablation-plan.json).

## Seven-category error evidence

[formal-error-analysis/report.md](formal-error-analysis/report.md) reports wrong function, missing argument, type, value, extra call, missed call and false call using explicit evidence rules. Cases with fewer parsed calls than the reference:34/12 for base1.5B/7B, versus419/472/402 for main42/43/44. Main's irrelevance gains coexist with severe call omission; the cause is not established before matched ablations finish.

Argument diagnostics are lower bounds because the official checker can stop at its first diagnostic. Ambiguous parallel no-match and parser failures remain unresolved, not guessed into semantic categories. For rank8/no-negative, irrelevance failures are235 parsed false calls plus5 parser errors; for rank8/10%-negative,30 parsed false calls plus1 parser error. Across BFCL categories, missed calls increase31→43; unresolved cases79→71. This measured pair does not show main-like catastrophic parallel omission. It does not isolate whether rank/data amount or their interaction drives the main regression; later pairs remain pending. Full per-case evidence, reference file and hashes are retained. These are deterministic diagnostics, not human-gold root-cause labels.

## Review and limitations

Accepted review method:**agent**, not human. `human_validation_complete=false`, `human_validation_required=false`; no new human annotation or delayed retests requested. The50-example negative audit supports47 labels, finds one clear mislabel and two uncertain cases; see [negative-audit/agent-review/](negative-audit/agent-review/). Findings are limitations, not human-gold metrics. No training labels or completed scores were silently changed. Name-disjoint donated tools do not guarantee semantic irrelevance. Public BFCL pretraining contamination remains possible.

## Artifacts, reproduction, cost and E3

- Baselines:[formal-baselines/](formal-baselines/). Main full raw predictions, metadata, scores/details and paired analyses:[formal-main-seed42/](formal-main-seed42/), [formal-main-seed43/](formal-main-seed43/), [formal-main-seed44/](formal-main-seed44/). Ablations:[formal-ablations/](formal-ablations/). Files named `partial` are unscored history, never final results.
- Saved-outcome reproduction (small CPU only): `python3 scripts/summarize_main_bfcl.py`; `python3 scripts/summarize_main_heldout.py`; `python3 scripts/analyze_bfcl_errors.py`; `python3 scripts/compare_main_seed42.py --seed 44`; `python3 scripts/compare_ablation_bfcl.py --rank 8`.
- For a clean Colab reproduction, follow [../README.md](../README.md), restore pinned prepared data from `gdrive:exp/runs/E2/E2-glaive-data-20261104`, and use the formal main/ablation scripts. **Do not resubmit the active pipeline or rerun completed work.** Existing execution/session, collection commands and actual client are in [../HANDOFF.md](../HANDOFF.md). All model work stays in Colab; Drive uses configured rclone/header, not interactive mounting.
- Actual timings, runtime interruptions and attribution limits:[../docs/cost.md](../docs/cost.md). Seed42 resumed from step300; no uninterrupted full-training duration is claimed. Account CU readings are shared, not E2 invoices. No paid provider evaluation call, automatic purchase or recharge is claimed. Unknown runtime-loss causes are not explained by kernel busy state alone.
- E3's actual seed42 adapter destination is `gdrive:exp/runs/E2/E2-main-resume-20261104-03-main-seed42-adapter`; receipt:[main-seed42.adapter-receipt.json](main-seed42.adapter-receipt.json). E3's handoff was updated; no E3 result is inferred here.

**Remaining:** four untrained ablation configurations, second/current held-out and later evaluations, remaining matched descriptive comparisons with uncertainty, final report update. Published-source comparability has been documented with frozen page/CSV hashes and unavailable matching targets. Existing jobs/client remain intact; report `waiting_remote`, not complete.
