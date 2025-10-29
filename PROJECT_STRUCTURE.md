# 📁 项目结构

本文档展示完整的项目目录结构和文件说明。

## 🏗️ 目录树

```
assistant-tools/                          # 根目录
│
├── 📄 README.md                         # ⭐ 工具集总览和入口
├── 📄 QUICK_START.md                    # ⚡ 快速开始指南
├── 📄 MIGRATION_GUIDE.md                # 🔄 从旧版本迁移指南
├── 📄 PROJECT_STRUCTURE.md              # 📁 本文件 - 项目结构说明
├── 📄 .gitignore                        # Git 忽略规则
│
├── 📂 docs/                             # 📚 全局文档目录
│   ├── DEVELOPMENT.md                  # 🛠️ 开发指南
│   ├── CONTRIBUTING.md                 # 🤝 贡献指南
│   └── ARCHITECTURE.md                 # 🏗️ 架构设计说明
│
├── 📂 tools/                            # 🛠️ 工具集合目录
│   │
│   └── 📂 sync-kb-to-qdrant/          # 📊 知识库同步工具
│       │
│       ├── 📄 README.md               # 工具使用文档
│       ├── 📄 .env.example            # 环境变量模板
│       ├── 📄 .gitignore              # 工具特定忽略规则
│       ├── 📄 pyproject.toml          # Python 项目配置
│       ├── 📄 uv.lock                 # 依赖锁定文件
│       ├── 📄 .python-version         # Python 版本
│       │
│       ├── 📄 QDRANT查询方案.md       # Qdrant 查询详细文档
│       ├── 📄 SAFETY_GUIDE.md         # 安全使用指南
│       ├── 📄 使用说明.txt            # API 上传工具说明
│       │
│       ├── 📂 src/                    # 源代码目录
│       │   ├── __init__.py           # Python 包初始化
│       │   ├── main.py               # 主入口模块
│       │   ├── database.py           # PostgreSQL 数据库操作
│       │   ├── qdrant_manager.py     # Qdrant 向量数据库管理
│       │   ├── embedding_service.py  # 嵌入模型服务
│       │   └── migrator.py           # 数据迁移逻辑
│       │
│       ├── 📂 scripts/                # 可执行脚本目录
│       │   ├── main.py               # 主执行脚本（CLI 入口）
│       │   ├── check_database.py     # 数据库检查脚本
│       │   ├── cleanup_collection.py # 清理集合脚本
│       │   └── generate_embedding.py # 生成嵌入脚本
│       │
│       └── 📂 tests/                  # 测试和工具目录
│           ├── test_query.py         # 查询测试工具
│           ├── test_upload.py        # 上传测试
│           ├── quick_test.py         # 快速测试
│           └── upload_to_api.py      # API 上传工具
│
└── 📂 models_cache/                    # 模型缓存目录（全局共享）
    └── models--*/                     # Hugging Face 模型缓存
```

## 📝 文件说明

### 根目录文件

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `README.md` | 工具集总览，列出所有可用工具 | ⭐⭐⭐ 必读 |
| `QUICK_START.md` | 快速开始指南，30 秒上手 | ⭐⭐⭐ 推荐 |
| `MIGRATION_GUIDE.md` | 迁移指南，从旧版本升级 | ⭐⭐ 升级时必读 |
| `PROJECT_STRUCTURE.md` | 项目结构说明（本文件） | ⭐ 参考 |
| `.gitignore` | Git 忽略规则 | ⭐⭐⭐ 重要 |

### docs/ 目录

| 文件 | 说明 | 受众 |
|------|------|------|
| `DEVELOPMENT.md` | 开发指南，环境配置、代码规范 | 开发者 |
| `CONTRIBUTING.md` | 贡献指南，如何参与项目 | 贡献者 |
| `ARCHITECTURE.md` | 架构设计文档 | 架构师/高级开发者 |

### tools/sync-kb-to-qdrant/ 目录

#### 配置文件

| 文件 | 说明 | 是否必需 |
|------|------|---------|
| `README.md` | 工具使用文档 | ⭐⭐⭐ 必读 |
| `.env.example` | 环境变量模板 | ⭐⭐⭐ 必需 |
| `pyproject.toml` | Python 项目配置和依赖 | ⭐⭐⭐ 必需 |
| `uv.lock` | 依赖版本锁定 | ⭐⭐ 推荐提交 |
| `.python-version` | Python 版本指定 | ⭐⭐ 推荐 |

#### 源代码 (src/)

| 文件 | 说明 | 职责 |
|------|------|------|
| `main.py` | 主入口模块 | 命令行参数解析、流程控制 |
| `database.py` | 数据库操作 | PostgreSQL 连接和查询 |
| `qdrant_manager.py` | Qdrant 管理 | 向量数据库操作 |
| `embedding_service.py` | 嵌入服务 | 文本向量化 |
| `migrator.py` | 迁移逻辑 | 数据迁移流程 |

#### 脚本 (scripts/)

| 文件 | 说明 | 用途 |
|------|------|------|
| `main.py` | 主执行脚本 | 日常使用的 CLI 入口 |
| `check_database.py` | 数据库检查 | 验证数据库连接和表结构 |
| `cleanup_collection.py` | 清理集合 | 清理 Qdrant 集合 |
| `generate_embedding.py` | 生成嵌入 | 单独生成文本嵌入 |

#### 测试 (tests/)

| 文件 | 说明 | 用途 |
|------|------|------|
| `test_query.py` | 查询测试 | 交互式查询工具 |
| `test_upload.py` | 上传测试 | 测试数据上传 |
| `quick_test.py` | 快速测试 | 快速功能验证 |
| `upload_to_api.py` | API 上传工具 | 批量上传到 API |

## 🎯 文件作用域

### 全局作用域

这些文件/目录对整个项目生效：

- `docs/` - 全局文档
- `models_cache/` - 共享模型缓存
- `.gitignore` - Git 忽略规则

### 工具作用域

这些文件/目录仅对特定工具生效：

- `tools/<tool-name>/` - 工具目录
- `tools/<tool-name>/.env` - 工具环境变量
- `tools/<tool-name>/.venv/` - 工具虚拟环境
- `tools/<tool-name>/src/` - 工具源代码

## 🔄 工作流程

### 使用单个工具

```bash
# 1. 进入工具目录
cd tools/sync-kb-to-qdrant

# 2. 配置环境
cp .env.example .env
# 编辑 .env...

# 3. 安装依赖
uv sync

# 4. 使用工具
python scripts/main.py --check
```

### 添加新工具

```bash
# 1. 创建工具目录
mkdir -p tools/my-new-tool/{src,scripts,tests}

# 2. 添加必要文件
cd tools/my-new-tool
touch README.md .env.example pyproject.toml
touch src/__init__.py src/main.py
touch scripts/run.py
touch tests/test_main.py

# 3. 更新根 README.md
# 在工具列表中添加新工具

# 4. 开发和测试
# ...
```

## 📊 目录大小估算

| 目录 | 典型大小 | 说明 |
|------|---------|------|
| `docs/` | < 1 MB | 纯文档 |
| `tools/sync-kb-to-qdrant/src/` | < 1 MB | Python 源代码 |
| `tools/sync-kb-to-qdrant/.venv/` | 50-500 MB | 虚拟环境（git 忽略）|
| `models_cache/` | 1-5 GB | 模型文件（git 忽略）|

## 🔐 敏感文件

这些文件包含敏感信息，**不应提交到 Git**：

- `tools/*/.env` - 环境变量（包含密码、密钥）
- `tools/*/.venv/` - 虚拟环境
- `models_cache/` - 模型缓存
- `tools/*/*.log` - 日志文件

已在 `.gitignore` 中配置。

## 📦 可提交文件

这些文件**应该提交到 Git**：

- 所有 `.md` 文档
- `pyproject.toml` / `package.json`
- `uv.lock` / `bun.lockb`（推荐）
- `.env.example` 模板
- 所有源代码（`src/`, `scripts/`, `tests/`）

## 🚀 最佳实践

### 命名约定

- **工具目录**: `kebab-case` (如 `sync-kb-to-qdrant`)
- **Python 文件**: `snake_case.py` (如 `database.py`)
- **TypeScript 文件**: `kebab-case.ts` (如 `main-service.ts`)
- **文档文件**: `UPPER_SNAKE_CASE.md` (如 `README.md`)

### 目录组织

- **独立性**: 每个工具完全独立
- **一致性**: 所有工具遵循相同结构
- **清晰性**: 文件命名和位置明确
- **可维护**: 易于理解和修改

### 文档编写

- **README.md**: 每个工具必备
- **代码注释**: 关键逻辑添加注释
- **类型注解**: Python 和 TypeScript 使用类型
- **示例代码**: 提供使用示例

## 📈 项目增长

### 当前状态

```
tools/
└── sync-kb-to-qdrant/  # 1 个工具
```

### 未来规划

```
tools/
├── sync-kb-to-qdrant/  # 数据同步
├── api-tester/         # API 测试
├── log-analyzer/       # 日志分析
├── deployment-tool/    # 部署工具
└── monitoring/         # 监控工具
```

## 🔍 快速导航

### 我想...

- **开始使用** → [QUICK_START.md](./QUICK_START.md)
- **查看所有工具** → [README.md](./README.md)
- **使用知识库同步** → [tools/sync-kb-to-qdrant/](./tools/sync-kb-to-qdrant/README.md)
- **学习开发** → [docs/DEVELOPMENT.md](./docs/DEVELOPMENT.md)
- **贡献代码** → [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md)
- **了解架构** → [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- **从旧版本升级** → [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

---

**清晰的结构，高效的工作！** 📁✨

