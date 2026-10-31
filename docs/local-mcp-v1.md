# FrameForge Local MCP V1

## 中文

FrameForge 提供 CLI、本地 stdio MCP 和 Python API。它们共用 `frameforge.core` 的检查逻辑；Python Host API 与 MCP 还共用 `frameforge.host_adapter`。不同入口暴露的操作范围不同：

| 入口 | 操作 | 错误表现 |
|---|---|---|
| CLI | `frameforge PROJECT`、`frameforge --plugins` | 参数解析错误由 argparse 输出并以退出码 2 结束；检查中的 `ValueError`/`OSError` 输出到 stderr，退出码 2 |
| Python API | `inspect_project`、`explain_warnings`、`verify_remediation`、`inspect_for_acceptance` | 保留 Python 异常类型；调用方负责处理 |
| MCP | `list_plugins`、`inspect_project`、`explain_warnings`、`verify_remediation`、`inspect_for_acceptance` | 项目路径授权失败在工具调用前抛出 `ValueError`；工具执行异常由 MCP SDK 转成协议工具错误，客户端应读取错误信息，不应把失败解释为“无 Warning”或空结果 |

CLI 与 MCP 不承诺字节级相同的错误文本或退出码；一致性要求是共用 Core 结果与底层异常原因，不隐藏失败、不把失败伪装成成功结果。MCP 的授权根目录校验属于传输边界，不由 CLI 或普通 Python API 自动执行。

安装：`python -m pip install -e '.[mcp]'`。在支持本地 stdio MCP 的 AI 客户端中注册：

```json
{
  "mcpServers": {
    "frameforge": {
      "command": "frameforge-mcp",
      "env": { "FRAMEFORGE_MCP_PROJECT_ROOTS": "/absolute/approved/project/root" }
    }
  }
}
```

也可运行 `python -m frameforge.mcp_server`。Python Host API 可从 `frameforge.host_adapter` 导入上述四个检查函数。CLI 保持 `frameforge /path/to/project` 与 `frameforge --plugins`；CLI 不提供 commit-bound `inspect_for_acceptance` 操作。

MCP 进程继承当前本地账号的文件读取权限，且必须设置 `FRAMEFORGE_MCP_PROJECT_ROOTS`（使用操作系统路径分隔符分隔多个授权根目录）。项目路径和外部插件目录都必须位于授权根目录内，解析符号链接后仍要保持在授权范围内。只应在可信机器上运行；这不是 OS 沙箱，也不应暴露到公网。外部插件目录只读取 JSON Manifest，不执行插件代码。检查不会写入项目，不会自动选择插件、批准标准或产生正式验收回执。Warning 始终非阻塞。客户端是否能安装/连接本地 MCP 取决于该客户端环境；连接成功须独立测试，不能从服务器实现推定。

## English

FrameForge provides a CLI, a local stdio MCP server and a Python API. They share the `frameforge.core` inspection logic; the Python Host API and MCP also share `frameforge.host_adapter`. The entrypoints intentionally expose different operation sets:

| Entry point | Operations | Error behavior |
|---|---|---|
| CLI | `frameforge PROJECT`, `frameforge --plugins` | argparse reports argument errors and exits with code 2; inspection `ValueError`/`OSError` is printed to stderr with exit code 2 |
| Python API | `inspect_project`, `explain_warnings`, `verify_remediation`, `inspect_for_acceptance` | Preserves Python exception types; callers handle them |
| MCP | `list_plugins`, `inspect_project`, `explain_warnings`, `verify_remediation`, `inspect_for_acceptance` | Project-root authorization fails with `ValueError` before inspection; execution exceptions are mapped by the MCP SDK to protocol tool errors. Clients must surface the error and must not interpret failure as “no warnings” or an empty successful result |

CLI and MCP do not promise byte-identical error text or exit codes. Consistency means they share Core results and underlying failure causes, do not hide failures, and never turn errors into successful empty results. MCP root authorization is a transport boundary; it is not automatically applied by the CLI or ordinary in-process Python API.

Install with `python -m pip install -e '.[mcp]'`, then register `frameforge-mcp` as a local stdio server:

```json
{
  "mcpServers": {
    "frameforge": {
      "command": "frameforge-mcp",
      "env": { "FRAMEFORGE_MCP_PROJECT_ROOTS": "/absolute/approved/project/root" }
    }
  }
}
```

Alternatively run `python -m frameforge.mcp_server`. The Python Host API functions are available from `frameforge.host_adapter`. The CLI remains `frameforge /path/to/project` and `frameforge --plugins`; it does not expose the commit-bound `inspect_for_acceptance` operation.

The MCP process inherits the local account's file-read permissions and must set `FRAMEFORGE_MCP_PROJECT_ROOTS` (separate multiple roots with the OS path separator). Project and optional plugin paths must resolve inside those roots, including after symlink resolution. Run it only in a trusted local environment; this is not an OS sandbox and must not be exposed publicly. External plugin directories are read as JSON manifests only; plugin code is never executed. Inspection does not write project files, activate plugins, approve standards, create gates or issue formal acceptance decisions. Warnings remain non-blocking. Client installation and connectivity must be tested on each host; server implementation alone does not prove connectivity.
