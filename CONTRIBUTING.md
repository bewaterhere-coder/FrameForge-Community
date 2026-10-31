# Contributing to FrameForge / 参与贡献

## 中文

欢迎维护引擎插件、代码/资源/UI 规范建议、文档和测试。新增引擎前请先阅读[插件开发指南](docs/plugin-authoring-guide.md)、[Manifest 示例](examples/plugin-manifests/example-engine.json)和[Manifest Schema](docs/plugin-manifest.schema.json)。FrameForge 是**非阻塞**的框架指导工具，不是项目正式规范的所有者。

### 提交流程

1. 提交 Issue，说明引擎与版本、问题或候选规范、官方参考资料、实际项目证据（如有）。不得上传私有代码、密钥、用户数据或未经许可的第三方素材。
2. 从 `main` 创建独立分支，优先编辑声明式 `src/frameforge/manifests/*.json`；不要直接扩展核心或执行第三方脚本。
3. 明确标记规范的证据等级：`candidate`（官方/社区参考，但未经真实项目验证）或 `validated`（已提供可复核的真实项目验证）。单元测试通过不能提升为 `validated`。
4. 添加正例、负例、缺失与边界测试；运行 `PYTHONPATH=src python -m unittest discover -s tests -q`。CLI 和 MCP 应保持相同的只读、显式选择、非阻塞语义。
5. 提交 PR，附官方引用、版本范围、风险与限制、测试命令和实际输出。由维护者评审；提交 PR 不代表接受规范或批准发布。

### 插件约束

- Discovery 不等于 Activation；必须由使用者显式选择。
- 候选插件不能修改项目文件，不能自动绑定标准，不能引入额外 Gate。
- 项目自定义规范优先；缺少规则、无匹配信号时应报告未评估，而不是虚构违规。
- 必须说明插件 ID、版本、检测依据、适用/不适用范围、建议内容、参考来源和已知误报。
- 非官方建议应注明社区来源和适用范围；不得将本仓库的建议描述为引擎厂商的官方认证。

### 测试与评审

候选插件允许在缺少真实工程的情况下合入，但必须保持 Candidate 标记，不得宣传为真实项目已验证。维护者可要求进一步测试，不因候选规则缺失阻塞其他项目开发。

## English

Contributions to engine manifests, code/art/UI guidance, documentation and tests are welcome. Read the [Plugin Authoring Guide](docs/plugin-authoring-guide.md), [manifest example](examples/plugin-manifests/example-engine.json), and [manifest schema](docs/plugin-manifest.schema.json) before proposing a new engine. FrameForge is a nonblocking advisory tool; each project owns its standards.

1. Open an Issue with engine/version, proposal, official reference links, and real-project evidence when available. Never upload private code, secrets or unlicensed assets.
2. Work from a separate branch. Prefer declarative manifests over new core modules or executable plugins.
3. Mark guidance as **candidate** when based on documentation but not tested on a real project; only reproducible real-project evidence can support **validated**. Unit tests alone do not qualify.
4. Test positive, negative, missing and edge cases with `PYTHONPATH=src python -m unittest discover -s tests -q`.
5. Open a PR with sources, compatibility scope, limitations, tests and output. Maintainers decide whether to accept it.

Discovery never activates a plugin, selected plugins never modify project-owned standards, and warnings never block development. Existing project rules take precedence. Explain plugin ID/version, detection signals, compatibility, recommendation and likely false positives. Community guidance is not an engine-vendor certification.
