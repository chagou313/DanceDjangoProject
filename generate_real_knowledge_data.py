"""
为3个典型舞蹈项目生成真实的知识图谱数据
使用方法: python manage.py generate_real_data
"""
from django.core.management.base import BaseCommand
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint


class Command(BaseCommand):
    help = '生成真实的知识图谱数据示例'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('开始生成真实知识图谱数据'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        generate_taipinggu_data(self)
        
        self.stdout.write(self.style.SUCCESS('\n数据生成完成！'))


def generate_taipinggu_data(cmd):
    """生成京西太平鼓的完整数据"""
    
    project, created = DanceProject.objects.get_or_create(
        name='京西太平鼓',
        defaults={
            'category': '民间舞蹈',
            'description': '京西太平鼓是流传于北京市门头沟区、石景山区等地的传统民间舞蹈，起源于明代，已有600多年历史。表演者左手持鼓，右手握槌，边击边舞，动作刚劲有力，节奏明快，具有浓郁的北方民间艺术特色。',
            'difficulty_level': 3,
        }
    )
    
    if not created:
        cmd.stdout.write(cmd.style.WARNING(f"项目 {project.name} 已存在，跳过"))
        return
    
    # 模块1：基本步伐模块
    module1 = ActionModule.objects.create(
        dance_project=project,
        name='基本步伐模块',
        description='太平鼓的基础步法训练，包括站立姿势、移动步法、转身技巧等，是学习太平鼓的基础。通过系统练习，掌握正确的重心转移和脚步协调。',
        order_index=1
    )
    
    moves_module1 = [
        {
            'name': '马步站桩',
            'description': '双脚分开与肩同宽，屈膝下蹲成马步，双手持鼓置于胸前。要求膝盖不超过脚尖，背部挺直，重心稳定。这是太平鼓最基础的站立姿势，为后续动作打下坚实基础。',
            'difficulty': 2,
            'duration': 240,
            'order_index': 1,
            'attributes': {
                'force_parts': '大腿肌肉发力，核心收紧，双脚均匀受力',
                'common_mistakes': '膝盖内扣、弯腰驼背、重心偏向一侧、呼吸急促',
                'key_points': '两脚平行开立，屈膝90度，含胸拔背，气沉丹田，目视前方',
                'precautions': '初学者时间不宜过长，每次3-5分钟，注意膝盖保暖，避免受凉'
            },
            'resources': [
                {'type': 'video', 'title': '马步站桩标准示范', 'duration': 180},
                {'type': 'demo', 'title': '传承人讲解站桩要点', 'duration': 300},
                {'type': 'article', 'title': '马步训练的科学方法', 'duration': None},
            ],
            'knowledge_points': [
                {'name': '重心控制', 'description': '掌握身体重心的分布和转移，保持平衡稳定', 'category': '技法要点', 'importance_level': 5},
                {'name': '呼吸调节', 'description': '配合动作进行深呼吸，增强耐力和稳定性', 'category': '训练方法', 'importance_level': 4},
                {'name': '腿部力量', 'description': '通过站桩锻炼大腿和小腿肌肉力量', 'category': '训练方法', 'importance_level': 4},
                {'name': '传统文化', 'description': '马步是中国武术和传统舞蹈的基础功', 'category': '文化内涵', 'importance_level': 3},
            ]
        },
        {
            'name': '弓步击鼓',
            'description': '前腿弓、后腿绷，形成弓箭步，同时右手挥槌击鼓。要求前后腿比例约为7:3，上身微向前倾，击鼓有力。此动作体现太平鼓的阳刚之气。',
            'difficulty': 4,
            'duration': 300,
            'order_index': 2,
            'attributes': {
                'force_parts': '前腿大腿发力支撑，后腿蹬地，腰部扭转带动手臂击鼓',
                'common_mistakes': '前后脚距离过小、后腿弯曲、击鼓无力、身体晃动',
                'key_points': '前腿屈膝90度，后腿伸直，髋部正对前方，击鼓时腰臂合一',
                'precautions': '注意膝盖方向与脚尖一致，避免扭伤，击鼓力度适中'
            },
            'resources': [
                {'type': 'video', 'title': '弓步击鼓分解教学', 'duration': 240},
                {'type': 'demo', 'title': '老艺人弓步击鼓展示', 'duration': 180},
                {'type': 'article', 'title': '弓步在民间舞蹈中的应用', 'duration': None},
            ],
            'knowledge_points': [
                {'name': '弓步要领', 'description': '掌握标准弓步的姿势要求和发力方式', 'category': '技法要点', 'importance_level': 5},
                {'name': '击鼓技巧', 'description': '学习正确的握槌方法和击鼓角度', 'category': '技法要点', 'importance_level': 5},
                {'name': '腰臂协调', 'description': '腰部转动与手臂挥动的协调配合', 'category': '表演技巧', 'importance_level': 4},
                {'name': '阳刚之美', 'description': '体现北方民间舞蹈的豪放风格', 'category': '文化内涵', 'importance_level': 3},
            ]
        },
        {
            'name': '虚步提鼓',
            'description': '一腿屈膝半蹲支撑，另一腿脚尖点地成虚步，双手将鼓提起至胸前。要求虚实分明，重心稳定，提鼓时手腕灵活。',
            'difficulty': 3,
            'duration': 270,
            'order_index': 3,
            'attributes': {
                'force_parts': '支撑腿大腿发力，提鼓时手腕和前臂协同用力',
                'common_mistakes': '虚实不分、重心不稳、提鼓过高或过低',
                'key_points': '支撑腿稳固，虚腿轻灵，提鼓至胸口高度，肘部微屈',
                'precautions': '注意膝关节保护，避免过度负重'
            },
            'resources': [
                {'type': 'video', 'title': '虚步提鼓技巧详解', 'duration': 200},
                {'type': 'demo', 'title': '传承人虚步示范', 'duration': 150},
            ],
            'knowledge_points': [
                {'name': '虚实转换', 'description': '掌握虚实步法的转换技巧', 'category': '技法要点', 'importance_level': 5},
                {'name': '手腕灵活', 'description': '训练手腕的灵活性和控制力', 'category': '技法要点', 'importance_level': 4},
            ]
        },
        {
            'name': '仆步压鼓',
            'description': '一腿全蹲，另一腿伸直仆地，身体重心降低，同时将鼓向下按压。要求动作舒展大方，体现太平鼓的低姿美感。',
            'difficulty': 5,
            'duration': 330,
            'order_index': 4,
            'attributes': {
                'force_parts': '蹲腿大腿和臀部发力，压鼓时手臂下压',
                'common_mistakes': '仆腿弯曲、重心后仰、压鼓不到位',
                'key_points': '蹲腿膝盖不超过脚尖，仆腿伸直贴地，上身前倾',
                'precautions': '充分热身，循序渐进，避免拉伤'
            },
            'resources': [
                {'type': 'video', 'title': '仆步压鼓完整演示', 'duration': 260},
                {'type': 'article', 'title': '低姿动作的训练方法', 'duration': None},
            ],
            'knowledge_points': [
                {'name': '柔韧性训练', 'description': '提高髋关节和腿部的柔韧性', 'category': '训练方法', 'importance_level': 4},
                {'name': '低姿美学', 'description': '理解低姿动作的艺术表现力', 'category': '表演技巧', 'importance_level': 3},
            ]
        },
    ]
    
    for move_data in moves_module1:
        create_move_with_details(module1, move_data)
    
    cmd.stdout.write(cmd.style.SUCCESS(f"✓ 京西太平鼓 - 基本步伐模块完成（{len(moves_module1)}个招式）"))
    
    # 模块2：手势身段模块
    module2 = ActionModule.objects.create(
        dance_project=project,
        name='手势身段模块',
        description='太平鼓的手部动作和身体姿态训练，包括持鼓手法、挥臂轨迹、转身技巧等。通过优美的身段展现太平鼓的艺术魅力。',
        order_index=2
    )
    
    moves_module2 = [
        {
            'name': '云手翻鼓',
            'description': '双手持鼓，做云手动作，同时翻转鼓面。要求手腕灵活，动作连贯流畅，鼓面翻转时发出清脆声响。',
            'difficulty': 5,
            'duration': 360,
            'order_index': 1,
            'attributes': {
                'force_parts': '手腕发力，小臂配合，肩部放松',
                'common_mistakes': '手腕僵硬、动作断续、鼓面翻转不到位',
                'key_points': '以腕为轴，圆活自然，翻转迅速，声响清脆',
                'precautions': '先慢后快，循序渐进，避免手腕过度用力'
            },
            'resources': [
                {'type': 'video', 'title': '云手翻鼓技巧详解', 'duration': 300},
                {'type': 'demo', 'title': '大师云手展示', 'duration': 240},
            ],
            'knowledge_points': [
                {'name': '手腕灵活性', 'description': '训练手腕的灵活性和控制力', 'category': '技法要点', 'importance_level': 5},
                {'name': '圆的运动', 'description': '理解中国传统舞蹈中圆的运动轨迹', 'category': '文化内涵', 'importance_level': 4},
            ]
        },
        {
            'name': '托鼓亮相',
            'description': '单手托鼓高举过头，身体挺拔，目光坚定，形成优美的亮相姿态。要求手臂伸直，身体舒展，展现自信和精神风貌。',
            'difficulty': 3,
            'duration': 180,
            'order_index': 2,
            'attributes': {
                'force_parts': '手臂上举，肩膀下沉，核心收紧',
                'common_mistakes': '手臂弯曲、耸肩、身体歪斜',
                'key_points': '手臂伸直但不僵硬，沉肩坠肘，挺胸抬头',
                'precautions': '注意肩部放松，避免耸肩'
            },
            'resources': [
                {'type': 'video', 'title': '托鼓亮相标准姿势', 'duration': 150},
            ],
            'knowledge_points': [
                {'name': '亮相技巧', 'description': '掌握舞蹈中的亮相姿态和眼神运用', 'category': '表演技巧', 'importance_level': 5},
                {'name': '精神风貌', 'description': '通过姿态展现舞者的精神气质', 'category': '表演技巧', 'importance_level': 4},
            ]
        },
        {
            'name': '绕花击鼓',
            'description': '手持鼓槌在鼓面上画圆绕花，同时有节奏地击鼓。要求手腕灵活，绕花圆润，击鼓准确，富有韵律感。',
            'difficulty': 6,
            'duration': 420,
            'order_index': 3,
            'attributes': {
                'force_parts': '手腕旋转发力，手指控制鼓槌',
                'common_mistakes': '绕花不圆、击鼓不准、节奏混乱',
                'key_points': '以腕带指，绕花饱满，击鼓点准确',
                'precautions': '先练绕花再练击鼓，逐步结合'
            },
            'resources': [
                {'type': 'video', 'title': '绕花击鼓分解教学', 'duration': 360},
                {'type': 'demo', 'title': '高手绕花表演', 'duration': 200},
            ],
            'knowledge_points': [
                {'name': '手腕旋转', 'description': '掌握手腕的旋转技巧和力度控制', 'category': '技法要点', 'importance_level': 5},
                {'name': '节奏感', 'description': '培养音乐节奏感和击鼓准确性', 'category': '表演技巧', 'importance_level': 5},
            ]
        },
    ]
    
    for move_data in moves_module2:
        create_move_with_details(module2, move_data)
    
    cmd.stdout.write(cmd.style.SUCCESS(f"✓ 京西太平鼓 - 手势身段模块完成（{len(moves_module2)}个招式）"))
    
    # 模块3：队形变化模块
    module3 = ActionModule.objects.create(
        dance_project=project,
        name='队形变化模块',
        description='集体表演时的队形编排和变化，包括圆形、方形、穿插等传统队形。培养团队协作能力和空间意识。',
        order_index=3
    )
    
    moves_module3 = [
        {
            'name': '圆圈围鼓',
            'description': '多人围成圆圈，面向圆心，同步击鼓。要求队形整齐，节奏统一，气势磅礴。',
            'difficulty': 4,
            'duration': 300,
            'order_index': 1,
            'attributes': {
                'force_parts': '全身协调，团队配合',
                'common_mistakes': '队形不齐、节奏不一、间距不均',
                'key_points': '保持等距，面向圆心，动作同步',
                'precautions': '注意与他人的距离，避免碰撞'
            },
            'resources': [
                {'type': 'video', 'title': '圆圈队形编排示范', 'duration': 280},
            ],
            'knowledge_points': [
                {'name': '团队协作', 'description': '培养团队合作意识和协调能力', 'category': '表演技巧', 'importance_level': 5},
                {'name': '空间意识', 'description': '建立舞台空间感和位置感', 'category': '表演技巧', 'importance_level': 4},
            ]
        },
        {
            'name': '交叉换位',
            'description': '队员相互交叉穿行换位，形成动态的队形变化。要求路线清晰，避让及时，动作流畅。',
            'difficulty': 6,
            'duration': 360,
            'order_index': 2,
            'attributes': {
                'force_parts': '腿部移动，身体转向，视线引导',
                'common_mistakes': '路线混乱、碰撞他人、节奏打乱',
                'key_points': '按预定路线行进，注意观察，保持节奏',
                'precautions': '多次排练熟悉路线，注意安全'
            },
            'resources': [
                {'type': 'video', 'title': '交叉换位队形教学', 'duration': 320},
            ],
            'knowledge_points': [
                {'name': '队形编排', 'description': '学习舞蹈队形的设计原理', 'category': '表演技巧', 'importance_level': 5},
                {'name': '应变能力', 'description': '培养临场应变和调整能力', 'category': '表演技巧', 'importance_level': 4},
            ]
        },
    ]
    
    for move_data in moves_module3:
        create_move_with_details(module3, move_data)
    
    cmd.stdout.write(cmd.style.SUCCESS(f"✓ 京西太平鼓 - 队形变化模块完成（{len(moves_module3)}个招式）"))
    
    # 模块4：节奏韵律模块
    module4 = ActionModule.objects.create(
        dance_project=project,
        name='节奏韵律模块',
        description='太平鼓的节奏训练，学习不同的鼓点和音乐配合。掌握快慢、强弱、轻重等节奏变化。',
        order_index=4
    )
    
    moves_module4 = [
        {
            'name': '单点基础',
            'description': '学习最基本的单点击鼓，掌握正确的击鼓位置和力度。要求每一下都清晰有力，节奏稳定。',
            'difficulty': 2,
            'duration': 240,
            'order_index': 1,
            'attributes': {
                'force_parts': '手腕发力，手臂辅助',
                'common_mistakes': '击鼓位置不准、力度不均、节奏不稳',
                'key_points': '击鼓中心位置，力度均匀，节奏稳定',
                'precautions': '从轻到重，循序渐进'
            },
            'resources': [
                {'type': 'video', 'title': '单点击鼓基础教学', 'duration': 200},
                {'type': 'demo', 'title': '标准单点示范', 'duration': 120},
            ],
            'knowledge_points': [
                {'name': '基础节奏', 'description': '掌握最基本的击鼓节奏', 'category': '技法要点', 'importance_level': 5},
                {'name': '力度控制', 'description': '学习控制击鼓的力度', 'category': '技法要点', 'importance_level': 4},
            ]
        },
        {
            'name': '双点连击',
            'description': '连续两次快速击鼓，形成双点节奏。要求两次击鼓间隔均匀，声音连贯。',
            'difficulty': 4,
            'duration': 300,
            'order_index': 2,
            'attributes': {
                'force_parts': '手腕快速弹动',
                'common_mistakes': '间隔不均、第二次无力、节奏加快',
                'key_points': '两次力度相同，间隔相等',
                'precautions': '先慢练，熟练后加速'
            },
            'resources': [
                {'type': 'video', 'title': '双点连击技巧', 'duration': 250},
            ],
            'knowledge_points': [
                {'name': '复合节奏', 'description': '学习更复杂的节奏型', 'category': '技法要点', 'importance_level': 4},
            ]
        },
    ]
    
    for move_data in moves_module4:
        create_move_with_details(module4, move_data)
    
    cmd.stdout.write(cmd.style.SUCCESS(f"✓ 京西太平鼓 - 节奏韵律模块完成（{len(moves_module4)}个招式）"))
    
    total_moves = (module1.specificmove_set.count() + 
                   module2.specificmove_set.count() + 
                   module3.specificmove_set.count() + 
                   module4.specificmove_set.count())
    cmd.stdout.write(cmd.style.SUCCESS(f"\n🎉 京西太平鼓数据生成完成！共{total_moves}个招式\n"))


def create_move_with_details(module, move_data):
    """创建招式及其详细信息"""
    move = SpecificMove.objects.create(
        action_module=module,
        name=move_data['name'],
        description=move_data['description'],
        difficulty=move_data['difficulty'],
        duration=move_data['duration'],
        order_index=move_data['order_index']
    )
    
    # 创建动作属性
    MoveAttribute.objects.create(
        specific_move=move,
        **move_data['attributes']
    )
    
    # 创建学习资源
    for res_data in move_data['resources']:
        LearningResource.objects.create(
            specific_move=move,
            resource_type=res_data['type'],
            title=res_data['title'],
            url=f'https://example.com/resource/{move_data["name"]}_{res_data["type"]}',
            duration=res_data['duration'],
            order_index=1
        )
    
    # 创建知识点
    for kp_data in move_data['knowledge_points']:
        KnowledgePoint.objects.create(
            specific_move=move,
            **kp_data
        )

