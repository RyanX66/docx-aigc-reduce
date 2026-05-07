# multi-agent-pipeline

Multi-Agent Document Processing Pipeline — 多 Agent 协作文档处理流水线框架。

演示如何通过多个 AI Agent 的长链推理与协作，完成从原始文件到验证输出的端到端自动化。

## 架构

```
                    ┌──────────────────────────────────┐
                    │     Orchestrator Agent           │
                    │  (Task decomposition & routing)  │
                    └──────────┬───────────────────────┘
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
  │  Agent 1        │ │  Agent 2        │ │  Agent 3        │
  │  Structure      │ │  Content        │ │  Verification   │
  │  Analyzer       │ │  Rewriter       │ │  Validator      │
  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
           │                   │                   │
           ▼                   ▼                   ▼
     Extract body      Apply rewrite        Verify:
     paragraphs        rules (2-round)      - citations
     (skip titles,     - round 1: vocab     - images
      images, refs)    - round 2: anti-AI   - headings
                                            - references
```

## 真实案例：毕业论文降 AIGC 流水线

### 输入
- 一份 416 段的 .docx 毕业论文
- 目标：降低 AIGC 检测率，保留所有格式、图片、引用

### Agent 协作流程

| 步骤 | Agent | 输入 | 输出 | 工具 |
|------|-------|------|------|------|
| 1 | Structure Analyzer | .docx 文件 | 142 段正文 JSON | `extract_body.py` |
| 2 | Content Rewriter R1 | 正文 JSON | 改写后 JSON | `rewrite_engine.py` (Round 1) |
| 3 | Content Rewriter R2 | R1 输出 | 最终改写 JSON | `rewrite_engine.py` (Round 2) |
| 4 | Format Writer | 改写 JSON + 原始 .docx | 输出 .docx | `apply_rewrite.py` |
| 5 | Validator | 原始 .docx + 输出 .docx | 验证报告 | `verify.py` |

### 关键数据

| 指标 | 结果 |
|------|------|
| 总段落 | 416 (保持不变) |
| 改写段落 | 137 段中英双语 |
| 图片保留 | 52/52 |
| 引用保留 | [1]~[14] 全部 |
| 标题保留 | 44/44 |
| 参考文献 | 一字未动 |
| 验证通过率 | 5/5 (100%) |

### 设计的 Agent 协作模式

**1. 串行长链推理 (Sequential Chain)**
每个 Agent 的输出是下一个 Agent 的输入，形成 5 步推理链。前一步失败则整条链停止。

**2. 状态持久化 (State Persistence)**
通过 `aigc_records.json` 记录每轮完成状态，支持跨对话恢复和断点续跑。中文两轮模式分两次对话完成。

**3. 格式安全边界 (Format Safety Boundary)**
- Agent 1 识别安全边界：哪些段落可以改、哪些绝对不能动
- Agent 4 在安全边界内执行写回，超出边界自动拒绝
- Agent 5 对边界外的内容做二次验证

**4. 专业子 Agent 分工**
- 每个 Agent 只做一件事，有自己的专用工具和领域知识
- Orchestrator 负责调度和状态管理
- Agent 之间通过标准化 JSON 接口通信

## 项目结构

```
multi-agent-pipeline/
├── README.md                    # 架构说明 + 案例
└── scripts/
    └── pipeline_runner.py       # 流水线编排器
```

## 扩展性

同一架构可适配：
- 代码审查流水线 (lint → review → fix → verify)
- 数据清洗流水线 (extract → clean → transform → validate)
- 翻译流水线 (parse → translate → format → review)

## 依赖

标准 Python 项目，与 [docx-aigc-reduce](https://github.com/RyanX66/docx-aigc-reduce) 配合使用。
