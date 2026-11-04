#!/usr/bin/env python3
"""Collect portable evidence from a persistent run directory; exclude checkpoints."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

def collect(source,destination):
    source=source.resolve();destination=destination.resolve()
    destination.mkdir(parents=True,exist_ok=True)
    raw_dir=destination/"raw";raw_dir.mkdir(exist_ok=True)
    for path in sorted(source.glob("*.score.json")):
        score=json.loads(path.read_text())
        raw=Path(score["predictions"]).resolve()
        if not raw.is_relative_to(source):raise ValueError("Prediction path escapes persistent run directory")
        if hashlib.sha256(raw.read_bytes()).hexdigest()!=score["predictions_sha256"]:raise ValueError("Raw prediction checksum mismatch")
        shutil.copy2(raw,raw_dir/raw.name)
        score["original_prediction_location"]=str(raw)
        # CLI runs from the repo root; the standard destination is results/.
        score["predictions"]=str(Path("results")/"raw"/raw.name)
        (destination/path.name).write_text(json.dumps(score,indent=2)+"\n")
        details=path.with_suffix(".details.jsonl")
        shutil.copy2(details,destination/details.name)
    for path in source.glob("*/train.json"):
        shutil.copy2(path,destination/(path.parent.name+".train.json"))
    archive=destination/"collected-results.tar.gz"
    with tarfile.open(archive,"w:gz") as tar:
        for path in sorted(destination.rglob("*")):
            if path.is_file() and path!=archive:
                tar.add(path,arcname=str(Path("results")/path.relative_to(destination)))
    print(f"Portable evidence: {archive}")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path);parser.add_argument("--destination",type=Path,default=Path("results"))
    args=parser.parse_args();collect(args.source,args.destination)
