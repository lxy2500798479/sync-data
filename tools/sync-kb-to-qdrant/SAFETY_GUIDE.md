# 🛡️ 数据安全指南

## 重要声明

本迁移工具的数据安全保证：

### ✅ PostgreSQL - 100% 安全
- **只进行读取操作**
- 使用 `SELECT` 查询获取数据
- **绝对不会修改、删除任何PostgreSQL数据**
- 即使程序出错也不会影响源数据

### ⚠️ Qdrant - 会写入数据，但智能处理

#### 集合创建策略
```python
# 如果集合已存在，跳过创建
if collection_name in existing_names:
    print(f"📋 集合 {collection_name} 已存在，跳过创建")
    return True
```

#### 数据插入策略 - 使用 UPSERT
```python
# 使用upsert操作，不会丢失现有数据
self.client.upsert(
    collection_name=collection_name,
    points=batch,
    wait=True
)
```

**UPSERT 操作说明：**
- 如果向量点ID不存在 → 插入新数据
- 如果向量点ID已存在 → 更新现有数据
- **不会删除其他现有数据**

#### 向量点ID格式
```python
# ID格式：公司ID_意图ID_问题索引
point_id = f"{company_id}_{intent_id}_{question_index}"
# 例如：company_123_intent_456_0
```

## 🔍 具体会发生什么

### 第一次运行
```
Qdrant中：
集合 kb_company_123: 空
           ↓ 运行迁移
集合 kb_company_123: [新增100个向量点]
```

### 第二次运行（数据有更新）
```
Qdrant中：
集合 kb_company_123: [现有100个向量点]
           ↓ 运行迁移
集合 kb_company_123: [更新的100个向量点] （相同ID会更新，不同ID会保留）
```

### 多公司场景
```
Qdrant中：
集合 kb_company_123: [公司123的数据] ← 不受影响
集合 kb_company_456: [公司456的数据] ← 不受影响
           ↓ 只迁移公司789
集合 kb_company_789: [新增公司789的数据] ← 新创建
```

## 🚨 潜在风险和预防

### 风险1：覆盖现有向量
**场景：** 如果同一公司的数据被多次迁移
**结果：** 相同ID的向量点会被更新为最新数据
**预防：** 
- 检查 `sync_version` 字段避免重复迁移
- 备份重要的Qdrant数据

### 风险2：磁盘空间
**场景：** 大量数据迁移可能占用较多磁盘空间
**预防：** 
- 运行前检查磁盘空间
- 使用 `--stats` 预估数据量

### 风险3：网络中断
**场景：** 长时间迁移过程中网络中断
**结果：** 部分数据已迁移，部分未完成
**预防：** 
- 支持断点续传（基于向量点ID检查）
- 分批处理，减少单次失败影响

## 🛠️ 安全使用建议

### 1. 首次使用 - 测试模式
```bash
# 先测试连接
python main.py --check

# 查看数据统计
python main.py --stats

# 迁移单个小公司测试
python main.py --company test_company_id
```

### 2. 备份现有数据（如果重要）
```bash
# 导出现有Qdrant集合（可选）
curl -X GET "http://localhost:6333/collections" > qdrant_backup.json
```

### 3. 监控迁移过程
```bash
# 使用详细日志模式
python main.py --all --model shibing624/text2vec-base-chinese 2>&1 | tee migration.log
```

### 4. 验证迁移结果
```bash
# 迁移完成后再次检查统计
python main.py --stats
```

## 📞 紧急情况处理

### 如果需要完全重置某个集合
```python
from sync_data.qdrant_manager import QdrantManager

qdrant = QdrantManager()
# 删除集合（谨慎操作！）
qdrant.delete_collection("kb_company_123")
```

### 如果需要清理空集合
```python
# 自动清理空集合
qdrant.cleanup_empty_collections()
```

## ✅ 总结

- **PostgreSQL**: 100% 安全，只读操作
- **Qdrant**: 智能写入，不会丢失现有数据
- **建议**: 首次使用先测试小数据集
- **风险**: 极低，主要是磁盘空间和网络稳定性

**结论：这个操作是安全的，不会破坏任何现有数据！**
