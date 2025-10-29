# 🚀 知识库数据同步工具

将PostgreSQL中的知识库数据同步到Qdrant向量数据库的Python工具。

## ⚡ 快速开始

```bash
# 1. 安装依赖
cd sync-data
uv sync
# 或使用 pip: pip install -r requirements.txt

# 2. 配置环境变量（创建 .env 文件）
# 复制下面的配置，填入你的数据库信息
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=your_database_name
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_SCHEMA=public
QDRANT_URL=http://localhost:6333

# 3. 检查环境
python main.py --check

# 4. 迁移数据（使用最佳中文模型）
python main.py --all --model BAAI/bge-large-zh-v1.5

# 或迁移单个公司
python main.py --company company_123 --model BAAI/bge-large-zh-v1.5
```

📖 **详细使用说明请查看 [启动指南.md](./启动指南.md)**

## ✨ 特性

- 🆓 **完全免费**: 使用开源本地嵌入模型，无API费用
- 🇨🇳 **中文优化**: 专门优化的中文语义理解模型
- ⚡ **高性能**: 批量处理和GPU加速支持
- 🔒 **数据安全**: 本地部署，数据不外传
- 📊 **完整监控**: 详细的迁移报告和进度跟踪

## 🛠️ 环境要求

- Python 3.11+
- PostgreSQL (源数据库)
- Qdrant (目标向量数据库)
- 可选: NVIDIA GPU (加速向量化)

## 📦 安装依赖

```bash
# 安装项目依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

## ⚙️ 环境配置

创建 `.env` 文件：

```env
# PostgreSQL数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=your_database_name
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_SCHEMA=public  # 重要！数据库Schema，默认为public

# Qdrant向量数据库配置
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=your_api_key  # 本地部署通常不需要

# 可选：模型缓存目录
# HF_CACHE_DIR=./models_cache
```

## 🧠 推荐的嵌入模型

| 模型 | 大小 | 性能 | 适用场景 |
|------|------|------|----------|
| `BAAI/bge-large-zh-v1.5` | ~1.3GB | 高 | 🏆 最佳中文效果，推荐使用 |
| `shibing624/text2vec-base-chinese` | ~400MB | 中 | ⚡ 速度快，平衡选择 |
| `paraphrase-multilingual-MiniLM-L12-v2` | ~470MB | 中低 | 💻 轻量级，CPU友好 |

## 🚀 使用方法

### 1. 检查环境配置

```bash
python main.py --check
```

### 2. 检查数据库表结构

```bash
python main.py --check-db
# 或直接运行
python check_database.py
```

### 3. 列出可用模型

```bash
python main.py --list-models
```

### 4. 查看数据库统计

```bash
python main.py --stats
```

### 5. 迁移指定公司

```bash
# 使用默认模型
python main.py --company company_123

# 使用指定模型
python main.py --company company_123 --model shibing624/text2vec-base-chinese
```

### 6. 迁移所有公司

```bash
# 使用默认模型
python main.py --all

# 使用轻量级模型
python main.py --all --model paraphrase-multilingual-MiniLM-L12-v2
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

## 🔍 查询测试

### 快速测试

```bash
# 交互式查询工具（推荐）
python test_query.py

# 命令行快速测试
python test_query.py "如何重置密码" "公司ID"
```

### Python 代码示例

```python
from sync_data.qdrant_manager import QdrantManager
from sync_data.embedding_service import LocalEmbeddingService

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

📖 **完整的查询方案请查看 [QDRANT查询方案.md](./QDRANT查询方案.md)**

## 📈 性能优化建议

### GPU加速
```bash
# 安装CUDA版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 模型选择策略
- **8GB+ GPU**: 使用 `BAAI/bge-large-zh-v1.5`
- **4GB GPU**: 使用 `shibing624/text2vec-base-chinese`
- **仅CPU**: 使用 `paraphrase-multilingual-MiniLM-L12-v2`

### 批处理优化
- 默认批大小: 32
- GPU内存充足时可增加到 64 或 128
- CPU环境建议降低到 16

## 🐛 故障排除

### 1. 数据库表不存在
```bash
# 检查数据库表结构
python main.py --check-db

# 常见原因和解决方案：
# - Schema配置错误：在.env中设置 DATABASE_SCHEMA=your_schema
# - 表名不匹配：确认是wechat-diplomat-api项目的数据库
# - 权限问题：确认数据库用户有访问权限
```

### 2. 模型下载失败
```bash
# 设置Hugging Face镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 3. 内存不足
```bash
# 使用更小的模型
python main.py --all --model paraphrase-multilingual-MiniLM-L12-v2
```

### 4. 连接超时
```bash
# 检查Qdrant服务状态
curl http://localhost:6333/collections
```

## 📋 项目结构

```
sync-data/
├── sync_data/              # 主要包
│   ├── __init__.py
│   ├── main.py            # 入口文件
│   ├── database.py        # PostgreSQL连接
│   ├── qdrant_manager.py  # Qdrant管理
│   ├── embedding_service.py # 嵌入服务
│   └── migrator.py        # 迁移逻辑
├── main.py                # 命令行入口
├── pyproject.toml         # 项目配置
├── .env                   # 环境变量
└── README.md             # 说明文档
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
