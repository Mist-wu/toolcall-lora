"""Command-line entrypoint for reproducible data, training, evaluation and reporting."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import statistics
from collections import Counter
import sys
from .data import convert_xlam, convert_glaive, read_jsonl, write_jsonl, split_rows

XLAM_REVISION = "26d14ebfe18b1f7b524bd39b404b50af5dc97866"
GLAIVE_REVISION = "e7f4b6456019f5d8bcb991ef0dd67d8ff23221ac"
CATEGORIES = ["simple_python", "multiple", "parallel", "parallel_multiple", "irrelevance"]


def prepare(args):
    if args.input:
        source = Path(args.input)
    else:
        from huggingface_hub import hf_hub_download
        source = Path(hf_hub_download(repo_id="Salesforce/xlam-function-calling-60k", repo_type="dataset", filename="xlam_function_calling_60k.json", revision=XLAM_REVISION))
    raw = json.loads(source.read_text())
    rows = [convert_xlam(r) for r in raw]
    parts = split_rows(rows, args.dev_size, args.test_size, args.seed)
    root = Path(args.output)
    for name, data in parts.items(): write_jsonl(root / f"{name}.jsonl", data)
    manifest = {"source": "Salesforce/xlam-function-calling-60k", "revision": XLAM_REVISION, "license": "CC-BY-4.0", "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "source_rows": len(raw), "split_seed": args.seed, "counts": {k:len(v) for k,v in parts.items()}, "split_policy": "normalized query groups; exact query+tools dedup; train/dev/test disjoint", "train_size_all": len(parts["train"]), "fixture": False, "source_is_model_generated": True}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


def prepare_glaive(args):
    from datasets import load_dataset
    dataset = load_dataset("glaiveai/glaive-function-calling-v2", revision=GLAIVE_REVISION, split="train", streaming=True)
    rows=[];skipped=0;seen=set()
    for index, row in enumerate(dataset):
        try: converted=convert_glaive(row,index)
        except (ValueError,KeyError,TypeError,SyntaxError):
            skipped+=1
            continue
        identity=(converted["query"].casefold().strip(),json.dumps(converted["tools"],sort_keys=True))
        if identity in seen:continue
        seen.add(identity);rows.append(converted)
        if len(rows)>=args.max_examples:break
    parts=split_rows(rows,args.dev_size,args.test_size,args.seed)
    root=Path(args.output)
    for name,data in parts.items():write_jsonl(root/f"{name}.jsonl",data)
    manifest={"source":"glaiveai/glaive-function-calling-v2","revision":GLAIVE_REVISION,"license":"Apache-2.0","source_rows_used":len(rows),"skipped_unsupported_or_no_first_call":skipped,"counts":{k:len(v) for k,v in parts.items()},"split_seed":args.seed,"split_policy":"first turn only; normalized query grouped; distinct dev/test; no follow-up flattening","fixture":False, "source_is_model_generated":True,"fallback_reason":"xLAM gated; scores not claimed to reproduce xLAM training"}
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


def prepare_bfcl(args):
    import bfcl_eval
    from .tool_format import normalize_tools
    data_dir = Path(bfcl_eval.__file__).parent / "data"
    rows = []
    hashes = {}
    for cat in CATEGORIES:
        source = data_dir / f"BFCL_v4_{cat}.json"
        answer_path = data_dir / "possible_answer" / source.name
        inputs = read_jsonl(source)
        answers = {r["id"]:r["ground_truth"] for r in read_jsonl(answer_path)} if answer_path.exists() else {}
        hashes[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
        if answer_path.exists(): hashes["possible_answer/" + source.name] = hashlib.sha256(answer_path.read_bytes()).hexdigest()
        for row in inputs:
            if len(row["question"]) != 1: raise ValueError("Expected single-turn BFCL category")
            if cat != "irrelevance" and row["id"] not in answers: raise ValueError("Missing official ground truth")
            messages = row["question"][0]
            rows.append({"id":row["id"], "benchmark":"bfcl", "category":cat, "messages":messages, "query":messages[-1]["content"], "tools":normalize_tools(row["function"]), "function":row["function"], "ground_truth":answers.get(row["id"],[])})
    write_jsonl(args.output, rows)
    Path(str(args.output) + ".manifest.json").write_text(json.dumps({"bfcl_version":importlib.metadata.version("bfcl-eval"), "categories":CATEGORIES, "rows":len(rows), "files_sha256":hashes, "metric_boundary":"Official AST checker on five single-turn categories with custom strict Qwen parser; not overall leaderboard score", "fixture":False}, indent=2) + "\n")
    print(f"Prepared {len(rows)} official BFCL cases")


def run_train(args):
    from .runtime import train, load_config
    cfg = load_config(args.config)
    if args.seed is not None: cfg["seed"] = args.seed
    if args.profile: cfg["device_profile"] = args.profile
    print(json.dumps(train(cfg, args.data, args.output, args.resume), indent=2))


def run_predict(args):
    from .runtime import predict
    rows = read_jsonl(args.data)
    if args.limit: rows = rows[:args.limit]
    print(json.dumps(predict(rows,args.model,args.output,args.adapter,args.batch_size,args.max_new_tokens,args.backend,args.profile,args.revision), indent=2))


def score(args):
    from .evaluate import score_all
    data, predictions = read_jsonl(args.data), read_jsonl(args.predictions)
    scored, summary = score_all(data, predictions)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out.with_suffix(".details.jsonl"), scored)
    meta_path = Path(str(args.predictions) + ".metadata.json")
    manifest_path = Path(str(args.data) + ".manifest.json")
    if not manifest_path.exists(): manifest_path = Path(args.data).parent / "manifest.json"
    summary.update({"schema_version":1, "dataset":str(args.data), "dataset_sha256":hashlib.sha256(Path(args.data).read_bytes()).hexdigest(), "data_manifest": json.loads(manifest_path.read_text()) if manifest_path.exists() else {"fixture":True,"reason":"missing data manifest"}, "predictions":str(args.predictions), "predictions_sha256":hashlib.sha256(Path(args.predictions).read_bytes()).hexdigest(), "inference":json.loads(meta_path.read_text()) if meta_path.exists() else {}, "label":args.label, "seed":args.seed, "smoke":args.smoke})
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


def matrix(args):
    base = json.loads(Path(args.base).read_text())
    rows = []
    combinations = [("main", "all",16,0.1)]
    combinations += [(f"n10000-r{rank}-neg{int(neg*100)}",10000,rank,neg) for rank in [8,16,64] for neg in [0,0.1]]
    combinations += [("n30000-r16-neg10",30000,16,0.1)]
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    for name, size, rank, neg in combinations:
        for seed in [42,43,44]:
            cfg = {**base,"run_name":name,"train_size":size,"lora_rank":rank,"lora_alpha":2*rank,"negative_fraction":neg,"seed":seed}
            path = out / f"{name}-seed{seed}.json"
            path.write_text(json.dumps(cfg, indent=2) + "\n")
            rows.append({"run":path.stem,"config":str(path),"seed":seed,"train_size":size,"rank":rank,"negative_fraction":neg})
    (out / "matrix.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(f"Wrote {len(rows)} configurations; no training launched")


def report(args):
    paths = sorted(Path(args.input).glob("*.score.json"))
    paths += sorted(Path(args.input).glob("formal-baselines/baseline-*/bfcl.score.json"))
    records = [json.loads(p.read_text()) for p in paths]
    if not records: raise ValueError("No *.score.json files found")
    groups = {}
    for record in records:
        dataset = "BFCL five-category subset" if "simple_python" in record else "held-out tool calls"
        groups.setdefault((record["label"], dataset), []).append(record)
    lines = ["# E2 results", "", "Measured results only. BFCL columns cover the five selected single-turn categories, not the full leaderboard.", "", "| Configuration | Dataset | Runs | Accuracy mean | Sample SD |", "|---|---|---:|---:|---:|"]
    for (name,dataset), group in groups.items():
        values = [r["overall_subset"]["accuracy"] for r in group]
        sd = f"{statistics.stdev(values):.4f}" if len(values)>1 else "not applicable"
        lines.append(f"| {name} | {dataset} | {len(values)} | {statistics.mean(values):.4f} | {sd} |")
    lines += ["", "Main training uses seeds 42/43/44. Single-seed ablations are exploratory and do not establish stable gains. Confirmatory contrasts must be selected using development data before adding seeds 43/44; test scores are not a selection criterion.", "", "## Error counts", "", "Held-out JSON errors use explicit semantic categories; BFCL keeps the official error_type rather than inventing equivalent labels.", "", "| Configuration | Dataset | Error | Count |", "|---|---|---|---:|"]
    for path,record in zip(paths,records):
        details=path.with_suffix(".details.jsonl")
        if not details.exists():continue
        counts=Counter()
        for row in read_jsonl(details):
            if row["valid"]:continue
            if "official_error_type" in row:
                counts[row["official_error_type"] or "official_unspecified_error"]+=1
            else:
                for error in row["errors"]:counts[error]+=1
        dataset="BFCL" if "simple_python" in record else "heldout"
        for error,count in sorted(counts.items()):
            lines.append(f"| {record['label']} / seed {record['seed']} | {dataset} | {error} | {count} |")
    out = Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print(str(out))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p=sub.add_parser("prepare");p.add_argument("--input");p.add_argument("--output",default="data/xlam");p.add_argument("--dev-size",type=int,default=2000);p.add_argument("--test-size",type=int,default=2000);p.add_argument("--seed",type=int,default=42);p.set_defaults(run=prepare)
    p=sub.add_parser("prepare-glaive");p.add_argument("--output",default="data/glaive");p.add_argument("--dev-size",type=int,default=2000);p.add_argument("--test-size",type=int,default=2000);p.add_argument("--seed",type=int,default=42);p.add_argument("--max-examples",type=int,default=60000);p.set_defaults(run=prepare_glaive)
    p=sub.add_parser("prepare-bfcl");p.add_argument("--output",default="data/bfcl/evaluation.jsonl");p.set_defaults(run=prepare_bfcl)
    p=sub.add_parser("train");p.add_argument("--config",default="configs/main.json");p.add_argument("--data",default="data/xlam");p.add_argument("--output",required=True);p.add_argument("--seed",type=int);p.add_argument("--profile",choices=["l4","t4","a100"]);p.add_argument("--resume");p.set_defaults(run=run_train)
    p=sub.add_parser("predict");p.add_argument("--data",required=True);p.add_argument("--model",default="Qwen/Qwen2.5-1.5B-Instruct");p.add_argument("--revision");p.add_argument("--adapter");p.add_argument("--output",required=True);p.add_argument("--backend",choices=["transformers","vllm"],default="transformers");p.add_argument("--profile",choices=["l4","t4","a100"],default="l4");p.add_argument("--batch-size",type=int,default=4);p.add_argument("--max-new-tokens",type=int,default=512);p.add_argument("--limit",type=int);p.set_defaults(run=run_predict)
    p=sub.add_parser("score");p.add_argument("--data",required=True);p.add_argument("--predictions",required=True);p.add_argument("--output",required=True);p.add_argument("--label",required=True);p.add_argument("--seed",type=int);p.add_argument("--smoke",action="store_true");p.set_defaults(run=score)
    p=sub.add_parser("matrix");p.add_argument("--base",default="configs/main.json");p.add_argument("--output",default="configs/matrix");p.set_defaults(run=matrix)
    p=sub.add_parser("report");p.add_argument("--input",default="results");p.add_argument("--output",default="results/report.md");p.set_defaults(run=report)
    args=parser.parse_args()
    try: args.run(args)
    except (ValueError,RuntimeError,FileNotFoundError) as error:
        parser.exit(1,f"ERROR: {error}\n")


if __name__ == "__main__": main()
