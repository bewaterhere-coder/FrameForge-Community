# FrameForge Best Practices / FrameForge 最佳实践

## 中文

本文介绍如何在一个或多个代码仓库中引入 FrameForge、绑定项目自己的规范，并让团队持续维护。FrameForge 是只读建议工具：项目拥有正式规范，插件必须显式选择，Warning 默认不阻塞开发。

### 1. 安装与首次检查

```sh
git clone https://github.com/bewaterhere-coder/FrameForge-Community.git
cd FrameForge-Community
python -m pip install .
frameforge --plugins
frameforge /path/to/your/game-project
```

当前从 GitHub 源码安装，尚未发布 PyPI 包。不要使用 `pip install frameforge`：PyPI 上已有同名的其他项目。

首次检查先识别技术栈、候选插件和规范缺口。发现插件不代表启用插件；首次扫描不会修改项目。

### 2. 建立项目自己的规范

由项目负责人确定规范的正式位置和版本。可以将规范保存在项目仓库，也可以在项目授权范围内引用其他位置。FrameForge 不要求团队采用某一种架构，也不替项目决定 MVP、MVVM、ECS、分层或资源目录方案。

建议至少明确：
- 代码架构与模块边界；
- UI、美术与交互约定（适用时）；
- 资源导入、命名、版本和引用规则；
- 测试范围、运行环境和验收证据；
- 规范负责人、版本及变更方式。

### 3. 显式绑定插件与规范

在项目根目录创建 `.frameforge/profile.json`，只选择当前项目需要的插件，并绑定项目正式规范路径。不要为了消除 Warning 而创建空白规范或启用无关插件。

```json
{
  "schema_version": 1,
  "plugins": [
    {"id": "unity", "version": "1.0.0"}
  ],
  "standards": [
    {"domain": "architecture", "path": "docs/architecture.md", "version": "1.0"}
  ]
}
```

以上仅为格式示例；插件 ID、版本和规范路径必须以实际项目为准。

### 4. 多仓库项目

多仓库项目可以在每个仓库分别维护 Profile，也可以由项目约定一个明确的规范仓库，并在各代码仓库中绑定其版本化副本或受控引用。不要让一个仓库的 Profile 隐式覆盖另一个仓库；不要将项目规范复制到 FrameForge 全局目录。

建议为每个仓库记录：
- 仓库职责和技术栈；
- 规范来源、版本及负责人；
- 已选择的插件及版本；
- 跨仓库接口与共享资源的归属；
- 无法扫描或尚未验证的范围。

### 5. 阅读检查结果

重点区分：
- `suggested_plugins`：发现的候选插件，不代表已选择；
- `selected_plugins`：项目 Profile 明确选择的插件；
- `standard_sources`：已绑定的规范引用，不自动证明规范已获批准；
- `standard_candidates`：按有限规则发现的候选文档，可能误报或遗漏；
- `professional_guidance` / `structural_observations`：有限范围内的专业提示或结构观察；
- `not_evaluated`：当前没有可靠证据，不能解释为 PASS 或 FAIL。

静态信号不是完整语义分析。没有 Warning 不等于完全合规；发现 Warning 也不自动代表代码错误。

### 6. 整改与复查

项目负责人决定是否采纳建议。整改必须遵循项目自身的变更授权和评审流程。完成后重新运行检查，比较旧 Warning 与新结果。FrameForge 的复查只说明观察结果发生了什么变化，不批准代码、不合并变更，也不产生正式验收结论。

### 7. 社区插件维护

新增引擎或专业领域支持时，先提交 Candidate 插件：记录官方来源、适用版本、识别信号、建议范围、排除项和失败边界。没有真实项目验证时必须保留 Candidate 状态。只有在多个真实项目中完成可复核验证后，才考虑升级为 Validated。

### 常见错误

- 将发现的插件当成已经启用；
- 把文件名命中当作规范权威或内容正确；
- 将静态提示当成运行时测试或完整合规认证；
- 把 FrameForge Warning 变成强制开发 Gate；
- 未经项目负责人确认就修改规范绑定；
- 将真实项目路径、账号、密钥或内部工作记录提交到公开仓库。

## English

This guide explains how to introduce FrameForge into one or more repositories, bind project-owned standards and maintain the setup over time. FrameForge is a read-only advisory tool: projects own their canonical standards, plugins require explicit selection, and warnings are non-blocking by default.

### 1. Install and inspect

```sh
git clone https://github.com/bewaterhere-coder/FrameForge-Community.git
cd FrameForge-Community
python -m pip install .
frameforge --plugins
frameforge /path/to/your/game-project
```

Install from GitHub source for now; no PyPI release is available. Do not run `pip install frameforge`: that name is already used by an unrelated PyPI project.

The first inspection discovers technology markers, candidate plugins and possible standards gaps. Discovery does not activate plugins or modify the project.

### 2. Define project-owned standards

Project owners decide where canonical standards live and how they are versioned. FrameForge does not require a particular architecture or prescribe a single UI, asset or code organization model.

Useful topics include architecture and module boundaries, UI/art conventions, asset import and reference rules, test scope and evidence, and standards ownership/versioning.

### 3. Select plugins and bind standards explicitly

Create `.frameforge/profile.json` at the project root. Select only the plugins needed by that project and bind canonical standards paths. Do not create empty standards or enable unrelated plugins merely to silence warnings. See the [Profile example](profile-example.json) and [plugin authoring guide](plugin-authoring-guide.md).

### 4. Multi-repository projects

Each repository may maintain its own Profile, or follow a documented shared-standards repository with versioned references. Do not let one repository's Profile silently override another's, and do not copy project standards into a global FrameForge directory. Record repository ownership, technology stack, standard source/version, selected plugins, cross-repository interfaces and unevaluated scope.

### 5. Interpret results carefully

Distinguish suggested plugins from selected plugins, bound standard references from discovered candidates, and observed evidence from actual compliance. `not_evaluated` means there is no reliable assessment; it is neither PASS nor FAIL. Static signals are not full semantic analysis. No warning does not prove complete compliance, and a warning does not automatically prove a defect.

### 6. Remediate and recheck

The project owner decides whether to act. Changes follow the project's own authorization and review process. A fresh inspection can compare previous and current warnings, but it does not approve code, merge changes or issue a formal acceptance decision.

### 7. Maintain community plugins

Start new engine or specialist plugins as Candidates. Record official sources, supported versions, detection signals, advisory scope, exclusions and failure boundaries. Keep Candidate status until evidence from multiple real projects has been reviewed and can be reproduced.

### Common mistakes

- Treating discovery as activation;
- Treating filename matches as proof of authority or content correctness;
- Treating static hints as runtime tests or complete compliance certification;
- Turning warnings into mandatory development gates;
- Changing standard bindings without project-owner approval;
- Committing real project paths, credentials, secrets or internal work records to a public repository.
