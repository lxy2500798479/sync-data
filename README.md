# 🛠️ Assistant Tools - 业务工具集合

一个集成多个实用工具的仓库，用于简化日常业务开发和运维工作。每个工具都是独立的、可单独使用的模块。

## 📦 工具列表

### 1. 📊 知识库同步工具 (sync-kb-to-qdrant)

将 PostgreSQL 中的知识库数据同步到 Qdrant 向量数据库的 Python 工具。

- **语言**: Python 3.11+
- **功能**: 
  - PostgreSQL 到 Qdrant 的数据迁移
  - 支持多种中文嵌入模型
  - 批量处理和 GPU 加速
  - 完整的查询测试工具
- **文档**: [📖 详细文档](./tools/sync-kb-to-qdrant/README.md)
- **快速开始**:
  ```bash
  cd tools/sync-kb-to-qdrant
  uv sync
  python scripts/main.py --check
  ```

### 2. 🔜 更多工具即将添加...

计划中的工具：
- 数据迁移工具
- API 测试工具
- 日志分析工具
- 自动化部署脚本

## 🚀 快速开始

### 克隆仓库

```bash
git clone <your-repo-url>
cd assistant-tools
```

### 选择工具

每个工具都在 `tools/` 目录下，有独立的文档和依赖管理：

```bash
cd tools/<tool-name>
# 查看该工具的 README.md 了解使用方法
```

## 📂 项目结构

```
assistant-tools/
├── README.md                    # 本文件 - 工具集总览
├── .gitignore                  # 全局忽略规则
│
├── tools/                      # 🛠️ 工具目录
│   ├── sync-kb-to-qdrant/     # 知识库同步工具
│   │   ├── README.md          # 工具说明
│   │   ├── pyproject.toml     # Python 依赖
│   │   ├── .env.example       # 环境变量模板
│   │   ├── src/               # 源代码
│   │   ├── scripts/           # 执行脚本
│   │   └── tests/             # 测试文件
│   │
│   └── <future-tool>/         # 未来的工具...
│
└── docs/                       # 📚 全局文档
    ├── DEVELOPMENT.md         # 开发指南
    ├── CONTRIBUTING.md        # 贡献指南
    └── ARCHITECTURE.md        # 架构说明
```

## 🎯 设计原则

1. **独立性**: 每个工具独立运行，互不依赖
2. **简洁性**: 每个工具专注于解决一个具体问题
3. **文档化**: 每个工具都有完整的使用文档
4. **可维护**: 清晰的代码结构和规范

## 🤝 贡献新工具

想要添加新工具？遵循以下步骤：

### 1. 创建工具目录

```bash
mkdir -p tools/<your-tool-name>/{src,scripts,tests}
```

### 2. 添加必要文件

```
tools/<your-tool-name>/
├── README.md           # 工具说明（必需）
├── .env.example        # 环境变量模板（如需要）
├── pyproject.toml      # Python 项目配置
├── package.json        # 或 Node.js 项目配置
├── src/                # 源代码目录
├── scripts/            # 可执行脚本
└── tests/              # 测试文件
```

### 3. 编写文档

在 `tools/<your-tool-name>/README.md` 中说明：
- 工具用途和功能
- 快速开始指南
- 环境要求
- 使用示例
- 故障排除

### 4. 更新主 README

在本文件的"工具列表"中添加你的工具。

## 📝 开发规范

### Python 工具

- 使用 Python 3.11+
- 使用 `uv` 或 `pip` 管理依赖
- 提供 `pyproject.toml` 和 `.env.example`
- 遵循 PEP 8 代码风格

### TypeScript/Node.js 工具

- 使用 TypeScript 5.0+
- 使用 `bun` 或 `npm` 管理依赖
- 提供 `package.json` 和 `.env.example`
- 遵循 ESLint 规范

## 🔧 环境要求

不同工具有不同的环境要求，请查看具体工具的 README.md。

### 通用要求

- Git
- 文本编辑器或 IDE

### 可选工具

- Python 3.11+ (Python 工具)
- Node.js 18+ 或 Bun (JavaScript/TypeScript 工具)
- Docker (容器化工具)

## 📖 文档资源

- [开发指南](./docs/DEVELOPMENT.md) - 开发环境配置和最佳实践
- [贡献指南](./docs/CONTRIBUTING.md) - 如何贡献代码
- [架构说明](./docs/ARCHITECTURE.md) - 项目架构设计

## 🐛 故障排除

### 常见问题

**Q: 如何单独使用某个工具？**

A: 进入工具目录，按照该工具的 README.md 操作即可：
```bash
cd tools/<tool-name>
# 按照 README 指示操作
```

**Q: 工具之间可以共享代码吗？**

A: 目前每个工具是独立的。如果需要共享代码，可以考虑创建 `shared/` 目录。

**Q: 如何添加新工具？**

A: 参考上面的"贡献新工具"章节。

## 📄 许可证

MIT License

---

**✨ 让业务开发更高效！**
