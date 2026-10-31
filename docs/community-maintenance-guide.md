# Community Maintenance Guide / 社区维护指南

## 中文

本文说明 FrameForge 社区如何接收提案、评审插件、维护规范来源，以及管理版本。目标是让新贡献者能参与，让维护者能一致地做决定；不建立复杂的委员会或强制审批体系。

### 1. 参与角色

- **贡献者**：提交 Issue、文档、Manifest、测试或实现；说明来源、适用范围和未知项。
- **维护者**：负责分类、评审证据、安全与兼容性、决定是否合入，以及维护版本说明。
- **项目使用者**：决定是否选择插件、采用建议或绑定规范。FrameForge 维护者无权替使用者批准其项目规范。

同一个人可以承担多个角色。除仓库权限外，不假设任何人的身份、雇佣关系或厂商授权。

### 2. Issue 分类与处理

收到提案后，先确认它属于哪一类：

1. **引擎/领域候选**：优先检查是否能用现有声明式 Manifest 表达。
2. **现有建议修正**：核对来源、版本范围、误报和不适用条件。
3. **真实项目验证**：检查授权、脱敏、可复核证据和负例。
4. **Core 能力请求**：只有多个插件存在相同需求、Manifest 无法表达时才考虑。
5. **安全问题**：转入 [安全政策](../SECURITY.md) 的私密报告流程，不在公开 Issue 讨论利用细节。

信息不足时，维护者应指出缺少的具体来源或证据，不推测项目背景。重复或范围不清的提案可以合并讨论、缩小范围或关闭，并说明理由。

### 3. Candidate 到 Validated

- 新插件和新规则默认是 **Candidate**。
- Candidate 可以依据官方文档或明确标注的社区资料提供有限建议，但必须公开说明未验证范围。
- **Validated** 不是贡献者自行勾选的标签。维护者只有在核验可复核的真实项目证据后才可确认。
- 真实项目证据应覆盖引擎/工具版本、项目结构差异、正例、负例、缺失/不适用情况、扫描边界和实际输出。
- 通常应有至少两个结构不同的真实项目；若只能验证一个，继续保留 Candidate，并明确样本限制。
- 证据必须由项目所有者授权并脱敏。公开 PR 不应包含私有源码、绝对路径、账号、提交 ID、截图中的业务信息或其他可识别项目的数据。
- 单元测试、合成 Fixture、官方文档阅读和 CI 通过都不能单独证明真实项目验证。

维护者可以缩小支持范围、保留 Candidate、要求补充证据或拒绝升级。Validated 也不表示完整覆盖、厂商认证或零误报。

### 4. PR 评审清单

维护者按变更范围检查：

- [ ] 是否优先复用现有 Manifest 和 Core 接口？
- [ ] 插件发现与启用是否分离，是否需要用户显式选择？
- [ ] 是否只读项目，未执行第三方脚本或修改项目文件？
- [ ] 是否保持 Warning 非阻塞，尊重项目自己的规范？
- [ ] 官方来源、版本范围和社区来源是否清楚标注？
- [ ] 是否覆盖正例、负例、缺失、版本差异和边界？
- [ ] 是否检查路径穿越、符号链接和敏感信息？
- [ ] Candidate / Validated 状态是否与证据相符？
- [ ] README、最佳实践和中英文说明是否同步？

测试通过只说明测试覆盖范围内的行为通过，不自动代表建议准确或项目已验证。

### 5. 版本与兼容性

- FrameForge 包版本与插件 Manifest 版本分别管理，不要混为一谈。
- 插件 ID 一经公开应保持稳定；破坏性字段变化必须说明兼容策略。
- 修改引擎版本范围、检测信号或建议语义时，应更新来源日期、测试和变更说明。
- 删除或替换规则前，检查是否有项目 Profile 正在引用；无法确认使用情况时，优先弃用并记录迁移方式，而不是静默改变含义。
- 发布版本时，维护者应检查 LICENSE、打包内容、变更说明和测试结果。没有明确发布批准时，只合入代码，不创建正式 Release 或部署。

### 6. 决策与冲突

评审意见应针对证据、适用范围、安全边界和维护成本。遇到分歧，记录不同意见及尚未验证的事实；可以先保持 Candidate 或缩小范围，不必为了追求统一结论而扩大 Core。

FrameForge 不要求项目采用统一架构，不把建议变成强制 Gate，也不替项目做开发验收。

### 7. 维护者交接

新增维护者时，明确其仓库权限和负责范围。交接至少包含：当前包版本、插件清单及证据等级、待处理 Issue/PR、安全报告处理状态（不公开敏感细节）、已知兼容性问题和下一次发布事项。不要把访问令牌或私密报告内容写入仓库文档。

## English

This guide explains how the FrameForge community receives proposals, reviews plugins, maintains source references and manages versions. It aims for consistent decisions without creating a complex committee or mandatory approval system.

### 1. Roles

- **Contributors** submit issues, documentation, manifests, tests or implementation, with sources, scope and unknowns.
- **Maintainers** triage and review evidence, security and compatibility; decide whether changes are merged and maintain release notes.
- **Project users** decide whether to select plugins, adopt advice or bind standards. FrameForge maintainers cannot approve standards on behalf of a project.

One person may hold more than one role. Do not infer employment, identity or vendor authorization from repository permissions.

### 2. Issue triage

Classify proposals as engine/domain candidates, corrections to existing guidance, real-project validation, reusable Core capability requests, or security reports. Prefer declarative manifests where possible. Route security reports through the private process in [Security Policy](../SECURITY.md); do not discuss exploit details in public issues.

Ask for specific missing sources or evidence rather than guessing project context. Duplicate or unclear proposals may be consolidated, narrowed or closed with an explanation.

### 3. Candidate to Validated

- New plugins and rules start as **Candidate**.
- Candidate guidance may use official documentation or clearly labeled community sources, but must state what has not been verified.
- **Validated** is a maintainer decision, not a contributor-selected label.
- Evidence should cover engine/tool versions, structural variation, positive and negative cases, missing/inapplicable cases, scan boundaries and actual output.
- Normally, evidence should cover at least two structurally different real projects. If only one is available, keep Candidate and state the sample limitation.
- Project owners must authorize and sanitize evidence. Never publish private source, absolute paths, account data, commit IDs, business details in screenshots or other identifying project data.
- Unit tests, synthetic fixtures, documentation review and CI success do not independently prove real-project validation.

Maintainers may narrow scope, retain Candidate, request evidence or decline promotion. Validated does not mean complete coverage, vendor certification or zero false positives.

### 4. PR review checklist

Review whether the change reuses existing manifest/core interfaces; separates discovery from activation; remains read-only; avoids executing third-party scripts; keeps warnings nonblocking; respects project-owned standards; cites sources and version scope; tests positive, negative, missing and boundary cases; checks path traversal, symlinks and sensitive data; and keeps Candidate/Validated claims consistent with evidence. Update README, best practices and both language versions when needed.

Passing tests only proves behavior within their coverage. It does not automatically prove advisory accuracy or real-project validation.

### 5. Versions and compatibility

- Manage the FrameForge package version and each plugin manifest version separately.
- Keep public plugin IDs stable. Document compatibility for breaking manifest changes.
- When engine ranges, detection signals or advisory meaning change, update sources, tests and change notes.
- Before removing or replacing a rule, consider existing project Profiles. If usage is unknown, prefer deprecation with migration guidance over silently changing meaning.
- Before a release, maintainers check the license, packaged files, change notes and test results. Without explicit release approval, merge code only; do not create a formal release or deploy.

### 6. Decisions and disagreements

Review evidence, scope, safety boundaries and maintenance cost. Record unresolved facts and differing views. Keeping a proposal as Candidate or narrowing its scope is acceptable; do not expand Core merely to force consensus.

FrameForge does not require one project architecture, turn advice into mandatory gates or perform project acceptance.

### 7. Maintainer handoff

When adding maintainers, define repository permissions and scope. A handoff should cover the package version, plugin inventory and evidence levels, open issues/PRs, security-report status without exposing sensitive details, known compatibility issues and planned releases. Never put access tokens or private report content in repository documentation.
