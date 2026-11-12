import MySQLdb

# MySQL 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': '123456',
    'db': 'dance_platform',
    'charset': 'utf8mb4'
}

print("=== 正在连接 MySQL 数据库 ===\n")

try:
    conn = MySQLdb.connect(**db_config)
    cursor = conn.cursor()
    
    # 获取所有业务表（排除 Django 系统表）
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'dance_platform' 
        AND table_name NOT LIKE 'django_%' 
        AND table_name NOT LIKE 'auth_%'
        AND table_name NOT LIKE 'admin_%'
        AND table_name NOT LIKE 'contenttypes_%'
        AND table_name NOT LIKE 'sessions_%'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print(f"找到 {len(tables)} 个业务表\n")
    print("=" * 120)
    
    for table in tables:
        table_name = table[0]
        print(f"\n📊 表名: {table_name}")
        print("=" * 120)
        
        # 获取表注释
        cursor.execute(f"""
            SELECT table_comment 
            FROM information_schema.tables 
            WHERE table_schema = 'dance_platform' 
            AND table_name = '{table_name}';
        """)
        comment = cursor.fetchone()
        if comment and comment[0]:
            print(f"表注释: {comment[0]}")
        
        # 获取字段信息
        cursor.execute(f"""
            SELECT 
                COLUMN_NAME as '字段名',
                COLUMN_TYPE as '数据类型',
                IS_NULLABLE as '是否可空',
                COLUMN_DEFAULT as '默认值',
                COLUMN_KEY as '键类型',
                EXTRA as '额外信息',
                COLUMN_COMMENT as '字段注释'
            FROM information_schema.columns 
            WHERE table_schema = 'dance_platform' 
            AND table_name = '{table_name}'
            ORDER BY ORDINAL_POSITION;
        """)
        columns = cursor.fetchall()
        
        print(f"\n{'序号':<5} {'字段名':<35} {'数据类型':<25} {'可空':<8} {'键':<8} {'字段注释':<40}")
        print("-" * 120)
        
        for idx, col in enumerate(columns, 1):
            col_name, col_type, is_null, default, key, extra, comment = col
            nullable = '是' if is_null == 'YES' else '否'
            key_type = key if key else '-'
            comment_str = comment if comment else '-'
            print(f"{idx:<5} {col_name:<35} {col_type:<25} {nullable:<8} {key_type:<8} {comment_str:<40}")
        
        print()
    
    print("\n\n✅ 查询完成！")
    
    conn.close()
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
