# Unity external assembly evidence V1

## 中文

`unity_assemblies(root, external_evidence=None)` 支持调用方显式传入**只读观测摘要**，不访问宿主机的 `Library`、不探测本机路径或自动安装包。以 asmdef 原始引用为键，值为 `{ "status": "observed_in_package_cache" | "not_observed_in_package_cache", "package": "包ID" }`。返回 `unresolved_reference_context[].external_evidence`，只用于解释外部包缓存观测；`resolution` 一律仍为 `unverified`。不存在的观测不能判定真正缺少依赖，缓存命中也不能替代 Unity 编译验证。默认未传参数时行为兼容，检查仍不阻塞开发。实际项目里的 Timeline 等包身份必须由调用方独立核验，框架不硬编码项目版本或 GUID。

## English

The optional `external_evidence` argument accepts caller-observed package-cache evidence by original asmdef reference. No host-cache scanning, automatic package actions, compliance certification or extra gate. Evidence never changes the unresolved list or `resolution=unverified` and cannot replace Unity compile verification.
