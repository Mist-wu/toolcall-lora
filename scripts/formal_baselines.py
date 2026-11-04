#!/usr/bin/env python3
"""Run both full official BFCL baselines on the already assigned GPU."""
import json
import os
from pathlib import Path
import subprocess
import sys
from toolcall_lora.data import read_jsonl

def run(*args):subprocess.run([sys.executable,"-m","toolcall_lora.cli",*map(str,args)],check=True)

root=Path("results/formal-baselines");root.mkdir(parents=True,exist_ok=True)
glaive=Path("/content/data/e2-glaive")
data_process=None
if not (glaive/"manifest.json").exists():
    data_log=(root/"data-preparation.log").open("w")
    data_process=subprocess.Popen([sys.executable,"-m","toolcall_lora.cli","prepare-glaive","--output",str(glaive)],stdout=data_log,stderr=subprocess.STDOUT)
data=root/"bfcl.jsonl"
run("prepare-bfcl","--output",data)
for size,batch in [("1.5",8),("7",2)]:
    label=f"baseline-{size}b"
    output=root/label;output.mkdir(exist_ok=True)
    predictions=output/"predictions.jsonl"
    score=output/"bfcl.score.json"
    print(f"Starting formal {label}: full {len(read_jsonl(data))} BFCL cases",flush=True)
    run("predict","--data",data,"--model",f"Qwen/Qwen2.5-{size}B-Instruct","--output",predictions,"--batch-size",batch,"--max-new-tokens","512")
    run("score","--data",data,"--predictions",predictions,"--output",score,"--label",label)
    # The root operator provides rclone configuration through the private environment.
    private_environment=Path("/content/experiment-env.json")
    if private_environment.is_file():
        settings=json.loads(private_environment.read_text())
        for name in ["RCLONE_CONFIG","RCLONE_HEADER"]:
            if name in settings:os.environ[name]=settings[name]
    if os.environ.get("RCLONE_CONFIG"):
        subprocess.run([sys.executable,"-m","exp_common.checkpoint","--source",str(output),"--experiment","E2","--run-id",os.environ.get("EXPERIMENT_RUN_ID","E2-formal-baselines")+"-"+label,"--receipt",str(root/(label+".drive-receipt.json"))],check=True)
    print(f"Completed formal {label}",flush=True)
data_returncode=data_process.wait() if data_process else 0
(root/"status.json").write_text(json.dumps({"status":"baselines_complete","models":["Qwen/Qwen2.5-1.5B-Instruct","Qwen/Qwen2.5-7B-Instruct"],"cases_per_model":len(read_jsonl(data)),"formal":True,"training_data_source":"glaiveai/glaive-function-calling-v2","data_preparation_returncode":data_returncode,"training_data_path":str(glaive)},indent=2)+"\n")
