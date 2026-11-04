"""Verified persistence hook for an immutable, fully written Trainer checkpoint."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess


def atomic_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+".tmp")
    with temporary.open("w") as handle:
        json.dump(value,handle,indent=2);handle.write("\n");handle.flush();os.fsync(handle.fileno())
    temporary.replace(path)


def persist_checkpoint(checkpoint, run_directory, hook=None):
    """Require hook exit 0 and a matching verified receipt; never delete source."""
    checkpoint=Path(checkpoint).resolve();run_directory=Path(run_directory).resolve()
    marker=json.loads((checkpoint/"complete.json").read_text())
    checkpoint_id=marker["checkpoint_id"]
    receipt=run_directory/"checkpoint-receipts"/(checkpoint_id+".json")
    last_verified=run_directory/"last-verified-checkpoint.json"
    configured=hook if hook is not None else os.environ.get("EXP_CHECKPOINT_SYNC")
    if not configured:raise RuntimeError("EXP_CHECKPOINT_SYNC is required for durable checkpoint copies")
    try:argv=json.loads(configured)
    except json.JSONDecodeError:raise ValueError("EXP_CHECKPOINT_SYNC must be a JSON argv array") from None
    if not isinstance(argv,list) or not argv or not all(isinstance(x,str) and x for x in argv):
        raise ValueError("EXP_CHECKPOINT_SYNC must be a nonempty string argv array")
    values={"source":str(checkpoint),"run_id":checkpoint_id,"receipt":str(receipt),"experiment":"E2"}
    try:command=[arg.format_map(values) for arg in argv]
    except (KeyError,ValueError):raise ValueError("Unsupported checkpoint hook placeholder") from None
    def verified(record):
        return record.get("state")=="verified" and record.get("run_id")==checkpoint_id and record.get("experiment")=="E2" and Path(record.get("source","")).resolve()==checkpoint
    if receipt.is_file():
        previous=json.loads(receipt.read_text())
        if verified(previous) and previous.get("hook_exit_code")==0:
            atomic_json(last_verified,previous)
            return previous
    receipt.parent.mkdir(parents=True,exist_ok=True)
    print(f"Persisting checkpoint {checkpoint_id}",flush=True)
    try:
        result=subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=1900)
    except (OSError,subprocess.SubprocessError):
        raise RuntimeError("Checkpoint persistence failed; source and previous verified copy retained") from None
    if result.returncode:
        raise RuntimeError("Checkpoint persistence failed; source and previous verified copy retained")
    try:record=json.loads(receipt.read_text())
    except (OSError,json.JSONDecodeError):raise RuntimeError("Checkpoint hook returned no valid receipt") from None
    if not verified(record):raise RuntimeError("Checkpoint hook receipt does not match this source and checkpoint ID")
    record["hook_exit_code"]=0
    atomic_json(receipt,record)
    atomic_json(last_verified,record)
    print(f"Verified checkpoint {checkpoint_id}",flush=True)
    return record
