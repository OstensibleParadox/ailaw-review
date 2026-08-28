## Reconstructed Submission Package

The canonical manuscript is now `what-is-ai-for-courts.tex`, with Parts in `article/`, authorities in `what-is-ai-for-courts.bib`, and the source-by-source audit in `citation-ledger.md`. Run `make pdf` to build the submission-format article at `output/pdf/what-is-ai-for-courts.pdf`.

The reconstructed argument is organized around one jurisprudential minimum: functional classifications of AI may vary across doctrines, but operational autonomy does not silently reassign legal status. The Article translates that invariant into a deployment-control cascade and a two-layer responsibility architecture for courts.

The research and drafting specification that governed the reconstruction follows.

---

What Is AI for Courts? 

-- A Jurisprudential Minimum for Adjudicating AI Disputes


TLDR; What minimum jurisprudential structure must AI Law possess before courts can adjudicate AI disputes coherently despite continuing disagreement over artificial mind and agency?

TABLE OF CONTENTS

Introduction
Part I: The Definition Crisis in AI Law — ~2,600 字
I.A AI 法作为新兴部门法 Ayres & Balkin、Abraham & Sharkey、Ramakrishnan、Duffourc、Chan脚注支撑。
内容：调整谁/调整什么/如何调整/违反后如何负责——四个经典问题；EU AI Act、中国与美国单行规范已快速填充后两个问题，主体与对象理论仍分散。
I.B 私人定义与法律定义的冲突
私人宣传能够形成 intended use、可预见依赖和合理安全期待，却不能创设一个吸收责任的人工主体。
I.C 部门法分类为什么可以不同
内容：AI 可以同时是产品责任法中的 product、合同法中的 service、著作权法中的 tool、宪法法中的人类表达媒介；统一的是基础事实和主体结构，不是制度标签。为 Part III 打地基。

---

### Part II: Artificial Intelligence Without Artificial Persons 
II.A 法律主体资格不是行为能力测试
Cite: Abbott & Sarch、Nerantzi & Sartor "hard AI crime"、Mukherjee & Chang "operational agency"主文对话对象，不是脚注——"operational agency" 是本节要明确拒绝的竞争方案。
内容：Hohfeld 式权利义务结构，一张紧凑表格；主体须能承载请求权/义务/权力/责任/救济/制裁关系，AI 能产生事实效果但无法独立闭合这些规范位置。
 II.B 机器心灵的法律括置 
rule performance 不等于 normative status；normative attitudes（RLHF 训练的是"被评价为正确"，不是"正确本身"）不等于法律地位；internal compliance（企业自证的宪法/spec/policy）不取代 external judgment。
法院无须解决机器意识；除非立法明确规定，语言能力、人格表现和操作自主性均不产生独立责任人格。
II.C 基础定义
AI 是一种不具独立法律人格、能够在部署后根据用户指令、开发者规则、系统状态或环境输入进行概率性自动运行的软件系统。说明"自动运行"描述操作结构、不意味自由意志，参数规模/蒸馏程度/benchmark 不改变主体资格。
II.D 自动机关而非人工行为人
内容：自动装置类比——除 user prompt 外，还有 agent loop/system prompt/RAG/工具返回/定时任务触发。核心句：没有人在输出瞬间逐字控制，不等于没有人设置并维持造成损害的机关。这一节是全文对 Yuanbao 案（零人类 agency）的理论铺垫，Yuanbao 本身放在 Part IV 展开。

---

Part III: Why Classification Matters 
III.A 人格权、精神健康和生命健康
Cite: Freitas 2025 Replika 哀悼研究、Banks 2024 deletion 的死亡/关系解体双重解读、Zhang 2025 darkside 35,390 段对话的四种有害角色、Kirk 2025 steering vectors 23.4% 依赖轨迹、Laestadius 2024 情感依赖。Garcia 在此完整展开（未成年人+companion+coverage gap）。
内容：生成式 AI 的特殊性不是"产品第一次能够伤人"，而是企业规模化生产的系统能以一对一关系的外观持续、适应性地作用于特定个人。覆盖自伤自杀诱导、未成年人、AI 伴侣关系依赖、严重精神打击、人格与自主性干预，不解决全部 tort doctrine，只证明现有产品/服务直觉不足以描述这种损害形态。
III.B 知识产权的一致性检验 
内容：A、B 插画师和无授权商家的例子；AI 人格与作者资格不是同一问题；AI 辅助作品的保护取决于人类贡献；风格模仿与具体表达复制必须区分；公司条款只能分配其可能拥有的权利，不能创造著作权。功能是证明承认 AI 独立人格会无谓增加权利链条而不解决任何必要问题。
III.C 人格化营销的法律后果
Case: Character.AI 
内容：人格化不生人格，但生归责事实和注意义务。市场中的人格化影响 intended use、foreseeable reliance、safety expectations、精神损害的可预见性、适当保护措施。

---

Part IV: Reconstructing Human Control 
IV.A 不完全可观察不是责任真空
内容：法律从来不要求完全打开行为人的内部状态才允许归责。
新起点：模型过程只具有部分可观察性，因此法律需要从可见行为、权限和控制动作重建责任链。
IV.B Cascade 作为 STPA 的 AI 部署实例
provider/deployment platform/model-harness/user-environment + authority/resource allocation + feedback/override/stop authority
IV.C 从工程变量到法律要件
内容：映射表.
谁是 controller → 谁承担相关职责；
谁批准 control action → 谁实施或授权行为；
谁维护 process model → 谁知道或应知风险；
谁收到 feedback → 谁具有事故知识；
谁有 override/rollback 权限 → 谁具有避免能力；
谁设置 KPI 和资源 → 是否属于组织性过失；
谁绕过 constraint → 是否存在个人违反。
这张表是 Part V 责任设计的直接前奏。
IV.D 混合部署结构 
内容：托管模型、API 与第三方应用、开放权重、abliterated 版本、匿名中转、政府模型、human-in-the-loop、分级访问与自动封禁——不是七个独立政策章节，而是对 IV.B/IV.C 归责能力的压力测试，逐项简短处理即可。

---
Part V: The Architecture of Responsibility 
V.A 公司对外责任
内容：受害者不应承担识别公司内部具体责任人的成本；企业活动创造并控制的风险，原则上先由公司或实际部署机构承担外部责任。公司不能靠"AI-generated"/"for reference only"/用户自行判断/数据导出说明/模型不可预测把风险一揽子转给用户；免责声明的作用必须逐项判断。
V.B 公司责任与个人责任并行 
内容：公司直接责任、雇主或组织责任、个人对自己行为的直接责任——三个不同概念。个人责任通常不需要先刺破公司面纱；veil piercing 只处理利用法人结构逃避既有责任的特殊情况。
V.C 强制责任章程
内容：risk owner；deployment sign-off；protected escalation；stop-work authority；rollback authority；dissent records；incident logs；独立安全评估；对善意报告者的保护；对隐瞒、篡改、越权者的个人责任。公司内部章程不能对外消灭受害者请求权，但可以决定 indemnification/internal recourse/discipline/safe harbor/个人过错证据。
V.D 双层责任规则
doctrinal formula——公司先对外负责，再依事前章程对内定责；保护提出风险的人，追究覆盖风险的人。这句话同时回答受害者救济、工程师 chilling effect、管理层责任、组织碎片化四个问题。
V.E 剩余责任与反证 
内容：用户故意越狱、第三方重大修改、黑客攻击、政府强制、部署机构独立越权、真正不可避免事件。

---
Part VI: The Boundaries of AI Governance
VI.A Capability Stratification 
内容：公众版/专业版/政府版/科研版之间的能力不平等；提出比例性、透明性、复核和升级通道，不直接宣布差别开放违法。
VI.B Anti-Substitution 
内容：AI 可以补充养老、残障支持和陪伴，但不能成为政府、机构和家庭撤回既有照护义务的理由。保护对象从"用户拥有的关系财产"改为用户人格、心理健康、自主、社会照护权利、安全退出与适当告知。
VI.C State Power
Case: Claude-Maven，从案例展开延伸成政策论证。
内容：政府可以选择采购什么产品，却不能无限要求私人公司拆除所有护栏、支持其反对的用途、持续提供未承诺的维护、因拒绝某种用途而受到观点报复。呼应 I.A 里 EU/中国/美国三法域的定位——这一节说明统一定性既限制公司，也限制政府。

---

### Conclusion — ~900 字
内容：只强化四件事。
AI 法需要稳定调整对象；
AI 的操作自主性不产生人工责任人格；
Cascade 恢复人类控制链；
双层责任结构同时保护公众和守规工程人员。
不重新讨论意识、财产权或全部政策风险。


层级	材料	篇幅
完整司法锚点	Garcia	600–900 字
完整比较法锚点	杭州 AI“幻觉”案	500–700 字
完整公法治理锚点	Claude–Maven／Anthropic–Pentagon	600–900 字
行业实施样本	2026 医疗机构 AI 治理共识	350–550 字
压缩旁证	Soelberg、Yuanbao	各 100–200 字或脚注

部分	核心权威的大致份额	功能
Introduction	5%	定位问题，不进行完整文献审判
Part I	28%	建立定义、主体与学说坐标
Part II	14%	法人格与机器心灵括置
Part III	12%	证明分类错误的实际后果
Part IV	8%	建立工程—法律翻译接口
Part V	30%	输出可被 doctrine 支撑的责任制度
Part VI	8%	界定边界和政府权力
Conclusion	接近 0	不在结论突然加入新权威


Part I 
1. 部门法与法律调整对象
用于支撑：
* 一个法律领域为何能够形成相对独立的研究对象；
* 主体、对象、权利义务和责任救济如何构成其基础结构；
* 新技术领域何时需要统一的上位概念。
这里需要法理学、法律分类、技术法或 cyberlaw 形成史，而不是只引用 AI Act。
2. 法律定义理论
这是 Aspen、法律定义的语境依赖性、定义的制度溢出效应、technological neutrality、功能定义与本体定义的区别。
本文必须承认最强反方：
不同法律制度本来就应采用不同的 AI 定义，统一定义可能快速过时或产生监管漏洞。
然后回答：
本文不要求一个覆盖所有用途的操作定义；本文要求的是一个不随部门法漂移的主体地位与责任不变量。
这一区分需要引用定义理论，而不能只靠作者断言。
3. Loper Bright 与行政解释
需要准确限定：
* 法院独立解释法律；
* 行政机关仍可在明确授权范围内细化规范；
* 技术定义不再能够当然依赖含混授权和 Chevron 式尊让。
这部分应以判决、行政法学核心评论以及 Aspen 的实际政策推论组成，而不是单一引用。
4. AI personhood 的最强学说
不能只引用否定 AI 人格的文章。至少应覆盖：
* 强人格论；
* 功能人格论；
* 有限或工具性人格；
* moral patienthood 与 legal personhood 的区分；
* 反人格论；
* electronic personhood 的政治与立法史。
Argument: 即使哲学争论未决，裁判所需的责任主体结构仍可被独立确定。
5. 私人人格化与法律定义权
这里放 Waivers of Agency 的公司一手材料，并与消费者保护、产品呈现、intended use、reasonable reliance 等 doctrine 对接。
核心规则：
人格化不能创设主体资格，但可以形成法律相关的事实。
6. 产品、服务、工具、表达媒介的功能分类
这里的任务不是重新讨论哪一种正确，而是证明：
* 同一对象在不同制度中可以合法取得不同功能分类；
* 这种分类不应改变它是否承担责任的主体地位。
Part I 因而可能占 20–25 个核心权威来源，而不是只承担七八个背景引注。

Part V 
1. 企业的直接责任
公司自身的设计、监督、警示、部署和治理义务。需要区分公司直接过失与雇员替代责任。
2. Vicarious liability 与 scope of employment
用于回答：
* 员工违反内部指令是否使公司免责；
* 故意行为、越权行为和业务风险如何处理；
* 为什么内部章程不能决定受害者的外部权利。
3. 个人直接责任
证明工程师、经理、高管并不因公司身份而当然免于对自己的行为负责，同时处理 duty、control、knowledge 和 causation 的限制。
4. 公司刑责与高层责任
不必铺开所有刑法，但需要公司过失杀人、responsible corporate officer doctrine、个人责任与组织责任并行的代表性制度。
5. 产品责任与软件责任
用于公司先行赔偿、缺陷、合理预见使用、第三方修改、持续控制和更新义务。
6. 企业合规与内部控制
强制责任章程不能凭空出现。需要对接：
* compliance program；
* internal controls；
* audit trails；
* risk ownership；
* board oversight；
* whistleblower protection；
* stop-work authority；
* independent review。
这里可以跨用公司法、证券监管、医疗、航空、核工业和职业安全中的成熟做法，但每个类比必须说明为什么 transferable。
7. 举证责任与信息不对称
“受害者不应承担识别具体工程师的成本”需要 procedural doctrine 支撑：
* 信息掌握；
* discovery；
* burden shifting；
* res ipsa 类比的边界；
* 企业记录义务；
* adverse inference。
8. Safe harbor 与 chilling effect
保护守规工程师不能只作为政策善意。需要处理：
* professional immunity；
* statutory safe harbors；
* compliance defense；
* whistleblower anti-retaliation；
* indemnification；
* reckless or knowing misconduct exception。
Part V 应当同样承载 20–25 个核心权威来源。而且这些引用不能全放在 V.C 的脚注尾部；每项制度组件都应当有自己的 doctrinal genealogy。

Part IV 
三件技术事实：
1. AI 部署不是一个单一模型，而是模型、harness、接口、工具、反馈和组织权限的控制结构；
2. STPA 能够识别 controller、unsafe control action、feedback、process model 和 stopping authority；
3. 这些变量能够被翻译成法律上的 duty、knowledge、control、breach 和 causation。
因此核心工程来源大概只需要：
* Leveson／STAMP-STPA 的奠基来源；
* 一至两项把 STPA 用于软件、自治系统或 AI 的权威应用；
* 一项关于实际 ML 组织责任或安全实践的实证研究；
* 必要的一手模型系统文档；
* 可能再加一个反方或限制性来源，说明 STPA 本身不是法律归责模型。
大约 5–8 个真正承重的技术来源已经足够。剩下的工程细节应由本文自己的图和定义承担，不需要用几十篇 ML 论文证明“context window 存在”。

Part II
需要少而硬的：
* Hohfeld；
* 法律人格经典理论；
* Wittgenstein／Brandom／Aristotle／Kant 中真正承重的原始或权威解释；
* AI consciousness/personhood 的最强现代对话对象；
* copyright 或 criminal law 对非人主体资格的代表性案例。
重点不是文献数量，而是不能让 philosophy 部分成为作者自由联想。

Part III
人格伤害部分需要：
* 实证研究；
* regulator investigation；
* 诉讼材料；
* 产品责任和人格利益的接口文献。
知识产权测试则只需要最权威的案例、版权局文件和少量学说。它不是版权综述。

Part VI
每一小节都应有自己的制度锚点：
* capability stratification 对接 access equality、digital divide 和风险分级；
* anti-substitution 对接照护义务、公共服务与 automation welfare；
* state power 对接采购法、First Amendment、unconstitutional conditions 和具体争议。
