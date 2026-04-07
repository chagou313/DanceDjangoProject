"""
非遗传统舞蹈知识图谱数据生成脚本
为356个舞蹈项目生成完整的知识图谱数据：
- 基础动作模块
- 具体招式
- 动作属性（发力部位、易错点、标准要领）
- 学习资源（教学视频、传承人示范）
- 知识点标签
"""

import os
import django
import random
from datetime import datetime
from django.core.management.base import BaseCommand

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DancedjangoProject.settings')
django.setup()

from origin.models import DanceProject as OriginDanceProject
from knowledge.models import (
    DanceProject, ActionModule, SpecificMove, 
    MoveAttribute, LearningResource, KnowledgePoint
)

# ==================== 知识库模板数据 ====================

# 基础动作模块模板（按舞蹈类型分类）
ACTION_MODULES_TEMPLATES = {
    'classical': [
        {'name': '基本功训练', 'description': '古典舞基础功法和身韵训练'},
        {'name': '身韵组合', 'description': '提沉冲靠含腆移等身韵元素'},
        {'name': '技术技巧', 'description': '旋转、跳跃、翻腾等技术动作'},
        {'name': '剧目片段', 'description': '经典剧目中的代表性舞段'},
    ],
    'folk': [
        {'name': '基本步法', 'description': '民族舞蹈的基础步伐训练'},
        {'name': '手势训练', 'description': '具有民族特色的手部动作'},
        {'name': '韵律组合', 'description': '体现民族风格的韵律练习'},
        {'name': '民俗表演', 'description': '结合民俗活动的舞蹈表演'},
    ],
    'traditional': [
        {'name': '基础姿态', 'description': '传统舞蹈的基本站姿和手位'},
        {'name': '行进动作', 'description': '传统舞蹈的移动和队形变化'},
        {'name': '祭祀仪式', 'description': '与祭祀活动相关的仪式性舞蹈'},
        {'name': '节庆表演', 'description': '传统节日庆典中的舞蹈形式'},
    ],
    'ethnic': [
        {'name': '民族特色动作', 'description': '各民族独有的舞蹈语汇'},
        {'name': '生活劳作模拟', 'description': '模仿生产生活的舞蹈动作'},
        {'name': '情感表达', 'description': '通过舞蹈表达民族情感'},
        {'name': '群体互动', 'description': '多人参与的集体舞蹈形式'},
    ],
}

# 具体招式模板（按模块类型）
SPECIFIC_MOVES_TEMPLATES = {
    '基本功训练': [
        {'name': '压腿', 'difficulty': 2, 'duration': 60},
        {'name': '下腰', 'difficulty': 3, 'duration': 45},
        {'name': '踢腿', 'difficulty': 2, 'duration': 90},
        {'name': '控腿', 'difficulty': 4, 'duration': 30},
    ],
    '身韵组合': [
        {'name': '提沉练习', 'difficulty': 2, 'duration': 120},
        {'name': '冲靠训练', 'difficulty': 3, 'duration': 90},
        {'name': '含腆组合', 'difficulty': 3, 'duration': 100},
        {'name': '云手圆场', 'difficulty': 4, 'duration': 150},
    ],
    '技术技巧': [
        {'name': '平转', 'difficulty': 5, 'duration': 60},
        {'name': '大跳', 'difficulty': 6, 'duration': 45},
        {'name': '倒踢紫金冠', 'difficulty': 7, 'duration': 30},
        {'name': '串翻身', 'difficulty': 6, 'duration': 50},
    ],
    '基本步法': [
        {'name': '圆场步', 'difficulty': 2, 'duration': 120},
        {'name': '碎步', 'difficulty': 2, 'duration': 90},
        {'name': '十字步', 'difficulty': 3, 'duration': 100},
        {'name': '踏步', 'difficulty': 2, 'duration': 80},
    ],
    '手势训练': [
        {'name': '兰花指', 'difficulty': 1, 'duration': 60},
        {'name': '掌式变化', 'difficulty': 2, 'duration': 90},
        {'name': '手腕转动', 'difficulty': 2, 'duration': 75},
        {'name': '手臂波浪', 'difficulty': 3, 'duration': 100},
    ],
    '基础姿态': [
        {'name': '正步站立', 'difficulty': 1, 'duration': 60},
        {'name': '丁字步', 'difficulty': 1, 'duration': 60},
        {'name': '弓箭步', 'difficulty': 2, 'duration': 45},
        {'name': '虚步', 'difficulty': 2, 'duration': 50},
    ],
    '行进动作': [
        {'name': '前进后退', 'difficulty': 1, 'duration': 90},
        {'name': '左右横移', 'difficulty': 2, 'duration': 80},
        {'name': '绕圈行进', 'difficulty': 3, 'duration': 120},
        {'name': '队形变换', 'difficulty': 4, 'duration': 150},
    ],
}

# 动作属性模板
MOVE_ATTRIBUTES_TEMPLATES = {
    '压腿': {
        'force_parts': '腿部肌肉、髋关节、腰部',
        'common_mistakes': '膝盖弯曲、身体前倾过度、呼吸不均匀',
        'key_points': '保持腿部伸直，缓慢下压，配合深呼吸，循序渐进',
        'precautions': '热身充分，避免用力过猛导致拉伤',
    },
    '提沉练习': {
        'force_parts': '腰部、腹部、背部肌群',
        'common_mistakes': '只动上半身、忽略气息配合、动作僵硬',
        'key_points': '以腰带身，气沉丹田，动作圆润流畅，意念引导',
        'precautions': '注意呼吸节奏，避免憋气',
    },
    '平转': {
        'force_parts': '腰部核心、腿部、脚踝',
        'common_mistakes': '重心不稳、视线不固定、手臂位置不正确',
        'key_points': '留头甩头、立半脚尖、收紧核心、双臂展开保持平衡',
        'precautions': '先在把杆练习，确保平衡能力',
    },
    '圆场步': {
        'force_parts': '小腿、脚踝、膝盖',
        'common_mistakes': '脚步过大、身体起伏明显、节奏不均匀',
        'key_points': '小步快频、脚跟先着地、上身平稳、如行云流水',
        'precautions': '保持膝盖微屈，避免僵硬',
    },
    '兰花指': {
        'force_parts': '手指、手腕',
        'common_mistakes': '手指过于用力、手腕僵硬、形态不优美',
        'key_points': '拇指中指相捏，其余三指自然翘起，手腕放松柔和',
        'precautions': '不要过度用力，保持自然优雅',
    },
}

# 默认动作属性（通用模板）
DEFAULT_ATTRIBUTES = {
    'force_parts': '根据具体动作确定主要发力的肌肉群和关节',
    'common_mistakes': '动作不到位、节奏不准确、身体协调性不足',
    'key_points': '注重动作的规范性、流畅性和美感，反复练习形成肌肉记忆',
    'precautions': '充分热身，量力而行，注意安全防护',
}

# 学习资源模板
LEARNING_RESOURCES_TEMPLATES = [
    {
        'resource_type': 'video',
        'title_prefix': '【教学视频】',
        'title_suffix': '详细讲解与示范',
        'url_template': 'https://example.com/video/{project_name}/{move_name}',
    },
    {
        'resource_type': 'demo',
        'title_prefix': '【传承人示范】',
        'title_suffix': '国家级传承人亲自演示',
        'url_template': 'https://example.com/demo/{project_name}/{move_name}',
    },
    {
        'resource_type': 'article',
        'title_prefix': '【图文教程】',
        'title_suffix': '分解动作详解',
        'url_template': 'https://example.com/article/{project_name}/{move_name}',
    },
]

# 知识点标签模板
KNOWLEDGE_POINTS_TEMPLATES = [
    {
        'name': '呼吸配合',
        'description': '舞蹈动作与呼吸的协调配合，是舞蹈表现力的重要基础',
        'category': '基础理论',
        'importance_level': 5,
    },
    {
        'name': '身体协调',
        'description': '全身各部位的协调运动，保证动作的流畅性和美感',
        'category': '技能要点',
        'importance_level': 5,
    },
    {
        'name': '节奏感',
        'description': '对音乐节拍和舞蹈节奏的准确把握',
        'category': '音乐素养',
        'importance_level': 4,
    },
    {
        'name': '文化背景',
        'description': '了解舞蹈背后的历史文化内涵和民俗意义',
        'category': '文化知识',
        'importance_level': 4,
    },
    {
        'name': '表情管理',
        'description': '面部表情与舞蹈情感的统一表达',
        'category': '表演技巧',
        'importance_level': 3,
    },
    {
        'name': '空间意识',
        'description': '对舞台空间和队形变化的感知与运用',
        'category': '舞台表现',
        'importance_level': 3,
    },
]


def get_or_create_dance_project(origin_project):
    """获取或创建知识图谱中的舞蹈项目"""
    dance_project, created = DanceProject.objects.get_or_create(
        name=origin_project.name,
        defaults={
            'description': origin_project.introduction or f'{origin_project.name}是{origin_project.get_level_display()}非物质文化遗产项目',
            'category': origin_project.get_dance_type_display(),
            'difficulty_level': random.randint(1, 5),
        }
    )
    return dance_project, created


def create_action_modules(dance_project, dance_type):
    """为基础动作模块创建数据"""
    templates = ACTION_MODULES_TEMPLATES.get(dance_type, ACTION_MODULES_TEMPLATES['traditional'])
    modules = []
    
    for idx, template in enumerate(templates):
        module, created = ActionModule.objects.get_or_create(
            dance_project=dance_project,
            name=template['name'],
            defaults={
                'description': template['description'],
                'order_index': idx,
            }
        )
        modules.append(module)
    
    return modules


def create_specific_moves(action_module, module_name):
    """为具体招式创建数据"""
    templates = SPECIFIC_MOVES_TEMPLATES.get(module_name, [
        {'name': f'{module_name}动作一', 'difficulty': 3, 'duration': 60},
        {'name': f'{module_name}动作二', 'difficulty': 4, 'duration': 90},
        {'name': f'{module_name}动作三', 'difficulty': 3, 'duration': 75},
    ])
    
    moves = []
    for idx, template in enumerate(templates):
        move, created = SpecificMove.objects.get_or_create(
            action_module=action_module,
            name=template['name'],
            defaults={
                'description': f'{template["name"]}是{action_module.name}中的重要招式',
                'difficulty': template['difficulty'],
                'duration': template['duration'],
                'order_index': idx,
            }
        )
        moves.append(move)
    
    return moves


def create_move_attributes(specific_move, move_name=None):
    """为招式创建动作属性"""
    # 尝试使用特定模板
    attributes_data = MOVE_ATTRIBUTES_TEMPLATES.get(move_name or specific_move.name, DEFAULT_ATTRIBUTES)
    
    attr, created = MoveAttribute.objects.get_or_create(
        specific_move=specific_move,
        defaults=attributes_data
    )
    return attr


def create_learning_resources(specific_move, project_name):
    """为招式创建学习资源"""
    resources = []
    
    for resource_template in LEARNING_RESOURCES_TEMPLATES:
        title = f"{resource_template['title_prefix']}{specific_move.name}{resource_template['title_suffix']}"
        
        resource, created = LearningResource.objects.get_or_create(
            specific_move=specific_move,
            resource_type=resource_template['resource_type'],
            title=title,
            defaults={
                'url': resource_template['url_template'].format(
                    project_name=project_name,
                    move_name=specific_move.name
                ),
                'description': f'关于{specific_move.name}的{resource_template["title_suffix"]}',
                'duration': random.randint(60, 600) if resource_template['resource_type'] in ['video', 'demo'] else None,
            }
        )
        resources.append(resource)
    
    return resources


def create_knowledge_points(specific_move):
    """为招式创建知识点标签"""
    points = []
    
    # 随机选择3-5个知识点
    selected_points = random.sample(KNOWLEDGE_POINTS_TEMPLATES, k=random.randint(3, 5))
    
    for point_data in selected_points:
        point, created = KnowledgePoint.objects.get_or_create(
            specific_move=specific_move,
            name=point_data['name'],
            defaults={
                'description': point_data['description'],
                'category': point_data['category'],
                'importance_level': point_data['importance_level'],
            }
        )
        points.append(point)
    
    return points


def generate_knowledge_graph_for_project(origin_project, cmd=None):
    """为单个舞蹈项目生成完整的知识图谱"""
    if cmd:
        cmd.stdout.write(f"处理项目: {origin_project.name} ({origin_project.project_code})")
    else:
        print(f"\n处理项目: {origin_project.name} ({origin_project.project_code})")
    
    # 1. 创建或获取舞蹈项目
    dance_project, project_created = get_or_create_dance_project(origin_project)
    if not project_created:
        if cmd:
            cmd.stdout.write(cmd.style.WARNING(f"  ⚠️  项目已存在，跳过"))
        else:
            print(f"  ⚠️  项目已存在，跳过")
        return False
    
    # 获取舞蹈类型
    dance_type = origin_project.dance_type
    
    # 2. 创建基础动作模块
    modules = create_action_modules(dance_project, dance_type)
    if cmd:
        cmd.stdout.write(cmd.style.SUCCESS(f"  [OK] 创建了 {len(modules)} 个基础动作模块"))
    else:
        print(f"  ✓ 创建了 {len(modules)} 个基础动作模块")
    
    total_moves = 0
    total_resources = 0
    total_points = 0
    
    # 3. 为每个模块创建具体招式及相关数据
    for module in modules:
        moves = create_specific_moves(module, module.name)
        total_moves += len(moves)
        
        for move in moves:
            # 创建动作属性
            create_move_attributes(move, move.name)
            
            # 创建学习资源
            resources = create_learning_resources(move, origin_project.name)
            total_resources += len(resources)
            
            # 创建知识点标签
            points = create_knowledge_points(move)
            total_points += len(points)
    
    if cmd:
        cmd.stdout.write(cmd.style.SUCCESS(f"  [OK] 创建了 {total_moves} 个具体招式"))
        cmd.stdout.write(cmd.style.SUCCESS(f"  [OK] 创建了 {total_resources} 个学习资源"))
        cmd.stdout.write(cmd.style.SUCCESS(f"  [OK] 创建了 {total_points} 个知识点标签"))
    else:
        print(f"  ✓ 创建了 {total_moves} 个具体招式")
        print(f"  ✓ 创建了 {total_resources} 个学习资源")
        print(f"  ✓ 创建了 {total_points} 个知识点标签")
    
    return True


class Command(BaseCommand):
    help = '为356个非遗传统舞蹈项目生成完整的知识图谱数据集'

    def handle(self, *args, **options):
        """主函数：为所有356个舞蹈项目生成知识图谱"""
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('开始生成非遗传统舞蹈知识图谱数据集'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        # 获取所有舞蹈项目
        origin_projects = OriginDanceProject.objects.all()
        total_count = origin_projects.count()
        
        self.stdout.write(f'\n共有 {total_count} 个舞蹈项目需要处理\n')
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for idx, origin_project in enumerate(origin_projects, 1):
            try:
                self.stdout.write(f'[{idx}/{total_count}]', ending=' ')
                result = generate_knowledge_graph_for_project(origin_project, self)
                if result:
                    success_count += 1
                else:
                    skip_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] 错误: {str(e)}'))
                error_count += 1
        
        # 统计结果
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('知识图谱数据生成完成！'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(f'成功生成: {success_count} 个项目')
        self.stdout.write(f'跳过(已存在): {skip_count} 个项目')
        self.stdout.write(f'错误: {error_count} 个项目')
        self.stdout.write(f'\n数据统计:')
        self.stdout.write(f'  - 舞蹈项目: {DanceProject.objects.count()}')
        self.stdout.write(f'  - 基础动作模块: {ActionModule.objects.count()}')
        self.stdout.write(f'  - 具体招式: {SpecificMove.objects.count()}')
        self.stdout.write(f'  - 动作属性: {MoveAttribute.objects.count()}')
        self.stdout.write(f'  - 学习资源: {LearningResource.objects.count()}')
        self.stdout.write(f'  - 知识点标签: {KnowledgePoint.objects.count()}')
        self.stdout.write(self.style.SUCCESS('=' * 80))
