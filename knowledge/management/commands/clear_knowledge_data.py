"""
清除所有知识图谱数据
使用方法: python manage.py clear_knowledge_data
"""
from django.core.management.base import BaseCommand
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint


class Command(BaseCommand):
    help = '清除所有知识图谱数据'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('开始清除所有知识图谱数据'))
        self.stdout.write(self.style.WARNING('=' * 70))
        
        # 统计当前数据量
        project_count = DanceProject.objects.count()
        module_count = ActionModule.objects.count()
        move_count = SpecificMove.objects.count()
        attr_count = MoveAttribute.objects.count()
        resource_count = LearningResource.objects.count()
        kp_count = KnowledgePoint.objects.count()
        
        self.stdout.write(f'\n当前数据量:')
        self.stdout.write(f'  项目数: {project_count}')
        self.stdout.write(f'  模块数: {module_count}')
        self.stdout.write(f'  招式数: {move_count}')
        self.stdout.write(f'  属性数: {attr_count}')
        self.stdout.write(f'  资源数: {resource_count}')
        self.stdout.write(f'  知识点数: {kp_count}')
        
        confirm = input('\n确定要清除所有数据吗？(yes/no): ')
        
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.SUCCESS('操作已取消'))
            return
        
        self.stdout.write('\n正在清除数据...')
        
        # 按依赖关系删除（从子到父）
        KnowledgePoint.objects.all().delete()
        self.stdout.write('  ✓ 已清除知识点')
        
        LearningResource.objects.all().delete()
        self.stdout.write('  ✓ 已清除学习资源')
        
        MoveAttribute.objects.all().delete()
        self.stdout.write('  ✓ 已清除动作属性')
        
        SpecificMove.objects.all().delete()
        self.stdout.write('  ✓ 已清除招式')
        
        ActionModule.objects.all().delete()
        self.stdout.write('  ✓ 已清除动作模块')
        
        DanceProject.objects.all().delete()
        self.stdout.write('  ✓ 已清除舞蹈项目')
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('所有知识图谱数据已清除！'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
