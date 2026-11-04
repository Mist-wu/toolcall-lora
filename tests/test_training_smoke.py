"""Explicit tiny random-weight CPU training test; never an experiment result."""
import json
import os
from pathlib import Path
import tempfile
import unittest


@unittest.skipUnless(os.environ.get("E2_TRAINING_TEST")=="1","requires optional training dependencies and tokenizer download")
class TinyTrainingTest(unittest.TestCase):
    def test_lora_optimizer_checkpoint_and_resume(self):
        import torch
        from transformers import AutoTokenizer, Qwen2Config, Qwen2ForCausalLM
        from toolcall_lora.data import write_jsonl
        from toolcall_lora.runtime import train
        torch.set_num_threads(1)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);model_path=root/"tiny-model"
            tokenizer=AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct",revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
            tokenizer.save_pretrained(model_path)
            tiny=Qwen2ForCausalLM(Qwen2Config(vocab_size=len(tokenizer),hidden_size=16,intermediate_size=32,num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,max_position_embeddings=2048,tie_word_embeddings=True,bos_token_id=tokenizer.bos_token_id,eos_token_id=tokenizer.eos_token_id))
            tiny.save_pretrained(model_path)
            rows=[{"id":str(i),"query":f"Add {i} and 1","tools":[{"name":"add","parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"]}}],"calls":[{"name":"add","arguments":{"a":i,"b":1}}]} for i in range(4)]
            data=root/"data"
            write_jsonl(data/"train.jsonl",rows)
            write_jsonl(data/"dev.jsonl",rows[:2])
            cfg={"model":str(model_path),"train_size":"all","seed":42,"data_seed":42,"lora_rank":4,"lora_alpha":8,"negative_fraction":0,"max_length":1024,"epochs":1,"device_profile":"l4"}
            output=root/"run"
            first=train(cfg,data,output,smoke=True)
            self.assertEqual(first["status"],"smoke_complete")
            self.assertTrue((output/"adapter"/"adapter_model.safetensors").is_file())
            checkpoint=output/"checkpoints"/"checkpoint-1"
            self.assertTrue((checkpoint/"optimizer.pt").is_file())
            second=train(cfg,data,output,resume=str(checkpoint),smoke=True)
            self.assertEqual(second["status"],"smoke_complete")
            self.assertEqual(json.loads((output/"checkpoints"/"checkpoint-2"/"trainer_state.json").read_text())["global_step"],2)


if __name__=="__main__":unittest.main()
