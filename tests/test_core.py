import json
import unittest
from toolcall_lora.tool_format import parse_tool_calls, render_tool_calls, normalize_tools, chat_messages
from toolcall_lora.data import split_rows, convert_xlam, convert_glaive, add_negatives, encode_supervised, query_key
from toolcall_lora.evaluate import bootstrap_accuracy, error_labels, exact_calls, paired_case_ci95, score_all


def sample(i):
    return {"id": str(i), "query": f"Question {i}", "tools": [{"name":f"tool_{i}","parameters":{"type":"object","properties":{"x":{"type":"integer"}}}}], "calls": [{"name":f"tool_{i}","arguments":{"x":i}}]}


class FormatTests(unittest.TestCase):
    def test_round_trip_parallel(self):
        calls=[{"name":"math.sum","arguments":{"x":[1,2],"note":"中文"}},{"name":"fetch","arguments":{}}]
        self.assertEqual(parse_tool_calls(render_tool_calls(calls)),calls)

    def test_malformed_rejected(self):
        for text in ['<tool_call>{}</tool_call>','<tool_call>{"name":"x","arguments":{}}','</tool_call>', '<tool_call>{"name":"x","arguments":"{}"}</tool_call>', '<tool_call>{"name":"x","arguments":{"x":1,"x":2}}</tool_call>', '<tool_call>{"name":"x","arguments":{"x":NaN}}</tool_call>']:
            with self.subTest(text=text), self.assertRaises(ValueError): parse_tool_calls(text)

    def test_ordinary_prose_is_no_call(self):
        self.assertEqual(parse_tool_calls("I cannot use these tools."),[])

    def test_normalizes_without_mutation(self):
        original=[{"name":"f","parameters":{"type":"dict","properties":{"a":{"type":"list","items":{"type":"int"}}}}}]
        tools=normalize_tools(original)
        self.assertEqual(tools[0]["function"]["parameters"]["properties"]["a"]["items"]["type"],"integer")
        self.assertEqual(original[0]["parameters"]["type"],"dict")

    def test_native_assistant(self):
        row=sample(1)
        msgs=chat_messages(row["query"],row["tools"],row["calls"])
        self.assertEqual(msgs[-1]["tool_calls"][0]["function"],row["calls"][0])


class DataTests(unittest.TestCase):
    def test_glaive_only_first_turn_and_safe_literal(self):
        system='SYSTEM: tools - {"name":"f","parameters":{"type":"object","properties":{"x":{"type":"integer"}}}}'
        chat='USER: First question\n\nASSISTANT: <functioncall> {"name": "f", "arguments": \'{"x": 3}\'} <|endoftext|>\nFUNCTION RESPONSE: 3\nUSER: followup\nASSISTANT: ignored'
        row=convert_glaive({"system":system,"chat":chat},3)
        self.assertEqual(row["calls"],[{"name":"f","arguments":{"x":3}}])
        self.assertEqual(row["query"],"First question")
        with self.assertRaises((ValueError,SyntaxError)):
            convert_glaive({"system":system,"chat":"USER: bad\nASSISTANT: <functioncall> __import__('os').system('bad') <|endoftext|>"},4)
    def test_xlam_string_fields(self):
        row=sample(1)
        result=convert_xlam({"id":1,"query":row["query"],"tools":json.dumps(row["tools"]),"answers":json.dumps(row["calls"])})
        self.assertEqual(result["calls"],row["calls"])

    def test_split_deterministic_and_disjoint(self):
        rows=[sample(i) for i in range(100)]
        duplicate={**sample(42),"id":"same-question-other-tools","tools":sample(7)["tools"]}
        rows.append(duplicate)
        a=split_rows(rows,10,10,42)
        b=split_rows(list(reversed(rows)),10,10,42)
        self.assertEqual({k: {r["id"] for r in v} for k,v in a.items()},{k: {r["id"] for r in v} for k,v in b.items()})
        sets=[{query_key(r) for r in part} for part in a.values()]
        self.assertFalse(sets[0]&sets[1] or sets[1]&sets[2] or sets[0]&sets[2])

    def test_negative_donors_train_only(self):
        rows=[sample(i) for i in range(18)]
        result=add_negatives(rows,0.1)
        negative=[r for r in result if r.get("negative")]
        self.assertEqual(len(negative),2)
        for row in negative:
            self.assertEqual(row["calls"],[])
            self.assertIn(row["negative_donor"],{r["id"] for r in rows})

    def test_insufficient_split_raises(self):
        with self.assertRaises(ValueError):split_rows([sample(i) for i in range(3)],2,2)

    def test_conflicting_duplicates_raise(self):
        a=sample(1);b={**a,"calls":[]}
        with self.assertRaises(ValueError):split_rows([a,b]+[sample(i) for i in range(2,9)],1,1)


class MaskTests(unittest.TestCase):
    class Tokenizer:
        def apply_chat_template(self,messages,tools,tokenize,add_generation_prompt):
            prompt="TOOLS="+json.dumps(tools)+"\nUSER="+messages[0]["content"]+"\nASSISTANT\n"
            return prompt if add_generation_prompt else prompt+json.dumps(messages[-1])+"<END>"
        def __call__(self,text,add_special_tokens):return {"input_ids":[ord(c) for c in text]}

    def test_prompt_mask_and_full_target(self):
        encoded=encode_supervised(self.Tokenizer(),sample(1),10000)
        first=next(i for i,x in enumerate(encoded["labels"]) if x!=-100)
        self.assertTrue(all(x==-100 for x in encoded["labels"][:first]))
        self.assertEqual(encoded["labels"][first:],encoded["input_ids"][first:])
        self.assertEqual(encoded["input_ids"][-5:],[ord(c) for c in "<END>"])

    def test_overflow_drops_complete_example(self):
        self.assertIsNone(encode_supervised(self.Tokenizer(),sample(1),20))


class MetricTests(unittest.TestCase):
    def test_order_independent_but_duplicate_sensitive(self):
        a=sample(1)["calls"][0];b=sample(2)["calls"][0]
        self.assertTrue(exact_calls([a,b],[b,a]))
        self.assertFalse(exact_calls([a,a,b],[a,b]))

    def test_json_types_not_python_equal(self):
        self.assertFalse(exact_calls([{"name":"f","arguments":{"x":True}}],[{"name":"f","arguments":{"x":1}}]))

    def test_ground_truth_selftest_100(self):
        rows=[sample(i) for i in range(10)]
        details, summary=score_all(rows,[{"id":r["id"],"text":render_tool_calls(r["calls"])} for r in rows])
        self.assertEqual(summary["overall_subset"]["accuracy"],1)
        self.assertEqual(summary["overall_subset"]["ci95"],[1,1])

    def test_missing_prediction_not_silently_dropped(self):
        with self.assertRaises(ValueError):score_all([sample(1),sample(2)],[{"id":"1","text":"none"}])

    def test_false_call_error(self):
        self.assertEqual(error_labels([],sample(1)["calls"]),["false_call"])

    def test_duplicate_ids_rejected_on_both_sides(self):
        row=sample(1)
        with self.assertRaises(ValueError):
            score_all([row,dict(row)],[{"id":"1","text":""}])
        with self.assertRaises(ValueError):
            score_all([row],[{"id":"1","text":""},{"id":"1","text":"other"}])
        with self.assertRaises(ValueError):
            score_all([row,sample(2)],[{"id":"1","text":""}])

    def test_two_published_bootstrap_conventions(self):
        values = [0] * 5 + [1] * 3
        result = bootstrap_accuracy(values)
        self.assertEqual(result["ci95_indices"], [24, 974])
        self.assertEqual(result["ci95"], [0, 0.75])
        self.assertEqual(paired_case_ci95(values), [0.125, 0.75])


if __name__=="__main__":unittest.main()
