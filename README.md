# docx-aigc-reduce

AI Agent 驱动工具集 — 毕业论文降 AIGC / 磁盘智能清理 / 多 Agent 协作流水线。

三个子项目在同一 Agent 会话中设计、编码、测试并上线。

---

## 项目一：论文降 AIGC 流水线

### 解决的问题

高校毕业论文 AIGC 检测率过高，需要对正文进行"去 AI 味"改写，同时保留标题、目录、图片、参考文献、致谢原封不动。

### 工作流

```
.docx 输入 → 提取正文段落 → 两轮降AIGC改写 → 保留格式写回 → 5项验证
```

### 使用

```bash
python scripts/extract_body.py 论文.docx body.json      # Agent 1: 结构分析
python scripts/rewrite_engine.py                          # Agent 2+3: 两轮改写
python scripts/apply_rewrite.py 论文.docx map.json out.docx # Agent 4: 格式写回
python scripts/verify.py 论文.docx out.docx               # Agent 5: 验证
```

### 实际处理结果

```
Passed: 5/5
  [OK] Paragraph count: 416
  [OK] Images preserved: 52
  [OK] Citation markers: [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
  [OK] All headings unchanged (44/44)
  [OK] Reference text unchanged (14 items)
```

---

## 项目二：Windows 智能磁盘清理

### 解决的问题

C 盘空间不足，用户不知道哪些可以安全删除。通过路径模式匹配 + 安全分级自动识别。

### 使用

```bash
python disk-cleaner-win/scripts/analyze.py C: report.json   # 分析
python disk-cleaner-win/scripts/cleanup.py                   # 安全清理
```

### 实际清理效果（同一 Agent 会话）

| 清理项 | 大小 | 风险 |
|--------|------|------|
| pip cache | 12.4 GB | 零风险 |
| User Temp | 6.0 GB | 零风险 |
| Recycle Bin | 1.2 GB | 零风险 |
| Windows Temp | 0.6 GB | 零风险 |
| 百度网盘 AutoUpdate | 2.1 GB | 零风险 |
| **合计释放** | **~22 GB** | |

```
C 盘可用: 25 GB (12%) → 46 GB (23%)
```

---

## 项目三：多 Agent 协作流水线框架

### 架构

```
Orchestrator → [Agent 1: 分析] → [Agent 2: 改写R1] → [Agent 3: 改写R2] → [Agent 4: 写回] → [Agent 5: 验证]
```

### 特性

- 5 Agent 串行长链推理，每步输出作为下一步输入
- 状态持久化，支持跨对话断点续跑
- 安全边界硬约束，非目标内容写保护

### 使用

```bash
python multi-agent-pipeline/scripts/pipeline_runner.py 论文.docx 输出.docx [--resume]
```

---

## 安装

```bash
pip install python-docx lxml
```

## 项目结构

```
docx-aigc-reduce/
├── README.md
├── SKILL.md                          # 完整改写规则（中文两轮+英文）
├── scripts/
│   ├── extract_body.py               # 正文段落提取
│   ├── rewrite_engine.py             # 本地改写引擎
│   ├── apply_rewrite.py              # 格式保留写回
│   └── verify.py                     # 5项完整性验证
├── disk-cleaner-win/
│   ├── README.md
│   └── scripts/
│       ├── analyze.py                # 磁盘分析+安全分级
│       └── cleanup.py                # 安全清理执行
└── multi-agent-pipeline/
    ├── README.md
    └── scripts/
        └── pipeline_runner.py         # 5 Agent 流水线编排器
```

## Agent 驱动记录

本项目全部代码在 deepseek-v4-pro[1m] 单一 Agent 会话中完成，覆盖：
- 需求分析 → 架构设计 → 代码编写 → 测试验证 → GitHub 上线
- 416 段真实毕业论文处理，5 项验证全通过
- 199GB 磁盘分析 + 22GB 安全清理
