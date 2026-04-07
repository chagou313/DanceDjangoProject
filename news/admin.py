from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from .models import News, Comment, UserInteraction, NewsImage

class NewsAdminForm(forms.ModelForm):
    """自定义资讯表单，明确标注舞蹈项目为可选项"""
    class Meta:
        model = News
        fields = '__all__'
        labels = {
            'dance_project': '舞蹈项目（选填）',
        }
        help_texts = {
            'dance_project': '如果该资讯没有明确关联的舞蹈项目，可以留空不选。',
        }

class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 0
    min_num = 0
    max_num = None
    fields = ('image_preview', 'image', 'caption', 'sort_order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;"/>', obj.image.url)
        return "无图片"
    image_preview.short_description = '预览'

    class Media:
        js = ['/static/js/news_paste_images.js', '/static/js/news_editor_toolbar.js', '/static/js/news_cover_paste.js']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ('title', 'category', 'dance_project', 'author', 'views', 'likes', 'collections', 'is_hot', 'created_at')
    list_filter = ('category', 'dance_project', 'is_hot', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [NewsImageInline]
    
    # 自定义 CSS，让表单字段撑满宽度
    class Media:
        css = {
            'all': [
                '/static/css/admin_full_width.css',
            ]
        }
        js = ['/static/js/news_paste_images.js', '/static/js/news_editor_toolbar.js', '/static/js/news_cover_paste.js']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'category', 'dance_project', 'author', 'summary'),
            'description': '💡 提示：在“内容”框中可以直接粘贴截图（Ctrl+V），图片会自动上传并插入到光标位置。<br>📌 注意：“舞蹈项目”为可选项，如果资讯没有明确关联的项目，可以不选。'
        }),
        ('封面图', {
            'fields': ('cover_image',),
            'classes': ('collapse',),
            'description': '封面图为可选项，用于列表页展示'
        }),
        ('统计信息', {
            'fields': ('views', 'likes', 'collections', 'is_hot'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """保存时自动设置作者为当前用户"""
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload_image/', self.admin_site.admin_view(self.upload_image), name='news_upload_image'),
        ]
        return custom_urls + urls

    def upload_image(self, request):
        if request.method == 'POST' and request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            
            # 使用 Django 的默认存储系统
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import uuid
            
            # 生成唯一文件名
            ext = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'png'
            file_name = f"{uuid.uuid4().hex}.{ext}"
            file_path = f"news/images/{file_name}"
            
            # 保存文件
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
            file_url = default_storage.url(saved_path)
            
            return JsonResponse({'url': file_url, 'success': True})
        return JsonResponse({'error': 'Invalid request', 'success': False}, status=400)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('news', 'user', 'parent', 'likes', 'created_at')
    list_filter = ('created_at', 'news__category')
    search_fields = ('content', 'user__username', 'news__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('news', 'user', 'parent')

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'news', 'interaction_type', 'created_at')
    list_filter = ('interaction_type', 'created_at', 'news__category')
    search_fields = ('user__username', 'news__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'news')

@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ('news', 'image_preview', 'caption', 'sort_order')
    list_filter = ('news',)
    search_fields = ('news__title', 'caption')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;"/>', obj.image.url)
        return "无图片"
    image_preview.short_description = '预览'
