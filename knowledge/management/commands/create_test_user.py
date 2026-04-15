"""
创建测试用户及其相关数据
用于测试个性化推荐功能
使用方法: python manage.py create_test_user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dance.models import UserProfile
from knowledge.models import DanceProject, ActionModule, SpecificMove, UserLearningProgress
from origin.models import DanceProject as OriginDanceProject
import random


class Command(BaseCommand):
    help = '创建有完整数据的测试用户'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('创建测试用户及相关数据'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # 1. 创建或获取测试用户
        username = 'testuser'
        email = 'test@example.com'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': '测试',
                'last_name': '用户',
            }
        )
        
        if created:
            user.set_password('test123456')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ 创建用户: {username} (密码: test123456)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ 使用已存在用户: {username}'))

        # 2. 创建或更新用户资料
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'skill_level': 3,
                'available_time_per_week': 10,
                'learning_goal': '系统学习非遗舞蹈，掌握2-3种舞蹈的基本技法',
                'preferred_dance_types': ['民间舞蹈', '传统舞蹈'],
                'city': '北京',
                'region': '华北',
            }
        )
        
        if not profile_created:
            # 更新现有资料
            profile.skill_level = 3
            profile.available_time_per_week = 10
            profile.learning_goal = '系统学习非遗舞蹈，掌握2-3种舞蹈的基本技法'
            profile.preferred_dance_types = ['民间舞蹈', '传统舞蹈']
            profile.save()
        
        self.stdout.write(self.style.SUCCESS(f'✓ 用户资料已设置:'))
        self.stdout.write(f'   - 技能等级: {profile.skill_level}级')
        self.stdout.write(f'   - 每周学习时间: {profile.available_time_per_week}小时')
        self.stdout.write(f'   - 偏好舞种: {", ".join(profile.preferred_dance_types)}')

        # 3. 获取一些舞蹈项目
        dance_projects = list(DanceProject.objects.all()[:10])
        
        if not dance_projects:
            self.stdout.write(self.style.WARNING('\n⚠️  知识库中没有舞蹈项目，尝试从 origin 表同步...'))
            # 从 origin 表同步前5个项目
            origin_projects = OriginDanceProject.objects.all()[:5]
            for origin_proj in origin_projects:
                kp_proj, _ = DanceProject.objects.get_or_create(
                    name=origin_proj.name,
                    defaults={
                        'description': origin_proj.introduction or f'{origin_proj.name}是非物质文化遗产项目',
                        'category': origin_proj.get_dance_type_display() if hasattr(origin_proj, 'get_dance_type_display') else '传统舞蹈',
                        'difficulty_level': random.randint(2, 4),
                    }
                )
                dance_projects.append(kp_proj)
                self.stdout.write(f'   ✓ 同步项目: {kp_proj.name}')

        if not dance_projects:
            self.stdout.write(self.style.ERROR('\n✗ 无法获取舞蹈项目数据'))
            return

        # 4. 创建学习进度数据
        self.stdout.write('\n创建学习进度数据...')
        
        progress_states = ['not_started', 'learning', 'completed', 'mastered']
        created_count = 0
        
        for i, project in enumerate(dance_projects[:5]):
            # 获取该项目的招式
            moves = SpecificMove.objects.filter(
                action_module__dance_project=project
            )[:3]
            
            if not moves.exists():
                # 如果没有招式，跳过
                continue
            
            for move in moves:
                # 根据项目索引设置不同的学习状态
                if i == 0:
                    state = 'mastered'  # 第一个项目已掌握
                    proficiency = random.uniform(85, 95)
                elif i == 1:
                    state = 'completed'  # 第二个项目已完成
                    proficiency = random.uniform(70, 85)
                elif i == 2:
                    state = 'learning'  # 第三个项目学习中
                    proficiency = random.uniform(40, 70)
                else:
                    state = random.choice(['not_started', 'learning'])
                    proficiency = random.uniform(10, 50) if state == 'learning' else 0
                
                # 创建或更新学习进度
                progress, prog_created = UserLearningProgress.objects.get_or_create(
                    user=user,
                    specific_move=move,
                    defaults={
                        'dance_project': project,
                        'status': state,
                        'proficiency_score': proficiency,
                        'practice_count': random.randint(5, 30) if state != 'not_started' else 0,
                        'total_practice_time': random.randint(600, 3600) if state != 'not_started' else 0,
                        'difficulty_rating': random.uniform(3, 7),
                    }
                )
                
                if not prog_created:
                    # 更新现有进度
                    progress.status = state
                    progress.proficiency_score = proficiency
                    progress.save()
                
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ 创建了 {created_count} 条学习进度记录'))

        # 5. 打印总结
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('测试用户创建完成！'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'\n登录信息:')
        self.stdout.write(f'   用户名: {username}')
        self.stdout.write(f'   密码: test123456')
        self.stdout.write(f'\n数据概览:')
        self.stdout.write(f'   - 学习项目数: {dance_projects[:5].__len__()}')
        self.stdout.write(f'   - 学习进度记录: {UserLearningProgress.objects.filter(user=user).count()}')
        
        # 统计各状态数量
        status_labels = {
            'not_started': '未开始',
            'learning': '学习中',
            'completed': '已完成',
            'mastered': '已掌握'
        }
        for state, label in status_labels.items():
            count = UserLearningProgress.objects.filter(user=user, status=state).count()
            if count > 0:
                self.stdout.write(f'   - {label}: {count} 条')
        
        self.stdout.write('\n现在可以登录并访问个性化推荐页面查看效果！')
        self.stdout.write('访问地址: http://localhost:8000/knowledge/recommendations/')
