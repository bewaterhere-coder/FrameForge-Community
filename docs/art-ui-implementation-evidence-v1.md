# Art/UI Implementation Evidence V1

## 中文
在项目显式选择 Art/UI 插件并声明 `art_ui_checks` 后，可在项目自己的 `.frameforge/profile.json` 中额外声明 `art_ui_implementation_checks`，将每项只读源码文本信号绑定到既有规范条款 ID。例如：

```json
"art_ui_implementation_checks": [
  {"check_id":"ui-asset-manifest","path":"Assets/Settings/UI/CommonAssets.asset","contains":"m_Name: CommonAssets"}
]
```

每项最多读取 250KB 文件，只查精确文本子串；不解析 Unity 序列化语义、不运行 Unity、不证明规范符合。输出 `signal_found`、`signal_not_found`、`source_unavailable` 或 `reference_unverified`，附行号及证据置信度。配置无效只产生 Warning，不使其他插件失效；越界路径和符号链接拒绝。未显式选择 Art/UI 或未声明检查时不执行。所有检查均不阻断开发。

## English
Optional `art_ui_implementation_checks` bind a bounded literal file signal to a declared Art/UI standard-clause ID. Only selected projects run these checks. The scanner reads at most 250KB per source and reports line evidence; it does not parse Unity YAML semantics, render UI, certify visual quality, or modify project resources. A missing signal is review evidence, not a verified defect. Invalid optional configuration warns without disabling other plugins. Path traversal and symlinks are not accepted; all results are non-blocking.

Implementation signal sources cannot be the same project-owned Art/UI standard file: matching a rule against itself is circular evidence, not implementation verification.
