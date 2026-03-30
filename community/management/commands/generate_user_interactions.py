"""
生成用户互动测试数据（点赞、收藏、评论）
"""
from django.core.management.base import BaseCommand
from community.models import Post, PostLike, PostCollection, Comment
from django.contrib.auth.models import User
import random


class Command(BaseCommand):
    help = '为用户生成点赞、收藏、评论测试数据'

    def handle(self, *args, **kwargs):
        self.stdout.write('=' * 60)
        self.stdout.write('开始生成用户互动测试数据...')
        self.stdout.write('=' * 60)
        
        # 获取所有用户和帖子
        users = list(User.objects.all()[:5])
        posts = list(Post.objects.all())
        
        if not users:
            self.stdout.write('错误：没有用户')
            return
        
        if not posts:
            self.stdout.write('错误：没有帖子')
            return
        
        self.stdout.write(f'\n📊 数据来源:')
        self.stdout.write(f'   - 用户数：{len(users)}')
        self.stdout.write(f'   - 帖子数：{len(posts)}')
        
        # 生成点赞记录
        self.stdout.write('\n❤️ 生成点赞记录...')
        like_count = 0
        for user in users:
            # 每个用户随机点赞 3-8 个帖子
            posts_to_like = random.sample(posts, min(random.randint(3, 8), len(posts)))
            for post in posts_to_like:
                like, created = PostLike.objects.get_or_create(
                    user=user,
                    post=post
                )
                if created:
                    like_count += 1
        
        # 更新帖子的点赞数
        for post in posts:
            post.likes = PostLike.objects.filter(post=post).count()
            post.save(update_fields=['likes'])
        
        self.stdout.write(f'   ✓ 新增 {like_count} 条点赞记录')
        
        # 生成收藏记录
        self.stdout.write('\n⭐ 生成收藏记录...')
        collection_count = 0
        for user in users:
            # 每个用户随机收藏 2-5 个帖子
            posts_to_collect = random.sample(posts, min(random.randint(2, 5), len(posts)))
            for post in posts_to_collect:
                collection, created = PostCollection.objects.get_or_create(
                    user=user,
                    post=post
                )
                if created:
                    collection_count += 1
        
        # 更新帖子的收藏数
        for post in posts:
            post.collections = PostCollection.objects.filter(post=post).count()
            post.save(update_fields=['collections'])
        
        self.stdout.write(f'   ✓ 新增 {collection_count} 条收藏记录')
        
        # 生成评论记录
        self.stdout.write('\n💬 生成评论记录...')
        comment_count = 0
        comments_data = [
            "写得真好，学到了很多！",
            "感谢分享，非常实用的内容。",
            "这个观点很有见解，受教了！",
            "舞蹈技巧讲解得很详细，赞一个！",
            "有机会一定要去看看现场表演。",
            "传统文化需要我们一起传承和发扬。",
            "期待更多优质的内容！",
            "作者很用心，支持一下！",
            "讲得太好了，已收藏慢慢学习。",
            "希望能多举办一些这样的活动。",
            "民族的就是世界的！",
            "为孩子们的教育方法点赞！",
        ]
        
        for user in users:
            # 每个用户随机评论 3-6 个帖子
            posts_to_comment = random.sample(posts, min(random.randint(3, 6), len(posts)))
            for post in posts_to_comment:
                content = random.choice(comments_data)
                Comment.objects.create(
                    user=user,
                    post=post,
                    content=content
                )
                comment_count += 1
        
        # 更新帖子的评论数
        for post in posts:
            post.comments_count = Comment.objects.filter(post=post, is_deleted=False).count()
            post.save(update_fields=['comments_count'])
        
        self.stdout.write(f'   ✓ 新增 {comment_count} 条评论记录')
        
        # 统计结果
        self.stdout.write('\n✅ 数据统计:')
        self.stdout.write(f'   - 总点赞数：{PostLike.objects.count()}')
        self.stdout.write(f'   - 总收藏数：{PostCollection.objects.count()}')
        self.stdout.write(f'   - 总评论数：{Comment.objects.count()}')
        
        # 显示每个用户的统计数据
        self.stdout.write('\n👥 用户互动统计:')
        for user in users:
            user_likes = PostLike.objects.filter(user=user).count()
            user_collections = PostCollection.objects.filter(user=user).count()
            user_comments = Comment.objects.filter(user=user, is_deleted=False).count()
            user_posts = Post.objects.filter(author=user).count()
            
            self.stdout.write(f'   • {user.username}:')
            self.stdout.write(f'      发帖：{user_posts} | 点赞：{user_likes} | 收藏：{user_collections} | 评论：{user_comments}')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('✨ 用户互动数据生成完成！')
        self.stdout.write('=' * 60)
