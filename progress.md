# BaZiBench 实现进度日志

**创建时间**: 2026-02-17

---

## 会话日志

### 2026-02-18 会话8 (Scoring System Implementation)

**任务**: 实现评分系统和结果分析功能

**操作记录**:

1.  **实现评分模块 (`bazibench/scoring/`)**:
    -   创建 `BaseScorer` 抽象基类。
    -   实现 `ExactMatchScorer`: 支持 JSON 对象和字符串的精确匹配。
    -   实现 `PartialMatchScorer`: 支持字典键值对和列表元素的部分匹配。
    -   实现 `LLMJudgeScorer`: 使用 LLM 对开放性问题进行评分（0-10分）。
2.  **增强评估框架 (`bazibench/evaluation/`)**:
    -   重构 `Evaluator.evaluate`: 集成评分逻辑，根据样本类型自动选择评分器。
    -   新增 `calculate_metrics`: 计算准确率、标准差等统计指标。
    -   新增 `_save_metrics`: 自动保存评估报告到 JSON 文件。
3.  **更新数据 Schema (`bazibench/dataset/schema.py`)**:
    -   在 `BaziSample` 中添加 `evaluation_type` 字段，默认为 `exact_match`。
4.  **编写测试**:
    -   `tests/test_scoring.py`: 单元测试，覆盖各种评分场景。
    -   `tests/test_evaluation_integration.py`: 集成测试，验证从模型输出到评分报告的完整流程。
5.  **验证**:
    -   所有新测试通过。

**当前状态**: 评分系统已就绪，评估框架具备了完整的“推理-评分-统计”闭环能力。

### 2026-02-18 会话7 (Critical Fixes)

**任务**: 修复 PRD 问题分析报告中的关键问题

**操作记录**:

1.  **核心计算修复**:
    -   `calculator.py`: 实现真太阳时计算（支持 `utc_offset`, `longitude`），修复大运性别验证。
    -   `strength.py`: 优化藏干权重（细化本气、中气、余气权重），调整强弱判断阈值。
    -   `wuxing.py`: 修复五行缺失判断，增加对藏干的检查。
2.  **数据生成器优化**:
    -   `schema.py`: 增加 `longitude`, `latitude`, `utc_offset` 字段。
    -   `generator.py`: 
        -   修复随机种子初始化问题 (`random.Random`)。
        -   同步强弱阈值逻辑，增加简单的调候用神判断。
        -   修复大运数据边界条件（少于3步时处理）。
        -   生成样本时填充地理位置信息（默认北京）。
3.  **评估框架增强**:
    -   `evaluator.py`: 引入 `ThreadPoolExecutor` 实现并发评估，添加线程锁确保文件写入安全。
4.  **模型接口改进**:
    -   `openai_model.py`: 优化重试逻辑（排除认证/参数错误），增加 `max_tokens` 默认配置。
5.  **依赖更新**:
    -   安装 `python-dotenv`, `lunar_python`, `tenacity`。
    -   所有测试通过（33 tests passed）。

**当前状态**: 核心计算逻辑更严谨，评估框架支持并发，数据生成更规范。

---

### 2026-02-18 会话6 (Refactoring & Fixes)

**任务**: 修复PRD中报告的问题（核心计算、评估框架、数据生成器）

**操作记录**:

1.  **核心计算升级**:
    -   集成 `lunar_python` 库以实现精确的节气和真太阳时计算
    -   重构 `BaZiCalculator.calculate` 使用 `lunar_python`
    -   实现 `calculate_dayun` 支持大运排盘
    -   优化 `strength.py` 评分逻辑（增加月令权重，区分藏干主气余气）
    -   更新 `tests/test_calculator.py` 修正测试预期
2.  **评估框架增强**:
    -   更新 `Evaluator.evaluate` 支持断点续传（跳过已存在的ID）
    -   在 `OpenAIModel.generate` 中添加 `tenacity` 重试机制
    -   统一异常处理（Evaluator 捕获异常并记录）
3.  **数据生成器扩展**:
    -   在 schema 中添加 `DaYunAnalysis` 和 `UsefulGodAnalysis`
    -   实现缺失的任务类型: `interactions`, `da_yun`, `useful_god`, `comprehensive`
    -   在 `tests/test_generator.py` 中添加新任务类型的测试
4.  **工程化改进**:
    -   添加 `bazibench/utils/logger.py`
    -   在 `__init__.py` 中添加 `python-dotenv` 支持
    -   更新 `requirements.txt`
    -   在 `__init__.py` 中导出核心类

**当前状态**: 所有报告的高/中优先级问题已解决，所有测试通过。

---

### 2026-02-18 会话5

**任务**: 配置 ZenMux 模型服务

**操作记录**:

1. 创建配置文件 `data/configs/models.yaml`
   - 配置 ZenMux provider (OpenAI兼容接口)
   - 添加模型: `qwen/qwen3.5-plus`, `minimax/minimax-m2.5`, `moonshotai/kimi-k2.5`, `z-ai/glm-5`
   - 特殊配置: `moonshotai/kimi-k2.5` 设置 `temperature: 1.0`
2. 实现模型注册表 `bazibench/models/registry.py`
   - 支持从 YAML 加载配置
   - 自动解析环境变量 `ZENMUX_API_KEY`
   - 实现参数合并逻辑 (优先使用传入参数，其次是模型配置)
3. 创建测试脚本 `scripts/test_zenmux_models.py`
   - 验证所有配置模型的连通性
   - 成功测试 4 个模型

**当前状态**: 模型配置与管理机制已建立，ZenMux 服务接入成功

---

### 2026-02-18 会话4

**任务**: 实现评估框架与模型接口

**操作记录**:

1. 创建 `bazibench/models` 模块
   - `base.py`: 定义模型抽象基类
   - `openai_model.py`: 实现OpenAI接口（支持自定义BaseURL）
   - `anthropic_model.py`: 实现Claude接口
2. 创建 `bazibench/evaluation` 模块
   - `evaluator.py`: 实现批量评估引擎，支持断点续传（通过追加写入）
3. 编写单元测试
   - `tests/test_models.py`: 验证模型接口实例化与Mock调用
   - `tests/test_evaluation.py`: 验证评估流程与结果保存
4. 更新依赖 `requirements.txt`，增加 `openai` 和 `anthropic`

**当前状态**: Phase 3 评估框架主体完成，等待评分系统接入

---

### 2026-02-18 会话3

**任务**: 实现数据集生成器与数据格式

**操作记录**:

1. 创建 `bazibench/dataset` 模块
   - `schema.py`: 定义Pydantic数据模型
   - `generator.py`: 实现样本生成器
   - `validator.py`: 实现数据验证逻辑
   - `__init__.py`: 导出核心类
2. 编写单元测试
   - `tests/test_generator.py`
   - `tests/test_validator.py`
3. 创建数据生成脚本 `scripts/generate_data.py`
4. 生成初始1000个测试样本到 `data/samples/bazi_benchmark_v1.jsonl`

**当前状态**: Phase 2 数据集生成器完成

---

### 2026-02-18 会话2

**任务**: 完整实现八字核心库与测试

**操作记录**:

1. 创建 `bazibench` 包与 `core` 模块
2. 实现六大核心模块：常量、四柱计算、五行、十神、强弱、刑冲合害
3. 编写并完善单元测试
4. 增加 `tests/conftest.py` 以修复包导入问题
5. 用户在本地环境运行 pytest 全部通过

**当前状态**: Phase 1 核心库与测试完成

---

### 2026-02-17 会话1

**开始时间**: 23:36

**任务**: 项目初始化和核心库实现

**操作记录**:

1. 读取PRD文档 - 了解项目需求和架构
2. 创建规划文件
   - task_plan.md ✓
   - findings.md ✓
   - progress.md ✓ (当前)

**下一步**: 创建项目目录结构和核心模块

---

## 文件创建/修改记录

| 文件 | 操作 | 说明 |
|------|------|------|
| bazibench/scoring/ | 创建 | 评分模块 (base, exact_match, partial_match, llm_judge) |
| bazibench/evaluation/evaluator.py | 修改 | 集成评分系统，添加统计功能 |
| bazibench/dataset/schema.py | 修改 | 添加 evaluation_type 字段 |
| tests/test_scoring.py | 创建 | 评分系统单元测试 |
| tests/test_evaluation_integration.py | 创建 | 评估流程集成测试 |
| task_plan.md | 创建 | 项目计划文档 |
| findings.md | 创建 | 研究发现文档 |
| progress.md | 创建 | 进度日志 |
| bazibench/dataset/ | 创建 | 数据集模块 |
| scripts/generate_data.py | 创建 | 数据生成脚本 |
| data/samples/ | 生成 | 初始数据集 |
| bazibench/core/calculator.py | 重构 | 使用 lunar_python，支持真太阳时 |
| bazibench/core/strength.py | 修改 | 优化藏干权重 |
| bazibench/core/wuxing.py | 修改 | 增加藏干五行统计 |
| bazibench/dataset/schema.py | 修改 | 增加地理位置字段 |
| bazibench/dataset/generator.py | 修改 | 修复阈值、随机种子、大运 |
| bazibench/evaluation/evaluator.py | 修改 | 支持并发和安全写入 |
| bazibench/models/openai_model.py | 修改 | 优化重试逻辑 |

---

## 测试结果

- 2026-02-18: pytest 全部通过 (Session 8) (新增 scoring 和 integration 测试)
- 2026-02-18: **pytest 全部通过 (Session 7)**
- 2026-02-18: 修复后 pytest 全部通过 (Session 6)
- 2026-02-18: 数据集生成脚本成功生成 1000 条有效样本
- 2026-02-18: pytest 全部通过（用户本地环境）

---

## 问题与解决

- **Issue**: 原有八字计算逻辑过于简单，不支持真太阳时和精确节气。
- **Solution**: 引入 `lunar_python` 库，重写 `BaZiCalculator`，并手动实现真太阳时校正。
- **Issue**: 日主强弱评分与用神判断不一致，且藏干权重粗糙。
- **Solution**: 细化 `HIDDEN_WEIGHTS`，统一评分阈值，增强用神逻辑。
- **Issue**: 评估框架串行效率低且有写入竞态。
- **Solution**: 引入 `ThreadPoolExecutor` 和 `threading.Lock`。

---

## 待办事项

- [x] 创建bazibench包结构
- [x] 实现核心计算模块
- [x] 编写单元测试
- [x] 验证计算准确性
- [x] 实现数据集生成器
- [x] 生成初始数据集
- [x] 修复PRD报告的问题
