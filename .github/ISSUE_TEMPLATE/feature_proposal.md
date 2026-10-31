---
name: Feature or capability proposal
about: Propose a reusable improvement without assuming it belongs in Core
title: '[proposal] '
labels: []
---

Please read [Contributing](../../CONTRIBUTING.md) before proposing a change.
提交前请阅读[贡献指南](../../CONTRIBUTING.md)。

## Problem and user impact / 问题与使用者影响

What concrete problem does this solve? Who encounters it, and how often?
要解决什么具体问题？哪些使用者会遇到，频率如何？

## Current workaround / 当前替代方式

What can users do today? What is missing or costly?
当前如何处理？缺少什么，成本在哪里？

## Proposed behavior / 建议行为

Describe the expected user-visible behavior. Avoid prescribing an implementation too early.
描述期望的用户可见行为，不必过早指定实现方式。

## Scope candidate / 可能的归属

- [ ] Existing plugin or declarative Manifest / 现有插件或声明式 Manifest
- [ ] New optional plugin / 新的可选插件
- [ ] Core capability used by multiple plugins / 多个插件共同需要的 Core 能力
- [ ] CLI / MCP / Host integration / 入口或 Host 集成
- [ ] Documentation or workflow / 文档或工作流
- [ ] Not sure; please help classify / 不确定，请协助判断

If proposing Core, explain why existing plugin contracts cannot express this and name at least two distinct use cases.
如果建议修改 Core，请说明现有插件契约为何无法表达，并给出至少两个不同使用场景。

## Evidence and references / 证据与参考资料

Link official documentation, examples, user feedback or reproducible observations. Clearly label assumptions.
提供官方文档、示例、用户反馈或可复现观察；明确标记推测。

## Compatibility and safety / 兼容性与安全

Describe affected versions, read/write needs, privacy concerns, failure cases and nonblocking behavior.
说明影响版本、读写需求、隐私风险、失败路径及非阻塞要求。

## Alternatives and trade-offs / 替代方案与取舍

What simpler options were considered? What should remain out of scope?
考虑过哪些更简单的方案？哪些内容应明确排除？

## Additional context / 其他信息

Do not include credentials, private project source, internal paths or unlicensed assets.
请勿提交凭据、私有项目源码、内部路径或未获授权的素材。
