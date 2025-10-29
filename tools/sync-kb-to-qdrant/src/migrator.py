"""
知识库数据迁移服务
从PostgreSQL迁移到Qdrant向量数据库
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from qdrant_client.models import PointStruct

from .database import PostgreSQLConnection
from .qdrant_manager import QdrantManager
from .embedding_service import LocalEmbeddingService


class KnowledgeBaseMigrator:
    """知识库数据迁移器"""
    
    def __init__(self, model_name: str = "BAAI/bge-large-zh-v1.5"):
        """
        初始化迁移器
        
        Args:
            model_name: 嵌入模型名称
        """
        print("🚀 初始化知识库迁移器...")
        
        # 初始化各个组件
        self.db = PostgreSQLConnection()
        self.qdrant = QdrantManager()
        self.embedding_service = LocalEmbeddingService(model_name)
        
        # 默认向量配置
        self.vector_config = {
            "has_named_vectors": False,
            "vector_names": [],
            "vector_config_type": "single"
        }
        
        # 测试连接
        print("🔍 测试数据库连接...")
        if not self.db.test_connection():
            raise ConnectionError("PostgreSQL连接失败")
        
        print("🔍 测试Qdrant连接...")
        if not self.qdrant.test_connection():
            raise ConnectionError("Qdrant连接失败")
        
        print("✅ 所有组件初始化完成")
    
    def calculate_popularity_tier(self, usage_count: int) -> str:
        """计算热度分层"""
        if usage_count >= 100:
            return "HOT"
        elif usage_count >= 10:
            return "WARM"
        else:
            return "COLD"
    
    def calculate_search_priority(self, usage_count: int) -> int:
        """计算搜索优先级"""
        return min(max(usage_count // 10 + 1, 1), 10)
    
    def build_payload(self, intent: Dict[str, Any], question: str, 
                     question_index: int, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建向量点的payload（规范结构：content + metadata）"""
        current_time = int(time.time() * 1000)
        
        return {
            # 主要内容：用于向量化的文本
            "content": question,
            
            # 元数据：所有业务相关信息
            "metadata": {
                # 核心业务标识
                "companyId": intent['company_id'],
                "intentId": intent['id'],
                "intentName": intent['name'],
                "originalId": f"{intent['company_id']}_{intent['id']}_{question_index}",  # 原始字符串ID用于追踪
                
                # 标准问题信息
                "currentQuestionIndex": question_index,
                "allStandardQuestions": intent['keywords'],
                "questionCount": len(intent['keywords']),
                
                # 答案信息
                "answers": [
                    {
                        "id": ans['id'],
                        "type": ans['type'],
                        "content": ans['content'],
                        "isActive": ans['is_active']
                    } for ans in answers
                ],
                "answerCount": len(answers),
                "activeAnswerCount": sum(1 for ans in answers if ans['is_active']),
                
                # 使用统计
                "intentUsageCount": intent.get('usage_count', 0),
                "usageCount24h": 0,  # 初始值
                "lastMatchedAt": 0,  # 初始值
                
                # 质量指标
                "avgConfidenceScore": 0.0,  # 初始值
                "matchSuccessRate": 0.0,  # 初始值
                
                # 性能分层
                "popularityTier": self.calculate_popularity_tier(intent.get('usage_count', 0)),
                "searchPriority": self.calculate_search_priority(intent.get('usage_count', 0)),
                
                # 向量质量
                "vectorQuality": 0.5,  # 将在计算向量后更新
                "language": "zh-CN",  # 中文语言标识
                
                # 基础状态
                "isDeleted": intent.get('is_deleted', 0) == 1,
                "intentIsActive": intent.get('is_active', True),
                "hasActiveAnswers": any(ans['is_active'] for ans in answers),
                
                # 时间追踪
                "createdAt": int(intent['created_at'].timestamp() * 1000),
                "updatedAt": int(intent['updated_at'].timestamp() * 1000),
                "lastAccessedAt": current_time,
                
                # 同步管理
                "syncVersion": "0.0.1",
                "lastSyncAt": current_time
            }
        }
    
    def process_intent(self, intent: Dict[str, Any]) -> List[PointStruct]:
        """处理单个意图，为每个问题生成向量点"""
        intent_id = intent['id']
        company_id = intent['company_id']
        keywords = intent.get('keywords', [])
        
        if not keywords:
            print(f"⚠️ 意图 {intent_id} 没有标准问题，跳过")
            return []
        
        print(f"🔄 处理意图: {intent['name']} ({len(keywords)} 个问题)")
        
        # 获取答案
        answers = self.db.get_intent_answers(intent_id)
        
        # 批量向量化所有标准问题
        print(f"   🧠 正在向量化 {len(keywords)} 个问题...")
        vectors = self.embedding_service.encode_batch(keywords)
        
        if len(vectors) != len(keywords):
            print(f"❌ 向量化数量不匹配: 期望 {len(keywords)}, 实际 {len(vectors)}")
            return []
        
        # 构建向量点
        points = []
        for i, (question, vector) in enumerate(zip(keywords, vectors)):
            # 构建payload
            payload = self.build_payload(intent, question, i, answers)
            
            # 更新向量质量
            payload["metadata"]["vectorQuality"] = self.embedding_service.calculate_vector_quality(vector)
            
            # 创建向量点（使用UUID格式ID）
            import uuid
            # 生成UUID格式的ID，确保唯一性
            point_id = str(uuid.uuid4())
            
            # 添加UUID到metadata中
            payload["metadata"]["id"] = point_id
            
            # 根据向量配置创建向量点
            if hasattr(self, 'vector_config') and self.vector_config.get('has_named_vectors', False):
                # 命名向量配置
                vector_names = self.vector_config.get('vector_names', [])
                if vector_names:
                    vector_name = vector_names[0]  # 使用第一个向量名
                    print(f"   🔧 使用命名向量: {vector_name}")
                    point = PointStruct(
                        id=point_id,
                        vectors={vector_name: vector},
                        payload=payload
                    )
                else:
                    # 如果没有向量名，回退到默认配置
                    point = PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
            else:
                # 单一向量配置
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            points.append(point)
        
        print(f"   ✅ 生成了 {len(points)} 个向量点")
        return points
    
    def migrate_company(self, company_id: str) -> Dict[str, Any]:
        """迁移单个公司的数据"""
        print(f"\n{'='*60}")
        print(f"📦 开始迁移公司: {company_id}")
        print(f"{'='*60}")
        
        result = {
            "company_id": company_id,
            "success": False,
            "total_intents": 0,
            "total_questions": 0,
            "total_vectors": 0,
            "success_count": 0,
            "error_count": 0,
            "errors": [],
            "duration_seconds": 0,
            "start_time": datetime.now()
        }
        
        start_time = time.time()
        
        try:
            # 1. 强制重建集合以确保维度匹配
            collection_name = "wechat_diplomat"
            print(f"📦 准备集合: {collection_name}")
            
            # 检查集合是否存在
            collection_info = self.qdrant.get_collection_info(collection_name)
            if collection_info:
                print(f"✅ 集合已存在，向量维度: {collection_info.get('vector_size', 'unknown')}")
                expected_size = self.embedding_service.dimensions
                actual_size = collection_info.get('vector_size', 0)
                
                # 如果维度不匹配，删除并重建
                if actual_size != expected_size and actual_size != 'unknown':
                    print(f"⚠️ 向量维度不匹配：期望 {expected_size}，实际 {actual_size}")
                    print(f"🗑️ 删除现有集合并重建...")
                    
                    try:
                        self.qdrant.client.delete_collection(collection_name)
                        print(f"✅ 已删除现有集合: {collection_name}")
                    except Exception as e:
                        print(f"❌ 删除集合失败: {e}")
                        raise Exception(f"无法删除现有集合: {e}")
                else:
                    print(f"✅ 向量维度匹配，使用现有集合")
            
            # 创建集合（如果不存在或已删除）
            if not self.qdrant.get_collection_info(collection_name):
                print(f"🏗️ 创建新集合: {collection_name} ({self.embedding_service.dimensions}维)")
                if not self.qdrant.create_collection(collection_name, self.embedding_service.dimensions):
                    raise Exception("集合创建失败")
                print(f"✅ 集合创建成功")
            
            # 获取向量配置
            vector_config = self.qdrant.get_vector_config(collection_name)
            print(f"🔧 向量配置: {vector_config['vector_config_type']}")
            self.vector_config = vector_config
            
            # 2. 获取公司的意图数据
            print("📊 获取意图数据...")
            intents = self.db.get_company_intents(company_id)
            
            result["total_intents"] = len(intents)
            result["total_questions"] = sum(len(intent.get('keywords', [])) for intent in intents)
            
            print(f"📈 统计信息:")
            print(f"   总意图数: {result['total_intents']}")
            print(f"   总问题数: {result['total_questions']}")
            
            if result["total_intents"] == 0:
                print("⚠️ 没有找到意图数据，跳过迁移")
                result["success"] = True
                return result
            
            # 3. 处理每个意图
            print("\n🔄 开始处理意图...")
            all_points = []
            
            for intent in tqdm(intents, desc="处理意图", ncols=80):
                try:
                    points = self.process_intent(intent)
                    all_points.extend(points)
                    result["success_count"] += 1
                    
                except Exception as e:
                    error_msg = f"意图 {intent['id']} 处理失败: {str(e)}"
                    result["errors"].append(error_msg)
                    result["error_count"] += 1
                    print(f"\n❌ {error_msg}")
            
            result["total_vectors"] = len(all_points)
            print(f"\n📊 处理完成:")
            print(f"   成功意图数: {result['success_count']}")
            print(f"   失败意图数: {result['error_count']}")
            print(f"   生成向量数: {result['total_vectors']}")
            
            # 4. 批量插入到Qdrant
            if all_points:
                print(f"\n📤 开始插入向量到Qdrant...")
                if self.qdrant.upsert_points(collection_name, all_points):
                    print("✅ 向量插入成功")
                else:
                    raise Exception("向量插入失败")
            
            # 5. 验证结果
            print("\n🔍 验证迁移结果...")
            collection_info = self.qdrant.get_collection_info(collection_name)
            if collection_info:
                actual_count = collection_info['points_count']
                print(f"📈 验证结果:")
                print(f"   期望向量数: {result['total_vectors']}")
                print(f"   实际向量数: {actual_count}")
                
                if actual_count == result['total_vectors']:
                    print("✅ 数据验证成功")
                else:
                    print("⚠️ 数据数量不匹配")
            
            # 6. 计算耗时
            result["duration_seconds"] = time.time() - start_time
            result["success"] = result["error_count"] == 0
            
            print(f"\n🎉 公司 {company_id} 迁移完成!")
            print(f"   耗时: {result['duration_seconds']:.2f} 秒")
            print(f"   状态: {'✅ 成功' if result['success'] else '⚠️ 部分成功'}")
            
            return result
            
        except Exception as e:
            result["duration_seconds"] = time.time() - start_time
            error_msg = f"公司迁移失败: {str(e)}"
            result["errors"].append(error_msg)
            print(f"\n❌ {error_msg}")
            return result
    
    def migrate_all_companies(self) -> List[Dict[str, Any]]:
        """迁移所有公司的数据"""
        print("🌐 开始迁移所有公司的知识库数据...")
        
        # 获取所有公司
        companies = self.db.get_all_companies()
        print(f"📊 找到 {len(companies)} 个公司")
        
        if not companies:
            print("⚠️ 没有找到公司数据")
            return []
        
        # 显示公司列表
        print("\n📋 公司列表:")
        for i, company in enumerate(companies, 1):
            print(f"   {i}. {company['name']} ({company['id']})")
        
        # 迁移每个公司
        results = []
        for i, company in enumerate(companies, 1):
            print(f"\n{'🔸' * 20} {i}/{len(companies)} {'🔸' * 20}")
            print(f"正在处理: {company['name']} ({company['id']})")
            
            result = self.migrate_company(company['id'])
            results.append(result)
            
            # 显示进度摘要
            if result['success']:
                print(f"✅ 完成: {result['success_count']} 个意图, {result['total_vectors']} 个向量")
            else:
                print(f"⚠️ 部分完成: {result['success_count']}/{result['total_intents']} 个意图")
            
            # 短暂休息，避免过载
            if i < len(companies):
                time.sleep(1)
        
        # 保存迁移报告
        self.save_migration_report(results)
        
        # 显示总体统计
        self.print_migration_summary(results)
        
        return results
    
    def save_migration_report(self, results: List[Dict[str, Any]]) -> str:
        """保存迁移报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"migration_report_{timestamp}.json"
        
        # 准备报告数据
        report = {
            "migration_time": timestamp,
            "total_companies": len(results),
            "successful_companies": sum(1 for r in results if r['success']),
            "total_intents": sum(r['total_intents'] for r in results),
            "total_vectors": sum(r['total_vectors'] for r in results),
            "total_duration": sum(r['duration_seconds'] for r in results),
            "companies": results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n📄 迁移报告已保存: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            return ""
    
    def print_migration_summary(self, results: List[Dict[str, Any]]):
        """打印迁移总结"""
        print(f"\n{'='*60}")
        print("🎉 迁移总结")
        print(f"{'='*60}")
        
        total_companies = len(results)
        successful_companies = sum(1 for r in results if r['success'])
        total_intents = sum(r['total_intents'] for r in results)
        total_vectors = sum(r['total_vectors'] for r in results)
        total_duration = sum(r['duration_seconds'] for r in results)
        
        print(f"📊 总体统计:")
        print(f"   公司数量: {successful_companies}/{total_companies}")
        print(f"   意图数量: {total_intents}")
        print(f"   向量数量: {total_vectors}")
        print(f"   总耗时: {total_duration:.2f} 秒")
        
        if total_vectors > 0:
            avg_time_per_vector = total_duration / total_vectors
            print(f"   平均每向量: {avg_time_per_vector:.3f} 秒")
        
        # 显示失败的公司
        failed_companies = [r for r in results if not r['success']]
        if failed_companies:
            print(f"\n❌ 失败的公司 ({len(failed_companies)} 个):")
            for result in failed_companies:
                print(f"   - {result['company_id']}: {len(result['errors'])} 个错误")
        
        print(f"\n✨ 迁移完成!")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        print("📊 获取数据库统计信息...")
        return self.db.get_database_stats()
    
    def get_qdrant_stats(self) -> Dict[str, Any]:
        """获取Qdrant统计信息"""
        print("📊 获取Qdrant统计信息...")
        return self.qdrant.get_system_info()
