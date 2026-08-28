# 带脚注 PDF / LaTeX → DOCX

[`footnote_to_docx.py`](./footnote_to_docx.py) 把 LaTeX 或有文本层的 PDF 转换成 DOCX。生成的注释是 Word 真脚注：正文包含 `w:footnoteReference`，脚注正文位于 `word/footnotes.xml`；不是页脚文字或手写上标。

## 依赖

- 必需：Pandoc 3.x。
- 含 biblatex 或自定义引证/脚注宏的 LaTeX：需要 TeX Live 中的 `make4ht` 与 `biber`。
- Python：见 `requirements-footnote-to-docx.txt`。
- 含 SVG 的 LaTeX：按 `rsvg-convert` → `mutool` → macOS `sips` 的顺序自动选择 PNG 回退。

安装 Python 依赖：

```bash
python3 -m pip install -r scripts/requirements-footnote-to-docx.txt
```

## 基本使用

```bash
# LaTeX：自动选择 Pandoc 或 make4ht 后端
python3 scripts/footnote_to_docx.py paper.tex -o paper.docx

# 有文本层 PDF：默认严格模式
python3 scripts/footnote_to_docx.py paper.pdf -o paper.docx

# 明确接受 PDF 启发式风险，并在 review JSON 中保留清单
python3 scripts/footnote_to_docx.py paper.pdf -o paper.docx --best-effort
```

默认同时生成 `<输出名>.review.json`。报告记录后端、脚注数量、PDF 配对位置和启发式证据分，以及 DOCX 包结构验收结果。`evidence_score`（兼容字段 `confidence`）不是经过校准的正确概率；即使得分为 `1.0`，仍应结合 marker、编号和警告清单复核。已有输出不会被覆盖；需要覆盖时显式使用 `--force`。

## LaTeX 路径

`--latex-backend auto` 是默认值：

- 普通 `\footnote{...}` 文档直接经 Pandoc AST 转换。
- 出现 biblatex、自定义脚注或引证宏时，优先运行 `make4ht → biber → make4ht`，从 TeX4ht HTML 中合并已经排版的脚注，再交给 Pandoc。这样可保留自定义法学引证格式，而不是让 citeproc 猜测自定义 `.bib` 类型。

自动模式在复杂 LaTeX 编译失败时会停止，不会静默降级为 Pandoc 并改写已排版引文。如果确实接受这种格式变化，必须显式传入 `--latex-backend pandoc`。

可强制指定后端：

```bash
python3 scripts/footnote_to_docx.py paper.tex --latex-backend pandoc
python3 scripts/footnote_to_docx.py paper.tex --latex-backend make4ht
```

直接 Pandoc 后端可声明额外宏：

```bash
python3 scripts/footnote_to_docx.py paper.tex \
  --footnote-command myfootnote \
  --citation-command mycite
```

`\input` / `\include` 默认由 `latexpand` 展开；找不到它时使用内置递归展开器。可以通过 `--reference-doc reference.docx` 控制 Word 样式。

## PDF 路径与严格模式

PDF 通常不保存“正文上标—页底脚注”的语义关系。脚本使用逐字符坐标、字号、基线和脚注分隔线，先独立盘点正文 marker 与页底脚注，再进行一对一、顺序受约束的匹配。它还会识别并剔除跨页稳定的运行页眉页脚，保留无法确定性质的行末连字符，并记录自动修复的跨行 URL。

严格模式是保守验收门：没有检测到任何脚注、存在未配对脚注或疑似 marker、页底小字未得到解释、证据分低于 `--pdf-min-confidence`、检测到双栏或多列表格版面、源编号重置/跳号，或出现 `supra/infra note N` 文字引用时都会停止。`--best-effort` 表示用户明确接受这些风险；审阅报告仍会保留相应清单，不会把它们描述成已验证正确。

这些输入需要人工复核，或先处理后再转换：

- 扫描件：先 OCR；脚本不会假装从无文本层 PDF 恢复脚注。
- 双栏、边注、表格或公式中的上标、符号脚注、跨页脚注、按页重编号；严格模式会对能够检测到的这些情形阻断。
- `supra/infra note N` 等依赖原编号的文字引用。
- 复杂公式、浮动图表、分页、字体与链接不会从 PDF 原样重建；Word 会重新排版。

如果同时拥有 `.tex` 和 PDF，应使用 `.tex` 作为语义来源，PDF 只用于视觉对照。

## 验收与测试

转换结束前，脚本会检查：

- 正文引用 ID 与正脚注定义 ID 完全一致；
- `word/footnotes.xml` 中的分隔符与续页分隔符；
- `document.xml.rels` 中的脚注关系；
- `[Content_Types].xml` 中的脚注类型；
- 源 AST 脚注数量与 DOCX 脚注数量相同；
- DOCX ZIP/XML 完整，且没有内部 marker 残留。

这里的“源 AST 数量一致”只证明写入 Word 的 OOXML 与本次恢复结果一致，不证明 PDF 中未被识别的脚注不存在。PDF 路径的语义风险由严格模式和 review JSON 中的独立证据清单控制。

运行集成测试：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

本项目论文可直接转换：

```bash
make docx PYTHON=python3
make clean-docx
```
