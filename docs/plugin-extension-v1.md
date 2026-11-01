# External Manifest Extension V1 / 外部 Manifest 扩展

FrameForge can read additional declarative JSON plugin manifests from an explicitly supplied directory:

```sh
frameforge /path/to/project --plugin-dir /path/to/manifest-directory
frameforge --plugins --plugin-dir /path/to/manifest-directory
```

The directory is never searched or loaded implicitly. The packaged plugin catalog remains available. External plugin IDs cannot override packaged plugin IDs. Invalid manifests fail the explicit catalog request; project files are never modified. This is **metadata-only** and **does not run arbitrary plugin code**.

Manifest example:

```json
{"id":"custom-engine","version":"1.0.0","domain":"code","standards":["architecture"],"detection":[["custom.project"]]}
```

Discovery suggests a plugin but does not activate it. A project must explicitly select an ID and version in its Framework Profile; that selection activates professional guidance independently of discovery markers. Missing standards produce advisory warnings, not development gates.

中文：可以通过 `--plugin-dir` 明确指定外部插件描述文件目录。默认不扫描外部目录，也不执行插件代码。插件 ID 不允许覆盖内置项；发现技术栈只作推荐，专业指导由项目 Profile 显式选择启用，且不依赖自动发现标记。规范缺失为 Warning，不阻断开发。
