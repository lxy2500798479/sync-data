"""
知识库数据同步到Qdrant - 主入口文件
"""

import argparse
import sys
import os
from typing import Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sync_data.migrator import KnowledgeBaseMigrator
from sync_data.embedding_service import RECOMMENDED_MODELS


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 知识库数据同步工具                      ║
║                PostgreSQL → Qdrant 向量数据库               ║
║                                                              ║
║              使用免费本地模型 • 支持中文优化                  ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def list_models():
    """列出可用的模型"""
    print("📋 可用的嵌入模型:")
    print()
    
    for key, model_info in RECOMMENDED_MODELS.items():
        print(f"🔸 {key}")
        print(f"   模型名称: {model_info['model_name']}")
        print(f"   向量维度: {model_info['dimensions']}")
        print(f"   模型大小: {model_info['size']}")
        print(f"   性能等级: {model_info['performance']}")
        print(f"   描述: {model_info['description']}")
        print()


def check_environment():
    """检查环境变量"""
    print("🔍 检查环境配置...")
    
    required_vars = [
        'DATABASE_HOST', 'DATABASE_NAME', 'DATABASE_USER', 'DATABASE_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("💡 请在 .env 文件中设置以下变量:")
        print("   DATABASE_HOST=localhost")
        print("   DATABASE_PORT=5432")
        print("   DATABASE_NAME=your_database")
        print("   DATABASE_USER=your_username")
        print("   DATABASE_PASSWORD=your_password")
        print("   DATABASE_SCHEMA=public  # 重要！数据库Schema")
        print("   QDRANT_URL=http://localhost:6333")
        print("   # QDRANT_API_KEY=your_api_key  # 本地部署可选")
        return False
    
    print("✅ 环境配置检查通过")
    
    # 检查数据库表结构
    try:
        from sync_data.database import PostgreSQLConnection
        db = PostgreSQLConnection()
        table_status = db.check_tables_exist()
        
        missing_tables = [table for table, exists in table_status.items() if not exists]
        if missing_tables:
            print(f"\n⚠️ 数据库表结构问题:")
            print(f"   缺少表: {', '.join(missing_tables)}")
            print(f"   当前Schema: {db.schema}")
            print(f"\n💡 解决方案:")
            print(f"   1. 运行: python check_database.py")
            print(f"   2. 检查DATABASE_SCHEMA配置")
            print(f"   3. 确认数据库是否为知识库系统")
            return False
        
        print("✅ 数据库表结构检查通过")
        
    except Exception as e:
        print(f"\n⚠️ 数据库连接或表检查失败: {e}")
        print(f"💡 建议运行: python check_database.py")
        return False
    
    return True


def migrate_company(company_id: str, model_name: str):
    """迁移指定公司"""
    try:
        print(f"🎯 开始迁移公司: {company_id}")
        print(f"🧠 使用模型: {model_name}")
        
        migrator = KnowledgeBaseMigrator(model_name)
        result = migrator.migrate_company(company_id)
        
        print("\n📊 迁移结果:")
        print(f"   公司ID: {result['company_id']}")
        print(f"   总意图数: {result['total_intents']}")
        print(f"   总问题数: {result['total_questions']}")
        print(f"   总向量数: {result['total_vectors']}")
        print(f"   成功数: {result['success_count']}")
        print(f"   失败数: {result['error_count']}")
        print(f"   耗时: {result['duration_seconds']:.2f} 秒")
        print(f"   状态: {'✅ 成功' if result['success'] else '⚠️ 部分成功'}")
        
        if result['errors']:
            print("\n❌ 错误详情:")
            for error in result['errors']:
                print(f"   - {error}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False


def migrate_all_companies(model_name: str):
    """迁移所有公司"""
    try:
        print("🌐 开始迁移所有公司")
        print(f"🧠 使用模型: {model_name}")
        
        migrator = KnowledgeBaseMigrator(model_name)
        results = migrator.migrate_all_companies()
        
        # 返回成功状态
        total_companies = len(results)
        successful_companies = sum(1 for r in results if r['success'])
        
        return successful_companies == total_companies
        
    except Exception as e:
        print(f"❌ 批量迁移失败: {e}")
        return False


def show_stats():
    """显示数据库统计"""
    try:
        print("📊 获取数据库统计信息...")
        
        # 使用默认模型初始化（只需要数据库连接）
        migrator = KnowledgeBaseMigrator("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        # PostgreSQL统计
        db_stats = migrator.get_database_stats()
        print("\n📀 PostgreSQL 统计:")
        print(f"   公司数量: {db_stats.get('total_companies', 0)}")
        print(f"   意图数量: {db_stats.get('total_intents', 0)}")
        print(f"   问题数量: {db_stats.get('total_questions', 0)}")
        print(f"   答案数量: {db_stats.get('total_answers', 0)}")
        
        # Qdrant统计
        qdrant_stats = migrator.get_qdrant_stats()
        print("\n🔮 Qdrant 统计:")
        print(f"   集合数量: {qdrant_stats.get('total_collections', 0)}")
        print(f"   向量数量: {qdrant_stats.get('total_points', 0)}")
        print(f"   存储大小: {qdrant_stats.get('total_disk_size', 0)} bytes")
        
        # 显示集合详情
        if qdrant_stats.get('collections'):
            print("\n📋 集合详情:")
            for collection in qdrant_stats['collections']:
                print(f"   🔸 {collection['name']}")
                print(f"      向量数量: {collection.get('points_count', 0)}")
                print(f"      向量维度: {collection.get('vector_size', 0)}")
                print(f"      存储大小: {collection.get('disk_data_size', 0)} bytes")
        
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")


def main():
    """主函数"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='知识库数据同步到Qdrant向量数据库',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --check                          # 检查环境配置
  python main.py --check-db                       # 详细检查数据库表结构
  python main.py --list-models                    # 列出可用模型
  python main.py --stats                          # 显示数据库统计
  python main.py --company company_123            # 迁移指定公司
  python main.py --all                            # 迁移所有公司
  python main.py --all --model text2vec-base      # 使用指定模型迁移所有公司
        """
    )
    
    # 操作选项
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--check', action='store_true', help='检查环境配置')
    action_group.add_argument('--check-db', action='store_true', help='详细检查数据库表结构')
    action_group.add_argument('--list-models', action='store_true', help='列出可用的嵌入模型')
    action_group.add_argument('--stats', action='store_true', help='显示数据库统计信息')
    action_group.add_argument('--company', type=str, help='迁移指定公司 (提供公司ID)')
    action_group.add_argument('--all', action='store_true', help='迁移所有公司')
    
    # 模型选项
    parser.add_argument('--model', 
                       default='shibing624/text2vec-base-chinese',
                       help='嵌入模型名称 (默认: shibing624/text2vec-base-chinese)')
    
    args = parser.parse_args()
    
    # 执行操作
    try:
        if args.check:
            check_environment()
        
        elif args.check_db:
            # 运行详细的数据库检查
            import subprocess
            result = subprocess.run([sys.executable, "check_database.py"], 
                                  capture_output=False, text=True)
            sys.exit(result.returncode)
        
        elif args.list_models:
            list_models()
        
        elif args.stats:
            if not check_environment():
                sys.exit(1)
            show_stats()
        
        elif args.company:
            if not check_environment():
                sys.exit(1)
            success = migrate_company(args.company, args.model)
            sys.exit(0 if success else 1)
        
        elif args.all:
            if not check_environment():
                sys.exit(1)
            success = migrate_all_companies(args.model)
            sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
