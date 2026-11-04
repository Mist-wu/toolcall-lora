# E2 current handoff

## Update 2026-11-04 22:37 UTC: rank8 neg10 checkpoint 200

Existing **n10000-r8-neg10 seed42** foreground training reached step245/694 at22:36:27UTC. Step200 copied successfully to `gdrive:exp/runs/E2/E2-n10000-r8-neg10-s42-step200-6208804f5039`, rclone exit0, ended22:32:57UTC. Actual receipt `results/formal-ablations/n10000-r8-neg10-seed42/checkpoint-200.receipt.json`. Fixed256-example training-time dev loss at epoch0.58 was0.000919598, not a test score. Actual subscriber `exp-iopub-e24-scope.service` remains active; original pipeline/client preserved without resubmission. First exploratory configuration is fully collected; this and four later variants, comparisons and final report remain incomplete. Continue existing output/ablation-status/checkpoint polling with commands below; collect completed outputs as ready and reuse all completed results.

## Update 2026-11-04 22:30 UTC: rank8 neg10 checkpoint 100

Existing **n10000-r8-neg10 seed42** foreground training reached step158/694 at22:29:37UTC. Step100 copied successfully to `gdrive:exp/runs/E2/E2-n10000-r8-neg10-s42-step100-d9b39afc1d21`, rclone exit0, ended22:25:31UTC. Actual receipt `results/formal-ablations/n10000-r8-neg10-seed42/checkpoint-100.receipt.json`. Fixed256-example training-time dev loss at epoch0.29 was0.002578957, not a test score. Actual subscriber `exp-iopub-e24-scope.service` remains active; command/client preserved without resubmission. First exploratory variant is fully collected; this variant and four later variants still require actual completion/evaluation, with comparisons and final report pending. Continue existing output/ablation-status/checkpoint polling using commands below; collect completed outputs as ready and reuse all completed main/first-ablation results.

## Update 2026-11-04 22:24 UTC: first exploratory ablation fully collected; rank8 neg10 training

Collected all four actual held-out artifacts in `results/formal-ablations/n10000-r8-neg0-seed42/heldout.*`: **1889/2000 = 94.45%**, bootstrap 95% CI **93.40–95.55%**. All2,000 scored details are present; prediction SHA256 matches score provenance. Inference21:57:53–22:17:41UTC (1,188s), documented in `docs/cost.md`. This remains separate JSON exact match with Glaive semantic-near-duplicate independence limitations, not BFCL or xLAM. Historical held-out snapshot remains unscored and superseded. **1/6 exploratory configurations is fully collected**, including training/config/environment/adapter, BFCL and held-out evidence.

Actual ablation status records completed=[n10000-r8-neg0], current=**n10000-r8-neg10 seed42**, running. Existing foreground training reached step71/694 at22:23UTC. Collected actual next configuration `results/formal-ablations/n10000-r8-neg10-seed42/request.json`. Real subscriber `exp-iopub-e24-scope.service` remains active; preserve command/client without resubmission. Five variants still require their actual training/evaluations, and paired ablation comparisons/final report remain incomplete. Do not select confirmation runs using test scores; retain single-seed exploratory scope.

Commands used / next checkpoint observation:

```sh
for f in predictions.jsonl predictions.jsonl.metadata.json score.json score.details.jsonl; do colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg0-seed42-heldout.$f results/formal-ablations/n10000-r8-neg0-seed42/heldout.$f; done
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg10-seed42/request.json results/formal-ablations/n10000-r8-neg10-seed42/request.json
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg10-seed42/last-verified-checkpoint.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/ablation-checkpoint-observed.json
```

Continue existing output/ablation-status polling using commands below; collect new actual checkpoints and completed outputs without resubmission.

## Update 2026-11-04 22:17 UTC: first ablation held-out inference 1904/2000

Original **n10000-r8-neg0 seed42** held-out inference advanced to **1904/2000** at22:16:49UTC. Collected actual incomplete snapshot `results/formal-ablations/n10000-r8-neg0-seed42/heldout.predictions.partial-1904.jsonl`, explicitly unscored and not a complete held-out result. Actual output subscriber `exp-iopub-e24-scope.service` remains active; original pipeline/client preserved without resubmission or replacement. Shared account at22:17UTC: **31.13 CU**, **15.40 CU/hour**, three assignments, not E2-only cost; no purchase/recharge. Next collect all four complete held-out files and follow next n10000-r8-neg10 training using existing output/status/download commands below. Remaining five trainings, evaluations/comparisons and final report remain pending; reuse completed main and first-ablation BFCL/error results. Do not score partial predictions.

## Update 2026-11-04 22:11 UTC: first ablation seven-category BFCL evidence collected

Extended `scripts/analyze_bfcl_errors.py` to include the actually collected completed ablation BFCL scores; reran only the small saved-outcome analysis, not inference/checker. `results/formal-error-analysis/{report.md,summary.json,cases.jsonl}` now covers baselines, main seeds and **1/6 exploratory ablations**. For n10000-r8-neg0 seed42, 425 failed cases: wrong_function9, missing_argument19, wrong_type5, wrong_value43, extra_call4, missed_call31, false_call235, unresolved79 (8 parser failures +71 ambiguous parallel no-match). Irrelevance0/240 comprises **235 parsed false calls and5 parser failures**, not240 confirmed parsed calls. Reference hash matches score provenance. Rules/uncertainty/agent-only review boundaries unchanged; no isolated causal conclusion about negatives before matched results.

Existing held-out inference for this adapter reached **1188/2000** at22:09:29UTC; incomplete snapshot remains unscored in `/srv/exp-runner/state/remote/E2-main-resume-20261104-03/n10000-r8-neg0-seed42-heldout.partial.jsonl`. Real output subscriber `exp-iopub-e24-scope.service` remains active and original pipeline/client preserved without resubmission. Next collect all four completed held-out files, then follow n10000-r8-neg10 in the same pipeline. Remaining five trainings, ablation evaluations/comparisons and final report remain incomplete. Poll with existing output/status/download commands below.

Reproduce updated error evidence: `python3 scripts/analyze_bfcl_errors.py`.

## Update 2026-11-04 22:04 UTC: first ablation BFCL complete

Collected all four actual BFCL artifacts in `results/formal-ablations/n10000-r8-neg0-seed42/bfcl.*`: **815/1240 = 65.7258%**, bootstrap 95% CI **63.1452–68.2258%**. Categories: simple_python350/400 (87.5%), multiple178/200 (89%), parallel149/200 (74.5%), parallel_multiple138/200 (69%), irrelevance**0/240**. Prediction SHA256 matches score provenance; all1,240 detail records are collected. Historical partial snapshots remain explicitly unscored and are superseded. The empirical bootstrap irrelevance interval [0,0] is degenerate because every observed case failed, not proof of zero population accuracy.

This is a single-seed exploratory trade-off: better parallel behavior but failure on every irrelevance case. It still underperforms both baselines overall. Do not attribute differences against main solely to negatives: rank/data size also differ; matched rank8 neg10 results are pending. BFCL inference21:30:23–21:57:41UTC (1,638s), recorded in `docs/cost.md` with attribution limits.

Original pipeline now runs this adapter's held-out evaluation; actual subscriber `exp-iopub-e24-scope.service` remains active. Preserve command/client without resubmission. Remaining five trainings, held-out/evaluation outputs, ablation comparisons/error evidence and final report remain incomplete. Next collect `/content/e2-artifacts/n10000-r8-neg0-seed42-heldout.*` when complete and follow n10000-r8-neg10 without resubmission. Main results remain complete and must be reused.

Collection used:

```sh
for f in predictions.jsonl predictions.jsonl.metadata.json score.json score.details.jsonl; do colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg0-seed42-bfcl.$f results/formal-ablations/n10000-r8-neg0-seed42/bfcl.$f; done
```

## Update 2026-11-04 21:57 UTC: first ablation BFCL inference 1172/1240

Original pipeline advanced to **1172/1240** BFCL predictions for **n10000-r8-neg0 seed42** at 21:56:36 UTC. Collected actual incomplete snapshot `results/formal-ablations/n10000-r8-neg0-seed42/bfcl.predictions.partial-1172.jsonl`, explicitly unscored; supersedes earlier observations, not a final result. Actual output subscriber `exp-iopub-e24-scope.service` remains active; command/client preserved without resubmission or replacement. Account-wide at21:56UTC: **36.29 CU**, **15.40 CU/hour**, three assignments, not E2-only cost; no purchase/recharge. First ablation training complete; remaining five trainings, complete ablation evaluations/comparisons and final report remain pending. Continue polling existing output/status and collect all four BFCL/held-out files when complete using commands below. Do not score partial predictions or rerun completed main results.

## Update 2026-11-04 21:49 UTC: first ablation BFCL inference 884/1240

Original pipeline advanced to **884/1240** BFCL predictions for **n10000-r8-neg0 seed42** at 21:48:41 UTC. Collected actual incomplete snapshot `results/formal-ablations/n10000-r8-neg0-seed42/bfcl.predictions.partial-884.jsonl`, explicitly unscored; supersedes the 696-case observation, not a final result. Actual output subscriber `exp-iopub-e24-scope.service` remains active; original command/client preserved without resubmission or replacement. First ablation training complete, remaining five trainings and complete ablation evaluations/comparisons/final report still pending. Continue polling existing output/status and collect all four BFCL/held-out files when complete using the commands below. Do not score partial predictions or rerun completed main results.

## Update 2026-11-04 21:42 UTC: first ablation BFCL inference 696/1240

Original pipeline is evaluating **n10000-r8-neg0 seed42**, now **696/1240** BFCL predictions at 21:41:47 UTC. Collected actual incomplete snapshot `results/formal-ablations/n10000-r8-neg0-seed42/bfcl.predictions.partial-696.jsonl`, explicitly unscored and not a final BFCL result. Actual output subscriber `exp-iopub-e24-scope.service` remains active; command/client preserved without resubmission or replacement. First ablation training is complete; remaining five trainings, all complete ablation evaluations/comparisons and final report remain pending. Continue polling existing output/status and collect the full four-file BFCL/held-out outputs when complete, as described below. Do not score partial snapshots or rerun completed main results.

Observation command:

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg0-seed42-bfcl.predictions.jsonl /srv/exp-runner/state/remote/E2-main-resume-20261104-03/n10000-r8-neg0-seed42-bfcl.partial.jsonl
```

## Update 2026-11-04 21:33 UTC: first exploratory ablation training complete

Collected `results/formal-ablations/n10000-r8-neg0-seed42/{train.json,request.json,env.txt,adapter-receipt.json,checkpoint-624.receipt.json}`. The two-epoch request finished **624 steps at 21:30:00 UTC**, retaining all 10,000 examples, zero overlength drops; Trainer reports epoch1.9952, not exactly2.0. Runtime2,705.1175 s versus wall interval2,730 s (20:44:30–21:30:00), documented in `docs/cost.md`; shared timing is not an isolated throughput benchmark. Adapter copied successfully at **21:30:18 UTC** to `gdrive:exp/runs/E2/E2-main-resume-20261104-03-n10000-r8-neg0-seed42-adapter`. Latest dev loss0.000515169 is from step600/256 examples, not a final test score.

Original pipeline is evaluating this adapter; no completed ablation BFCL/held-out score yet. Actual subscriber `exp-iopub-e24-scope.service` remains active; preserve command/client without resubmission. First ablation training complete, remaining five trainings plus all ablation evaluations/comparisons and final report incomplete. Account-wide at21:32UTC: **43.45 CU**, **17.34 CU/hour**, four assignments, not E2-only charges; no purchase/recharge. Reuse all completed main experiments and analyses.

Collected with:

```sh
for f in train.json request.json env.txt; do colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg0-seed42/$f results/formal-ablations/n10000-r8-neg0-seed42/$f; done
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/workspace/results/n10000-r8-neg0-seed42.adapter-receipt.json results/formal-ablations/n10000-r8-neg0-seed42/adapter-receipt.json
```

Next poll existing output/status and collect `/content/e2-artifacts/n10000-r8-neg0-seed42-bfcl.*` and `n10000-r8-neg0-seed42-heldout.*` (predictions, metadata, score, score details) when complete into this ablation result directory. Continue later variants without resubmission; all six remain single-seed exploratory.

## Update 2026-11-04 21:24 UTC: first ablation checkpoint 500

Existing **n10000-r8-neg0 seed42** foreground training reached step533/624 at 21:23:13 UTC. Step500 copied successfully to `gdrive:exp/runs/E2/E2-n10000-r8-neg0-s42-step500-81a3c8f620fe`, rclone exit0, ended 21:20:55 UTC. Actual receipt `results/formal-ablations/n10000-r8-neg0-seed42/checkpoint-500.receipt.json`. Fixed256-example training-time dev loss at epoch1.60 was 0.000534404, not a test score. Actual output subscriber `exp-iopub-e24-scope.service` remains active; original command/client preserved without resubmission. None of the six exploratory ablations has completed yet. Continue polling output/status/checkpoint using commands below; collect completed train/config/environment/adapter receipt and full BFCL/held-out outputs when ready. Reuse completed main results and analyses.

## Update 2026-11-04 21:18 UTC: first ablation checkpoint 400

Existing **n10000-r8-neg0 seed42** foreground training reached step450/624 at 21:17:07 UTC. Step400 copied successfully to `gdrive:exp/runs/E2/E2-n10000-r8-neg0-s42-step400-91460577884e`, rclone exit0, ended 21:13:44 UTC. Actual receipt `results/formal-ablations/n10000-r8-neg0-seed42/checkpoint-400.receipt.json`. Fixed256-example training-time dev loss at epoch1.28 was 0.000761621, not a test score. Actual output subscriber `exp-iopub-e24-scope.service` remains active; original command/client preserved without resubmission. None of the six exploratory ablations has completed yet. Continue polling output/status/checkpoint using commands below; collect completed train/config/environment/adapter receipt and full BFCL/held-out outputs when ready. Reuse completed main results and analyses.

## Update 2026-11-04 21:11 UTC: first ablation checkpoint 300 and configuration

Existing **n10000-r8-neg0 seed42** foreground training reached step354/624 at 21:10:46 UTC. Step300 copied successfully to `gdrive:exp/runs/E2/E2-n10000-r8-neg0-s42-step300-04d5beeb017b`, rclone exit0, ended 21:06:33 UTC. Collected `results/formal-ablations/n10000-r8-neg0-seed42/{checkpoint-300.receipt.json,request.json}`. Actual configuration: 10,000 selected positives, rank8/alpha16, no negatives, two epochs, max2048, training seed42/data_seed42. Fixed256-example training-time dev loss at epoch0.96 was 0.001054402, not a test score. Actual output subscriber `exp-iopub-e24-scope.service` remains active; command/client preserved without resubmission. No ablation completed yet; all six remain single-seed exploratory. Continue polling existing output/status/checkpoint with commands below, then collect completed train/config/environment/adapter receipt and full BFCL/held-out outputs. Main experiments, aggregate statistics and main/baseline error evidence are complete and must not be rerun.

Configuration collection used:

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg0-seed42/request.json results/formal-ablations/n10000-r8-neg0-seed42/request.json
```

## Update 2026-11-04 21:04 UTC: main/baseline seven-category error evidence complete

Added `scripts/analyze_bfcl_errors.py` and actual `results/formal-error-analysis/{report.md,summary.json,cases.jsonl,bfcl.evaluation.jsonl}`. Small CPU analysis uses saved official diagnostic labels plus actual parsed call counts/name multisets, without rerunning inference/checker or inventing human/agent semantic labels. Downloaded the original 1,240-case prepared BFCL reference (2.7 MiB); its SHA256 matches every model's score provenance. Seven requested categories are reported with explicit rules; ambiguous no-match and parser failures remain unresolved, not forced into the table. Argument diagnostics are lower bounds, not exhaustive latent errors.

Call-deficit cases: **34** (1.5B), **12** (7B), **419/472/402** (main42/43/44). False-call cases: **69/95/22/27/23**; unresolved including parse: **100/31/19/5/13**. These are per-failed-case observations, not causal attribution to negative training. `README.md` links the report and reproduction: `python3 scripts/analyze_bfcl_errors.py`. Original scores and training data unchanged. Agent review is accepted, never human gold; no new human work required.

Existing first ablation **n10000-r8-neg0 seed42** reached step234/624 at 21:01:42 UTC; step200 copied successfully to `gdrive:exp/runs/E2/E2-n10000-r8-neg0-s42-step200-798ab3cf9eda`, rclone exit0 at 20:59:20 UTC. Receipt `results/formal-ablations/n10000-r8-neg0-seed42/checkpoint-200.receipt.json`. Real subscriber `exp-iopub-e24-scope.service` is active; original command/client preserved without resubmission. Shared account at 21:04 UTC: **50.52 CU**, **17.34 CU/hour**, four assignments, not E2-only cost; no purchase/recharge. Six exploratory ablations, their comparison/error evidence and final report remain incomplete. Next poll existing output/ablation-status/checkpoint with commands below, collect actual ablation training/evaluation artifacts as they finish, and incorporate them into final analysis.

Reference collection used:

```sh
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/workspace/data/bfcl/evaluation.jsonl /srv/exp-runner/state/remote/E2-main-resume-20261104-03/bfcl-evaluation.jsonl
```

## Update 2026-11-04 20:56 UTC: main held-out aggregate complete

Added small-CPU reproduction `scripts/summarize_main_heldout.py` and `results/formal-main-summary/heldout.summary.{json,md}` from all three saved main held-out scores/outcomes. Mean **94.65%**, sample SD **0.15 pp**, seed-t 95% CI **[94.2774%, 95.0226%]** (df2, weak normal-seed assumption). Separate case-bootstrap CI conditional on these models: **[93.6167%, 95.65%]**, resampling 2,000 shared case IDs, not 6,000 independent seed-case outcomes. Original scores and data unchanged; no baseline held-out delta claimed. Source hashes and semantic-near-duplicate/agent-review limitations retained. `README.md` now covers all completed main evaluations and links both aggregate analyses.

Existing foreground ablation **n10000-r8-neg0 seed42** reached step130/624 at 20:54 UTC, completed list still empty. Step100 copied successfully at 20:52:07 UTC to `gdrive:exp/runs/E2/E2-n10000-r8-neg0-s42-step100-67cc49e251be` (rclone exit0); actual receipt `results/formal-ablations/n10000-r8-neg0-seed42/checkpoint-100.receipt.json`. Real output subscriber `exp-iopub-e24-scope.service` remains active; command/client preserved without resubmission. All six exploratory ablations and final seven-category error analysis/report remain incomplete.

Reproduce held-out analysis: `python3 scripts/summarize_main_heldout.py`. Next finish seven-category error analysis on saved main/baseline outcomes while polling the existing ablation pipeline using commands below. Latest ablation checkpoint observation:

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/n10000-r8-neg0-seed42/last-verified-checkpoint.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/ablation-checkpoint-observed.json
```

## Update 2026-11-04 20:49 UTC: seed44 held-out complete; exploratory ablations running

Collected all four seed44 Glaive held-out artifacts in `results/formal-main-seed44/heldout.*`: **1896/2000 = 94.80%**, bootstrap 95% CI **93.75–95.75%**. All 2,000 detail records are present and prediction SHA256 matches score provenance. Inference ran 20:24:21–20:44:19 UTC (1,198 s), recorded in `docs/cost.md`. This separate JSON exact-match result is not BFCL/xLAM or evidence of uncontaminated generalization; agent-observed Glaive semantic near-duplicates limit independence. All main training and both evaluations per seed are now collected.

Ran `python3 scripts/compare_main_seed42.py --seed 44` on saved outcomes; collected `results/formal-main-seed44/comparison.{json,md}`. Seed44 overall paired changes: **−15.56 pp** versus 1.5B, 95% CI **[−18.71, −12.82]**, 99 improved/292 regressed; **−27.18 pp** versus 7B, **[−30.32, −24.19]**, 82 improved/419 regressed. No model reruns, metrics or training data changed.

Original foreground pipeline now runs exploratory **n10000-r8-neg0 seed42**, observed step22/624 at 20:46 UTC. Actual status says running, completed list empty. Collected real `results/formal-ablation-plan.json` from remote workspace; all six variants remain single-seed exploratory. One status download timed out; retry succeeded without any runtime recovery/resubmission. Real output subscriber `exp-iopub-e24-scope.service` remains active. Preserve both command and client. Next summarize the three held-out scores, finish seven-category error analysis, and collect ablation checkpoints/train/evaluation outputs as they finish. 30k remains unavailable; do not fabricate samples or select confirmations using test scores.

Commands used / next observation:

```sh
for f in predictions.jsonl predictions.jsonl.metadata.json score.json score.details.jsonl; do colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed44-heldout.$f results/formal-main-seed44/heldout.$f; done
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/workspace/results/ablation-status.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/ablation-status-observed.json
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/output.log /srv/exp-runner/state/remote/E2-main-resume-20261104-03/output-observed.log
```

## Update 2026-11-04 20:41 UTC: README reflects three-seed BFCL conclusion

Updated `README.md` with seed44 BFCL category results and the completed three-seed main summary (56.75% mean, 2.74 pp sample SD), negative transfer against both baselines, and separate seed-t/case-bootstrap uncertainty. Linked actual aggregate artifacts and reproduction command; explicitly kept E2 incomplete. No training/evaluation reruns or metric changes.

Existing seed44 held-out inference advanced to **1568/2000** at 20:39:55 UTC. Actual incomplete snapshot is `/srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed44-heldout.partial.jsonl`, unscored. Downloaded existing output/status; actual subscriber `exp-iopub-e24-scope.service` remains active. Preserve running pipeline/client without resubmission. Next collect all four completed held-out files, run the individual seed44 comparison and summarize held-out seeds. Continue existing six exploratory ablations and finish seven-category error analysis; no human annotation/retests are required. Poll with existing download commands below.

## Update 2026-11-04 20:34 UTC: main three-seed BFCL statistics complete

Added reproducible small-CPU analysis `scripts/summarize_main_bfcl.py` and actual aggregate results `results/formal-main-summary/bfcl.summary.{json,md}` using the three completed BFCL score/detail sets. Main mean **56.7473%**, sample SD **2.7376 pp**, seed-t 95% CI **49.9468–63.5478%** (df2, weak normal-seed assumption). Mean change versus 1.5B **−18.0108 pp**, seed-t CI **[−24.8113, −11.2102]**; versus 7B **−29.6237 pp**, seed-t CI **[−36.4242, −22.8231]**. Separately reported paired case-bootstrap CIs conditional on the three fitted models: **[−21.0215, −15.1613]** and **[−32.6075, −26.5054]** pp. These are different uncertainties, not 3,720 independent cases or a joint seed/data CI. Category results and input hashes retained. All seeds underperform both baselines overall; main does not catch 7B. Glaive/agent-review limitations remain explicit.

Reproduce: `python3 scripts/summarize_main_bfcl.py` (no training/inference). Existing seed44 held-out inference reached **832/2000** at 20:32:33 UTC; its incomplete snapshot remains only in `/srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed44-heldout.partial.jsonl`, unscored. Original foreground pipeline and active real subscriber `exp-iopub-e24-scope.service` preserved. Next poll output/status and collect complete seed44 held-out files, then individual seed44 comparison and held-out aggregate. Six exploratory ablations and final seven-category error analysis still remain; E2 is not complete. Use download commands below without resubmission.

## Update 2026-11-04 20:27 UTC: seed44 BFCL complete

Collected all four seed44 BFCL artifacts in `results/formal-main-seed44/bfcl.*`: **734/1240 = 59.1935%**, bootstrap 95% CI **56.5323–61.8548%**. Category scores: simple_python 340/400 (85%), multiple 143/200 (71.5%), parallel 1/200 (0.5%), parallel_multiple 34/200 (17%), irrelevance 216/240 (90%). The prediction SHA256 matches score provenance; all 1,240 scored detail records are collected. Incomplete snapshots remain unscored history and are superseded by the full files.

All three main BFCL scores are now available (42: 57.26%; 43: 53.79%; 44: 59.19%), each below both baselines overall. Final three-seed statistics remain to be written, not inferred from case CIs. Seed44 BFCL inference ran 20:06:40–20:24:09 UTC (1,049 s); documented in `docs/cost.md` with shared-cost limits. Seed44 held-out evaluation is now running in the original foreground pipeline; actual subscriber `exp-iopub-e24-scope.service` remains active. Preserve the command/client without resubmission. Held-out outputs, six exploratory ablations and final analysis remain pending.

Collected with:

```sh
for f in predictions.jsonl predictions.jsonl.metadata.json score.json score.details.jsonl; do colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed44-bfcl.$f results/formal-main-seed44/bfcl.$f; done
```

Next poll existing output/status and `/content/e2-artifacts/main-seed44-heldout.predictions.jsonl`; collect all four held-out files when complete, then run `python3 scripts/compare_main_seed42.py --seed 44` and complete three-seed statistics. The current comparison script reads the completed held-out score for its limitations paragraph, so do not run it for seed44 before that score exists.

## Update 2026-11-04 20:20 UTC: seed44 BFCL inference 908/1240

Existing foreground pipeline advanced to **908/1240** seed44 BFCL predictions. Collected `results/formal-main-seed44/bfcl.predictions.partial-908.jsonl`, explicitly incomplete and unscored; it supersedes the 524-case progress snapshot, not a final score. Actual output subscriber `exp-iopub-e24-scope.service` remains active. Original command/client preserved without resubmission or replacement. Seed44 complete BFCL/held-out evaluations, six exploratory ablations and final three-seed/error analysis remain pending. Continue polling with the download commands below; collect the full four-file BFCL/held-out outputs when complete and do not score partial snapshots.

## Update 2026-11-04 20:14 UTC: seed44 BFCL inference 524/1240

Existing foreground pipeline is evaluating the completed seed44 adapter. Downloaded an incomplete **524/1240** prediction snapshot to `results/formal-main-seed44/bfcl.predictions.partial-524.jsonl`. This is not scored and must not be treated as a complete BFCL result. Actual output subscriber `exp-iopub-e24-scope.service` remains active; no command/client resubmission or replacement. Seed44 complete BFCL/held-out evaluations, six exploratory ablations and final three-seed/error analysis remain pending.

Observed with:

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed44-bfcl.predictions.jsonl /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed44-bfcl.partial.jsonl
```

Next poll existing output/status; collect the full four-file BFCL/held-out outputs as described below when complete. Reuse existing baselines and seeds42/43; do not score partial snapshots or rerun completed inference.

## Update 2026-11-04 20:08 UTC: seed44 training and adapter complete

Collected `results/main-seed44.{train,request}.json`, `results/main-seed44.env.txt`, final checkpoint receipt `results/main-seed44-checkpoint-1288.receipt.json` and adapter receipt `results/main-seed44.adapter-receipt.json`. Two-epoch training completed at **20:06:17 UTC**, retaining all 20,608 examples (18,547 positives), zero overlength drops. Wall interval 5,638 s; Trainer runtime 5,590.9204 s, not an isolated throughput benchmark; recorded in `docs/cost.md`. Final adapter copied successfully to `gdrive:exp/runs/E2/E2-main-resume-20261104-03-main-seed44-adapter` at **20:06:36 UTC**. Its recorded dev loss remains the step1200 measurement, not a final test score.

The original foreground pipeline has entered inference; actual subscriber `exp-iopub-e24-scope.service` remains active. Preserve both without resubmission. Seed44 BFCL/held-out scores, six exploratory ablations and final three-seed/error analysis remain incomplete.

Collection commands used (request matches the previously collected configuration):

```sh
for f in train.json request.json env.txt; do colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed44/$f results/main-seed44.$f; done
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/workspace/results/main-seed44.adapter-receipt.json results/main-seed44.adapter-receipt.json
```

Next poll output/status with the commands below. When complete, collect `/content/e2-artifacts/main-seed44-bfcl.*` and `main-seed44-heldout.*` (predictions JSONL, metadata JSON, score JSON, score details JSONL) into `results/formal-main-seed44/`, then run `python3 scripts/compare_main_seed42.py --seed 44` and complete three-seed analysis. Do not score incomplete prediction snapshots.

## Update 2026-11-04 20:00 UTC: seed44 checkpoint 1200

Existing foreground pipeline reached seed44 step1200/1288 and completed its checkpoint copy at 20:00:10 UTC. Destination `gdrive:exp/runs/E2/E2-main-s44-step1200-6643deecb2aa`, rclone exit 0; receipt `results/main-seed44-checkpoint-1200.receipt.json`. Training-time 256-example dev loss was 0.000627034 at epoch 1.86, not a test score. Actual output subscriber `exp-iopub-e24-scope.service` remains active. Updated `docs/cost.md` with previously collected account readings through 19:53 UTC, explicitly not E2-only charges. Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Next poll output/status using the download commands below; upon training completion collect `/content/e2-artifacts/main-seed44/{train.json,request.json,env.txt}` and `/content/experiment-runs/E2-main-resume-20261104-03/workspace/results/main-seed44.adapter-receipt.json`, then follow BFCL/held-out outputs without resubmission.

## Update 2026-11-04 19:54 UTC: README covers completed seeds42/43; seed44 checkpoint 1100

Updated `README.md` with actual seed43 category scores, overall/paired CIs, separate held-out result, analysis reproduction command and current execution ownership. Both completed seeds underperform both baselines overall; these are not yet a three-seed conclusion. No measurements or training data changed; agent-review/held-out limitations remain explicit.

Existing foreground pipeline reached seed44 step1105/1288 at 19:53:22 UTC. Step1100 copied to `gdrive:exp/runs/E2/E2-main-s44-step1100-2be70e186b76`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-1100.receipt.json`. Actual output subscriber `exp-iopub-e24-scope.service` remains active. Shared account reading: 70.76 CU balance, 17.34 CU/hour across four assignments, not E2-only cost. Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling output/status/checkpoint using the download commands below; collect seed44 train/config/environment and adapter receipt when finished.

## Update 2026-11-04 19:46 UTC: seed43 paired comparison; seed44 checkpoint 1000

Completed the small-CPU paired analysis of existing seed43 BFCL outcomes with `python3 scripts/compare_main_seed42.py --seed 43`; no model reruns. Saved `results/formal-main-seed43/comparison.{json,md}` with source hashes and exact checker labels. Generalized the existing script via `--seed` (default42). Seed43 loses **20.97 pp** versus 1.5B (paired bootstrap 95% CI **[-24.03, -17.98]**, 84 improved/344 regressed cases) and **32.58 pp** versus 7B (**[-35.65, -29.27]**, 76 improved/480 regressed). Irrelevance improves +17.92 pp versus 1.5B, but parallel wrong-count errors rise from 38 to 395 across both parallel categories. Checker labels are diagnostics, not forced seven-way semantic labels. This is a single-seed result, not the required three-seed conclusion; Glaive held-out independence and agent-review limitations remain disclosed.

Existing foreground pipeline reached seed44 step1001/1288 at 19:45:54 UTC. Step1000 copied to `gdrive:exp/runs/E2/E2-main-s44-step1000-7d998c36039b`, rclone exit 0; receipt `results/main-seed44-checkpoint-1000.receipt.json`. Actual output subscriber `exp-iopub-e24-scope.service` is active. Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint using the download commands below.

## Update 2026-11-04 19:39 UTC: seed44 checkpoint 900

Existing foreground pipeline reached seed44 step903/1288 at 19:38:49 UTC. Step900 copied to `gdrive:exp/runs/E2/E2-main-s44-step900-907ce9cdcbbf`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-900.receipt.json`. Training-time 256-example dev loss was 0.000651464 at epoch 1.40, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` remains active. Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint using the download commands below.

## Update 2026-11-04 19:32 UTC: seed44 checkpoint 800

Existing foreground pipeline reached seed44 step801/1288 at 19:31:31 UTC. Step800 copied to `gdrive:exp/runs/E2/E2-main-s44-step800-80dc85bb8e7e`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-800.receipt.json`. Training-time 256-example dev loss was 0.000500524 at epoch 1.24, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` remains active. Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint using the download commands below.

## Update 2026-11-04 19:25 UTC: seed44 checkpoint 700

Existing foreground pipeline reached seed44 step715/1288 at 19:25:29 UTC. Step700 copied to `gdrive:exp/runs/E2/E2-main-s44-step700-2a4e20901eff`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-700.receipt.json`. Training-time 256-example dev loss was 0.000469362 at epoch 1.09, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` is active. Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint using the download commands below.

## Update 2026-11-04 19:18 UTC: seed44 checkpoint 600

Existing foreground pipeline reached seed44 step612/1288 at 19:17:47 UTC. Step600 copied to `gdrive:exp/runs/E2/E2-main-s44-step600-e8de2eb0b363`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-600.receipt.json`. Training-time 256-example dev loss was 0.000504885 at epoch 0.93, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` remains active. Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint using the download commands below.

## Update 2026-11-04 19:12 UTC: seed44 checkpoint 500

Existing foreground pipeline reached seed44 step531/1288 at 19:11:43 UTC. Step500 copied to `gdrive:exp/runs/E2/E2-main-s44-step500-a1d0588a969b`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-500.receipt.json`. Training-time 256-example dev loss was 0.000669655 at epoch 0.78, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` is active. Shared account reading at 19:12 UTC: 83.77 CU balance, 17.34 CU/hour, four assignments (not E2-only cost). Preserve the running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint using the download commands below.

## Update 2026-11-04 19:04 UTC: seed44 checkpoint 400

Existing foreground pipeline reached seed44 step425/1288. Step400 copied to `gdrive:exp/runs/E2/E2-main-s44-step400-e14e617a711f`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-400.receipt.json`. Training-time 256-example dev loss was 0.001221978 at epoch 0.62, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` is active. Preserve the running command/client without resubmission; seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint with the download commands below.

## Update 2026-11-04 18:56 UTC: seed44 checkpoint 300

Existing foreground pipeline reached seed44 step320/1288. Step300 copied to `gdrive:exp/runs/E2/E2-main-s44-step300-380a5f3d0e13`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-300.receipt.json`. The 256-example training-time dev loss was 0.000610810 at epoch 0.47, not a test score. The actual subscriber `exp-iopub-e24-scope.service` remains active. Preserve the same running command/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Continue polling existing output/status/checkpoint with the download commands below.

## Update 2026-11-04 18:49 UTC: seed44 checkpoint 200

Existing foreground pipeline reached seed44 step215/1288. Step200 copied to `gdrive:exp/runs/E2/E2-main-s44-step200-0c5a7f492a0b`, rclone exit 0; actual receipt `results/main-seed44-checkpoint-200.receipt.json`. Training-time 256-example dev loss was 0.001357997 at epoch 0.31, not a test score. The actual subscriber `exp-iopub-e24-scope.service` is active. Shared account usage at 18:49 UTC: 89.52 CU balance, 17.34 CU/hour across four assignments, not E2-only spending. Preserve the same running job/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete; continue polling output/status/checkpoint with the commands below.

## Update 2026-11-04 18:43 UTC: seed44 checkpoint 100

The existing foreground pipeline reached seed44 step134/1288. Step100 copied to `gdrive:exp/runs/E2/E2-main-s44-step100-9154d0ffd01f`, rclone exit 0; receipt `results/main-seed44-checkpoint-100.receipt.json`. Collected the actual seed44 configuration in `results/main-seed44.request.json`. Training-time 256-example dev loss was 0.005073927 at epoch 0.16, not a test score. `exp-iopub-e24-scope.service` is active. Preserve the existing running command/client without resubmission. Main seed44, six exploratory ablations and final analysis remain incomplete. Continue polling output/status and the seed44 checkpoint with the commands below.

## Update 2026-11-04 18:36 UTC: seed43 held-out complete; seed44 training

Collected all seed43 Glaive held-out predictions, metadata, score and details in `results/formal-main-seed43/heldout.*`: **1,893/2,000 = 94.65%**, bootstrap 95% CI **93.65–95.65%**. Prediction hash matches the score record. Inference ran 18:12:19–18:32:10 UTC (1,191 s); recorded in `docs/cost.md`. This is a single-seed Glaive result, not xLAM, a three-seed aggregate or evidence of uncontaminated generalization: agent-observed semantic near-duplicates across Glaive splits limit independence.

The existing pipeline has started main seed44 and reached step44/1288 at 18:36 UTC; its actual request is `/srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed44.request.json`. `exp-iopub-e24-scope.service` remains active. Preserve the running job/client without resubmission. Seed44, six exploratory ablations and final analysis remain incomplete. Next poll the existing output/status and collect seed44 checkpoints from `/content/e2-artifacts/main-seed44/last-verified-checkpoint.json` when available.

```sh
for name in predictions.jsonl predictions.jsonl.metadata.json score.json score.details.jsonl; do
  colab download -s exp-e24-recovery-a100 "/content/e2-artifacts/main-seed43-heldout.$name" "results/formal-main-seed43/heldout.$name"
done
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed44/last-verified-checkpoint.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed44-checkpoint-observed.json
```

## Update 2026-11-04 18:29 UTC: seed43 held-out 1700-case snapshot

The existing foreground pipeline advanced to 1,700/2,000 seed43 Glaive held-out predictions (1,700 unique IDs). Collected `results/formal-main-seed43/heldout.predictions.partial-1700.jsonl` as an incomplete, unscored snapshot. It is not a final accuracy or aggregate; semantic near-duplicates across Glaive splits still limit independence. `exp-iopub-e24-scope.service` is active. Preserve the running command/client without resubmission. Next poll using the commands below and collect full predictions, metadata, score and details when complete, then follow seed44 training. Seed44, ablations and final analysis remain outstanding.

## Update 2026-11-04 18:23 UTC: seed43 held-out partial snapshot

The existing foreground pipeline reached 1,104/2,000 Glaive held-out predictions for seed43 (1,104 unique IDs). Collected `results/formal-main-seed43/heldout.predictions.partial-1104.jsonl` as an incomplete, unscored snapshot, not a final metric. `exp-iopub-e24-scope.service` is active; preserve the same running command/client without resubmission. Glaive semantic near-duplicates remain a test-independence limitation. Seed43 complete held-out scores, seed44, exploratory ablations and final analysis are outstanding.

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed43-heldout.predictions.jsonl /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed43-heldout.partial.jsonl
```

Next poll the existing output/status and this prediction file; collect complete predictions, metadata, score and details once available using the seed42 pattern below.

## Update 2026-11-04 18:16 UTC: seed43 BFCL complete

Collected all seed43 BFCL predictions, inference metadata, score and case details in `results/formal-main-seed43/bfcl.*`. **667/1,240 = 53.790%** subset accuracy, bootstrap 95% CI **51.129–56.532%**. Categories: simple_python 85.0%, multiple 56.0%, parallel 0/200, parallel_multiple 3/200 (1.5%), irrelevance 212/240 (88.33%). The actual prediction SHA256 matches the score record. Preserve this negative result; it is one seed, not the three-seed aggregate or full BFCL leaderboard score. Baselines remain 74.758% (1.5B) and 86.371% (7B).

The original pipeline has moved on to seed43 held-out inference; final held-out scores, seed44 and exploratory ablations remain outstanding. The actual subscriber `exp-iopub-e24-scope.service` is active. Preserve the same job/client without resubmission. Next poll output/status and collect complete `main-seed43-heldout.*` from `/content/e2-artifacts` using the seed42 download pattern below.

```sh
for name in predictions.jsonl predictions.jsonl.metadata.json score.json score.details.jsonl; do
  colab download -s exp-e24-recovery-a100 "/content/e2-artifacts/main-seed43-bfcl.$name" "results/formal-main-seed43/bfcl.$name"
done
```

## Update 2026-11-04 18:10 UTC: seed43 BFCL 956-case snapshot

The existing foreground pipeline advanced to 956/1,240 seed43 BFCL predictions (956 unique case IDs), collected in `results/formal-main-seed43/bfcl.predictions.partial-956.jsonl`. This is incomplete and unscored, not a final accuracy or aggregate. `exp-iopub-e24-scope.service` is active; preserve it and the running command without resubmission. Use the prediction download command below and existing output/status polls. Collect complete predictions, metadata, score and details when available, then seed43 held-out results. Seed44, exploratory ablations and final analysis remain outstanding.

## Update 2026-11-04 18:04 UTC: seed43 BFCL partial predictions collected

Existing foreground pipeline continues seed43 BFCL inference. Downloaded 512/1,240 predictions with 512 unique case IDs to `results/formal-main-seed43/bfcl.predictions.partial-512.jsonl`. This is an incomplete, unscored snapshot, not a final accuracy or a three-seed result. `exp-iopub-e24-scope.service` is active. Do not resubmit or replace the running job/client; seed43 complete scores/held-out evaluation, seed44 and ablations remain outstanding.

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed43-bfcl.predictions.jsonl /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed43-bfcl.partial.jsonl
```

Continue polling existing output/status and the prediction file; collect full predictions, metadata, score and details once complete using the seed42 pattern below.

## Update 2026-11-04 17:57 UTC: seed43 training and adapter complete

Main seed43 finished two epochs at 17:56:39 UTC: 18,547 selected positives, 20,608 retained training examples including negatives, zero overlength drops. Collected `results/main-seed43.train.json`, `results/main-seed43.request.json`, and `results/main-seed43.env.txt`. Adapter copied to `gdrive:exp/runs/E2/E2-main-resume-20261104-03-main-seed43-adapter` at 17:56:58 UTC; actual receipt `results/main-seed43.adapter-receipt.json`. The full timestamp interval is 5,673 s versus Trainer runtime 5,625.1212 s, not a throughput benchmark. Recorded these boundaries and account-wide usage (102.51 CU, 17.34 CU/hour, four assignments) in `docs/cost.md`.

The existing foreground pipeline has started seed43 BFCL inference; no final seed43 test metric has been collected yet. `exp-iopub-e24-scope.service` was active at 17:56 UTC. Preserve the running job/client, seed44 and ablations without resubmitting. Poll the existing output/status; when complete, collect `main-seed43-bfcl.*` then `main-seed43-heldout.*` from `/content/e2-artifacts` using the seed42 download pattern below.

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed43/train.json results/main-seed43.train.json
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed43/request.json results/main-seed43.request.json
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed43/env.txt results/main-seed43.env.txt
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/workspace/results/main-seed43.adapter-receipt.json results/main-seed43.adapter-receipt.json
```

## Update 2026-11-04 17:51 UTC: seed43 checkpoint 1200

The existing foreground pipeline reached seed43 step 1204/1288. Step1200 copied to `gdrive:exp/runs/E2/E2-main-s43-step1200-6dac6aa18ae3`, rclone exit 0; receipt `results/main-seed43-checkpoint-1200.receipt.json`. The 256-example training-time dev loss was 0.000569355 at epoch 1.86, not a test score. `exp-iopub-e24-scope.service` was active at 17:49 UTC. Preserve the running command and subscriber without resubmission. Seed43 final adapter/evaluations, seed44 and ablations remain incomplete. Next poll the output/status, then collect `/content/e2-artifacts/main-seed43/train.json` and the workspace's `results/main-seed43.adapter-receipt.json` when they exist; follow the seed42 collection pattern below.

## Update 2026-11-04 17:43 UTC: README result snapshot and seed43 checkpoint 1100

Updated `README.md` to show the completed seed42 BFCL/Glaive results and paired uncertainty, remove obsolete ownership/recovery statements, link the actual E3 adapter receipt, and disclose the accepted agent audit and Glaive semantic near-duplicates. No data or measurements were changed; this remains an interim single-seed result, with main43/44 and ablations unfinished.

Existing foreground pipeline reached seed43 step 1100/1288; its step1100 copy to `gdrive:exp/runs/E2/E2-main-s43-step1100-96b90dfb8d35` completed with rclone exit 0. Receipt: `results/main-seed43-checkpoint-1100.receipt.json`. Training-time 256-example dev loss was 0.000571716 at epoch 1.71, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` was active at 17:41 UTC. Preserve the running job/client; continue polling using the download commands below without resubmission.

## Update 2026-11-04 17:36 UTC: seed43 checkpoint 1000 and cost ledger

The existing foreground pipeline reached seed43 step 1000/1288 and completed its checkpoint copy to `gdrive:exp/runs/E2/E2-main-s43-step1000-52b550a97dc8` (rclone exit 0); receipt `results/main-seed43-checkpoint-1000.receipt.json`. Training-time dev loss on 256 examples was 0.000505016 at epoch 1.55, not a test score. `exp-iopub-e24-scope.service` was active at 17:34 UTC. Preserve the same job and subscriber; do not resubmit. Seed43/44 final evaluations and ablations remain incomplete.

Updated `docs/cost.md` with the actual completed seed42 resumed-training and inference timestamps/durations, retained example counts, and shared account usage. The resumed segment is not full seed42 training time; account CU readings are not E2-only costs. Latest reading at 17:35:23 UTC: 108.35 CU, 17.34 CU/hour, four assignments. Continue polling with the download commands below.

## Update 2026-11-04 17:29 UTC: seed43 checkpoint 900

The existing foreground pipeline reached seed43 step 905/1288 at 17:28:45 UTC. Step 900 copied to `gdrive:exp/runs/E2/E2-main-s43-step900-7aba81037cda`, rclone exit 0; receipt `results/main-seed43-checkpoint-900.receipt.json`. The 256-example training-time dev loss was 0.000587398 at epoch 1.4, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` was active at 17:27 UTC. Preserve this running job and subscriber without resubmission. Seed43/44 final evaluations and the ablations remain incomplete; continue polling using the download commands below.

## Update 2026-11-04 17:22 UTC: seed43 checkpoint 800

The existing foreground pipeline reached seed43 step 811/1288. Step 800 copied to `gdrive:exp/runs/E2/E2-main-s43-step800-2359cfc35597`, rclone exit 0; receipt `results/main-seed43-checkpoint-800.receipt.json`. The 256-example training-time dev loss was 0.000490672 at epoch 1.24, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` was active at 17:21 UTC. Shared account usage at 17:21:56 UTC: 111.23 CU balance, 17.34 CU/hour across four assignments, not E2-only cost. Preserve the job and subscriber without resubmission; seed43/44 final evaluations and the ablations remain incomplete. Continue polling using the download commands below.

## Update 2026-11-04 17:14 UTC: seed43 checkpoint 700

The existing foreground pipeline reached seed43 step 705/1288. Step 700 copied to `gdrive:exp/runs/E2/E2-main-s43-step700-0011a11f3661`, rclone exit 0; receipt `results/main-seed43-checkpoint-700.receipt.json`. The 256-example training-time dev loss was 0.000564851 at epoch 1.09, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` is active. Preserve the running job and subscriber without resubmission; seed43/44 final evaluations and the ablations remain incomplete. Poll using the download commands below.

## Update 2026-11-04 17:08 UTC: seed43 checkpoint 600

The existing foreground pipeline reached seed43 step 624/1288. Step 600 copied to `gdrive:exp/runs/E2/E2-main-s43-step600-f906ea3c368d`, rclone exit 0; receipt `results/main-seed43-checkpoint-600.receipt.json`. The 256-example training-time dev loss was 0.000616616 at epoch 0.93, not a test score. `exp-iopub-e24-scope.service` was active at 17:06 UTC. A download attempt timed out; subsequent downloads succeeded and showed further training progress. Preserve the existing job and subscriber; no resubmission or recovery is needed. Continue polling with the commands below. Seed43/44 final evaluations and the ablations remain incomplete.

## Update 2026-11-04 17:00 UTC: seed43 checkpoint 500

Existing foreground pipeline reached seed43 step 511/1288. Step 500 copied to `gdrive:exp/runs/E2/E2-main-s43-step500-132b66a925dc`, rclone exit 0; receipt `results/main-seed43-checkpoint-500.receipt.json`. Training-time 256-example dev loss was 0.000745143 at epoch 0.78, not a test score. The actual output subscriber `exp-iopub-e24-scope.service` remains active. One download attempt timed out; subsequent downloads succeeded and showed continued training, so no recovery or resubmission was needed. Account-wide usage at 17:00 UTC: 116.99 CU balance, 17.34 CU/hour across four assignments (not E2-only cost). Continue polling the same run with the download commands below; seed43/44 evaluations and ablations remain incomplete.

## Update 2026-11-04 16:52 UTC: paired seed42 analysis and seed43 checkpoint 400

Computed paired comparisons from the already-collected seed42/baseline case outcomes, without new inference. Main seed42 is **−17.50 pp** versus 1.5B (paired bootstrap 95% CI **[−20.56, −14.68] pp**) and **−29.11 pp** versus 7B (**[−32.34, −25.81] pp**). Irrelevance improves by +20 pp versus 1.5B, but parallel wrong-count checker failures increase from 38 to 341 across the two parallel categories. Exact error labels, source hashes and per-category intervals are in `results/formal-main-seed42/comparison.{json,md}`; reproduce with `python3 scripts/compare_main_seed42.py`. This is an interim single-seed analysis, not a three-seed conclusion. Checker labels do not uniquely establish seven-way semantic error causes; final error analysis remains required.

Existing foreground pipeline reached seed43 step 403/1288 at 16:52 UTC. Step 400 copied to `gdrive:exp/runs/E2/E2-main-s43-step400-410c3eb401ca`, rclone exit 0; receipt `results/main-seed43-checkpoint-400.receipt.json`. `exp-iopub-e24-scope.service` was active at 16:50 UTC. Preserve this existing job and subscriber; do not resubmit. Main seeds43/44 and the six exploratory ablations remain incomplete. Poll using the download commands below.

## Update 2026-11-04 16:45 UTC: seed43 checkpoint 300

Existing foreground pipeline reached seed43 step 305/1288. Step 300 was copied to `gdrive:exp/runs/E2/E2-main-s43-step300-c49806819505` with rclone exit 0; receipt `results/main-seed43-checkpoint-300.receipt.json`. The 256-example training-time dev loss was 0.00061714 at epoch 0.47, not a test score. The output subscriber `exp-iopub-e24-scope.service` was active at 16:44 UTC. Continue polling the same run using the commands below, without resubmitting; seed43/44 and ablations are incomplete.

## Update 2026-11-04 16:38 UTC: seed43 checkpoint 200

The existing foreground pipeline reached seed43 step 208/1288; `exp-iopub-e24-scope.service` is active. Step 200 copied to `gdrive:exp/runs/E2/E2-main-s43-step200-42893b83bcb2`, rclone exit 0; actual receipt `results/main-seed43-checkpoint-200.receipt.json`. Training-time dev loss on 256 examples was 0.001469 at epoch 0.31, not a test score. Account-wide usage at 16:38 UTC was 122.77 CU balance at 17.34 CU/hour across four assignments, not E2-only cost. Continue polling the existing job; do not resubmit. Seed43/44 and the ablations remain incomplete.

## Update 2026-11-04 16:30 UTC: seed43 training

Existing foreground `E2-main-resume-20261104-03` has advanced to main seed43 step 110/1288. Step 100 was copied to `gdrive:exp/runs/E2/E2-main-s43-step100-a71af6992b25`; actual rclone receipt `results/main-seed43-checkpoint-100.receipt.json`. The current output subscriber is `exp-iopub-e24-scope.service`, active; the older PID 82069 is obsolete. Do not resubmit the existing job. Poll its output/status using the commands below.

**Review scope updated 2026-11-05:** the 50-example agent audit is the accepted review; no new human annotation or delayed retest is requested. `human_validation_complete=false` and `human_validation_required=false`; retain uncertain audit findings as limitations and never use agent ratings as human-gold labels. This supersedes historical pending-human wording below.

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed43/last-verified-checkpoint.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed43-checkpoint-observed.json
```

## Update 2026-11-04 16:23 UTC: seed 42 held-out score collected

The existing run completed 2,000 Glaive held-out predictions for main seed42: **94.5%** accuracy, bootstrap 95% CI **93.4–95.55%**. Full predictions, metadata, score and details are in `results/formal-main-seed42/heldout.*`. This is a single-seed result on the Glaive test split, not xLAM or a three-seed aggregate; the separately documented semantic near-duplicates across Glaive splits limit the test's independence. The existing foreground pipeline and output subscriber remain active; continue the remaining main seeds and variants without resubmitting.

```sh
root=/content/e2-artifacts
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.predictions.jsonl" results/formal-main-seed42/heldout.predictions.jsonl
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.predictions.jsonl.metadata.json" results/formal-main-seed42/heldout.predictions.jsonl.metadata.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.score.json" results/formal-main-seed42/heldout.score.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.score.details.jsonl" results/formal-main-seed42/heldout.score.details.jsonl
```

## Update 2026-11-04 16:16 UTC

The existing foreground job remains running; main seed42 held-out inference advanced to **1472/2000** predictions. Preserved the unscored incomplete snapshot at `results/formal-main-seed42/heldout.predictions.partial-1472.jsonl`. Subscriber PID 82069 remains active. Use the held-out download command below to poll; collect complete predictions, metadata and score when available, and do not resubmit the ongoing seed43/44 and ablation pipeline.

## Update 2026-11-04 16:10 UTC

The existing foreground job remains active and seed42 held-out inference reached 840/2000 cases; saved the incomplete, unscored snapshot in `results/formal-main-seed42/heldout.predictions.partial-840.jsonl`. Subscriber PID 82069 remains active. Continue the same job and collect its full held-out score; do not resubmit.

The separately performed **agent**, not human, audit of the 50 fixed negative examples is preserved in `results/negative-audit/agent-review/`. It judged 47 tool choices irrelevant, one clearly mislabeled (`glaive-20088-negative-991`), and two uncertain; it also found semantic near-duplicates across the Glaive splits. These directed observations do not quantify overall label noise or prove BFCL leakage; disclose the limitations and do not change this run or its scores. The 50 actual human verdicts remain pending.

## Update 2026-11-04 16:04 UTC: seed 42 BFCL score collected

The existing run completed all 1,240 five-category BFCL cases for main seed42. Collected predictions, metadata, score, and case details in `results/formal-main-seed42/`. Measured accuracy **57.258%** (bootstrap 95% CI **54.677–60.0%**), versus the same-dataset 1.5B baseline **74.758%**; parallel accuracy **0/200**, versus baseline **65.5%**. This is a negative single-seed result, not the three-seed aggregate or full leaderboard. Irrelevance accuracy was 90.42%. Preserve these results rather than rerunning to improve them. Held-out inference is underway: saved an unscored 252/2000 snapshot to `results/formal-main-seed42/heldout.predictions.partial-252.jsonl`. The foreground job and output subscriber PID 82069 remain active; do not resubmit.

```sh
root=/content/e2-artifacts
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.predictions.jsonl" results/formal-main-seed42/bfcl.predictions.jsonl
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.predictions.jsonl.metadata.json" results/formal-main-seed42/bfcl.predictions.jsonl.metadata.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.score.json" results/formal-main-seed42/bfcl.score.json
colab download -s exp-e24-recovery-a100 "$root/main-seed42-bfcl.score.details.jsonl" results/formal-main-seed42/bfcl.score.details.jsonl
colab download -s exp-e24-recovery-a100 "$root/main-seed42-heldout.predictions.jsonl" /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42-heldout.partial.jsonl
```

## Update 2026-11-04 15:57 UTC

The existing foreground run remains running; seed42 BFCL predictions reached **896/1240**. Saved the incomplete snapshot to `results/formal-main-seed42/bfcl.predictions.partial-896.jsonl`; it is not a score. `exp-iopub-e24.service` was no longer present and no matching subscriber process was found; the reason is unknown. Attached one real-output subscriber to the existing busy kernel (PID 82069, log `/srv/exp-runner/logs/exp-e24-recovery-a100-iopub.log`), without submitting another job:

```sh
setsid -f /srv/exp-runner/runtime/python/bin/python /srv/exp-runner/app/ops/attach_existing_output.py exp-e24-recovery-a100 </dev/null >>/srv/exp-runner/logs/exp-e24-recovery-a100-iopub.log 2>&1
```

Continue polling the existing output/status and collect the full BFCL score and held-out results when ready. Do not resubmit.

## Update 2026-11-04 15:50 UTC

The existing foreground run remains active and is evaluating the completed main seed42 adapter on BFCL. Downloaded a **partial 536/1240 prediction snapshot**, `results/formal-main-seed42/bfcl.predictions.partial-536.jsonl`; it is not a scored result. The real output subscriber remains active. Shared account usage at 15:50 UTC: 137.24 CU balance, 17.34 CU/h across four assignments (not E2-only cost). Collect full predictions and scores when complete; held-out evaluation and later seeds/ablations remain in the running pipeline.

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed42-bfcl.predictions.jsonl /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42-bfcl.partial.jsonl
```

## Update 2026-11-04 15:44 UTC: seed 42 adapter complete

Main seed 42 completed two epochs at 15:43:24 UTC (18,547 selected positives, 20,608 training examples including negatives); actual training record is `results/main-seed42.train.json`. Its adapter was copied successfully to `gdrive:exp/runs/E2/E2-main-resume-20261104-03-main-seed42-adapter` at 15:43:44 UTC; copy receipt `results/main-seed42.adapter-receipt.json`. The run has started inference/evaluation and remains active; these are not yet final BFCL or held-out scores. E3 can use this actual adapter for its separate comparison; E3 HANDOFF records the destination. Seeds 43/44 and six seed42 variants are still in the existing pipeline. Do not resubmit.

Collected with:

```sh
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed42/train.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42.train.json
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/workspace/results/main-seed42.adapter-receipt.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/main-seed42.adapter-receipt.json
```

## Update 2026-11-04 15:37 UTC

Existing A100 foreground run continues at seed 42 step 1203/1288; its output subscriber is active. Step 1200 copied to `gdrive:exp/runs/E2/E2-main-s42-step1200-599d0b33cb61` (rclone exit 0); receipt `results/main-seed42-checkpoint-1200.receipt.json`. The 256-example training-time dev loss at epoch 1.86 was 0.0005691974656656384, not a final test metric. The completed E3 adapter is still pending; collect its receipt and train record when ready. Poll below without resubmitting.

## Update 2026-11-04 15:30 UTC

The existing A100 foreground run continues, reaching seed 42 step 1103/1288; the actual output subscriber is active. Step 1100 copied to `gdrive:exp/runs/E2/E2-main-s42-step1100-751e50e86d79` (rclone exit 0); receipt `results/main-seed42-checkpoint-1100.receipt.json`. Training-time 256-example dev loss at epoch 1.71 was 0.0006018654676154256, not a final test result. The finished E3 adapter remains pending. Poll using the commands below; do not resubmit.

## Update 2026-11-04 15:22 UTC

Existing A100 foreground run continues: seed 42 reached step 1001/1288 and the output subscriber is active. Step 1000 copied to `gdrive:exp/runs/E2/E2-main-s42-step1000-996c08718538` (rclone exit 0); receipt `results/main-seed42-checkpoint-1000.receipt.json`. Its training-time 256-example dev loss at epoch 1.55 was 0.000523304333910346, not a final test result. The final E3 adapter remains pending. Continue polling using the commands below; do not resubmit.

## Update 2026-11-04 15:15 UTC

Existing A100 foreground run continues: seed 42 reached step 901/1288 and the real-output subscriber is active. Step 900 copied to `gdrive:exp/runs/E2/E2-main-s42-step900-998e5ec60d6d` (rclone exit 0); receipt `results/main-seed42-checkpoint-900.receipt.json`. The 256-example training-time dev loss at epoch 1.4 was 0.0006694518961012363, not a test result. The completed adapter for E3 is still pending. Continue polling below; do not resubmit.

## Update 2026-11-04 15:08 UTC

Existing foreground run is active; seed 42 reached step 809/1288 and `exp-iopub-e24.service` is active. Step 800 was copied to `gdrive:exp/runs/E2/E2-main-s42-step800-0257573cff50` (rclone exit 0); receipt `results/main-seed42-checkpoint-800.receipt.json`. The 256-example dev loss at epoch 1.24 was 0.0005717489402741194, a training-time measurement, not a final test metric. This checkpoint is not the final E3 adapter. Continue polling with the commands below; do not resubmit.

## Update 2026-11-04 15:01 UTC

The existing foreground run remains active; seed 42 reached step 713/1288 and `exp-iopub-e24.service` is active. Step 700 copied successfully to `gdrive:exp/runs/E2/E2-main-s42-step700-d6e9866b9bb3` at 15:00 UTC; receipt: `results/main-seed42-checkpoint-700.receipt.json`. This is a training checkpoint, not the final adapter for E3. Continue polling using the commands below; do not resubmit.

## Update 2026-11-04 14:55 UTC

The existing `E2-main-resume-20261104-03` foreground run remains active, with output at seed 42 step 626/1288; `exp-iopub-e24.service` is active. Step 600 copied successfully to `gdrive:exp/runs/E2/E2-main-s42-step600-483a953ed830` at 14:53 UTC; the actual receipt is `results/main-seed42-checkpoint-600.receipt.json`. This is a checkpoint, not the finished adapter required by E3. Continue polling with the commands below; do not resubmit.

## Update 2026-11-04 14:48 UTC

Existing foreground run `E2-main-resume-20261104-03` is running; output reached seed 42 step 536/1288, and `exp-iopub-e24.service` remains active. The step-500 checkpoint was copied to `gdrive:exp/runs/E2/E2-main-s42-step500-3f88f4ca1b6a` at 14:46 UTC (rclone exit status 0); receipt: `results/main-seed42-checkpoint-500.receipt.json`. This checkpoint is not the finished adapter; E3 still awaits seed 42 completion. Continue polling with the commands below, without resubmission.

## Update 2026-11-04 14:41 UTC

The existing `E2-main-resume-20261104-03` job remains running on `exp-e24-recovery-a100`: HTTP status reports running and its real output reached seed 42 step 440/1288. The server's `exp-iopub-e24.service` is active. The checkpoint-400 rclone copy completed successfully at 14:38:56 UTC; receipt is `results/main-seed42-checkpoint-400.receipt.json` and destination is `gdrive:exp/runs/E2/E2-main-s42-step400-93abe7d040e8`. This is a resume checkpoint, **not** a finished adapter; E3 still waits for the final seed42 adapter and train record. At 14:41 UTC `colab usage` reported shared account balance 157.48 CU and total rate 17.34 CU/h across four assignments, not E2-only spending.

Poll without starting a second job:

```sh
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/status.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/status-observed.json
colab download -s exp-e24-recovery-a100 /content/experiment-runs/E2-main-resume-20261104-03/output.log /srv/exp-runner/state/remote/E2-main-resume-20261104-03/output-observed.log
colab download -s exp-e24-recovery-a100 /content/e2-artifacts/main-seed42/last-verified-checkpoint.json /srv/exp-runner/state/remote/E2-main-resume-20261104-03/checkpoint-observed.json
```

**Started 2026-11-04 23:30:16 JST: `E2-main-resume-20261104-03` is running in the actual Jupyter kernel foreground (PID 6202).** Runtime `exp-e24-recovery-a100`, endpoint `gpu-a100-s-ass1b0-kysuwtw187ve` (A100 40GB). E4's model has exited; E2 owns the GPU. The Mac client continues reading real IOPub output while root/e8 attach the server client. Local writes freeze only when root explicitly confirms the handoff.

## Current run and exact next action

Running run: **`E2-main-resume-20261104-03`**, source commit **`04506d9943f5d9835d97a5edc25d5f76ae60ab60`**. Local request: `artifacts/E2-main-resume-20261104-03/request.json`; remote source and foreground entrypoint are already uploaded. Independent `/content/e2-venv`, Glaive data, step 300 checkpoint, and pinned 1.5B weights are prepared. Actual IOPub progress reached step 366/1288 at 2026-11-04T14:36:05.001476+00:00, confirming continuation beyond checkpoint 300. The current main42 adapter estimate is 00:35–00:50 JST on 2026-11-05, subject to remaining evaluation/copy overhead.

Already submitted payload; do not submit it again:

```sh
bash scripts/resume_formal.sh gdrive:exp/runs/E2/E2-main-s42-step300-4478da60bce6
```

The payload resumes seed 42 at step 300, completes main seeds 42/43/44, then directly runs all six 10k variants at seed 42. The original two baselines are not rerun. Actual work is submitted to the existing Jupyter kernel foreground and the client continuously consumes real IOPub output. Root/e8 own server connection continuity after the Mac handoff; attach to the existing message/run, never submit another model.

Remote root: `/content/experiment-runs/E2-main-resume-20261104-03`. HTTP downloads work while the kernel is busy:

```sh
colab download -s exp-e24-recovery-a100 \
  /content/experiment-runs/E2-main-resume-20261104-03/status.json status.json
colab download -s exp-e24-recovery-a100 \
  /content/experiment-runs/E2-main-resume-20261104-03/output.log output.log
colab download -s exp-e24-recovery-a100 \
  /content/experiment-runs/E2-main-resume-20261104-03/kernel-client.json kernel-client.json
```

`kernel-client.json` records the executed message ID and connection-file path for attaching a real output client. Use official SSH for file packaging or runtime inspection while the kernel is busy; an extra `colab exec` waits behind the active foreground job. Do not stop the only output client before the server client has attached.

## Durable evidence and resume files

- Both formal BFCL subset baselines completed 1240 cases: 1.5B **74.758%** (95% CI 72.419–77.258), 7B **86.371%** (84.355–88.145). Paired overall difference **+11.613pp** [9.113,14.274]. **Negative result:** 7B irrelevance is 60.42%, versus 1.5B 70.42%; paired difference −10pp [−15.83,−4.17]. Raw results and comparison are in `results/formal-baselines/`.
- Drive baselines: `gdrive:exp/runs/E2/E2-formal-baselines-20261104-01-baseline-1.5b` and `gdrive:exp/runs/E2/E2-formal-recovery-20261104-02-baseline-7b`.
- Fixed Glaive split: train 18547/dev 2003/test 2000, saved at `gdrive:exp/runs/E2/E2-glaive-data-20261104`. Native runtime path `/content/data/e2-glaive`.
- Latest recovered main checkpoint: `gdrive:exp/runs/E2/E2-main-s42-step300-4478da60bce6`; downloaded complete model/optimizer/scheduler/RNG/TrainerState(global_step 300). Matching request: `gdrive:exp/runs/E2/E2-formal-recovery-20261104-02-main-seed42-config/request.json`.
- Current local training output will be `/content/e2-artifacts/main-seed42`. Latest durable checkpoint receipt: `last-verified-checkpoint.json` there; checkpoints save every 100 optimizer steps. New saves include `request.json`; final adapter exports include `train.json`, `env.txt`, and `request.json`.
- E3 needs `/content/e2-artifacts/main-seed42/adapter` after seed 42 completes. Its Drive destination will be in the current workspace's `results/main-seed42.adapter-receipt.json`; matching training evidence is `results/main-seed42.train.json`. No final adapter exists yet.

## Scope, limits, and historical failures

Main requires seeds 42/43/44. Six 10k rank/negative variants first run seed 42 only and remain **single-seed exploratory**. Stable main-conclusion contrasts receive 43/44 only after selection on development data, never test scores. New train records include the most recent fixed 256-example dev loss and its evaluation step. The 30k variant remains blocked by only 18547 unique training positives. All 50 human negative-audit verdicts in `results/negative-audit/` are null; do not mark human review completed.

The earlier `exp-preflight-l4` and `exp-e4-qwen` runtimes disappeared; causes were not established. `E2-formal-recovery-20261104-02` is historical, not running. The follow-on `E2-exploratory-ablations-20261104-01` upload failed before execution; no separate follow-on process should be resumed. The new payload chains ablations directly.

Pinned stack: Python 3.12, torch 2.6.0+cu124, Transformers 4.51.3, PEFT 0.15.2, Accelerate 1.6.0, datasets 3.5.0, BFCL 2026.3.23. Private runtime files are `/content/e2-experiment-env.json` and `/content/e2-rclone.conf`; normal copies use `gdrive:exp/runs` with the existing quota header. Earlier shared throughput was about 4.2s/optimizer step; do not promise all seeds before bedtime or treat shared/resumed timings as a throughput benchmark. CU snapshots in `results/formal-baselines/usage-snapshots.jsonl` are account-wide, not E2-only charges.

Actual foreground receipt: `results/resume-03-kernel-client.json`. Message ID `4344e714-5beab0aa0d35eec67cb710a4_9905_1`; connection file `/root/.local/share/jupyter/runtime/kernel-66b45375-3f56-45c3-aedf-6272148d3275.json`. This identifies the existing execution for a subscribing output client, not a command to execute twice. Current request/status copies are `results/resume-03-request.json` and `results/resume-03-status.json`.
