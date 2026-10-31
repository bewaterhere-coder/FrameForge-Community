# Project Standard Clause Evidence V1 / 项目条款证据上下文

## 中文

本次仅扩展原 `clause_coverage`，不创建新的合规判定器。每条项目显式配置的 `check_clauses` 增加 `clause_evidence.status/line`（正式引用文档中的唯一文本命中）、`code_evidence.status/locations`（已选择插件与声明式规则的有限源码信号）及 `not_evaluated_reason`（规则未运行、条款不能唯一定位或代码信号不足）。`status` 与 `compliance=unverified` 保持原语义，文本匹配无法证明执行路径、规范符合或项目负责人已批准。空条款仍返回空覆盖；无需额外进程或 Gate。

真实项目使用应先由维护者核对条款正文、精确源文件及插件选择，然后明确配置规则；不从任何单个项目推断通用规范。

## English

Add evidence context to existing explicitly configured clause coverage: unique clause location, bounded code tokens, and a reason when the comparison cannot be evaluated. Preserve `compliance=unverified`, source ownership, and nonblocking behavior. This is not semantic code correctness or automated standards approval.
