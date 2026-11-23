"""Verified persistence hook for an immutable, fully written Trainer checkpoint."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess


IDENTITY_FIELDS = (
    "run_name", "model", "model_revision", "train_size", "data_seed", "seed",
    "lora_rank", "lora_alpha", "negative_fraction", "max_length", "epochs",
)
RESUME_FILES = ("adapter_model.safetensors", "optimizer.pt", "scheduler.pt", "trainer_state.json")
RNG_FILE = "rng_state.pth"


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def read_json(path, label):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unreadable {label}: {path}") from error


def training_identity(config):
    if not isinstance(config, dict):
        raise ValueError("Training configuration must be an object")
    return {field: config.get(field) for field in IDENTITY_FIELDS}


def safe_name(value):
    if not isinstance(value, str) or value in {"", ".", ".."}:
        return False
    path = Path(value)
    return path.name == value and not path.is_absolute()


def hook_argv(hook=None):
    configured = hook if hook is not None else os.environ.get("EXP_CHECKPOINT_SYNC")
    if not configured:
        raise RuntimeError("EXP_CHECKPOINT_SYNC is required for durable checkpoint copies")
    try:
        argv = json.loads(configured)
    except json.JSONDecodeError:
        raise ValueError("EXP_CHECKPOINT_SYNC must be a JSON argv array") from None
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
        raise ValueError("EXP_CHECKPOINT_SYNC must be a nonempty string argv array")
    return argv


def format_hook(source, run_id, receipt, hook=None):
    values = {"source": str(source), "run_id": str(run_id), "receipt": str(receipt), "experiment": "E2"}
    try:
        return [arg.format_map(values) for arg in hook_argv(hook)]
    except (KeyError, ValueError):
        raise ValueError("Unsupported checkpoint hook placeholder") from None


def require_formal_persistence(hook=None):
    """Refuse to train or upload until the runner hook is the shared persistence interface."""
    import importlib.util
    argv = hook_argv(hook)
    rendered = "\n".join(argv)
    if "exp_common.checkpoint" not in argv:
        raise RuntimeError("Formal persistence must use the injected exp_common.checkpoint hook")
    for placeholder in ("{source}", "{experiment}", "{run_id}", "{receipt}"):
        if placeholder not in rendered:
            raise RuntimeError("Formal checkpoint hook must format source, experiment, run_id, and receipt")
    if importlib.util.find_spec("exp_common.checkpoint") is None:
        raise RuntimeError("exp_common.checkpoint is not importable; refusing to start training or adapter upload")
    return argv


def validate_checkpoint(checkpoint, expected_config):
    """Check request, identity, seed, step, composition, and RNG state before any copy."""
    checkpoint = Path(checkpoint).resolve()
    if not (checkpoint / "complete.json").is_file():
        raise ValueError("Checkpoint lacks a completed-save marker; do not resume a partial write")
    if not (checkpoint / "request.json").is_file():
        raise ValueError("Checkpoint lacks its own request.json")
    request = read_json(checkpoint / "request.json", "checkpoint request")
    marker = read_json(checkpoint / "complete.json", "checkpoint marker")
    if training_identity(request) != training_identity(expected_config):
        raise ValueError("Checkpoint training identity does not match this run")
    if request != expected_config:
        raise ValueError("Checkpoint request does not match this training configuration")
    if marker.get("seed") != expected_config.get("seed") or request.get("seed") != expected_config.get("seed"):
        raise ValueError("Checkpoint seed does not match this training configuration")
    step = marker.get("global_step")
    if isinstance(step, bool) or not isinstance(step, int) or step < 0:
        raise ValueError("Checkpoint global_step is missing or invalid")
    if checkpoint.name.startswith("checkpoint-"):
        suffix = checkpoint.name.rsplit("-", 1)[-1]
        if not suffix.isdigit() or int(suffix) != step:
            raise ValueError("Checkpoint directory step does not match complete.json")
    listed = marker.get("files")
    if not isinstance(listed, list) or not listed or any(not safe_name(name) for name in listed):
        raise ValueError("Checkpoint marker lacks a usable file composition")
    if any(name not in listed for name in RESUME_FILES):
        raise ValueError("Checkpoint composition is missing a resume file")
    required = list(dict.fromkeys([*listed, RNG_FILE, "request.json"]))
    missing = [name for name in required if not (checkpoint / name).is_file()]
    if missing:
        raise ValueError("Checkpoint is missing required resume files: " + ", ".join(missing))
    state = read_json(checkpoint / "trainer_state.json", "trainer state")
    if state.get("global_step") != step:
        raise ValueError("trainer_state.json global_step does not match the checkpoint marker")
    _read_rng_state(checkpoint / RNG_FILE)
    checkpoint_id = marker.get("checkpoint_id")
    if not safe_name(checkpoint_id):
        raise ValueError("Checkpoint marker lacks a single-component checkpoint_id")
    return marker


def _read_rng_state(path):
    try:
        import torch
    except ImportError as error:
        raise RuntimeError("Checkpoint RNG state cannot be restored") from error
    try:
        try:
            state = torch.load(path, map_location="cpu", weights_only=False)
        except TypeError:
            state = torch.load(path, map_location="cpu")
    except Exception as error:
        raise ValueError("Checkpoint RNG state cannot be restored") from error
    if not isinstance(state, dict) or any(key not in state for key in ("python", "numpy", "cpu")):
        raise ValueError("Checkpoint RNG state is incomplete")
    return state


def _verified_receipt(record, checkpoint, checkpoint_id):
    return (
        isinstance(record, dict)
        and record.get("state") == "verified"
        and record.get("run_id") == checkpoint_id
        and record.get("experiment") == "E2"
        and Path(record.get("source", "")).resolve() == checkpoint
    )


def persist_checkpoint(checkpoint, run_directory, hook=None):
    """Require a resumable checkpoint, then hook exit 0 and a matching verified receipt."""
    checkpoint = Path(checkpoint).resolve()
    run_directory = Path(run_directory).resolve()
    request_path = run_directory / "request.json"
    if not request_path.is_file():
        raise ValueError("Cannot persist a checkpoint before the run request is recorded")
    marker = validate_checkpoint(checkpoint, read_json(request_path, "run request"))
    checkpoint_id = marker["checkpoint_id"]
    receipt = run_directory / "checkpoint-receipts" / (checkpoint_id + ".json")
    last_verified = run_directory / "last-verified-checkpoint.json"
    if receipt.is_file():
        try:
            previous = json.loads(receipt.read_text())
        except (OSError, json.JSONDecodeError):
            previous = None
        if _verified_receipt(previous, checkpoint, checkpoint_id) and previous.get("hook_exit_code") == 0:
            atomic_json(last_verified, previous)
            return previous
    command = format_hook(checkpoint, checkpoint_id, receipt, hook)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    print(f"Persisting checkpoint {checkpoint_id}", flush=True)
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1900)
    except (OSError, subprocess.SubprocessError):
        raise RuntimeError("Checkpoint persistence failed; source and previous verified copy retained") from None
    if result.returncode:
        raise RuntimeError("Checkpoint persistence failed; source and previous verified copy retained")
    try:
        record = json.loads(receipt.read_text())
    except (OSError, json.JSONDecodeError):
        raise RuntimeError("Checkpoint hook returned no valid receipt") from None
    if not _verified_receipt(record, checkpoint, checkpoint_id):
        raise RuntimeError("Checkpoint hook receipt does not match this source and checkpoint ID")
    record["hook_exit_code"] = 0
    atomic_json(receipt, record)
    atomic_json(last_verified, record)
    print(f"Verified checkpoint {checkpoint_id}", flush=True)
    return record
