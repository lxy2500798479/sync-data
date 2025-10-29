#!/usr/bin/env python3
"""
将知识库数据上传到 API 接口
从 PostgreSQL 读取数据，转换为指定格式，批量上传
"""

import os
import uuid
import json
import requests
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm

# 导入现有的数据库模块
from sync_data.database import PostgreSQLConnection

# 加载环境变量
load_dotenv()

# ============= 配置区域（在这里修改） =============
COMPANY_ID = "01998d91-d276-76b3-a5dc-00a580cafd93"  # 📝 公司ID
DB_COLLECTION_NAME = "chat_shangtong_faq_v0"  # 📝 集合名称
API_URL = "https://ai-toolkit.wyts.tech/v0/vector/document/save"
ACCESS_TOKEN = "sUwzcwDE7YgwYa8fvq6c"  # 📝 访问令牌
VERSION = "1.0.0"  # 📝 版本号
BATCH_SIZE = 10  # ⚠️ API 限制：每批最多 10 条
# ================================================


class APIUploader:
    """API 上传器"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self.db = PostgreSQLConnection()  # 从环境变量自动读取配置
    
    def transform_to_api_format(self, intent: Dict[str, Any], question: str, 
                               answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        转换为 API 所需的格式
        
        Args:
            intent: 意图数据
            question: 标准问题
            answers: 答案列表
            
        Returns:
            API 格式的文档
        """
        # 使用 intent ID 作为文档 ID（固定）
        doc_id = intent['id']
        
        # 构建精简的 metadata
        metadata = {
            "companyId": intent['company_id'],
            "intentName": intent['name'],
            "version": VERSION,  # 版本号
            "level": "通用",  # 默认级别
            "sort": 'order',
            "answers": []
        }
        
        # 处理答案，将 content 转换为字符串数组
        for ans in answers:
            if not ans.get('is_active'):
                continue
                
            content_data = ans.get('content', {})
            content_array = []
            
            # 处理不同格式的 content
            if isinstance(content_data, dict):
                text = content_data.get('text', '')
                if isinstance(text, list):
                    # 如果是列表，直接使用
                    content_array = [str(item) for item in text if item]
                elif isinstance(text, str) and text:
                    # 如果是字符串，包装成列表
                    content_array = [text]
            elif isinstance(content_data, str):
                # 如果 content 本身就是字符串
                content_array = [content_data]
            
            # 只添加有内容的答案
            if content_array:
                metadata['answers'].append({
                    "content": content_array
                })
        
        return {
            "id": doc_id,
            "content": question,
            "metadata": metadata
        }
    
    def fetch_company_data(self, company_id: str) -> List[Dict[str, Any]]:
        """
        获取公司的所有知识库数据
        
        Args:
            company_id: 公司 ID
            
        Returns:
            转换后的文档列表
        """
        print(f"\n{'='*60}")
        print(f"📦 正在获取公司数据: {company_id}")
        print(f"{'='*60}\n")
        
        # 获取所有活跃意图
        intents = self.db.get_company_intents(company_id)
        print(f"✅ 找到 {len(intents)} 个意图")
        
        # 🚀 性能优化：批量获取所有答案（避免 N+1 查询）
        intent_ids = [intent['id'] for intent in intents]
        print(f"🔍 批量查询所有答案...")
        answers_map = self.db.get_answers_by_intent_ids(intent_ids)
        print(f"✅ 查询完成")
        
        documents = []
        
        # 处理每个意图
        for intent in tqdm(intents, desc="处理意图"):
            intent_id = intent['id']
            keywords = intent.get('keywords', [])
            
            if not keywords:
                continue
            
            # 从内存中获取答案（不再查询数据库）
            answers = answers_map.get(intent_id, [])
            
            # 为每个标准问题生成一个文档
            for question in keywords:
                doc = self.transform_to_api_format(intent, question, answers)
                documents.append(doc)
        
        print(f"\n✅ 共生成 {len(documents)} 个文档")
        return documents
    
    def upload_batch(self, db_collection_name: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        上传一批文档到 API
        
        Args:
            db_collection_name: 集合名称
            documents: 文档列表（最多 500 个）
            
        Returns:
            API 响应
        """
        payload = {
            "dbCollectionName": db_collection_name,
            "dimensions": 768,
            "documents": documents
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Access-Token": ACCESS_TOKEN
                },
                timeout=60
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 上传失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   响应内容: {e.response.text}")
            raise
    
    def upload_company_data(self, company_id: str):
        """
        上传公司的所有数据
        
        Args:
            company_id: 公司 ID
        """
        # 获取所有文档
        documents = self.fetch_company_data(company_id)
        
        if not documents:
            print("⚠️ 没有数据需要上传")
            return
        
        # 分批上传
        total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n{'='*60}")
        print(f"📤 开始上传数据")
        print(f"   API地址: {self.api_url}")
        print(f"   集合名称: {DB_COLLECTION_NAME}")
        print(f"   总文档数: {len(documents)}")
        print(f"   批次数: {total_batches}")
        print(f"   每批大小: {BATCH_SIZE}")
        print(f"{'='*60}\n")
        
        success_count = 0
        
        for i in range(0, len(documents), BATCH_SIZE):
            batch = documents[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            
            print(f"📤 上传批次 {batch_num}/{total_batches} ({len(batch)} 个文档)...")
            
            try:
                result = self.upload_batch(DB_COLLECTION_NAME, batch)
                print(f"✅ 批次 {batch_num} 上传成功")
                print(f"   响应: {json.dumps(result, ensure_ascii=False)}")
                success_count += len(batch)
                
            except Exception as e:
                print(f"❌ 批次 {batch_num} 上传失败: {e}")
                # 可以选择继续或停止
                choice = input("是否继续下一批？(y/n): ")
                if choice.lower() != 'y':
                    break
        
        print(f"\n{'='*60}")
        print(f"✅ 上传完成！")
        print(f"   成功: {success_count}/{len(documents)}")
        print(f"{'='*60}")
    
    def close(self):
        """关闭数据库连接（PostgreSQLConnection 自动管理连接）"""
        pass  # 不需要手动关闭


def show_menu():
    """显示交互式菜单"""
    print("\n" + "="*60)
    print("🚀 知识库数据上传工具")
    print("="*60)
    print("请选择操作：")
    print("  1. 📄 查看预览数据（不上传）")
    print("  2. 📤 上传数据到 API")
    print("  3. ❌ 退出")
    print("="*60)
    
    while True:
        choice = input("请输入选项 (1/2/3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("❌ 无效选项，请输入 1、2 或 3")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='上传知识库数据到 API')
    parser.add_argument('--preview', action='store_true', help='预览数据格式，不实际上传')
    parser.add_argument('--upload', action='store_true', help='直接上传数据，不显示菜单')
    
    args = parser.parse_args()
    
    # 使用配置中的公司ID
    company_id = COMPANY_ID
    
    print(f"\n📦 配置信息:")
    print(f"   公司ID: {company_id}")
    print(f"   集合名称: {DB_COLLECTION_NAME}")
    print(f"   API地址: {API_URL}")
    print(f"   Access-Token: {ACCESS_TOKEN[:10]}...{ACCESS_TOKEN[-4:]}\n")
    
    uploader = APIUploader()
    
    try:
        # 确定操作模式
        if args.preview:
            # 命令行参数：预览模式
            mode = '1'
        elif args.upload:
            # 命令行参数：上传模式
            mode = '2'
        else:
            # 交互式菜单
            mode = show_menu()
        
        if mode == '1':
            # 预览模式：只获取数据，不上传
            print("\n🔍 预览模式：获取数据格式...\n")
            documents = uploader.fetch_company_data(company_id)
            
            if documents:
                print("\n" + "="*60)
                print("📄 示例文档（前 3 个）:")
                print("="*60)
                for i, doc in enumerate(documents[:3], 1):
                    print(f"\n文档 {i}:")
                    print(json.dumps(doc, ensure_ascii=False, indent=2))
                
                print("\n" + "="*60)
                print(f"📦 集合名称: {DB_COLLECTION_NAME}")
                print(f"✅ 共 {len(documents)} 个文档")
                print(f"💾 预计请求次数: {(len(documents) + BATCH_SIZE - 1) // BATCH_SIZE}")
                print("="*60)
                
                # 询问是否导出JSON文件
                print("\n💾 是否导出为JSON文件？")
                export_choice = input("请输入 (y/n): ").strip().lower()
                if export_choice == 'y':
                    # 生成文件名（带时间戳）
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"preview_data_{timestamp}.json"
                    
                    # 构建完整的导出数据结构
                    export_data = {
                        "exportTime": datetime.now().isoformat(),
                        "companyId": company_id,
                        "dbCollectionName": DB_COLLECTION_NAME,
                        "totalDocuments": len(documents),
                        "version": VERSION,
                        "documents": documents
                    }
                    
                    # 写入文件
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n✅ 数据已导出到: {filename}")
                    print(f"📊 文件大小: {os.path.getsize(filename) / 1024:.2f} KB")
                else:
                    print("❌ 已取消导出")
            else:
                print("⚠️ 没有找到数据")
        
        elif mode == '2':
            # 正式上传
            print("\n⚠️  即将上传数据到 API，是否继续？")
            confirm = input("请输入 yes 确认: ").strip().lower()
            if confirm == 'yes':
                uploader.upload_company_data(company_id)
            else:
                print("❌ 已取消上传")
        
        elif mode == '3':
            # 退出
            print("👋 再见！")
            return
    
    finally:
        uploader.close()


if __name__ == "__main__":
    main()

