# Unreal Engine Plugin Candidate V0.1 / Unreal Engine 引擎插件候选 V0.1

## 中文

**状态：Candidate，未经真实 Unreal 项目验证。** 当前仅提供项目发现和两个可选目录级审查提示，不提供 C++/Blueprint 语义分析、UBT 构建验证、资产引用检查或运行时正确性检查。

### 官方依据

1. [Projects and Templates](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-projects-and-templates-in-unreal-engine)：每个 Unreal 项目有 `.uproject` 文件，项目资源和 Content Browser 的文件结构对应。
2. [Directory Structure](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-directory-structure)：常见目录包括 Config、Content、Source、Plugins、Binaries、Intermediate、Saved 等；其中部分是生成物或缓存，不应误判为正式源文件。
3. [Modules](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-modules)：C++ 模块由模块目录、`Build.cs`、Public/Private 等组织；模块可嵌套，不能假设固定单层布局。Blueprint-only 项目不要求 Source 目录。
4. [Plugins](https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine)：项目插件位于项目 `Plugins` 路径，使用 `.uplugin` 描述文件；插件可以包含代码、二进制和内容，不能只按目录名判断其完整性。

### 当前实现边界

- 唯一检测信号：项目根目录直接子项中的 `*.uproject` 文件名模式。只检查根目录，不递归、不跟随符号链接；这覆盖项目自定义名称，不要求项目重命名。
- `Plugins/` 存在时提示核对 `.uplugin` 描述文件、源码/二进制、引擎版本、许可证和维护责任；不判断插件已启用或可加载。
- `Source/` 存在时提示核对模块边界和 `Build.cs` 依赖；不存在时不报警，因为 Blueprint-only 项目可以没有 C++ Source。
- 不强制 `Content/`、`Config/`、`Source/`、`Plugins/` 目录同时存在，不把 `Intermediate/`、`Saved/`、`Binaries/` 当作正式源代码缺失。
- 不执行 Unreal Editor、UnrealBuildTool、Build.cs、插件脚本或项目代码；不修改项目文件。

### 已知缺口与下一版

根目录模式检测仅匹配直接子项，当前不递归搜索嵌套项目；如果仓库包含多个 `.uproject`，只报告一个稳定排序后的文件名作为发现证据，不代表所有项目都已分析。

### 后续验证要求

至少需要两个结构不同的真实 Unreal 5.x 项目，覆盖 C++ 与 Blueprint-only、项目自定义 `.uproject` 文件名、插件目录、模块嵌套、缺失配置、负例和扫描边界。获得项目所有者授权并脱敏后，才可评估升级为 Validated。Fixture 和单元测试不能替代真实项目验证。

## English

**Status: Candidate; not validated on a real Unreal project.** V0.1 provides project discovery and two optional directory-level review hints only. It does not analyze C++/Blueprint semantics, run UBT builds, inspect asset references or prove runtime correctness.

Official references: [Projects and Templates](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-projects-and-templates-in-unreal-engine), [Directory Structure](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-directory-structure), [Modules](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-modules), and [Plugins](https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine). Projects use a `.uproject` descriptor; C++ modules use module directories and `Build.cs` dependency declarations; modules may be nested; Blueprint-only projects need not contain `Source`; project plugins use `.uplugin` descriptors and may include code, binaries and content.

V0.1 detects root-level `*.uproject` files by filename pattern. It does not recurse into nested directories or follow symlinks. If multiple project descriptors exist, discovery reports one stable-sorted filename as evidence; it does not claim to inspect every project. `Plugins/` and `Source/` presence produce nonblocking review hints only; neither absence nor presence proves correctness. No editor, build tool, project code or plugin code is executed, and no files are changed.

Promotion to Validated requires authorized evidence from at least two structurally different real Unreal 5.x projects, including C++ and Blueprint-only, custom descriptor names, nested modules, plugin layout, missing configuration, negative cases and scan boundaries. Fixtures and unit tests are insufficient.
