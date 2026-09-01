# 全文扫描总报告：清除—增益执行清单

**对象**：*Who Controls, Who Answers? A Deployment Front Door for High-Impact AI Litigation*（7 个 Part 源文件 + docx 编译全稿 + 70 条脚注 + Tables 1–3）
**基准**：worknote.md 的 9 处插入方案
**性质**：本报告只做扫描与定位，不改动任何源文件。源文件原件在 `../article/`，工作副本在 `source/`。

---

## 〇、执行顺序总览（先清后增）

| 阶段 | 动作 | 依据 |
|---|---|---|
| 第一步 | 修复唯一真正的逻辑冲突：material-change threshold 双重归属（§2 vs Part IV.A） | §一·1 |
| 第二步 | 清除/压缩 6 组冗余回声段落，为插入让位 | §二 |
| 第三步 | 统一术语漂移（12 项，其中 4 项随第一、二步顺带完成） | §三 |
| 第四步 | 按锚点映射执行 worknote 的 9 处插入 | [anchor-mapping.md](anchor-mapping.md) §B |
| 第五步 | 校正 worknote 自身的 3 处归属错误后再动笔引用 | §一·2 |

---

## 一、观点一致性结论

### 1. 确认的实质冲突（只有一处，但必须先修）

**material-change threshold 被设定了两次。**

- designation 侧（三处一致）：03 L13（Part II.A）/ 03 L139（§ 1 条文："The designation shall identify the … material-change threshold"）/ 03 L141（§ 2 末句："The designation supplies the retention period and material-change rule."）
- operator 侧（冲突源）：05 L34（Part IV.A）："The control sheet should identify which changes require renewed evaluation or approval and which enter a lower-burden change log." 通段未提 designation 的先在设定；Table 3 第一行也把 "material-change threshold" 列为 control sheet 组件。

读起来的效果：operator 自设阈值 → 可博弈 metric（把一切变更路由进低负担日志）。worknote 的诊断完全正确。
**修法**：05 L34 改为"control sheet 适用 designation 所定阈值"（= worknote 插入 9），并同步 Table 3 第一行措辞。§ 1、§ 2、Part II.A 三处 designation 侧无需改动。

### 2. worknote 对现有稿的断言：9 项核验，8 项属实，3 处归属需校正

属实且可直接依赖的：level-neutrality 三处均为从句（01 L21 / 03 L195 / 06 L34）；"some losses have no private remedy"（06 L10）；gateway 句（03 L28）；"closed manifest"（05 L40）；control-sheet 段（05 L34）；IV.E minimization 确实在 Table 3 之后约 28 段；Part V 确为四个 boundaries；V.C 领土让步（06 L32）；加州 SB 243 脚注承认"有形式无规则"（03 L21 脚注）。

**三处归属错误（动笔前必须校正，否则答复信/修改稿会引错位置）：**

| worknote 的说法 | 实际情况 |
|---|---|
| Table 1 把 mandatory updates 等视为保留 lane 的证据 "despite contract language…"（p. 22） | 该引文在 Table 1 **之前的正文段**（03 L57）和**之后的正文段**（03 L83，cross-tenant disabling）；Table 1 行内只有 "consistent exercise in practice" |
| § 8 说 "Independently relevant operational conduct retains only the effect governing law gives it"（p. 22） | 该句在 **Part II.C 正文**（03 L59）；§ 8 条文（03 L157）的对应表述是 "Governing law supplies every element and defense and determines the independent relevance, if any, of operational conduct." |
| FCRA § 1681m(h)(8) 排除私人诉权"只是脚注"（p. 51） | 排除规则就在**正文**（05 L96），脚注仅引法条；但"文章比其最近国内模型更 person-facing 这一点全文未明言"属实 |

另：worknote 的 "n. 19" 与当前编译稿脚注编号不符（该脚注现为 fn 145），引用时用内容定位。

### 3. 与插入方案的关系

- 插入 3（EU AI Act Art. 86 comparator）与插入 4（法德 pre-action 程序）是**纯新增**——全文目前无任何 EU AI Act / 民法法系内容，无旧文冲突。
- 插入 2 会立即"证伪"两处枚举句（见 §二 C-2、C-3），这两处必须先改写再插入，不能并置。

---

## 二、清除清单（冗余回声与待改写段落）

按处理强度排序。**每条均已核验原文**，位置 = tex 文件行号（docx 段落号）。

### 必改（与插入直接联动）

- **C-1【改写】05 L34（P0216）Part IV.A control-sheet 段** — 唯一逻辑冲突，见 §一·1。→ 衔接插入 9。
- **C-2【改写】05 L74（P0236）Part IV.D 开篇句** "Three regimes perform distinct comparator roles…" — 插入 3 新增第四个 comparator 后即刻过时；同时缺插入 2 的"三者皆 national regimes"说明。05 L98 收尾段同步改。→ 衔接插入 2+3。
- **C-3【改写】06 L4（P0256）Part V 开篇枚举句** "Four boundaries make that allocation durable…" — 插入 6 加第五个 boundary 后过时。→ 衔接插入 6。
- **C-4【压缩】05 L34 段末两句（P0217）** "The completed form creates no merits inference; the underlying operational records retain only the effect governing law gives them." — 与 03 L59（P0103）近乎逐字重复的 merits-firewall 回声。压成一句交叉引用即可。与 C-1 同段，一并改写。
- **C-5【压缩】03 L57 末句 + 03 L83 第三句（P0102、P0109）** — slicing / cross-tenant disabling / 合同标签不决定论的分析。插入 7 的新 II.E 小节将系统重述并引用这些内容，不压缩则 II.C 与 II.E 双重覆盖。保留两段的 definitional 部分。→ 衔接插入 7。
- **C-6【扩写】02 L55（P0054）Part I.C 州诉前综述段首尾句** — 纯国内框架需开口容纳法国 CPC art. 145 与德国 ZPO §§ 485–494a。→ 衔接插入 4。

### 可删（纯冗余，删除无损论证）

- **C-7【删】Part I 内 "record never created cannot be reconstructed" 三连回声中的两处**：02 文件 P0048 末句、P0050 末句。主陈述保留 02 的 P0041 一处；Introduction（01 L25）与 IV 开头（05 L4）、Conclusion（07）各保留（功能不同）。Abstract 内同样重复两次（P0004、P0006），删一处——摘要在主控 tex 中，不在本目录。
- **C-8【删】Introduction 脚注（fn 22）内整句复述 Yu et al. 559 份意见书研究** — 主陈述在 02 的 I.D（P0059 + fn 122），脚注内整句为纯回声。
- **C-9【压缩】03 II.D.iii（P0122–123）对 Stage One/Two 的再定义句** — 与 03 L38（P0090）重叠，压为交叉引用。

### 明确保留（勿误删）

- 三处 level-neutrality 顺带句（01 L21 / 03 L195 / 06 L34）——插入 1 明确以它们为支撑（"pp. 5, 35 and 57 already assume it"）。
- 03 L28（gateway 句）、05 L96（FCRA）、06 L10（no private remedy）——插入将引用这些锚点。
- Garcia 程序姿态三处（P0013 / P0173 / P0274）与 "information asymmetry decides the case" 首尾呼应（P0027 / P0280）——功能各异或刻意呼应，保留。

---

## 三、术语一致性结论

完整 40 条术语台账见 [terminology-audit.md](terminology-audit.md)。要点：

**好的消息**：§ 2/§ 4/§ 5/§ 6/§ 8/§ 9/§ 11 的全部条文交叉引用（正文 4 处 + 模型条文内部 8 处）逐条核对**无一指向错误**；docx 与 tex 逐字同步，可放心只改 tex。

**需要统一的漂移（12 项，按优先级）**：

1. **manifest 三名并存**：§ 2 "local record"（03 L141）/ Part IV.A "control sheet" / Part IV.B "closed manifest"（05 L40），外加 "local manifest"（04 L75、06 L32）与 "minimum manifest"（05 L104）——从未互相等同。这是除 material-change 外最伤的一处：读者无法确认三个名字是否同指一物。建议确定一个法定名（如 § 2 用词）+ 一个描述名，全文统一并在首次并置处写明等同关系。
2. **deployment-record duty 双重定义**：01 L25 与 03 L94 各定义一次，删其一。
3. **第二失败四种命名**：01 L7 "deployment-record failure" / 02 L6·L24 "record availability" 坐标 / 02 L28 "the production problem"（与 02 L30 "the actor-identification problem" 不平行）/ 04 L4 "record-production application"。
4. **事件标识符五名**：event identifier（05 L42 定义）/ event key（04 L65）/ run identifier、unique incident identifier（02 L47）/ common event identifier（03 L40 与 § 4）。统一为 § 4 用词。
5. **触发文书/触发事件各五名**：sworn declaration（§ 3）vs verified notice / front-door notice / compliant request / compliant identity request；adverse event（§ 3）vs verified covered event（01 L23、07 L5）vs covered occurrence（03 L32）。
6. **designation 内容清单三处不一致**：01 L23（含 "trigger"）/ 03 L13（含 "claimant threshold"+"material-change rules"）/ § 1（10 项，无 trigger/claimant threshold）。与 §一·1 联动，修 C-1 时一并统一。
7. **affected person（法定术语，24 次）vs claimant/requester 混用**；first-answer duty vs obligation（02 L111）；minimum answer（06 L14）vs first answer。
8. **Stage One/Two 先用后定义**（02 L60 早于 03 L30 的定义）；gateway（9 次）、safe exit（10 次）无定义点；"field dictionary" 全文未出现——worknote 使用的这个词在稿中实为 **data dictionary**（05 L44），写插入文时用稿内术语。
9. 一次性替代说法：01 L17 "reachable first recipient"、01 L13 "identity-and-event stage"、03 L4 "prompt exit"。
10. non-de-minimally（4 次）vs non-de-minimis（03 L63，1 次）；§ 3(d) 与 03 L30 第 4 项措辞不一。
11. **Table 1–3 全文无正文 `\ref` 引用**（有 `\label`）；Table 3 标题 "Minimum Deployment-Record Infrastructure" 与正文术语 "control sheet" 不一致。
12. docx 中 Table 1/2 以图片嵌入（无法文本核对字面）、Table 3 为原生表格——编译注意项，非内容问题。

---

## 四、九处插入落点速查（来自 anchor-mapping.md）

| # | worknote 位置 | tex 落点 | 前置清除动作 |
|---|---|---|---|
| 1 | Part II.A p.18，五条标准后 | 03 L15 之后 | 无（顺带句保留） |
| 2 | Part IV.D p.49 开篇句 | 05 L74 | C-2 改写同处 |
| 3 | Part IV.D p.51，FCRA 后 | 05 L96 之后 | C-2 改写枚举句 |
| 4 | Part I.C p.13 州诉前综述 | 02 L55 | C-6 扩写首尾句 |
| 5 | Table 3 lead-in p.44 | 05 L10 与 L12 之间 | 无 |
| 6 | Part V p.55 第五 boundary | 06 L34 之后（或并入 V.C） | C-3 改写枚举句 |
| 7 | Part II.E p.27 新小节 | 03 L130 之后、L132 之前 | C-5 压缩 II.C 两处 |
| 8 | Model Act § 4 加一款 | 03 L145 | 新增后在 § 1 清单（03 L139）补 "form" |
| 9 | Part IV.A p.46 control-sheet 段 | 05 L34 | = C-1，同一次改写完成 |

**写作注意**：插入文使用稿内既有术语（data dictionary 而非 field dictionary；§ 4 的事件标识符用词）；引用稿件内部位置时按 §一·2 校正后的真实归属。

---

## 五、局限声明

- docx 提取文本无分页信息，worknote 页码→tex 位置的映射基于内容锚定（多为逐字引用），页码本身不可核。
- 摘要、关键词、目录在主控 tex（`../what-is-ai-for-courts.tex`）中，不在本次扫描的七个文件内；Abstract 内一处重复（C-7）需到主控文件处理。
- Table 1/2 在 docx 中为图片，其字面内容未与 tex 核对（标题一致）。
- *Majoritarian Signals* 的页码锚点（MS p. xx）不在本仓库，未核验。
