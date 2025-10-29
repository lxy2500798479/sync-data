#!/usr/bin/env python3
"""
快速测试上传脚本
不连接数据库，使用模拟数据测试 API 格式
"""

import json
import uuid

def generate_sample_documents(count: int = 5):
    """生成示例文档"""
    documents = []
    
    sample_questions = [
        {
            "question": "社工证书正规吗？",
            "intent_name": "证书类问题",
            "answer": "【社工证】是国家职业资格证书，由国家颁发，属于国家级一类，国家官网/OSTA均可查，因此拿到证书后可以从事相关工作，帮助评职称，【全国通用、终身有效】，没有省份区别"
        },
        {
            "question": "怎么报名？",
            "intent_name": "报名类问题",
            "answer": "您在老师这里报名，学习和报名考试我们都有专人负责指导，不需要您操心。"
        },
        {
            "question": "包过吗？",
            "intent_name": "包过类问题",
            "answer": "咱们通过率都是有保障的，您这边跟课学完不缺考，不弃考，都是可以顺利通过考试的"
        },
        {
            "question": "什么时候考试？",
            "intent_name": "考试类问题",
            "answer": "正常是每年是统一在3月份报名考试，近几年社工岗位空缺，报考人数增加，其他时间段有过补考的，但是下次的考试具体是以官网通知时间为准"
        },
        {
            "question": "多少钱？",
            "intent_name": "价格类问题",
            "answer": "考证无非就是两个选择，一个自学，一个报班，自学是盲目的，找不到重点和考点，只能一把抓，浪费时间和精力"
        }
    ]
    
    company_id = "01998d91-d276-76b3-a5dc-00a580cafd93"
    
    for i in range(min(count, len(sample_questions))):
        sample = sample_questions[i]
        
        doc = {
            "id": str(uuid.uuid4()),
            "content": sample["question"],
            "metadata": {
                "companyId": company_id,
                "intentId": str(uuid.uuid4()),
                "intentName": sample["intent_name"],
                "version": "1.0.0",
                "answers": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "TEXT",
                        "content": {
                            "text": sample["answer"]
                        }
                    }
                ]
            }
        }
        
        documents.append(doc)
    
    return documents


def print_api_request(db_collection_name: str, documents: list):
    """打印 API 请求格式"""
    payload = {
        "dbCollectionName": db_collection_name,
        "documents": documents
    }
    
    print("="*60)
    print("📤 API 请求示例")
    print("="*60)
    print(f"\nPOST https://chat-api.juhebot.com/open/GuidRequest/v1/vector/document/save")
    print(f"\nContent-Type: application/json\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("\n" + "="*60)
    print(f"✅ 文档数量: {len(documents)}")
    print(f"📏 请求大小: {len(json.dumps(payload))} 字节")
    print("="*60)


def main():
    """主函数"""
    print("\n🧪 API 上传格式测试\n")
    
    # 生成示例数据
    print("📝 生成示例数据...\n")
    documents = generate_sample_documents(count=4)
    
    # 显示单个文档格式
    print("="*60)
    print("📄 单个文档格式示例")
    print("="*60)
    print(json.dumps(documents[0], ensure_ascii=False, indent=2))
    
    # 显示完整 API 请求
    print("\n")
    db_collection_name = "knowledge_base_01998d91-d276-76b3-a5dc-00a580cafd93"
    print_api_request(db_collection_name, documents)
    
    # 显示批次划分示例
    print("\n📊 批次划分示例（假设有 1234 个文档）\n")
    total_docs = 1234
    batch_size = 500
    total_batches = (total_docs + batch_size - 1) // batch_size
    
    print(f"总文档数: {total_docs}")
    print(f"每批大小: {batch_size}")
    print(f"总批次数: {total_batches}\n")
    
    for i in range(total_batches):
        start = i * batch_size
        end = min((i + 1) * batch_size, total_docs)
        count = end - start
        print(f"  批次 {i+1}: 文档 {start+1}-{end} ({count} 个)")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("\n💡 下一步:")
    print("   1. 检查上面的数据格式是否符合 API 要求")
    print("   2. 运行预览模式: python upload_to_api.py --company <id> --preview")
    print("   3. 正式上传: python upload_to_api.py --company <id>")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

