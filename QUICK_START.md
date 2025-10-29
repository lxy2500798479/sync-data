# ⚡ 快速开始

欢迎使用 Assistant Tools！这是一个实用工具集合仓库，帮助你快速完成各种业务任务。

## 📦 仓库结构

```
assistant-tools/
├── README.md              # 📖 工具集总览（从这里开始）
├── QUICK_START.md        # ⚡ 本文件 - 快速开始
├── MIGRATION_GUIDE.md    # 🔄 迁移指南（如果从旧版本升级）
│
├── tools/                # 🛠️ 工具集合
│   └── sync-kb-to-qdrant/  # 知识库同步工具
│       └── README.md     # 工具详细文档
│
└── docs/                 # 📚 全局文档
    ├── DEVELOPMENT.md   # 开发指南
    ├── CONTRIBUTING.md  # 贡献指南
    └── ARCHITECTURE.md  # 架构说明
```

## 🎯 30 秒快速体验

### 使用知识库同步工具

```bash
# 1. 进入工具目录
cd tools/sync-kb-to-qdrant

# 2. 安装依赖
uv sync
# 或: pip install -e .

# 3. 配置环境（复制并编辑）
cp .env.example .env

# 4. 检查环境
python scripts/main.py --check

# 5. 开始使用
python scripts/main.py --help
```

## 📚 工具列表

### 1️⃣ 知识库同步工具 (sync-kb-to-qdrant)

**用途**: 将 PostgreSQL 知识库数据同步到 Qdrant 向量数据库

**快速使用**:
```bash
cd tools/sync-kb-to-qdrant
python scripts/main.py --check          # 检查环境
python scripts/main.py --stats          # 查看统计
python scripts/main.py --all            # 迁移所有数据
```

**详细文档**: [点击查看](./tools/sync-kb-to-qdrant/README.md)

### 2️⃣ 更多工具...

敬请期待！

## 🔍 选择你需要的工具

### 我需要数据同步

→ 使用 [sync-kb-to-qdrant](./tools/sync-kb-to-qdrant/)

### 我需要 API 测试

→ 即将推出

### 我需要日志分析

→ 即将推出

## 💡 使用建议

### 首次使用

1. **阅读工具的 README** - 了解具体功能和要求
2. **配置环境变量** - 复制 `.env.example` 为 `.env`
3. **检查环境** - 运行检查命令确保配置正确
4. **开始使用** - 按照文档执行命令

### 日常使用

```bash
# 通用流程
cd tools/<tool-name>        # 进入工具目录
source .venv/bin/activate   # 激活虚拟环境（可选）
python scripts/main.py ...  # 执行命令
```

### 多工具使用

每个工具都是独立的，可以同时使用多个：

```bash
# 终端 1: 使用工具 1
cd tools/sync-kb-to-qdrant
python scripts/main.py --all

# 终端 2: 使用工具 2（未来）
cd tools/another-tool
python scripts/run.py
```

## 🔧 常见问题

### Q: 如何查看可用的工具？

A: 查看 `tools/` 目录，每个子目录都是一个工具。

```bash
ls tools/
# 或查看主 README.md 的工具列表
```

### Q: 如何安装单个工具的依赖？

A: 进入工具目录，运行安装命令：

```bash
cd tools/<tool-name>

# Python 工具
uv sync           # 推荐
# 或
pip install -e .

# TypeScript 工具
bun install       # 推荐
# 或
npm install
```

### Q: 工具之间会相互影响吗？

A: 不会。每个工具都有独立的：
- 依赖管理（`pyproject.toml` 或 `package.json`）
- 虚拟环境（`.venv/` 或 `node_modules/`）
- 环境变量（`.env`）

### Q: 如何更新工具？

A: 拉取最新代码并更新依赖：

```bash
# 更新代码
git pull

# 更新工具依赖
cd tools/<tool-name>
uv sync --upgrade  # Python
# 或
bun update         # TypeScript
```

### Q: 遇到问题怎么办？

A: 按照以下顺序：

1. 查看工具的 README.md 的"故障排除"章节
2. 查看 [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)（如果从旧版本升级）
3. 查看 [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md)
4. 创建 Issue 寻求帮助

## 🌟 推荐工作流

### 初次设置

```bash
# 1. 克隆仓库
git clone <repo-url>
cd assistant-tools

# 2. 浏览可用工具
cat README.md

# 3. 选择需要的工具
cd tools/sync-kb-to-qdrant

# 4. 阅读工具文档
cat README.md

# 5. 配置和使用
cp .env.example .env
# 编辑 .env...
uv sync
python scripts/main.py --check
```

### 日常使用

```bash
# 直接进入工具目录
cd tools/<tool-name>

# 运行命令
python scripts/main.py ...
# 或
bun run src/main.ts ...
```

## 🚀 进阶使用

### 添加别名（可选）

为常用命令创建别名：

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias kb-sync='cd /path/to/assistant-tools/tools/sync-kb-to-qdrant && python scripts/main.py'

# 使用
kb-sync --check
kb-sync --all
```

### 创建自动化脚本

```bash
#!/bin/bash
# daily-sync.sh

cd /path/to/assistant-tools/tools/sync-kb-to-qdrant
source .venv/bin/activate
python scripts/main.py --all --model BAAI/bge-large-zh-v1.5
```

### 添加 cron 任务

```bash
# 每天凌晨 2 点执行同步
0 2 * * * /path/to/daily-sync.sh >> /var/log/sync.log 2>&1
```

## 📖 下一步

### 了解更多

- [工具集总览](./README.md) - 查看所有可用工具
- [开发指南](./docs/DEVELOPMENT.md) - 学习如何开发和贡献
- [贡献指南](./docs/CONTRIBUTING.md) - 如何参与项目
- [架构说明](./docs/ARCHITECTURE.md) - 了解项目设计

### 开始使用特定工具

- [sync-kb-to-qdrant](./tools/sync-kb-to-qdrant/README.md) - 知识库同步工具

### 贡献你的工具

如果你有实用的工具想要分享：

1. 阅读 [贡献指南](./docs/CONTRIBUTING.md)
2. 参考现有工具的结构
3. 创建 PR

## 💬 获取帮助

- 📖 查看文档
- 🐛 创建 Issue
- 💡 参与讨论

---

**开始你的高效工作之旅！** 🎉

