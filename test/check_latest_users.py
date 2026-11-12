import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from dance.models import UserProfile

print("\n=== 最新的 3 个用户 ===\n")

users = User.objects.order_by('-id')[:3]
for u in users:
    try:
        profile = UserProfile.objects.get(user=u)
        region_name = profile.region.name if profile.region else "未设置"
        print(f"用户名：{u.username} (ID={u.id})")
        print(f"  地区：{region_name}")
        print(f"  地区 ID: {profile.region.id if profile.region else 'None'}")
        print()
    except UserProfile.DoesNotExist:
        print(f"用户名：{u.username} - UserProfile 不存在")
        print()
