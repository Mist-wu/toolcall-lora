#!/usr/bin/env python3
"""Run one controlled E2 campaign phase inside an already-owned Colab session."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import os

def run(*args):
    subprocess.run([sys.executable,"-m","toolcall_lora.cli",*map(str,args)],check=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage",choices=["baselines","train"],required=True)
    p.add_argument("--data",default="data/xlam")
    p.add_argument("--artifacts",required=True,help="Persistent Drive run directory")
    p.add_argument("--run",default="main",help="matrix configuration without seed suffix, or all")
    p.add_argument("--seeds",nargs="+",type=int,default=[42,43,44])
    p.add_argument("--profile",choices=["l4","t4","a100"],default="l4")
    p.add_argument("--backend",choices=["transformers","vllm"],default="transformers")
    args=p.parse_args()
    persistent=Path(args.artifacts);persistent.mkdir(parents=True,exist_ok=True)
    local=Path("results");local.mkdir(exist_ok=True)
    bfcl=Path("data/bfcl/evaluation.jsonl")
    if not bfcl.exists():run("prepare-bfcl")
    def evaluate(model,label,seed=None,adapter=None):
        suffix=label+(f"-seed{seed}" if seed is not None else "")
        for dataset,name in [(bfcl,"bfcl"),(Path(args.data)/"test.jsonl","heldout")]:
            predictions=persistent/f"{suffix}-{name}.predictions.jsonl"
            score=persistent/f"{suffix}-{name}.score.json"
            call=["predict","--data",dataset,"--model",model,"--output",predictions,"--backend",args.backend,"--profile",args.profile,"--batch-size",2 if args.profile=="t4" else 4]
            if adapter:call += ["--adapter",adapter]
            # Explicit command reruns are deterministic, rather than trusting partial output files.
            run(*call)
            call=["score","--data",dataset,"--predictions",predictions,"--output",score,"--label",label]
            if seed is not None:call += ["--seed",seed]
            run(*call)
            shutil.copy2(score,local/score.name)
            shutil.copy2(score.with_suffix(".details.jsonl"),local/score.with_suffix(".details.jsonl").name)
    if args.stage=="baselines":
        for size in ["1.5","7"]:evaluate(f"Qwen/Qwen2.5-{size}B-Instruct",f"baseline-{size}b")
    else:
        run("matrix")
        matrix=json.loads(Path("configs/matrix/matrix.json").read_text())
        selected=[r for r in matrix if r["seed"] in args.seeds and (args.run=="all" or r["run"].rsplit("-seed",1)[0]==args.run)]
        if not selected:raise ValueError("No selected configurations")
        for item in selected:
            cfg=json.loads(Path(item["config"]).read_text())
            dest=persistent/item["run"]
            complete=dest/"train.json"
            if complete.exists():
                old=json.loads(complete.read_text())
                expected={**cfg,"device_profile":args.profile,"smoke":False}
                if old.get("status")!="train_complete" or old.get("config")!=expected:
                    raise ValueError(f"Incompatible existing training record: {complete}")
            else:
                candidates=list((dest/"checkpoints").glob("checkpoint-*"))
                checkpoints=sorted((path for path in candidates if (path/"complete.json").is_file()),key=lambda path:int(path.name.split("-")[-1]))
                if candidates and not checkpoints:raise ValueError("Only partially written checkpoints exist; inspect before restarting")
                call=["train","--config",item["config"],"--data",args.data,"--output",dest,"--profile",args.profile]
                if checkpoints:call += ["--resume",checkpoints[-1]]
                run(*call)
            shutil.copy2(complete,local/f"{item['run']}.train.json")
            for name in ["train.json", "request.json", "env.txt"]:
                shutil.copy2(dest / name, dest / "adapter" / name)
            subprocess.run([sys.executable,"-m","exp_common.checkpoint","--source",str(dest/"adapter"),"--experiment","E2","--run-id",os.environ.get("EXPERIMENT_RUN_ID","E2-main")+"-"+item["run"]+"-adapter","--receipt",str(local/f"{item['run']}.adapter-receipt.json")],check=True)
            evaluate(cfg["model"],cfg["run_name"],cfg["seed"],dest/"adapter")
    subprocess.run([sys.executable,"scripts/collect_results.py",str(persistent)],check=True)
    run("report")

if __name__=="__main__":main()
