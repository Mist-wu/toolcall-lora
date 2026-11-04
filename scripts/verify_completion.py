#!/usr/bin/env python3
"""Fail closed unless formal baseline, matrix and held-out evidence is complete."""
import json
from pathlib import Path
import sys
import hashlib
import math

ROOT=Path(__file__).resolve().parents[1]
def require(condition,message):
    if not condition:raise ValueError(message)

def verify():
    path=ROOT/"results/formal-summary.json"
    require(path.is_file(),"formal-summary.json missing: implementation/smoke does not complete E2")
    summary=json.loads(path.read_text())
    require(summary.get("experiment_id")=="E2" and summary.get("status")=="formal_complete","wrong formal status")
    require(summary.get("synthetic") is False and summary.get("smoke") is False,"synthetic or smoke evidence")
    require(summary.get("baseline_sources_verified") is True,"public baseline source comparison pending")
    require(summary.get("negative_data_audit_complete") is True,"negative-tool relevance audit pending")
    records=summary.get("records",[])
    required={"baseline-1.5b","baseline-7b","main","n10000-r8-neg0","n10000-r8-neg10","n10000-r16-neg0","n10000-r16-neg10","n10000-r64-neg0","n10000-r64-neg10","n30000-r16-neg10"}
    require({r["label"] for r in records}==required,"incomplete baseline/ablation coverage")
    for record in records:
        paths=record.get("score_files",[])
        needed={None} if record["label"].startswith("baseline-") else {42,43,44}
        seeds=set()
        for rel in paths:
            score_path=(ROOT/rel).resolve()
            require(score_path.is_relative_to(ROOT),"score path escapes repo")
            require(score_path.is_file(),f"missing score {rel}")
            score=json.loads(score_path.read_text())
            require(score.get("smoke") is False and score.get("data_manifest",{}).get("fixture") is False,"nonformal score")
            require(score.get("label")==record["label"],"score label mismatch")
            require(score.get("inference",{}).get("gpu"),"GPU inference provenance missing")
            predictions=Path(score["predictions"])
            if not predictions.is_absolute():predictions=ROOT/predictions
            require(predictions.is_file(),"raw predictions missing")
            require(hashlib.sha256(predictions.read_bytes()).hexdigest()==score["predictions_sha256"],"prediction provenance mismatch")
            for category in ["simple_python","multiple","parallel","parallel_multiple","irrelevance"]:
                require(score.get(category,{}).get("n",0)>0,f"missing BFCL {category}")
                accuracy=score[category]["accuracy"]
                require(isinstance(accuracy,(int,float)) and math.isfinite(accuracy) and 0<=accuracy<=1,"invalid measured accuracy")
                interval=score[category]["ci95"]
                require(len(interval)==2 and 0<=interval[0]<=interval[1]<=1,"invalid confidence interval")
            require(score["overall_subset"]["n"]==score["data_manifest"].get("rows"),"BFCL coverage differs from official manifest")
            raw=[json.loads(line) for line in predictions.read_text().splitlines() if line.strip()]
            require(len(raw)==score["overall_subset"]["n"] and len({r["id"] for r in raw})==len(raw),"raw prediction coverage is incomplete or duplicated")
            seeds.add(score.get("seed"))
        require(seeds==needed,f"wrong seeds for {record['label']}")
        if not record["label"].startswith("baseline-"):
            training_seeds=set()
            for rel in record.get("train_files",[]):
                train=json.loads((ROOT/rel).read_text())
                require(train.get("status")=="train_complete" and train.get("config",{}).get("smoke") is False,"smoke training cannot count as formal")
                require(train.get("config",{}).get("run_name")==record["label"],"training configuration mismatch")
                require(train["config"].get("model")=="Qwen/Qwen2.5-1.5B-Instruct","wrong training model")
                require(train.get("gpu"),"training GPU provenance missing")
                require(train.get("metrics",{}).get("epoch",0)>=1.99,"two formal epochs not completed")
                manifest=train.get("data_manifest",{})
                require(manifest.get("fixture") is False,"training source is a fixture or lacks provenance")
                require(manifest.get("counts",{}).get("test",0)>=2000 and manifest.get("counts",{}).get("dev",0)>=2000,"independent held-out split missing")
                requested=train["config"]["train_size"]
                expected=manifest["counts"]["train"] if requested=="all" else requested
                require(train.get("selected_positive_examples")==expected,"partial training input pool")
                training_seeds.add(train["seed"])
            require(training_seeds=={42,43,44},"training evidence for three seeds missing")
    require(summary.get("heldout_test_score_files"),"independent xLAM held-out test not evaluated")
    for rel in summary["heldout_test_score_files"]:
        score=json.loads((ROOT/rel).read_text())
        require(score.get("smoke") is False and score.get("data_manifest",{}).get("fixture") is False,"nonformal held-out evidence")
        require(score.get("heldout_test",{}).get("n",0)>=2000,"held-out sample incomplete")
    for name in ["README.md","docs/baselines.md","docs/cost.md"]:require((ROOT/name).stat().st_size>100,f"missing documentation {name}")
    print("E2 formal completion verified")

try:verify()
except (ValueError,KeyError,OSError,json.JSONDecodeError) as error:
    print(f"E2 NOT COMPLETE: {error}",file=sys.stderr)
    sys.exit(1)
