# 🏗️ 架构说明

本文档描述 Assistant Tools 工具集的整体架构设计和组织原则。

## 📋 目录

- [设计理念](#设计理念)
- [项目结构](#项目结构)
- [工具架构](#工具架构)
- [扩展性设计](#扩展性设计)

## 🎯 设计理念

### 核心原则

Assistant Tools 遵循以下设计原则：

1. **独立性** (Independence)
   - 每个工具是独立的、自包含的单元
   - 工具之间无直接依赖
   - 可以单独安装和使用

2. **简洁性** (Simplicity)
   - 每个工具专注于解决一个具体问题
   - 避免过度设计和不必要的复杂性
   - 清晰的 API 和命令行接口

3. **一致性** (Consistency)
   - 统一的目录结构
   - 统一的文档格式
   - 统一的配置方式

4. **可维护性** (Maintainability)
   - 清晰的代码结构
   - 完整的文档
   - 充分的测试覆盖

5. **可扩展性** (Extensibility)
   - 易于添加新工具
   - 支持自定义配置
   - 灵活的插件机制（未来）

## 📂 项目结构

### 顶层目录

```
assistant-tools/
├── README.md              # 工具集总览和索引
├── .gitignore            # 全局忽略规则
│
├── tools/                # 工具集合目录
│   ├── tool-1/          # 工具 1
│   ├── tool-2/          # 工具 2
│   └── tool-n/          # 工具 N
│
└── docs/                 # 全局文档
    ├── DEVELOPMENT.md   # 开发指南
    ├── CONTRIBUTING.md  # 贡献指南
    └── ARCHITECTURE.md  # 本文件
```

### 设计意图

#### `tools/` 目录
- **用途**: 存放所有独立工具
- **特点**: 
  - 每个子目录是一个完整的工具
  - 工具间平级关系，无层级依赖
  - 支持不同编程语言

#### `docs/` 目录
- **用途**: 存放跨工具的全局文档
- **内容**:
  - 开发规范
  - 贡献指南
  - 架构说明
  - 最佳实践

## 🛠️ 工具架构

### 标准工具结构

每个工具遵循统一的目录结构：

```
tools/<tool-name>/
├── README.md              # ⭐ 工具说明文档
├── .env.example          # 环境变量模板
├── .gitignore           # 工具特定忽略规则
│
├── pyproject.toml       # Python 配置
├── package.json         # 或 Node.js 配置
│
├── src/                  # ⭐ 源代码目录
│   ├── __init__.py      # Python 包初始化
│   ├── main.py          # 主入口
│   ├── config.py        # 配置管理
│   ├── utils.py         # 工具函数
│   └── ...              # 其他模块
│
├── scripts/              # 可执行脚本目录
│   ├── run.py           # 主执行脚本
│   ├── setup.py         # 安装脚本
│   └── ...              # 其他脚本
│
├── tests/                # ⭐ 测试目录
│   ├── __init__.py
│   ├── test_main.py
│   └── ...
│
└── docs/                 # 工具特定文档
    ├── USAGE.md         # 详细使用说明
    ├── API.md           # API 文档
    └── ...
```

### 模块职责

#### `src/` - 核心代码
- **main.py**: 程序入口，处理命令行参数
- **config.py**: 配置加载和验证
- **utils.py**: 通用工具函数
- **[feature].py**: 具体功能模块

#### `scripts/` - 可执行脚本
- **run.py**: 主要的执行脚本
- **setup.py**: 环境设置脚本
- **migrate.py**: 迁移脚本（如适用）

#### `tests/` - 测试代码
- 单元测试
- 集成测试
- 端到端测试

## 🔌 工具类型

### 按功能分类

```
tools/
├── data-tools/           # 数据处理工具
│   ├── sync-kb-to-qdrant/
│   └── data-migration/
│
├── dev-tools/            # 开发工具
│   ├── api-tester/
│   └── log-analyzer/
│
└── ops-tools/            # 运维工具
    ├── deployment-scripts/
    └── monitoring/
```

### 按语言分类

#### Python 工具

**特点**:
- 使用 `pyproject.toml` 管理依赖
- 使用 `uv` 或 `pip` 安装
- 适合数据处理、脚本自动化

**配置示例**:
```toml
[project]
name = "tool-name"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
]

[project.scripts]
tool-name = "src.main:main"
```

#### TypeScript/Node.js 工具

**特点**:
- 使用 `package.json` 管理依赖
- 使用 `bun` 或 `npm` 安装
- 适合 API 服务、前端工具

**配置示例**:
```json
{
  "name": "tool-name",
  "version": "0.1.0",
  "type": "module",
  "main": "src/main.ts",
  "scripts": {
    "start": "bun run src/main.ts",
    "test": "bun test"
  },
  "dependencies": {
    "hono": "^4.0.0"
  }
}
```

## 🔄 数据流

### 典型工具的数据流

```
输入源 → 配置加载 → 数据处理 → 输出/存储
  ↓         ↓            ↓            ↓
 CLI      .env        核心逻辑      文件/DB
 文件    config.py    main.py      API
 API     环境变量      utils.py     日志
```

### 示例：sync-kb-to-qdrant

```
PostgreSQL → 配置 → 数据获取 → 向量化 → Qdrant
    ↓         ↓        ↓          ↓        ↓
  源数据     .env   database.py embedding qdrant.py
  表结构   连接信息  SQL查询    本地模型  批量写入
```

## 🔐 配置管理

### 配置层级

1. **默认配置** - 代码中的默认值
2. **环境变量** - `.env` 文件
3. **命令行参数** - 运行时覆盖

### 优先级

```
命令行参数 > 环境变量 > 默认配置
```

### 配置示例

```python
# config.py
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 默认配置
    DATABASE_HOST = getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = int(getenv("DATABASE_PORT", "5432"))
    
    # 必需配置（无默认值）
    DATABASE_NAME = getenv("DATABASE_NAME")
    
    @classmethod
    def validate(cls):
        if not cls.DATABASE_NAME:
            raise ValueError("DATABASE_NAME is required")
```

## 📊 依赖管理

### 原则

1. **最小化依赖** - 只添加必需的依赖
2. **锁定版本** - 使用锁文件确保可重现
3. **定期更新** - 保持依赖的安全性

### Python 依赖

```toml
[project]
dependencies = [
    "requests>=2.31.0,<3.0.0",  # 指定版本范围
    "pydantic>=2.0.0",          # 主要版本
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
]
```

### TypeScript 依赖

```json
{
  "dependencies": {
    "hono": "^4.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
```

## 🧪 测试策略

### 测试层级

```
        /\
       /  \
      /E2E \         端到端测试 (少量)
     /------\
    /  集成  \       集成测试 (中等)
   /----------\
  /   单元测试  \    单元测试 (大量)
 /--------------\
```

### 测试覆盖目标

- **单元测试**: 80%+ 代码覆盖
- **集成测试**: 关键流程覆盖
- **端到端测试**: 主要场景覆盖

## 🚀 扩展性设计

### 添加新工具

新工具可以：
1. 使用任何编程语言
2. 有自己的依赖管理
3. 定义自己的配置格式
4. 独立测试和部署

**要求**:
- 遵循标准目录结构
- 提供完整的 README.md
- 包含 `.env.example`（如需要）

### 共享代码（未来）

如果多个工具需要共享代码，可以考虑：

```
assistant-tools/
├── shared/              # 共享代码库
│   ├── python/         # Python 公共模块
│   │   ├── logger.py
│   │   └── utils.py
│   └── typescript/     # TypeScript 公共模块
│       └── utils.ts
│
└── tools/
    └── ...
```

### 插件系统（规划中）

未来可能支持插件机制：

```python
# 工具定义
class Tool:
    name: str
    version: str
    
    def run(self, args): ...
    def configure(self, config): ...

# 插件注册
register_tool(MyTool())
```

## 📈 性能考虑

### 原则

1. **按需加载** - 延迟导入重型依赖
2. **批量处理** - 减少 I/O 操作次数
3. **并发处理** - 利用多线程/异步
4. **缓存结果** - 避免重复计算

### 示例

```python
# ✅ 按需加载
def process_large_file():
    import pandas as pd  # 只在需要时导入
    df = pd.read_csv("large_file.csv")
    # ...

# ✅ 批量处理
def process_items(items):
    batch_size = 100
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        process_batch(batch)
```

## 🔍 监控和日志

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息（默认）
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志格式

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Processing started")
```

## 📖 文档架构

### 文档层级

```
全局文档 (docs/)          # 跨工具的通用文档
    ↓
工具文档 (tools/*/README.md)  # 工具使用文档
    ↓
代码文档 (docstrings)     # 函数/类文档
```

### 文档同步

- 代码变更 → 更新 docstrings
- 功能变更 → 更新 README
- 架构变更 → 更新 ARCHITECTURE.md

## 🔮 未来规划

### 短期（1-3 个月）

- [ ] 添加更多实用工具
- [ ] 改进文档和示例
- [ ] 建立 CI/CD 流程

### 中期（3-6 个月）

- [ ] 引入共享代码库
- [ ] 统一配置管理
- [ ] 性能优化

### 长期（6-12 个月）

- [ ] 插件系统
- [ ] Web 管理界面
- [ ] 容器化部署

## 📚 参考资料

### 设计模式

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [12-Factor App](https://12factor.net/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

### 最佳实践

- [Python 项目结构](https://docs.python-guide.org/writing/structure/)
- [Node.js 最佳实践](https://github.com/goldbergyoni/nodebestpractices)

---

**架构是演进的，欢迎反馈和建议！** 🚀


