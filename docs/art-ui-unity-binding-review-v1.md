# Art/UI Unity Binding Review V1

Project-owned optional `art_ui_unity_binding` config provides common/main asset, group and address fields. This read-only scanner checks Unity .meta GUID relationships, Addressables group GUID/address pairs and the main UI asset collection common GUID. It never changes resources or claims runtime/visual correctness. Both Unity and Art/UI must be explicitly selected. Invalid optional config warns without blocking.

Example (illustrative paths only):
~~~json
"art_ui_unity_binding": {
  "common": { "asset": "Assets/Settings/UI/CommonAssets.asset", "group": "Assets/AddressableAssetsData/AssetGroups/UI_Common.asset", "address": "UI/Common/Assets" },
  "main": { "asset": "Assets/Settings/UI/MainAssets.asset", "group": "Assets/AddressableAssetsData/AssetGroups/UI_Main.asset", "address": "UI/Main/Assets" }
}
~~~

中文：配置路径及地址由项目显式提供，不在 FrameForge 核心写死任何项目路径。检查只判断静态资源引用关系，不代表 Unity 运行时加载、Sprite 内容或视觉质量验收；无配置则不执行，错误配置只报告非阻塞 Warning。示例路径为虚构内容。
