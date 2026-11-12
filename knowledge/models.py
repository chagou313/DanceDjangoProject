from django.db import models

from .storage import video_storage

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
    video_file = models.FileField(upload_to='resource/', storage=video_storage, blank=True, null=True, verbose_name="视频文件")
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


class UserLearningProgress(models.Model):
    """用户学习进度追踪表"""
    STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('learning', '学习中'),
        ('completed', '已完成'),
        ('mastered', '已掌握'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='learning_progress', verbose_name="用户")
    dance_project = models.ForeignKey(DanceProject, on_delete=models.CASCADE, related_name='user_progress', verbose_name="舞蹈项目")
    specific_move = models.ForeignKey('SpecificMove', on_delete=models.CASCADE, related_name='user_progress', verbose_name="具体招式")
    
    # 学习状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name="学习状态")
    
    # 学习数据
    practice_count = models.IntegerField(default=0, verbose_name="练习次数")
    total_practice_time = models.IntegerField(default=0, verbose_name="总练习时长(秒)")
    last_practice_time = models.DateTimeField(null=True, blank=True, verbose_name="最后练习时间")
    
    # 能力评估
    proficiency_score = models.FloatField(default=0.0, verbose_name="熟练度(0-100)")
    difficulty_rating = models.FloatField(default=0.0, verbose_name="用户感知难度(1-10)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户学习进度"
        verbose_name_plural = "用户学习进度"
        unique_together = ['user', 'specific_move']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.specific_move.name} ({self.get_status_display()})"


class UserKnowledgeMastery(models.Model):
    """用户知识点掌握度表"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='knowledge_mastery', verbose_name="用户")
    knowledge_point = models.ForeignKey(KnowledgePoint, on_delete=models.CASCADE, related_name='user_mastery', verbose_name="知识点")
    
    mastery_level = models.FloatField(default=0.0, verbose_name="掌握程度(0-1)")
    quiz_correct_rate = models.FloatField(default=0.0, verbose_name="答题正确率")
    quiz_attempts = models.IntegerField(default=0, verbose_name="答题次数")
    last_assessment_time = models.DateTimeField(null=True, blank=True, verbose_name="最后评估时间")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户知识点掌握度"
        verbose_name_plural = "用户知识点掌握度"
        unique_together = ['user', 'knowledge_point']
        ordering = ['-mastery_level']
    
    def __str__(self):
        return f"{self.user.username} - {self.knowledge_point.name} ({self.mastery_level:.2f})"


class RecommendationLog(models.Model):
    """推荐记录日志表"""
    ALGORITHM_CHOICES = [
        ('content_based', '基于内容'),
        ('collaborative', '协同过滤'),
        ('knowledge_graph', '知识图谱'),
        ('hybrid', '混合推荐'),
        ('popular', '热门推荐'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='recommendation_logs', verbose_name="用户")
    recommended_project = models.ForeignKey(DanceProject, on_delete=models.CASCADE, related_name='recommendation_logs', verbose_name="推荐项目")
    recommendation_algorithm = models.CharField(max_length=50, choices=ALGORITHM_CHOICES, verbose_name="推荐算法")
    recommendation_score = models.FloatField(verbose_name="推荐得分")
    recommendation_reason = models.TextField(blank=True, verbose_name="推荐理由")
    
    # 用户反馈
    is_clicked = models.BooleanField(default=False, verbose_name="是否点击")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成学习")
    feedback_rating = models.IntegerField(null=True, blank=True, choices=[(i, f'{i}星') for i in range(1, 6)], verbose_name="用户评分(1-5)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="推荐时间")
    
    class Meta:
        verbose_name = "推荐记录"
        verbose_name_plural = "推荐记录"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.recommended_project.name} ({self.recommendation_algorithm})"
