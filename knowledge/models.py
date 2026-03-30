from django.db import models

class DanceProject(models.Model):
    """舞蹈项目表（知识图谱核心）"""
    name = models.CharField(max_length=200, verbose_name="舞蹈项目名称")
    description = models.TextField(verbose_name="项目描述")
    category = models.CharField(max_length=100, verbose_name="分类")
    difficulty_level = models.IntegerField(default=1, verbose_name="难度等级（1-5）")
    image = models.ImageField(upload_to='knowledge/%Y%m%d/', blank=True, null=True, verbose_name="图片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "舞蹈项目"
        verbose_name_plural = "舞蹈项目"
    
    def __str__(self):
        return self.name

class ActionModule(models.Model):
    """基础动作模块表"""
    dance_project = models.ForeignKey(DanceProject, on_delete=models.CASCADE, related_name='action_modules', verbose_name="所属舞蹈项目")
    name = models.CharField(max_length=200, verbose_name="动作模块名称")
    description = models.TextField(verbose_name="模块描述")
    order_index = models.IntegerField(default=0, verbose_name="排序索引")
    
    class Meta:
        verbose_name = "基础动作模块"
        verbose_name_plural = "基础动作模块"
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.dance_project.name} - {self.name}"

class SpecificMove(models.Model):
    """具体招式表"""
    action_module = models.ForeignKey(ActionModule, on_delete=models.CASCADE, related_name='specific_moves', verbose_name="所属动作模块")
    name = models.CharField(max_length=200, verbose_name="招式名称")
    description = models.TextField(verbose_name="招式描述")
    difficulty = models.IntegerField(default=1, verbose_name="难度系数（1-10）")
    duration = models.IntegerField(default=30, verbose_name="建议练习时长（秒）")
    order_index = models.IntegerField(default=0, verbose_name="排序索引")
    
    class Meta:
        verbose_name = "具体招式"
        verbose_name_plural = "具体招式"
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.action_module.name} - {self.name}"

class MoveAttribute(models.Model):
    """动作属性表"""
    specific_move = models.ForeignKey(SpecificMove, on_delete=models.CASCADE, related_name='attributes', verbose_name="所属招式")
    force_parts = models.TextField(verbose_name="发力部位")
    common_mistakes = models.TextField(verbose_name="易错点")
    key_points = models.TextField(verbose_name="标准要领")
    precautions = models.TextField(blank=True, verbose_name="注意事项")
    
    class Meta:
        verbose_name = "动作属性"
        verbose_name_plural = "动作属性"
    
    def __str__(self):
        return f"{self.specific_move.name} - 动作属性"

class LearningResource(models.Model):
    """学习资源表"""
    RESOURCE_TYPES = [
        ('video', '教学视频'),
        ('demo', '传承人示范'),
        ('article', '图文教程'),
        ('audio', '音频讲解'),
    ]
    
    specific_move = models.ForeignKey(SpecificMove, on_delete=models.CASCADE, related_name='learning_resources', verbose_name="所属招式")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name="资源类型")
    title = models.CharField(max_length=200, verbose_name="资源标题")
    url = models.URLField(verbose_name="资源链接")
    thumbnail = models.ImageField(upload_to='resources/%Y%m%d/', blank=True, null=True, verbose_name="缩略图")
    duration = models.IntegerField(blank=True, null=True, verbose_name="时长（秒）")
    description = models.TextField(blank=True, verbose_name="资源描述")
    order_index = models.IntegerField(default=0, verbose_name="排序索引")
    
    class Meta:
        verbose_name = "学习资源"
        verbose_name_plural = "学习资源"
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.specific_move.name} - {self.title}"

class KnowledgePoint(models.Model):
    """知识点标签表"""
    specific_move = models.ForeignKey(SpecificMove, on_delete=models.CASCADE, related_name='knowledge_points', verbose_name="关联招式")
    name = models.CharField(max_length=200, verbose_name="知识点名称")
    description = models.TextField(verbose_name="知识点描述")
    category = models.CharField(max_length=100, verbose_name="分类")
    importance_level = models.IntegerField(default=1, verbose_name="重要程度（1-5）")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name="父知识点")
    
    class Meta:
        verbose_name = "知识点标签"
        verbose_name_plural = "知识点标签"
    
    def __str__(self):
        return self.name

class AIQuestion(models.Model):
    """AI 问答记录表"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="用户")
    question = models.TextField(verbose_name="问题")
    answer = models.TextField(verbose_name="回答")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提问时间")
    is_helpful = models.BooleanField(default=False, verbose_name="是否有帮助")
    
    class Meta:
        verbose_name = "AI 问答记录"
        verbose_name_plural = "AI 问答记录"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.question[:50]}"
