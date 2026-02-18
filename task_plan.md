# BaZiBench 项目实现计划

**创建时间**: 2026-02-17
**最后更新**: 2026-02-18
**状态**: 进行中
**目标**: 构建完整的八字分析LLM评估基准框架

---

## 项目概述

BaZiBench是一个创新的LLM评估基准，通过八字分析这一复杂的传统文化任务，全面评估大语言模型的多步骤逻辑推理能力。

**核心模块**:
1. 八字计算核心库 (bazi_core)
2. 数据集生成器 (dataset_generator)
3. 评估框架 (evaluation)
4. 评分系统 (scoring)
5. 模型接口层 (models)

---

## 实现阶段

### Phase 1: 项目结构与核心库 [完成]
**状态**: completed
**交付物**:
- `bazibench/` Python包
- `bazibench/core/` 核心计算模块
- `tests/` 测试文件

### Phase 2: 数据集生成器 [完成]
**状态**: completed
**交付物**:
- `bazibench/dataset/` 数据集模块
- `data/` 数据存储目录

### Phase 3: 评估框架 [完成]
**状态**: completed
**交付物**:
- `bazibench/models/` 模型接口模块
- `bazibench/evaluation/` 评估引擎

### Phase 4: 评分系统 [完成]
**状态**: completed
**交付物**:
- `bazibench/scoring/` 评分模块

### Phase 5: 整合与测试 [完成]
**状态**: completed
**交付物**:
- 完整可用的框架
- README文档
- 示例代码

### Phase 6: 项目标准化与优化 [完成]
**状态**: completed
**目标**: 移除临时版本 (mini/v1/v2)，统一数据生成流程，进行小规模验证测试。

**任务清单**:
- [x] 统一数据生成脚本 `scripts/generate_data.py`
  - [x] 包含所有任务类型
  - [x] 启用数据验证
  - [x] 输出为 `data/samples/bazi_benchmark.jsonl`
- [x] 清理冗余文件
  - [x] 删除 `scripts/generate_mini_data.py`
  - [x] 删除 `data/samples/bazi_benchmark_mini.jsonl`
  - [x] 删除 `data/samples/bazi_benchmark_v2.jsonl`
  - [x] 删除 `data/results_mini_v2/`
- [x] 生成标准数据集
  - [x] 运行 `generate_data.py` 生成完整数据集
- [x] 抽取测试样本
  - [x] 从完整数据集中随机抽取20个样本用于测试
  - [x] 保存为 `data/samples/bazi_benchmark_test_20.jsonl`
- [x] 执行小规模测试
  - [x] 使用 `xiaomi/mimo-v2-flash-free` 模型
  - [x] 针对 20 个样本进行评估
- [x] 结果分析与修复
  - [x] 检查运行日志和结果
  - [x] 修复十神计算逻辑错误 (core/ten_gods.py)
  - [x] 优化Prompt提示词，增强JSON输出约束 (dataset/generator.py)
  - [x] 调整评分策略，对刑冲合害任务启用部分匹配 (PartialMatch)
  - [x] 验证修复效果 (准确率从 33% 提升至 53%)

---

## 技术决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 语言 | Python 3.9+ | 科学计算生态成熟 |
| 数据格式 | JSON/YAML | 易读、易扩展 |
| 配置管理 | YAML | 支持复杂配置 |
| 测试框架 | pytest | Python标准选择 |
| 评分策略 | Exact/Partial | 针对不同任务类型灵活评分 |

---

## 错误记录

| 错误 | 尝试 | 解决方案 |
|------|------|----------|
| 十神判断错误 | 检查代码逻辑 | 修正 `ten_gods.py` 中同性/异性生克的判断逻辑 (正印/偏印反转) |
| 刑冲合害评分过低 | 检查模型输出 | 模型输出包含额外键值或幻觉，改为 `PartialMatchScorer` 并约束JSON输出 |
| 强弱判断格式混乱 | 优化Prompt | 增加严格的格式输出指令 |
