# toolcall-lora：小模型工具调用的 LoRA 微调

用 LoRA 微调 Qwen2.5-1.5B-Instruct 的原生工具调用能力，用 BFCL 官方 AST 检查器评测，对照 1.5B 和 7B 原模型。重点看两件事：负样本（不该调工具的请求）能不能教会小模型“不乱调工具”，以及 LoRA rank 对效果的影响。

## 结果

BFCL 评测用 5 个类别共 1,240 题：`simple_python`、`multiple`、`parallel`、`parallel_multiple` 和 `irrelevance`。这是官方检查器在子集上的分数，不是排行榜总分。

**rank 8、1 万条正样本，加 10% 负样本（种子 42）：**

| 类别 | 题数 | 1.5B 原模型 | 7B 原模型 | 不加负样本 | 加 10% 负样本 |
|---|---:|---:|---:|---:|---:|
| simple_python | 400 | 84.00% | 95.50% | 87.50% | 86.75% |
| multiple | 200 | 83.00% | 95.50% | 89.00% | 85.50% |
| parallel | 200 | 65.50% | 90.00% | 74.50% | 69.50% |
| parallel_multiple | 200 | 62.50% | 86.50% | 69.00% | 71.50% |
| irrelevance | 240 | 70.42% | 60.42% | 0.00% | **87.08%** |
| 合计 | 1,240 | 74.76% | 86.37% | 65.73% | **81.37%** |

- 加负样本后，合计从 65.73% 提到 81.37%（配对 bootstrap 95% 置信区间 +13.2～+18.2 个点）。
- 和 1.5B 原模型比，合计高 6.61 个点（95% 置信区间 +4.4～+8.9），5 个类别的点估计都更高。
- `irrelevance` 从 0/240 提到 209/240，比 7B 原模型高 26.7 个点。

**rank 16、全部 1.85 万条正样本、10% 负样本（3 个种子）：**

- BFCL `irrelevance` 三种子均值 89.58%（1.5B 原模型 70.42%，7B 原模型 60.42%）。
- Glaive 留出集 2,000 条，调用 JSON 完全匹配三种子均值 94.65%，种子间标准差 0.15 个点。

完整的逐类分数、配对置信区间和原始预测在 `results/` 下，见 [rank 8 对比](results/formal-ablation-comparisons/rank8.bfcl.md)、[三种子汇总](results/formal-main-summary/bfcl.summary.md) 和 [原模型对比](results/formal-baselines/comparison.md)。

## 做法

- **数据**：Glaive function-calling 数据，只取第一组完整的“用户请求 → 工具调用”，不拼接依赖上下文的后续轮次。按归一化后的问题分组切分 train / dev / test，同一个问题不会跨集合。
- **负样本**：从训练集里借一个名字不相关的工具，配上原来的请求，目标输出是“不调用工具”。
- **训练**：PEFT LoRA（alpha = 2 × rank），2 个 epoch，L4 / A100 用 bf16，有效 batch 32。超长样本整条丢弃并计数，不截断成不合法的 JSON。只用固定的 256 条开发集样本看 loss，不用测试集挑模型。
- **评测**：BFCL 官方 AST 检查器，加一个严格的 Qwen 原生工具调用标签解析器。留出集用与顺序无关的 JSON 完全匹配。
- **统计**：三种子结果给出 t 分布置信区间；配对比较用 1,000 次按题重采样的 bootstrap。

## 复现

环境用 Python 3.12，依赖版本固定在 `pyproject.toml`。

```sh
bash scripts/colab_bootstrap.sh
source /content/e2-venv/bin/activate
python3 -m toolcall_lora.cli prepare-glaive --output /content/data/e2-glaive
python3 -m toolcall_lora.cli prepare-bfcl
bash scripts/formal_baselines.sh   # 1.5B 和 7B 原模型
bash scripts/formal_train.sh       # 主实验，种子 42/43/44
bash scripts/formal_ablations.sh   # rank 和负样本比例
```

正式训练通过 `EXP_CHECKPOINT_SYNC` 调用持久化命令。可传入包含 `{source}`、`{experiment}`、`{run_id}`、`{receipt}` 的 JSON 参数数组；命令成功后须写回匹配的检查点验证回执。Colab 脚本默认从 `E2_ENV_FILE`（默认 `/content/experiment-env.json`）读取 Drive 配置并调用 `exp_common.checkpoint`。

已有结果的汇总不需要 GPU：

```sh
python3 scripts/compare_ablation_bfcl.py --rank 8
python3 scripts/summarize_main_bfcl.py
python3 scripts/summarize_main_heldout.py
```

## 目录

| 路径 | 内容 |
|---|---|
| `src/toolcall_lora/` | 数据转换、训练、推理和评分 |
| `scripts/` | 训练和评测入口、结果汇总脚本 |
| `configs/` | 主实验和消融配置 |
| `results/` | 原始预测、分数和对比报告 |
| `docs/baselines.md` | 数据和基线来源 |
| `docs/cost.md` | GPU 用时记录 |
