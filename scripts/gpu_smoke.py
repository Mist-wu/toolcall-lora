#!/usr/bin/env python3
"""Actual 1.5B CUDA optimizer, resume, generation and checker smoke, not formal data."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from toolcall_lora.data import read_jsonl,write_jsonl

def run(*args):subprocess.run([sys.executable,"-m","toolcall_lora.cli",*map(str,args)],check=True)

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output",type=Path,default=Path("/content/e2-smoke"))
args=parser.parse_args()
root=args.output;root.mkdir(parents=True,exist_ok=True)
import torch
if not torch.cuda.is_available():raise SystemExit("GPU required for this smoke; use test_training_smoke.py for CPU test")
data=root/"data"
rows=[{"id":f"fixture-{i}","query":f"Add {i} and 1 using add.","tools":[{"name":"add","description":"Add two integers","parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"]}}],"calls":[{"name":"add","arguments":{"a":i,"b":1}}]} for i in range(8)]
write_jsonl(data/"train.jsonl",rows[:4]);write_jsonl(data/"dev.jsonl",rows[4:6]);write_jsonl(data/"test.jsonl",rows[6:])
(data/"manifest.json").write_text(json.dumps({"fixture":True,"source":"synthetic_gpu_smoke","counts":{"train":4,"dev":2,"test":2}}))
cfg=json.loads(Path("configs/main.json").read_text());cfg.update({"negative_fraction":0,"max_length":512,"eval_size":2})
config=root/"smoke-config.json";config.write_text(json.dumps(cfg))
started=time.time()
output=root/"training"
run("train","--config",config,"--data",data,"--output",output,"--smoke")
run("train","--config",config,"--data",data,"--output",output,"--smoke","--resume",output/"checkpoints/checkpoint-1")
official=root/"official.jsonl";run("prepare-bfcl","--output",official)
all_rows=read_jsonl(official)
subset=[next(r for r in all_rows if r["category"]==category) for category in ["simple_python","multiple","parallel","parallel_multiple","irrelevance"]]
evaluation=root/"five-cases.jsonl";write_jsonl(evaluation,subset)
predictions=root/"predictions.jsonl"
run("predict","--data",evaluation,"--model",cfg["model"],"--adapter",output/"adapter","--output",predictions,"--batch-size","1","--max-new-tokens","128")
score=root/"smoke.score.json"
run("score","--data",evaluation,"--predictions",predictions,"--output",score,"--label","gpu-smoke","--seed","42","--smoke")
result=json.loads(score.read_text())
assert result["overall_subset"]["n"]==5 and result["smoke"] is True
assert (output/"checkpoints/checkpoint-1/optimizer.pt").is_file()
receipt={"status":"smoke_complete","formal":False,"gpu":torch.cuda.get_device_name(),"torch":torch.__version__,"cuda":torch.version.cuda,"elapsed_seconds":time.time()-started,"optimizer_steps":2,"checkpoint_resume":True,"official_bfcl_cases":5,"result_path":str(score)}
(root/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
