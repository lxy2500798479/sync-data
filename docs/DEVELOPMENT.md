# 🛠️ 开发指南

本指南帮助开发者快速上手 Assistant Tools 工具集的开发工作。

## 📋 目录

- [环境准备](#环境准备)
- [开发规范](#开发规范)
- [添加新工具](#添加新工具)
- [测试指南](#测试指南)
- [发布流程](#发布流程)

## 🚀 环境准备

### 基础工具

1. **Git** - 版本控制
2. **代码编辑器** - 推荐 VS Code、PyCharm 或 Cursor
3. **语言环境**:
   - Python 3.11+ (Python 工具)
   - Node.js 18+ 或 Bun (JavaScript/TypeScript 工具)

### Python 开发环境

```bash
# 安装 uv (推荐的 Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv

# 创建虚拟环境
cd tools/<your-tool>
uv sync
```

### TypeScript 开发环境

```bash
# 安装 Bun (推荐)
curl -fsSL https://bun.sh/install | bash

# 或使用 npm
npm install -g npm@latest

# 安装依赖
cd tools/<your-tool>
bun install  # 或 npm install
```

## 📐 开发规范

### 代码风格

#### Python

遵循 **PEP 8** 规范：

```python
# ✅ 好的示例
def process_data(input_data: dict, batch_size: int = 32) -> list:
    """
    处理输入数据并返回结果列表。
    
    Args:
        input_data: 输入数据字典
        batch_size: 批处理大小，默认 32
        
    Returns:
        处理后的数据列表
    """
    results = []
    for item in input_data.items():
        results.append(process_item(item))
    return results

# ❌ 不好的示例
def processData(inputData,batchSize=32):
    results=[]
    for item in inputData.items():
        results.append(process_item(item))
    return results
```

**关键规则**:
- 使用 4 空格缩进（不使用 Tab）
- 函数和变量使用 `snake_case`
- 类使用 `PascalCase`
- 常量使用 `UPPER_SNAKE_CASE`
- 添加类型注解
- 编写文档字符串

#### TypeScript

遵循 **ESLint + Prettier** 规范：

```typescript
// ✅ 好的示例
interface UserData {
  userId: string;
  userName: string;
  email?: string;
}

export function processUser(data: UserData): Promise<void> {
  // 处理逻辑
  return Promise.resolve();
}

// ❌ 不好的示例
function processUser(data) {
  return new Promise((resolve) => {
    resolve();
  });
}
```

**关键规则**:
- 使用 2 空格缩进
- 使用 `camelCase` 命名
- 接口和类使用 `PascalCase`
- 始终使用类型注解
- 优先使用 `const` 和 `let`，避免 `var`

### 目录结构规范

每个工具应遵循以下结构：

```
tools/<tool-name>/
├── README.md              # ⭐ 必需 - 工具说明
├── .env.example           # 环境变量模板（如需要）
├── .gitignore            # 工具特定的忽略规则
│
├── pyproject.toml        # Python 项目配置
├── package.json          # 或 Node.js 项目配置
├── uv.lock / bun.lockb   # 依赖锁定文件
│
├── src/                   # ⭐ 必需 - 源代码
│   ├── __init__.py       # Python 包初始化
│   └── main.py           # 主要逻辑
│
├── scripts/               # 可执行脚本
│   └── run.py
│
├── tests/                 # ⭐ 推荐 - 测试文件
│   └── test_main.py
│
└── docs/                  # 额外文档（可选）
    └── USAGE.md
```

## 🆕 添加新工具

### 步骤 1: 创建目录结构

```bash
cd tools
mkdir -p <your-tool-name>/{src,scripts,tests,docs}
cd <your-tool-name>
```

### 步骤 2: 初始化项目

**Python 工具**:

```bash
# 创建 pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "your-tool-name"
version = "0.1.0"
description = "工具描述"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    # 添加依赖
]

[project.scripts]
your-tool = "src.main:main"
EOF

# 初始化环境
uv sync
```

**TypeScript 工具**:

```bash
# 初始化项目
bun init
# 或
npm init -y

# 安装 TypeScript
bun add -d typescript @types/node
```

### 步骤 3: 编写代码

创建基本的入口文件：

**Python** (`src/main.py`):

```python
#!/usr/bin/env python3
"""
工具名称 - 简短描述
"""
import argparse
import sys
from typing import Optional


def main(args: Optional[list] = None) -> int:
    """主入口函数"""
    parser = argparse.ArgumentParser(description="工具描述")
    parser.add_argument("--version", action="version", version="0.1.0")
    
    parsed_args = parser.parse_args(args)
    
    # 你的逻辑
    print("Hello from your tool!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**TypeScript** (`src/main.ts`):

```typescript
#!/usr/bin/env bun

/**
 * 工具名称 - 简短描述
 */

export async function main(): Promise<number> {
  console.log('Hello from your tool!');
  return 0;
}

// 如果直接运行此文件
if (import.meta.main) {
  process.exit(await main());
}
```

### 步骤 4: 编写 README

```markdown
# 工具名称

简短描述工具的用途。

## 功能

- 功能 1
- 功能 2

## 快速开始

\`\`\`bash
cd tools/your-tool-name
# 安装依赖
# 运行命令
\`\`\`

## 使用示例

\`\`\`bash
# 示例命令
\`\`\`

## 配置

说明需要的环境变量和配置。

## 故障排除

常见问题和解决方案。
```

### 步骤 5: 更新主 README

在根目录的 `README.md` 中添加你的工具：

```markdown
### N. 🎯 你的工具名称

简短描述

- **语言**: Python/TypeScript
- **功能**: 
  - 功能列表
- **文档**: [📖 详细文档](./tools/your-tool-name/README.md)
```

## 🧪 测试指南

### Python 测试

使用 `pytest` 编写测试：

```python
# tests/test_main.py
import pytest
from src.main import main


def test_main_returns_zero():
    """测试主函数返回 0"""
    result = main([])
    assert result == 0


def test_version_argument():
    """测试 --version 参数"""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
```

运行测试：

```bash
# 安装 pytest
uv add --dev pytest

# 运行测试
pytest
```

### TypeScript 测试

使用 `bun:test` 或 `jest`：

```typescript
// tests/main.test.ts
import { describe, expect, test } from 'bun:test';
import { main } from '../src/main';

describe('main', () => {
  test('returns 0', async () => {
    const result = await main();
    expect(result).toBe(0);
  });
});
```

运行测试：

```bash
bun test
# 或
npm test
```

## 📦 依赖管理

### 添加依赖

**Python**:

```bash
# 生产依赖
uv add package-name

# 开发依赖
uv add --dev package-name

# 指定版本
uv add "package-name>=1.0.0,<2.0.0"
```

**TypeScript**:

```bash
# 生产依赖
bun add package-name

# 开发依赖
bun add -d package-name

# 指定版本
bun add package-name@^1.0.0
```

### 更新依赖

```bash
# Python
uv sync --upgrade

# TypeScript
bun update
```

## 🔍 代码审查清单

提交代码前检查：

- [ ] 代码遵循风格规范
- [ ] 添加了必要的注释和文档字符串
- [ ] 编写了测试用例
- [ ] 测试全部通过
- [ ] 更新了 README.md
- [ ] 添加了 .env.example（如需要）
- [ ] 没有提交敏感信息（密码、密钥等）
- [ ] 代码可以在干净的环境中运行

## 🚀 发布流程

### 1. 版本更新

更新版本号（遵循 [语义化版本](https://semver.org/lang/zh-CN/)）：

- **主版本**（Major）: 不兼容的 API 变更
- **次版本**（Minor）: 向后兼容的功能新增
- **修订版本**（Patch）: 向后兼容的问题修复

### 2. 更新 CHANGELOG

记录变更内容：

```markdown
## [1.1.0] - 2025-10-29

### Added
- 新增功能 X

### Changed
- 改进功能 Y

### Fixed
- 修复问题 Z
```

### 3. 提交代码

```bash
git add .
git commit -m "feat(tool-name): 添加新功能"
git push origin main
```

### 4. 创建标签（可选）

```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

## 💡 最佳实践

### 1. 错误处理

```python
# ✅ 好的错误处理
try:
    result = dangerous_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    return None
except Exception as e:
    logger.exception("Unexpected error occurred")
    raise
```

### 2. 日志记录

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("操作成功")
logger.warning("警告信息")
logger.error("错误信息")
```

### 3. 配置管理

使用环境变量或配置文件：

```python
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = getenv("DATABASE_URL", "postgresql://localhost/db")
API_KEY = getenv("API_KEY")  # 必需的配置

if not API_KEY:
    raise ValueError("API_KEY environment variable is required")
```

### 4. 性能优化

- 使用批处理减少 I/O 操作
- 合理使用缓存
- 避免过度嵌套的循环
- 使用生成器处理大数据

## 🔗 有用的资源

### Python

- [PEP 8 风格指南](https://peps.python.org/pep-0008/)
- [Python 类型注解](https://docs.python.org/3/library/typing.html)
- [pytest 文档](https://docs.pytest.org/)

### TypeScript

- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [Bun 文档](https://bun.sh/docs)
- [ESLint 规则](https://eslint.org/docs/latest/rules/)

## 🤝 获取帮助

- 查看现有工具的代码作为参考
- 阅读工具的 README.md
- 在仓库中创建 Issue

---

**祝开发愉快！** 🎉


