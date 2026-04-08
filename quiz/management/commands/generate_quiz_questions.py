"""
为知识图谱中的舞蹈项目批量生成答题闯关题目
使用方法: python manage.py generate_quiz_questions --limit 50
"""
from django.core.management.base import BaseCommand
from quiz.models import Question, Level, LevelQuestion
from knowledge.models import KnowledgePoint, SpecificMove, ActionModule, DanceProject as KPDanceProject
from origin.models import DanceProject as OriginDanceProject
import random


class Command(BaseCommand):
    help = '为知识图谱中的舞蹈项目批量生成答题闯关题目'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100, help='限制生成的题目数量')
        parser.add_argument('--clear', action='store_true', help='生成前先清除所有旧题目')

    def handle(self, *args, **options):
        limit = options.get('limit', 100)
        clear_first = options.get('clear', False)
        
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('批量生成答题闯关题目'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 如果需要清除旧数据
        if clear_first:
            self.stdout.write(self.style.WARNING('\n⚠️  正在清除所有旧题目...'))
            LevelQuestion.objects.all().delete()
            Question.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ 旧题目已清除\n'))
        
        # 获取所有舞蹈项目和知识点
        origin_projects = OriginDanceProject.objects.all()
        kp_projects = KPDanceProject.objects.all().select_related()
        
        total_generated = 0
        
        for origin_project in origin_projects:
            try:
                # 尝试获取对应的知识图谱项目（如果有的话）
                kp_project = None
                try:
                    kp_project = KPDanceProject.objects.get(name=origin_project.name)
                except KPDanceProject.DoesNotExist:
                    pass
                
                if kp_project:
                    specific_moves = SpecificMove.objects.filter(
                        action_module__dance_project=kp_project
                    ).select_related('action_module')
                    
                    for move in specific_moves[:2]:
                        if total_generated >= limit:
                            break
                        kps = KnowledgePoint.objects.filter(specific_move=move)
                        for kp in kps[:1]:
                            if total_generated >= limit:
                                break
                            question = self.generate_choice_question(kp, move, kp_project, origin_project)
                            if question: total_generated += 1
                else:
                    # 如果没有 KP 项目，直接基于 origin 生成
                    if total_generated < limit:
                        question = self.generate_origin_choice_question(origin_project)
                        if question: total_generated += 1
                
                if total_generated >= limit:
                    break
                    
            except Exception as e:
                import traceback
                self.stdout.write(self.style.ERROR(f'✗ 处理 {origin_project.name} 失败: {str(e)}\n{traceback.format_exc()}'))
        
        # 创建关卡
        self.create_levels()
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'生成完成！共生成了 {total_generated} 道题目'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # 打印统计
        choice_count = Question.objects.filter(question_type='choice').count()
        judge_count = Question.objects.filter(question_type='judge').count()
        level_count = Level.objects.count()
        
        self.stdout.write(f'\n📊 统计:')
        self.stdout.write(f'   选择题: {choice_count}')
        self.stdout.write(f'   判断题: {judge_count}')
        self.stdout.write(f'   关卡数: {level_count}')

    def generate_origin_choice_question(self, project):
        """基于 origin 舞蹈项目生成选择题"""
        try:
            templates = [
                {
                    'content': f'{project.name}属于哪个非遗级别？',
                    'correct': project.get_level_display(),
                    'wrong_options': ['国家级', '省级', '市级', '县级'],
                },
                {
                    'content': f'{project.name}的申报地区是？',
                    'correct': project.declare_region or '待定',
                    'wrong_options': ['北京', '上海', '广州', '成都'],
                },
                {
                    'content': f'{project.name}的舞蹈类型是？',
                    'correct': project.get_dance_type_display(),
                    'wrong_options': ['古典舞', '民族舞', '民间舞', '现代舞'],
                },
            ]
            
            template = random.choice(templates)
            # 确保选项去重且数量为4
            all_options = [template['correct']] + template['wrong_options']
            unique_options = list(dict.fromkeys(all_options))  # 去重保持顺序
            while len(unique_options) < 4:
                unique_options.append(f'其他选项{len(unique_options)}')
            options = unique_options[:4]
            random.shuffle(options)
            
            correct_index = options.index(template['correct'])
            correct_answer = chr(65 + correct_index)
            
            question = Question.objects.create(
                dance_project=project,
                question_type='choice',
                difficulty=random.randint(1, 3),
                content=template['content'],
                options=options,
                correct_answer=correct_answer,
                explanation=f'{project.name}是{project.get_level_display()}非遗项目。',
            )
            self.stdout.write(f'  ✓ 生成题目: {template["content"]}')
            return question
        except Exception as e:
            import traceback
            self.stdout.write(self.style.ERROR(f'  ✗ 生成题目失败: {str(e)}\n{traceback.format_exc()}'))
            return None

    def generate_choice_question(self, kp, move, kp_project, origin_project):
        """生成选择题"""
        try:
            # 构建问题和选项
            templates = [
                {
                    'content': f'{kp.name}在{kp_project.name}中的作用是什么？',
                    'correct': kp.description[:50],
                    'wrong_options': [
                        f'主要用于增强表演的视觉效果',
                        f'是{kp_project.name}的基本功训练内容',
                        f'体现了传统文化的艺术特色',
                    ]
                },
                {
                    'content': f'{move.name}属于哪个动作模块？',
                    'correct': move.action_module.name,
                    'wrong_options': [
                        '基本手姿模块',
                        '身段韵律模块',
                        '跳跃动作模块',
                    ]
                },
                {
                    'content': f'{kp_project.name}的主要特点是什么？',
                    'correct': kp_project.description[:50] if kp_project.description else '具有深厚的文化底蕴',
                    'wrong_options': [
                        '动作简单，易于学习',
                        '节奏明快，适合现代表演',
                        '融合了多种舞蹈元素',
                    ]
                },
            ]
            
            template = random.choice(templates)
            
            # 组合选项
            options = [template['correct']] + template['wrong_options']
            random.shuffle(options)
            
            # 正确答案的字母
            correct_index = options.index(template['correct'])
            correct_answer = chr(65 + correct_index)
            
            # 查找或创建舞蹈项目关联
            dance_project = origin_project
            
            question = Question.objects.create(
                knowledge_point=kp,
                dance_project=dance_project,
                question_type='choice',
                difficulty=random.randint(1, 3),
                content=template['content'],
                options=options,
                correct_answer=correct_answer,
                explanation=f'正确答案是{correct_answer}。{kp.description}',
            )
            
            return question
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  生成选择题失败: {str(e)}'))
            return None

    def generate_judge_question(self, kp, move, kp_project, origin_project):
        """生成判断题"""
        try:
            # 随机决定是正确还是错误的陈述
            is_true = random.choice([True, False])
            
            if is_true:
                content = f'{kp.name}是{kp_project.name}中的重要知识点'
                correct_answer = '正确'
                explanation = f'是的，{kp.name}确实是{kp_project.name}的重要组成部分。{kp.description}'
            else:
                content = f'{kp.name}与{kp_project.name}没有关联'
                correct_answer = '错误'
                explanation = f'这个说法是错误的。{kp.name}实际上是{kp_project.name}的重要知识点。{kp.description}'
            
            dance_project = origin_project
            
            question = Question.objects.create(
                knowledge_point=kp,
                dance_project=dance_project,
                question_type='judge',
                difficulty=random.randint(1, 2),
                content=content,
                options=None,
                correct_answer=correct_answer,
                explanation=explanation,
            )
            
            return question
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  生成判断题失败: {str(e)}'))
            return None

    def create_levels(self):
        """创建关卡"""
        levels_data = [
            {
                'name': '入门挑战 - 基础知识',
                'description': '测试你对非遗舞蹈基础知识的了解',
                'category': 'mixed',
                'difficulty': 1,
                'required_score': 60,
                'time_limit': 300,
                'question_count': 10,
                'order_index': 1,
                'icon': 'fa-seedling',
            },
            {
                'name': '进阶之路 - 起源探索',
                'description': '深入了解各种舞蹈的历史渊源',
                'category': 'origin',
                'difficulty': 2,
                'required_score': 70,
                'time_limit': 300,
                'question_count': 15,
                'order_index': 2,
                'icon': 'fa-book',
            },
            {
                'name': '传承之光 - 名家风采',
                'description': '了解非遗舞蹈传承人的故事',
                'category': 'inheritor',
                'difficulty': 3,
                'required_score': 70,
                'time_limit': 360,
                'question_count': 15,
                'order_index': 3,
                'icon': 'fa-user-tie',
            },
            {
                'name': '技法精进 - 动作要领',
                'description': '掌握各种舞蹈的核心技法',
                'category': 'technique',
                'difficulty': 3,
                'required_score': 75,
                'time_limit': 420,
                'question_count': 20,
                'order_index': 4,
                'icon': 'fa-running',
            },
            {
                'name': '文化深探 - 底蕴解读',
                'description': '探索非遗舞蹈背后的文化内涵',
                'category': 'culture',
                'difficulty': 4,
                'required_score': 80,
                'time_limit': 480,
                'question_count': 20,
                'order_index': 5,
                'icon': 'fa-landmark',
            },
            {
                'name': '大师挑战 - 综合考验',
                'description': '全面检验你的非遗舞蹈知识',
                'category': 'mixed',
                'difficulty': 5,
                'required_score': 85,
                'time_limit': 600,
                'question_count': 30,
                'order_index': 6,
                'icon': 'fa-crown',
            },
        ]
        
        for level_data in levels_data:
            level, created = Level.objects.get_or_create(
                name=level_data['name'],
                defaults=level_data
            )
            
            if created:
                self.stdout.write(f'✓ 创建关卡: {level.name}')
            
            # 为关卡分配题目
            questions = Question.objects.filter(
                difficulty__lte=level.difficulty
            ).order_by('?')[:level.question_count]
            
            # 清除旧的关联
            LevelQuestion.objects.filter(level=level).delete()
            
            # 创建新的关联
            for idx, question in enumerate(questions):
                LevelQuestion.objects.create(
                    level=level,
                    question=question,
                    score=100 // level.question_count,
                    order_index=idx
                )
        
        self.stdout.write(f'✓ 关卡题目分配完成')
