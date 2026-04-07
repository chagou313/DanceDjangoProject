from django.db import models
from django.contrib.auth.models import User
from origin.models import DanceProject

class News(models.Model):
    """新闻资讯表"""
    CATEGORY_CHOICES = [
        ('science', '科普类'),
        ('activity', '活动类'),
        ('policy', '政策类'),
        ('inheritor', '传承人类资讯'),
    ]
    
    DANCE_TYPE_CHOICES = [
        ('classical', '古典舞'),
        ('folk', '民族舞'),
        ('traditional', '传统舞'),
        ('ethnic', '民间舞'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="标题")
    summary = models.TextField(blank=True, verbose_name="摘要/简介", help_text="简短介绍，用于列表页展示（选填）")
    content = models.TextField(verbose_name="内容")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="资讯类型")
    dance_project = models.ForeignKey(DanceProject, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="舞蹈项目")
    cover_image = models.ImageField(upload_to='news/%Y%m%d/', blank=True, null=True, verbose_name="封面图")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    collections = models.IntegerField(default=0, verbose_name="收藏数")
    views = models.IntegerField(default=0, verbose_name="浏览量")
    is_hot = models.BooleanField(default=False, verbose_name="是否热门")
    
    class Meta:
        verbose_name = "新闻资讯"
        verbose_name_plural = "新闻资讯"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    """评论表"""
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments', verbose_name="资讯")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_comments', verbose_name="用户")
    content = models.TextField(verbose_name="评论内容")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies', verbose_name="父评论")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    
    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} 评论 {self.news.title}'

class UserInteraction(models.Model):
    """用户互动记录表（点赞、收藏）"""
    INTERACTION_TYPES = [
        ('like', '点赞'),
        ('collect', '收藏'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    news = models.ForeignKey(News, on_delete=models.CASCADE, verbose_name="资讯")
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES, verbose_name="互动类型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="互动时间")
    
    class Meta:
        verbose_name = "用户互动记录"
        verbose_name_plural = "用户互动记录"
        unique_together = ['user', 'news', 'interaction_type']
    
    def __str__(self):
        return f'{self.user.username} {self.get_interaction_type_display()} {self.news.title}'

class NewsImage(models.Model):
    """新闻多图表"""
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='images', verbose_name="关联新闻")
    image = models.ImageField(upload_to='news/images/%Y%m%d/', verbose_name="图片")
    caption = models.CharField(max_length=200, blank=True, verbose_name="图片说明")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    
    class Meta:
        verbose_name = "新闻图片"
        verbose_name_plural = "新闻图片"
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        return f'{self.news.title} - 图片 {self.id}'
