# Standards Authority Resolution V1 / 项目规范权威关系提示

## 中文

此功能属于 **只读、非阻塞的待确认项汇总**，不是规范审批器或文本冲突检测器。它读取 `standard_sources` 与 `standard_candidates`，返回 `standard_authority_review`，包含 Profile 已绑定引用、未被引用的候选路径、引用是否失效、以及建议项目负责人核对的动作。`potential_conflict=not_evaluated` 明确表明没有检查文档语义冲突；`content_conflicts_verified=false`；`authority=owner_confirmation_unverified`。未绑定时要求确认规范来源；已绑定也不推定已获批准。候选文件可能属于其他领域，`other_candidates` 是全项目尚未被任何 Profile 领域绑定的候选路径，而非已判定为同域冲突；不同领域已绑定文档不会互相列作候选。`candidate_relation=unclassified_project_wide` 使该边界可被 Host 直接识别。项目负责人自行管理正式规范和 Git 历史，FrameForge 不修改任何文件、不自动启用插件、不引入 Gate。

## English

This is a read-only, nonblocking review of existing profile bindings and filename-only candidates. `other_candidates` lists project-wide paths not already bound in any Profile domain. Documents bound to another domain are not alternatives; `candidate_relation=unclassified_project_wide` makes this explicit. These are not confirmed same-domain documents or semantic conflicts. `potential_conflict=not_evaluated`, `content_conflicts_verified=false`, and `owner_confirmation_unverified` prevent claims of verified approval or conflicts. No automatic change, agent, gate or extra service is created.
