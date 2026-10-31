# AI Host Adapter V1 / AI Host 只读适配接口

## 中文

FrameForge 不需要独立服务或绑定某个 AI 平台。已有且获得项目读取授权的 Python Host，可以在本地进程中调用 `frameforge.host_adapter`：

```python
from frameforge.host_adapter import (
    inspect_project, explain_warnings, verify_remediation,
    inspect_for_acceptance,
)

report = inspect_project("/authorized/project")
advice = explain_warnings("/authorized/project")
# AI 分析并经项目授权执行真实整改后
comparison = verify_remediation("/authorized/project", report["warnings"])
```

前三个函数均为只读操作：

- `inspect_project(project, plugin_dir=None, unity_external_evidence=None)`：返回完整项目检查结果。
- `explain_warnings(project, plugin_dir=None)`：返回当前 Warning 与整改上下文。
- `verify_remediation(project, previous_warnings, plugin_dir=None)`：重新检查并比较 Warning，返回 `resolved_warnings`、`remaining_warnings` 和 `new_warnings`。它是即时比较，不是正式验收或持久化回执。问题身份按 `code + message` 匹配，避免把同码但不同内容的问题误认为同一个问题。

### 基于 Git Commit 的验收辅助检查

`inspect_for_acceptance(project, expected_commit, plugin_dir=None, profile_source_commit=None)` 是额外的只读辅助接口，适用于需要把检查结果绑定到指定 Git 提交的 Host 工作流。

```python
from frameforge.host_adapter import inspect_for_acceptance

snapshot = inspect_for_acceptance(
    "/authorized/project",
    expected_commit="完整的 40 位 Git Commit SHA",
)
assert snapshot["repository_commit"] == "预期的提交 SHA"
assert snapshot["formal_acceptance"] is False
```

调用前必须满足：

1. 目标目录是 Git 仓库根目录。
2. 当前 HEAD 与 `expected_commit` 完全一致；必须提供完整 40 位 SHA，不能使用分支名或短 SHA。
3. 工作区干净，包括未跟踪文件。
4. 本机可以调用 Git。

如果传入 `profile_source_commit`，FrameForge 会从该明确指定的提交读取 `.frameforge/profile.json`；不会自动从最新 main 或其他分支继承 Profile。该参数同样要求完整 40 位 SHA。

此接口只返回绑定到提交的只读检查快照。结果中的 `compliance_verified` 和 `formal_acceptance` 不会被置为通过；`blocking` 保持为 `false`。它不批准需求、计划、代码或发布，不生成正式验收回执，也不替代项目自己的验收流程。

### 授权与边界

调用方必须具备项目读取权限，并遵守自身的目录授权。普通 Python Host API 不会自动提供文件系统沙箱；本地 MCP 的授权根目录限制属于 MCP 传输边界。FrameForge 不增加项目写入能力，不自动整改项目，也不执行外部插件代码。项目文件变更必须另行取得项目授权。

## English

FrameForge requires no dedicated service or binding to a specific AI platform. An existing Python host with project read access can call `frameforge.host_adapter` in its local process:

```python
from frameforge.host_adapter import (
    inspect_project, explain_warnings, verify_remediation,
    inspect_for_acceptance,
)

report = inspect_project("/authorized/project")
advice = explain_warnings("/authorized/project")
# After analysis and separately authorized project changes:
comparison = verify_remediation("/authorized/project", report["warnings"])
```

The first three functions are read-only:

- `inspect_project(project, plugin_dir=None, unity_external_evidence=None)`: returns the full project inspection.
- `explain_warnings(project, plugin_dir=None)`: returns current warnings and remediation context.
- `verify_remediation(project, previous_warnings, plugin_dir=None)`: performs a fresh inspection and compares warning identities, returning `resolved_warnings`, `remaining_warnings` and `new_warnings`. This is an in-memory comparison, not formal acceptance or a durable receipt. Issues are matched by `code + message`, so different issues sharing a code are not conflated.

### Commit-bound acceptance advisory

`inspect_for_acceptance(project, expected_commit, plugin_dir=None, profile_source_commit=None)` is an additional read-only helper for host workflows that need to bind an inspection snapshot to an exact Git commit.

```python
from frameforge.host_adapter import inspect_for_acceptance

snapshot = inspect_for_acceptance(
    "/authorized/project",
    expected_commit="the-full-40-character-Git-commit-SHA",
)
assert snapshot["repository_commit"] == "the-expected-commit-SHA"
assert snapshot["formal_acceptance"] is False
```

Requirements:

1. The target directory must be the Git repository root.
2. HEAD must exactly match `expected_commit`; provide a full 40-character SHA, not a branch name or abbreviated SHA.
3. The working tree must be clean, including untracked files.
4. Git must be available to the local process.

If `profile_source_commit` is supplied, FrameForge reads `.frameforge/profile.json` from that explicitly selected commit. It never silently inherits a Profile from the latest main branch or another ref. This parameter also requires a full 40-character SHA.

The function returns only a read-only inspection snapshot bound to the commit. It does not set `compliance_verified` or `formal_acceptance` to true; `blocking` remains `false`. It does not approve requirements, plans, code or releases, issue a formal acceptance receipt, or replace the project's own acceptance process.

### Authorization and boundaries

The caller must have project read access and follow its own path authorization. The ordinary Python Host API does not provide a filesystem sandbox; approved-root checks belong to the local MCP transport boundary. FrameForge adds no project-write capability, does not perform remediation, and never executes external plugin code. Project changes require separate authorization.
