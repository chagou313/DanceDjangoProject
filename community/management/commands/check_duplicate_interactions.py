"""
检查并清理重复的点赞和收藏记录
"""
from django.core.management.base import BaseCommand
from community.models import PostLike, PostCollection
from django.contrib.auth.models import User
from django.db.models import Count


class Command(BaseCommand):
    help = '检查并清理重复的点赞和收藏记录'

    def handle(self, *args, **kwargs):
        self.stdout.write('=' * 60)
        self.stdout.write('开始检查重复记录...')
        self.stdout.write('=' * 60)
        
        # 检查点赞记录
        self.stdout.write('\n❤️ 检查点赞记录...')
        total_duplicate_likes = 0
        
        for user in User.objects.all():
            duplicates = PostLike.objects.filter(user=user).values('post_id').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            if duplicates:
                for dup in duplicates:
                    post_id = dup['post_id']
                    count = dup['count']
                    # 保留第一条，删除其余的
                    likes_to_delete = PostLike.objects.filter(user=user, post_id=post_id)[1:]
                    delete_count = likes_to_delete.count()
                    likes_to_delete.delete()
                    
                    self.stdout.write(f'   • 用户 {user.username}: 帖子 ID {post_id} 有 {count} 条记录，已删除 {delete_count} 条')
                    total_duplicate_likes += delete_count
        
        if total_duplicate_likes == 0:
            self.stdout.write('   ✓ 没有发现重复的点赞记录')
        else:
            self.stdout.write(f'   ✓ 共清理 {total_duplicate_likes} 条重复点赞记录')
        
        # 检查收藏记录
        self.stdout.write('\n⭐ 检查收藏记录...')
        total_duplicate_collections = 0
        
        for user in User.objects.all():
            duplicates = PostCollection.objects.filter(user=user).values('post_id').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            if duplicates:
                for dup in duplicates:
                    post_id = dup['post_id']
                    count = dup['count']
                    # 保留第一条，删除其余的
                    collections_to_delete = PostCollection.objects.filter(user=user, post_id=post_id)[1:]
                    delete_count = collections_to_delete.count()
                    collections_to_delete.delete()
                    
                    self.stdout.write(f'   • 用户 {user.username}: 帖子 ID {post_id} 有 {count} 条记录，已删除 {delete_count} 条')
                    total_duplicate_collections += delete_count
        
        if total_duplicate_collections == 0:
            self.stdout.write('   ✓ 没有发现重复的收藏记录')
        else:
            self.stdout.write(f'   ✓ 共清理 {total_duplicate_collections} 条重复收藏记录')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('✨ 重复记录检查清理完成！')
        self.stdout.write('=' * 60)
