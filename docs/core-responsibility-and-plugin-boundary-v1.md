# FrameForge Core Responsibilities and Plugin Boundary V1

## 中文

本文定义 FrameForge Core 的通用职责，以及 Core、项目自有规范、插件和 Host Adapter 之间的公开边界。它是架构基线，不要求一次性重写现有实现，也不代表所有专业能力已经完全插件化。

### 1. Core 的定位

Core 是通用基础设施，负责发现项目事实、读取项目自己的 Framework Profile、解析规范引用、协调已明确选择的能力，并汇总可追溯的建议与证据。

Core 不是统一规范裁判、项目开发 Gate，也不是容纳所有引擎专业知识的容器。

### 2. Core 应负责什么

- **项目发现**：只检查获授权的项目根目录和明确限定的路径；记录发现依据、置信度和扫描限制；不执行项目代码或插件代码，不修改项目文件。
- **Framework Profile**：读取和校验项目自己的 Profile，记录插件 ID、版本、规范引用和项目配置。缺失或无效配置产生非阻塞 Warning。
- **插件目录与生命周期**：发现内置及用户明确提供的声明式 Manifest；校验身份、版本、领域和能力声明；区分 Available、Discovered、Suggested、Selected、Evaluated、Unavailable、Not Evaluated。发现不等于启用。
- **规范解析**：解析项目自有规范引用，保留来源、版本、路径、适用范围和权威性不确定状态；不自动绑定、批准或改写规范。
- **建议与报告**：统一汇总发现、Profile、规范解析和插件证据；保留证据来源、评估状态和限制；框架建议默认不阻塞开发。
- **能力协调**：只协调项目明确选择且当前可用的能力；优先复用已有检查实现；不把缺失访问或未评估转换为 PASS。

### 3. 插件负责什么

插件负责领域专业知识，例如 Unity、Skynet、Godot、Unreal、Cocos Creator、C++、Art/UI 和 Asset Pipeline。

插件必须说明其 ID、版本、适用范围、证据来源、能力、失败状态和已知限制。插件不得静默修改项目文件或项目正式规范。

### 4. 当前 V1 的信任边界

当前外部插件是声明式 Manifest 扩展，只提供元数据，不授权执行任意外部代码。

选择外部 Manifest 只表示选择应用程序已经实现并明确分发的能力，不代表加载 Manifest 中的 Python、Lua 或其他可执行代码。未来如确实需要可执行插件，必须另行定义有版本的权限、调用、隔离、失败和输出契约。

### 5. Core 公共报告与兼容

CLI、本地 MCP 和授权 Host Adapter 必须使用同一 Core 语义。适配器可以改变展示方式，但不能各自定义插件启用、规范权威或发现结果语义。

当前 V1 报告字段是兼容基线。未来若统一字段或调整结构，必须通过显式 Schema 版本和迁移说明进行；不得由单个 Adapter 私自改名或重新解释字段。

每条发现应尽可能保留插件 ID/版本、状态、证据、建议、适用范围和限制。证据存在不等于实现正确；没有发现信号也不等于能力缺失。

### 6. Core 不应负责什么

- 不硬编码每种引擎、语言、美术领域或资源管线的详细规则。
- 不将发现的插件视为已启用。
- 不将规范引用视为项目负责人批准。
- 不自动创建、改写、批准或迁移项目规范。
- 不增加强制开发 Gate，不替代项目自己的评审、测试和验收。
- 不通过声明式 Manifest 执行任意第三方代码。
- 不要求项目采用特定仓库布局、开发流程、AI Host 或外部服务。

### 7. 渐进式解耦原则

Core 应依赖稳定、窄范围的通用分发边界，而不是直接依赖每个领域的 Validator。专业实现可以先留在现有模块中，不要求为了模块外观而全部移动或拆成独立安装包。

只有至少两个真实能力需要相同的通用机制，且现有 Manifest 无法表达时，才增加新的 Core 抽象。优先做小范围提取，并保持 V1 行为、报告字段和 CLI/MCP/Host 结果兼容。

当前实现差距应作为可追踪的架构事项记录，不自动构成大规模重构要求。

### 8. 非目标

本文不定义可执行插件 Runtime、插件市场、远程服务、数据库、强制 Validator 框架、统一规范目录或项目治理流程。

## English

This document defines the generic responsibilities of FrameForge Core and the public boundary between Core, project-owned standards, plugins and host adapters. It is an architecture baseline, not a mandate for a one-time rewrite or a claim that every specialist capability is already fully modular.

### 1. Core purpose

Core is shared infrastructure for discovering project facts, reading the project's own Framework Profile, resolving standard references, coordinating explicitly selected capabilities, and aggregating traceable advice and evidence.

Core is not a universal standards authority, a development gate, or a container for every engine's specialist knowledge.

### 2. Core responsibilities

- **Project discovery:** inspect only authorized roots and bounded paths; record evidence, confidence and scan limits; never execute project or plugin code during passive discovery; never modify project files.
- **Framework Profile:** read and validate the project-owned Profile, including plugin IDs, versions, standard references and project configuration. Missing or invalid data produces nonblocking warnings.
- **Plugin catalog and lifecycle:** discover built-in and explicitly supplied declarative manifests; validate identity, version, domain and capability declarations; distinguish Available, Discovered, Suggested, Selected, Evaluated, Unavailable and Not Evaluated. Discovery is not activation.
- **Standards resolution:** resolve project-owned references while preserving source, version, path, applicability and authority uncertainty. Never silently bind, approve or rewrite standards.
- **Advice and reports:** combine discovery, Profile, standards resolution and plugin evidence while preserving provenance, evaluation state and limitations. Framework advice is nonblocking by default.
- **Capability coordination:** coordinate only explicitly selected and available capabilities; reuse existing checks where possible; never turn missing access or unevaluated work into PASS.

### 3. Plugin responsibilities

Plugins own specialist knowledge such as Unity, Skynet, Godot, Unreal, Cocos Creator, C++, Art/UI and asset pipelines.

Each plugin must describe its ID, version, scope, evidence sources, capabilities, failure states and known limitations. Plugins must not silently modify project files or canonical project standards.

### 4. V1 trust boundary

Current external plugins are declarative Manifest extensions. They provide metadata and do not authorize arbitrary external code execution.

Selecting an external Manifest only selects capabilities already implemented and explicitly dispatched by the application. It does not load executable Python, Lua or other code from the Manifest. Any future executable plugin model requires a separate versioned contract for permissions, invocation, isolation, failures and outputs.

### 5. Public report and compatibility

CLI, local MCP and authorized Host adapters must share the same Core semantics. Adapters may present results differently, but must not define competing plugin activation, standards authority or finding semantics.

Current V1 report fields remain the compatibility baseline. Any future field normalization or structural change requires an explicit schema version and migration notes. An adapter must not independently rename or reinterpret fields.

Where applicable, each finding should preserve plugin ID/version, status, evidence, recommendation, applicability and limitations. Evidence does not prove correctness; absence of a signal does not prove a capability is missing.

### 6. Core non-responsibilities

- Do not hard-code detailed rules for every engine, language, art discipline or asset pipeline.
- Do not treat discovered plugins as activated.
- Do not treat a standard reference as owner approval.
- Do not create, rewrite, approve or migrate project standards automatically.
- Do not introduce mandatory development gates or replace project review, testing or acceptance.
- Do not execute arbitrary third-party code through declarative manifests.
- Do not require a specific repository layout, workflow, AI host or external service.

### 7. Incremental decoupling

Core should depend on a narrow, stable generic dispatch boundary rather than directly importing every domain validator. Specialist implementations may remain in their current modules; moving files or splitting every module into an installable package is not a goal by itself.

Add a new Core abstraction only when at least two real capabilities need the same reusable mechanism and the current Manifest cannot express it. Prefer narrow extractions that preserve V1 behavior, report fields and CLI/MCP/Host parity.

Track implementation gaps as explicit architecture work, not as automatic mandates for a broad rewrite.

### 8. Non-goals

This document does not define an executable plugin runtime, plugin marketplace, remote service, database, mandatory validator framework, universal standards catalog or project governance workflow.
