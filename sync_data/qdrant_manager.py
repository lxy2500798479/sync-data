"""
Qdrant向量数据库管理模块
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, CreateCollection, PointStruct,
    Filter, FieldCondition, MatchValue, PayloadSchemaType
)
from qdrant_client.http.exceptions import ResponseHandlingException
import os
from typing import List, Dict, Any, Optional
import time


class QdrantManager:
    """Qdrant向量数据库管理器"""
    
    def __init__(self):
        """初始化Qdrant客户端"""
        self.qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        
        print(f"🔗 连接到Qdrant: {self.qdrant_url}")
        
        try:
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                timeout=30
            )
            
            # 测试连接
            collections = self.client.get_collections()
            print(f"✅ Qdrant连接成功！当前有 {len(collections.collections)} 个集合")
            
        except Exception as e:
            print(f"❌ Qdrant连接失败: {e}")
            print("💡 请检查：")
            print("   1. Qdrant服务是否启动")
            print("   2. URL是否正确")
            print("   3. 网络连接是否正常")
            raise
    
    def test_connection(self) -> bool:
        """测试Qdrant连接"""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            print(f"❌ Qdrant连接测试失败: {e}")
            return False
    
    def create_collection(self, collection_name: str, vector_size: int) -> bool:
        """创建向量集合"""
        try:
            # 检查集合是否已存在
            collections = self.client.get_collections().collections
            existing_names = [col.name for col in collections]
            
            if collection_name in existing_names:
                print(f"📋 集合 {collection_name} 已存在，跳过创建")
                return True
            
            print(f"🏗️ 正在创建集合: {collection_name}")
            print(f"   向量维度: {vector_size}")
            
            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
                # 优化配置
                optimizers_config={
                    "default_segment_number": 2,
                    "max_segment_size": 50000
                },
                # 分片配置（根据数据量调整）
                shard_number=1,
                replication_factor=1
            )
            
            print(f"✅ 集合创建成功: {collection_name}")
            
            # 创建索引
            success = self.create_indexes(collection_name)
            return success
            
        except Exception as e:
            print(f"❌ 创建集合失败: {collection_name}, 错误: {e}")
            return False
    
    def create_indexes(self, collection_name: str) -> bool:
        """为集合创建必要的索引"""
        print(f"📇 正在为集合 {collection_name} 创建索引...")
        
        # 定义需要创建的索引（字段现在在metadata中）
        indexes = [
            ("metadata.id", PayloadSchemaType.KEYWORD),
            ("metadata.isDeleted", PayloadSchemaType.BOOL),
            ("metadata.intentIsActive", PayloadSchemaType.BOOL),
            ("metadata.hasActiveAnswers", PayloadSchemaType.BOOL),
            ("metadata.popularityTier", PayloadSchemaType.KEYWORD),
            ("metadata.intentId", PayloadSchemaType.KEYWORD),
            ("metadata.companyId", PayloadSchemaType.KEYWORD),
        ]
        
        success_count = 0
        for field_name, field_type in indexes:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=field_type
                )
                success_count += 1
                print(f"   ✅ 索引创建成功: {field_name}")
                
            except Exception as e:
                print(f"   ⚠️  索引创建警告 {field_name}: {e}")
        
        print(f"📇 索引创建完成: {success_count}/{len(indexes)} 个成功")
        return success_count > 0
    
    def upsert_points(self, collection_name: str, points: List[PointStruct], 
                     batch_size: int = 100) -> bool:
        """批量插入向量点"""
        if not points:
            print("⚠️ 没有向量点需要插入")
            return True
        
        try:
            print(f"📤 正在插入 {len(points)} 个向量点到集合 {collection_name}")
            
            # 分批处理
            total_batches = (len(points) + batch_size - 1) // batch_size
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                print(f"   📦 处理批次 {batch_num}/{total_batches} ({len(batch)} 个点)")
                
                # 插入批次
                operation_info = self.client.upsert(
                    collection_name=collection_name,
                    points=batch,
                    wait=True  # 等待操作完成
                )
                
                print(f"   ✅ 批次 {batch_num} 插入成功")
                
                # 短暂休息，避免过载
                if batch_num < total_batches:
                    time.sleep(0.1)
            
            print(f"🎉 所有向量点插入完成！")
            return True
            
        except Exception as e:
            print(f"❌ 向量点插入失败: {e}")
            return False
    
    def search(self, collection_name: str, query_vector: List[float], 
               limit: int = 10, score_threshold: float = 0.7,
               filter_conditions: Optional[Filter] = None) -> List[Any]:
        """搜索向量"""
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_conditions,
                with_payload=True,
                with_vectors=False  # 不返回向量，节省带宽
            )
            return results
            
        except Exception as e:
            print(f"❌ 向量搜索失败: {e}")
            return []
    
    def get_vector_config(self, collection_name: str) -> Dict[str, Any]:
        """获取集合的向量配置信息"""
        try:
            info = self.client.get_collection(collection_name)
            
            vector_config = {
                "has_named_vectors": False,
                "vector_names": [],
                "default_vector_size": 0,
                "vector_config_type": "single"
            }
            
            if hasattr(info, 'config') and hasattr(info.config, 'params'):
                vectors_config = info.config.params.vectors
                
                # 调试信息
                print(f"🔍 调试向量配置: type={type(vectors_config)}, content={vectors_config}")
                
                # 检查是否为空的向量配置
                is_empty = False
                if hasattr(vectors_config, '__dict__'):
                    # 有 __dict__ 属性的对象
                    vector_dict = vectors_config.__dict__
                    if not vector_dict or len(vector_dict) == 0:
                        is_empty = True
                elif isinstance(vectors_config, dict):
                    # 直接是dict类型
                    if not vectors_config or len(vectors_config) == 0:
                        is_empty = True
                
                if is_empty:
                    # 空的向量配置
                    vector_config["vector_config_type"] = "empty"
                elif isinstance(vectors_config, dict):
                    # 命名向量配置（真正的字典，键是向量名）
                    if vectors_config and len(vectors_config) > 0:
                        vector_config["has_named_vectors"] = True
                        vector_config["vector_names"] = list(vectors_config.keys())
                        vector_config["vector_config_type"] = "named"
                        # 获取第一个向量的大小
                        first_vector = list(vectors_config.values())[0]
                        if hasattr(first_vector, 'size'):
                            vector_config["default_vector_size"] = first_vector.size
                elif hasattr(vectors_config, 'size'):
                    # 单一向量配置（VectorParams 对象）
                    vector_config["default_vector_size"] = vectors_config.size
                    vector_config["vector_config_type"] = "single"
                else:
                    # 未知配置类型，可能是空的
                    vector_config["vector_config_type"] = "empty"
            
            return vector_config
            
        except Exception as e:
            print(f"❌ 获取向量配置失败: {e}")
            return {
                "has_named_vectors": False,
                "vector_names": [],
                "default_vector_size": 0,
                "vector_config_type": "unknown"
            }

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """获取集合信息"""
        try:
            info = self.client.get_collection(collection_name)
            
            # 兼容不同版本的Qdrant API
            result = {
                "name": collection_name,
                "points_count": getattr(info, 'points_count', 0),
                "vectors_count": getattr(info, 'vectors_count', 0),
                "segments_count": getattr(info, 'segments_count', 0),
                "status": getattr(info, 'status', 'unknown'),
                "optimizer_status": getattr(info, 'optimizer_status', 'unknown')
            }
            
            # 可选字段，可能在某些版本中不存在
            if hasattr(info, 'disk_data_size'):
                result["disk_data_size"] = info.disk_data_size
            else:
                result["disk_data_size"] = 0
                
            if hasattr(info, 'ram_data_size'):
                result["ram_data_size"] = info.ram_data_size
            else:
                result["ram_data_size"] = 0
            
            # 向量配置信息
            try:
                if hasattr(info, 'config') and hasattr(info.config, 'params'):
                    if hasattr(info.config.params, 'vectors'):
                        # 处理不同类型的向量配置
                        vectors_config = info.config.params.vectors
                        if hasattr(vectors_config, 'size'):
                            result["vector_size"] = vectors_config.size
                        elif hasattr(vectors_config, '__dict__'):
                            # 如果是字典类型的配置
                            vector_info = getattr(vectors_config, '__dict__', {})
                            result["vector_size"] = vector_info.get('size', 'unknown')
                        else:
                            result["vector_size"] = 'unknown'
                            
                        if hasattr(vectors_config, 'distance'):
                            result["distance_function"] = vectors_config.distance
                        else:
                            result["distance_function"] = 'unknown'
                    else:
                        result["vector_size"] = 'unknown'
                        result["distance_function"] = 'unknown'
                else:
                    result["vector_size"] = 'unknown'
                    result["distance_function"] = 'unknown'
            except Exception as config_error:
                print(f"⚠️ 获取集合 {collection_name} 配置信息时出错: {config_error}")
                result["vector_size"] = 'unknown'
                result["distance_function"] = 'unknown'
            
            return result
            
        except Exception as e:
            print(f"❌ 获取集合信息失败 {collection_name}: {e}")
            return None
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """列出所有集合"""
        try:
            collections = self.client.get_collections()
            result = []
            
            for collection in collections.collections:
                info = self.get_collection_info(collection.name)
                if info:
                    result.append(info)
            
            return result
            
        except Exception as e:
            print(f"❌ 列出集合失败: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        try:
            print(f"🗑️ 正在删除集合: {collection_name}")
            self.client.delete_collection(collection_name)
            print(f"✅ 集合删除成功: {collection_name}")
            return True
            
        except Exception as e:
            print(f"❌ 集合删除失败 {collection_name}: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取Qdrant系统信息"""
        try:
            collections = self.list_collections()
            
            total_points = sum(col.get('points_count', 0) for col in collections)
            total_size = sum(col.get('disk_data_size', 0) for col in collections)
            
            return {
                "total_collections": len(collections),
                "total_points": total_points,
                "total_disk_size": total_size,
                "collections": collections
            }
            
        except Exception as e:
            print(f"❌ 获取系统信息失败: {e}")
            return {}
    
    def cleanup_empty_collections(self) -> int:
        """清理空集合"""
        collections = self.list_collections()
        deleted_count = 0
        
        for collection in collections:
            if collection.get('points_count', 0) == 0:
                print(f"🧹 发现空集合: {collection['name']}")
                if self.delete_collection(collection['name']):
                    deleted_count += 1
        
        if deleted_count > 0:
            print(f"🗑️ 清理完成，删除了 {deleted_count} 个空集合")
        else:
            print("✨ 没有发现空集合")
        
        return deleted_count
