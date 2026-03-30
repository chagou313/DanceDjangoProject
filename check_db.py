import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from dance.models import UserProfile
from origin.models import Region

print("\n=== 检查数据库表 ===\n")
print(f'User 表名：{User._meta.db_table}')
print(f'UserProfile 表名：{UserProfile._meta.db_table}')

print(f'\n总用户数：{User.objects.count()}个')
users = User.objects.all()[:5]
for u in users:
    print(f' - {u.username} (ID={u.id})')

print(f'\n总 UserProfile 数：{UserProfile.objects.count()}个')
profiles = UserProfile.objects.select_related('user', 'region').all()[:5]
for p in profiles:
    region_name = p.region.name if p.region else "无"
    print(f' - {p.user.username}: 地区={region_name}')

# 检查新注册的用户
print("\n=== 检查最新注册用户 ===\n")
latest_profiles = UserProfile.objects.select_related('user', 'region').order_by('-created_at')[:3]
for p in latest_profiles:
    print(f'用户：{p.user.username}')
    print(f'  昵称：{p.nickname or "未填写"}')
    print(f'  地区 ID: {p.region.id if p.region else "None"}')
    print(f'  地区名称：{p.region.name if p.region else "未设置"}')
    print()
