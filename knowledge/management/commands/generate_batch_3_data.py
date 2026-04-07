"""
批量生成第三批50个真实非遗舞蹈项目知识图谱数据
使用方法: python manage.py generate_batch_3_data
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '批量生成第三批50个非遗舞蹈项目知识图谱数据'

    def handle(self, *args, **options):
        from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
        from origin.models import DanceProject as OriginProject
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('开始生成第三批非遗舞蹈知识图谱数据'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 获取已生成知识图谱数据的项目名称
        existing_names = set(
            ActionModule.objects.values_list('dance_project__name', flat=True).distinct()
        )
        self.stdout.write(f'已有 {len(existing_names)} 个项目生成了知识图谱数据\n')
        
        # 从origin获取真实项目，排除已生成的
        all_origin_projects = OriginProject.objects.exclude(name__in=existing_names).order_by('id')
        total_available = all_origin_projects.count()
        self.stdout.write(f'origin中共有 {total_available} 个未生成的项目\n')
        
        if total_available == 0:
            self.stdout.write(self.style.WARNING('没有更多项目可以生成！'))
            return
        
        # 选取最多50个项目
        selected_projects = list(all_origin_projects[:50])
        self.stdout.write(f'选中 {len(selected_projects)} 个项目\n')
        
        success_count = 0
        for i, origin_project in enumerate(selected_projects, 1):
            name = origin_project.name
            
            try:
                # 检查knowledge中是否已存在
                existing = DanceProject.objects.filter(name=name).first()
                if existing:
                    # 删除旧数据
                    existing.delete()
                
                # 创建项目
                project = DanceProject.objects.create(
                    name=name,
                    category=origin_project.get_dance_type_display() if hasattr(origin_project, 'get_dance_type_display') else '传统舞',
                    description=origin_project.declare_region if hasattr(origin_project, 'declare_region') else '传统舞蹈项目',
                    difficulty_level=3,
                )
                
                self.stdout.write(f'[{i}/{len(selected_projects)}] 正在生成: {name}')
                
                # 根据名称特征确定类型
                project_type = determine_type(name)
                modules_config = get_modules_config(name, project_type)
                
                total_moves = 0
                for j, (module_name, module_desc, module_type) in enumerate(modules_config, 1):
                    module = ActionModule.objects.create(
                        dance_project=project,
                        name=module_name,
                        description=module_desc,
                        order_index=j
                    )
                    
                    moves_count = 3 if j == 1 else 2
                    for k in range(1, moves_count + 1):
                        create_move(module, k, name, module_type)
                    
                    moves_count = module.specific_moves.count()
                    total_moves += moves_count
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ {name} 完成 - 共{total_moves}个招式'))
                success_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ {name} 失败: {str(e)[:100]}'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS(f'第三批数据生成完成！成功: {success_count}/{len(selected_projects)}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))


def determine_type(name):
    """根据项目名称确定类型"""
    if '鼓' in name:
        return 'drum'
    elif any(x in name for x in ['棍', '板', '鞭', '虎', '牛']):
        return 'martial'
    elif any(x in name for x in ['族', '藏', '蒙', '维吾尔', '哈萨克', '彝', '苗', '侗', '壮', '瑶', '白', '哈尼', '土家', '傣', '黎', '纳西', '达斡尔', '鄂温克', '锡伯', '俄罗斯']):
        return 'ethnic'
    else:
        return 'folk'


def get_modules_config(name, project_type):
    """根据项目类型获取模块配置"""
    if project_type == 'drum':
        return [
            ('基本鼓法模块', f'{name}的基础击鼓技法训练。', 'drum_basic'),
            ('跳跃动作模块', f'{name}特色的跳跃和腾挪动作。', 'drum_jump'),
            ('队形变化模块', f'{name}集体表演时的队形编排。', 'formation'),
        ]
    elif project_type == 'martial':
        return [
            ('基本武术模块', f'{name}的基础武术动作训练。', 'martial_basic'),
            ('器械技法模块', f'{name}的器械运用技法。', 'weapon_tech'),
            ('实战演练模块', f'{name}的实战演练技巧。', 'combat'),
        ]
    elif project_type == 'ethnic':
        return [
            ('基本手姿模块', f'{name}的特色手部姿势训练。', 'ethnic_hand'),
            ('身段韵律模块', f'{name}的身体韵律美感训练。', 'ethnic_body'),
            ('特色技法模块', f'{name}特有的民族舞蹈技法。', 'ethnic_special'),
        ]
    else:
        return [
            ('基本步法模块', f'{name}的基础步伐训练。', 'step_basic'),
            ('手势身段模块', f'{name}的手部动作训练。', 'hand_posture'),
            ('表演技巧模块', f'{name}的表演技巧训练。', 'performance'),
        ]


def create_move(module, index, project_name, module_type):
    """创建招式"""
    move_templates = get_move_templates(module_type, project_name)
    move_data = move_templates[(index - 1) % len(move_templates)]
    
    from knowledge.models import SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
    
    move = SpecificMove.objects.create(
        action_module=module,
        name=move_data['name'],
        description=move_data['description'],
        difficulty=move_data['difficulty'],
        duration=move_data['duration'],
        order_index=index
    )
    
    MoveAttribute.objects.create(specific_move=move, **move_data['attributes'])
    
    for res_type in ['video', 'demo']:
        LearningResource.objects.create(
            specific_move=move,
            resource_type=res_type,
            title=f'{move.name}教学视频',
            url=f'https://example.com/resource/{move.name}_{res_type}',
            duration=move_data['duration'] - 60,
            order_index=1
        )
    
    for k, kp_cat in enumerate(['技法要点', '文化内涵', '表演技巧']):
        KnowledgePoint.objects.create(
            specific_move=move,
            name=f'{move.name}的{kp_cat}',
            description=f'{move.name}的{kp_cat}要点',
            category=kp_cat,
            importance_level=4 if k == 0 else 3
        )


def get_move_templates(module_type, project_name):
    """根据模块类型返回对应的招式模板"""
    templates = {
        'drum_basic': get_drum_basic_moves,
        'drum_jump': get_drum_jump_moves,
        'formation': get_formation_moves,
        'martial_basic': get_martial_basic_moves,
        'weapon_tech': get_weapon_tech_moves,
        'combat': get_combat_moves,
        'step_basic': get_step_basic_moves,
        'hand_posture': get_hand_posture_moves,
        'performance': get_performance_moves,
        'ethnic_hand': get_ethnic_hand_moves,
        'ethnic_body': get_ethnic_body_moves,
        'ethnic_special': get_ethnic_special_moves,
    }
    func = templates.get(module_type, get_general_moves)
    return func(project_name)


def get_drum_basic_moves(project_name):
    return [
        {'name': '单点击鼓', 'description': f'{project_name}的基础击鼓技法。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '手腕发力', 'common_mistakes': '击鼓位置不准', 'key_points': '击鼓中心', 'precautions': '循序渐进'}},
        {'name': '双击连奏', 'description': f'快速连续两次击鼓。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '手腕弹动', 'common_mistakes': '间隔不均', 'key_points': '节奏均匀', 'precautions': '先慢后快'}},
        {'name': '滚奏技法', 'description': f'连续快速击鼓形成滚动效果。', 'difficulty': 6, 'duration': 360, 'attributes': {'force_parts': '手腕持续运动', 'common_mistakes': '频率不均', 'key_points': '频率稳定', 'precautions': '保护手腕'}},
    ]

def get_drum_jump_moves(project_name):
    return [
        {'name': '跃步击鼓', 'description': f'跳起在空中击鼓。', 'difficulty': 5, 'duration': 320, 'attributes': {'force_parts': '腿部爆发力', 'common_mistakes': '落地不稳', 'key_points': '蹬地有力', 'precautions': '注意膝盖保护'}},
        {'name': '转身跳击', 'description': f'跳起转身击鼓。', 'difficulty': 7, 'duration': 380, 'attributes': {'force_parts': '腰部扭转', 'common_mistakes': '转身不完整', 'key_points': '转体迅速', 'precautions': '循序渐进'}},
    ]

def get_formation_moves(project_name):
    return [
        {'name': '圆圈围鼓', 'description': f'多人围圈同步击鼓。', 'difficulty': 3, 'duration': 300, 'attributes': {'force_parts': '团队配合', 'common_mistakes': '队形不齐', 'key_points': '保持等距', 'precautions': '避免碰撞'}},
        {'name': '交叉换位', 'description': f'队员交叉穿行换位。', 'difficulty': 5, 'duration': 360, 'attributes': {'force_parts': '腿部移动', 'common_mistakes': '路线混乱', 'key_points': '按路线行进', 'precautions': '注意安全'}},
    ]

def get_martial_basic_moves(project_name):
    return [
        {'name': '马步站桩', 'description': f'{project_name}的基础站桩。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '大腿发力', 'common_mistakes': '膝盖内扣', 'key_points': '含胸拔背', 'precautions': '时间不宜过长'}},
        {'name': '弓步冲拳', 'description': f'弓箭步冲拳。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '腰部扭转', 'common_mistakes': '出拳无力', 'key_points': '髋部正对前方', 'precautions': '膝盖与脚尖一致'}},
        {'name': '虚步亮掌', 'description': f'虚步亮掌。', 'difficulty': 3, 'duration': 270, 'attributes': {'force_parts': '手臂伸展', 'common_mistakes': '重心不稳', 'key_points': '支撑腿稳固', 'precautions': '保护膝关节'}},
    ]

def get_weapon_tech_moves(project_name):
    return [
        {'name': '持械站立', 'description': f'{project_name}的基本持械姿势。', 'difficulty': 2, 'duration': 200, 'attributes': {'force_parts': '核心收紧', 'common_mistakes': '重心不稳', 'key_points': '器械护身', 'precautions': '肩膀放松'}},
        {'name': '器械挥舞', 'description': f'{project_name}的器械挥舞技法。', 'difficulty': 5, 'duration': 320, 'attributes': {'force_parts': '全身协调', 'common_mistakes': '动作僵硬', 'key_points': '攻防一体', 'precautions': '注意安全'}},
    ]

def get_combat_moves(project_name):
    return [
        {'name': '进退攻防', 'description': f'前进后退攻防演练。', 'difficulty': 5, 'duration': 340, 'attributes': {'force_parts': '全身协调', 'common_mistakes': '步法混乱', 'key_points': '攻防转换迅速', 'precautions': '控制力度'}},
        {'name': '连环进击', 'description': f'连续多次进攻动作。', 'difficulty': 7, 'duration': 380, 'attributes': {'force_parts': '连续发力', 'common_mistakes': '动作脱节', 'key_points': '动作连贯', 'precautions': '体力分配'}},
    ]

def get_step_basic_moves(project_name):
    return [
        {'name': '十字步', 'description': f'{project_name}的基础步伐。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '腿部交替', 'common_mistakes': '步伐沉重', 'key_points': '脚步轻灵', 'precautions': '注意脚下安全'}},
        {'name': '颤步扭腰', 'description': f'膝盖颤动腰部扭动。', 'difficulty': 3, 'duration': 280, 'attributes': {'force_parts': '膝盖弹动', 'common_mistakes': '上下脱节', 'key_points': '膝颤腰扭协调', 'precautions': '腰部热身'}},
        {'name': '跳步转身', 'description': f'单脚跳起转身。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '腿部爆发力', 'common_mistakes': '落地不稳', 'key_points': '跳跃轻盈', 'precautions': '脚踝保护'}},
    ]

def get_hand_posture_moves(project_name):
    return [
        {'name': '云手翻花', 'description': f'双手云手翻花。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '手腕旋转', 'common_mistakes': '手腕僵硬', 'key_points': '以腕为轴', 'precautions': '循序渐进'}},
        {'name': '托手亮相', 'description': f'单手托起亮相。', 'difficulty': 3, 'duration': 240, 'attributes': {'force_parts': '手臂上举', 'common_mistakes': '耸肩', 'key_points': '沉肩坠肘', 'precautions': '肩部放松'}},
    ]

def get_performance_moves(project_name):
    return [
        {'name': '表情运用', 'description': f'{project_name}的面部表情技巧。', 'difficulty': 3, 'duration': 260, 'attributes': {'force_parts': '面部控制', 'common_mistakes': '表情僵硬', 'key_points': '表情自然', 'precautions': '观察生活'}},
        {'name': '情感表达', 'description': f'通过舞蹈表达情感。', 'difficulty': 5, 'duration': 320, 'attributes': {'force_parts': '情感投入', 'common_mistakes': '情感虚假', 'key_points': '情感真挚', 'precautions': '理解内涵'}},
    ]

def get_ethnic_hand_moves(project_name):
    return [
        {'name': '孔雀手型', 'description': f'{project_name}的特色手型。', 'difficulty': 3, 'duration': 240, 'attributes': {'force_parts': '手指灵活', 'common_mistakes': '手指僵硬', 'key_points': '拇指食指圆润', 'precautions': '活动手指'}},
        {'name': '展翅手势', 'description': f'双臂展开如展翅。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '肩部展开', 'common_mistakes': '手臂不舒展', 'key_points': '肩背打开', 'precautions': '避免耸肩'}},
        {'name': '翻腕动作', 'description': f'手腕快速翻转。', 'difficulty': 4, 'duration': 260, 'attributes': {'force_parts': '手腕灵活', 'common_mistakes': '翻转不到位', 'key_points': '以腕为轴', 'precautions': '活动手腕'}},
    ]

def get_ethnic_body_moves(project_name):
    return [
        {'name': '三道弯体态', 'description': f'身体形成S形曲线。', 'difficulty': 5, 'duration': 330, 'attributes': {'force_parts': '腰部扭转', 'common_mistakes': '弯曲不自然', 'key_points': '三弯流畅', 'precautions': '练习柔韧性'}},
        {'name': '颤膝律动', 'description': f'膝盖颤动带动全身。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '膝盖弹动', 'common_mistakes': '颤动过大', 'key_points': '小幅颤动', 'precautions': '膝盖热身'}},
    ]

def get_ethnic_special_moves(project_name):
    return [
        {'name': '旋转技巧', 'description': f'{project_name}的快速旋转。', 'difficulty': 7, 'duration': 360, 'attributes': {'force_parts': '核心收紧', 'common_mistakes': '旋转不稳', 'key_points': '重心集中', 'precautions': '避免眩晕'}},
        {'name': '移颈摇头', 'description': f'头部平移配合节奏。', 'difficulty': 3, 'duration': 240, 'attributes': {'force_parts': '颈部控制', 'common_mistakes': '幅度过大', 'key_points': '小幅移动', 'precautions': '颈部热身'}},
    ]

def get_general_moves(module_name):
    return [
        {'name': '基础动作', 'description': f'基础舞蹈动作训练。', 'difficulty': 2, 'duration': 240, 'attributes': {'force_parts': '全身协调', 'common_mistakes': '动作不规范', 'key_points': '动作标准', 'precautions': '循序渐进'}},
        {'name': '进阶技巧', 'description': f'进阶舞蹈技巧训练。', 'difficulty': 4, 'duration': 300, 'attributes': {'force_parts': '多部位协调', 'common_mistakes': '技巧不牢', 'key_points': '技巧熟练', 'precautions': '练习基础'}},
    ]
