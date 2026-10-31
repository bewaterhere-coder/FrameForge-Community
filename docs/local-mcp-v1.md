# FrameForge Local MCP V1

## 中文

FrameForge 同时提供 CLI、本地 MCP 和 Python API。三者共用 `frameforge.core` 与 `host_adapter`，不会出现两套独立规范引擎。

安装：`python -m pip install -e '.[mcp]'`。在支持本地 stdio MCP 的 AI 客户端中配置：

```json
{
  "mcpServers": {
    "frameforge": {
      "command": "frameforge-mcp",
      "env": {"FRAMEFORGE_MCP_PROJECT_ROOTS": "/absolute/approved/project/root"}
    }
  }
}
```

也可运行 `python -m frameforge.mcp_server`。MCP 工具有 `list_plugins`、`inspect_project`、`explain_warnings`、`verify_remediation`；项目路径由客户端传入。CLI 仍为 `frameforge /path/to/project` 与 `frameforge --plugins`。

MCP 进程继承当前本地账号的文件读取权限，且必须设置 `FRAMEFORGE_MCP_PROJECT_ROOTS`（使用操作系统路径分隔符分隔多个授权根目录）。项目路径和外部插件目录都必须位于授权根目录内，解析符号链接后仍要保持在授权范围内。只应在可信机器上运行；这不是 OS 沙箱，也不应暴露到公网。外部插件目录只读取 JSON Manifest，不执行插件代码。检查不会写入项目，不会自动选择插件、批准标准或产生正式验收回执。Warning 始终非阻塞。客户端是否能安装/连接本地 MCP 取决于该客户端环境；连接成功须独立测试，不能从服务器实现推定。

## English

The CLI, local stdio MCP server and Python API share the same core and host adapter. Install with `python -m pip install -e '.[mcp]'`, then register the command `frameforge-mcp` as a local stdio MCP server in your client. Alternatively run `python -m frameforge.mcp_server`. Tools: `list_plugins`, `inspect_project`, `explain_warnings`, `verify_remediation`.

Set `FRAMEFORGE_MCP_PROJECT_ROOTS` to explicit approved root directories (OS path separator for multiple roots). The project and optional plugin directory must resolve inside these roots, including after symlink resolution. Project paths are supplied by the caller. The server inherits the local user's read permissions and must only run in a trusted local environment. It does not edit files, activate plugins, approve standards, create gates or issue formal acceptance decisions. Connectivity must be verified separately on each host.
