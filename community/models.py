from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    """话题分类表"""
    name = models.CharField(max_length=50, unique=True, verbose_name="话题名称")
    description = models.TextField(blank=True, verbose_name="话题描述")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标类名")
    color = models.CharField(max_length=7, default='#D8BF64', verbose_name="主题色")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "话题分类"
        verbose_name_plural = "话题分类"
        ordering = ['-sort_order', 'name']
    
    def __str__(self):
        return self.name

class Post(models.Model):
    """帖子表"""
    STATUS_CHOICES = [
        ('published', '已发布'),
        ('draft', '草稿'),
        ('deleted', '已删除'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name="作者")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="话题")
    tags = models.CharField(max_length=500, blank=True, verbose_name="标签（逗号分隔）")
    cover_image = models.ImageField(upload_to='community/%Y%m%d/', blank=True, null=True, verbose_name="封面图")
    location = models.CharField(max_length=200, blank=True, verbose_name="地点")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', verbose_name="状态")
    views = models.IntegerField(default=0, verbose_name="浏览量")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    collections = models.IntegerField(default=0, verbose_name="收藏数")
    comments_count = models.IntegerField(default=0, verbose_name="评论数")
    is_top = models.BooleanField(default=False, verbose_name="是否置顶")
    is_featured = models.BooleanField(default=False, verbose_name="是否精华")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "帖子"
        verbose_name_plural = "帖子"
        ordering = ['-is_top', '-created_at']
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    """评论表"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="帖子")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments', verbose_name="用户")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name="父评论")
    content = models.TextField(verbose_name="评论内容")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    
    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} 评论 {self.post.title}'

class PostLike(models.Model):
    """帖子点赞记录表"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="帖子")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")
    
    class Meta:
        verbose_name = "帖子点赞记录"
        verbose_name_plural = "帖子点赞记录"
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f'{self.user.username} 点赞 {self.post.title}'

class PostCollection(models.Model):
    """帖子收藏记录表"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="帖子")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")
    
    class Meta:
        verbose_name = "帖子收藏记录"
        verbose_name_plural = "帖子收藏记录"
        unique_together = ['post', 'user']
    
    def __str__(self):
        return f'{self.user.username} 收藏 {self.post.title}'

class Report(models.Model):
    """举报管理表"""
    REPORT_TYPES = [
        ('spam', '垃圾广告'),
        ('inappropriate', '不当内容'),
        ('harassment', '人身攻击'),
        ('copyright', '侵权'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processed', '已处理'),
        ('rejected', '已驳回'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name="举报人")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, verbose_name="被举报帖子")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True, verbose_name="被举报评论")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="举报类型")
    reason = models.TextField(verbose_name="举报原因")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    handler = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='handled_reports', verbose_name="处理人")
    handled_at = models.DateTimeField(blank=True, null=True, verbose_name="处理时间")
    remark = models.TextField(blank=True, verbose_name="处理备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="举报时间")
    
    class Meta:
        verbose_name = "举报记录"
        verbose_name_plural = "举报记录"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.reporter.username} 举报 {self.get_report_type_display()}'
