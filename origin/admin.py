from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Region, DanceProject, Inheritor

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level', 'parent')
    search_fields = ('name', 'code')
    list_filter = ('level',)

@admin.register(DanceProject)
class DanceProjectAdmin(admin.ModelAdmin):
    list_display = ('project_code', 'name', 'level', 'dance_type', 'declare_region', 'views')
    search_fields = ('project_code', 'name', 'declare_region')
    list_filter = ('level', 'dance_type', 'announce_time')
    ordering = ('project_code',)
    change_form_template = 'admin/danceproject_change_form.html'
    
    def response_change(self, request, obj):
        """保存后自动跳转到下一个项目"""
        # 获取下一个项目
        next_obj = DanceProject.objects.filter(id__gt=obj.id).order_by('id').first()
        if next_obj:
            messages.success(request, f'已保存"{obj.name}"，跳转到"{next_obj.name}"')
            return redirect(reverse('admin:origin_danceproject_change', args=[next_obj.id]))
        else:
            messages.info(request, f'已保存"{obj.name}"，这是最后一个项目！')
        
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        """新增后也跳转到下一个"""
        next_obj = DanceProject.objects.filter(id__gt=obj.id).order_by('id').first()
        if next_obj:
            messages.success(request, f'已创建"{obj.name}"，跳转到"{next_obj.name}"')
            return redirect(reverse('admin:origin_danceproject_change', args=[next_obj.id]))
        
        return super().response_add(request, obj, post_url_continue)

@admin.register(Inheritor)
class InheritorAdmin(admin.ModelAdmin):
    list_display = ('inheritor_code', 'name', 'gender', 'project_name', 'declare_region')
    search_fields = ('name', 'project_name', 'inheritor_code')
    list_filter = ('gender', 'ethnicity')

