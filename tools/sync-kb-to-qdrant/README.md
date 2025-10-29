# 📊 知识库同步工具 (sync-kb-to-qdrant)

将 PostgreSQL 中的知识库数据同步到 Qdrant 向量数据库的 Python 工具。

> 💡 **提示**: 这是 [Assistant Tools](../../README.md) 工具集的一部分

## ✨ 特性

- 🆓 **完全免费**: 使用开源本地嵌入模型，无 API 费用
- 🇨🇳 **中文优化**: 专门优化的中文语义理解模型
- ⚡ **高性能**: 批量处理和 GPU 加速支持
- 🔒 **数据安全**: 本地部署，数据不外传
- 📊 **完整监控**: 详细的迁移报告和进度跟踪

## 🛠️ 环境要求

- Python 3.11+
- PostgreSQL (源数据库)
- Qdrant (目标向量数据库)
- 可选: NVIDIA GPU (加速向量化)

## ⚡ 快速开始

### 1. 安装依赖

```bash
cd tools/sync-kb-to-qdrant
uv sync
# 或使用 pip: pip install -e .
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填入数据库信息
```

### 3. 检查环境

```bash
python scripts/main.py --check
```

### 4. 开始迁移

```bash
# 使用最佳中文模型迁移所有数据
python scripts/main.py --all --model BAAI/bge-large-zh-v1.5

# 或迁移单个公司
python scripts/main.py --company company_123 --model BAAI/bge-large-zh-v1.5
```

## 🧠 推荐的嵌入模型

| 模型 | 大小 | 性能 | 适用场景 |
|------|------|------|----------|
| `BAAI/bge-large-zh-v1.5` | ~1.3GB | 高 | 🏆 最佳中文效果，推荐使用 |
| `shibing624/text2vec-base-chinese` | ~400MB | 中 | ⚡ 速度快，平衡选择 |
| `paraphrase-multilingual-MiniLM-L12-v2` | ~470MB | 中低 | 💻 轻量级，CPU 友好 |

## 📖 详细使用

### 命令行选项

```bash
# 检查环境配置
python scripts/main.py --check

# 检查数据库表结构
python scripts/main.py --check-db
# 或
python scripts/check_database.py

# 列出可用模型
python scripts/main.py --list-models

# 查看数据库统计
python scripts/main.py --stats

# 迁移指定公司
python scripts/main.py --company company_123
python scripts/main.py --company company_123 --model shibing624/text2vec-base-chinese

# 迁移所有公司
python scripts/main.py --all
python scripts/main.py --all --model paraphrase-multilingual-MiniLM-L12-v2
```

### 查询测试

```bash
# 交互式查询工具（推荐）
python tests/test_query.py

# 命令行快速测试
python tests/test_query.py "如何重置密码" "company_123"

# 快速测试
python tests/quick_test.py
```

### Python 代码示例

```python
from src.qdrant_manager import QdrantManager
from src.embedding_service import LocalEmbeddingService

# 初始化
qdrant = QdrantManager()
embedding = LocalEmbeddingService('BAAI/bge-large-zh-v1.5')

# 查询
question = "如何重置密码"
vector = embedding.encode_single(question)
results = qdrant.search("kb_company_123", vector, limit=5)

for result in results:
    print(f"匹配问题: {result.payload['current_question']}")
    print(f"置信度: {result.score}")
    print(f"答案: {result.payload['answers'][0]['content']}")
```

## 📊 数据结构

迁移后的向量点包含以下核心字段：

```json
{
  "company_id": "公司ID",
  "intent_id": "意图ID", 
  "intent_name": "意图名称",
  "current_question": "当前标准问题",
  "all_standard_questions": ["所有标准问题列表"],
  "answers": [{"答案数据"}],
  "popularity_tier": "HOT|WARM|COLD",
  "embedding_model": "使用的嵌入模型",
  "vector_quality": "向量质量分数"
}
```

## 📈 性能优化

### GPU 加速

```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 模型选择策略

- **8GB+ GPU**: 使用 `BAAI/bge-large-zh-v1.5`
- **4GB GPU**: 使用 `shibing624/text2vec-base-chinese`
- **仅 CPU**: 使用 `paraphrase-multilingual-MiniLM-L12-v2`

### 批处理优化

- 默认批大小: 32
- GPU 内存充足时可增加到 64 或 128
- CPU 环境建议降低到 16

## 🐛 故障排除

### 1. 数据库表不存在

```bash
# 检查数据库表结构
python scripts/main.py --check-db

# 常见原因和解决方案：
# - Schema 配置错误：在 .env 中设置 DATABASE_SCHEMA=your_schema
# - 表名不匹配：确认是 wechat-diplomat-api 项目的数据库
# - 权限问题：确认数据库用户有访问权限
```

### 2. 模型下载失败

```bash
# 设置 Hugging Face 镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 3. 内存不足

```bash
# 使用更小的模型
python scripts/main.py --all --model paraphrase-multilingual-MiniLM-L12-v2
```

### 4. 连接超时

```bash
# 检查 Qdrant 服务状态
curl http://localhost:6333/collections
```

## 📋 项目结构

```
sync-kb-to-qdrant/
├── README.md              # 本文件
├── .env.example          # 环境变量模板
├── pyproject.toml        # 项目配置
├── uv.lock              # 依赖锁定
│
├── src/                  # 源代码
│   ├── __init__.py
│   ├── main.py          # 核心入口
│   ├── database.py      # PostgreSQL 连接
│   ├── qdrant_manager.py # Qdrant 管理
│   ├── embedding_service.py # 嵌入服务
│   └── migrator.py      # 迁移逻辑
│
├── scripts/              # 可执行脚本
│   ├── main.py          # 主入口脚本
│   ├── check_database.py # 数据库检查
│   ├── cleanup_collection.py # 清理集合
│   └── generate_embedding.py # 生成嵌入
│
└── tests/                # 测试和工具
    ├── test_query.py    # 查询测试
    ├── test_upload.py   # 上传测试
    ├── quick_test.py    # 快速测试
    └── upload_to_api.py # API 上传工具
```

## 📚 更多文档

- [QDRANT查询方案.md](./QDRANT查询方案.md) - 详细的查询方案和最佳实践
- [SAFETY_GUIDE.md](./SAFETY_GUIDE.md) - 安全使用指南
- [使用说明.txt](./使用说明.txt) - API 上传工具使用说明

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**返回 [工具集主页](../../README.md)**
