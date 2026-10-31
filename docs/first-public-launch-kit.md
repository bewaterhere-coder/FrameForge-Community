# FrameForge First Public Launch Kit / FrameForge 首轮公开推广资料

## 中文

### 目标

帮助第一次接触 FrameForge 的游戏开发者在几分钟内理解产品、运行真实检查，并知道如何提供反馈。首轮推广以获得真实试用和高质量反馈为目标，不以 Stars 或下载量作为唯一指标。

### 产品定位

**Define your own game architecture. Let FrameForge help keep it consistent.**

FrameForge 是面向游戏开发的开源、项目级框架规范工具。项目自己定义架构与规范，按需选择插件；FrameForge 提供基于证据的检查与建议，不替项目决定架构，也不把 Warning 变成开发门禁。

核心事实：
- Core 负责稳定、通用的发现与检查语义。
- 项目拥有自己的 Profile 和规范来源。
- 插件发现不等于启用；Candidate 不等于 Validated。
- CLI、MCP 和 AI Host 共享一致的检查语义。
- 检查报告区分证据、建议、Warning 和未评估范围。
- 默认只读；静态检查不代表引擎运行时验证。

### 首发链接

- Website: https://bewaterhere-coder.github.io/FrameForge-Community/
- Source: https://github.com/bewaterhere-coder/FrameForge-Community
- Sample game: https://github.com/bewaterhere-coder/FrameForge-Community/tree/main/examples/sample-game-godot
- Demo walkthrough: https://github.com/bewaterhere-coder/FrameForge-Community/blob/main/docs/demo-walkthrough.md
- Discussions: https://github.com/bewaterhere-coder/FrameForge-Community/discussions

### Hacker News — Show HN 草稿

**Title:** Show HN: FrameForge – Define your own game architecture

Game projects build their own architecture rules, naming conventions, UI standards and asset pipelines. Those rules are often hard for developers—and AI coding tools—to discover and follow consistently.

I built FrameForge as an open-source, project-owned framework standards tool for game development.

Each project owns its Profile and standards. Teams choose only the plugins they need. FrameForge reports evidence and useful warnings without forcing one universal architecture or blocking development by default.

The same inspection semantics are available through CLI, local MCP and AI Host integrations. A minimal Godot sample project demonstrates how a game can define its own architecture and asset standards.

FrameForge is Apache-2.0. The Godot integration is currently a Candidate; the sample demonstrates static advisory behavior, not Godot runtime validation.

Website: https://bewaterhere-coder.github.io/FrameForge-Community/  
Source: https://github.com/bewaterhere-coder/FrameForge-Community

I'd value feedback from game developers: how do you define and keep project-specific architecture standards consistent, especially when using AI coding tools?

### Reddit — r/gamedev 草稿

**Title:** I built an open-source tool for project-owned game architecture standards

I have worked on game projects where architecture, UI rules, asset pipelines and naming conventions are documented in different places. As teams grow—and especially when AI coding tools join the workflow—those rules can become difficult to discover and keep consistent.

FrameForge is my attempt to make those standards explicit at the project level.

It does not prescribe one architecture for every game. Each project owns its Profile and standards, and chooses which engine or specialist plugins to use. Checks are advisory and evidence-led; warnings do not become mandatory gates.

There is a small Godot sample game in the repository to show the workflow. The Godot plugin is marked Candidate, and the demo is a static inspection—not an engine runtime validation.

I'd appreciate feedback on whether this solves a real problem in your game projects, and what would make the first-use experience clearer.

Website: https://bewaterhere-coder.github.io/FrameForge-Community/  
GitHub: https://github.com/bewaterhere-coder/FrameForge-Community

### Reddit — r/godot 草稿

**Title:** A tiny Godot sample project for trying FrameForge's project-owned standards

I added a small Godot 4 sample game to FrameForge Community. The point is not to introduce another Godot framework; it is to demonstrate how a game project can own its architecture and asset standards in a small Profile, then inspect those choices with FrameForge.

The Godot integration is currently Candidate. FrameForge discovers the plugin manifest and reads the sample's selected plugin and standards references. It does not run the Godot editor or claim engine/runtime validation.

I'd welcome feedback from Godot developers on the Profile, standards layout and first-use instructions.

Sample: https://github.com/bewaterhere-coder/FrameForge-Community/tree/main/examples/sample-game-godot  
Walkthrough: https://github.com/bewaterhere-coder/FrameForge-Community/blob/main/docs/demo-walkthrough.md

### 90 秒真实终端 Demo 分镜

| 时间 | 画面与操作 | 旁白重点 |
|---|---|---|
| 0–10s | 展示 Sample Game 目录与 Profile | 每个游戏项目拥有自己的规范 |
| 10–25s | 执行 `python -m pip install .` | 安装来自公开仓库的 FrameForge |
| 25–40s | 执行 `python -m frameforge.cli --plugins` | 发现插件；Candidate 不会自动启用 |
| 40–60s | 执行 `bash scripts/demo.sh` | 检查项目选择和规范引用 |
| 60–75s | 展示 Advisory、Warnings、Blocking | 结果有证据边界，默认不阻塞开发 |
| 75–90s | 展示 CLI / MCP 文档和 GitHub | 邀请开发者试用、提问和贡献 |

录制要求：
- 直接录制真实终端，不合成虚假的运行输出。
- 录制前从干净 checkout 安装，保留完整命令和退出码。
- 隐去个人路径、用户名、Token、私有仓库及其他环境信息。
- 屏幕上清楚标记这是静态检查，不是 Godot 引擎运行验证。
- 发布前重新运行演示脚本，不能沿用过期输出冒充当前结果。

### Release 准备清单（不代表已发布）

- [ ] 核验 main HEAD、版本号和工作区状态。
- [ ] 核验 README、安装命令、依赖和支持的 Python 版本。
- [ ] 从干净环境安装并运行 CLI。
- [ ] 运行完整测试套件并记录准确结果。
- [ ] 核验示例项目和插件状态描述。
- [ ] 核验 LICENSE、NOTICE（如适用）、第三方资源许可。
- [ ] 编写 Release notes，列明功能、限制和已知问题。
- [ ] 由维护者明确批准后再创建 Git tag / GitHub Release。

不得将 CI PASS 当作发布批准；本文件本身不会创建 Release、Tag 或部署。

### 推广执行原则

1. 先在一个相关社区发布一条高质量帖子，避免多社区重复刷屏。
2. 公开说明这是维护者自己的开源项目，不伪装成第三方推荐。
3. 认真回应技术问题，记录首次安装失败和实际使用障碍。
4. 第一轮重点验证：开发者是否理解定位、是否能成功运行、是否愿意在自己的项目试用。
5. 不购买 Stars、不制造虚假用户或测试数据，不宣称尚未验证的引擎支持。

---

## English

### Goal

Help a game developer who has never seen FrameForge understand the project, run a real inspection within minutes, and know how to give feedback. The first launch should optimize for genuine trials and useful feedback—not stars or downloads alone.

### Positioning

**Define your own game architecture. Let FrameForge help keep it consistent.**

FrameForge is an open-source, project-owned framework standards tool for game development. Projects define their own architecture and standards and opt into the plugins they need. FrameForge provides evidence-led inspection and advice; it does not prescribe a universal architecture or turn warnings into development gates.

Key facts:
- Core owns stable, shared discovery and inspection semantics.
- Each project owns its Profile and standards sources.
- Plugin discovery is not activation; Candidate is not Validated.
- CLI, MCP and AI Host share consistent inspection semantics.
- Reports distinguish evidence, advice, warnings and unevaluated scope.
- Inspection is read-only by default; static checks are not engine runtime validation.

### Launch links

- Website: https://bewaterhere-coder.github.io/FrameForge-Community/
- Source: https://github.com/bewaterhere-coder/FrameForge-Community
- Sample game: https://github.com/bewaterhere-coder/FrameForge-Community/tree/main/examples/sample-game-godot
- Demo walkthrough: https://github.com/bewaterhere-coder/FrameForge-Community/blob/main/docs/demo-walkthrough.md
- Discussions: https://github.com/bewaterhere-coder/FrameForge-Community/discussions

### Hacker News — Show HN draft

**Title:** Show HN: FrameForge – Define your own game architecture

Game projects build their own architecture rules, naming conventions, UI standards and asset pipelines. Those rules are often hard for developers—and AI coding tools—to discover and follow consistently.

I built FrameForge as an open-source, project-owned framework standards tool for game development.

Each project owns its Profile and standards. Teams choose only the plugins they need. FrameForge reports evidence and useful warnings without forcing one universal architecture or blocking development by default.

The same inspection semantics are available through CLI, local MCP and AI Host integrations. A minimal Godot sample project demonstrates how a game can define its own architecture and asset standards.

FrameForge is Apache-2.0. The Godot integration is currently a Candidate; the sample demonstrates static advisory behavior, not Godot runtime validation.

Website: https://bewaterhere-coder.github.io/FrameForge-Community/  
Source: https://github.com/bewaterhere-coder/FrameForge-Community

I'd value feedback from game developers: how do you define and keep project-specific architecture standards consistent, especially when using AI coding tools?

### Reddit — r/gamedev draft

**Title:** I built an open-source tool for project-owned game architecture standards

I have worked on game projects where architecture, UI rules, asset pipelines and naming conventions are documented in different places. As teams grow—and especially when AI coding tools join the workflow—those rules can become difficult to discover and keep consistent.

FrameForge is my attempt to make those standards explicit at the project level.

It does not prescribe one architecture for every game. Each project owns its Profile and standards, and chooses which engine or specialist plugins to use. Checks are advisory and evidence-led; warnings do not become mandatory gates.

There is a small Godot sample game in the repository to show the workflow. The Godot plugin is marked Candidate, and the demo is a static inspection—not an engine runtime validation.

I'd appreciate feedback on whether this solves a real problem in your game projects, and what would make the first-use experience clearer.

Website: https://bewaterhere-coder.github.io/FrameForge-Community/  
GitHub: https://github.com/bewaterhere-coder/FrameForge-Community

### Reddit — r/godot draft

**Title:** A tiny Godot sample project for trying FrameForge's project-owned standards

I added a small Godot 4 sample game to FrameForge Community. The point is not to introduce another Godot framework; it is to demonstrate how a game project can own its architecture and asset standards in a small Profile, then inspect those choices with FrameForge.

The Godot integration is currently Candidate. FrameForge discovers the plugin manifest and reads the sample's selected plugin and standards references. It does not run the Godot editor or claim engine/runtime validation.

I'd welcome feedback from Godot developers on the Profile, standards layout and first-use instructions.

Sample: https://github.com/bewaterhere-coder/FrameForge-Community/tree/main/examples/sample-game-godot  
Walkthrough: https://github.com/bewaterhere-coder/FrameForge-Community/blob/main/docs/demo-walkthrough.md

### 90-second real terminal demo storyboard

| Time | Screen and action | Key message |
|---|---|---|
| 0–10s | Show Sample Game directory and Profile | Each game project owns its standards |
| 10–25s | Run `python -m pip install .` | Install FrameForge from the public repository |
| 25–40s | Run `python -m frameforge.cli --plugins` | Discover plugins; Candidate is not auto-enabled |
| 40–60s | Run `bash scripts/demo.sh` | Inspect project choices and standards references |
| 60–75s | Show Advisory, Warnings and Blocking | Evidence has clear limits; development is not blocked by default |
| 75–90s | Show CLI / MCP docs and GitHub | Invite developers to try, discuss and contribute |

Recording requirements:
- Capture a real terminal; do not fabricate command output.
- Start from a clean checkout, install, and retain commands and exit codes.
- Hide personal paths, usernames, tokens, private repositories and unrelated environment details.
- Clearly label the demo as static inspection, not Godot engine runtime validation.
- Re-run the demo script before recording; never present stale output as current.

### Release readiness checklist (not a release)

- [ ] Verify main HEAD, version and working tree.
- [ ] Verify README, install commands, dependencies and supported Python versions.
- [ ] Install from a clean environment and run the CLI.
- [ ] Run the full test suite and record exact results.
- [ ] Verify sample project and plugin status claims.
- [ ] Verify LICENSE, NOTICE (if applicable) and third-party asset licenses.
- [ ] Write release notes with features, limitations and known issues.
- [ ] Create a Git tag / GitHub Release only after explicit maintainer approval.

CI passing is not release approval. This document does not create a Release, Tag or deployment.

### Promotion principles

1. Start with one relevant community and one high-quality post; avoid cross-post spam.
2. Disclose that this is the maintainer's own open-source project.
3. Respond to technical questions and record onboarding failures.
4. First validate whether developers understand the positioning, can run the tool and want to try it in their own projects.
5. Do not buy stars, fabricate users or test data, or claim engine support that has not been validated.
