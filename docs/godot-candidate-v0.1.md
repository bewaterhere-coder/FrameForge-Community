# Godot Engine Plugin Candidate V0.1 / Godot 引擎插件候选 V0.1

## 中文

**状态：Candidate，未经真实 Godot 项目验证。** 当前仅提供项目发现和一个可选的第三方 Addon 目录审查提示，不提供 Godot 代码架构、场景树、资源导入或运行时正确性检查。不得将本候选描述为已验证的 Godot 专业规范插件。

### 官方依据

1. [Project organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/project_organization.html)：Godot 项目以文件系统组织资源，项目结构没有强制统一方案；官方建议按场景/资源关系组织，并给出目录和命名建议。
2. [Nodes and Scenes](https://docs.godotengine.org/en/stable/getting_started/step_by_step/nodes_and_scenes.html)：节点构成场景树，场景可组合与复用，主场景在 `project.godot` 中配置。
3. [Scene organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)：场景组织应考虑节点依赖与边界；Autoload 适用于确有全局生命周期/访问需求的系统，不应默认将所有管理器设为全局单例。
4. [Import process](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/import_process.html)：资源导入由 Godot 管理，内部导入缓存位于 `.godot/imported/`；运行时资源访问应使用 ResourceLoader 等引擎资源接口，而不是依赖编辑器缓存路径。

### 当前实现边界

- 唯一检测信号：项目根目录 `project.godot`。这是引擎项目入口的候选识别，不证明项目完整或可运行。
- 可选提示：发现 `addons/` 时提醒维护者核对第三方 Addon 的来源、许可证、Godot 版本兼容和维护责任。目录存在不表示风险或违规。
- 不假设 `scenes/`、`scripts/`、`assets/` 等固定目录必须存在。Godot 官方明确允许项目按自身需要组织文件。
- 不检查 Autoload 数量、节点树、场景引用、GDScript 类型、资源导入缓存或导出结果；这些需要更可靠的项目上下文、版本适配和真实工程验证。
- 不执行 GDScript、Editor Plugin 或任何项目代码；不运行 Godot Editor；不修改项目文件。

### 后续验证要求

至少需要两个结构不同的真实 Godot 4.x 项目，覆盖正例、非 Godot 负例、缺失项目配置、常见自定义目录布局、Addon 版本/许可证证据及扫描边界。获得项目所有者授权并脱敏后，才可评估从 Candidate 升级为 Validated。Fixture 和本仓库单元测试不能代替真实项目验证。

## English

**Status: Candidate; not validated on a real Godot project.** V0.1 provides project discovery and one optional third-party Addon review hint only. It does not provide Godot architecture, scene-tree, asset-import or runtime-correctness checks.

Official references: [Project organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/project_organization.html), [Nodes and Scenes](https://docs.godotengine.org/en/stable/getting_started/step_by_step/nodes_and_scenes.html), [Scene organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html), and [Import process](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/import_process.html). Godot allows project-specific filesystem organization; scenes are composed from nodes; the main scene is configured in `project.godot`; Autoloads are an explicit lifecycle choice; imported assets are managed by the engine.

The only detection signal is a root-level `project.godot`. An `addons/` directory triggers a non-blocking provenance/license/version-ownership review hint, not a defect. No conventional `scenes/`, `scripts/` or `assets/` layout is required. The plugin does not execute project code, invoke the editor, mutate files or claim runtime validation.

Promotion to Validated requires authorized evidence from at least two structurally different real Godot 4.x projects, including positive/negative cases, missing configuration, custom layouts, addon provenance and scan boundaries. Fixtures and unit tests are insufficient.
