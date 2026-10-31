# AI Host Adapter V1 / AI Host 只读适配接口

## 中文

FrameForge 不需要独立服务或绑定某个 AI 平台。任何已授权的 Python Host 都可从项目目录运行 Python，并直接调用三个函数：

```python
from frameforge.host_adapter import inspect_project, explain_warnings, verify_remediation
report = inspect_project("/authorized/project")
advice = explain_warnings("/authorized/project")
# AI 分析并经项目授权执行真实整改后
comparison = verify_remediation("/authorized/project", report["warnings"])
```

三者均为**只读函数**：第一项返回完整现有扫描结构；第二项返回 Warning 与整改建议；第三项对比上一份 Warning 和当前重新扫描结果，返回 `resolved_codes`、`remaining_warnings`、`new_codes`。该对比不是正式验收结论。以 Warning 的 `code + message` 组合识别同一问题；相同错误码但不同对象不会被误判为同一问题，新增 `resolved_warnings` 和 `new_warnings` 供 Host 精确解释。调用方必须有项目读取权限，遵守自身项目目录授权；FrameForge 不增加文件系统授权或写入能力。

Host 可直接调用这些函数，不要求手动复制 JSON，也不需要安装新服务。该接口供已有授权 Host 在本地进程中调用。整改项目文件需要独立授权，不能只为消除 Warning 编造规范或更改正式真源。

## English

The in-process adapter provides `inspect_project`, `explain_warnings`, and `verify_remediation` to an existing authorized Python host. All calls are read-only, and the verification output compares code-and-message issue identities after a fresh scan without claiming formal acceptance. No server, AI runtime, background process, automatic mutation or new development gate is introduced. The adapter is intended for invocation by an existing authorized local host.
