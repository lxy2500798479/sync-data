"""
PostgreSQL数据库连接和查询模块
"""

import psycopg2
import psycopg2.extras
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class PostgreSQLConnection:
    """PostgreSQL数据库连接管理器"""
    
    def __init__(self):
        """初始化数据库连接参数"""
        self.connection_params = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', '5432')),
            'database': os.getenv('DATABASE_NAME'),
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD')
        }
        
        # schema配置 (可选，默认为public)
        self.schema = os.getenv('DATABASE_SCHEMA', 'public')
        
        # 验证必要参数
        required_params = ['database', 'user', 'password']
        missing_params = [param for param in required_params if not self.connection_params[param]]
        if missing_params:
            raise ValueError(f"缺少必要的数据库参数: {', '.join(missing_params)}")
        
        print(f"📊 数据库配置: {self.connection_params['database']}.{self.schema}")
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            return psycopg2.connect(**self.connection_params)
        except psycopg2.Error as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
            return False
    
    def check_tables_exist(self) -> Dict[str, bool]:
        """检查知识库相关表是否存在"""
        required_tables = ['knowledge_base_intents', 'knowledge_base_answers']
        table_status = {}
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for table_name in required_tables:
                        # 检查表是否存在
                        cur.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = %s 
                                AND table_name = %s
                            );
                        """, (self.schema, table_name))
                        
                        exists = cur.fetchone()[0]
                        table_status[table_name] = exists
                        
                        if exists:
                            print(f"✅ 表存在: {self.schema}.{table_name}")
                        else:
                            print(f"❌ 表不存在: {self.schema}.{table_name}")
            
            return table_status
            
        except Exception as e:
            print(f"❌ 检查表结构失败: {e}")
            return {table: False for table in required_tables}
    
    def list_all_tables(self) -> List[str]:
        """列出数据库中的所有表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT schemaname, tablename 
                        FROM pg_tables 
                        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
                        ORDER BY schemaname, tablename;
                    """)
                    
                    tables = []
                    print("📋 数据库中的所有表:")
                    for row in cur.fetchall():
                        schema_name, table_name = row
                        full_name = f"{schema_name}.{table_name}"
                        tables.append(full_name)
                        print(f"   {full_name}")
                    
                    return tables
                    
        except Exception as e:
            print(f"❌ 列出表失败: {e}")
            return []
    
    def get_company_intents(self, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取公司的意图数据（不去重，保持原始数据）"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if company_id:
                    cur.execute(f"""
                        SELECT 
                            ki.id,
                            ki.name,
                            ki.keywords,
                            ki.usage_count,
                            ki."isActive" as is_active,
                            ki.is_deleted,
                            ki.created_at,
                            ki.updated_at,
                            ki.company_id
                        FROM "{self.schema}".knowledge_base_intents ki
                        WHERE ki.company_id = %s AND ki.is_deleted = 0 AND ki."isActive" = true
                        ORDER BY ki.created_at ASC
                    """, (company_id,))
                else:
                    cur.execute(f"""
                        SELECT 
                            ki.id,
                            ki.name,
                            ki.keywords,
                            ki.usage_count,
                            ki."isActive" as is_active,
                            ki.is_deleted,
                            ki.created_at,
                            ki.updated_at,
                            ki.company_id
                        FROM "{self.schema}".knowledge_base_intents ki
                        WHERE ki.is_deleted = 0 AND ki."isActive" = true
                        ORDER BY ki.company_id, ki.created_at ASC
                    """)
                
                return [dict(row) for row in cur.fetchall()]
    
    def get_intent_answers(self, intent_id: str) -> List[Dict[str, Any]]:
        """获取意图的答案"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT 
                        id,
                        type,
                        content,
                        "isActive" as is_active,
                        created_at,
                        updated_at
                    FROM "{self.schema}".knowledge_base_answers
                    WHERE intent_id = %s AND is_deleted = 0 AND "isActive" = true
                    ORDER BY created_at ASC
                """, (intent_id,))
                
                return [dict(row) for row in cur.fetchall()]
    
    def get_answers_by_intent_ids(self, intent_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量获取多个意图的答案（性能优化）
        
        Args:
            intent_ids: 意图ID列表
            
        Returns:
            字典，key 是 intent_id，value 是答案列表
        """
        if not intent_ids:
            return {}
        
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT 
                        intent_id,
                        id,
                        type,
                        content,
                        "isActive" as is_active,
                        created_at,
                        updated_at
                    FROM "{self.schema}".knowledge_base_answers
                    WHERE intent_id = ANY(%s) AND is_deleted = 0 AND "isActive" = true
                    ORDER BY intent_id, created_at ASC
                """, (intent_ids,))
                
                # 按 intent_id 分组
                result = {}
                for row in cur.fetchall():
                    row_dict = dict(row)
                    intent_id = row_dict.pop('intent_id')
                    
                    if intent_id not in result:
                        result[intent_id] = []
                    result[intent_id].append(row_dict)
                
                return result
    
    def get_all_companies(self) -> List[Dict[str, Any]]:
        """获取所有公司"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # 注意：这里假设表名是 companies，请根据实际情况调整
                cur.execute(f"""
                    SELECT DISTINCT company_id as id, company_id as name 
                    FROM "{self.schema}".knowledge_base_intents 
                    WHERE company_id IS NOT NULL 
                    ORDER BY company_id
                """)
                return [dict(row) for row in cur.fetchall()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # 统计意图数量
                cur.execute(f"""
                    SELECT 
                        COUNT(*) as total_intents,
                        COUNT(DISTINCT company_id) as total_companies,
                        SUM(array_length(keywords, 1)) as total_questions
                    FROM "{self.schema}".knowledge_base_intents 
                    WHERE is_deleted = 0
                """)
                intent_stats = dict(cur.fetchone())
                
                # 统计答案数量
                cur.execute(f"""
                    SELECT COUNT(*) as total_answers
                    FROM "{self.schema}".knowledge_base_answers 
                    WHERE is_deleted = 0
                """)
                answer_stats = dict(cur.fetchone())
                
                return {**intent_stats, **answer_stats}
