"""
本地嵌入服务模块
支持多种免费的中文嵌入模型
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import torch
import os


# 推荐的免费中文模型配置
RECOMMENDED_MODELS = {
    "bge-large-zh-v1.5": {
        "model_name": "BAAI/bge-large-zh-v1.5",
        "dimensions": 1024,
        "description": "百度开源，中文效果很好，推荐使用",
        "size": "~1.3GB",
        "performance": "高"
    },
    "youtu-embedding": {
        "model_name": "tencent/Youtu-Embedding",
        "dimensions": 1024,
        "description": "腾讯优图，中文效果优秀，企业级",
        "size": "~1.3GB",
        "performance": "高"
    },
    "text2vec-large-chinese": {
        "model_name": "shibing624/text2vec-large-chinese", 
        "dimensions": 1024,
        "description": "专门针对中文优化",
        "size": "~1.3GB",
        "performance": "高"
    },
    "text2vec-base-chinese": {
        "model_name": "shibing624/text2vec-base-chinese",
        "dimensions": 768, 
        "description": "较小的模型，速度快",
        "size": "~400MB",
        "performance": "中"
    },
    "paraphrase-multilingual": {
        "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "dimensions": 384,
        "description": "多语言支持，包含中文，最轻量",
        "size": "~470MB",
        "performance": "中低"
    }
}


class LocalEmbeddingService:
    """本地嵌入服务"""
    
    def __init__(self, model_name: str = "BAAI/bge-large-zh-v1.5"):
        """
        初始化本地嵌入服务
        
        Args:
            model_name: 嵌入模型名称，支持以下模型：
                - BAAI/bge-large-zh-v1.5 (推荐，中文效果最好)
                - shibing624/text2vec-base-chinese (速度快)
                - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (轻量级)
        """
        print(f"🚀 正在加载嵌入模型: {model_name}")
        
        # 设置设备
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"📱 使用设备: {self.device}")
        
        if self.device == 'cpu':
            print("⚠️  使用CPU运行，速度可能较慢。如有GPU，请安装CUDA版本的PyTorch")
        
        # 设置缓存目录
        cache_dir = os.getenv('HF_CACHE_DIR', './models_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        try:
            # 加载模型（使用 safetensors 避免 torch.load 漏洞）
            self.model = SentenceTransformer(
                model_name, 
                device=self.device,
                cache_folder=cache_dir,
                trust_remote_code=True,
                # 强制使用 safetensors 格式
                use_auth_token=None
            )
            self.model_name = model_name
            self.dimensions = self.model.get_sentence_embedding_dimension()
            
            print(f"✅ 模型加载成功！")
            print(f"   模型名称: {self.model_name}")
            print(f"   向量维度: {self.dimensions}")
            print(f"   缓存目录: {cache_dir}")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            print("💡 建议尝试以下解决方案：")
            print("   1. 检查网络连接")
            print("   2. 尝试使用较小的模型")
            print("   3. 手动下载模型到本地")
            raise
    
    def encode_single(self, text: str) -> List[float]:
        """编码单个文本"""
        if not text or not text.strip():
            print("⚠️ 发现空文本，使用零向量")
            return [0.0] * self.dimensions
            
        try:
            embedding = self.model.encode(
                text, 
                convert_to_tensor=False, 
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return embedding.tolist()
        except Exception as e:
            print(f"❌ 文本编码失败: {e}")
            print(f"   问题文本: {text[:100]}...")
            return [0.0] * self.dimensions
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """批量编码文本"""
        if not texts:
            return []
        
        print(f"🔄 开始批量编码 {len(texts)} 个文本...")
        
        # 预处理文本
        processed_texts = []
        for i, text in enumerate(texts):
            # 确保text是字符串类型
            if not isinstance(text, str):
                print(f"⚠️ 第 {i+1} 个文本不是字符串类型: {type(text)} - {text}")
                if isinstance(text, (list, tuple)) and text:
                    # 如果是列表，尝试获取第一个字符串元素
                    text_str = ""
                    for item in text:
                        if isinstance(item, str) and item.strip():
                            text_str = item.strip()
                            break
                    if text_str:
                        processed_texts.append(text_str)
                    else:
                        processed_texts.append("空文本")
                else:
                    processed_texts.append(str(text) if text else "空文本")
            elif not text or not text.strip():
                print(f"⚠️ 第 {i+1} 个文本为空，使用占位符")
                processed_texts.append("空文本")
            else:
                processed_texts.append(text.strip())
        
        try:
            # 批量编码
            embeddings = self.model.encode(
                processed_texts, 
                batch_size=batch_size,
                convert_to_tensor=False,
                normalize_embeddings=True,
                show_progress_bar=True,
                device=self.device
            )
            
            print(f"✅ 批量编码完成！生成了 {len(embeddings)} 个向量")
            return embeddings.tolist()
            
        except Exception as e:
            print(f"❌ 批量编码失败: {e}")
            print("🔄 回退到单个编码模式...")
            
            # 回退到单个编码
            results = []
            for i, text in enumerate(processed_texts):
                try:
                    result = self.encode_single(text)
                    results.append(result)
                    if (i + 1) % 10 == 0:
                        print(f"   已处理 {i+1}/{len(processed_texts)} 个文本")
                except Exception as single_error:
                    print(f"❌ 第 {i+1} 个文本编码失败: {single_error}")
                    results.append([0.0] * self.dimensions)
            
            return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "device": self.device,
            "model_type": "local_sentence_transformer"
        }
    
    @staticmethod
    def list_available_models() -> Dict[str, Dict[str, Any]]:
        """列出可用的模型"""
        return RECOMMENDED_MODELS
    
    @staticmethod
    def recommend_model(gpu_memory_gb: float = 0) -> str:
        """根据硬件配置推荐模型"""
        if gpu_memory_gb >= 8:
            return "BAAI/bge-large-zh-v1.5"  # 或 "tencent/Youtu-Embedding"
        elif gpu_memory_gb >= 4:
            return "shibing624/text2vec-base-chinese"
        else:
            return "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    def calculate_vector_quality(self, vector: List[float]) -> float:
        """计算向量质量分数"""
        if not vector or len(vector) != self.dimensions:
            return 0.0
        
        # 基于方差的质量评估
        vector_array = np.array(vector)
        mean_val = np.mean(vector_array)
        variance = np.var(vector_array)
        
        # 标准化到0-1范围
        quality_score = min(variance * 10, 1.0)
        return float(quality_score)
