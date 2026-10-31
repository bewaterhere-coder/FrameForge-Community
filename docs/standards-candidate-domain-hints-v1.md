# Standards Candidate Domain Hints V1 / 候选规范领域提示

## 中文

FrameForge 对已发现的候选规范文件名输出 `domain_hints` 与 `domain_hint_basis=filename_tokens_only`，帮助 AI Host 初步区分架构、Art/UI、资源与测试规范。候选可以匹配多个领域，也可以不匹配任何领域。`standard_authority_review.items[].domain_hint_matches` 只是从既有未绑定候选中筛出带对应领域提示的路径；原 `other_candidates` 完整保留，不因提示而丢弃资料。提示不是规范权威、同领域确认或内容冲突判断，不改变 `owner_confirmation_unverified`、`potential_conflict=not_evaluated` 和 `blocking=false`。不读取候选文件正文，不自动绑定、不修改项目。

## English

Candidate domain hints are filename-token heuristics only. They may be absent or multi-valued. `domain_hint_matches` is a convenience subset of existing unbound candidates; `other_candidates` remains complete. Hints do not prove owner approval, a same-domain relationship, a semantic conflict, or compliance. All behavior remains read-only and nonblocking.
