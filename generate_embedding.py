#!/usr/bin/env python3
"""
生成文本向量嵌入
供 TypeScript 后端调用使用
"""

import sys
import json
from sync_data.embedding_service import LocalEmbeddingService

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数"}))
        sys.exit(1)
    
    question = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else 'BAAI/bge-large-zh-v1.5'
    
    try:
        # 初始化嵌入服务
        embedding_service = LocalEmbeddingService(model_name)
        
        # 生成向量
        vector = embedding_service.encode_single(question)
        
        # 返回 JSON
        print(json.dumps(vector))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()

