from django.contrib import admin
from .models import Topic, Post, Comment, PostLike, PostCollection, Report

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'color', 'sort_order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['-sort_order', 'name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'topic', 'status', 'views', 'likes', 'comments_count', 'is_top', 'is_featured', 'created_at']
    list_filter = ['status', 'topic', 'is_top', 'is_featured', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-is_top', '-created_at']
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'parent', 'content', 'likes', 'is_deleted', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['content', 'user__username', 'post__title']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    ordering = ['-created_at']

@admin.register(PostCollection)
class PostCollectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']
    ordering = ['-created_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'post', 'comment', 'report_type', 'status', 'handler', 'created_at']
    list_filter = ['status', 'report_type', 'created_at']
    search_fields = ['reason', 'reporter__username', 'post__title']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
