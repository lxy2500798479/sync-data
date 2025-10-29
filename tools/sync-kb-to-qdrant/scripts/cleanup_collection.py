#!/usr/bin/env python3
"""
清理和重新创建集合
删除指定集合并重新创建为1024维
"""

import sys
from sync_data.qdrant_manager import QdrantManager

def cleanup_collection(collection_name: str, new_dimension: int = 1024):
    """清理并重新创建集合"""
    print("=" * 60)
    print("🧹 清理并重新创建集合")
    print("=" * 60)
    print()
    
    qdrant = QdrantManager()
    
    # 1. 检查集合是否存在
    collections = qdrant.list_collections()
    existing_collections = [col['name'] for col in collections]
    
    if collection_name not in existing_collections:
        print(f"❌ 集合 {collection_name} 不存在")
        print(f"📋 可用集合: {', '.join(existing_collections)}")
        return False
    
    print(f"📋 找到集合: {collection_name}")
    
    # 2. 获取集合信息
    info = qdrant.get_collection_info(collection_name)
    if info:
        print(f"   向量数量: {info.get('points_count', 0)}")
        print(f"   当前维度: {info.get('vector_size', 'unknown')}")
    
    # 3. 确认删除
    print(f"\n⚠️  警告：这将删除集合 {collection_name} 的所有数据！")
    confirm = input("确认删除并重新创建？(y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ 已取消")
        return False
    
    # 4. 删除集合
    print(f"\n🗑️  正在删除集合 {collection_name}...")
    if qdrant.delete_collection(collection_name):
        print(f"✅ 集合删除成功")
    else:
        print(f"❌ 集合删除失败")
        return False
    
    # 5. 重新创建集合
    print(f"\n🏗️  正在创建新集合 {collection_name}...")
    print(f"   向量维度: {new_dimension}")
    
    if qdrant.create_collection(collection_name, new_dimension):
        print(f"✅ 集合创建成功")
        return True
    else:
        print(f"❌ 集合创建失败")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python cleanup_collection.py <集合名称> [维度]")
        print()
        print("示例:")
        print("  python cleanup_collection.py wechat_diplomat 1024")
        print("  python cleanup_collection.py wechat_diplomat")
        return
    
    collection_name = sys.argv[1]
    dimension = int(sys.argv[2]) if len(sys.argv) > 2 else 1024
    
    cleanup_collection(collection_name, dimension)

if __name__ == "__main__":
    main()


