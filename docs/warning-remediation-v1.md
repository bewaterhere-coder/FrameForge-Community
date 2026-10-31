# Warning Remediation V1 / Warning 整改建议协议

## 中文

FrameForge 只输出可供 AI Host 使用的整改建议，不执行整改。每个 `warnings[]` 保留原有 `code`、`message`，并增加 `remediation`：

- `proposed_action`：可供 AI Host 解释的动作标识，不是自动执行命令。
- `approval`：正式项目绑定或规范修改需要项目所有者确认。
- `verification`：重新执行 FrameForge 时用于判断 Warning 是否消失的条件说明。
- `status: needs_review`：本次扫描仍然存在该 Warning；没有持久化的“已处理”标签。
- `auto_apply: false`：FrameForge 不修改 Profile、规范或源代码。

**完整闭环**：AI 读取 Warning → 检查正式项目证据 → 草拟最小整改 → 按项目权限取得必要批准 → 由授权开发工具执行修改 → 再次调用 FrameForge → 对比 Warning 是否消失。出现 `warnings=[]` 仅说明当前检查没有触发已定义 Warning，不证明架构合规。

`PROFILE_MISSING` 不能通过偷偷创建空 Profile 消除；`STANDARD_MISSING` 不能通过编造规范正文消除；`PLUGIN_VERSION_MISMATCH` 必须先确认版本兼容。误报应作为规则修复问题处理，不能隐藏 Warning。未来如需记录风险接受，应与扫描结果分开管理，绝不影响 `blocking=false`。

## English

FrameForge outputs remediation advice for an external AI host but never applies changes. Existing warning fields `code` and `message` remain stable. The optional `remediation` object provides a proposed action identifier, project-owner approval requirement, recheck condition, `status: needs_review`, and `auto_apply: false`.

An AI host should investigate project-owned evidence, propose a minimal correction, obtain required authorization, apply it through an authorized development tool, and rerun FrameForge. A warning disappears only when its detection condition no longer holds. Empty warnings do not establish architecture correctness. Missing profiles and standards must not be silently fabricated; version changes require compatibility review. There is no AI runtime, additional gate, or project mutation inside FrameForge.

### 专项评审边界 / Review limitation

静态检查目前只能确认规范文件存在及路径安全，**不能判断正文是否真实、是否正式批准或是否为空洞占位内容**。即使有人创建占位文件让 `STANDARD_UNAVAILABLE` 消失，也不能据此宣称已完成有效整改。AI Host 必须复核规范来源及项目所有者批准；其他未解决 Warning 仍需保留。

The checker verifies reference presence and path safety, not document authority or substantive quality. A placeholder can clear a file-presence warning without resolving the actual governance gap; an AI host must inspect provenance and obtain project-owner confirmation. Other warnings stay visible until independently resolved.
