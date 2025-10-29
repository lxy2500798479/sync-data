#!/usr/bin/env python3
"""
数据库表结构检查工具
"""

import os
import sys
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sync_data.database import PostgreSQLConnection


def check_database_structure():
    """检查数据库结构"""
    print("🔍 数据库结构检查")
    print("=" * 50)
    
    try:
        db = PostgreSQLConnection()
        
        # 测试连接
        if not db.test_connection():
            print("❌ 数据库连接失败，请检查配置")
            return
        
        print("✅ 数据库连接成功")
        
        # 列出所有表
        print("\n📋 数据库中的所有表:")
        all_tables = db.list_all_tables()
        
        if not all_tables:
            print("   没有找到任何表")
            return
        
        # 检查知识库相关表
        print("\n🔍 检查知识库相关表:")
        table_status = db.check_tables_exist()
        
        missing_tables = [table for table, exists in table_status.items() if not exists]
        
        if missing_tables:
            print(f"\n❌ 缺少以下表:")
            for table in missing_tables:
                print(f"   - {db.schema}.{table}")
            
            print(f"\n💡 可能的原因:")
            print(f"   1. Schema配置错误 (当前: {db.schema})")
            print(f"   2. 表名不正确")
            print(f"   3. 数据库不是知识库系统的数据库")
            
            # 搜索相似表名
            print(f"\n🔍 搜索相似表名:")
            for missing_table in missing_tables:
                similar_tables = [t for t in all_tables if missing_table.split('.')[-1] in t.lower()]
                if similar_tables:
                    print(f"   {missing_table} 的相似表:")
                    for similar in similar_tables:
                        print(f"      - {similar}")
                else:
                    print(f"   未找到与 {missing_table} 相似的表")
        else:
            print("✅ 所有必需的表都存在")
            
            # 尝试获取统计信息
            print(f"\n📊 尝试获取数据统计:")
            try:
                stats = db.get_database_stats()
                print(f"   公司数量: {stats.get('total_companies', 0)}")
                print(f"   意图数量: {stats.get('total_intents', 0)}")
                print(f"   问题数量: {stats.get('total_questions', 0)}")
                print(f"   答案数量: {stats.get('total_answers', 0)}")
            except Exception as e:
                print(f"   ❌ 获取统计失败: {e}")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")


def suggest_schema_fix():
    """建议Schema修复方案"""
    print(f"\n💡 Schema配置建议:")
    print(f"-" * 30)
    
    current_schema = os.getenv('DATABASE_SCHEMA', 'public')
    print(f"当前Schema: {current_schema}")
    
    print(f"\n🔧 修复方法:")
    print(f"1. 检查.env文件，添加正确的Schema:")
    print(f"   DATABASE_SCHEMA=your_actual_schema")
    
    common_schemas = ['public', 'knowledge_base', 'kb', 'main', 'app']
    print(f"\n2. 常见Schema名称:")
    for schema in common_schemas:
        print(f"   - {schema}")
    
    print(f"\n3. 查找正确Schema的方法:")
    print(f"   在PostgreSQL中执行:")
    print(f"   SELECT schemaname, tablename FROM pg_tables WHERE tablename LIKE '%knowledge%';")


def interactive_schema_test():
    """交互式Schema测试"""
    print(f"\n🎯 交互式Schema测试")
    print(f"-" * 30)
    
    print("请输入要测试的Schema名称 (回车跳过):")
    
    while True:
        schema_input = input("Schema名称: ").strip()
        
        if not schema_input:
            break
        
        try:
            # 临时设置schema
            os.environ['DATABASE_SCHEMA'] = schema_input
            
            # 重新创建连接
            db = PostgreSQLConnection()
            table_status = db.check_tables_exist()
            
            missing_tables = [table for table, exists in table_status.items() if not exists]
            
            if not missing_tables:
                print(f"✅ Schema '{schema_input}' 中找到了所有必需的表!")
                print(f"   建议在.env文件中设置: DATABASE_SCHEMA={schema_input}")
                break
            else:
                print(f"❌ Schema '{schema_input}' 中缺少表: {missing_tables}")
        
        except Exception as e:
            print(f"❌ 测试Schema '{schema_input}' 失败: {e}")


def main():
    """主函数"""
    print("🔍 知识库数据库结构检查工具")
    print("=" * 60)
    
    # 检查环境变量
    required_vars = ['DATABASE_HOST', 'DATABASE_NAME', 'DATABASE_USER', 'DATABASE_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请先配置.env文件")
        return
    
    # 检查数据库结构
    check_database_structure()
    
    # 建议修复方案
    suggest_schema_fix()
    
    # 交互式测试
    try:
        interactive_schema_test()
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")


if __name__ == "__main__":
    main()
