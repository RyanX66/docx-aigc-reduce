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
# 1. 提取正文
python scripts/extract_body.py 论文.docx body.json

# 2. 逐段改写正文（按 SKILL.md 中的两轮改写规则）→ 生成 rewrite_mapping.json

# 3. 写回 .docx
python scripts/apply_rewrite.py 论文.docx rewrite_mapping.json 输出.docx

# 4. 验证
python scripts/verify.py 论文.docx 输出.docx
```

## 脚本

| 脚本 | 功能 |
|------|------|
| `extract_body.py` | 提取正文段落，跳过标题/目录/图片/参考文献/致谢 |
| `apply_rewrite.py` | 改写文本写回 .docx，保留 run 级格式 |
| `verify.py` | 5项验证：段落数/图片数/引用标记/标题/参考文献 |

## 验证结果示例

```
Passed: 5/5
  [OK] Paragraph count: 416
  [OK] Images preserved: 52
  [OK] Citation markers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
  [OK] All headings unchanged
  [OK] References unchanged
```

## 改写规则（SKILL.md 内置）

- **中文第一轮**：增加冗余解释、系统性词汇替换、句式口语化
- **中文第二轮**：清除 AI 模板套话、松散化逻辑连接、冗余精炼平衡
- **英文规则**：打破模板化学术表达、自然化句式、保留适度粗糙感
