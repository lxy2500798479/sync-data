#!/usr/bin/env python3
"""
快速测试脚本 - 自动检测并测试查询
"""

import sys
from sync_data.qdrant_manager import QdrantManager
from sync_data.embedding_service import LocalEmbeddingService

# 向量维度到模型的映射
DIM_TO_MODEL = {
    1024: 'BAAI/bge-large-zh-v1.5',  # 或 'tencent/Youtu-Embedding'
    768: 'shibing624/text2vec-base-chinese',
    384: 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
}

def quick_test(question: str, collection_index: int = 2):
    """快速测试查询"""
    print("=" * 60)
    print("🔍 Qdrant 快速查询测试")
    print("=" * 60)
    print()
    
    # 连接 Qdrant
    print("🔗 连接 Qdrant...")
    qdrant = QdrantManager()
    
    # 获取集合列表
    collections = qdrant.list_collections()
    if not collections:
        print("❌ 没有找到任何集合")
        return
    
    print("\n📋 可用集合:")
    for i, col in enumerate(collections):
        vector_size = col.get('vector_size', 'unknown')
        print(f"  {i+1}. {col['name']} ({col.get('points_count', 0)} 个向量, {vector_size}维)")
    
    # 选择集合
    if collection_index > len(collections):
        collection_index = len(collections)
    
    collection = collections[collection_index - 1]
    collection_name = collection['name']
    vector_size = collection.get('vector_size', 'unknown')
    
    print(f"\n✅ 选择集合: {collection_name} ({vector_size}维)")
    
    # 根据向量维度选择模型
    if isinstance(vector_size, int) and vector_size in DIM_TO_MODEL:
        model_name = DIM_TO_MODEL[vector_size]
        print(f"💡 自动使用模型: {model_name}")
    else:
        print("⚠️  无法确定模型，使用默认模型")
        model_name = 'shibing624/text2vec-base-chinese'
    
    # 加载模型
    print(f"📥 正在加载模型...")
    embedding = LocalEmbeddingService(model_name)
    
    # 执行查询
    print(f"\n🔍 查询问题: \"{question}\"")
    print("-" * 60)
    
    try:
        # 生成向量
        vector = embedding.encode_single(question)
        
        # 搜索
        results = qdrant.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=3,
            score_threshold=0.5
        )
        
        if not results:
            print("❌ 没有找到匹配的结果")
            return
        
        print(f"✅ 找到 {len(results)} 个结果:\n")
        
        for i, result in enumerate(results, 1):
            payload = result.payload
            score = result.score
            
            # 从 metadata 中获取数据
            metadata = payload.get('metadata', {})
            content = payload.get('content', 'N/A')
            
            print(f"{i}. 相似度: {score:.4f}")
            print(f"   问题: {content}")
            print(f"   意图: {metadata.get('intentName', 'N/A')}")
            
            # 显示答案
            answers = metadata.get('answers', [])
            if answers and len(answers) > 0:
                answer = answers[0]
                if isinstance(answer, dict):
                    ans_content = answer.get('content', {})
                    if isinstance(ans_content, dict):
                        text = ans_content.get('text', '')
                        if isinstance(text, str):
                            preview = text[:100] + ('...' if len(text) > 100 else '')
                            print(f"   答案: {preview}")
                        elif isinstance(text, list) and len(text) > 0:
                            preview = text[0][:100] + ('...' if len(text[0]) > 100 else '')
                            print(f"   答案: {preview}")
            
            print()
    
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 默认查询 "包过吗"
    question = sys.argv[1] if len(sys.argv) > 1 else "包过吗"
    collection_index = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    quick_test(question, collection_index)


