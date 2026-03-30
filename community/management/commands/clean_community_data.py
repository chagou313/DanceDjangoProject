"""
清理交流社区模块的所有测试数据
"""
from django.core.management.base import BaseCommand
from community.models import Topic, Post, Comment, PostLike, PostCollection, Report
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = '清理交流社区模块的所有测试数据'

    def handle(self, *args, **kwargs):
        self.stdout.write('=' * 60)
        self.stdout.write('开始清理交流社区测试数据...')
        self.stdout.write('=' * 60)
        
        # 1. 统计当前数据量
        self.stdout.write('\n📊 清理前数据统计:')
        self.stdout.write(f'   - 话题分类：{Topic.objects.count()} 条')
        self.stdout.write(f'   - 帖子：{Post.objects.count()} 条')
        self.stdout.write(f'   - 评论：{Comment.objects.count()} 条')
        self.stdout.write(f'   - 点赞记录：{PostLike.objects.count()} 条')
        self.stdout.write(f'   - 收藏记录：{PostCollection.objects.count()} 条')
        self.stdout.write(f'   - 举报记录：{Report.objects.count()} 条')
        
        # 2. 删除数据（注意顺序，因为有外键依赖）
        self.stdout.write('\n🗑️  开始删除数据:')
        
        # 删除举报记录
        report_count = Report.objects.count()
        Report.objects.all().delete()
        self.stdout.write(f'   ✓ 删除 {report_count} 条举报记录')
        
        # 删除收藏记录
        collection_count = PostCollection.objects.count()
        PostCollection.objects.all().delete()
        self.stdout.write(f'   ✓ 删除 {collection_count} 条收藏记录')
        
        # 删除点赞记录
        like_count = PostLike.objects.count()
        PostLike.objects.all().delete()
        self.stdout.write(f'   ✓ 删除 {like_count} 条点赞记录')
        
        # 删除评论
        comment_count = Comment.objects.count()
        Comment.objects.all().delete()
        self.stdout.write(f'   ✓ 删除 {comment_count} 条评论')
        
        # 删除帖子
        post_count = Post.objects.count()
        Post.objects.all().delete()
        self.stdout.write(f'   ✓ 删除 {post_count} 条帖子')
        
        # 删除话题分类
        topic_count = Topic.objects.count()
        Topic.objects.all().delete()
        self.stdout.write(f'   ✓ 删除 {topic_count} 个话题分类')
        
        # 3. 验证删除结果
        self.stdout.write('\n✅ 清理后数据统计:')
        self.stdout.write(f'   - 话题分类：{Topic.objects.count()} 条')
        self.stdout.write(f'   - 帖子：{Post.objects.count()} 条')
        self.stdout.write(f'   - 评论：{Comment.objects.count()} 条')
        self.stdout.write(f'   - 点赞记录：{PostLike.objects.count()} 条')
        self.stdout.write(f'   - 收藏记录：{PostCollection.objects.count()} 条')
        self.stdout.write(f'   - 举报记录：{Report.objects.count()} 条')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('✨ 交流社区测试数据清理完成！')
        self.stdout.write('=' * 60)
