# Unity asmdef reference context V1 / Unity 程序集引用上下文

## 中文

增加 `unresolved_reference_context`，逐项区分 GUID 引用和按名称引用，并仅在 `Unity.*` 与 `com.unity.*` 命名空间一致、且程序集名与包 ID 末段精确匹配时提供 `declared_package_hints`，例如 `Unity.Addressables` 与 `com.unity.addressables`。该匹配是名称提示，不保证程序集来源或编译解析，所有项均标记 `resolution=unverified`。不改变已有 `unresolved_references`、风险状态或开发非阻塞原则。Unity 官方包名与程序集名可能不一致，未提示的引用也不能因此判为缺失。

## English

Reports the type of unresolved asmdef references and Unity-namespace-constrained and suffix-matched package-manifest hints. Every candidate remains unverified. A package declaration never proves that a Unity assembly resolves; absence of a hint never proves a missing reference. No gate or filesystem changes.
