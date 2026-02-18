# BaZi Benchmark Optimization Plan

## 1. 现状分析 (Current Status Analysis)

经过对项目代码库 (`bazibench/core`, `bazibench/dataset`, `bazibench/scoring`) 的详细审查，结合 PRD 文档，我们对 Dimension 6-8 的实现情况得出以下结论：

### Dimension 6: 刑冲合害 (Interactions)

* **现状**: `core/interactions.py` 已实现了六合 (Liu He)、六冲 (Liu Chong)、三合 (San He)、相刑 (Xing)、自刑 (Self Xing)。

* **缺失**: 缺少 **三会 (San Hui)** 和 **六害 (Xiang Hai/Liu Hai)** 的实现。

* **影响**: 评估维度不完整，无法全面测试模型对地支复杂关系的掌握。

### Dimension 7: 大运流年 (Luck Cycle)

* **现状**: `core/calculator.py` 和 `generator.py` 仅实现了 **大运 (Da Yun)** 的排盘。

* **缺失**: 完全缺失 **流年 (Liu Nian/Annual Pillar)** 的计算逻辑和相关题目生成。

* **影响**: 无法评估模型对时间流转（流年）与命局关系的推理能力，不符合 PRD 中 D7 的完整定义。

### Dimension 8: 综合解读 (Comprehensive Interpretation)

* **现状**: `generator.py` 中的 prompt 较为简单 (`"请对该{gender}命进行综合八字分析..."`)。

* **缺失**: 缺乏分领域的具体引导（如事业、财运、婚姻），导致模型输出可能过于发散，难以进行标准化的 LLM-as-a-judge 评估。

* **影响**: 综合能力的评估颗粒度不够。

### 其他发现 (Other Findings)

* **Dimension 5 (Useful God)**: 目前仅基于强弱和调候的简单启发式规则，缺乏深度逻辑。

* **LLM Judge**: 代码已支持 OpenAI 兼容接口，但 `data/configs/models.yaml` 中 Qwen 的配置被注释。

***

## 2. 优化方案 (Optimization Plan)

我们将分阶段实施以下优化，重点完善 D6-D8 的功能，并启用 Qwen 模型进行评估。

### Phase 1: 核心逻辑增强 (Core Logic Enhancement)

**目标**: 补全 D6 和 D7 的核心算法缺失。

1. **完善** **`core/interactions.py`**:

   * 增加 `check_san_hui` 函数：识别寅卯辰（木）、巳午未（火）、申酉戌（金）、亥子丑（水）三会局。

   * 增加 `check_xiang_hai` 函数：识别子未害、丑午害、寅巳害、卯辰害、申亥害、酉戌害。

   * 更新 `get_interactions` 聚合函数。

2. **完善** **`core/calculator.py`**:

   * 增加 `calculate_liunian` 函数：根据大运和出生年份，推算指定年份的流年干支。

   * 逻辑：流年干支 = (年份 - 3) % 60 对应的干支（或基于1984甲子年推算）。

### Phase 2: 数据生成器升级 (Dataset Generator Upgrade)

**目标**: 更新生成器以支持新维度的题目生成。

1. **更新** **`dataset/generator.py`**:

   * **D6 (Interactions)**: 增加生成涉及三会、六害的题目（例如：“地支中是否存在三会木局？”）。

   * **D7 (Luck Cycle)**: 增加流年相关题目（例如：“请推算2024年的流年干支及其与日柱的关系”）。

   * **D8 (Comprehensive)**: 优化 Prompt 模板，增加结构化要求（例如：“请从性格、事业、财运三个方面进行综合分析”），以便于 Judge 评分。

### Phase 3: 评估配置与模型接入 (Configuration & Model Integration)

**目标**: 启用 `qwen/qwen3.5-plus` 作为评估模型和 Judge 模型。

1. **配置** **`data/configs/models.yaml`**:

   * 取消 `qwen/qwen3.5-plus` 的注释。

   * 配置 `zenmux` provider（或标准 OpenAI compatible provider）。

   * 设置 API Key 环境变量。

2. **验证** **`scoring/llm_judge.py`**:

   * 确保 Judge 评分逻辑适配 Qwen 的输出格式。

### Phase 4: 执行与验证 (Execution & Verification)

1. **生成新数据集**: 运行 `scripts/generate_data.py` 生成包含新 D6-D8 题目的测试集 `data/samples/bazi_benchmark_v2.jsonl`。
2. **运行评估**: 使用 `scripts/run_benchmark.py` 对 Qwen 模型进行全维度评估。
3. **生成报告**: 输出最终的分析报告。

***

## 3. 任务清单 (Task List)

* [ ] **Core**: 实现 `interactions.py` 中的三会 (San Hui) 和六害 (Xiang Hai)。

* [ ] **Core**: 实现 `calculator.py` 中的流年 (Liu Nian) 计算。

* [ ] **Dataset**: 更新 `generator.py` 适配 D6 (新关系), D7 (流年), D8 (结构化 Prompt)。

* [ ] **Config**: 修改 `models.yaml` 启用 Qwen 模型。

* [ ] **Script**: 生成 v2 版本数据集。

* [ ] **Script**: 运行 Benchmark 并生成报告。

