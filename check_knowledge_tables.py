import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from django.core.management import execute_from_command_line

# 检查知识图谱表
from django.db import connection
cursor = connection.cursor()
cursor.execute("SHOW TABLES LIKE 'knowledge_%'")
tables = cursor.fetchall()

print("=" * 80)
print("知识图谱数据表检查")
print("=" * 80)

if tables:
    print(f"\n找到 {len(tables)} 个知识图谱表:")
    for table in tables:
        print(f"  ✓ {table[0]}")
else:
    print("\n⚠️  未找到知识图谱表，需要重新创建迁移")
    print("\n执行以下步骤:")
    print("1. 删除 knowledge/migrations/0001_initial.py")
    print("2. 运行: python manage.py makemigrations knowledge")
    print("3. 运行: python manage.py migrate knowledge")

print("=" * 80)
