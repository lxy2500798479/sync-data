#!/usr/bin/env python3
"""
Qdrant 查询测试工具
用于测试向量搜索和匹配功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from sync_data.qdrant_manager import QdrantManager
from sync_data.embedding_service import LocalEmbeddingService

# 推荐模型列表
RECOMMENDED_MODELS = {
    'best': 'BAAI/bge-large-zh-v1.5',
    'tencent': 'tencent/Youtu-Embedding',
    'balanced': 'shibing624/text2vec-base-chinese',
    'light': 'paraphrase-multilingual-MiniLM-L12-v2'
}


def interactive_search():
    """交互式搜索"""
    print("=" * 60)
    print("🔍 Qdrant 向量搜索测试工具")
    print("=" * 60)
    print()
    
    # 初始化服务
    print("🔗 连接 Qdrant...")
    qdrant = QdrantManager()
    
    # 先选择集合，根据向量维度自动选择模型
    print("\n📋 可用集合:")
    collections = qdrant.list_collections()
    if not collections:
        print("❌ 没有找到任何集合")
        print("💡 请先运行数据迁移: python main.py --all")
        return
    
    for i, col in enumerate(collections):
        vector_size = col.get('vector_size', 'unknown')
        print(f"  {i+1}. {col['name']} ({col.get('points_count', 0)} 个向量, {vector_size}维)")
    
    col_choice = input("\n请选择集合 (1-N): ").strip()
    try:
        collection_idx = int(col_choice) - 1
        if 0 <= collection_idx < len(collections):
            collection_name = collections[collection_idx]['name']
            vector_size = collections[collection_idx].get('vector_size', 'unknown')
        else:
            print("❌ 无效选择")
            return
    except ValueError:
        print("❌ 无效输入")
        return
    
    # 根据向量维度自动选择模型
    print(f"\n📊 检测到集合向量维度: {vector_size}")
    if isinstance(vector_size, int):
        if vector_size == 1024:
            model_name = RECOMMENDED_MODELS['best']
            print(f"💡 自动选择: 最佳中文模型 ({model_name})")
        elif vector_size == 768:
            model_name = RECOMMENDED_MODELS['balanced']
            print(f"💡 自动选择: 平衡模型 ({model_name})")
        elif vector_size == 384:
            model_name = RECOMMENDED_MODELS['light']
            print(f"💡 自动选择: 轻量级模型 ({model_name})")
        else:
            print(f"⚠️  未知的向量维度 {vector_size}，使用默认模型")
            model_name = RECOMMENDED_MODELS['balanced']
    else:
        print("⚠️  无法检测向量维度，使用默认模型")
        model_name = RECOMMENDED_MODELS['balanced']
    
    print(f"\n✅ 使用的集合: {collection_name}")
    print(f"✅ 使用的模型: {model_name}")
    print("📥 正在加载模型（首次使用需要下载）...")
    
    embedding = LocalEmbeddingService(model_name)
    
    # 开始搜索循环
    print("\n" + "=" * 60)
    print("🚀 开始搜索（输入 'quit' 退出）")
    print("=" * 60)
    
    while True:
        question = input("\n请输入问题: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 再见!")
            break
        
        if not question:
            continue
        
        print(f"\n🔍 搜索: \"{question}\"")
        print("-" * 60)
        
        try:
            # 生成向量
            vector = embedding.encode_single(question)
            
            # 搜索
            results = qdrant.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=5,
                score_threshold=0.5
            )
            
            if not results:
                print("❌ 没有找到匹配的结果")
                continue
            
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
                
                # 显示答案（取第一个）
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
            print(f"❌ 搜索失败: {e}")


def quick_test(question: str, company_id: str, model_name: str = None):
    """快速测试"""
    if model_name is None:
        model_name = RECOMMENDED_MODELS['balanced']
    
    print(f"🔍 搜索问题: \"{question}\"")
    print(f"🏢 公司ID: {company_id}")
    print(f"🧠 模型: {model_name}")
    print("-" * 60)
    
    try:
        # 初始化
        qdrant = QdrantManager()
        embedding = LocalEmbeddingService(model_name)
        
        # 集合名称
        collection_name = f"kb_{company_id}"
        
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
                            print(f"   答案: {text[:200]}...")
                        elif isinstance(text, list) and len(text) > 0:
                            print(f"   答案: {text[0][:200]}...")
            
            print()
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        if len(sys.argv) < 3:
            print("用法:")
            print("  python test_query.py                    # 交互式搜索")
            print("  python test_query.py <问题> <公司ID>    # 快速测试")
            return
        
        question = sys.argv[1]
        company_id = sys.argv[2]
        model_name = sys.argv[3] if len(sys.argv) > 3 else None
        
        quick_test(question, company_id, model_name)
    else:
        # 交互式模式
        interactive_search()


if __name__ == "__main__":
    main()

