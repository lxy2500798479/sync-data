# 🔍 Qdrant 查询方案

## 📋 概述

本文档提供了使用 Qdrant 向量数据库进行语义搜索的多种方案，帮助你实现"用户说一句话，匹配对应知识"的功能。

## 🎯 使用场景

- **用户问题**: "如何重置密码？"
- **匹配知识库**: 从Qdrant中找到最相关的答案
- **返回结果**: 返回匹配的问题和答案

## 🚀 方案一：Python 测试查询（推荐快速测试）

### 交互式搜索

```bash
cd sync-data
python test_query.py
```

**使用步骤**:
1. 选择嵌入模型（推荐最佳中文模型）
2. 选择要查询的集合（公司）
3. 输入问题进行搜索
4. 查看匹配结果和相似度

### 命令行快速测试

```bash
# 基本用法
python test_query.py "如何重置密码" "公司ID"

# 使用指定模型
python test_query.py "如何重置密码" "公司ID" "BAAI/bge-large-zh-v1.5"
```

## 🔧 方案二：集成到 TypeScript 后端

### 1. 创建 Qdrant 查询服务

```typescript
// src/service/qdrant/qdrant-query.service.ts
import { QdrantClient } from '@qdrant/js-client-rest';
import { logger } from '@/utils/loki';

export class QdrantQueryService {
  private client: QdrantClient;
  
  constructor() {
    this.client = new QdrantClient({
      url: process.env.QDRANT_URL || 'http://localhost:6333',
      apiKey: process.env.QDRANT_API_KEY,
    });
  }

  /**
   * 搜索知识库
   */
  async searchKnowledge(
    companyId: string,
    question: string,
    embedding: number[],
    limit: number = 5,
    scoreThreshold: number = 0.5
  ) {
    try {
      const collectionName = `kb_${companyId}`;
      
      const results = await this.client.search(collectionName, {
        vector: embedding,
        limit,
        score_threshold: scoreThreshold,
        with_payload: true,
        with_vectors: false,
      });

      return results.map(result => ({
        score: result.score,
        payload: result.payload,
      }));
    } catch (error) {
      logger.error({ error, companyId }, '[Qdrant] 搜索失败');
      return [];
    }
  }
}

export const qdrantQueryService = new QdrantQueryService();
```

### 2. 创建嵌入服务（调用 Python 模型）

```typescript
// src/service/qdrant/embedding.service.ts
import { exec } from 'child_process';
import { promisify } from 'util';
import { logger } from '@/utils/loki';

const execAsync = promisify(exec);

export class EmbeddingService {
  private modelName: string;

  constructor(modelName: string = 'BAAI/bge-large-zh-v1.5') {
    this.modelName = modelName;
  }

  /**
   * 生成文本的向量嵌入
   */
  async encode(question: string): Promise<number[]> {
    try {
      // 调用 Python 脚本生成向量
      const scriptPath = 'D:/WORK/assistant/sync-data/generate_embedding.py';
      const command = `python "${scriptPath}" "${question}" "${this.modelName}"`;
      
      const { stdout } = await execAsync(command);
      const embedding = JSON.parse(stdout);
      
      return embedding;
    } catch (error) {
      logger.error({ error, question }, '[Embedding] 生成向量失败');
      throw error;
    }
  }
}

export const embeddingService = new EmbeddingService();
```

### 3. 修改知识库查询服务

```typescript
// src/service/knowledgebase/knowledgebase-query.service.ts
import { qdrantQueryService } from '../qdrant/qdrant-query.service';
import { embeddingService } from '../qdrant/embedding.service';

export class KnowledgebaseQueryService {
  /**
   * 使用 Qdrant 向量搜索
   */
  public async askWithQdrant(question: string, companyId?: string) {
    if (!companyId) {
      return { answer: '缺少公司ID' };
    }

    try {
      // 1. 生成问题向量
      const embedding = await embeddingService.encode(question);
      
      // 2. 搜索 Qdrant
      const results = await qdrantQueryService.searchKnowledge(
        companyId,
        question,
        embedding,
        5,
        0.5
      );

      if (results.length === 0) {
        return { answer: '未找到相关答案' };
      }

      // 3. 获取最佳匹配
      const bestMatch = results[0];
      const payload = bestMatch.payload;

      // 4. 提取答案
      const answers = payload.answers || [];
      if (answers.length === 0) {
        return { answer: '该问题暂无答案' };
      }

      const answer = answers[0];
      
      // 5. 返回答案
      if (answer.type === 'TEXT') {
        return { 
          type: 'TEXT', 
          content: answer.content.text 
        };
      } else if (answer.type === 'MATERIAL') {
        return { 
          type: 'MATERIAL', 
          content: { materialId: answer.content.materialId } 
        };
      }

      return { answer: '未知答案类型' };
    } catch (error) {
      logger.error({ error, question }, '[KnowledgeBase] Qdrant查询失败');
      return { answer: '查询失败' };
    }
  }
}
```

## 🧪 方案三：HTTP API 测试

### 1. 创建 Python API 服务

```python
# sync-data/api_server.py
from flask import Flask, request, jsonify
from sync_data.qdrant_manager import QdrantManager
from sync_data.embedding_service import LocalEmbeddingService

app = Flask(__name__)
qdrant = QdrantManager()
embedding = LocalEmbeddingService('BAAI/bge-large-zh-v1.5')

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    question = data.get('question')
    company_id = data.get('company_id')
    
    if not question or not company_id:
        return jsonify({'error': '缺少参数'}), 400
    
    try:
        # 生成向量
        vector = embedding.encode_single(question)
        
        # 搜索
        collection_name = f"kb_{company_id}"
        results = qdrant.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=5,
            score_threshold=0.5
        )
        
        # 格式化结果
        formatted_results = []
        for result in results:
            formatted_results.append({
                'score': result.score,
                'question': result.payload.get('current_question'),
                'intent': result.payload.get('intent_name'),
                'answer': result.payload.get('answers', [{}])[0].get('content', {}).get('text', '')
            })
        
        return jsonify({
            'success': True,
            'results': formatted_results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8888)
```

### 2. 启动 API 服务

```bash
cd sync-data
python api_server.py
```

### 3. 调用 API

```bash
curl -X POST http://localhost:8888/search \
  -H "Content-Type: application/json" \
  -d '{
    "question": "如何重置密码",
    "company_id": "01982734-15e4-7edb-92e4-fd046e92dd97"
  }'
```

## 📊 性能对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Python测试脚本 | 简单快速，易于调试 | 需要手动操作 | 开发测试阶段 |
| TypeScript集成 | 统一架构，性能好 | 需要调用Python服务 | 生产环境 |
| HTTP API | 灵活，可独立部署 | 网络开销 | 微服务架构 |

## 💡 推荐方案

### 开发阶段
使用 **方案一**（Python测试脚本）快速验证数据质量和匹配效果

### 生产环境
使用 **方案二**（TypeScript集成）：
1. 在 TypeScript 中调用 Python API
2. 或者直接使用 Python HTTP API 服务

## 🔍 查询优化建议

### 1. 调整相似度阈值

```typescript
// 高精度（严格匹配）
scoreThreshold: 0.7

// 平衡（推荐）
scoreThreshold: 0.5

// 宽松（尽可能返回结果）
scoreThreshold: 0.3
```

### 2. 限制返回数量

```typescript
// 只返回最佳匹配
limit: 1

// 返回Top 3（推荐）
limit: 3

// 返回Top 5（用于排序）
limit: 5
```

### 3. 添加过滤条件

```typescript
// 只搜索启用的意图
const filter = {
  must: [
    {
      key: 'metadata.intentIsActive',
      match: { value: true }
    }
  ]
};
```

## 📝 完整使用流程

```bash
# 1. 迁移数据到 Qdrant
python main.py --all --model BAAI/bge-large-zh-v1.5

# 2. 测试查询
python test_query.py

# 3. 集成到后端（根据需求选择方案）

# 4. 监控和优化
python main.py --stats
```

## 🎯 总结

- **测试**: 使用 `test_query.py` 交互式查询
- **集成**: 在 TypeScript 中调用 Python 服务
- **优化**: 调整阈值和过滤条件提升准确度
- **监控**: 定期检查 Qdrant 数据统计

