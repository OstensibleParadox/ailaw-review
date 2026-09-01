# 术语一致性审计报告
## 《Who Controls, Who Answers? A Deployment Front Door for High-Impact AI Litigation》（Harv. J.L. & Tech. 投稿草稿）

审计范围：`source/01-introduction.tex` – `07-conclusion.tex`（七个 Part 工作母本）、`before-the-merits-extracted.txt`（docx 编译全稿正文，带 [P0000|style] 段落编号）、`before-the-merits-footnotes.txt`（70 条脚注）、`before-the-merits-tables.txt`（表 1–3）。所有次数为七个 tex 文件（正文+内嵌脚注）内不区分大小写的出现次数；docx 另含 abstract/TOC/keywords 前置件，会略增计数。所有引文均为审计中实际读到的原文。

---

# (A) 术语台账

| # | 术语 | 首次定义位置（tex） | 使用次数 | 主要变体 | 是否漂移 |
|---|------|--------------------|---------|---------|---------|
| 1 | pre-merits attribution gap | 01:7（`\term`） | 2（+"attribution gap" 4：01:29、03:4 等） | the attribution gap / the gap | 否 |
| 2 | actor-identification failure / deployment-record failure | 01:7（两个 `\term`） | 1+1 | actor-identification problem（02:30）/ the production problem（02:28）/ record-production application（04:4） | **是**（见 B-4） |
| 3 | actor-identity / record-availability coordinates | 02:6（叙述性引入） | 各 1（连字符形容词）+ 02:24 名词形各 1 | actor identity and record availability（不连字符） | 轻度（见 B-4） |
| 4 | computational / system / organizational opacity | 02:12（三个 `\term`） | 各 1–2 | black box（02:14，作为被批评的混同说法） | 否 |
| 5 | deployment front-door rule / front door | 01:23（`\term{deployment front-door rule}`） | front door 35 + front-door 18 | the front door / front-door rule / front-door role（5）/ front-door notice（2）/ front-door function（04:4、05:15、05:88）/ front-door architecture（03:19、06:34）/ front-door problem（02:45）/ front end（01:19、02:57 标题）/ Deployment Front Door（标题名词形） | 轻度（名词/形容词分工可接受；"front end" 近义未说明，见 B-9） |
| 6 | designation | 03 II.A（`sec:designation`，03:8–13）；§ 1（03:139） | 31 | sectoral designation / legislative designation / the designation / designated deployment | 否（但 designation 内容清单三处不一，见 B-7） |
| 7 | high-impact AI | 标题 + 01:13 | high-impact 3 + high impact 2 | "High impact"（03:11）/ high-impact purpose（03:57）/ High-impact decisions（03:100）/ high-impact deployment（abstract P0005） | 轻度 |
| 8 | affected person | 03:28 语境定义；§ 1 "affected persons"（03:139） | 24 | affected persons / affected people（02:4）/ claimant（01:5、02:24、03:130 等）/ requester（03:36、§ 6 等） | 轻度（claimant/requester 与法定术语混用，见 B-8） |
| 9 | visible operator | 03:28（`\term`） | 18（+"the operator" 39 作简称） | covered operator（5：03:17、03:23、03:98、05:48、06:28）/ gateway / reachable first recipient（01:17，一次性） | **是**（covered operator、gateway、first recipient 未与 visible operator 明示等同，见 B-2、B-9） |
| 10 | gateway | 无 `\term` 定义；最近定义点 03:28 "Its gateway role" | 9 | gateway role（2）/ visible-operator gateway（03:6、fn 111）/ the gateway（03:38、03:130）/ private-actor gateway（05:94） | **是**（未定义同义词，见 B-9） |
| 11 | Stage One / Stage Two | 操作性引入 03:30 / 03:42；§ 3 / § 7 | 37 / 15 | identity-and-event stage（01:13，一次性）/ bounded Stage Two inquiry（03:63）/ Coordinated Stage Two（04:86 标题） | 轻度（02:60、02:62 先于定义使用，见 B-9） |
| 12 | first answer | 03:38（`\term`） | 23 + first-answer 15 | fixed first answer（01:15）/ fixed identity-and-event answer（01:23）/ closed first answer（02:30、06:4）/ statutory first answer（03:124）/ first-answer duty（03:34 等）/ first-answer obligation（02:111）/ minimum answer（06:14） | 轻度（duty/obligation、minimum answer 变体，见 B-8） |
| 13 | event receipt | 03:38（`\term`） | 5（+abstract 1） | the receipt（§ 4、03:195）/ fixed receipt（03:181、03:189、03:191） | 轻度 |
| 14 | custodian map | 03:38（`\term`） | 5（+abstract 1） | the map（§ 4）/ deployment, event, custodian, and control map（02:62）/ control map（06:42） | 轻度 |
| 15 | covered control holder | § 1（03:139，定义句） | 12 | control holder（01:13、05:40、06:32 等简称）/ covered enterprise（03:47、03:65） | 否 |
| 16 | control lane(s) | 无 `\term`；隐含于 § 5 | 13 | claim-specific lane（01:23、03:42）/ AI-specific lane（03:130、04:90）/ custody lanes（02:34）/ material-control lane（07:5）/ assigned lane / wrong lane（04:88） | 轻度 |
| 17 | material control | 03 II.C 标题（03:44）+ 三要件（03:49–53）；§ 5 | 9 + material-control 6 | material-control routing rule（fn 111）/ material-control test / material-control lane（07:5） | 否（轻度） |
| 18 | risk specificity / practical authority / information materiality | 03:49 / 03:51 / 03:53（各 `\term`） | 3 / 8 / 5 | II.C 标题作 "Risk, Authority, and Information Materiality" 与要件名 "risk specificity" 不对称；practical ability（02:51，Rule 34 语境） | 轻度 |
| 19 | non-de-minimally | 03:53 | 4 | non-de-minimis（03:63，1 次） | **是**（形态不一，见 B-10） |
| 20 | safe exit | 无 `\term`；最近定义点 03:130 "Safe exit is the reciprocal limit" | 10 | prompt exit（03:4）/ exits the front-door role（01:23）/ terminates the special role（02:32）/ safe exit its intended economy（03:85） | **是**（无正式定义点 + prompt exit 变体，见 B-9） |
| 21 | deployment-record duty | 01:25（`\term`）**和** 03:94（再次 `\term`） | 3（+record duty 03:65 ×2、05:4） | deployment-record duty / the record duty / record-duty holder（03:65）/ operating duty（04:84） | **是**（双重定义，见 B-3） |
| 22 | deployment record | 无独立 `\term`（由 #21 义务条款带出） | 13 + deployment-record 7 | deployment-record failure（01:7）/ deployment-record production（02:111） | 否 |
| 23 | deployment-control cascade | 01:25（`\term`） | 8（含 the cascade 简称、02 § I.E 标题、Figure 1） | the cascade | 否 |
| 24 | cascade 四层（authority and resources 等） | 02:76–79（四个 `\term`） | 各 1–2 | — | 否 |
| 25 | retrieval right / contractual retrieval right | 03:96–98 制度性引入；§ 2 "a contractual right to retrieve"（03:141） | retrieval right 6 + retrieval path 3 | contractual rights to retrieve（03:96）/ usable retrieval right（03:98）/ predeployment retrieval right（06:30）/ retrieval architecture（03:96、03:193）/ contractual retrieval and preservation path（03:38）/ contractual retrieval path（06:32）/ retrieval obligation（§ 4） | 轻度-中度（变体多但指向同一制度） |
| 26 | merits firewall | 03:59（`\term`）；§ 8 标题 | 5（+abstract 1） | — | 否 |
| 27 | minimum record | 01:17；§ 1 列举（03:139） | 15 | minimum deployment record（fn 111、07:5）/ operational minimum record（04:79 标题）/ operational minimum（04:84）/ minimum field（05:104）/ minimum supplier fields（05:48）/ minimum answer（06:14） | 轻度-中度 |
| 28 | local record（§ 2 术语） | § 2（03:141） | 6 | closed local record（03:96）/ local manifest（04:75、06:32） | **是**（与 control sheet、manifest 三词并存，见 B-1、B-2） |
| 29 | control sheet | 05:8–10（IV.A 标题+首句）；预告 02:109 | 6 | minimum control sheet（02:109）/ written control sheet / the approved control sheet（05:32）；Table 3 标题作 "Minimum Deployment-Record Infrastructure" | **是**（见 B-2、B-11） |
| 30 | closed manifest | 05:40 | 1（+manifest 总计 9） | local manifest（04:75、06:32）/ minimum manifest（05:104）/ the manifest（05:46、05:50、05:52） | **是**（同一物四个限定词，见 B-2） |
| 31 | standard interface | 05:38（IV.B 标题） | 1（标题） | The interface（05:44、05:48）/ information plane（05:40，一次性）/ sectoral data dictionary（05:44） | 轻度（标题术语正文未复现） |
| 32 | data dictionary | 05:44 | 1 | sectoral data dictionary。**"field dictionary" 全文未出现** | 否 |
| 33 | deployment identifier / component-version identifier / event identifier | 05:42（三个 `\term`） | 2 / 1 / 13 | deployment ID（5：05:32、05:40、05:64 等）/ event key（04:65）/ run identifier（02:47）/ unique event identifier（02:47）/ unique incident identifier（02:47）/ common event identifier（03:40、§ 4） | **是**（见 B-5） |
| 34 | identity record / feedback record / event record（三种 record clocks） | 05:58 / 05:60 / 05:62（各 `\term`） | 4 / 2 / 7 | different clocks（05:54 标题）/ separate record clocks（05:6） | 否 |
| 35 | 触发文书（§ 3 的 declaration/notice） | § 3（03:143）"a sworn declaration or declaration under penalty of perjury" | sworn declaration 1 / verified notice 3 / compliant request 4 | verified front-door notice（03:104）/ front-door notice（04:17、05:32）/ compliant identity request（02:53）/ verified covered event（01:23、07:5） | **是**（见 B-6） |
| 36 | 触发事件（adverse/covered event） | § 3(a)（03:143）"an adverse event" | adverse event 9 / covered event 3 | verified covered event（01:23、07:5）/ verified adverse event（abstract、06:8）/ covered occurrence（03:32）/ covered event（03:181 等） | 轻度（见 B-6） |
| 37 | occurrence threshold / claimant threshold | 03:30 / 03:13 | 3 / 1 | the threshold（04:15）/ Stage One occurrence threshold（§ 6） | 轻度（claimant threshold 仅 03:13 出现一次，见 B-7） |
| 38 | 救济四档 | 03:124–127（四个 `\term`）；§ 9 | 各 1 | — | 否 |
| 39 | two-stage rule | 01:29 | 1 | Stage One/Stage Two（见 #11） | 否 |
| 40 | ex ante (duty/record) | 01:17、01:25 | 约 7 | ex ante minimum record / ex ante deployment-record duty / ex ante duty / ex ante state-law duty（03:6）/ ex ante event and control record（05:96） | 否 |

---

# (B) 漂移 / 冲突清单

## B-1 【实质冲突，最高优先】material-change threshold 的设定主体：designation（§ 1/§ 2）vs operator 的 control sheet（Part IV.A）

- **位置 1a**：`03-front-door-rule.tex`，Part II.A "Sectoral Designation Defines the Field"（第 13 行；docx [P0081]）：
  > "The proposed statute therefore applies only when a legislature has specified the protected interests, visible operator, minimum record, **retention and material-change rules**, claimant threshold, and remedy."
- **位置 1b**：`03-front-door-rule.tex`，Model Act § 1（第 139 行；docx [P0139]）：
  > "The designation shall identify the covered function, protected interests, visible operator, affected persons, minimum record, retention period, **material-change threshold**, administering authority, enforcement route, and civil-penalty ceiling."
- **位置 1c**：`03-front-door-rule.tex`，Model Act § 2 末句（第 141 行；docx [P0140]）：
  > "**The designation supplies the retention period and material-change rule.**"
- **位置 2a**：`05-record-infrastructure.tex`，Part IV.A "The Deployment-Record Control Sheet"（第 10 行；docx [P0213 附近]）：
  > "Before release, **the operator should adopt a written control sheet** for each designated deployment, version family, operating context, and risk category."
- **位置 2b**：同文件 Table 3（`tab:control-sheet`，第 22 行；表文件 TABLE 2 第一行）：control sheet 的 "Identity and scope" 组件包含 "…vendors; limits; **material-change threshold**"。
- **位置 2c**：同文件第 34 行（docx [P0216]）：
  > "The material-change threshold is especially important for learning and composite systems. … **The control sheet should identify which changes require renewed evaluation or approval** and which enter a lower-burden change log."
- **问题**：§ 1/§ 2 及 Part II.A 三处一致地把 material-change threshold/rule 列为 **designation（立法机关/授权机构）** 的列举事项；Part IV.A 三处则把它作为 **operator 在 release 前自行制定的 control sheet** 的内容，且 IV.A 通段未提 designation 对该阈值的先在设定。读者无法判断：阈值到底是法定的（operator 只能执行），还是 operator 自定的（designation 只要求"有一个阈值"）。
- **建议**：采分层表述并互相指向——§ 1 改为 designation 设定 "the criteria or minimum content of the material-change threshold"，Part IV.A 第 34 行处加一句，明示 control sheet 的阈值是 "applying the designation's material-change rule to this deployment"。或反向：若意图是 operator 自定，则删去 § 1 清单中的 "material-change threshold" 并在 § 2 改为 "a material-change rule consistent with the designation's criteria"。两种修法都必须同时改 § 1、§ 2 末句、Part II.A 第 13 行三处，保持同源。

## B-2 【术语三元并存，未互相等同】§ 2 "local record" vs Part IV.A "control sheet" vs Part IV.B "closed manifest"（另有 local/minimum manifest）

- § 2（03:141）："the visible operator shall create and maintain **a local record** identifying the system and versions; …"
- 02:109（Part I 末）："Part IV translates those questions into **a minimum control sheet**."
- 05:40（IV.B）："The visible operator keeps **a closed manifest**: deployment ID; covered purpose and population; application and model versions; material components and suppliers; record custodians; risk and release owners; relevant contract rights; and the event schema…"
- 04:75："The employer keeps **the local manifest**, position definition, customer settings, application, downstream review, disposition, notice, and event identifier."
- 06:32："The domestic visible operator nevertheless owes **the local manifest**, event receipt, and contractual retrieval path."
- 05:104："The operator keeps **a minimum manifest** rather than raw content by default."
- **问题**：同一 § 2 本地记录至少有三个名字（local record / control sheet / manifest），manifest 又有 closed/local/minimum 三个限定词；全文没有一句话说明三者关系（是同一物的表单/索引两面？还是三个不同层级？）。04:75 与 06:32 的 "local manifest" 是 hybrid 写法，进一步混淆。
- **建议**：在 IV.A 首段或 IV.B 首句加一句等同条款，例如 "The control sheet (Section 2's 'local record') is maintained as a closed manifest: …"；此后统一：法条与程序语境用 "local record"，表单样态用 "control sheet"，运行时索引用 "manifest"，并固定 manifest 的限定词（建议 "closed manifest"，删 local/minimum manifest）。

## B-3 【双重定义】deployment-record duty 被 `\term` 定义两次

- 01:25："the proposal also imposes an ex ante **\term{deployment-record duty}**. The record identifies versions, risk and approval authority, evaluations, unresolved risk decisions, material changes, complaints, incidents, interventions, custodians, and retrieval rights."
- 03:94（Part II.C.1；docx [P0114]）："**\term{deployment-record duty}** arises before a covered deployment affects the public. The visible operator has a nondelegable local duty to identify …"
- **建议**：保留 03:94 为正式定义（与 § 2 相邻），01:25 去除 `\term` 标记改为普通指称。另注意 03:65 的简称 "The record duty supplies …" / "the record-duty holder"，建议首次简称处括注。

## B-4 【三层命名不一】"两种失败"在 Introduction、Part I.B、Part I.E、Part III 各有名字

- 01:7："The first is an **actor-identification failure** … The second is a **deployment-record failure** …"
- 02:6 / 02:24：坐标轴作 "**actor-identity and record-availability** coordinates" / "Actor identity and record availability are independent coordinates"。
- 02:28（第二构型）："This is **the production problem**."；02:30（第三构型）："This is **the actor-identification problem**."
- 02:111："**Actor-identification** asks which enterprise occupied a risk-specific control lane. **Deployment-record production** asks for the bounded materials …"
- 04:4："*Garcia* is **the record-production application** …"
- **问题**：第二失败在四个位置分别叫 deployment-record failure / record availability / the production problem / record-production application；其中 02:28 的 "the production problem" 与 02:30 的 "the actor-identification problem" 并列时命名体系不平行（一个按环节、一个按主体）。
- **建议**：统一以 01:7 的两个 failure 名称为锚，02:28 改为 "This is the deployment-record (production) failure."，04:4 改 "the deployment-record application" 或括注对应。

## B-5 【标识符变体簇】event identifier（05:42 定义）vs event key / run identifier / unique incident identifier / common event identifier

- 05:42（`\term` 定义）："An **event identifier** connects an affected person or consequential decision to the versions and records that governed it."
- 02:47（Strike 3 语境）："a unique **event identifier**" 与 "a unique **incident identifier**" 同段混用；同段还有 "the operator does not retain the feature or **run identifier**"。
- 04:65："the best available **event key**—a requisition number, application ID, tenant URL, or timestamp."
- 03:40 与 § 4（03:145）："the **common event identifier**"。
- 另有 deployment identifier（05:42）vs **deployment ID**（05:32、05:40、05:64，共 5 次）全称/简称混用。
- **建议**：全文以 "event identifier" 为通称；跨主体共享时用 "common event identifier" 并在 05:42 定义句内引入该短名；04:65 的 "event key" 改为 "event identifier"（或括注 "the applicant-facing event key"）；02:47 的 "run identifier" 改为 "run/event identifier"；"incident identifier" 改 "event identifier"。deployment ID 在首次出现后统一简称即可（现状可接受，但建议 05:32 处括注 "deployment ID"）。

## B-6 【触发文书与触发事件称谓漂移】§ 3 的 declaration vs 散文的 verified notice / front-door notice / compliant request；adverse event vs covered event

- § 3（03:143）："An affected person may deliver to the visible operator's designated agent **a sworn declaration or declaration under penalty of perjury** identifying: (a) **an adverse event** …"（"sworn declaration or declaration under penalty of perjury" 本身亦属冗余并列）
- 散文侧：03:30 "A **verified notice** identifies: (1) **an adverse event** …"；03:104 "A **verified front-door notice** …"；04:17、05:32 "**front-door notice**"；03:124、§ 9 "**compliant request**"；02:53 "a **compliant identity request**"；05:70 "The **verified notice** described in Part II"。
- 事件侧：01:23、07:5 "a **verified covered event**"；abstract [P0005]、06:8 "a **verified adverse event**"；03:32 "a **covered occurrence**"；§ 3(a)、03:30 用 "adverse event"。
- **建议**：在 § 3 引入短名（"such declaration, a 'verified notice'"），其后散文统一用 verified notice；"compliant request" 仅在救济/时效语境（03:124、§ 9）保留或同步改注。事件统一为 "covered adverse event"（§ 3(a) 与 01:23、07:5、abstract 对齐），删 "covered occurrence"。

## B-7 【designation 内容清单三处不一致】trigger / claimant threshold / material-change threshold 是否属于 designation

- 01:23（7 项）："a legislative designation of **the protected interest, covered deployment, visible operator, minimum record, retention period, trigger, and remedy**"——含 "trigger"，无 material-change threshold、无 affected persons。
- 03:13（7 项）："the legislature has specified **the protected interests, visible operator, minimum record, retention and material-change rules, claimant threshold, and remedy**"——"trigger" 变成 "claimant threshold"，多出 material-change rules，无 covered deployment。
- § 1（03:139，10 项）："**the covered function, protected interests, visible operator, affected persons, minimum record, retention period, material-change threshold, administering authority, enforcement route, and civil-penalty ceiling**"——既无 "trigger" 也无 "claimant threshold"，多出 affected persons、administering authority、enforcement route、civil-penalty ceiling。
- **建议**：以 § 1 为权威清单，01:23 与 03:13 改写为与之对齐（或明示为"主要事项"并加 "among other elements"）。注意这与 B-1 联动：material-change threshold 若在 § 1 清单中保留，则 B-1 必须按"designation 定标准"方向修。

## B-8 【角色称谓混用】法定术语 affected person vs claimant / requester；first-answer duty vs obligation；minimum answer vs first answer

- "claimant"：01:5、02:24、02:32、03:13（claimant threshold）、03:130 等；"requester"：03:36、§ 6、02:62（requester–producer relation）等；法定术语 "affected person" 24 次。
- 02:111 "a **first-answer obligation**" vs 03:34、§ 3、§ 10 "**first-answer duty**"（多处）。
- 06:14 "The **minimum answer** is transaction linked and principally factual" vs 全文 "first answer"（23 次）。
- **建议**：程序散文中统一 "the affected person"（或首次出现后固定一个短名）；02:111 改 "first-answer duty"；06:14 改 "The first answer"（或 "minimum first answer"）。

## B-9 【先用后定义 / 无定义同义词】Stage One·Stage Two、gateway、safe exit、first recipient、front end

- **Stage One/Stage Two** 首次出现于 02:60、02:62（"Once Stage One supplies that map … one bounded form of Stage Two testing"），操作性定义在 03:30/03:42；Introduction 01:13 另用一次性说法 "a bounded **identity-and-event stage**"。
- **gateway** 用 9 次（含 03:28 "Its **gateway role**"、03:38 "The **gateway** then supplies"、03:130 "The **gateway obligation**"、03:6 "the **visible-operator gateway**"、05:94 "a private-actor **gateway**"），从未 `\term` 定义，实质是 visible operator 角色的同义词。
- **safe exit** 用 10 次，无 `\term` 定义点（最近的定义句是 03:130 "Safe exit is the reciprocal limit"）；03:4 用一次性变体 "a **prompt exit**"。
- 01:17 "a reachable **first recipient**" 为全文唯一一次，其后全部由 visible operator 承担该概念。
- **front end**：01:19 "The front door supplies the missing **front end**"；02 § I.D 标题 "Existing Evidence Rights Need a Deployment **Front End**"——与 front door 的近义分工（缺口侧 vs 规则侧）只有 01:19 一句暗示。
- **建议**：03:28 定义 visible operator 时括注 "its gateway role"；03:130 给 safe exit 加 `\term` 或加粗定义句；03:4 的 "prompt exit" 改 "safe exit"；01:17 的 "first recipient" 改 "visible operator"；01:13 的 "identity-and-event stage" 改 "Stage One"（或 "the first stage"）；01:19 处可用半句话点明 "front end（缺口侧）/front door（规则侧）" 的对仗。

## B-10 【形态/拼写微漂移】

- **non-de-minimally**（03:53、§ 5(c)、03:63 前半、Table 1 第三行，4 次）vs **non-de-minimis**（03:63 后半 "bears no non-de-minimis relation"，1 次）。建议统一（法律英语通例为 "de minimis"；作副词自造形式建议统一为 "non-de-minimally" 或改写为 "bears on … in more than a de minimis way"）。
- **§ 3 六项与 03:30 六项的第 4 项措辞不一**：03:30 "(4) the relevant **time**, transaction, account, decision, or **interaction**" vs § 3(d) "the **event**, transaction, account, **application**, decision, or **period**"。建议以 § 3(d) 为准改 03:30。
- high impact / high-impact、deployment ID / deployment identifier、"the operator"（39 次简称）等属可接受的语法分工，不列为漂移，仅提示保持现状即可。

## B-11 【条文与图表引用核查】

- **§ 编号指向一致性（结论：全部一致）**：model act 共 § 1–§ 11。正文（模型条文之外）的数字引用只有 4 处，全部指向正确内容：03:34 "model Act **section 7** supplies the separate boundary after a federal action … is pending"（§ 7 确为联邦边界条）✓；03:181 "**Model Act sections 3 and 10** make that line operative"（§ 3/§ 10 确为 no-condition-precedent 条）✓；03:191 "the record that model Act **section 2** already required" 与 "**Sections 7 and 10** state the boundary" ✓；03:193 "**Model Act section 2** creates a contractual right to retrieve supplier fields" ✓。模型条文内部交叉引用（§ 4→"Section 7's protections"、"Section 2's contract"；§ 5→"Section 2's contract"；§ 6→"violation of Section 2"；§ 8→"Section 4 duties"/"Section 5 requirement"；§ 9→"Section 8 governs"；§ 11→"delivery under Section 3"）经逐条核对均指向正确。**§ 5(b) 在散文中从未被按号引用**（其 practical authority 要件均以文字指称），无冲突。
- **用户假设的"control sheet 被一处归给 § 4、另一处归给 designation"：未检出**。control sheet 全文只出现于 02:109（预告 Part IV）与 05（Part IV.A），无任何位置把它编号归给 § 4 或 designation。真实存在的归属冲突是 B-1（material-change threshold）与 B-2（local record/control sheet/manifest 未等同）。
- **引用风格不一（轻度）**：03:34 "model Act section 7"（小写）vs 03:181 "Model Act sections 3 and 10"（大写）vs 03:191 "Sections 7 and 10"；"Model Act"（2 次）/"model Act"（3 次）/"model act"（06:26，1 次）大小写三种并存。另注意同号相邻的外部条文：05:86 "The Federal Trade Commission's 2025 **section 6(b)** study"（FTC Act）、06:30 "**Federal Arbitration Act section 7**"（FAA § 7）、05:96 "**section 1681m(h)(8)**"（FCRA）——均有限定词、不构成错误，但与 model act § 6/§ 7 同号，建议保持限定词不脱漏。
- **Table 1–3 无任何正文引用**：三个 tex 表只有 `\label{tab:…}`，全文无 `\ref{tab:…}`，正文（含 docx）不出现 "Table 1/2/3" 字样。建议在各表所在小节正文加 "Table N" 指引句。
- **Table 3 标题与正文术语不一致**：05:10 正文称该物为 "control sheet"，而 Table 3 标题为 "**Minimum Deployment-Record Infrastructure**"（05:13；docx [P0214]）。建议改题 "Minimum Deployment-Record Control Sheet" 或在 IV.A 明示二者同一（与 B-2 联动）。
- **docx 样式层**：docx 中 Table 1、Table 2 的题注样式为 "Image Caption"、Table 3 为 "Table Caption"（before-the-merits-extracted.txt [P0108]、[P0182]、[P0214]），投稿前宜统一。

## B-12 【tex 与 docx 编译稿的术语层一致性（结论：一致）】

- docx 正文与七个 tex 文件逐点抽查（含 [P0025]↔01:25、[P0081]↔03:13、[P0114]↔03:94、[P0139]/[P0140]↔§ 1/§ 2、[P0215]/[P0216]↔05:32/05:34、[P0221]↔05:44、[P0223]↔05:48、[P0231]↔05:64）**措辞逐字一致**；docx 另含 tex 七个分文件之外的前置件（Title/Author/Abstract/Keywords/TOC），其术语（"deployment front door"、"visible operator"、"event receipt and custodian map"、"cumulative material-control test"、"pre-merits attribution gap"）与正文用法一致。
- 术语总计数差异全部由前置件（abstract/keywords/TOC）与脚注单列文件解释（例：material-control 的 tex 6 次中 2 次是 `\label` 不可见、1 次在脚注 fn 111；docx 正文 4 次 = 可见 3 次 + abstract 1 次，完全对账）。
- 直接解包 docx 验证：document.xml 含 3 个真实文本表（206/108/402 个文本运行，内容与 tex 三表一致）+ 1 张图片（cascade 图）。**`before-the-merits-tables.txt` 中 TABLE 0、TABLE 1 无内容是提取脚本的产物，不是 docx 缺陷**。
- 结论：docx 是 tex 的忠实编译产物，术语层无可见分歧；唯一 docx 特有差异是 B-11 所述题注样式不一。另提示：文件名 "before-the-merits" 与现标题 "Who Controls, Who Answers?" 不一致，疑为旧稿名残留，投稿前建议重命名输出文件以免混淆。

---

## 附：审计方法说明

七部 tex 全文通读；所有候选术语及扫描中新发现术语（first recipient、control-based filter、information plane、event key、run identifier、minimum answer、prompt exit、closed/local/minimum manifest、production problem 等）用不区分大小写的全文检索计数并逐处核对上下文；§ 1–§ 11 模型条文与正文 4 处数字引用、模型条文内部 8 处交叉引用逐条人工比对指向；docx 经解包 document.xml 验证表格与正文保真度。未读到的内容（如编译主控 main.tex、参考文献库）不在本次范围内，文中未做断言。
