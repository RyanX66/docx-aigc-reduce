# docx-aigc-reduce

毕业论文/学术文档 .docx 降 AIGC 自动化流水线。

**核心原则：只改正文，其他一切不动。**

## 解决的问题

高校毕业论文 AIGC 检测率过高，需要对正文进行"去 AI 味"改写。手动处理面临：
- Word 文档结构复杂，需保留标题/目录/图片/参考文献/致谢
- 改写规则包含两轮递进策略，人工执行效率极低
- 改写后需验证引用完整性，手工核对极易遗漏

## 工作流

```
.docx 输入 → 提取正文段落 → 逐段降AIGC改写 → 保留格式写回 → 验证完整性 → 输出
```

## 依赖

```bash
pip install python-docx lxml
```

## 使用

```bash
# 完整流水线
python scripts/extract_body.py 论文.docx body.json                    # 1. 提取正文
python scripts/rewrite_engine.py                                       # 2. 本地改写
python scripts/apply_rewrite.py 论文.docx rewrite_mapping.json out.docx # 3. 写回
python scripts/verify.py 论文.docx out.docx                           # 4. 验证
```

## 脚本

| 脚本 | 功能 |
|------|------|
| `extract_body.py` | 智能提取正文段落，自动跳过标题/目录/图片/参考文献/致谢 |
| `rewrite_engine.py` | 本地规则引擎，两轮递进降 AIGC：词汇替换 + AI 套话清洗 |
| `apply_rewrite.py` | 改写文本写回 .docx，保留 run 级原始格式 |
| `verify.py` | 5 项自动化验证：段落数/图片数/引用标记/标题/参考文献 |

## 实际处理案例

处理 416 段毕业论文，137 段正文逐段改写：

```
Passed: 5/5
  [OK] Paragraph count: 416
  [OK] Images preserved: 52
  [OK] Citation markers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
  [OK] All headings unchanged (44/44)
  [OK] Reference text unchanged
```

## 改写引擎规则

| 轮次 | 策略 | 技术 |
|------|------|------|
| 第一轮 | 冗余化 | 动词短语扩展、辅助词注入、系统性词汇替换 |
| 第二轮 | 去 AI 味 | AI 模板短语清洗、逻辑连接松散化、冗余精炼平衡 |
| 英文 | 自然化 | 打破学术模板、保留自然粗糙感、克制措辞 |

## 项目结构

```
docx-aigc-reduce/
├── README.md
├── SKILL.md                 # 完整改写规则（中文两轮 + 英文）
└── scripts/
    ├── extract_body.py      # 正文提取
    ├── rewrite_engine.py    # 本地改写引擎
    ├── apply_rewrite.py     # 格式保留写回
    └── verify.py            # 完整性验证
```
