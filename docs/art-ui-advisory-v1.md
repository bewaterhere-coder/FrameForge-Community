# Art/UI Advisory V1

## 中文

Art/UI 是独立的声明式可选插件；检测 UI 资产目录只表示**推荐**，不会自动选择插件、执行代码或修改资源。项目需在自己的 `.frameforge/profile.json` 里选择 `art-ui@1.0.0`，并以 `standards["art-ui"]` 指向项目自己维护的正式美术或 UI 规范文件。

首次规则覆盖三类**可复核线索**：公共 UI 资源目录、布局与安全区测试候选位置、资源导入与生命周期管理目录。输出是具体路径、审查建议及非阻塞状态；目录存在**不代表**符合规范，目录未匹配也**不代表**真实缺失。项目的竖屏比例、安全区、像素细节、触控尺寸等标准由项目自己的规范定义，FrameForge 不硬编码任何单一项目的参数，也不解析截图或证明视觉质量。目录证据必须位于项目根目录内，不接受指向外部的符号链接。

**脱敏示例边界：** 可在公开示例仓库中使用虚构目录结构演示扫描，例如 `Assets/UI/Common`、`Assets/Prefabs/UI/Common`、`Tests/PlayMode` 和 `Addressables`。这些是示例路径，不代表任何真实项目扫描结果，也不构成规范要求。

## English

Art/UI is an optional declarative plugin. Detecting UI asset paths only suggests its relevance; it never selects or executes the plugin or mutates resources. Projects explicitly select `art-ui@1.0.0` in their own `.frameforge/profile.json` and bind `standards["art-ui"]` to a project-owned authoritative standard.

V1 supplies bounded evidence paths and non-blocking review advice for shared UI assets, layout/safe-area testing and asset delivery/lifecycle. Presence is not compliance; unmatched locations are not confirmed gaps. Project-specific aspect ratios, pixel style, safe areas and touch targets remain defined by the project rather than the FrameForge core. Screenshots and visual quality are not evaluated. External symlink targets are not evidence.

Any sample paths are fictional fixtures, not observations from a customer or private project.
