from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from knowledge.models import (
    DanceProject, ActionModule, SpecificMove, 
    UserLearningProgress
)
from dance.models import UserProfile
from community.models import Post, PostLike, Comment as PostComment, PostCollection
from news.models import News, Comment as NewsComment, UserInteraction
from quiz.models import UserQuizRecord, UserAnswerDetail, Question, Level
from django.db.models import Count, Q, Avg, Sum
import random


class Command(BaseCommand):
    help = '为 chagou 管理员用户生成完整的测试数据（学习进度、答题进度、点赞收藏等）'

    def handle(self, *args, **options):
        # 获取用户
        try:
            user = User.objects.get(username='chagou')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('用户 chagou 不存在'))
            return
        
        self.stdout.write(f'\n为用户 {user.username} (ID={user.id}) 生成完整测试数据...\n')
        
        # ==================== 1. 创建用户资料 ====================
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'skill_level': 4,
                'available_time_per_week': 10,
                'learning_goal': '深入学习中国传统舞蹈，掌握古典舞和民间舞的核心技法',
                'preferred_dance_types': ['古典舞蹈', '民间舞蹈'],
            }
        )
        
        if not created:
            profile.skill_level = 4
            profile.available_time_per_week = 10
            profile.learning_goal = '深入学习中国传统舞蹈，掌握古典舞和民间舞的核心技法'
            profile.preferred_dance_types = ['古典舞蹈', '民间舞蹈']
            profile.save()
        
        self.stdout.write(self.style.SUCCESS('✓ 用户资料已设置'))
        self.stdout.write(f'   - 技能等级: {profile.skill_level}级')
        self.stdout.write(f'   - 每周学习时间: {profile.available_time_per_week}小时')
        self.stdout.write(f'   - 偏好舞种: {", ".join(profile.preferred_dance_types)}\n')
        
        # ==================== 2. 生成学习进度数据 ====================
        self.stdout.write('\n【生成学习进度数据】')
        all_projects = list(DanceProject.objects.all())
        if not all_projects:
            self.stdout.write(self.style.ERROR('数据库中没有舞蹈项目数据'))
            return
        
        self.stdout.write(f'找到 {len(all_projects)} 个舞蹈项目\n')
        
        # 选择8个项目进行学习（更多项目让推荐更丰富）
        selected_projects = random.sample(all_projects, min(8, len(all_projects)))
        
        progress_created = 0
        progress_updated = 0
        
        for idx, project in enumerate(selected_projects):
            moves = SpecificMove.objects.filter(
                action_module__dance_project=project
            ).select_related('action_module')
            
            if not moves.exists():
                continue
            
            move_list = list(moves)
            
            # 根据项目索引设置不同的学习进度模式
            if idx < 2:
                # 前2个项目：深入学习，大部分已完成/已掌握
                status_weights = {'mastered': 65, 'completed': 25, 'learning': 10}
            elif idx < 4:
                # 第3-4个项目：中等进度
                status_weights = {'completed': 45, 'learning': 45, 'mastered': 10}
            elif idx < 6:
                # 第5-6个项目：刚开始学习
                status_weights = {'learning': 70, 'not_started': 20, 'completed': 10}
            else:
                # 其他项目：少量学习
                status_weights = {'not_started': 50, 'learning': 40, 'completed': 10}
            
            for move in move_list:
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
                
                if status == 'not_started':
                    proficiency_score = 0
                    practice_count = 0
                    total_practice_time = 0
                else:
                    proficiency_score = random.uniform(*proficiency_range)
                    standard_time = move.duration * move.difficulty * 3
                    total_practice_time = int((proficiency_score / 100) * standard_time)
                    practice_count = max(1, total_practice_time // move.duration)
                
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
        
        self.stdout.write(self.style.SUCCESS(f'✓ 学习进度: 新增 {progress_created} 条，更新 {progress_updated} 条'))
        
        # ==================== 3. 生成答题进度数据 ====================
        self.stdout.write('\n【生成答题进度数据】')
        questions = Question.objects.all()
        levels = Level.objects.filter(is_active=True)
        
        if questions.exists() and levels.exists():
            question_list = list(questions)
            level_list = list(levels)
            
            # 创建5个答题记录
            records_created = 0
            total_correct = 0
            total_questions = 0
            
            for i in range(5):
                level = random.choice(level_list)
                # 随机选择10道题
                selected_questions = random.sample(question_list, min(10, len(question_list)))
                
                correct_count = 0
                wrong_count = 0
                
                # 创建答题记录
                from django.utils import timezone
                start_time = timezone.now()
                
                quiz_record = UserQuizRecord.objects.create(
                    user=user,
                    level=level,
                    start_time=start_time,
                    end_time=start_time,
                    total_questions=len(selected_questions),
                    current_question_index=len(selected_questions),
                    is_completed=True,
                )
                
                # 为每道题创建答题详情
                for idx, question in enumerate(selected_questions):
                    # 70%正确率
                    is_correct = random.random() < 0.7
                    if is_correct:
                        correct_count += 1
                    else:
                        wrong_count += 1
                    
                    UserAnswerDetail.objects.create(
                        quiz_record=quiz_record,
                        question=question,
                        user_answer='A' if is_correct else 'B',
                        is_correct=is_correct,
                        time_spent=random.randint(10, 60),
                    )
                
                # 更新答题记录
                score = correct_count * 10
                quiz_record.score = score
                quiz_record.correct_answers = correct_count
                quiz_record.wrong_answers = wrong_count
                quiz_record.is_passed = score >= level.required_score
                quiz_record.save()
                
                total_correct += correct_count
                total_questions += len(selected_questions)
                records_created += 1
            
            self.stdout.write(self.style.SUCCESS(f'✓ 答题记录: 创建 {records_created} 次答题，共 {total_questions} 题，正确 {total_correct} 题'))
        else:
            self.stdout.write(self.style.WARNING('⚠ 数据库中没有题目或关卡数据'))
        
        # ==================== 4. 生成社区互动数据 ====================
        self.stdout.write('\n【生成社区互动数据】')
        posts = Post.objects.all()
        if posts.exists():
            post_list = list(posts)
            selected_posts = random.sample(post_list, min(20, len(post_list)))
            
            likes_created = 0
            comments_created = 0
            collections_created = 0
            
            for post in selected_posts:
                # 点赞（60%概率）
                if random.random() < 0.6:
                    PostLike.objects.get_or_create(user=user, post=post)
                    likes_created += 1
                
                # 评论（30%概率）
                if random.random() < 0.3:
                    comment_text = random.choice([
                        '这个动作要领讲得很清楚！',
                        '学习了，谢谢分享',
                        '请问这个动作有什么注意事项吗？',
                        '很实用的技巧',
                        '收藏了，慢慢练习',
                        '老师教得真好',
                        '这个视频很有帮助',
                    ])
                    PostComment.objects.create(
                        user=user,
                        post=post,
                        content=comment_text
                    )
                    comments_created += 1
                
                # 收藏（20%概率）
                if random.random() < 0.2:
                    PostCollection.objects.get_or_create(user=user, post=post)
                    collections_created += 1
            
            self.stdout.write(self.style.SUCCESS(f'✓ 社区互动: 点赞 {likes_created} 次，评论 {comments_created} 条，收藏 {collections_created} 次'))
        else:
            self.stdout.write(self.style.WARNING('⚠ 数据库中没有帖子数据'))
        
        # ==================== 5. 生成资讯互动数据 ====================
        self.stdout.write('\n【生成资讯互动数据】')
        articles = News.objects.all()
        if articles.exists():
            article_list = list(articles)
            selected_articles = random.sample(article_list, min(15, len(article_list)))
            
            news_likes = 0
            news_comments = 0
            news_collections = 0
            
            for article in selected_articles:
                # 点赞（50%概率）
                if random.random() < 0.5:
                    UserInteraction.objects.get_or_create(
                        user=user,
                        news=article,
                        interaction_type='like'
                    )
                    news_likes += 1
                
                # 评论（20%概率）
                if random.random() < 0.2:
                    comment_text = random.choice([
                        '很有价值的资讯',
                        '感谢分享',
                        '学到了很多',
                        '期待更多内容',
                        '写得很好',
                    ])
                    NewsComment.objects.create(
                        user=user,
                        news=article,
                        content=comment_text
                    )
                    news_comments += 1
                
                # 收藏（15%概率）
                if random.random() < 0.15:
                    UserInteraction.objects.get_or_create(
                        user=user,
                        news=article,
                        interaction_type='collect'
                    )
                    news_collections += 1
            
            self.stdout.write(self.style.SUCCESS(f'✓ 资讯互动: 点赞 {news_likes} 次，评论 {news_comments} 条，收藏 {news_collections} 次'))
        else:
            self.stdout.write(self.style.WARNING('⚠ 数据库中没有资讯数据'))
        
        # ==================== 6. 统计总结 ====================
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('数据生成完成！'))
        self.stdout.write('=' * 70)
        
        # 学习统计
        status_summary = UserLearningProgress.objects.filter(user=user).aggregate(
            total=Count('id'),
            mastered=Count('id', filter=Q(status='mastered')),
            completed=Count('id', filter=Q(status='completed')),
            learning=Count('id', filter=Q(status='learning')),
            not_started=Count('id', filter=Q(status='not_started')),
            avg_proficiency=Avg('proficiency_score'),
            total_practice_time=Sum('total_practice_time'),
        )
        
        self.stdout.write(f'\n📊 学习数据统计:')
        self.stdout.write(f'   - 学习项目数: {selected_projects.__len__()}')
        self.stdout.write(f'   - 学习招式总数: {status_summary["total"]}')
        self.stdout.write(f'   - 已掌握: {status_summary["mastered"]} 个')
        self.stdout.write(f'   - 已完成: {status_summary["completed"]} 个')
        self.stdout.write(f'   - 学习中: {status_summary["learning"]} 个')
        self.stdout.write(f'   - 未开始: {status_summary["not_started"]} 个')
        self.stdout.write(f'   - 平均熟练度: {status_summary["avg_proficiency"]:.1f}%')
        
        total_hours = status_summary['total_practice_time'] / 3600
        self.stdout.write(f'   - 总练习时长: {total_hours:.1f} 小时')
        
        # 答题统计
        quiz_stats = UserQuizRecord.objects.filter(user=user).aggregate(
            total=Count('id'),
            correct=Sum('correct_answers'),
            total_questions=Sum('total_questions'),
        )
        if quiz_stats['total'] and quiz_stats['total_questions']:
            accuracy = (quiz_stats['correct'] / quiz_stats['total_questions']) * 100
            self.stdout.write(f'\n📝 答题统计:')
            self.stdout.write(f'   - 答题次数: {quiz_stats["total"]} 次')
            self.stdout.write(f'   - 答题总数: {quiz_stats["total_questions"]} 题')
            self.stdout.write(f'   - 正确数: {quiz_stats["correct"]} 题')
            self.stdout.write(f'   - 正确率: {accuracy:.1f}%')
        
        # 社区统计
        community_stats = {
            'likes': PostLike.objects.filter(user=user).count(),
            'comments': PostComment.objects.filter(user=user).count(),
            'collections': PostCollection.objects.filter(user=user).count(),
        }
        self.stdout.write(f'\n💬 社区互动:')
        self.stdout.write(f'   - 点赞: {community_stats["likes"]} 次')
        self.stdout.write(f'   - 评论: {community_stats["comments"]} 条')
        self.stdout.write(f'   - 收藏: {community_stats["collections"]} 次')
        
        self.stdout.write(f'\n现在可以登录 chagou 查看个性化推荐！')
        self.stdout.write('访问地址:')
        self.stdout.write('   - 我的进度: http://localhost:8000/knowledge/my-progress/')
        self.stdout.write('   - 个性化推荐: http://localhost:8000/knowledge/recommendations/')
        self.stdout.write('   - 答题进度: http://localhost:8000/quiz/user_progress/')
        self.stdout.write('   - 我的错题: http://localhost:8000/quiz/wrong/\n')
