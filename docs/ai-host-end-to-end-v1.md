# AI Host End-to-End Workflow / AI Host 端到端使用流程

## 中文

**前提：** AI Host 已获得目标项目的读取授权，并具备可用的 FrameForge Python 环境或本地连接。FrameForge 不提供自动审批或项目写入服务。

**示例请求：**“检查这个多模块项目的框架规范，列出已绑定的文档、候选规范、需要确认的事项，以及尚不能判断的条款。”

Host 可调用只读 API：

```python
from frameforge.host_adapter import inspect_project, explain_warnings
report = inspect_project('/authorized/project')
warnings = explain_warnings('/authorized/project')
```

解释结果时，应区分 `suggested_plugins`（候选）与 `selected_plugins`（明确选择），区分 `standard_sources`（已绑定引用）与 `standard_candidates`（待确认候选）。`owner_approved=unverified` 不代表审批通过或失败；有限文件名发现不能证明规范权威；`potential_conflict=not_evaluated` 不能证明存在实际冲突；`clause_coverage=[]` 表示未配置检查条款；源码信号和空 Warning 列表均不能证明完整合规。应提供来源文件供项目负责人确认。

用户要求整改时，Host 必须先检查项目资料和权限。FrameForge 不创建占位规范，也不自动修改项目。只有获得独立授权后，Host 才能执行项目变更；之后可调用 `verify_remediation(project, previous_warnings)` 重新扫描。复查结果不是正式验收。

**证据边界：** API 测试和隔离样例只能验证接口行为，不能证明任意项目的规范合规，也不替代真实引擎编译、运行时或集成测试。

## English

An AI host with explicit project read access and an available FrameForge Python environment can call the in-process adapter. FrameForge does not provide automatic approval or project-write services.

The host should distinguish suggested plugins from selected plugins, bound standard references from discovered candidates, and observed signals from verified compliance. `owner_approved=unverified` is not an approval decision; filename discovery does not prove authority; `potential_conflict=not_evaluated` does not establish a conflict; and empty clause coverage or warnings do not prove complete compliance. Present source files for project-owner review.

Remediation requires separate project authorization. FrameForge does not create placeholder standards or modify project files. After an authorized change, `verify_remediation(project, previous_warnings)` can perform a fresh read-only comparison, but it is not formal acceptance. API tests and fixtures do not replace real engine builds, runtime tests or project-specific integration validation.
