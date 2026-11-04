#!/usr/bin/env python3
"""Copy a prepared Drive dataset to local runtime storage, checking every byte."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

p=argparse.ArgumentParser(description=__doc__)
p.add_argument("source",type=Path)
p.add_argument("destination",type=Path)
args=p.parse_args()
if args.source.resolve()==args.destination.resolve():raise SystemExit("source and destination must differ")
args.destination.mkdir(parents=True,exist_ok=True)
manifest=json.loads((args.source/"manifest.json").read_text())
for name in ["train.jsonl","dev.jsonl","test.jsonl","manifest.json"]:
    source=args.source/name;target=args.destination/name
    if not source.is_file() or source.is_symlink():raise SystemExit(f"missing/invalid source: {name}")
    temporary=target.with_suffix(target.suffix+".staging")
    shutil.copyfile(source,temporary)
    def digest(path):
        with path.open("rb") as handle:
            hasher=hashlib.sha256()
            for chunk in iter(lambda:handle.read(1024*1024),b""):hasher.update(chunk)
            return hasher.hexdigest()
    if digest(source)!=digest(temporary):raise SystemExit(f"copy checksum mismatch: {name}")
    temporary.replace(target)
    if name.endswith("jsonl"):
        with target.open() as handle:count=sum(bool(line.strip()) for line in handle)
        if count!=manifest["counts"][name.removesuffix(".jsonl")]:raise SystemExit(f"record count mismatch: {name}")
print(json.dumps({"staged":str(args.destination),"source":manifest["source"],"counts":manifest["counts"]}))
