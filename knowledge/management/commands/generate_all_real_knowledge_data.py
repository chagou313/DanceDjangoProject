"""
为所有舞蹈项目批量生成真实的知识图谱数据
使用方法: python manage.py generate_all_real_knowledge_data --batch-size 20
"""
import time
from django.core.management.base import BaseCommand
from knowledge.models import DanceProject, ActionModule, SpecificMove, MoveAttribute, LearningResource, KnowledgePoint
from origin.models import DanceProject as OriginDanceProject


class Command(BaseCommand):
    help = '为所有舞蹈项目批量生成真实的知识图谱数据'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=20, help='每处理多少个显示一次进度')
        parser.add_argument('--clear', action='store_true', help='生成前先清除所有旧数据')
        parser.add_argument('--limit', type=int, help='限制生成的项目数量（用于测试）')

    def handle(self, *args, **options):
        batch_size = options.get('batch_size', 20)
        clear_first = options.get('clear', False)
        limit = options.get('limit', None)
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('批量生成非遗舞蹈知识图谱真实数据'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 如果需要清除旧数据
        if clear_first:
            self.stdout.write(self.style.WARNING('\n⚠️  正在清除所有旧数据...'))
            KnowledgePoint.objects.all().delete()
            LearningResource.objects.all().delete()
            MoveAttribute.objects.all().delete()
            SpecificMove.objects.all().delete()
            ActionModule.objects.all().delete()
            DanceProject.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ 旧数据已清除\n'))
        
        # 获取所有origin中的舞蹈项目
        origin_projects = OriginDanceProject.objects.all()
        if limit:
            origin_projects = origin_projects[:limit]
        
        total_count = origin_projects.count()
        self.stdout.write(f'\n共有 {total_count} 个舞蹈项目需要处理')
        self.stdout.write(f'批次大小: {batch_size}\n')
        
        success_count = 0
        skip_count = 0
        error_count = 0
        start_time = time.time()
        
        for idx, origin_project in enumerate(origin_projects, 1):
            try:
                # 显示进度
                if idx % batch_size == 0 or idx == 1:
                    elapsed = time.time() - start_time
                    self.stdout.write(f'\n进度: [{idx}/{total_count}] ({idx*100//total_count}%) - 已用时 {elapsed:.1f}秒')
                
                # 在knowledge表中查找或创建项目
                kp_project, created = DanceProject.objects.get_or_create(
                    name=origin_project.name,
                    defaults={
                        'description': origin_project.introduction or f'{origin_project.name}是非物质文化遗产项目',
                        'category': origin_project.get_dance_type_display(),
                        'difficulty_level': 3,
                    }
                )
                
                # 如果已存在且有数据，跳过
                if not created and ActionModule.objects.filter(dance_project=kp_project).exists():
                    skip_count += 1
                    continue
                
                # 如果已存在但无数据，清除旧数据
                if not created:
                    ActionModule.objects.filter(dance_project=kp_project).delete()
                
                # 根据舞蹈特征生成对应的数据
                self.generate_dance_data(kp_project, origin_project)
                success_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n✗ 失败 [{idx}]: {origin_project.name} - {str(e)}'))
                error_count += 1
        
        # 打印最终统计
        elapsed = time.time() - start_time
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('批量生成完成！'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'总项目数: {total_count}')
        self.stdout.write(self.style.SUCCESS(f'成功生成: {success_count}'))
        self.stdout.write(self.style.WARNING(f'跳过(已存在): {skip_count}'))
        self.stdout.write(self.style.ERROR(f'失败: {error_count}'))
        self.stdout.write(f'总用时: {elapsed:.1f}秒')
        
        # 打印数据库统计
        self.print_final_stats()

    def print_final_stats(self):
        """打印最终统计信息"""
        projects = DanceProject.objects.count()
        modules = ActionModule.objects.count()
        moves = SpecificMove.objects.count()
        resources = LearningResource.objects.count()
        kps = KnowledgePoint.objects.count()
        
        self.stdout.write('\n📊 数据库最终统计:')
        self.stdout.write(f'   舞蹈项目: {projects}')
        self.stdout.write(f'   动作模块: {modules}')
        self.stdout.write(f'   具体招式: {moves}')
        self.stdout.write(f'   学习资源: {resources}')
        self.stdout.write(f'   知识点: {kps}')

    def generate_dance_data(self, kp_project, origin_project):
        """根据舞蹈类型和特征生成数据"""
        dance_name = origin_project.name
        dance_type = origin_project.dance_type
        
        # 智能分类：根据项目名称和类型决定使用哪种模板
        if '鼓' in dance_name:
            self.generate_drum_dance(kp_project, dance_name)
        elif '盾' in dance_name or '牌' in dance_name:
            self.generate_shield_dance(kp_project, dance_name)
        elif '花鼓' in dance_name:
            self.generate_flower_drum_dance(kp_project, dance_name)
        elif '秧歌' in dance_name:
            self.generate_yangge_dance(kp_project, dance_name)
        elif '龙' in dance_name or '舞龙' in dance_name:
            self.generate_dragon_dance(kp_project, dance_name)
        elif '狮' in dance_name or '舞狮' in dance_name:
            self.generate_lion_dance(kp_project, dance_name)
        elif '傩' in dance_name:
            self.generate_nuo_dance(kp_project, dance_name)
        elif '灯' in dance_name:
            self.generate_lantern_dance(kp_project, dance_name)
        elif dance_type == 'traditional' or '传统' in dance_name:
            self.generate_traditional_dance(kp_project, dance_name)
        else:
            # 默认民间舞蹈模板
            self.generate_folk_dance(kp_project, dance_name)

    def generate_drum_dance(self, project, dance_name):
        """鼓类舞蹈模板"""
        modules_data = [
            {
                'name': '基本鼓法模块',
                'description': f'{dance_name}的基础击鼓技法，包括单点、双点、滚奏等基本技法。',
                'moves': [
                    {
                        'name': '单点击鼓',
                        'description': '右手持鼓槌，以腕部发力单击鼓面中心，发出清脆响亮的声音。',
                        'difficulty': 2,
                        'duration': 300,
                        'attributes': {
                            'force_parts': '手腕、前臂',
                            'common_mistakes': '手臂僵硬、力度过大、击鼓位置不准确',
                            'key_points': '手腕放松，以腕发力，击鼓中心，声音清脆',
                            'precautions': '初学者应先练习手腕灵活性'
                        },
                        'resources': [{'type': 'video', 'title': '单点击鼓基础教学', 'duration': 240}],
                        'knowledge_points': [
                            {'name': '手腕发力', 'description': '掌握以腕部为主的发力技巧', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                    {
                        'name': '双点连击',
                        'description': '连续两次快速击鼓，形成"咚咚"的节奏型，间隔均匀。',
                        'difficulty': 3,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '手腕、手指',
                            'common_mistakes': '两次击鼓力度不均、间隔不稳定',
                            'key_points': '手腕带动，两次击鼓力度均匀，节奏稳定',
                            'precautions': '先慢练，熟练掌握后再加快速度'
                        },
                        'resources': [{'type': 'video', 'title': '双点连击技巧讲解', 'duration': 300}],
                        'knowledge_points': [
                            {'name': '节奏型掌握', 'description': '学习基本的双点节奏型', 'category': '音乐素养', 'importance_level': 5},
                        ]
                    },
                ]
            },
            {
                'name': '跳跃动作模块',
                'description': f'{dance_name}特色的跳跃和腾挪动作，展现豪放风格。',
                'moves': [
                    {
                        'name': '蹬腿跳跃',
                        'description': '单腿蹬地跃起，同时击鼓，落地稳健。',
                        'difficulty': 4,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '腿部、腰部、核心力量',
                            'common_mistakes': '跳跃高度不够、落地不稳、击鼓时机不对',
                            'key_points': '蹬地有力，跳跃协调，落地稳健，击鼓准确',
                            'precautions': '注意膝盖保护，循序渐进增加难度'
                        },
                        'resources': [{'type': 'video', 'title': '蹬腿跳跃分解教学', 'duration': 360}],
                        'knowledge_points': [
                            {'name': '腿部力量', 'description': '增强腿部爆发力', 'category': '身体素质', 'importance_level': 4},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_shield_dance(self, project, dance_name):
        """盾牌舞模板"""
        modules_data = [
            {
                'name': '基本武术模块',
                'description': f'{dance_name}的基础武术动作和站桩训练。',
                'moves': [
                    {
                        'name': '马步站桩',
                        'description': '双脚分开与肩同宽，屈膝下蹲成马步，双手持盾，稳如泰山。',
                        'difficulty': 3,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '腿部、腰部、核心力量',
                            'common_mistakes': '马步不稳、重心偏移、身体前倾',
                            'key_points': '马步扎实，重心稳定，身体正直，气息平稳',
                            'precautions': '初学者时间不宜过长，循序渐进增加时长'
                        },
                        'resources': [{'type': 'video', 'title': '马步站桩基础训练', 'duration': 300}],
                        'knowledge_points': [
                            {'name': '站桩基本功', 'description': '掌握传统武术站桩要领', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                ]
            },
            {
                'name': '盾牌技法模块',
                'description': f'{dance_name}的盾牌运用和防守技法。',
                'moves': [
                    {
                        'name': '盾牌格挡',
                        'description': '运用盾牌进行上下左右的格挡防守，动作敏捷灵活。',
                        'difficulty': 4,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '手臂、腰部、反应能力',
                            'common_mistakes': '格挡不及时、盾牌位置不对、动作僵硬',
                            'key_points': '反应敏捷，盾牌到位，动作流畅，防守严密',
                            'precautions': '需要先练习基本反应速度'
                        },
                        'resources': [{'type': 'video', 'title': '盾牌格挡技巧', 'duration': 300}],
                        'knowledge_points': [
                            {'name': '防守技法', 'description': '掌握盾牌防守的基本方法', 'category': '技能要点', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_flower_drum_dance(self, project, dance_name):
        """花鼓舞蹈模板"""
        modules_data = [
            {
                'name': '基本手势模块',
                'description': f'{dance_name}的手部动作和手势变化，展现灵动优美。',
                'moves': [
                    {
                        'name': '兰花指',
                        'description': '拇指与中指相捏，其余三指自然舒展，形如兰花，是花鼓舞蹈的典型手型。',
                        'difficulty': 2,
                        'duration': 240,
                        'attributes': {
                            'force_parts': '手指、手腕',
                            'common_mistakes': '手指僵硬、手型不标准、手腕不灵活',
                            'key_points': '手指自然弯曲，拇指中指相捏，手腕放松灵活',
                            'precautions': '需要经常练习手指灵活性'
                        },
                        'resources': [{'type': 'video', 'title': '兰花指手势教学', 'duration': 180}],
                        'knowledge_points': [
                            {'name': '手型规范', 'description': '掌握标准的手型要求', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                    {
                        'name': '云手',
                        'description': '双手在胸前划圆，如云卷云舒，动作优美流畅。',
                        'difficulty': 3,
                        'duration': 300,
                        'attributes': {
                            'force_parts': '手臂、腰部、手腕',
                            'common_mistakes': '划圆不流畅、手臂僵硬、节奏不匀',
                            'key_points': '以腰带动，手臂划圆流畅，手腕配合，节奏均匀',
                            'precautions': '先慢练体会动作路线'
                        },
                        'resources': [{'type': 'video', 'title': '云手动作详解', 'duration': 240}],
                        'knowledge_points': [
                            {'name': '手臂韵律', 'description': '掌握手臂运动的韵律感', 'category': '技能要点', 'importance_level': 5},
                        ]
                    },
                ]
            },
            {
                'name': '身段韵律模块',
                'description': f'{dance_name}的身段变化和韵律表达。',
                'moves': [
                    {
                        'name': '三道弯',
                        'description': '身体呈现头、胸、腰三段弯曲的S型姿态，展现女性柔美。',
                        'difficulty': 4,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '腰部、胸部、颈部',
                            'common_mistakes': '弯曲不自然、三段不协调、身体僵硬',
                            'key_points': '三段弯曲自然流畅，姿态优美，气息配合',
                            'precautions': '需要先练习腰部柔韧性'
                        },
                        'resources': [{'type': 'video', 'title': '三道弯身段教学', 'duration': 300}],
                        'knowledge_points': [
                            {'name': '身段造型', 'description': '掌握三道弯的标准造型', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_yangge_dance(self, project, dance_name):
        """秧歌舞蹈模板"""
        modules_data = [
            {
                'name': '基本步法模块',
                'description': f'{dance_name}的基础步伐训练。',
                'moves': [
                    {
                        'name': '十字步',
                        'description': '双脚交叉行进，形成十字轨迹，是秧歌的典型步法。',
                        'difficulty': 3,
                        'duration': 300,
                        'attributes': {
                            'force_parts': '腿部、脚部',
                            'common_mistakes': '步伐混乱、重心不稳、节奏不对',
                            'key_points': '步伐清晰，重心稳定，节奏明快',
                            'precautions': '先慢练熟悉步伐路线'
                        },
                        'resources': [{'type': 'video', 'title': '十字步基础教学', 'duration': 240}],
                        'knowledge_points': [
                            {'name': '基础步法', 'description': '掌握秧歌的基本步法', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                ]
            },
            {
                'name': '手绢花模块',
                'description': f'{dance_name}的手绢花技法和手部动作。',
                'moves': [
                    {
                        'name': '转绢花',
                        'description': '手腕旋转带动手绢形成花型，动作灵活优美。',
                        'difficulty': 4,
                        'duration': 300,
                        'attributes': {
                            'force_parts': '手腕、手指',
                            'common_mistakes': '手绢转不起来、动作僵硬、节奏不匀',
                            'key_points': '手腕灵活，手指配合，手绢旋转流畅',
                            'precautions': '需要反复练习手腕灵活性'
                        },
                        'resources': [{'type': 'video', 'title': '转绢花技巧教学', 'duration': 240}],
                        'knowledge_points': [
                            {'name': '手绢技法', 'description': '掌握手绢花的基本技法', 'category': '技能要点', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_dragon_dance(self, project, dance_name):
        """龙舞模板"""
        modules_data = [
            {
                'name': '基本龙舞模块',
                'description': f'{dance_name}的基础龙舞动作。',
                'moves': [
                    {
                        'name': '游龙',
                        'description': '舞龙者持龙杆，步伐协调，使龙身呈现游动姿态。',
                        'difficulty': 3,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '全身协调、手臂力量',
                            'common_mistakes': '龙身不流畅、步伐混乱、配合不协调',
                            'key_points': '步伐稳健，龙身流畅，团队配合默契',
                            'precautions': '需要多次排练培养默契'
                        },
                        'resources': [{'type': 'video', 'title': '游龙基础教学', 'duration': 300}],
                        'knowledge_points': [
                            {'name': '团队协作', 'description': '培养团队合作意识', 'category': '表演技巧', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_lion_dance(self, project, dance_name):
        """狮舞模板"""
        modules_data = [
            {
                'name': '基本狮舞模块',
                'description': f'{dance_name}的基础狮舞动作。',
                'moves': [
                    {
                        'name': '狮子蹲步',
                        'description': '模拟狮子蹲伏姿态，步伐稳健，动作灵活。',
                        'difficulty': 3,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '腿部、腰部',
                            'common_mistakes': '姿态不象形、步伐不稳、动作僵硬',
                            'key_points': '姿态逼真，步伐稳健，动作灵活',
                            'precautions': '需要练习腿部力量'
                        },
                        'resources': [{'type': 'video', 'title': '狮子蹲步教学', 'duration': 300}],
                        'knowledge_points': [
                            {'name': '象形表演', 'description': '掌握动物姿态的模仿技巧', 'category': '表演技巧', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_nuo_dance(self, project, dance_name):
        """傩舞模板"""
        modules_data = [
            {
                'name': '傩舞基础模块',
                'description': f'{dance_name}的基础傩舞动作和仪式动作。',
                'moves': [
                    {
                        'name': '傩舞步',
                        'description': '傩舞特有的神秘步伐，动作古朴庄重。',
                        'difficulty': 3,
                        'duration': 360,
                        'attributes': {
                            'force_parts': '腿部、腰部',
                            'common_mistakes': '步伐不标准、节奏不稳',
                            'key_points': '步伐庄重，节奏稳定，动作古朴',
                            'precautions': '需要理解傩舞的文化内涵'
                        },
                        'resources': [{'type': 'video', 'title': '傩舞步基础教学', 'duration': 300}],
                        'knowledge_points': [
                            {'name': '文化理解', 'description': '理解傩舞的宗教文化背景', 'category': '文化知识', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_lantern_dance(self, project, dance_name):
        """灯舞模板"""
        modules_data = [
            {
                'name': '灯舞基础模块',
                'description': f'{dance_name}的持灯舞蹈动作。',
                'moves': [
                    {
                        'name': '持灯舞步',
                        'description': '手持灯笼起舞，步伐轻盈，动作优美。',
                        'difficulty': 3,
                        'duration': 300,
                        'attributes': {
                            'force_parts': '手臂、腿部',
                            'common_mistakes': '灯笼不稳、步伐沉重、动作不协调',
                            'key_points': '灯笼平稳，步伐轻盈，动作优美',
                            'precautions': '注意灯笼的平衡'
                        },
                        'resources': [{'type': 'video', 'title': '持灯舞步教学', 'duration': 240}],
                        'knowledge_points': [
                            {'name': '道具运用', 'description': '掌握灯笼道具的运用技巧', 'category': '技能要点', 'importance_level': 4},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_traditional_dance(self, project, dance_name):
        """传统舞蹈通用模板"""
        modules_data = [
            {
                'name': '基本手姿模块',
                'description': f'{dance_name}的手部动作和手势变化。',
                'moves': [
                    {
                        'name': '基本手型',
                        'description': f'{dance_name}的典型手型。',
                        'difficulty': 2,
                        'duration': 240,
                        'attributes': {
                            'force_parts': '手指、手腕',
                            'common_mistakes': '手指僵硬、手型不标准',
                            'key_points': '手指自然，手型标准',
                            'precautions': '需要经常练习'
                        },
                        'resources': [{'type': 'video', 'title': '基本手型教学', 'duration': 180}],
                        'knowledge_points': [
                            {'name': '手型规范', 'description': '掌握标准手型', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                ]
            },
            {
                'name': '身段韵律模块',
                'description': f'{dance_name}的身段变化。',
                'moves': [
                    {
                        'name': '基本身段',
                        'description': f'{dance_name}的典型身段。',
                        'difficulty': 3,
                        'duration': 300,
                        'attributes': {
                            'force_parts': '腰部、身体',
                            'common_mistakes': '身段不协调',
                            'key_points': '身段优美，动作流畅',
                            'precautions': '需要练习身体柔韧性'
                        },
                        'resources': [{'type': 'video', 'title': '基本身段教学', 'duration': 240}],
                        'knowledge_points': [
                            {'name': '身段造型', 'description': '掌握标准身段', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def generate_folk_dance(self, project, dance_name):
        """民间舞蹈通用模板"""
        modules_data = [
            {
                'name': '基本步伐模块',
                'description': f'{dance_name}的基础步伐训练。',
                'moves': [
                    {
                        'name': '基本步法',
                        'description': f'{dance_name}的基础步法。',
                        'difficulty': 2,
                        'duration': 300,
                        'attributes': {
                            'force_parts': '腿部、脚部',
                            'common_mistakes': '步法不规范、节奏不稳',
                            'key_points': '步法准确，节奏稳定',
                            'precautions': '循序渐进练习'
                        },
                        'resources': [{'type': 'video', 'title': '基础步法教学', 'duration': 240}],
                        'knowledge_points': [
                            {'name': '基础步法', 'description': '掌握基础步法', 'category': '基础技法', 'importance_level': 5},
                        ]
                    },
                ]
            },
        ]
        
        self.create_modules(project, modules_data)

    def create_modules(self, project, modules_data):
        """批量创建模块和招式"""
        for module_idx, module_data in enumerate(modules_data, 1):
            # 创建模块
            module = ActionModule.objects.create(
                dance_project=project,
                name=module_data['name'],
                description=module_data['description'],
                order_index=module_idx
            )
            
            # 创建招式
            for move_idx, move_data in enumerate(module_data['moves'], 1):
                move = SpecificMove.objects.create(
                    action_module=module,
                    name=move_data['name'],
                    description=move_data['description'],
                    difficulty=move_data['difficulty'],
                    duration=move_data['duration'],
                    order_index=move_idx
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
                for res_idx, res_data in enumerate(move_data.get('resources', []), 1):
                    LearningResource.objects.create(
                        specific_move=move,
                        resource_type=res_data['type'],
                        title=res_data['title'],
                        url='https://example.com/resource',
                        duration=res_data.get('duration', 0),
                        order_index=res_idx
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
