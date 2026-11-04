"""Opt-in network tokenizer check: E2_TOKENIZER_TEST=1 python -m unittest ..."""
import os
import unittest
from toolcall_lora.data import encode_supervised


@unittest.skipUnless(os.environ.get("E2_TOKENIZER_TEST")=="1","requires explicit tokenizer download")
class RealTokenizerTest(unittest.TestCase):
    def test_qwen_native_template_and_assistant_mask(self):
        from transformers import AutoTokenizer
        tokenizer=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
        row={"id":"probe","query":"What is 2 plus 3?","tools":[{"name":"calculator","description":"Add numbers","parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"]}}],"calls":[{"name":"calculator","arguments":{"a":2,"b":3}}]}
        encoded=encode_supervised(tokenizer,row)
        supervised=tokenizer.decode([v for v in encoded["labels"] if v!=-100])
        self.assertIn("<tool_call>",supervised)
        self.assertIn('"calculator"',supervised)
        self.assertNotIn("# Tools",supervised)
        self.assertTrue(supervised.endswith("<|im_end|>\n"))


if __name__=="__main__":unittest.main()
