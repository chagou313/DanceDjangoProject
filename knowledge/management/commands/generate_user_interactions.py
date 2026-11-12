from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from community.models import Post, PostLike, PostCollection, Comment
from knowledge.models import DanceProject, UserLearningProgress
import random
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = '为 test1111 用户生成真实的社区互动数据（点赞、收藏、评论）'

    def handle(self, *args, **options):
        # 获取用户
        try:
            user = User.objects.get(username='test1111')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('用户 test1111 不存在'))
            return
        
        self.stdout.write(f'\n为用户 {user.username} (ID={user.id}) 生成社区互动数据...\n')
        
        # 1. 获取用户学习的舞蹈项目
        learned_projects = UserLearningProgress.objects.filter(
            user=user
        ).values_list('dance_project', flat=True).distinct()
        
        if not learned_projects:
            self.stdout.write(self.style.WARNING('该用户还没有学习任何项目，先运行 generate_test_user_data'))
            return
        
        learned_projects = list(learned_projects)
        self.stdout.write(f'✓ 用户学习了 {len(learned_projects)} 个项目\n')
        
        # 2. 获取所有帖子
        all_posts = list(Post.objects.all().order_by('-created_at'))
        if not all_posts:
            self.stdout.write(self.style.ERROR('数据库中没有帖子数据'))
            return
        
        self.stdout.write(f'找到 {len(all_posts)} 个帖子\n')
        
        # 3. 根据用户学习兴趣筛选相关帖子
        related_posts = []
        for post in all_posts:
            # 检查帖子是否与用户学习的项目相关
            is_related = False
            
            # 通过标题或内容匹配
            for project_id in learned_projects:
                try:
                    from origin.models import DanceProject as OriginDanceProject
                    project = OriginDanceProject.objects.get(id=project_id)
                    if project.name in post.title or project.name in post.content:
                        is_related = True
                        break
                except:
                    pass
            
            # 也检查是否包含舞蹈相关关键词
            dance_keywords = ['舞蹈', '舞步', '招式', '动作', '技巧', '练习']
            if any(keyword in post.title or keyword in post.content for keyword in dance_keywords):
                is_related = True
            
            if is_related:
                related_posts.append(post)
        
        self.stdout.write(f'相关帖子: {len(related_posts)} 个\n')
        
        # 4. 生成点赞数据
        self.stdout.write('\n生成点赞数据...')
        liked_count = 0
        
        # 对相关帖子有更高的点赞概率
        for post in related_posts[:30]:  # 最多点赞30个相关帖子
            if random.random() < 0.7:  # 70%概率点赞
                PostLike.objects.get_or_create(user=user, post=post)
                liked_count += 1
        
        # 对其他帖子也有少量点赞
        other_posts = [p for p in all_posts if p not in related_posts]
        for post in random.sample(other_posts, min(15, len(other_posts))):
            PostLike.objects.get_or_create(user=user, post=post)
            liked_count += 1
        
        self.stdout.write(self.style.SUCCESS(f' ✓ 创建了 {liked_count} 个点赞'))
        
        # 5. 生成收藏数据
        self.stdout.write('\n生成收藏数据...')
        collected_count = 0
        
        # 收藏通常是点赞的子集，且更偏向高质量/相关内容
        liked_posts = PostLike.objects.filter(user=user).values_list('post', flat=True)
        liked_posts_list = list(liked_posts)
        
        for post_id in liked_posts_list:
            post = Post.objects.get(id=post_id)
            # 60%的点赞会转化为收藏
            if random.random() < 0.6:
                PostCollection.objects.get_or_create(user=user, post=post)
                collected_count += 1
        
        self.stdout.write(self.style.SUCCESS(f' ✓ 创建了 {collected_count} 个收藏'))
        
        # 6. 生成评论数据
        self.stdout.write('\n生成评论数据...')
        comment_count = 0
        
        # 对部分点赞的帖子进行评论
        liked_post_objects = Post.objects.filter(id__in=liked_posts_list)
        commented_posts = random.sample(list(liked_post_objects), min(12, len(liked_post_objects)))
        
        sample_comments = [
            "这个动作讲解得很清楚，学到了很多！",
            "请问这个招式的要领是什么？",
            "太棒了，收藏了慢慢练",
            "有没有视频示范呀？",
            "这个技巧我之前一直做不好，看了你的分享明白了",
            "感谢分享，很有帮助",
            "练习的时候要注意什么吗？",
            "这个舞蹈的文化背景能介绍一下吗？",
            "已经按照这个方法练习了一周，效果很好",
            "希望能出更多这样的教程",
            "这个动作的难度怎么样？适合初学者吗？",
            "请问每天练习多久比较合适？",
        ]
        
        for post in commented_posts:
            comment_text = random.choice(sample_comments)
            Comment.objects.create(
                user=user,
                post=post,  # 已经是 Post 对象
                content=comment_text,
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            comment_count += 1
        
        self.stdout.write(self.style.SUCCESS(f' ✓ 创建了 {comment_count} 条评论'))
        
        # 7. 生成一些自己的帖子
        self.stdout.write('\n生成用户的发帖记录...')
        post_count = 0
        
        user_post_topics = [
            {
                'title': '学习蜈蚣舞的心得体会',
                'content': '最近开始学习蜈蚣舞，这个舞蹈的动作很有特色，特别是模仿蜈蚣爬行的动作，需要很好的协调性。大家有什么练习建议吗？',
            },
            {
                'title': '请教龙舞的基本步伐',
                'content': '刚开始学习龙舞，基础步伐总是掌握不好，有没有前辈可以指点一下？',
            },
            {
                'title': '分享一个练习小技巧',
                'content': '发现每天早晚各练习30分钟比一次性练2小时效果更好，大家可以试试。',
            },
        ]
        
        for post_data in user_post_topics:
            Post.objects.create(
                author=user,
                title=post_data['title'],
                content=post_data['content'],
                created_at=timezone.now() - timedelta(days=random.randint(5, 60))
            )
            post_count += 1
        
        self.stdout.write(self.style.SUCCESS(f' ✓ 创建了 {post_count} 个帖子'))
        
        # 8. 统计总结
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('社区互动数据生成完成！'))
        self.stdout.write('=' * 70)
        
        # 统计数据
        total_likes = PostLike.objects.filter(user=user).count()
        total_collections = PostCollection.objects.filter(user=user).count()
        total_comments = Comment.objects.filter(user=user).count()
        total_posts = Post.objects.filter(author=user).count()
        
        self.stdout.write(f'\n互动数据统计:')
        self.stdout.write(f'   - 点赞数: {total_likes}')
        self.stdout.write(f'   - 收藏数: {total_collections}')
        self.stdout.write(f'   - 评论数: {total_comments}')
        self.stdout.write(f'   - 发帖数: {total_posts}')
        
        # 分析兴趣偏好
        self.stdout.write(f'\n兴趣分析:')
        
        # 统计点赞帖子的关键词
        liked_posts_detail = PostLike.objects.filter(user=user).select_related('post')
        keyword_stats = {}
        
        for like in liked_posts_detail:
            post = like.post
            # 提取可能的舞蹈项目名称
            for project_id in learned_projects:
                try:
                    from origin.models import DanceProject as OriginDanceProject
                    project = OriginDanceProject.objects.get(id=project_id)
                    if project.name in post.title or project.name in post.content:
                        keyword_stats[project.name] = keyword_stats.get(project.name, 0) + 1
                except:
                    pass
        
        if keyword_stats:
            sorted_keywords = sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)
            self.stdout.write('   最感兴趣的舞蹈项目:')
            for name, count in sorted_keywords[:5]:
                self.stdout.write(f'     - {name}: {count} 次互动')
        
        self.stdout.write('\n现在可以查看个性化推荐，系统会根据这些互动数据生成更精准的推荐！')
        self.stdout.write('访问地址: http://localhost:8000/knowledge/recommendations/')
