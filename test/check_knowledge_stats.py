from knowledge.models import DanceProject, ActionModule, SpecificMove

projects_with_data = DanceProject.objects.exclude(action_modules__isnull=True).distinct()
print(f'\n✅ 已生成知识图谱数据的非遗项目: {projects_with_data.count()}个\n')
print('=' * 60)

print('\n项目分类统计:\n')
from django.db.models import Count
categories = projects_with_data.values('category').annotate(count=Count('id')).order_by('category')
for cat in categories:
    print(f'  {cat["category"]}: {cat["count"]}个')

print('\n' + '=' * 60)
print('\n最新生成的项目:\n')
latest = projects_with_data.order_by('-id')[:15]
for i, p in enumerate(latest, 1):
    module_count = p.action_modules.count()
    move_count = SpecificMove.objects.filter(action_module__dance_project=p).count()
    print(f'  {i:2d}. {p.name:20s} ({p.category}) - {module_count}模块, {move_count}招式')

print('\n' + '=' * 60)
total_moves = SpecificMove.objects.filter(action_module__dance_project__in=projects_with_data).count()
print(f'\n总计: {projects_with_data.count()}个项目, {total_moves}个招式')
