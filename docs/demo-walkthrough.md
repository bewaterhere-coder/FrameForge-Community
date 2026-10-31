# FrameForge Demo Walkthrough / FrameForge 实际操作演示

## 中文

本演示使用仓库内的 Godot Sample Game，展示真实 CLI 安装、插件发现、项目 Profile 读取和只读建议结果。它不是 Godot 引擎运行演示，也不是完整架构合规认证。

### 运行演示

在仓库根目录执行：

```sh
python -m pip install .
bash scripts/demo.sh
```

### 演示流程

1. **发现能力**：列出 FrameForge 可用的声明式插件 Manifest。Candidate 会明确标记，不会因为被发现而自动启用。
2. **读取项目选择**：检查示例项目的 `.frameforge/profile.json`，确认项目显式选择 Godot 插件。
3. **读取项目规范引用**：展示项目自己的架构和资源规范路径。
4. **输出建议**：展示有限范围的静态建议、Warning 数量和 `blocking=false`。
5. **解释边界**：整个过程只读，不修改项目；不启动 Godot 编辑器、不构建或运行游戏，也不宣称完成运行时验证。

### 真实操作结果

本仓库的 CI 会检查示例项目 Profile、插件发现、规范引用及非阻塞结果。运行 `scripts/demo.sh` 可在本机重新生成当前结果；结果随仓库内容和 FrameForge 版本变化，不应把历史截图或输出当成永久保证。

## English

This walkthrough uses the repository's Godot Sample Game to demonstrate a real CLI installation, plugin discovery, project Profile loading and read-only advisory output. It is not a Godot engine runtime demo or a complete architecture compliance certification.

### Run the demo

From the repository root:

```sh
python -m pip install .
bash scripts/demo.sh
```

### What the demo shows

1. **Discover capabilities:** list declarative plugin manifests and label Candidates. Discovery never activates a plugin.
2. **Read project choices:** inspect the sample's `.frameforge/profile.json` and confirm its explicit Godot plugin selection.
3. **Read project-owned standards:** show the architecture and asset-pipeline references maintained by the sample project.
4. **Show advisory output:** report bounded static advice, warning count and `blocking=false`.
5. **State the limits:** the workflow is read-only. It does not launch the Godot editor, build or run the game, or claim runtime validation.

The CI checks Profile loading, plugin discovery, standards references and non-blocking output. Run `scripts/demo.sh` to regenerate current results. Output may change with repository content and FrameForge versions.
