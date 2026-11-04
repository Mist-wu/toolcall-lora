# Pending human review of synthetic negatives

The fixed 50-example sample exactly reproduces the main configuration's data shuffle and negative-tool construction (data seed 42), then samples the negative pool with seed 42. Read each query and donated tool schema; fill `human_verdict` and `human_notes` only after a person reviews it. All verdicts are currently null. Name-disjoint tool names alone do not establish semantic irrelevance.

This artifact prepares human review; it does not complete it or validate the negative labels. The three main training seeds use the same data seed, so this sample covers that shared negative-construction process.
