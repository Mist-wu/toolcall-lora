"""Opt-in offline checks using data bundled with pinned bfcl-eval."""
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from toolcall_lora.data import read_jsonl
from toolcall_lora.evaluate import score_prediction
from toolcall_lora.tool_format import render_tool_calls


@unittest.skipUnless(importlib.util.find_spec("bfcl_eval"),"optional bfcl-eval not installed")
class OfficialBFCLTests(unittest.TestCase):
    def test_first_ground_truth_each_category(self):
        import bfcl_eval
        directory=Path(bfcl_eval.__file__).parent/"data"
        for category in ["simple_python","multiple","parallel","parallel_multiple","irrelevance"]:
            with self.subTest(category=category):
                source=read_jsonl(directory/f"BFCL_v4_{category}.json")[0]
                answer=directory/"possible_answer"/f"BFCL_v4_{category}.json"
                truth=read_jsonl(answer)[0]["ground_truth"] if answer.exists() else []
                calls=[{"name":name,"arguments":{key:values[0] for key,values in arguments.items() if values[0]!=""}} for item in truth for name,arguments in item.items()]
                row={**source,"benchmark":"bfcl","category":category,"ground_truth":truth}
                self.assertTrue(score_prediction(row,render_tool_calls(calls))["valid"])

    def test_foreign_registry_restored_when_checker_raises(self):
        import bfcl_eval.eval_checker.ast_eval.ast_checker as checker
        prior=SimpleNamespace(underscore_to_dot=True)
        checker.MODEL_CONFIG_MAPPING["e2-qwen"]=prior
        row={"id":"fake","benchmark":"bfcl","category":"simple_python","function":[{"name":"demo","parameters":{"type":"dict","properties":{},"required":[]}}],"ground_truth":[{"demo":{}}]}
        def boom(*args,**kwargs):
            raise RuntimeError("checker failed")
        try:
            with patch.object(checker,"ast_checker",boom),self.assertRaises(RuntimeError):
                score_prediction(row,render_tool_calls([{"name":"demo","arguments":{}}]))
            self.assertIs(checker.MODEL_CONFIG_MAPPING.get("e2-qwen"),prior)
        finally:
            if checker.MODEL_CONFIG_MAPPING.get("e2-qwen") is prior:
                checker.MODEL_CONFIG_MAPPING.pop("e2-qwen",None)


if __name__=="__main__":unittest.main()
