from django.core.management.base import BaseCommand
from community.models import Topic

class Command(BaseCommand):
    help = '初始化社区话题分类'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始初始化话题分类...')
        
        # 定义默认话题
        topics_data = [
            {'name': '舞蹈技巧', 'description': '分享舞蹈技巧和练习方法', 'icon': 'fas fa-running', 'color': '#D8BF64', 'sort_order': 10},
            {'name': '文化传承', 'description': '探讨非遗舞蹈的历史和文化内涵', 'icon': 'fas fa-book-open', 'color': '#E8D59B', 'sort_order': 9},
            {'name': '学习心得', 'description': '交流学习经验和感悟', 'icon': 'fas fa-lightbulb', 'color': '#F5EDC8', 'sort_order': 8},
            {'name': '作品展示', 'description': '展示个人舞蹈作品和视频', 'icon': 'fas fa-video', 'color': '#D4AF37', 'sort_order': 7},
            {'name': '活动公告', 'description': '发布舞蹈活动和演出信息', 'icon': 'fas fa-calendar-alt', 'color': '#C9A961', 'sort_order': 6},
            {'name': '音乐服饰', 'description': '讨论舞蹈配乐和服装道具', 'icon': 'fas fa-music', 'color': '#E5C585', 'sort_order': 5},
            {'name': '名人名作', 'description': '介绍舞蹈名家和经典作品', 'icon': 'fas fa-star', 'color': '#D7B672', 'sort_order': 4},
            {'name': '地域特色', 'description': '探讨不同地区的舞蹈特色', 'icon': 'fas fa-map-marker-alt', 'color': '#C4A55A', 'sort_order': 3},
            {'name': '教学研讨', 'description': '舞蹈教学方法和理论研究', 'icon': 'fas fa-chalkboard-teacher', 'color': '#D9C078', 'sort_order': 2},
            {'name': '其他', 'description': '其他相关话题', 'icon': 'fas fa-comment', 'color': '#B8A050', 'sort_order': 1},
        ]
        
        created_count = 0
        updated_count = 0
        
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults=topic_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✓ 创建话题：{topic.name}')
            else:
                # 更新现有话题的信息
                for key, value in topic_data.items():
                    if key != 'name':
                        setattr(topic, key, value)
                topic.save()
                updated_count += 1
                self.stdout.write(f'✓ 更新话题：{topic.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n初始化完成！'))
        self.stdout.write(f'新建话题数：{created_count}')
        self.stdout.write(f'更新话题数：{updated_count}')
