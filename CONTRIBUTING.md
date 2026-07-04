# 贡献指南

欢迎贡献！无论是修复 bug、新增功能，还是改进文档，我们都感谢你的参与。

## 开发流程

1. **Fork 本仓库**
2. **创建特性分支**：`git checkout -b feat/xxx`
3. **编写测试**：先写测试，再实现（TDD）
4. **运行测试**：确保全部通过
5. **提交**：使用 Conventional Commits
6. **推送并创建 PR**

## Commit 规范

```
<type>: <简短描述>

<详细说明（可选）>
```

### Type 类型

| Type | 说明 |
|:----|:-----|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档 |
| `chore` | 杂项（CI、配置等） |
| `test` | 测试 |
| `refactor` | 重构 |
| `style` | 代码格式（不影响功能） |

### 示例

```
feat: add 十斋日 detection
fix: correct month-end handling for leap months
docs: update subscription URL in README
```

## 测试要求

| 类型 | 要求 |
|:----|:-----|
| 新增功能 | 必须包含测试 |
| Bug 修复 | 必须包含失败→修复的测试 |
| 代码重构 | 测试必须全部通过（证明行为不变） |

## PR 要求

- 描述变更内容
- 引用相关 Issue（如有）
- 测试通过
- 代码格式整洁

## 环境准备

```bash
git clone https://github.com/<USER>/liuzhai-ics.git
cd liuzhai-ics
pip install -r requirements.txt
pip install -e .
pip install pytest
```

---

感谢贡献 🙏
