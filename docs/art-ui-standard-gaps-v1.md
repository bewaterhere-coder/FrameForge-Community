# Art/UI project-owned standard gap references V1

## 中文
项目可在 Profile 中按需声明 `art_ui_checks`，每项指定唯一 ID、正式规范中必须能够定位的原文子句 `clause`、可选证据路径 `evidence_paths`。仅当显式选择 art-ui 插件、并且项目识别到该插件时执行。示例：

```json
"art_ui_checks": [
  {
    "id": "reuse-common",
    "clause": "Public UI assets",
    "evidence_paths": ["Assets/Art/UI/Common"]
  }
]
```

状态 `clause_not_found`、`clause_ambiguous`、`standard_unavailable`、`evidence_not_found` 和 `review_required` 都是只读的待核对信息，不是违规证明或阻塞 Gate。完整的视觉符合性必须依据实际截图、Unity 运行时和项目正式规范进行独立验收。未填写 `art_ui_checks` 时不推断任何具体规范缺失。最多 32 项，每项最多 16 个证据路径；拒绝路径穿越与越界符号链接。

## English
Projects may opt in to `art_ui_checks` in their Profile. Each check names a stable ID, an exact clause substring in a project-owned Art/UI standard, and optional evidence paths. Checks only run when Art/UI is explicitly selected and discovered. All statuses are non-blocking review evidence, not visual compliance results. No checks means no project-specific missing-clause assertions. The bounded declaration rejects path escapes, and externally resolved symlinks are not accepted as evidence.
