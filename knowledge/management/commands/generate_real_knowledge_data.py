"""
为典型舞蹈项目生成真实的知识图谱数据
使用方法: python manage.py generate_real_knowledge_data
"""
from django.core.management.base import BaseCommand
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
from origin.models import DanceProject as OriginDanceProject


class Command(BaseCommand):
    help = '为典型舞蹈项目生成真实的知识图谱数据'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('开始生成真实非遗舞蹈知识图谱数据'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 选择几个典型的舞蹈项目
        target_dances = [
            '京西太平鼓',
            '永新盾牌舞',
            '翼城花鼓',
        ]
        
        success_count = 0
        for dance_name in target_dances:
            try:
                # 从 origin 获取真实项目
                origin_project = OriginDanceProject.objects.filter(name=dance_name).first()
                if not origin_project:
                    self.stdout.write(self.style.WARNING(f'⚠️  跳过: {dance_name} (origin中不存在)'))
                    continue
                
                # 在 knowledge 表中查找或创建对应项目
                kp_project, created = DanceProject.objects.get_or_create(
                    name=dance_name,
                    defaults={
                        'description': origin_project.introduction or f'{dance_name}是国家级非物质文化遗产项目',
                        'category': origin_project.get_dance_type_display(),
                        'difficulty_level': 3,
                    }
                )
                
                # 如果已存在，先删除旧数据
                if not created:
                    self.stdout.write(self.style.WARNING(f'清理旧数据: {dance_name}'))
                    ActionModule.objects.filter(dance_project=kp_project).delete()
                
                self.stdout.write(f'\n正在生成: {dance_name}')
                
                # 根据舞蹈类型生成不同的模块
                if '鼓' in dance_name or '太平鼓' in dance_name:
                    self.generate_drum_dance_data(kp_project, dance_name)
                elif '盾' in dance_name or '牌' in dance_name:
                    self.generate_shield_dance_data(kp_project, dance_name)
                elif '花鼓' in dance_name:
                    self.generate_flower_drum_data(kp_project, dance_name)
                else:
                    self.generate_folk_dance_data(kp_project, dance_name)
                
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ 完成: {dance_name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ 失败: {dance_name} - {str(e)}'))
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'生成完成！成功: {success_count}/{len(target_dances)}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def generate_drum_dance_data(self, project, dance_name):
        """生成鼓类舞蹈数据（如京西太平鼓）"""
        # 模块1: 基本鼓法
        module1 = ActionModule.objects.create(
            dance_project=project,
            name='基本鼓法模块',
            description=f'{dance_name}的基础击鼓技法，包括单点、双点、滚奏等基本鼓法，是学习该舞蹈的核心基础。',
            order_index=1
        )
        
        moves1 = [
            {
                'name': '单点击鼓',
                'description': '右手持鼓槌，以腕部发力，单击鼓面中心，发出清脆响亮的声音。要求手腕灵活，力度适中。',
                'difficulty': 2,
                'duration': 300,
                'order_index': 1,
                'attributes': {
                    'force_parts': '手腕、前臂',
                    'common_mistakes': '手臂僵硬、力度过大或过小、击鼓位置不准确',
                    'key_points': '手腕放松，以腕发力，击鼓中心，声音清脆',
                    'precautions': '初学者应先练习手腕灵活性，不要急于加快速度'
                },
                'resources': [
                    {'type': 'video', 'title': '单点击鼓基础教学', 'duration': 240},
                    {'type': 'demo', 'title': '传承人示范-单点击鼓', 'duration': 180},
                ],
                'knowledge_points': [
                    {'name': '手腕发力', 'description': '掌握以腕部为主的发力技巧', 'category': '基础技法', 'importance_level': 5},
                    {'name': '节奏控制', 'description': '保持稳定的击鼓节奏', 'category': '音乐素养', 'importance_level': 4},
                ]
            },
            {
                'name': '双点连击',
                'description': '连续两次快速击鼓，形成"咚咚"的节奏型。要求两次击鼓间隔均匀，力度一致。',
                'difficulty': 3,
                'duration': 360,
                'order_index': 2,
                'attributes': {
                    'force_parts': '手腕、手指',
                    'common_mistakes': '两次击鼓力度不均、间隔不稳定、手臂紧张',
                    'key_points': '手腕带动，两次击鼓力度均匀，节奏稳定',
                    'precautions': '先慢练，熟练掌握后再加快速度'
                },
                'resources': [
                    {'type': 'video', 'title': '双点连击技巧讲解', 'duration': 300},
                ],
                'knowledge_points': [
                    {'name': '节奏型掌握', 'description': '学习基本的双点节奏型', 'category': '音乐素养', 'importance_level': 5},
                    {'name': '力度控制', 'description': '保持两次击鼓力度一致', 'category': '技能要点', 'importance_level': 4},
                ]
            },
            {
                'name': '滚奏技法',
                'description': '快速连续击鼓，形成连续的滚奏效果。需要手腕和手指的高度配合，是鼓类舞蹈的核心技法。',
                'difficulty': 5,
                'duration': 420,
                'order_index': 3,
                'attributes': {
                    'force_parts': '手腕、手指、前臂协调',
                    'common_mistakes': '速度不均、力度不稳、手臂过度紧张',
                    'key_points': '手腕放松，手指配合，滚奏均匀连贯',
                    'precautions': '需要长期练习，不可急于求成'
                },
                'resources': [
                    {'type': 'video', 'title': '滚奏技法完整教学', 'duration': 480},
                    {'type': 'demo', 'title': '传承人滚奏示范', 'duration': 360},
                ],
                'knowledge_points': [
                    {'name': '连续击打', 'description': '掌握快速连续击鼓的技巧', 'category': '高级技法', 'importance_level': 5},
                    {'name': '手腕放松', 'description': '保持手腕的灵活性和放松状态', 'category': '基础理论', 'importance_level': 5},
                ]
            },
        ]
        
        self.create_moves_with_details(module1, moves1)
        
        # 模块2: 跳跃动作
        module2 = ActionModule.objects.create(
            dance_project=project,
            name='跳跃动作模块',
            description=f'{dance_name}特色的跳跃和腾挪动作，展现豪放粗犷的风格特点。',
            order_index=2
        )
        
        moves2 = [
            {
                'name': '蹬腿跳跃',
                'description': '单腿蹬地跃起，同时击鼓，落地稳健。体现黄土高原人民的豪迈性格。',
                'difficulty': 4,
                'duration': 360,
                'order_index': 1,
                'attributes': {
                    'force_parts': '腿部、腰部、核心力量',
                    'common_mistakes': '跳跃高度不够、落地不稳、击鼓时机不对',
                    'key_points': '蹬地有力，跳跃协调，落地稳健，击鼓准确',
                    'precautions': '注意膝盖保护，循序渐进增加难度'
                },
                'resources': [
                    {'type': 'video', 'title': '蹬腿跳跃分解教学', 'duration': 360},
                ],
                'knowledge_points': [
                    {'name': '腿部力量', 'description': '增强腿部爆发力', 'category': '身体素质', 'importance_level': 4},
                    {'name': '协调配合', 'description': '跳跃与击鼓的协调配合', 'category': '技能要点', 'importance_level': 5},
                ]
            },
            {
                'name': '转身飞槌',
                'description': '旋转身体同时挥槌击鼓，动作舒展大方，气势磅礴。',
                'difficulty': 5,
                'duration': 420,
                'order_index': 2,
                'attributes': {
                    'force_parts': '腰部旋转、手臂挥动、全身协调',
                    'common_mistakes': '旋转不稳、击鼓位置偏差、身体失衡',
                    'key_points': '以腰为轴，旋转流畅，击鼓准确，气势饱满',
                    'precautions': '先练习旋转平衡，再结合击鼓动作'
                },
                'resources': [
                    {'type': 'video', 'title': '转身飞槌完整演示', 'duration': 420},
                    {'type': 'demo', 'title': '传承人转身飞槌示范', 'duration': 300},
                ],
                'knowledge_points': [
                    {'name': '旋转平衡', 'description': '掌握旋转中的身体平衡', 'category': '技能要点', 'importance_level': 5},
                    {'name': '气势表达', 'description': '展现豪放磅礴的气势', 'category': '表演技巧', 'importance_level': 4},
                ]
            },
        ]
        
        self.create_moves_with_details(module2, moves2)
        
        # 模块3: 队形变化
        module3 = ActionModule.objects.create(
            dance_project=project,
            name='队形变化模块',
            description=f'{dance_name}集体表演时的队形编排和阵法变化，展现群体舞蹈的壮观场面。',
            order_index=3
        )
        
        moves3 = [
            {
                'name': '四门斗底阵',
                'description': '四人一组，形成四方阵型，相互呼应，节奏统一。是传统太平鼓的经典阵法。',
                'difficulty': 4,
                'duration': 480,
                'order_index': 1,
                'attributes': {
                    'force_parts': '全身协调、团队配合',
                    'common_mistakes': '队形不整齐、节奏不统一、位置错乱',
                    'key_points': '队形规整，节奏一致，相互呼应，配合默契',
                    'precautions': '需要多次排练，培养团队默契'
                },
                'resources': [
                    {'type': 'video', 'title': '四门斗底阵法教学', 'duration': 540},
                ],
                'knowledge_points': [
                    {'name': '队形编排', 'description': '学习传统阵法的基本原理', 'category': '表演技巧', 'importance_level': 5},
                    {'name': '团队协作', 'description': '培养团队合作意识', 'category': '表演技巧', 'importance_level': 5},
                ]
            },
        ]
        
        self.create_moves_with_details(module3, moves3)
        
        self.stdout.write(f'  ✓ 生成 {module1.specific_moves.count() + module2.specific_moves.count() + module3.specific_moves.count()} 个招式')

    def generate_shield_dance_data(self, project, dance_name):
        """生成盾牌舞数据（如永新盾牌舞）"""
        # 模块1: 基本武术
        module1 = ActionModule.objects.create(
            dance_project=project,
            name='基本武术模块',
            description=f'{dance_name}的基础武术动作和站桩训练，体现武术与舞蹈的完美结合。',
            order_index=1
        )
        
        moves1 = [
            {
                'name': '马步站桩',
                'description': '双脚分开与肩同宽，屈膝下蹲成马步，双手持盾，稳如泰山。是盾牌舞的基本功。',
                'difficulty': 3,
                'duration': 360,
                'order_index': 1,
                'attributes': {
                    'force_parts': '腿部、腰部、核心力量',
                    'common_mistakes': '马步不稳、重心偏移、身体前倾或后仰',
                    'key_points': '马步扎实，重心稳定，身体正直，气息平稳',
                    'precautions': '初学者时间不宜过长，循序渐进增加时长'
                },
                'resources': [
                    {'type': 'video', 'title': '马步站桩基础训练', 'duration': 300},
                    {'type': 'demo', 'title': '传承人站桩示范', 'duration': 240},
                ],
                'knowledge_points': [
                    {'name': '站桩基本功', 'description': '掌握传统武术站桩要领', 'category': '基础技法', 'importance_level': 5},
                    {'name': '重心控制', 'description': '学会控制身体重心', 'category': '技能要点', 'importance_level': 5},
                ]
            },
            {
                'name': '弓步冲拳',
                'description': '前腿弓步，后腿蹬直，一手持盾防御，一手冲拳出击，刚劲有力。',
                'difficulty': 4,
                'duration': 420,
                'order_index': 2,
                'attributes': {
                    'force_parts': '腿部、腰部、手臂',
                    'common_mistakes': '弓步不到位、冲拳无力、身体不协调',
                    'key_points': '弓步扎实，冲拳有力，盾拳配合，刚柔并济',
                    'precautions': '注意动作规范性，避免受伤'
                },
                'resources': [
                    {'type': 'video', 'title': '弓步冲拳分解教学', 'duration': 360},
                ],
                'knowledge_points': [
                    {'name': '武术基本动作', 'description': '掌握弓步冲拳的标准动作', 'category': '基础技法', 'importance_level': 4},
                    {'name': '攻防意识', 'description': '理解舞蹈中的攻防含义', 'category': '文化知识', 'importance_level': 4},
                ]
            },
        ]
        
        self.create_moves_with_details(module1, moves1)
        
        # 模块2: 盾牌技法
        module2 = ActionModule.objects.create(
            dance_project=project,
            name='盾牌技法模块',
            description=f'{dance_name}的盾牌运用和防守技法，展现盾牌的独特魅力。',
            order_index=2
        )
        
        moves2 = [
            {
                'name': '盾牌格挡',
                'description': '运用盾牌进行上下左右的格挡防守，动作敏捷灵活，保护身体各个部位。',
                'difficulty': 4,
                'duration': 360,
                'order_index': 1,
                'attributes': {
                    'force_parts': '手臂、腰部、反应能力',
                    'common_mistakes': '格挡不及时、盾牌位置不对、动作僵硬',
                    'key_points': '反应敏捷，盾牌到位，动作流畅，防守严密',
                    'precautions': '需要先练习基本反应速度'
                },
                'resources': [
                    {'type': 'video', 'title': '盾牌格挡技巧', 'duration': 300},
                ],
                'knowledge_points': [
                    {'name': '防守技法', 'description': '掌握盾牌防守的基本方法', 'category': '技能要点', 'importance_level': 5},
                    {'name': '反应速度', 'description': '提高身体反应能力', 'category': '身体素质', 'importance_level': 4},
                ]
            },
        ]
        
        self.create_moves_with_details(module2, moves2)
        
        self.stdout.write(f'  ✓ 生成 {module1.specific_moves.count() + module2.specific_moves.count()} 个招式')

    def generate_flower_drum_data(self, project, dance_name):
        """生成花鼓类舞蹈数据（如翼城花鼓）"""
        # 模块1: 基本手势
        module1 = ActionModule.objects.create(
            dance_project=project,
            name='基本手势模块',
            description=f'{dance_name}的手部动作和手势变化，展现花鼓舞蹈的灵动优美。',
            order_index=1
        )
        
        moves1 = [
            {
                'name': '兰花指',
                'description': '拇指与中指相捏，其余三指自然舒展，形如兰花，是花鼓舞蹈的典型手型。',
                'difficulty': 2,
                'duration': 240,
                'order_index': 1,
                'attributes': {
                    'force_parts': '手指、手腕',
                    'common_mistakes': '手指僵硬、手型不标准、手腕不灵活',
                    'key_points': '手指自然弯曲，拇指中指相捏，手腕放松灵活',
                    'precautions': '需要经常练习手指灵活性'
                },
                'resources': [
                    {'type': 'video', 'title': '兰花指手势教学', 'duration': 180},
                ],
                'knowledge_points': [
                    {'name': '手型规范', 'description': '掌握标准的手型要求', 'category': '基础技法', 'importance_level': 5},
                    {'name': '手指灵活性', 'description': '提高手指的灵活性和协调性', 'category': '技能要点', 'importance_level': 4},
                ]
            },
            {
                'name': '云手',
                'description': '双手在胸前划圆，如云卷云舒，动作优美流畅，展现花鼓舞蹈的韵律美。',
                'difficulty': 3,
                'duration': 300,
                'order_index': 2,
                'attributes': {
                    'force_parts': '手臂、腰部、手腕',
                    'common_mistakes': '划圆不流畅、手臂僵硬、节奏不匀',
                    'key_points': '以腰带动，手臂划圆流畅，手腕配合，节奏均匀',
                    'precautions': '先慢练体会动作路线'
                },
                'resources': [
                    {'type': 'video', 'title': '云手动作详解', 'duration': 240},
                    {'type': 'demo', 'title': '传承人云手示范', 'duration': 180},
                ],
                'knowledge_points': [
                    {'name': '手臂韵律', 'description': '掌握手臂运动的韵律感', 'category': '技能要点', 'importance_level': 5},
                    {'name': '腰部带动', 'description': '学会以腰带动手臂运动', 'category': '基础理论', 'importance_level': 5},
                ]
            },
        ]
        
        self.create_moves_with_details(module1, moves1)
        
        # 模块2: 身段韵律
        module2 = ActionModule.objects.create(
            dance_project=project,
            name='身段韵律模块',
            description=f'{dance_name}的身段变化和韵律表达，展现舞蹈的优美姿态。',
            order_index=2
        )
        
        moves2 = [
            {
                'name': '三道弯',
                'description': '身体呈现头、胸、腰三段弯曲的S型姿态，是花鼓舞蹈的典型身段，展现女性柔美。',
                'difficulty': 4,
                'duration': 360,
                'order_index': 1,
                'attributes': {
                    'force_parts': '腰部、胸部、颈部',
                    'common_mistakes': '弯曲不自然、三段不协调、身体僵硬',
                    'key_points': '三段弯曲自然流畅，姿态优美，气息配合',
                    'precautions': '需要先练习腰部柔韧性'
                },
                'resources': [
                    {'type': 'video', 'title': '三道弯身段教学', 'duration': 300},
                ],
                'knowledge_points': [
                    {'name': '身段造型', 'description': '掌握三道弯的标准造型', 'category': '基础技法', 'importance_level': 5},
                    {'name': '身体柔韧', 'description': '提高身体的柔韧性', 'category': '身体素质', 'importance_level': 4},
                ]
            },
        ]
        
        self.create_moves_with_details(module2, moves2)
        
        self.stdout.write(f'  ✓ 生成 {module1.specific_moves.count() + module2.specific_moves.count()} 个招式')

    def generate_folk_dance_data(self, project, dance_name):
        """生成民间舞蹈数据（通用）"""
        module1 = ActionModule.objects.create(
            dance_project=project,
            name='基本步伐模块',
            description=f'{dance_name}的基础步伐训练。',
            order_index=1
        )
        
        moves1 = [
            {
                'name': '基本步法',
                'description': f'{dance_name}的基础步法。',
                'difficulty': 2,
                'duration': 300,
                'order_index': 1,
                'attributes': {
                    'force_parts': '腿部、脚部',
                    'common_mistakes': '步法不规范、节奏不稳',
                    'key_points': '步法准确，节奏稳定',
                    'precautions': '循序渐进练习'
                },
                'resources': [
                    {'type': 'video', 'title': '基础步法教学', 'duration': 240},
                ],
                'knowledge_points': [
                    {'name': '基础步法', 'description': '掌握基础步法', 'category': '基础技法', 'importance_level': 5},
                ]
            },
        ]
        
        self.create_moves_with_details(module1, moves1)
        self.stdout.write(f'  ✓ 生成 {module1.specific_moves.count()} 个招式')

    def create_moves_with_details(self, module, moves_data):
        """为模块创建招式及相关数据"""
        for move_data in moves_data:
            # 创建招式
            move = SpecificMove.objects.create(
                action_module=module,
                name=move_data['name'],
                description=move_data['description'],
                difficulty=move_data['difficulty'],
                duration=move_data['duration'],
                order_index=move_data['order_index']
            )
            
            # 创建动作属性
            attr_data = move_data['attributes']
            MoveAttribute.objects.create(
                specific_move=move,
                force_parts=attr_data['force_parts'],
                common_mistakes=attr_data['common_mistakes'],
                key_points=attr_data['key_points'],
                precautions=attr_data.get('precautions', '')
            )
            
            # 创建学习资源
            for idx, res_data in enumerate(move_data.get('resources', []), 1):
                LearningResource.objects.create(
                    specific_move=move,
                    resource_type=res_data['type'],
                    title=res_data['title'],
                    url='https://example.com/resource',  # 示例URL，可后续替换
                    duration=res_data.get('duration', 0),
                    order_index=idx
                )
            
            # 创建知识点
            for kp_data in move_data.get('knowledge_points', []):
                KnowledgePoint.objects.create(
                    specific_move=move,
                    name=kp_data['name'],
                    description=kp_data['description'],
                    category=kp_data['category'],
                    importance_level=kp_data['importance_level']
                )
