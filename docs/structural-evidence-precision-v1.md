# Structural Evidence Precision V1 / 结构证据精度 V1

## 中文

本说明定义静态结构提示的证据边界。检查器可以报告重复程序集名称、疑似事务失败分支等有限信号，但必须保留文件与行号，并明确标记为待复核线索。普通注释不应被误识别为可执行分支。

这些检查是只读、非阻塞的静态观察，不能替代编译器、完整语言解析器、运行时或数据库集成测试。标记存在不证明逻辑正确；标记缺失也不证明功能缺失，因为实现可能位于其他模块或采用不同结构。

## English

Static structural checks may report bounded signals such as duplicate assembly names or potential transaction failure branches. Findings should retain file/line evidence and remain review hints. Ordinary comments must not be mistaken for executable branches.

These checks are read-only and non-blocking. They do not replace compilers, full language parsers, runtime tests or database integration tests. A marker does not prove correctness, and an absent marker does not prove a capability is missing; implementations may live in other modules or use different structures.
