# E2 固定 50 条负例：agent 实质审阅

审阅日期：2026-11-05（日本时间）。`reviewer_type=agent`。已完整覆盖固定文件的 50/50 条，每条包含原查询、全部供体工具的原描述和参数、语义判断、理由及具体问题。最终逐项文件为 `agent-review.jsonl`；两个 `review-01-25.jsonl` / `review-26-50.jsonl` 是分段审阅原稿，统计应只读取最终文件一次。

这完成了 agent 审阅，没有冒充真人标注。原文件的 50 个 `human_verdict`、50 个 `human_notes` 仍全部为 null。未修改原仓库、训练、服务器、正式分数，未调用外部 API，未提交 Git。

## 结论与计数

| 对工具选择负标签的判断 | 条数 | 含义 |
|---|---:|---|
| `semantically_irrelevant` | 47 | 按工具声明用途，`calls=[]` 得到支持；不代表只能拒答用户 |
| `related_or_equivalent_tool` | 1 | #27 的可用工具可以直接完成请求，空调用标签错误 |
| `uncertain` | 2 | #10、#40 的百分比工具跨领域复用，缺少明确适用性约定 |
| 合计 | 50 | 50 个唯一样本 ID；只有 45 个不同的归一化查询 |

`negative_label_supported` 只评价是否应当调用当前供给工具；不是对整句训练回复的背书。审核按工具说明和参数领域含义判断，不把任意数字填入不相关公式凑出目标值视为适配。

## 明确错标：名字不同但语义等价

**#27 `glaive-20088-negative-991`** 的请求是：

> I have some chicken, tomatoes, and garlic. Can you find a recipe for me?

供体 `search_recipes` 的原描述是 **“Search for recipes based on ingredients or cuisine”**，`ingredients` 是字符串数组（“The ingredients required for the recipe”），`cuisine` 可选，`required=[]`。合法的拟议调用是：

```json
{"name":"search_recipes","arguments":{"ingredients":["chicken","tomatoes","garlic"]}}
```

此调用仅在审核中提出，没有执行。原正例工具名是 `search_recipe`，供体是 `search_recipes`；两名不相交，但语义和输入完全匹配。供体里的另一个 `calculate_area` 无关，不影响存在一个可用食谱工具。因此 `calls=[]` 及统一拒答会教模型拒绝本来可完成的调用。这是本固定样本中 1 条确认错误，不能直接外推成全部 2,061 条负例的精确错误率。

## 两条保留不确定

- **#10 `glaive-84028-negative-1397`**：请求 “total bill amount is $100” 和 “15% tip”；供体 `calculate_discount(original_price, discount_percentage)` 返回折后价。输入 100、15 得 85，再做 100−85 可得到小费 15；但商品原价/折扣与账单/小费的角色不同。是否允许这种透明的辅助运算，没有定义。
- **#40 `glaive-1554-negative-489`**：请求 “originally priced at $200” 和 “20% discount”；供体 `calculate_tip(bill_amount, tip_percentage)` 可得到百分比金额 40，再用 200−40 得折后 160。它有实际数学关联，但文档承诺的是小费，未承诺折扣。

两条均为 `uncertain` / `negative_label_supported=null`，不强行记为正确负例或错误负例。需先由人确定工具跨领域复用的统一标准，再裁决；不应为改善统计而逐条改变标准。

## 空调用与拒答文案是两个问题

`src/toolcall_lora/tool_format.py::chat_messages` 把所有空调用训练成同一句：

> I cannot complete this request with the available tools.

因此，即使工具确实无关，也不一定适合将唯一回复训练为无法完成。例如：

- #7 `glaive-22175-negative-1450`：7 的平方可直接回答 49；账单小费工具不适合此请求，但并不妨碍回答。
- #8 `glaive-81033-negative-459`：长 10、宽 5 的矩形面积可直接算为 50。
- #16 `glaive-14241-negative-977`：75 kg / 1.8 m 的 BMI 可直接算为约 23.15；不涉及医疗判断。
- #48 `glaive-55827-negative-1840`：用户明确要一个笑话，模型可以直接讲；播放音乐不是所请求的动作。

逐项记录了 **34 条直接回答能力导致的过度拒答风险**、**5 条年龄题的参考日期依赖**（#6、#22、#30、#34、#41）、**1 条贷款本金口径需要澄清**（#12）、**1 条有适用工具却拒答**（#27）；其余 9 条没有在本审阅中另标回复文案问题。这里的 34 条包含一般知识/建议类请求，不表示已检索外部事实或给出生产级完整答案。34+5+1+1=41 是回复问题标记数，不是 41 条错误工具选择标签。

#12 `glaive-69726-negative-633` 同时说 “loan amount of $200,000” 和 “down payment of $40,000”，应澄清 200,000 是否已经是贷款本金；不擅自把它改为 160,000。年龄题的 “today” 没有固定数据采样参照日期，也不能把审阅当天的年龄写为历史样本金标准。

另外 #18、#24 的供体 `calculate_area` schema 存在形状参数表达问题：#18 将矩形归入单一 `side`，#24 则同时必填 `radius/base/height/side`。这些缺陷不改变它们对电影/BMI请求的工具不匹配判断，已作为供体 schema 质量问题单列。

## 来源、重复与泄漏边界

读取了负例 README、manifest、`data.py::add_negatives`、`query_key` / `split_rows`、`tool_format.py::chat_messages`，并只读核对本地 Glaive train/dev/test。

- 按训练数据种子 42 先打乱，再构造 10% 负例，得到 2,061 条；再按种子 42 抽 50，**逐字段复现当前固定样本**。
- 50 条源正例 ID、50 个供体 ID 均来自 train，供体 schema 与样本一致，原查询也一致；50/50 通过了“工具名集合不相交”条件。#27 证明这一条件不足以保证语义无关。
- 样本原查询按大小写和空白归一化后，在 dev/test 的**精确匹配数均为 0**。这不是无泄漏证明。
- 样本内部 #6/#22/#30/#34 是完全相同的年龄查询；#3/#29/#31 是完全相同的 Rowling 查询。50 条仅覆盖 45 个不同归一化查询，不应当成 50 个不同任务语义。
- 已逐句核实 **17 个审核样本**有跨划分的同任务、同关键输入值改写近重复；最终 JSONL 的 `split_evidence.semantic_near_duplicates` 保存原查询和调用证据。这是定向查证的已确认例子，不是穷尽近重复检索所得比例。

代表性证据：

| 训练负例样本（源查询不变） | dev/test 原始证据 | 为什么是近重复 |
|---|---|---|
| #16 `glaive-14241-negative-977`: “I want to calculate my BMI. I weigh 75 kilograms and my height is 1.8 meters.” | test `glaive-823`: “I need to calculate my BMI. I weigh 75 kilograms and my height is 1.8 meters.”；`calculate_bmi(weight=75,height=1.8)` | want/need 改写，同输入和计算目标 |
| #15 `glaive-67252-negative-1165`: “The total is $85 and I want to leave a 15% tip.” | dev `glaive-302`: “My bill amount is $85 and I want to leave a 15% tip.”；test `glaive-33236`: “The total bill is $85 and I want to give a 15% tip.” | 同账单、同比例、同小费目标 |
| #27 `glaive-20088-negative-991`: “chicken, tomatoes, and garlic” / “find a recipe” | test `glaive-17391`: “Hi, I have some chicken, tomatoes and garlic. Can you suggest a recipe?”；`search_recipes(ingredients=[chicken,tomatoes,garlic])` | 同食材、同食谱请求 |
| #25 `glaive-6006-negative-689`: “What is the definition of the word 'serendipity'?” | test `glaive-7703`: “Hi, I need to know the definition of the word \"serendipity\".”；`search_definition(word=serendipity)` | 同词、同定义目标 |

供给工具的完整 schema 可以不同，因此这些不是完整 prompt 的逐字重复。训练中保留原正例、再增加不同工具条件下的空调用，本身也是一种对照训练，不应仅因同 query 出现两次就称为标注冲突。但现有分组只按归一化原句，无法排除语义改写跨划分；Glaive dev/test 独立性不能用“精确重叠为零”来概括。**本次没有审查 BFCL 与训练数据的全部交叉，不能据此宣布 BFCL 泄漏，亦未测量任何正式分数受影响的幅度。**

## 尚需真人的部分

agent 审核已完成，原真人审核仍为 0/50；若验收坚持“由人审核”，不能把此文件改称人审完成。`requires_human_review=true` 仅标识优先裁决项，不代表其它条目的原人审字段已完成：

1. #27：确认明确错标，并决定是否修订下一版训练数据；不得静默改变现有运行或正式结果。
2. #10、#40：统一裁定百分比工具跨领域重用的边界。
3. #12：明确贷款本金与首付口径。
4. 数据集负责人决定空调用时直接回答/询问澄清/无法执行的回复准则，以及近重复分组是否需要另版数据；这是后续处理建议，本次未实施。

源样本 SHA-256：`09334b171b036f2c89b97474aee7bbec63ad6f487c3192ec149142047492d039`（审阅前后相同）。

训练文件 SHA-256：`cc47c09a1847ee00bf2a38e7c67801a3b826f85a4ddc0cc16b7595d9ee66b210`（与原 manifest 一致）。
