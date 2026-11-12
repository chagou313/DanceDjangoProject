import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')

import django
django.setup()

from quiz.models import Level
from quiz.views import quiz_list
from django.test import RequestFactory
from django.contrib.auth.models import User

# 获取第一个用户
user = User.objects.first()
if not user:
    print("没有用户，请先创建用户")
    exit(1)

print(f"测试用户: {user.username}")

# 创建请求
factory = RequestFactory()
request = factory.get('/quiz/')
request.user = user

# 调用视图
response = quiz_list(request)

print(f"响应状态码: {response.status_code}")
print(f"模板名称: {response.template_name if hasattr(response, 'template_name') else 'N/A'}")

# 检查context
if hasattr(response, 'context_data'):
    levels = response.context_data.get('levels', [])
    print(f"关卡数量: {len(levels)}")
    if levels:
        print(f"第一个关卡: {levels[0]['name']}")
else:
    print("无法获取context_data")

# 直接查询数据库
levels_from_db = Level.objects.filter(is_active=True)
print(f"\n数据库中的关卡数: {levels_from_db.count()}")
for level in levels_from_db[:3]:
    print(f"  - {level.name}")
