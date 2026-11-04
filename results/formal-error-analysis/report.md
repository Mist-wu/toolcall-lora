# BFCL seven-category evidence analysis

Completed main seeds and baselines plus 1/6 collected exploratory ablation BFCL results; five-category subset. Ablations are single-seed, not confirmatory.

Per-failed-case evidence, potentially multilabel, not an exhaustive seven-way partition or semantic root-cause annotation. Unresolved cases are retained, not assigned by guesswork. The official checker stops at a diagnostic, so argument counts are lower bounds.

| Evidence category | baseline-1.5b | baseline-7b | main-seed42 | main-seed43 | main-seed44 | n10000-r8-neg0-seed42 |
|---|---:|---:|---:|---:|---:|---:|
| wrong_function | 10 | 2 | 1 | 1 | 1 | 9 |
| missing_argument | 40 | 1 | 21 | 19 | 20 | 19 |
| wrong_type | 5 | 5 | 5 | 5 | 5 | 5 |
| wrong_value | 44 | 18 | 42 | 44 | 42 | 43 |
| extra_call | 11 | 5 | 1 | 0 | 0 | 4 |
| missed_call | 34 | 12 | 419 | 472 | 402 | 31 |
| false_call | 69 | 95 | 22 | 27 | 23 | 235 |
| All failed cases | 313 | 169 | 530 | 573 | 506 | 425 |
| Unresolved (including parser failures) | 100 | 31 | 19 | 5 | 13 | 79 |

## Definitions

- **wrong_function**: Official wrong_func_name, or parsed equal-count response whose function-name multiset differs from the reference. Unequal-count name mismatches are not forced into function substitution.
- **missing_argument**: Official missing_required or missing_optional. This means a benchmark-expected parameter, not necessarily a schema-required parameter.
- **wrong_type**: Official type_error:* diagnostic.
- **wrong_value**: Official value_error:* diagnostic.
- **extra_call**: Parsed response has more calls than reference, with at least one expected call. Irrelevance calls use false_call instead.
- **missed_call**: Parsed response has fewer calls than reference, including zero. Count deficit is not proof of a semantic reason.
- **false_call**: Parsed call on a zero-call irrelevance reference.

## Interpretation

The main models show much more call omission than the baselines; the seven-way table separates count direction using actual parsed outputs rather than guessing from wrong_count alone. It does not attribute the regression causally to negative training before ablations finish. Missing-parameter/type/value counts only describe errors exposed by the official checker, not all latent errors.

Ambiguous same-name, same-count parallel no-match cases remain unresolved rather than being declared value errors. Parser failures remain outside the seven labels, not automatically counted as missed calls. Full per-case evidence and unresolved checker labels are in `cases.jsonl` and `summary.json`.

No human labels or new judge ratings. Parser count deficits are observable behavior, not proof of why the model erred. BFCL pretraining contamination and Glaive negative-label noise/near-duplicates remain possible. No training data or official metrics changed.
 Agent review is accepted, not human-gold validation; human_validation_complete=false and human_validation_required=false.

Reproduce this small CPU analysis: `python3 scripts/analyze_bfcl_errors.py`. The saved reference file is the original 1,240-case prepared BFCL evaluation, with its SHA256 compared to each score provenance. No checker/inference rerun.
