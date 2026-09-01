# 论证一致性审计报告：清除清单候选
**对象**：Who Controls, Who Answers? A Deployment Front Door for High-Impact AI Litigation（submission draft）
**基准**：worknote.md（9 处插入方案）
**定位方式**：编译全稿 before-the-merits-extracted.txt 的 [P0000] 段落号 + .tex 源文件行号。注意：extracted txt 无分页标记，worknote 所引页码（p.5/19/22/35/46/51/53/57）无法逐页直接核对；但各锚点的章节顺序与页码顺序完全自洽（p.44 Table 3 → p.46 IV.A/IV.B → p.49 IV.D → p.51 IV.D.iii FCRA → ~p.52 IV.E → p.53 V.A），页码可信。

---

## (A) worknote 断言核验表

| # | worknote 断言 | 核验结论 | 原稿位置 + 原文短引 |
|---|---|---|---|
| a | "level neutrality" 出现三次（pp. 5, 35, 57），且都是从句/顺带提及 | **属实**（三处齐全，均为顺带句；页码不可直接验证但位置合理） | ① P0023 Introduction（01-introduction.tex L21）："The primary adoption audience is a state legislature regulating a designated sector; Congress can use the same architecture where national uniformity is required."（分号后半句）。② P0166 Part II.G forum-boundary 段（03-front-door-rule.tex L195）："Congress can adopt the same architecture for a federal cause of action, in which event Erie does not arise."（ Erie 讨论段中插入句）。③ P0271 Part V.C 末句（06-objections-boundaries.tex L34）："Congress can use the same front-door architecture when national uniformity is required."（preemption 长段最后一句）。三处读者语境确为 Erie/preemption，与 worknote 描述一致 |
| b | FCRA § 1681m(h)(8) 排除私人诉权只是脚注（p. 51） | **部分不属实**：排除规则在**正文**，脚注仅引法条与案例 | P0247 Part IV.D.iii 正文（05-record-infrastructure.tex L96）："section 1681m(h)(8) excludes private civil actions for failures under section 1681m and assigns that section to public enforcement"。配套脚注（footnotes 文件标号 fn 350，全文顺序第 53 个脚注）只有 "See 15 U.S.C. § 1681m(h)(8) (2024); Perry v. First Nat'l Bank, 459 F.3d 816, 822–23 (7th Cir. 2006)"。即"埋在 comparator 长段中部"属实，"只在脚注"不属实。worknote 更深的论点——"文章选择了比其最近国内模型更 person-facing 的路线"——确实全文未明言 |
| c | "some losses have no private remedy" 的承认（p. 53） | **属实**（正文） | P0259 Part V.A（06 L10）："Some losses have no private remedy; others sound in contract, tort, antidiscrimination, administrative, consumer-protection, or no-liability rules." |
| d | Stage One "follows from visibility and provenance, not a presumption that it controlled every risk"（p. 19） | **属实**（正文，II.B 首段末句） | P0088 Part II.B（03 L28）："Its gateway role follows from visibility and provenance, not a presumption that it controlled every risk." |
| e-1 | Table 1 把 mandatory updates / cross-tenant disabling / monitoring 视为保留 lane 的证据 "despite contract language assigning all responsibility downstream"（p. 22） | **实质属实，归属不精确**：引文是 Table 1 相邻正文，不是表格本体；"cross-tenant disabling" 在另一段 | P0102 Part II.C negative-rules 段（03 L57，Table 1 之前）："a provider that retains mandatory updates, remote suspension, risk monitoring, or binding deployment conditions may retain a lane despite contract language assigning 'all responsibility' downstream." P0109（03 L83，Table 1 之后）："actual practice—mandatory updates, cross-tenant disabling, monitoring, or customer control over whether a score is used—may reveal authority that a contract label obscures." Table 1 本体 practical-authority 行仅有 "consistent exercise in practice" / 终止列 "technical ability prohibited and unused"。worknote 把表格与前后两段正文合并引用了 |
| e-2 | § 8 "Independently relevant operational conduct retains only the effect governing law gives it"（p. 22） | **实质属实，归属错误**：原句在 II.C 正文，不在 § 8 | P0103 Part II.C merits-firewall 段（03 L59）："The merits firewall therefore bars an inference based solely on coverage, notice, compliance, noncompliance, or participation. Independently relevant operational conduct retains only the effect governing law gives it." § 8 法条（P0148，03 L157）的对应句是另一措辞："Governing law supplies every element and defense and determines the independent relevance, if any, of operational conduct." |
| e-3 | Part IV.B "closed manifest"（p. 46） | **属实** | P0219 Part IV.B 首段（05 L40）："The visible operator keeps a closed manifest: deployment ID; covered purpose and population; application and model versions; material components and suppliers; record custodians; risk and release owners; relevant contract rights; and the event schema used for consequential actions." |
| e-4 | control sheet "should identify which changes require renewed evaluation or approval..."（p. 46） | **属实**（在 IV.A 而非 IV.B，worknote 插入表自身定位正确） | P0216 Part IV.A（05 L34）："The control sheet should identify which changes require renewed evaluation or approval and which enter a lower-burden change log." |
| f | Part IV.E minimization 论证出现在 Table 3 之后约八页处 | **结构与距离属实；精确页数不可验证** | Table 3（Minimum Deployment-Record Infrastructure）在 IV.A（P0212–13，05 L12–30）；IV.E "Recordkeeping Risks Require Minimization by Design" 自 P0249 起（05 L100）。中间隔 IV.B（约 7 段）、IV.C（约 8 段）、IV.D（3 小节 13 段）。"相隔很远、顺序读者先形成密度印象"成立；"八页"与 worknote 自给的 p.44→~p.52 锚点自洽 |
| g | Part V 确有四个 boundaries；V.C 承认够不到上游供应商、要靠 § 2 合同取回权 | **属实** | P0256 Part V 开头（06 L4）："Four boundaries make that allocation durable: existing law defines the protected interest; constitutional and confidentiality rules shape disclosure; arbitration, territorial limits, and federal preemption govern the enforcing forum; and product or speech classification remains for the merits." V.C 承认见 P0270（06 L32）："A control holder receives a direct statutory duty only when the enterprise and identified deployment fall within valid territorial and choice-of-law reach… The domestic visible operator nevertheless owes the local manifest, event receipt, and contractual retrieval path… without pretending that state process reaches every global node." 另 P0269（06 L30，仲裁语境）："The operator's predeployment retrieval right supplies the defined vendor fields without enlarging arbitral subpoena power." |
| h | 脚注 19 承认 California companion-chatbot 法案只有形式而无 front-door rule | **属实**（编号可确认为全文第 19 个脚注） | footnotes 文件标号 fn 145，按顺序恰为第 19 个脚注："The enacted provisions do not contain the deployment front-door rule proposed here; they demonstrate that a legislature can designate a relational deployment, identify its operator, and attach enforceable protocol and reporting duties."（正文 P0086 / 03 L21 亦只说 "demonstrate the feasibility of this form"） |

**附带核验（worknote §03/05 的其他引用点，全部命中）**：
- "Silence, a blanket proprietary designation, and referral to an unnamed vendor are not responses." — P0091（03 L34）✓
- "refuses or materially underanswers" — P0094（03 L36）✓
- Table 1 终止列 "technical ability prohibited and unused" ✓；Table 3 intervention 行 "restrict, revoke credentials, update, pause, roll back, or terminate; triggers, response times, and tested procedures" ✓；evaluation 行 "rejected or conditional mitigations, and unresolved risk decisions" ✓
- "Two affected persons presenting different liability theories receive the same identity, version, event, custodian, and control fields" — P0180（03 L189，II.G）✓
- § 9 "Bare nonperformance creates no private statutory damages" — P0149（03 L159）✓
- 插入 7 位置描述准确：II.E（Protection, Remedies, and Safe Exit）确含 graduated consequences（P0127–34）与 safe exit（P0136）；插入 1 位置准确：II.A 五条 designation 标准在 P0082
- **全文无任何 EU AI Act / Article 86 / AI Liability Directive / 民法法系 pre-action 内容**——插入 3、4 为纯新增，不存在相冲突的旧文字

---

## (B) 重复论述清单

| # | 论点 | 主陈述（建议保留） | 冗余回声 | 处理建议 |
|---|---|---|---|---|
| 1 | "record never created cannot be reconstructed"（ex ante duty 的存在理由） | P0025 Introduction："Because litigation cannot recover a record never created, the proposal also imposes an ex ante deployment-record duty." | ① P0004 + P0006 Abstract 内重复两次；② P0041 Part I.B："a post-event subpoena cannot create lineage or approval that the operator never recorded"；③ P0048 Part I.C："create a release approval, configuration history, or incident record that never existed"；④ P0050 Part I.C（Rule 27 段）："A deposition cannot supply an unknown model version or a deployment record that no witness or enterprise created"；⑤ P0157 Part II.G 开头；⑥ P0209 Part IV 开头；⑦ P0278 Conclusion | Abstract 删一处；**Part I 内 ②③④ 三连回声压缩为一处**（保留 P0041，它与"第二种格局"绑定）；⑤ ⑥ 各承担 Erie 与基础设施的不同功能，保留但可在 II.G 删去定义性复述；Conclusion 保留 |
| 2 | 两阶段规则全图（designation → fixed first answer → claim-specific lane → safe exit → merits unchanged） | P0024 Introduction（首次完整陈述） | P0044 Part I.B 末段（sequence 重述）；P0077 Part II 开头；P0122–123 Part II.D.iii 对 Stage One/Two 的再定义（与 P0090 II.B 的定义重叠）；P0279 Conclusion | Intro 与 Conclusion 首尾呼应保留；**II.D.iii 的 Stage One 定义句可压缩**（已有 "described above"，可再删一句）；II 开头保留 |
| 3 | 网关理由：visibility 而非控制推定 | P0088 Part II.B（worknote 将引用的教义句） | P0024 Introduction："The operator is selected because an affected person can find it, not because the statute presumes it controlled the risk." | 两处均保留（预告 vs 教义陈述）；**注意**：插入 7（II.E adversarial compliance）将再次引用此句，届时全文出现三次，II.E 内用简引即可 |
| 4 | Merits firewall / "no merits inference" | P0103 Part II.C（含 "Independently relevant operational conduct retains only the effect governing law gives it"）+ P0148 § 8（法条化） | **P0217 Part IV.A 末段："The completed form creates no merits inference; the underlying operational records retain only the effect governing law gives them."——与 P0103 近乎逐字重复，是全文最典型的冗余回声**；另 P0105、P0005、P0015、P0280 各处短回声 | **压缩/改写 P0217 末两句**为一句交叉引用（与清除清单 C-4 合并处理）；法条 § 8 保留 |
| 5 | Rule 34 control +  predeployment 合同取回权 | P0115–0116 Part II.D.i（设计义务的主陈述） | P0052 Part I.C 末两句已提前开出处方："a visible operator should retain the minimum record locally and obtain a contractual right to retrieve defined provenance and event fields from a supplier"；P0165 Part II.G（Erie 语境）；P0269 Part V.C（仲裁语境）；P0140 § 2（法条） | **压缩 P0052 末两句**（Part I 是诊断章，处方留给 Part II，一句预告即可）；P0165/P0269 各承担不同法域功能，保留 |
| 6 | "sectoral, event specific, proportionate, protected / no general right to inspect / no remedy for unrecognized loss" 限定语组 | P0258–0259 Part V.A（展开版） | P0026 Introduction："The rule remains sectoral, event specific, proportionate, and protected. It supplies no general right to inspect AI and no remedy for a loss that governing law does not recognize."；P0005 Abstract | 保留（预告/展开结构合理）；插入 6 落地后 V 章将新增第五 boundary，注意与该组限定语的衔接 |
| 7 | Yu et al. 559 份联邦意见书研究（"courts use preexisting doctrines"） | P0059 Part I.D 正文 + fn 122 | Introduction fn 22 内同研究同结论："A systematic review of 559 federal opinions likewise reports that courts predominantly resolve AI disputes through preexisting legal doctrines…" | **删 Intro 脚注内的该句**（纯回声，主陈述在 I.D） |
| 8 | Garcia 程序姿态（Rule 12 产品裁定/言论裁定/和解无 merits 认定） | P0173 Part III.A.i | P0013 Introduction（完整案情首述，必要）；P0274 Part V.D（classification neutrality 语境再述） | 三处功能不同，**保留**；V.D 复述已最简 |
| 9 | "information asymmetry decides the case" 首尾呼应 | P0280 Conclusion | P0027 Intro roadmap 末句："substantive law should decide AI cases, not an information asymmetry that prevents substantive law from starting." | **保留**（刻意 callback，非冗余） |

---

## (C) 待清除 / 待改写段落清单（按优先级）

### C-1【改写 · 最高优先 · 真正逻辑冲突】
**P0216 Part IV.A（05-record-infrastructure.tex L34）第三句**："The control sheet should identify which changes require renewed evaluation or approval and which enter a lower-burden change log."
- **为什么该清**：读作 operator 自设 material-change threshold，与 § 1（P0139："The designation shall identify the… material-change threshold"）和 § 2 末句（P0140："The designation supplies the retention period and material-change rule"）直接冲突；且自设阈值是真实可博弈的 metric（把所有变更路由进 low-burden log）。
- **衔接**：worknote 插入 9（Part IV.A control-sheet 段改写）。同时统一 Table 3 第一行 "Identity and scope" 中 "material-change threshold" 的措辞为"记录 designation 所定阈值"。

### C-2【改写 · 枚举将被证伪】
**P0236 Part IV.D 开头（05 L74）**："Three regimes perform distinct comparator roles: organizational record creation, regulator-defined information demands, and a private path from visible decisionmaker to upstream file holder."
- **为什么该清**：插入 3 新增第四个 comparator（AI Act Art. 86 + 已撤回的 AI Liability Directive），"Three regimes" 与三角色列举立即过时；开头亦无插入 2 要求的"三个 comparator 均为 national regimes"的说明。P0248 收尾段 "Together, the comparators answer feasibility at the right level…" 需同步加入第四角色。
- **衔接**：插入 2（IV.D 首句）+ 插入 3（FCRA 后新增 comparator）。

### C-3【改写 · 枚举将被证伪】
**P0256 Part V 开头（06 L4）**："Four boundaries make that allocation durable: …" 枚举句。
- **为什么该清**：插入 6 新增第五 boundary（designation dependency + thin deterrence 定价），"Four boundaries" 及分号列举过时。
- **衔接**：插入 6（Part V 新 boundary，或并入 V.C）。

### C-4【压缩 · 近乎逐字重复】
**P0217 Part IV.A 末段（05 L36）末两句**："The completed form creates no merits inference; the underlying operational records retain only the effect governing law gives them."
- **为什么该清**：与 P0103（II.C）近乎逐字重复（见 B-4）。
- **衔接**：与 C-1 同段，做插入 9 时一并改写为一句交叉引用 § 8。

### C-5【压缩 · 为插入 7 让位，避免 double coverage】
**P0102（03 L57，negative rules 段）与 P0109（03 L83，reserved rights 段）** 中与 evasion 分析重叠的句子——"Conversely, a provider that retains mandatory updates, remote suspension, risk monitoring… may retain a lane despite contract language assigning 'all responsibility' downstream"（P0102 末句）与 "actual practice—mandatory updates, cross-tenant disabling, monitoring…—may reveal authority that a contract label obscures"（P0109 第三句）。
- **为什么该清**：插入 7（II.E 新小节 adversarial compliance，~400 词）将系统地重述 slicing 与 strategic-incompetence 分析并直接引用这两处内容；不压缩则同一论证在 II.C 与新 II.E 小节双重覆盖。
- **衔接**：插入 7。保留两段的 definitional 部分（negative rules 清单、reserved-rights 标准），把 evasion 成本/自败分析让给新小节。

### C-6【小改 · 框架扩展】
**P0054 Part I.C 州 pre-suit 段（02 L55）首尾句**：开头 "State pre-suit proceedings confirm that a narrow identity stage is administrable while revealing the absence of a uniform route" 与结尾 "These systems provide design elements—verification, a closed purpose, burden review, a short proceeding, and cost allocation—rather than an existing federal solution."
- **为什么该清**：插入 4 将加入法国 mesure d'instruction in futurum（CPC art. 145）与德国 selbständiges Beweisverfahren（ZPO §§ 485–494a），纯国内框架的首尾句需扩写为跨法系表述。无逻辑冲突，属衔接性改写。
- **衔接**：插入 4。

### C-7【可删 · Part I 内三连回声瘦身】
**P0048 末句与 P0050 末句**（见 B-1 ③④）。
- **为什么该清**：同一前提在 Part I 内重复三次。
- **衔接**：与 C-6 同章，做插入 4 时一并瘦身。

### C-8【可删 · 纯回声脚注句】
**Introduction fn 22 内**："A systematic review of 559 federal opinions likewise reports that courts predominantly resolve AI disputes through preexisting legal doctrines and that litigated harms are shaped by existing causes of action."
- **为什么该清**：与 Part I.D 主陈述 P0059 + fn 122 完全重复（见 B-7）。
- **衔接**：独立清理，不依赖任何插入。

### C-9【核查而非删除 · 纯新增确认】
**§ 4（P0141，03 L145）** 现无 "in the form the designation specifies" 条款——插入 8 为纯新增，无需删旧文；但新增后建议在 § 1 designation 清单（P0139）补 "form"，保持 § 1/§ 4 一致。
- **衔接**：插入 8。

### C-10【明确保留 · 勿误删】
三处 level-neutrality 顺带句（P0023 / P0166 / P0271）——worknote 明确将其作为插入 1 的支撑引用（"pp. 5, 35 and 57 already assume it"），插入 1 落地后它们从"承载型题外话"转为有意 cross-reference，**不应删除**。同理 P0088（d 项）、P0247（b 项）、P0259（c 项）均为插入将要引用的锚点，保留。
