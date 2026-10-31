# FrameForge

**插件化项目框架与规范指导 / Pluggable Project Framework Intelligence**

FrameForge 是独立的、只读的框架发现与规范建议工具。项目拥有自己的规范真源；技术栈发现时可提供候选插件和路径级建议；只有显式选择插件后才运行相应的专业检查。

## 中文

### 快速开始

需要 Python 3.10+ 和 Git。当前先从 GitHub 源码安装（尚未提供 PyPI 安装包）：

```sh
git clone https://github.com/bewaterhere-coder/FrameForge-Community.git
cd FrameForge-Community
python -m pip install .
```

检查插件清单，再把路径替换成你自己的 Unity 或其他游戏项目目录：

```sh
frameforge --plugins
frameforge /path/to/your/game-project
```

首次检查只会发现技术栈和报告规范缺口，不会修改项目或自动启用插件。要启用专业检查，在**项目自身**建立 `.frameforge/profile.json`，明确填写插件 ID、版本和项目正式规范路径，格式参见 [Profile 示例](docs/profile-example.json)。检查命令仍为 `frameforge /path/to/your/game-project`。

### 贡献者开发环境

```sh
python -m pip install -e '.[mcp]'
PYTHONPATH=src python -m unittest discover -s tests -q
```

只有开发或运行本地 stdio MCP Server 时才需要安装可选的 `mcp` 依赖。普通使用者只需按上面的快速开始安装。

> 当前发布方式是从 GitHub 源码安装；PyPI 发布尚未进行。普通使用者不需要安装开发依赖或运行测试套件。

### 通过 AI Host 使用

在已授权项目目录和可用的 Python 环境中，用户可以直接对连接了项目环境的 AI 说：**“检查这个项目的框架规范，告诉我已绑定的规范、候选文档、需要确认的事项和未评估的检查。”** AI Host 可调用 `frameforge.host_adapter.inspect_project(project)`，并使用 `explain_warnings` 解读 Warning、`verify_remediation` 重新检查。三者均只读。这些接口需要由已连接且获授权的 Host 调用；没有环境连接的 AI 不能仅靠自然语言访问用户本机项目。

结果应优先解释 `suggested_plugins`（仅发现、未自动启用）、`standard_sources`（已绑定引用不等于 Owner 已批准）、`standard_candidates`（有限文件名候选，可能误报/遗漏）、`standard_authority_review`（仅列待确认关系，不判断内容冲突）、`clause_coverage`（没有检查规则时为空；证据命中也不是合规 PASS），最后区分 `warnings`、专业审查建议与 `blocking=false`。项目负责人自行确认插件选择、正式规范和改动授权。详见 [自然语言使用案例与验收边界](docs/ai-host-end-to-end-v1.md)。

### 本地 MCP 与 CLI 双入口

CLI 保持 `frameforge /path/to/project`；如需 AI 客户端直接调用，可安装 `python -m pip install -e '.[mcp]'` 并将 `frameforge-mcp` 注册为本地 stdio MCP Server。两者共用同一只读核心。配置示例及安全边界见 [Local MCP V1](docs/local-mcp-v1.md)。

### 内置插件能力

| 插件 | 当前能力 | 重要边界 |
|---|---|---|
| Unity | 技术栈发现；asmdef 图、GUID、包声明上下文；生命周期和程序集源码提示 | 外部包声明不证明已解析；不运行 Unity 编译或 PlayMode |
| Skynet | 技术栈发现；显式指定事务源的 COMMIT / ROLLBACK、锁、版本条件及幂等重放证据线索；Actor/持久化提示 | 不分析完整 Lua 控制流；不证明数据库事务正确 |
| Art/UI | 项目规范条款、实现文本和 Unity 资源引用与 Addressables 关系证据 | 需显式配置相关检查；不证明视觉质量或运行时表现 |
| Godot | <code>project.godot</code> 项目发现；第三方 <code>addons/</code> 来源审查提示（Candidate，未做真实项目验证） | 不提供场景树、GDScript、资源导入或运行时检查 |
| Unreal Engine | 根目录 <code>*.uproject</code> 发现；<code>Plugins/</code> 与 <code>Source/</code> 目录审查提示（Candidate，未做真实项目验证） | 不提供 C++/Blueprint 语义、UBT 构建或运行时检查 |
| Defold | 根目录 <code>game.project</code> 发现（Candidate，未做真实项目验证） | 不提供 Lua、Collection、资源依赖、构建或运行时检查 |
| Cocos Creator、C++、Asset Pipeline | 声明式发现与规范缺口提示 | 不提供等价于 Unity / Skynet 的专业实现检查 |

外部插件通过 `--plugin-dir` 明确加载声明式 Manifest，**不会运行外部插件代码**，参见 [扩展契约](docs/plugin-extension-v1.md)。Godot 和 Unreal Engine 支持目前仅为 Candidate，分别见 [Godot 候选说明](docs/godot-candidate-v0.1.md)、[Unreal 候选说明](docs/unreal-engine-candidate-v0.1.md) 和 [Defold 候选说明](docs/defold-candidate-v0.1.md)。社区贡献者请先阅读[插件开发指南](docs/plugin-authoring-guide.md)，并使用[Manifest 示例](examples/plugin-manifests/example-engine.json)与[Schema](docs/plugin-manifest.schema.json)。插件发现不等于激活；缺失规范、无效引用等通过 `warnings` 提示；候选静态风险位于专业指导或结构观察字段，不一定进入 `warnings`。它们都不阻塞开发、提交或合并。

### 从零上手与跨系统协作

推荐按 [最佳实践：多仓项目完整教程](docs/best-practices.md) 操作：明确正式规范真源 → 对各仓库分别发现 → 显式选择插件和绑定项目 Profile → 用 CLI、本地 MCP 或已连接 AI Host 运行只读检查 → 核对真实代码与测试 → 在项目自身的流程内整改与验收。教程也说明了常见误判、连接与目录授权边界。


### 使用与证据解读

[完整项目操作流程](docs/v1-advisory-workflow.md) 按“发现 → 选择插件 → 绑定规范 → 阅读证据 → 持续维护”组织；真实项目案例应由项目所有者单独授权并脱敏后再公开。输出中的 `observed` 或 `evidence_found` 仅表示找到静态信号，`not_evaluated` 不是违规判定，`blocking` 恒为 `false`。FrameForge 不接管正式验收、发布或部署。

**状态：V1 Advisory Pilot。** 具备只读项目发现、规范绑定和试用级专业指导能力，不宣称能自动认证完整架构合规性。

## English

FrameForge is a standalone, read-only project framework discovery and standards advisory tool. Projects own their canonical standards. Discovery may return path-level advisory previews but never activates professional checks, and findings never create a development gate.

### Quick start

Requirements: Python 3.10+ and Git. Install from the public GitHub repository (a PyPI package is not published yet):

```sh
git clone https://github.com/bewaterhere-coder/FrameForge-Community.git
cd FrameForge-Community
python -m pip install .
```

List available plugins, then inspect your own Unity or other game project:

```sh
frameforge --plugins
frameforge /path/to/your/game-project
```

Inspection is read-only and does not activate plugins. For opt-in checks, create a project-owned `.frameforge/profile.json` with explicit plugin IDs/versions and canonical standard references; see the [profile example](docs/profile-example.json). Ordinary users do not need development dependencies or the test suite.

### Contributor setup and tests

```sh
python -m pip install -e '.[mcp]'
PYTHONPATH=src python -m unittest discover -s tests -q
```

The optional `mcp` extra is only needed when running the local stdio MCP server.

### Use through a connected AI host

With an authorized project environment and Python host, ask the AI to inspect the project's framework standards. The host can invoke `frameforge.host_adapter.inspect_project`, `explain_warnings`, and `verify_remediation` as read-only operations. These APIs require a connected, authorized host; a disconnected assistant cannot access local projects. Plugin discovery does not activate plugins; candidate standards do not imply approval; filename domain hints are not content-level conflict checks; empty clause coverage does not imply compliance. See [end-to-end workflow and acceptance boundaries](docs/ai-host-end-to-end-v1.md).

### Local MCP and CLI

The optional local stdio MCP entrypoint is `frameforge-mcp` (`pip install -e '.[mcp]'`). It shares the same read-only core as CLI; see [Local MCP V1](docs/local-mcp-v1.md).

### End-to-end tutorial

Follow the [bilingual best-practices walkthrough](docs/best-practices.md) for a multi-repository project: discover, explicitly select plugins, bind project-owned standards, invoke CLI/MCP/AI host, review evidence, and use the project's existing remediation and acceptance process. The report is supplemental evidence, not an automatic gate or formal acceptance decision. Missing access must be reported as not evaluated.

### Built-in capability matrix

| Plugin | Available advisory capability | Not proven |
|---|---|---|
| Unity | asmdef graph, GUID and manifest context, lifecycle and assembly hints | Package resolution, Unity compilation or PlayMode correctness |
| Skynet | Explicit transaction-source COMMIT/ROLLBACK, lock, version predicates and idempotency/replay evidence hints | Lua control-flow correctness or MySQL atomicity |
| Art/UI | Selected standard clauses, implementation text, Unity asset-reference and Addressables relationships | Visual quality or runtime behavior |
| Defold | Root-level `game.project` discovery (Candidate; no real-project validation) | Lua, Collection, asset dependency, build or runtime checks |
| Cocos Creator, C++, Asset Pipeline | Declarative discovery and standards-gap advice | Comparable implementation-level auditing |

Optional external manifests must be loaded explicitly with `--plugin-dir`; they never execute plugin code. Read the [extension contract](docs/plugin-extension-v1.md), [complete workflow](docs/v1-advisory-workflow.md) and documented workflow.

`evidence_found` and `observed` mean that bounded static evidence exists, not compliance. `not_evaluated` does not mean a violation. Missing standards and invalid references appear in `warnings`, while static review signals appear under guidance or structural observations and may leave `warnings` empty. `blocking=false` keeps all advisory results non-blocking. FrameForge does not perform formal project acceptance, release or deployment.

**Status: V1 Advisory Pilot**, not a full architecture conformity validator.

### 贡献与候选插件

欢迎社区提交游戏引擎、Art/UI、Asset Pipeline 规范候选。详见 [贡献指南](CONTRIBUTING.md)、[社区维护指南](docs/community-maintenance-guide.md)、[社区行为准则](CODE_OF_CONDUCT.md)、[引擎候选提案模板](.github/ISSUE_TEMPLATE/engine_candidate.md) 、[安全报告规则](SECURITY.md) 和 [GitHub Discussions](https://github.com/bewaterhere-coder/FrameForge-Community/discussions)。候选规则不意味着真实工程验证通过；项目自有规范仍然优先。**本项目采用 Apache License 2.0，详见仓库根目录 `LICENSE`。**

### Community contributions

Contributions of engine, Art/UI and asset-pipeline guidance are welcome. See [Contributing](CONTRIBUTING.md), the [Community Maintenance Guide](docs/community-maintenance-guide.md), the [Code of Conduct](CODE_OF_CONDUCT.md), the [engine candidate template](.github/ISSUE_TEMPLATE/engine_candidate.md) and [Security Policy](SECURITY.md), and [GitHub Discussions](https://github.com/bewaterhere-coder/FrameForge-Community/discussions). Candidate guidance is not real-project validation, and project-owned standards remain authoritative. **This project is licensed under Apache License 2.0; see the root `LICENSE` file.**
