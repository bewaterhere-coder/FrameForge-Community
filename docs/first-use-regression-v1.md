# First-use AI Host regression / AI Host 首次使用回归

## 中文

`tests/test_first_use_journey.py` 使用一个全新的临时 Unity 项目验证首次检查、插件建议、非阻塞 Warning、只读 Host 调用、**模拟项目负责人独立建立 Profile 和规范文档**、规范绑定与回读、Warning 消除及正式验收边界。重复检查不得自动生成或改写 Profile。

运行：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_first_use_journey -v` 或运行全量 `python3 -m unittest discover -s tests -q`。

本测试仅验证 API 及数据契约，不验证真实 AI Host UI 对话、任意连接平台授权、Unity 编辑器运行或正式工程规范合规性。文档、Profile 的测试写入只发生在隔离临时项目内，不由 FrameForge 自动执行。

## English

The first-use regression uses a temporary Unity project to test discovery, nonblocking warnings, read-only Host calls, a separate simulated project-owner configuration step, binding and fresh warning recheck. Host calls must never write a Profile or standards. This is an API contract test, not a user-interface, Unity runtime, owner-approval, or formal compliance test.
