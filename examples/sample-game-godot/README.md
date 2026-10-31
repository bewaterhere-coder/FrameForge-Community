# FrameForge Sample Game — Godot 4

## 中文

这是一个最小、可运行的 Godot 4 俯视角收集游戏，用来展示 FrameForge 如何读取一个**项目自己拥有的架构规范**。

### 运行游戏

1. 安装 Godot 4.3 或兼容的 Godot 4.x 版本。
2. 在 Godot Project Manager 中导入本目录的 `project.godot`。
3. 运行主场景。
4. 使用 WASD 或方向键移动角色，收集全部 3 颗水晶。

游戏使用 GDScript 和代码绘制的简单图形，不依赖外部素材包。

### 使用 FrameForge 检查

在仓库根目录安装 FrameForge：

```sh
python -m pip install .
frameforge examples/sample-game-godot
```

示例项目明确选择 Godot 插件，并绑定自己的架构和资源规范：

- `.frameforge/profile.json`：项目自己维护的插件选择与规范路径。
- `docs/architecture.md`：本示例的代码与场景边界。
- `docs/asset-pipeline.md`：本示例的素材规则。

Godot 插件目前属于 **Candidate**。FrameForge 的检查是只读建议，不代表 Godot 编辑器、构建或运行时验证，也不会修改游戏项目。CI 会验证 FrameForge 能发现该项目、读取 Profile 并返回非阻塞结果；不会把这项检查描述为 Godot 游戏运行测试。

## English

A tiny, runnable top-down collection game built with Godot 4. It demonstrates how a game project owns its architecture standards and explicitly selects FrameForge guidance.

### Run the game

1. Install Godot 4.3 or a compatible Godot 4.x release.
2. Import this folder's `project.godot` in Godot Project Manager.
3. Run the main scene.
4. Move with WASD or the arrow keys and collect all three crystals.

The game uses GDScript and simple code-drawn shapes. No external asset pack is required.

### Inspect with FrameForge

From the repository root:

```sh
python -m pip install .
frameforge examples/sample-game-godot
```

The project explicitly selects the Godot plugin and binds its own standards in `.frameforge/profile.json`. Read `docs/architecture.md` and `docs/asset-pipeline.md` for the project-owned rules.

The Godot plugin is still **Candidate**. FrameForge performs read-only advisory inspection; it does not run the Godot editor, build or game. CI checks FrameForge discovery, Profile loading and non-blocking output only—not Godot runtime behavior.
