# 📖 如何使用 Assistant Tools

本文档提供重构后的快速使用指南。

## 🎯 一分钟快速上手

### 使用知识库同步工具

```bash
# 1. 进入工具目录
cd tools/sync-kb-to-qdrant

# 2. 配置环境（首次）
cp .env.example .env
# 用编辑器打开 .env，填入你的数据库配置

# 3. 安装依赖（首次）
uv sync

# 4. 检查环境
python scripts/main.py --check

# 5. 开始使用
python scripts/main.py --all --model BAAI/bge-large-zh-v1.5
```

## 📂 重构后的目录结构

```
assistant-tools/           # 根目录（原 sync-data）
│
├── 📖 README.md          # 工具集总览 - 从这里开始
├── ⚡ QUICK_START.md     # 快速开始指南
├── 📖 HOW_TO_USE.md      # 本文件 - 使用指南
├── 🔄 MIGRATION_GUIDE.md # 迁移指南
├── 📁 PROJECT_STRUCTURE.md # 项目结构
├── ✅ REFACTOR_SUMMARY.md  # 重构总结
│
├── 📂 docs/              # 全局文档
│   ├── DEVELOPMENT.md   # 开发指南
│   ├── CONTRIBUTING.md  # 贡献指南
│   └── ARCHITECTURE.md  # 架构说明
│
├── 📂 tools/             # 🎯 工具目录（重要！）
│   └── 📂 sync-kb-to-qdrant/  # 知识库同步工具
│       ├── README.md            # 工具文档
│       ├── .env.example         # 环境变量模板
│       ├── pyproject.toml       # Python 配置
│       │
│       ├── src/                 # 源代码
│       ├── scripts/             # 可执行脚本
│       └── tests/               # 测试文件
│
└── 📂 models_cache/      # 模型缓存（共享）
```

## 🔥 常用命令速查

### 环境配置

```bash
# 进入工具目录
cd tools/sync-kb-to-qdrant

# 创建配置文件
cp .env.example .env

# 编辑配置
# Windows: notepad .env
# Linux/Mac: nano .env
# 或使用你喜欢的编辑器

# 安装依赖
uv sync
# 或使用 pip
pip install -e .
```

### 日常使用

```bash
# 确保在工具目录中
cd tools/sync-kb-to-qdrant

# 检查环境
python scripts/main.py --check

# 查看数据库统计
python scripts/main.py --stats

# 检查数据库表结构
python scripts/check_database.py

# 迁移所有数据
python scripts/main.py --all --model BAAI/bge-large-zh-v1.5

# 迁移单个公司
python scripts/main.py --company company_123

# 交互式查询测试
python tests/test_query.py

# 快速测试
python tests/quick_test.py

# API 上传
python tests/upload_to_api.py
```

### 模型管理

```bash
# 列出可用模型
python scripts/main.py --list-models

# 使用不同的模型
python scripts/main.py --all --model shibing624/text2vec-base-chinese
python scripts/main.py --all --model BAAI/bge-large-zh-v1.5

# 清理模型缓存（如果需要）
rm -rf models_cache/  # 或手动删除
```

## 🆚 命令变更对照表

### 之前（旧版本）

```bash
cd sync-data
python main.py --check
python main.py --all
python test_query.py
```

### 现在（新版本）

```bash
cd tools/sync-kb-to-qdrant
python scripts/main.py --check
python scripts/main.py --all
python tests/test_query.py
```

**主要变更**:
- 需要进入 `tools/sync-kb-to-qdrant` 目录
- 脚本在 `scripts/` 目录下
- 测试在 `tests/` 目录下

## 🎨 推荐的工作流程

### 方式 1: 直接使用

```bash
# 每次使用时
cd /path/to/assistant-tools/tools/sync-kb-to-qdrant
python scripts/main.py <命令>
```

### 方式 2: 创建别名（推荐）

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
alias kb-sync='cd /path/to/assistant-tools/tools/sync-kb-to-qdrant && python scripts/main.py'
alias kb-query='cd /path/to/assistant-tools/tools/sync-kb-to-qdrant && python tests/test_query.py'
alias kb-cd='cd /path/to/assistant-tools/tools/sync-kb-to-qdrant'
```

然后：

```bash
kb-sync --check
kb-sync --all
kb-query
kb-cd  # 进入工具目录
```

### 方式 3: 脚本封装

创建 `~/bin/kb-sync.sh`:

```bash
#!/bin/bash
cd /path/to/assistant-tools/tools/sync-kb-to-qdrant
source .venv/bin/activate
python scripts/main.py "$@"
```

```bash
chmod +x ~/bin/kb-sync.sh
kb-sync.sh --check
kb-sync.sh --all
```

## 📝 配置说明

### 环境变量文件 (.env)

位置: `tools/sync-kb-to-qdrant/.env`

必需配置:

```env
# PostgreSQL
DATABASE_HOST=localhost        # 数据库主机
DATABASE_PORT=5432            # 数据库端口
DATABASE_NAME=your_db_name    # 数据库名称
DATABASE_USER=your_username   # 数据库用户
DATABASE_PASSWORD=your_pass   # 数据库密码
DATABASE_SCHEMA=public        # 数据库 Schema

# Qdrant
QDRANT_URL=http://localhost:6333  # Qdrant 地址
```

可选配置:

```env
# 模型缓存
HF_CACHE_DIR=./models_cache   # 模型缓存目录
HF_ENDPOINT=https://hf-mirror.com  # 使用镜像加速
```

## 🐛 常见问题

### Q1: 找不到模块错误

```
ModuleNotFoundError: No module named 'src'
```

**解决**: 确保在正确的目录

```bash
cd tools/sync-kb-to-qdrant
uv sync
```

### Q2: 数据库连接失败

```
Error: 无法连接到数据库
```

**解决**: 检查 `.env` 配置

```bash
cd tools/sync-kb-to-qdrant
cat .env  # 查看配置
# 确认配置正确
```

### Q3: 找不到 .env 文件

```
Warning: .env file not found
```

**解决**: 创建配置文件

```bash
cd tools/sync-kb-to-qdrant
cp .env.example .env
# 编辑 .env 填入配置
```

### Q4: 模型下载慢

**解决**: 使用镜像加速

```bash
# 在 .env 中添加
echo "HF_ENDPOINT=https://hf-mirror.com" >> .env
```

### Q5: 旧的命令不工作

**问题**: `python main.py --check` 报错

**原因**: 重构后命令路径改变

**解决**: 使用新的命令路径

```bash
cd tools/sync-kb-to-qdrant
python scripts/main.py --check
```

## 🔄 从旧版本迁移

如果你之前在使用旧版本：

1. **查看迁移指南**
   ```bash
   cat MIGRATION_GUIDE.md
   ```

2. **更新工作目录**
   ```bash
   cd tools/sync-kb-to-qdrant
   ```

3. **迁移配置文件**
   ```bash
   # 如果你有旧的 .env 文件
   cp ../../.env .env  # 从根目录复制
   # 或重新创建
   cp .env.example .env
   ```

4. **重新安装依赖**
   ```bash
   uv sync
   ```

5. **测试**
   ```bash
   python scripts/main.py --check
   ```

## 📚 更多文档

### 用户文档

- [快速开始](./QUICK_START.md) - 30 秒快速体验
- [迁移指南](./MIGRATION_GUIDE.md) - 从旧版本升级
- [项目结构](./PROJECT_STRUCTURE.md) - 了解目录结构
- [工具文档](./tools/sync-kb-to-qdrant/README.md) - 详细的工具说明

### 开发文档

- [开发指南](./docs/DEVELOPMENT.md) - 开发环境和规范
- [贡献指南](./docs/CONTRIBUTING.md) - 如何参与项目
- [架构说明](./docs/ARCHITECTURE.md) - 项目设计

### 工具文档

- [知识库同步工具](./tools/sync-kb-to-qdrant/README.md)
- [Qdrant 查询方案](./tools/sync-kb-to-qdrant/QDRANT查询方案.md)
- [安全指南](./tools/sync-kb-to-qdrant/SAFETY_GUIDE.md)

## 💡 使用技巧

### 1. 使用虚拟环境

```bash
cd tools/sync-kb-to-qdrant
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate      # Windows

# 现在可以直接运行命令
python scripts/main.py --check
```

### 2. 批量操作

```bash
# 迁移多个公司
for company in company_1 company_2 company_3; do
  python scripts/main.py --company $company
done
```

### 3. 定时任务

```bash
# crontab -e
# 每天凌晨 2 点执行
0 2 * * * cd /path/to/tools/sync-kb-to-qdrant && /path/to/.venv/bin/python scripts/main.py --all >> /var/log/sync.log 2>&1
```

### 4. 日志记录

```bash
# 记录输出到日志文件
python scripts/main.py --all 2>&1 | tee sync.log
```

## 🚀 快速参考卡片

```
┌─────────────────────────────────────────────┐
│  Assistant Tools - 快速参考               │
├─────────────────────────────────────────────┤
│                                             │
│  📂 工具目录:                               │
│     cd tools/sync-kb-to-qdrant             │
│                                             │
│  ⚙️  配置:                                   │
│     cp .env.example .env                   │
│                                             │
│  📦 安装:                                    │
│     uv sync                                │
│                                             │
│  ✅ 检查:                                    │
│     python scripts/main.py --check         │
│                                             │
│  🚀 运行:                                    │
│     python scripts/main.py --all           │
│                                             │
│  🔍 查询:                                    │
│     python tests/test_query.py             │
│                                             │
│  📖 文档:                                    │
│     cat README.md                          │
│                                             │
└─────────────────────────────────────────────┘
```

## 📞 获取帮助

1. 查看工具的 README: `cat tools/sync-kb-to-qdrant/README.md`
2. 查看快速开始: `cat QUICK_START.md`
3. 查看迁移指南: `cat MIGRATION_GUIDE.md`
4. 创建 Issue 寻求帮助

---

**开始高效使用工具集！** 🎉

