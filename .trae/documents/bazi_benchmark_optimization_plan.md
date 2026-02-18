# BaZi Benchmark 优化计划

**创建时间**: 2026-02-18
**状态**: 待审核

---

## 问题概述

基于对项目代码的全面分析，发现以下主要问题：

### 高优先级问题 (P0)
1. **代码重复定义**: `strength.py` 中 `analyze_strength` 函数被定义两次
2. **五行计数逻辑不一致**: `counts` 只统计主气，`missing` 却检查藏干
3. **性别字段缺失**: 部分样本 `gender` 为 null，影响大运计算

### 中优先级问题 (P1)
4. **评分器与输出格式不匹配**: 模型输出冗长，期望输出简洁
5. **强弱判断阈值需验证**: 阈值基于经验，缺乏典籍验证
6. **numpy 依赖处理不完整**: requirements.txt 缺少 numpy

### 低优先级问题 (P2-P3)
7. **测试覆盖不足**: 缺少边界情况测试
8. **刑冲合害分析不完整**: 未考虑天干合化等
9. **用神判断过于简化**: 只考虑强弱，未考虑格局
10. **评估结果分析维度有限**: 缺少错误类型分析

---

## 优化方案

### Phase 1: 修复高优先级问题

#### 1.1 修复代码重复定义
**文件**: `bazibench/core/strength.py`

**操作**: 删除第一个 `analyze_strength` 函数定义（第22-69行），保留第二个完整版本（第71-142行）

**验证**: 运行 `pytest tests/test_strength.py -v`

---

#### 1.2 统一五行计数逻辑
**文件**: `bazibench/core/wuxing.py`

**问题分析**:
- 当前 `counts` 只统计天干+地支主气
- `missing` 检查时却考虑了藏干
- 导致期望输出与模型理解不一致

**方案选择**:
- **方案A**: 统一为只统计主气（简化版，适合基础评估）
- **方案B**: 统一为统计藏干（完整版，更符合传统命理）

**推荐**: 方案A - 保持当前 `counts` 逻辑，修改 `missing` 检查逻辑

**修改内容**:
```python
# 修改 missing 检查，只检查主气
all_elements = set()
for stem in stems:
    all_elements.add(STEM_INFO[stem]["wuxing"])
for branch in branches:
    all_elements.add(BRANCH_INFO[branch]["wuxing"])
# 移除藏干检查
missing = [e for e in WUXING if e not in all_elements]
```

**同步修改**: 更新数据生成器中的期望输出格式说明

---

#### 1.3 修复性别字段缺失
**文件**: `bazibench/dataset/generator.py`

**问题**: `generate_sample` 方法中 `gender` 可能为 None

**修改**: 确保所有样本都有有效的 gender 值
```python
def generate_sample(self, task_type: str = "chart") -> BaziSample:
    dt = self.generate_random_date()
    gender = self.rng.choice([0, 1])  # 已有，确保不为 None
```

**验证**: 检查生成的数据文件中 gender 字段

---

### Phase 2: 优化评分系统

#### 2.1 增强 ExactMatchScorer
**文件**: `bazibench/scoring/exact_match.py`

**优化点**:
1. 增加对排盘格式的智能识别（年柱/月柱/日柱/时柱）
2. 优化五行计数的容错匹配
3. 增加对"身旺"/"身强"等同义词的处理

**新增方法**:
```python
def _extract_bazi_chart(self, text: str) -> Dict[str, str]:
    """提取八字四柱"""
    # 支持多种格式:
    # "庚午 辛巳 丁丑 乙巳"
    # "年柱: 庚午, 月柱: 辛巳..."
    # "| 年柱 | 庚午 | ..."
```

---

#### 2.2 优化 Prompt 设计
**文件**: `bazibench/dataset/generator.py`

**问题**: 当前 prompt 过于开放，模型输出格式不统一

**优化**: 在 instruction 中明确输出格式要求
```python
# 五行任务
instruction = f"""请分析该八字的五行个数与缺失：{chart}

请按以下格式输出（不要添加额外解释）：
五行统计: 金: X, 木: X, 水: X, 火: X, 土: X
缺失五行: X（如无缺失则填"无"）"""
```

---

### Phase 3: 完善依赖与测试

#### 3.1 更新依赖
**文件**: `requirements.txt`

**修改**:
```diff
+ numpy>=1.20.0  # 用于统计分析
```

或移除 evaluator.py 中未使用的 numpy 相关代码

---

#### 3.2 增加测试用例
**文件**: `tests/test_strength.py`, `tests/test_wuxing.py`

**新增测试**:
1. 节气交接时刻的排盘测试
2. 五行计数与缺失的一致性测试
3. 边界情况测试（如五行俱全、极端强弱）

---

### Phase 4: 验证与回归测试

#### 4.1 运行完整测试套件
```bash
pytest tests/ -v --cov=bazibench
```

#### 4.2 重新生成测试数据
```bash
python scripts/generate_data.py --output data/samples/bazi_benchmark_v2.jsonl --count 1000
```

#### 4.3 运行小规模评估验证
```bash
python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free --samples 30
```

---

## 实施顺序

| 步骤 | 任务 | 预计影响 |
|------|------|----------|
| 1 | 删除重复函数定义 | 代码质量提升 |
| 2 | 统一五行计数逻辑 | 五行任务准确率提升 |
| 3 | 修复性别字段 | 大运任务可用 |
| 4 | 增强评分器 | 整体准确率提升 |
| 5 | 优化 Prompt | 输出格式统一 |
| 6 | 更新依赖 | 消除警告 |
| 7 | 增加测试 | 代码可靠性提升 |
| 8 | 验证回归 | 确保修复有效 |

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 五行逻辑修改影响现有数据 | 中 | 重新生成测试数据 |
| 评分器修改影响历史结果对比 | 低 | 保留旧版本评分器作为对比 |
| Prompt 修改影响模型表现 | 中 | A/B 测试对比 |

---

## 预期成果

1. **代码质量**: 消除重复代码，提高可维护性
2. **评估准确性**: 五行任务准确率预计提升 20%+
3. **数据完整性**: 所有样本包含有效性别信息
4. **测试覆盖**: 增加边界情况测试，覆盖率提升

---

## 待确认事项

1. 五行计数逻辑选择方案 A（只统计主气）还是方案 B（统计藏干）？
2. 是否需要保留历史评估结果作为对比基准？
3. 是否需要同步更新已生成的测试数据？
