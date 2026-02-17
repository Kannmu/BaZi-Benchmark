# BaZiBench 项目实现计划

**创建时间**: 2026-02-17
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

### Phase 1: 项目结构与核心库 [进行中]
**状态**: completed
**目标**: 搭建项目骨架，实现八字计算核心功能

**任务清单**:
- [x] 创建项目目录结构
- [x] 实现八字计算核心库
  - [x] 天干地支基础数据
  - [x] 公历转八字四柱
  - [x] 五行生克关系
  - [x] 十神计算
  - [x] 日主强弱判断
  - [x] 藏干分析
  - [x] 刑冲合害分析
- [x] 编写单元测试
- [x] 验证计算准确性

**交付物**:
- `bazibench/` Python包
- `bazibench/core/` 核心计算模块
- `tests/` 测试文件

---

### Phase 2: 数据集生成器
**状态**: completed

**准备工作**:
- Phase 1 已完成，进入 Phase 2 之前可开始数据格式与样例设计
**目标**: 实现程序化数据集生成

**任务清单**:
- [x] 设计数据格式schema
- [x] 实现样本生成器
- [x] 实现多维度问题生成
- [x] 难度分级逻辑
- [x] 数据验证机制

**交付物**:
- `bazibench/dataset/` 数据集模块
- `data/` 数据存储目录
- 初始1000个测试样本

---

### Phase 3: 评估框架
**状态**: pending
**目标**: 实现完整的评估流程

**任务清单**:
- [ ] 模型接口抽象层
- [ ] OpenAI API支持
- [ ] Anthropic Claude支持
- [ ] 自定义BaseURL支持
- [ ] 批量评估功能
- [ ] 结果统计和分析

**交付物**:
- `bazibench/models/` 模型接口模块
- `bazibench/evaluation/` 评估引擎

---

### Phase 4: 评分系统
**状态**: pending
**目标**: 实现多类型评分机制

**任务清单**:
- [ ] 精确匹配评分
- [ ] 部分匹配评分
- [ ] 规则验证评分
- [ ] LLM-as-Judge评分
- [ ] 综合评分算法

**交付物**:
- `bazibench/scoring/` 评分模块

---

### Phase 5: 整合与测试
**状态**: pending
**目标**: 完成端到端测试

**任务清单**:
- [ ] 集成测试
- [ ] 示例脚本
- [ ] 文档编写
- [ ] 发布准备

**交付物**:
- 完整可用的框架
- README文档
- 示例代码

---

## 技术决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 语言 | Python 3.9+ | 科学计算生态成熟 |
| 数据格式 | JSON/YAML | 易读、易扩展 |
| 配置管理 | YAML | 支持复杂配置 |
| 测试框架 | pytest | Python标准选择 |

---

## 错误记录

| 错误 | 尝试 | 解决方案 |
|------|------|----------|
| (待记录) | - | - |

---

## 文件结构规划

```
bazibench/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── constants.py      # 天干地支常量
│   ├── calculator.py     # 八字计算器
│   ├── wuxing.py         # 五行分析
│   ├── ten_gods.py       # 十神计算
│   ├── strength.py       # 日主强弱
│   └── interactions.py   # 刑冲合害
├── dataset/
│   ├── __init__.py
│   ├── generator.py      # 数据集生成器
│   ├── schema.py         # 数据格式定义
│   └── validator.py      # 数据验证
├── models/
│   ├── __init__.py
│   ├── base.py           # 模型基类
│   ├── openai_model.py   # OpenAI接口
│   ├── anthropic_model.py # Claude接口
│   └── custom_model.py   # 自定义模型
├── evaluation/
│   ├── __init__.py
│   ├── evaluator.py      # 评估引擎
│   └── runner.py         # 批量评估
├── scoring/
│   ├── __init__.py
│   ├── exact_match.py    # 精确匹配
│   ├── partial_match.py  # 部分匹配
│   └── llm_judge.py      # LLM评判
└── utils/
    ├── __init__.py
    └── helpers.py        # 工具函数

data/
├── samples/              # 测试样本
├── results/              # 评估结果
└── configs/              # 配置文件

tests/
├── test_core.py
├── test_dataset.py
├── test_evaluation.py
└── test_scoring.py
```
