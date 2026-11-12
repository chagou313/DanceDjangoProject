import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from knowledge.models import DanceProject, ActionModule, SpecificMove
from origin.models import DanceProject as OriginDanceProject

print("=" * 60)
print("检查知识图谱数据")
print("=" * 60)

# 统计 origin 表
origin_count = OriginDanceProject.objects.count()
print(f"\n📊 Origin 舞蹈项目总数: {origin_count}")

# 统计 knowledge 表
kp_count = DanceProject.objects.count()
print(f"📊 Knowledge 舞蹈项目总数: {kp_count}")

# 统计动作模块
module_count = ActionModule.objects.count()
print(f"📊 动作模块总数: {module_count}")

# 统计招式
move_count = SpecificMove.objects.count()
print(f"📊 具体招式总数: {move_count}")

# 列出前10个有数据的 knowledge 项目
print("\n" + "=" * 60)
print("Knowledge 表中有数据的项目:")
print("=" * 60)

projects_with_data = []
for project in DanceProject.objects.all()[:20]:
    modules = ActionModule.objects.filter(dance_project=project)
    if modules.exists():
        moves_count = SpecificMove.objects.filter(action_module__dance_project=project).count()
        projects_with_data.append({
            'id': project.id,
            'name': project.name,
            'modules': modules.count(),
            'moves': moves_count
        })
        print(f"  [{project.id}] {project.name}")
        print(f"      模块: {modules.count()}, 招式: {moves_count}")

# 列出前10个 origin 项目
print("\n" + "=" * 60)
print("Origin 表中的项目（前10个）:")
print("=" * 60)

for project in OriginDanceProject.objects.all()[:10]:
    # 查找对应的 knowledge 项目
    try:
        kp_project = DanceProject.objects.get(name=project.name)
        has_data = ActionModule.objects.filter(dance_project=kp_project).exists()
        status = "✓ 有数据" if has_data else "✗ 无数据"
        print(f"  [{project.id}] {project.name} -> Knowledge ID: {kp_project.id} {status}")
    except DanceProject.DoesNotExist:
        print(f"  [{project.id}] {project.name} -> ✗ Knowledge 表中不存在")

# 测试特定项目 ID
print("\n" + "=" * 60)
print("测试项目 ID 558:")
print("=" * 60)

try:
    origin_project = OriginDanceProject.objects.get(id=558)
    print(f"Origin 项目: {origin_project.name}")
    
    try:
        kp_project = DanceProject.objects.get(name=origin_project.name)
        print(f"Knowledge 项目: {kp_project.name} (ID: {kp_project.id})")
        
        modules = ActionModule.objects.filter(dance_project=kp_project)
        print(f"动作模块数量: {modules.count()}")
        
        if modules.exists():
            for module in modules:
                moves = SpecificMove.objects.filter(action_module=module)
                print(f"  模块: {module.name} - {moves.count()} 个招式")
        else:
            print("⚠️ 该项目没有动作模块数据！")
            
    except DanceProject.DoesNotExist:
        print("✗ Knowledge 表中找不到对应项目")
        
except OriginDanceProject.DoesNotExist:
    print("✗ Origin 表中不存在 ID 为 558 的项目")
