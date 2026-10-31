# Built-in Professional Capabilities and Extension Boundaries V1

## 中文

本文根据 Community 当前代码记录内置专业能力的真实范围、实现边界和后续扩展顺序。它不代表完整引擎验证，也不要求建设新的插件 Runtime。

### 1. 当前分层

| 层 | 当前职责 |
|---|---|
| Core（core.py） | 项目发现、Manifest 读取、Profile 校验、规范解析和统一报告 |
| 内置分发器（plugin_checks.py） | 仅分发项目已发现且由 Profile 明确选择的内置检查 |
| 专业检查 | Unity、Skynet、Art/UI 的有限只读静态检查 |
| Manifest | 声明插件身份、版本、领域、发现条件和建议 |
| CLI / MCP / Host | 调用同一 Core，不自行定义检查语义 |

外部 Manifest 仅是声明式元数据，不会执行其中引用的 Python、Lua、C++ 或其他代码。新增 Manifest 不等于新增可执行专业检查。

### 2. 能力现状

| 插件 | 当前实现 | 证据范围 | 未覆盖内容 | 当前状态 |
|---|---|---|---|---|
| Unity | structure.unity_assemblies；Manifest 建议 | asmdef 图、GUID、重复名称、项目内 Packages 声明上下文 | 不运行 Unity 编译、Build、PlayMode；不完整解析包依赖 | 内置静态检查 |
| Skynet | structure.skynet_transaction；Manifest 建议 | 显式指定 Lua 文件中的有限事务标记、SQL 和失败路径线索 | 不是 Lua AST/控制流分析；不证明事务原子性、CAS 或幂等 | 内置静态检查 |
| Art/UI | art_ui_standards、art_ui_evidence、art_ui_unity_binding | 项目条款定位、受限文本信号、Unity GUID/Addressables 关系 | 不评价视觉质量、实际布局或运行时表现 | 内置静态检查 |
| Cocos Creator | cocos-creator.json | 路径组合发现 | 无专业实现检查 | Manifest-only |
| C++ | cpp.json | CMake / Meson 发现 | 无 AST、构建图或依赖方向检查 | Manifest-only |
| Asset Pipeline | asset-pipeline.json | 声明式领域发现 | 无导入、引用、构建或运行时检查 | Manifest-only |
| Godot | godot.json | 项目发现与 Addons 提示 | 未做真实项目验证；无 Scene/GDScript/导入检查 | Candidate |
| Unreal | unreal.json | .uproject 发现、Plugins/Source 路径提示 | 未做真实项目验证；无 C++/Blueprint/UBT 检查 | Candidate |
| Defold | defold.json | game.project 发现 | 未做真实项目验证；无 Lua/Collection/资源检查 | Candidate |

“内置静态检查”表示本仓库有实现和自动化测试，不表示通过真实引擎、真实项目或厂商验证。Candidate 与 Validated 必须严格区分。

### 3. 代码边界审查

已经具备：
- core.py 不再直接导入 Art/UI Validator；通过 plugin_checks.py 的 Profile 校验入口使用它们。
- Art/UI 标准、实现文本和 Unity 资源关系分属独立模块。
- Unity、Skynet 只在插件被发现且由项目 Profile 选择后执行。
- Skynet 事务源由 Profile 显式指定，不自动扫描任意 Lua 文件。
- 所有检查只读、非阻塞，缺失证据不得视为 PASS。

仍存在的耦合：
- structure.py 同时包含 Unity asmdef 与 Skynet 事务检查，两个领域相互独立。
- plugin_checks.py 集中了解 Unity、Skynet、Art/UI 的具体实现函数。
- Manifest 发现与专业检查实现分离；声明一个插件不会自动产生新的专业执行能力。

### 4. 独立扩展路径

1. **Manifest-only**：适用于项目标记、路径发现、文件存在提示和有限字面信号。优先采用。
2. **内置专业检查**：当领域需要结构化证据、跨文件关系或 Manifest 无法安全表达的算法时，才增加 FrameForge 自身的受限实现。
3. **Core 通用能力**：只有至少两个不同领域存在真实共同需求，且现有接口无法表达时才修改 Core。单一引擎规则不得进入 Core。

Unity 与 Skynet 可以在它们下次需要真实代码改动时，从 structure.py 拆到各自领域模块。此项不应仅为目录美观而立即重构；不需要动态导入、第三方代码执行或新 Runtime。

### 5. 新专业检查要求

- 明确领域、插件 ID、版本范围和适用项目。
- 覆盖正例、负例、缺失、错误输入和不适用情况。
- 限制扫描根目录、文件大小、递归范围和符号链接。
- 只有项目明确选择且插件已发现时才执行。
- 保留证据路径、来源、状态、置信度、建议和限制。
- 不修改项目、不运行项目代码、不连接项目数据库或外部服务。
- 结果非阻塞；静态信号不能描述成运行验证。
- Candidate 升级为 Validated 必须有授权、脱敏、可复核的真实项目证据；合成 Fixture 和单元测试不够。

### 6. 建议演进顺序

1. 保持 Core 和 Manifest 契约稳定。
2. 补充 Cocos Creator、C++、Asset Pipeline 的官方来源及正负例发现测试，保持 Manifest-only。
3. 有真实贡献用例后再评估 Godot、Unreal、Defold 的专业检查。
4. Unity、Skynet、Art/UI 只针对真实误报、漏报或新证据需求扩展。
5. Unity 与 Skynet 在下一次相关代码改动时再拆分领域模块，并保持报告兼容。

### 7. 非目标

不引入可执行第三方插件、动态模块加载、插件市场、远程服务、数据库、后台进程、统一引擎抽象或新的强制 Gate。

## English

This document records the actual scope, implementation boundaries and extension order of Community's built-in specialist capabilities. It does not claim complete engine validation or require a new plugin runtime.

### 1. Current layers

| Layer | Responsibility |
|---|---|
| Core (core.py) | Project discovery, Manifest loading, Profile validation, standards resolution and unified reports |
| Built-in dispatcher (plugin_checks.py) | Dispatch only built-in checks for plugins discovered and explicitly selected by the project Profile |
| Specialist checks | Bounded, read-only static checks for Unity, Skynet and Art/UI |
| Manifest | Declare plugin identity, version, domain, detection and advice |
| CLI / MCP / Host | Invoke the same Core without redefining check semantics |

External Manifests are declarative metadata only. They do not execute referenced Python, Lua, C++ or other code. Adding a Manifest does not add executable specialist checks.

### 2. Capability inventory

| Plugin | Current implementation | Evidence scope | Not covered | Status |
|---|---|---|---|---|
| Unity | structure.unity_assemblies; Manifest advice | asmdef graph, GUIDs, duplicate names and checked-in Packages declaration context | No Unity compile, Build or PlayMode; no complete package resolution | Built-in static check |
| Skynet | structure.skynet_transaction; Manifest advice | Bounded transaction, SQL and failure-path hints in a Profile-specified Lua file | Not Lua AST/control-flow analysis; does not prove atomicity, CAS or idempotency | Built-in static check |
| Art/UI | art_ui_standards, art_ui_evidence, art_ui_unity_binding | Project clause location, bounded text signals and Unity GUID/Addressables relations | No visual quality, actual layout or runtime assessment | Built-in static check |
| Cocos Creator | cocos-creator.json | Path-combination discovery | No specialist implementation check | Manifest-only |
| C++ | cpp.json | CMake / Meson discovery | No AST, build graph or dependency-direction check | Manifest-only |
| Asset Pipeline | asset-pipeline.json | Declarative domain discovery | No import, reference, build or runtime asset check | Manifest-only |
| Godot | godot.json | Project discovery and Addons advice | No real-project validation; no Scene/GDScript/import checks | Candidate |
| Unreal | unreal.json | .uproject discovery and Plugins/Source path advice | No real-project validation; no C++/Blueprint/UBT checks | Candidate |
| Defold | defold.json | game.project discovery | No real-project validation; no Lua/Collection/asset checks | Candidate |

“Built-in static check” means code and automated tests exist in this repository. It does not mean validation against a real engine, real project or vendor certification. Candidate and Validated remain distinct.

### 3. Code-boundary review

Already in place:
- core.py no longer imports Art/UI validators directly; it uses the Profile-validation entrypoint in plugin_checks.py.
- Art/UI standards, implementation text and Unity asset relationships are separate modules.
- Unity and Skynet run only when discovered and explicitly selected in the project Profile.
- The Skynet transaction source is explicitly specified by the Profile; arbitrary Lua files are not scanned.
- Checks are read-only and non-blocking; missing evidence is not PASS.

Remaining coupling:
- structure.py contains both Unity asmdef and Skynet transaction checks, although they are separate domains.
- plugin_checks.py directly knows the concrete Unity, Skynet and Art/UI implementation functions.
- Manifest discovery is separate from specialist execution; a Manifest alone does not add a specialist check.

### 4. Independent extension paths

1. **Manifest-only:** project markers, path discovery, file-presence advice and bounded literal signals. Prefer this path.
2. **Built-in specialist checks:** add a bounded FrameForge implementation only when a domain needs structured evidence, cross-file relationships or an algorithm that the Manifest cannot safely express.
3. **Generic Core capability:** change Core only when at least two distinct domains share a real need that the existing interface cannot express. A single engine's rules do not belong in Core.

Unity and Skynet may move out of structure.py into domain modules when either area next needs a real code change. Do not perform this only for cosmetic organization. No dynamic imports, third-party code execution or new runtime is required.

### 5. Requirements for new specialist checks

- State the domain, plugin ID, version range and project applicability.
- Cover positive, negative, missing, invalid and not-applicable cases.
- Bound scan roots, file sizes, recursion and symlink behavior.
- Run only when the project explicitly selects a discovered plugin.
- Preserve evidence paths, provenance, status, confidence, advice and limits.
- Never modify projects, execute project code, or connect to project databases or external services.
- Keep results non-blocking; static signals are not runtime validation.
- Candidate becomes Validated only with authorized, sanitized and reproducible real-project evidence. Synthetic fixtures and unit tests are insufficient.

### 6. Recommended evolution order

1. Keep Core and the Manifest contract stable.
2. Improve official-source coverage and positive/negative discovery tests for Cocos Creator, C++ and Asset Pipeline; keep them Manifest-only.
3. Evaluate Godot, Unreal and Defold specialist checks only when real contributor use cases exist.
4. Extend Unity, Skynet and Art/UI only for demonstrated false positives, false negatives or new evidence needs.
5. Split Unity and Skynet into domain modules when those areas next need code changes, preserving report compatibility.

### 7. Non-goals

No executable third-party plugins, dynamic module loading, plugin marketplace, remote services, databases, background processes, universal engine abstraction or new mandatory gates.
