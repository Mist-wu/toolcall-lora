"""Opt-in offline checks using data bundled with pinned bfcl-eval."""
import importlib.util
import unittest
from pathlib import Path
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


if __name__=="__main__":unittest.main()
