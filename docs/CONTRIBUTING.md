# 🤝 贡献指南

感谢你考虑为 Assistant Tools 做出贡献！本指南将帮助你了解如何参与项目。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [报告问题](#报告问题)
- [提交代码](#提交代码)
- [代码审查流程](#代码审查流程)

## 🌟 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性暗示的语言或图像
- 挑衅、侮辱或贬损性评论
- 骚扰（公开或私下）
- 未经明确许可发布他人私人信息
- 其他不专业或不受欢迎的行为

## 🎯 如何贡献

### 贡献类型

你可以通过多种方式贡献：

1. **报告 Bug** - 发现问题并告诉我们
2. **建议新功能** - 提出改进想法
3. **改进文档** - 修正错别字、添加示例
4. **编写代码** - 修复 Bug 或实现新功能
5. **添加新工具** - 贡献新的实用工具

### 开始之前

1. **查看现有 Issues** - 确保你的想法尚未被提出
2. **阅读文档** - 了解项目结构和规范
3. **与维护者沟通** - 对于大的改动，先讨论后实施

## 🐛 报告问题

### Bug 报告

创建详细的 Bug 报告帮助我们快速定位和修复问题。

**优秀的 Bug 报告应包含**:

```markdown
**描述**
简短描述问题

**复现步骤**
1. 进入 '...'
2. 点击 '...'
3. 看到错误

**期望行为**
你期望发生什么

**实际行为**
实际发生了什么

**截图**
如果适用，添加截图

**环境**
- 操作系统: [如 Windows 11]
- Python/Node 版本: [如 Python 3.11]
- 工具版本: [如 v0.1.0]

**附加信息**
其他相关信息
```

### 功能建议

提出新功能时，请说明：

1. **问题描述** - 这个功能解决什么问题？
2. **建议方案** - 你希望如何实现？
3. **替代方案** - 考虑过哪些其他方法？
4. **使用场景** - 谁会使用这个功能？

## 💻 提交代码

### 设置开发环境

1. **Fork 仓库**

   点击 GitHub 页面右上角的 "Fork" 按钮

2. **克隆你的 Fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/assistant-tools.git
   cd assistant-tools
   ```

3. **添加上游仓库**

   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/assistant-tools.git
   ```

4. **创建分支**

   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

### 开发工作流

1. **保持同步**

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **进行更改**

   - 遵循[开发规范](./DEVELOPMENT.md)
   - 编写清晰的代码和注释
   - 添加必要的测试

3. **运行测试**

   ```bash
   # Python 工具
   cd tools/your-tool
   pytest

   # TypeScript 工具
   cd tools/your-tool
   bun test
   ```

4. **提交更改**

   遵循[约定式提交](https://www.conventionalcommits.org/zh-hans/)规范：

   ```bash
   git add .
   git commit -m "feat(tool-name): 添加新功能"
   ```

   **提交类型**:
   - `feat`: 新功能
   - `fix`: Bug 修复
   - `docs`: 文档更新
   - `style`: 代码格式调整
   - `refactor`: 重构（不改变功能）
   - `test`: 测试相关
   - `chore`: 构建/工具链相关

   **示例**:
   ```bash
   git commit -m "feat(sync-kb): 添加批量导入功能"
   git commit -m "fix(sync-kb): 修复连接超时问题"
   git commit -m "docs: 更新快速开始指南"
   ```

5. **推送到 Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**

   - 访问你的 Fork 页面
   - 点击 "New Pull Request"
   - 填写 PR 描述
   - 等待审查

### Pull Request 指南

**PR 标题**应简洁明了：

```
feat(tool-name): 添加新功能
fix(tool-name): 修复某个问题
docs: 更新文档
```

**PR 描述**应包含：

```markdown
## 变更说明
简述你的更改

## 相关 Issue
Closes #123

## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 重构
- [ ] 其他（请说明）

## 测试
描述你如何测试这些更改

## 截图（如适用）
添加截图说明变更

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了测试
- [ ] 测试通过
- [ ] 更新了文档
- [ ] 没有破坏性变更（或已在描述中说明）
```

### 代码审查

提交 PR 后：

1. **自动检查** - CI/CD 会自动运行测试
2. **维护者审查** - 维护者会审查你的代码
3. **反馈** - 根据反馈进行修改
4. **合并** - 审查通过后，你的代码会被合并

**审查可能需要**:
- 代码修改
- 添加测试
- 更新文档
- 解决冲突

## 🎨 代码风格

### Python

```python
# ✅ 好的示例
def calculate_total(items: list[dict], tax_rate: float = 0.1) -> float:
    """
    计算总价（含税）
    
    Args:
        items: 商品列表，每项包含 price 字段
        tax_rate: 税率，默认 10%
        
    Returns:
        总价（含税）
    """
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)
```

### TypeScript

```typescript
// ✅ 好的示例
interface Item {
  price: number;
}

export function calculateTotal(items: Item[], taxRate: number = 0.1): number {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  return subtotal * (1 + taxRate);
}
```

## ➕ 添加新工具

想要贡献新工具？太棒了！

### 步骤

1. **创建 Issue** 描述你的工具
2. **等待反馈** 确认方向正确
3. **实现工具** 遵循[开发指南](./DEVELOPMENT.md)
4. **提交 PR** 包含完整文档和测试

### 新工具必需包含

- [ ] `README.md` - 完整的使用文档
- [ ] 源代码 - 在 `src/` 目录
- [ ] 测试 - 在 `tests/` 目录
- [ ] `.env.example` - 环境变量模板（如需要）
- [ ] 依赖配置 - `pyproject.toml` 或 `package.json`

### 新工具示例

查看现有工具作为参考：
- [sync-kb-to-qdrant](../tools/sync-kb-to-qdrant/) - Python 工具示例

## 📝 文档贡献

文档改进永远欢迎！

### 改进类型

- 修正拼写/语法错误
- 添加使用示例
- 改进说明清晰度
- 添加常见问题解答
- 翻译文档

### 文档结构

```markdown
# 标题

简短介绍

## 功能

功能列表

## 快速开始

\`\`\`bash
# 代码示例
\`\`\`

## 详细说明

更多细节

## 故障排除

常见问题
```

## 🏆 贡献者

感谢所有贡献者！你的贡献会被记录在：

- GitHub Contributors 页面
- 项目 README（重大贡献）
- Release Notes

## ❓ 问题？

如有疑问：

1. 查看[开发指南](./DEVELOPMENT.md)
2. 搜索现有 Issues
3. 创建新 Issue 询问

## 📄 许可证

贡献即表示你同意你的代码在 MIT 许可证下发布。

---

**再次感谢你的贡献！** 🎉

你的参与让这个项目更好！


