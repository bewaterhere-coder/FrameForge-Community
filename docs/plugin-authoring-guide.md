# Plugin Authoring Guide / 插件开发指南

## 中文

本指南面向希望为 FrameForge 增加游戏引擎或专业领域支持的社区贡献者。**优先提交声明式 Manifest，不要先写代码。** 当前外部插件是只读元数据：FrameForge 不导入、不执行插件脚本，也不会因发现引擎而自动启用插件。

### 1. 先确定贡献类型

| 类型 | 适用情况 | 最低证据 | 默认状态 |
|---|---|---|---|
| Engine candidate | 新引擎识别、目录线索和规范建议 | 可访问的官方文档来源；说明适用版本 | Candidate |
| Guidance improvement | 改进现有插件的建议、边界或误报说明 | 官方文档或明确标注的社区来源 | Candidate，等待维护者评审 |
| Real-project validation | 验证候选规则在真实项目中是否有用 | 获授权、脱敏、可复核的项目证据及负例 | 由维护者评估是否可标记 Validated |
| Core capability | 只有 Manifest 无法表达的通用能力 | 说明现有声明式接口为何不足，并提供安全/兼容测试 | 单独评审，不作为普通插件的默认路线 |

没有真实项目并不妨碍提交候选插件。**单元测试、文档示例或合成 Fixture 不能证明真实项目已验证。**

### 2. 创建独立 Manifest

先复制 [`examples/plugin-manifests/example-engine.json`](../examples/plugin-manifests/example-engine.json)，改为自己的文件名，例如 `godot.json` 或 `unreal.json`。通过 `--plugin-dir` 显式加载：

```sh
frameforge --plugins --plugin-dir ./my-plugin-manifests
frameforge /path/to/project --plugin-dir ./my-plugin-manifests
```

Manifest 字段：

- `id`：稳定、全小写的插件 ID；不要与内置 ID 冲突。
- `evidence_level`：可选的 `candidate` / `validated` 声明；升级必须经过维护者核验证据。
- `sources`：可选来源数组，记录发布方、标题、URL、适用引擎版本和查阅日期。
- `version`：插件自身版本，不是引擎版本。
- `domain`：专业领域，例如 `code`、`art-ui`、`asset-pipeline`。
- `standards`：该插件可关联的规范领域名称。
- `detection`：路径组；**同一组内所有路径都存在**才匹配，该字段只做路径检测。
- `detection_globs`：可选的项目根目录文件名模式，只检查根目录直接子项，不递归、不跟随符号链接；适用于项目名不固定的引擎描述文件。
- `content_markers`：可选的文件内容标记；只用于有限识别，不得放私有项目名称、密钥或用户数据。
- `advisories`：可选的路径级建议。路径存在只代表发现线索，不代表符合规范。
- `professional_guidance`：可选的受限源码字面信号建议，不是语法树或控制流分析。

路径必须是相对项目根目录的路径，不得包含绝对路径或 `..`。不要依赖用户机器的绝对目录、账号、项目代号或私有仓库结构。建议使用引擎官方定义且跨项目稳定的文件名/目录作为检测线索；若某线索仅适用于部分版本，应在文档中明确版本范围。

### 3. 验证等级与来源

每个新插件 PR 必须在说明中写明：

- **Candidate**：依据官方文档或社区资料形成的候选规则，尚未在真实项目验证。
- **Validated**：有授权真实项目的可复核验证，包括适用版本、正例、负例、缺失/不适用路径、扫描边界和结果。不得公开项目私有源码、路径、提交号、截图或业务标识；必要时只提交脱敏测试说明。

每条来源标注发布方、文档标题、适用引擎版本、URL 和查阅日期。官方文档、社区文章、个人经验要分开标记。FrameForge 社区建议不是引擎厂商认证。

### 4. 必需测试

对新检测规则至少覆盖：

1. 正例：目标项目特征存在。
2. 负例：相似但不属于目标引擎/领域的项目。
3. 缺失：关键文件不存在。
4. 版本/布局差异：不适用版本不得误报为已确认缺陷。
5. 安全边界：绝对路径、`..` 路径、符号链接逃逸不能访问项目根目录外内容。
6. 行为边界：发现不等于启用；未选择插件不运行专业检查；不修改项目文件；结果不产生阻塞 Gate。

运行：

```sh
PYTHONPATH=src python -m unittest discover -s tests -q
python -m pip wheel --no-deps --no-build-isolation -w /tmp/frameforge-wheel .
```

### 5. 何时需要修改 Core

只有多个插件确实需要相同的通用能力、且现有 Manifest 无法表达时，才提议 Core 变更。提案应包括至少两个不同插件的真实用例、向后兼容策略、失败路径和测试。不要为单个引擎增加专属 Core 模块，不要执行第三方插件代码，不要引入后台服务或数据库。

### 6. 提交 PR

PR 应包含：插件 ID/版本、引擎版本范围、官方/社区来源、Manifest、正负例测试、Candidate/Validated 声明、已知误报与未覆盖范围。维护者可要求缩小范围或保持 Candidate。合并不等于引擎厂商背书，也不代表整个引擎技术栈已被完整验证。

## English

This guide is for contributors adding game-engine or specialist guidance. **Start with a declarative manifest, not code.** External plugins are read-only metadata: FrameForge does not import or execute plugin scripts, and engine discovery never activates a plugin.

### 1. Choose the contribution type

| Type | Use it for | Minimum evidence | Default status |
|---|---|---|---|
| Engine candidate | Engine detection, path hints and standards advice | Accessible official references and version scope | Candidate |
| Guidance improvement | Better advice, boundaries or false-positive notes | Official docs or clearly labeled community sources | Candidate pending review |
| Real-project validation | Evidence that a candidate rule works in a real project | Authorized, sanitized, reproducible project evidence including negative cases | Maintainer may assess Validated status |
| Core capability | A reusable capability that manifests cannot express | Why the declarative contract is insufficient plus safety/compatibility tests | Separate review; not the default plugin path |

A real project is not required to submit a candidate. Unit tests, documentation examples and synthetic fixtures do **not** prove real-project validation.

### 2. Create a standalone manifest

Copy [`examples/plugin-manifests/example-engine.json`](../examples/plugin-manifests/example-engine.json) and give it a stable filename such as `godot.json` or `unreal.json`. Load it explicitly with `--plugin-dir`. The manifest defines a stable plugin ID/version, domain, standards, optional evidence level and source records, path detection groups, optional root-level filename globs, optional content markers, path advisories and bounded literal source hints. Detection groups require all paths in a group. File presence is evidence only, never compliance.

Paths must be project-relative and must not contain absolute roots or `..`. Do not encode private project names, account paths, repository layouts, secrets or user data. Document engine-version scope and layout differences. Distinguish vendor documentation from community advice.

### 3. Evidence levels

- **Candidate** means documentation- or community-based guidance not yet verified in a real project.
- **Validated** requires authorized, reproducible real-project evidence: engine version, positive and negative cases, missing/inapplicable paths, scan boundaries and results. Never publish private source, paths, commit IDs, screenshots or business identifiers. Synthetic fixtures alone are insufficient.

For every source, record publisher, title, engine version scope, URL and access date. Community guidance is not vendor certification.

### 4. Required tests

Cover positive, negative, missing, version/layout differences, path traversal and symlink escape, explicit activation, read-only behavior and nonblocking results. Run the unit suite and build a wheel using the commands above.

### 5. When to change Core

Only propose a core change when multiple plugins need the same reusable capability and the manifest contract cannot express it. Include use cases from at least two distinct plugins, compatibility, failure paths and tests. Do not add one-off engine modules, execute third-party plugin code, or add background services/databases.

### 6. Open a PR

Include plugin ID/version, engine version range, sources, manifest, positive/negative tests, evidence level, false positives and exclusions. Maintainers may keep the plugin at Candidate or narrow its scope. Merge is not vendor endorsement or proof of complete engine coverage.
