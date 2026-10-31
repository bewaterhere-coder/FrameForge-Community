# Product Scope V1 / 产品范围 V1

## 中文

FrameForge 是独立、可选的项目框架发现与规范建议工具。它不拥有项目开发状态，也不替代项目自己的正式规范、测试或验收流程。

### V1 能力
- 只读识别项目技术栈与已知项目标记。
- 通过声明式 Manifest 发现可用插件，不执行插件代码。
- 仅在项目 Profile 明确选择后，才运行对应的专业检查。
- 对规范缺失、引用失效、插件缺失和未知配置提供非阻塞 Warning。
- 提供可供 CLI、MCP 和其他授权 Host 使用的机器可读结果。

### 所有权与安全边界
项目拥有自己的正式规范。FrameForge 可以建议，但不会自动创建、覆盖或批准规范。发现插件不等于启用插件；插件注册信息是元数据，不构成执行任意代码的授权。CLI 和检查器只读目标项目。

### 验收原则
1. 新项目可以得到 Warning，但不因缺少框架定义而被阻断。
2. 多技术栈项目可以得到多个候选插件，但不会自动启用。
3. 已绑定规范只作为检查来源，不自动证明其已获项目负责人批准。
4. 未选择、缺失或无法可靠评估的能力应明确报告，不伪称 PASS。
5. FrameForge 不创建新的强制 Gate，不替代项目已有验收规则。

## English

FrameForge is a standalone, optional project-framework discovery and standards-advisory tool. It does not own project development status or replace project-owned standards, tests or acceptance processes.

V1 provides read-only technology discovery, declarative plugin discovery, explicit project-level plugin selection, non-blocking warnings and machine-readable output for authorized hosts. Plugin discovery never activates a plugin, and manifests do not authorize arbitrary code execution. Projects own their canonical standards; FrameForge may recommend but cannot create, overwrite or approve them. Missing or unevaluated capabilities must be reported honestly. FrameForge does not introduce mandatory gates or replace existing project acceptance rules.
