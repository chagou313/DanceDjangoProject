from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from knowledge.models import (
    DanceProject, ActionModule, SpecificMove, 
    UserLearningProgress
)
from dance.models import UserProfile
from django.db.models import Count, Q, Avg, Sum
import random


class Command(BaseCommand):
    help = '为 test1111 用户生成真实学习数据'

    def handle(self, *args, **options):
        # 获取用户
        try:
            user = User.objects.get(username='test1111')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('用户 test1111 不存在'))
            return
        
        self.stdout.write(f'\n为用户 {user.username} (ID={user.id}) 生成学习数据...\n')
        
        # 1. 创建或更新用户资料
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'skill_level': 3,
                'available_time_per_week': 8,
                'learning_goal': '系统学习非遗舞蹈，掌握多种传统舞蹈技法',
                'preferred_dance_types': ['民间舞蹈', '古典舞蹈'],
            }
        )
        
        if not created:
            # 更新现有资料
            profile.skill_level = 3
            profile.available_time_per_week = 8
            profile.learning_goal = '系统学习非遗舞蹈，掌握多种传统舞蹈技法'
            profile.preferred_dance_types = ['民间舞蹈', '古典舞蹈']
            profile.save()
        
        self.stdout.write(self.style.SUCCESS('✓ 用户资料已设置'))
        self.stdout.write(f'   - 技能等级: {profile.skill_level}级')
        self.stdout.write(f'   - 每周学习时间: {profile.available_time_per_week}小时')
        self.stdout.write(f'   - 偏好舞种: {", ".join(profile.preferred_dance_types)}\n')
        
        # 2. 获取所有舞蹈项目
        all_projects = list(DanceProject.objects.all())
        if not all_projects:
            self.stdout.write(self.style.ERROR('数据库中没有舞蹈项目数据'))
            return
        
        self.stdout.write(f'找到 {len(all_projects)} 个舞蹈项目\n')
        
        # 3. 选择5个项目进行学习
        selected_projects = random.sample(all_projects, min(5, len(all_projects)))
        
        progress_created = 0
        progress_updated = 0
        
        for idx, project in enumerate(selected_projects):
            self.stdout.write(f'\n处理项目: {project.name}')
            
            # 获取该项目的所有招式
            moves = SpecificMove.objects.filter(
                action_module__dance_project=project
            ).select_related('action_module')
            
            if not moves.exists():
                self.stdout.write(self.style.WARNING(f'  ⚠ 该项目没有招式数据，跳过'))
                continue
            
            move_list = list(moves)
            self.stdout.write(f'  找到 {len(move_list)} 个招式')
            
            # 根据项目索引设置不同的学习进度模式
            if idx == 0:
                # 第1个项目：深入学习，大部分已完成/已掌握
                status_weights = {'mastered': 60, 'completed': 30, 'learning': 10}
                base_proficiency = 75
            elif idx == 1:
                # 第2个项目：中等进度
                status_weights = {'completed': 40, 'learning': 50, 'mastered': 10}
                base_proficiency = 55
            elif idx == 2:
                # 第3个项目：刚开始学习
                status_weights = {'learning': 70, 'not_started': 20, 'completed': 10}
                base_proficiency = 35
            else:
                # 其他项目：少量学习
                status_weights = {'not_started': 50, 'learning': 40, 'completed': 10}
                base_proficiency = 20
            
            # 为每个招式创建学习进度
            for move in move_list:
                # 随机决定状态
                rand = random.randint(1, 100)
                cumulative = 0
                
                if rand <= (cumulative := cumulative + status_weights.get('mastered', 0)):
                    status = 'mastered'
                    proficiency_range = (85, 98)
                elif rand <= (cumulative := cumulative + status_weights.get('completed', 0)):
                    status = 'completed'
                    proficiency_range = (70, 84)
                elif rand <= (cumulative := cumulative + status_weights.get('learning', 0)):
                    status = 'learning'
                    proficiency_range = (20, 69)
                else:
                    status = 'not_started'
                    proficiency_range = (0, 0)
                
                # 计算熟练度
                if status == 'not_started':
                    proficiency_score = 0
                    practice_count = 0
                    total_practice_time = 0
                else:
                    proficiency_score = random.uniform(*proficiency_range)
                    
                    # 根据熟练度反推练习时间
                    # proficiency = (total_time / standard_time) * 100
                    # standard_time = duration * difficulty * 3
                    standard_time = move.duration * move.difficulty * 3
                    total_practice_time = int((proficiency_score / 100) * standard_time)
                    
                    # 练习次数 = 总时间 / 每次平均练习时长（假设每次练习duration秒）
                    practice_count = max(1, total_practice_time // move.duration)
                
                # 创建或更新进度记录
                progress, created = UserLearningProgress.objects.update_or_create(
                    user=user,
                    specific_move=move,
                    defaults={
                        'dance_project': project,
                        'status': status,
                        'proficiency_score': round(proficiency_score, 1),
                        'practice_count': practice_count,
                        'total_practice_time': total_practice_time,
                    }
                )
                
                if created:
                    progress_created += 1
                else:
                    progress_updated += 1
        
        # 4. 统计结果
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('数据生成完成！'))
        self.stdout.write('=' * 70)
        
        # 统计各状态数量
        status_summary = UserLearningProgress.objects.filter(user=user).aggregate(
            total=Count('id'),
            mastered=Count('id', filter=Q(status='mastered')),
            completed=Count('id', filter=Q(status='completed')),
            learning=Count('id', filter=Q(status='learning')),
            not_started=Count('id', filter=Q(status='not_started')),
            avg_proficiency=Avg('proficiency_score'),
            total_practice_time=Sum('total_practice_time'),
            total_practice_count=Sum('practice_count'),
        )
        
        self.stdout.write(f'\n学习数据统计:')
        self.stdout.write(f'   - 学习项目数: {selected_projects.__len__()}')
        self.stdout.write(f'   - 学习招式总数: {status_summary["total"]}')
        self.stdout.write(f'   - 已掌握: {status_summary["mastered"]} 个')
        self.stdout.write(f'   - 已完成: {status_summary["completed"]} 个')
        self.stdout.write(f'   - 学习中: {status_summary["learning"]} 个')
        self.stdout.write(f'   - 未开始: {status_summary["not_started"]} 个')
        self.stdout.write(f'   - 平均熟练度: {status_summary["avg_proficiency"]:.1f}%')
        
        total_hours = status_summary['total_practice_time'] / 3600
        self.stdout.write(f'   - 总练习时长: {total_hours:.1f} 小时 ({status_summary["total_practice_time"]} 秒)')
        self.stdout.write(f'   - 总练习次数: {status_summary["total_practice_count"]} 次')
        
        self.stdout.write(f'\n新增记录: {progress_created} 条')
        self.stdout.write(f'更新记录: {progress_updated} 条')
        
        self.stdout.write('\n现在可以登录 test1111 查看学习进度和个性化推荐！')
        self.stdout.write('访问地址:')
        self.stdout.write('   - 我的进度: http://localhost:8000/knowledge/my-progress/')
        self.stdout.write('   - 个性化推荐: http://localhost:8000/knowledge/recommendations/')
