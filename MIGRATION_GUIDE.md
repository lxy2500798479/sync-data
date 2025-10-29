# 🔄 迁移指南

本文档说明如何从旧的项目结构迁移到新的工具集结构。

## 📌 变更概述

### 旧结构（已弃用）

```
sync-data/
├── sync_data/          # 源代码
├── main.py            # 脚本
├── test_*.py          # 测试
├── pyproject.toml     # 配置
└── README.md          # 文档
```

### 新结构（推荐）

```
assistant-tools/
├── README.md              # 工具集总览
├── docs/                  # 全局文档
│   ├── DEVELOPMENT.md
│   ├── CONTRIBUTING.md
│   └── ARCHITECTURE.md
│
└── tools/                 # 工具目录
    └── sync-kb-to-qdrant/ # 知识库同步工具
        ├── README.md
        ├── pyproject.toml
        ├── .env.example
        ├── src/           # 源代码（原 sync_data/）
        ├── scripts/       # 脚本（原根目录的 *.py）
        └── tests/         # 测试（原根目录的 test_*.py）
```

## 🚀 迁移步骤

### 步骤 1: 备份现有工作（如需要）

```bash
# 如果你有本地修改，先提交或备份
git status
git add .
git commit -m "backup: 迁移前的备份"
```

### 步骤 2: 更新工作目录

所有命令现在需要在工具目录中执行：

```bash
# 旧方式（已弃用）
cd sync-data
python main.py --check

# 新方式（推荐）
cd tools/sync-kb-to-qdrant
python scripts/main.py --check
```

### 步骤 3: 迁移环境变量

如果你有 `.env` 文件：

```bash
# 复制你的配置到新位置
cp .env tools/sync-kb-to-qdrant/.env

# 或者重新创建
cd tools/sync-kb-to-qdrant
cp .env.example .env
# 编辑 .env 文件
```

### 步骤 4: 重新安装依赖

```bash
cd tools/sync-kb-to-qdrant

# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 步骤 5: 更新脚本和自动化

如果你有自动化脚本或 cron 任务：

```bash
# 旧命令
cd /path/to/sync-data && python main.py --all

# 新命令
cd /path/to/assistant-tools/tools/sync-kb-to-qdrant && python scripts/main.py --all
```

### 步骤 6: 更新 Python 导入（如果你在其他项目中使用）

```python
# 旧导入（已弃用）
from sync_data.database import Database
from sync_data.qdrant_manager import QdrantManager

# 新导入（推荐）
import sys
sys.path.append('/path/to/assistant-tools/tools/sync-kb-to-qdrant')
from src.database import Database
from src.qdrant_manager import QdrantManager
```

## 📝 命令对照表

### 主要命令

| 旧命令 | 新命令 | 说明 |
|--------|--------|------|
| `python main.py --check` | `python scripts/main.py --check` | 检查环境 |
| `python main.py --all` | `python scripts/main.py --all` | 迁移所有数据 |
| `python check_database.py` | `python scripts/check_database.py` | 检查数据库 |
| `python test_query.py` | `python tests/test_query.py` | 查询测试 |
| `python upload_to_api.py` | `python tests/upload_to_api.py` | API 上传 |

### 安装命令

| 旧命令 | 新命令 | 说明 |
|--------|--------|------|
| `cd sync-data` | `cd tools/sync-kb-to-qdrant` | 进入工具目录 |
| `uv sync` | `uv sync` | 安装依赖（相同） |
| `pip install -e .` | `pip install -e .` | 开发模式安装（相同） |

## 🔧 故障排除

### 问题 1: 找不到模块

**错误**: `ModuleNotFoundError: No module named 'sync_data'`

**解决方案**:
```bash
# 确保在正确的目录
cd tools/sync-kb-to-qdrant

# 重新安装
uv sync
```

### 问题 2: 环境变量未生效

**错误**: 数据库连接失败

**解决方案**:
```bash
# 确认 .env 文件位置
ls tools/sync-kb-to-qdrant/.env

# 如果不存在，创建它
cd tools/sync-kb-to-qdrant
cp .env.example .env
# 编辑 .env 文件填入配置
```

### 问题 3: 模型缓存找不到

**错误**: 重新下载模型

**解决方案**:

模型缓存现在位于工具目录下：

```bash
# 如果你有现有的模型缓存，可以移动或复制
cp -r models_cache/ tools/sync-kb-to-qdrant/models_cache/

# 或者在 .env 中指定缓存路径
echo "HF_CACHE_DIR=../../models_cache" >> tools/sync-kb-to-qdrant/.env
```

### 问题 4: 旧文件仍然存在

**说明**: 为了安全，旧文件暂时保留

**清理方案**（确认新结构工作正常后）:

```bash
# 删除旧的源代码目录
rm -rf sync_data/

# 删除旧的脚本文件
rm main.py check_database.py cleanup_collection.py generate_embedding.py

# 删除旧的测试文件
rm test_*.py quick_test.py upload_to_api.py

# 删除旧的文档（已移动到工具目录）
rm 使用说明.txt QDRANT查询方案.md SAFETY_GUIDE.md
```

## 📚 新的工作流程

### 日常使用

```bash
# 1. 进入工具目录
cd tools/sync-kb-to-qdrant

# 2. 激活虚拟环境（如果需要）
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate      # Windows

# 3. 运行命令
python scripts/main.py --check
python scripts/main.py --all --model BAAI/bge-large-zh-v1.5
python tests/test_query.py
```

### 添加新工具

现在你可以轻松添加新工具：

```bash
# 创建新工具目录
mkdir -p tools/my-new-tool/{src,scripts,tests}

# 参考现有工具的结构
cp tools/sync-kb-to-qdrant/README.md tools/my-new-tool/
# 修改 README.md...
```

## 🎯 优势

新结构的优势：

1. **模块化** - 每个工具独立，互不干扰
2. **可扩展** - 轻松添加新工具
3. **清晰** - 明确的目录结构
4. **一致** - 统一的组织方式
5. **灵活** - 每个工具可以使用不同的技术栈

## 📞 获取帮助

如果遇到问题：

1. 查看 [快速开始](./QUICK_START.md)
2. 查看工具的 [README](./tools/sync-kb-to-qdrant/README.md)
3. 查看 [开发指南](./docs/DEVELOPMENT.md)
4. 创建 Issue

## ✅ 迁移检查清单

完成迁移后，检查：

- [ ] 能在新目录中运行命令
- [ ] 环境变量正确配置
- [ ] 依赖正确安装
- [ ] 测试通过
- [ ] 自动化脚本已更新
- [ ] 文档已更新（如有）

## 🗑️ 清理旧文件（可选）

确认新结构完全正常后，你可以清理旧文件。

参考上面的"问题 4: 旧文件仍然存在"章节。

---

**迁移完成后，你就可以享受新的工具集结构带来的便利了！** 🎉

