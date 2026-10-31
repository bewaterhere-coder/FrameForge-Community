# Defold Engine Plugin Candidate V0.1 / Defold 引擎插件候选 V0.1

## 中文

**状态：Candidate，未经真实 Defold 项目验证。** V0.1 仅通过项目根目录的 `game.project` 识别 Defold 项目，不提供 Lua 语义分析、Collection/GO 结构分析、资源引用验证、构建或运行时检查。

### 官方依据

- [Defold Project settings](https://defold.com/manuals/project-settings/)：官方说明 `game.project` 包含项目级设置，必须位于项目根目录且文件名固定为 `game.project`。文件使用 INI 格式；项目设置涵盖启动 Collection、资源、显示、输入、物理、网络和平台配置。

### 当前实现边界

- 唯一检测信号：项目根目录的 `game.project`。
- 不假设项目必须使用 `main/`、`scripts/`、`assets/` 等固定目录。
- 不从 `game.project` 的任意设置推断项目架构质量或运行正确性。
- 不分析 Lua、Collection、Game Object、脚本生命周期、资源依赖或扩展实现。
- 不执行 Defold Editor、Bob、Lua、原生扩展或项目代码；不修改项目文件。
- 发现 Defold 只会产生候选插件建议，不会自动启用插件。

### 后续验证要求

至少需要两个结构不同、由项目所有者授权的真实 Defold 项目，覆盖正常项目、非 Defold 负例、缺失 `game.project`、自定义资源目录、扩展/依赖差异及扫描边界。公开证据必须脱敏。Fixture、单元测试和官方文档阅读不能替代真实项目验证。

## English

**Status: Candidate; not validated on a real Defold project.** V0.1 detects a Defold project from the root-level `game.project` file only. It does not analyze Lua semantics, Collection/Game Object structure, asset references, builds or runtime behavior.

### Official reference

- [Defold Project settings](https://defold.com/manuals/project-settings/): Defold documents `game.project` as the required, fixed-name project settings file at the project root. It uses INI syntax and contains project-wide settings, including bootstrap, resources, display, input, physics, network and platform options.

### Current boundaries

- The only detection signal is a root-level `game.project`.
- No fixed `main/`, `scripts/` or `assets/` layout is assumed.
- Settings are not used to infer architecture quality or runtime correctness.
- Lua, Collections, Game Objects, lifecycle, asset dependencies and extension implementations are not analyzed.
- No editor, Bob build tool, Lua, native extension or project code is executed. Project files are never modified.
- Discovery suggests the candidate plugin but never activates it.

### Validation required for promotion

At least two structurally different real Defold projects are required, with project-owner authorization. Evidence should cover a positive project, a non-Defold negative case, missing `game.project`, custom asset layouts, extension/dependency differences and scan boundaries. Public evidence must be sanitized. Fixtures, unit tests and documentation review do not replace real-project validation.
