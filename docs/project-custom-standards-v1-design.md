# Project Custom Standards V1 — Design Review / 项目自定义规范设计评审

## 中文（先行）

**结论：沿用现有 `.frameforge/profile.json`、`standards`、`check_clauses` 和 `semantic_rules`，先补齐发现、权威确认和结果分级的协议。项目自己的文档是唯一正式规范，插件只是可选知识与证据来源。此文档是设计草案，不代表用户已批准新规范。**

### 目标使用流程

1. **发现（只读）**：AI 在 Host 已授权的项目范围内检查代码、技术栈、现有 Profile、架构文档、美术/UI、资源、测试约定；返回带有路径与证据的候选列表。找不到文档则给 Warning，不创建占位文件。候选文件的存在不意味着它是正式规范。
2. **确认权威**：区分三种状态：`bound_reference`（Profile 明确绑定的来源）、`candidate_reference`（扫描发现但尚未绑定）、`owner_confirmed`（项目负责人明确确认的规范及其版本）。已有绑定优先用作检查上下文，但**绑定与文件存在均不等于已获正式批准**。不同来源出现内容冲突时，输出冲突证据与待决项；不以文件名、扫描顺序或插件建议自动裁定。只有项目负责人确认，才能更新正式 Profile 或规范文档。
3. **制定或定制**：AI 可根据现有代码与技术栈建议 MVP、MVVM、ECS、UI、资源、测试等多种选项，不强制特定架构；用户可选择全部、自定义组合或完全不用。草案与正式规范必须明确区分。
4. **绑定**：优先复用 `standards` 路径及现有 `check_clauses` 条款定位；确需静态检查时使用已有 `semantic_rules` 或按需插件。条款分成 `reference_located`（仅定位）、`evidence_observed`（找到有限证据）、`not_evaluated`（无可靠评估），这些均不表示符合规范。无可靠检查器的条款保持 `not_evaluated`，不伪造通过。
5. **重新检查**：Host 只读调用 `inspect_project`/`explain_warnings`/`verify_remediation`；返回证据、来源、覆盖范围、置信度与未验证项。Warning 不阻塞开发；正式验收属于项目原有流程。

### 最小契约边界与失败路径

| 情况 | 期望行为 |
|---|---|
| 项目无 Profile | `PROFILE_MISSING` Warning，继续扫描，不自动写入 |
| 已有规范但未绑定 | 作为候选建议，等待 Owner 确认，不自动 Activation |
| 规范路径不存在/符号链接越界 | Warning；拒绝引用授权边界外资源，不跟随越界链接 |
| 多份规范冲突 | 已绑定引用可作为现有检查上下文，但冲突不自动解决；标明引用路径和待决事项 |
| Profile 绑定文件存在但无授权记录 | 仅返回 `bound_reference`；不得推断已获项目负责人批准 |
| 文件名匹配但正文不包含实际规则 | 仅为候选/引用可用；不得视为合规或权威性已验证 |
| 仅有示例、占位或 AI 草稿 | 不认定为已批准规范，不通过存在性推定权威 |
| 插件版本不可用 | Warning，其他项目检查继续，不自动升级 |
| 条款缺可靠的自动检查能力 | `not_evaluated`，不产生合规 PASS |
| 单一文件含可定位条款但代码实现未知 | `reference_located`，仍须真实代码或运行结果支持 |
| 同名规范在不同项目 | 按独立项目根解析，绝不共享用户侧绑定与检查结果 |
| 静态字面信号命中 | 只报告证据及检查范围，不宣称架构合规 |
| 规范修改/版本变更 | 重新绑定/重检并记录来源变化；不静默改正式规则 |
| 项目要求不同设计模式 | 以该项目正式规范为准，不硬编码任何单一项目的 MVP/UI 技术选择 |

### V1 实现边界

- **复用**：`src/frameforge/core.py` 的规范引用与候选发现、`semantic.py` 的受限扫描、现有插件 registry 和 `host_adapter.py`。
- **可增量补齐**：把规范候选的证据/来源状态输出给 Host，标明哪些项目条款已绑定、待确认、无自动验证能力；优先小改接口，不建第二套 Profile/规则引擎。`bound_reference` 是引用状态，不是额外审批系统；除非项目已有可信授权证据，不能返回 `owner_confirmed`。
- **向后兼容**：现有 `schema_version=1`、`warnings`、`discovered_standards`、`semantic_checks` 与 `blocking=false` 保持兼容；新增来源或覆盖状态应为附加字段，不改变已有 Warning 的含义。
- **确定性**：项目内部文档的发现结果按稳定路径排序；不要依赖目录遍历的碰巧顺序认定权威；来源冲突按条款事实和显式引用报告，而不单凭两份文档同时存在就断言冲突。
- **不做**：自动发布正式规范、自然语言直接生成可执行检查器、创建通用 Agent/数据库/后台服务、强制 Gate、绑定特定外部开发治理系统、把项目规范复制到 FrameForge 全局。
- **验收重点**：无 Profile、有效自定义规范、规范冲突、失效路径、Symlink 越界、AI 草稿不作权威、无评估能力、版本漂移、两个项目互不串规则；真实项目隔离验证；输出始终 `blocking=false`。

### 本轮评审发现的真实实现差距

- **已验证**：`core.py` 支持 `standards` 引用与三个固定领域的候选路径扫描；`check_clauses` 目前将条款与 architecture 引用进行单一定位；`semantic_rules` 仅支持受限 C#/Lua 字面量检查。
- **尚未实现**：通用规范领域的动态发现、明确的项目授权证据追溯、条款覆盖率与多源冲突诊断。不能把这些设计目标宣称为现有产品能力。
- **最小实施顺序**：先补规范来源与覆盖状态的只读输出，并为现有 Profile 保持无损兼容；确认真实冲突场景后再补冲突诊断；AI 辅助写规范必须独立取得项目负责人授权。

### 设计审查裁定

当前仓库已经支持明确的项目自定义规范引用和少量项目规则，**V1 不需要新核心服务或数据库**。设计阶段先确认权威来源与规则可评价性的契约，再决定是否存在真实代码缺口；此 PR 不变更运行代码或正式项目规范。

## English

Project-owned standards remain authoritative. Reuse the existing profile, standards references, check clauses and bounded semantic checks. Discover candidate documents read-only, distinguish proposal from approved source, and require explicit project-owner confirmation before modifying bindings. Plugin discovery never activates a plugin. Missing, conflicting, symlink-escaping or unverified sources yield nonblocking warnings/review recommendations, not compliance PASS. Unsupported clauses are `not_evaluated`; locating a clause or observing a literal signal is not a compliance verdict. A bound reference is not proof of owner approval, and detected candidate documents cannot automatically win conflicts. Current implementation only discovers fixed candidate paths and supports bounded C#/Lua literal rules; general provenance and conflict diagnosis remain future work. Preserve schema v1 and current warnings as a backward-compatible contract. Avoid new services, databases, AI runtimes, generic validators, and external project dependencies. This design-only change neither alters runtime behavior nor approves any project's standards.

### Discovery implementation addendum / 发现功能实施补充

V1 提供附加字段 `standard_candidates`，在项目根、常见文档目录的**直接子文件**中，以有界文件名规则发现候选 Markdown/RST/TXT 文档（最多读取 400 个目录项、100 个候选文件，不读取正文）。候选仅是 `filename_only` 证据，永不自动变为正式规范或覆盖 Profile 绑定。目录遍历不跟随符号链接，扫描上限在 `scan.truncated` 中报告；不保证发现所有文档，不实现冲突裁定或内容真实性审核。

V1 adds `standard_candidates` with filename-only evidence in a small bounded set of conventional project document directories. Candidate discovery never approves standards or overrides explicit project bindings. No full-tree traversal, content authority validation, or conflict resolution is claimed.
