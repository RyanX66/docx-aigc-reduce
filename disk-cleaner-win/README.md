# disk-cleaner-win

Windows 智能磁盘分析清理工具 — AI-assisted disk space management.

## 解决的问题

Windows C 盘空间不足是普遍痛点。用户面对复杂的目录结构，不知道哪些可以安全删除、哪些会影响系统运行。本工具通过路径模式匹配 + 安全分级，自动分类并生成清理建议。

## 工作流

```
扫描磁盘 → 递归计算目录大小 → 安全分级(safe/cache/critical) → 生成报告 → 确认清理
```

## 依赖

```bash
pip install -r requirements.txt   # (standard library only, no extra deps)
```

## 使用

```bash
# 分析 C 盘
python scripts/analyze.py C: report.json

# 安全清理
python scripts/cleanup.py
```

## 安全分级系统

| 级别 | 说明 | 示例 |
|------|------|------|
| **safe** | 零风险，可立即清理 | pip cache, %TEMP%, Recycle Bin, Windows Temp |
| **cache** | 应用缓存，清理后重建 | 百度网盘, 腾讯, WPS, B站, 抖音缓存 |
| **critical** | 严禁删除 | System32, Program Files, Documents |
| **unknown** | 需人工判断 | 其他未分类目录 |

## 实际清理效果

```
C 盘 199GB 分析结果：

[SAFE TO CLEAN]    Total: 19.8 GB
  12.4 GB  pip cache
   6.0 GB  User Temp
   1.2 GB  Recycle Bin
   0.6 GB  Windows Temp

[APP CACHE]        Total: 18.2 GB
   5.2 GB  WPS Office
   4.2 GB  百度网盘
   2.1 GB  腾讯 QQ/微信
   ...

Before: 25 GB free (12%)
After:  46 GB free (23%)
Freed:  +21 GB
```

## 与 AI/Agent 的结合

本工具在 Claude Code Agent 会话中被设计、编码、测试并完成实际清理：
- Agent 自动分析磁盘占用结构
- 基于路径模式自动分级
- 交互式确认后执行清理
- 清理前后对比验证

## 项目结构

```
disk-cleaner-win/
├── README.md
└── scripts/
    ├── analyze.py      # 磁盘分析 + 安全分级 + 报告生成
    └── cleanup.py      # 安全清理执行器
```
