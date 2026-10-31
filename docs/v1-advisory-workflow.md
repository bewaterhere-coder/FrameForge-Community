# FrameForge V1 项目使用流程 / Project workflow

## 中文

**适用范围**：对任意已授权项目进行只读发现、插件选择、规范引用及风险提示。项目规范由项目维护者负责；FrameForge 不生成或修改正式规范。

1. **发现**：安装 FrameForge 后运行 `frameforge --plugins` 和 `frameforge /path/to/project`。先阅读 `suggested_plugins`、`discovered_standards`、`advisories` 和 `warnings`；未配置 Profile 时出现 `PROFILE_MISSING` 是正常提示，不会阻断开发。
2. **选择**：确认实际技术栈，在项目内的 `.frameforge/profile.json` 指定 `schema_version: 1` 和 `selected_plugins`（ID 与版本）。**不要把检测到的所有插件自动写入 Profile**。先在隔离副本中试用，只有项目维护者有权更新正式 Profile。
3. **绑定规范**：在 `standards` 中引用项目自己的正式文档（例如 `architecture`），不要复制规范正文给 FrameForge。使用服务端框架插件时若需查看某个事务文件，明确设置 `structural_paths.skynet_transaction` 为项目内相对路径；不设置即不评价该事务。Art/UI 项目可按实际需要选配条款、实现信号和 Unity 资源绑定检查。
4. **审阅结果**：`professional_guidance` 是匹配源代码的审查提示；`structural_observations` 是有限结构证据；`semantic_checks` 的规则和条款必须由项目显式提供。查看具体文件、行号、`scan.truncated`、`confidence` 和 `status`。候选路径缺失、样本无匹配、包未解析均**不等于**正式缺陷。并非所有审查提示都放在 `warnings`：专业信号通常位于 `professional_guidance` 或 `structural_observations`。对重要结论返回项目源码和正式规范核实，必要时使用 Unity 编译或真实数据库集成测试。
5. **持续维护**：技术栈、插件版本、项目 Profile 或正式规范发生变化后，重新运行只读检查，比较实际证据并更新项目侧引用。版本不一致时优先修正绑定；FrameForge 不替代原项目审查及验收。

AI Host 可在已连接并获授权的项目环境中复用 `inspect_project`、`explain_warnings` 与 `verify_remediation`。发现候选文件时先看 `standard_candidates`、`domain_hints`；按 `standard_sources`、`standard_authority_review` 核对绑定与待确认项；`clause_coverage=[]` 表示尚无配置条款，而不是全部检查通过。参见 [端到端案例](ai-host-end-to-end-v1.md)。

Unity 外部引用的 `external_dependency_state` 可区分 `external_package_observed`、`external_package_not_observed` 和 `external_evidence_unverified`；这是 Host 提供的缓存观测分组，不能自动判定可选包、完整依赖解析或编译 PASS。`resolution` 仍为 `unverified`。

**输出保证**：所有结果保持非阻塞（`blocking=false`）。项目不存在 Profile 或未选择插件，也可正常继续开发。静态 `observed` 不能视为测试 PASS、规范符合或正式验收。

## English

**Scope:** Read-only technology discovery, explicit plugin selection and evidence-based advice for an authorized project. The project remains the sole owner of its formal standards.

1. **Discover:** Run `frameforge --plugins` and `frameforge /path/to/project`; inspect `suggested_plugins`, `discovered_standards`, `advisories` and `warnings`. `PROFILE_MISSING` is advisory only.
2. **Select:** In the project's `.frameforge/profile.json`, explicitly set schema version 1 and selected plugin IDs/versions. Discovery must not automatically activate all suggested plugins. Trial configuration belongs in a disposable copy first.
3. **Bind:** Point `standards` to authoritative project documents. To inspect a server-side transaction file, opt in with the project-relative `structural_paths.skynet_transaction`. Art/UI checks likewise require explicit project context.
4. **Review:** Interpret `professional_guidance`, `structural_observations`, optional semantic/Art/UI evidence, source locations, confidence and scan limits. Professional or structural review signals need not appear in the top-level `warnings` list. An absent marker or unresolved package is not a proven defect; use real builds and database tests where the claim requires them.
5. **Maintain:** Re-run after stack, profile, plugin or standards changes; repair project-owned references. Do not turn FrameForge findings into a merge gate or acceptance receipt.

A connected and authorized AI host may use `inspect_project`, `explain_warnings`, and `verify_remediation`. Check candidates, source bindings, authority-review questions and clause coverage separately. Empty clause coverage is not a pass. See [end-to-end case](ai-host-end-to-end-v1.md).

Unity `external_dependency_state` distinguishes host-reported package-cache observation, absence, and missing evidence. It never establishes optionality, actual assembly resolution or compilation success; `resolution` remains `unverified`.

**Guarantee:** `blocking=false`. Static evidence does not certify code correctness, architectural conformance or formal acceptance.
