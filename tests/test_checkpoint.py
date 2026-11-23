import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from toolcall_lora.checkpoint import persist_checkpoint, require_formal_persistence, validate_checkpoint


def write_json(path, value):
    path.write_text(json.dumps(value) + "\n")


def request(seed):
    return {"model": "offline", "seed": seed, "data_seed": 42, "smoke": False}


class CheckpointTests(unittest.TestCase):
    def make_run(self, root, seed=42):
        out = root / "dest"
        out.mkdir()
        write_json(out / "request.json", request(seed))
        return out

    def make_checkpoint(self, root, seed=42, step=7, name="checkpoint-7", files=True):
        checkpoint = root / name
        checkpoint.mkdir()
        write_json(checkpoint / "request.json", request(seed))
        listed = ["adapter_model.safetensors", "optimizer.pt", "scheduler.pt", "trainer_state.json", "rng_state.pth"]
        write_json(checkpoint / "complete.json", {"global_step": step, "files": listed, "seed": seed, "checkpoint_id": "fixture"})
        write_json(checkpoint / "trainer_state.json", {"global_step": step})
        if files:
            for filename in listed:
                if filename != "trainer_state.json":
                    (checkpoint / filename).write_bytes(b"")
        return checkpoint

    def test_foreign_checkpoint_rejected_before_hook(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = self.make_run(root, 42)
            checkpoint = self.make_checkpoint(root, seed=44, name="foreign", files=False)
            ran = root / "hook-ran"
            hook = json.dumps([sys.executable, "-c", f"open({str(ran)!r},'w').write('ran')"])
            with self.assertRaises(ValueError):
                validate_checkpoint(checkpoint, request(42))
            with self.assertRaises(ValueError):
                persist_checkpoint(checkpoint, out, hook=hook)
            self.assertFalse(ran.exists())
            self.assertFalse((out / "last-verified-checkpoint.json").exists())

    def test_stale_receipt_is_not_reused_for_incomplete_checkpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = self.make_run(root, 42)
            checkpoint = self.make_checkpoint(root, files=False)
            receipt = out / "checkpoint-receipts" / "fixture.json"
            receipt.parent.mkdir(parents=True)
            write_json(receipt, {"state": "verified", "experiment": "E2", "run_id": "fixture", "source": str(checkpoint.resolve()), "hook_exit_code": 0})
            with self.assertRaises(ValueError):
                persist_checkpoint(checkpoint, out, hook=json.dumps([sys.executable, "-c", "raise SystemExit(0)"]))
            self.assertFalse((out / "last-verified-checkpoint.json").exists())

    def test_directory_step_and_trainer_state_must_agree(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = self.make_checkpoint(root, step=7, name="checkpoint-3", files=False)
            with self.assertRaises(ValueError) as caught:
                validate_checkpoint(checkpoint, request(42))
            self.assertIn("step", str(caught.exception))
            checkpoint = self.make_checkpoint(root, step=7, name="checkpoint-7", files=True)
            write_json(checkpoint / "trainer_state.json", {"global_step": 6})
            with self.assertRaises(ValueError) as caught:
                validate_checkpoint(checkpoint, request(42))
            self.assertIn("trainer_state", str(caught.exception))

    def test_formal_hook_is_rejected_before_use(self):
        with patch.dict(os.environ, {"EXP_CHECKPOINT_SYNC": json.dumps(["offline"])}):
            with self.assertRaises(RuntimeError):
                require_formal_persistence()
        argv = [sys.executable, "-m", "exp_common.checkpoint", "--source", "{source}", "--experiment", "{experiment}", "--run-id", "{run_id}", "--receipt", "{receipt}"]
        with patch.dict(os.environ, {"EXP_CHECKPOINT_SYNC": json.dumps(argv)}), patch("importlib.util.find_spec", return_value=None):
            with self.assertRaises(RuntimeError) as caught:
                require_formal_persistence()
        self.assertIn("not importable", str(caught.exception))
        with patch.dict(os.environ, {"EXP_CHECKPOINT_SYNC": json.dumps(argv)}), patch("importlib.util.find_spec", return_value=object()):
            self.assertEqual(require_formal_persistence(), argv)

    @unittest.skipUnless(importlib.util.find_spec("torch"), "torch is required to build a restorable RNG state")
    def test_complete_checkpoint_receipt_can_be_reused(self):
        import torch
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = self.make_run(root, 42)
            checkpoint = self.make_checkpoint(root, files=True)
            torch.save({"python": (1,), "numpy": (2,), "cpu": torch.zeros(1, dtype=torch.uint8)}, checkpoint / "rng_state.pth")
            hook = root / "hook.py"
            hook.write_text(
                "import json,sys\nfrom pathlib import Path\n"
                "source,run_id,receipt=sys.argv[1:4]\n"
                "Path(receipt).write_text(json.dumps({'state':'verified','experiment':'E2','run_id':run_id,'source':source}))\n"
            )
            command = json.dumps([sys.executable, str(hook), "{source}", "{run_id}", "{receipt}"])
            record = persist_checkpoint(checkpoint, out, hook=command)
            self.assertEqual(record["state"], "verified")
            self.assertEqual(record["hook_exit_code"], 0)
            hook.write_text("raise SystemExit(8)\n")
            reused = persist_checkpoint(checkpoint, out, hook=command)
            self.assertEqual(reused["state"], "verified")
            self.assertEqual(reused["hook_exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
