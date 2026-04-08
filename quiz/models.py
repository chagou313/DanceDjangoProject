from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    """题库表"""
    QUESTION_TYPES = [
        ('choice', '选择题'),
        ('judge', '判断题'),
        ('multi', '多选题'),
    ]
    
    DIFFICULTY_CHOICES = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
    ]
    
    # 关联知识点和舞蹈项目
    knowledge_point = models.ForeignKey('knowledge.KnowledgePoint', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联知识点")
    dance_project = models.ForeignKey('origin.DanceProject', on_delete=models.SET_NULL, null=True, blank=True, related_name='questions', verbose_name="关联舞蹈项目")
    
    # 题目信息
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name="题型")
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, verbose_name="难度")
    content = models.TextField(verbose_name="题目内容")
    options = models.JSONField(blank=True, null=True, verbose_name="选项（JSON 格式）")
    correct_answer = models.CharField(max_length=500, verbose_name="正确答案")
    explanation = models.TextField(verbose_name="答案解析")
    
    # 延伸知识点（答对后推荐）
    extension_knowledge_points = models.ManyToManyField('knowledge.KnowledgePoint', blank=True, related_name='extension_questions', verbose_name="延伸知识点")
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "题目"
        verbose_name_plural = "题目"
    
    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.get_question_type_display()} - {self.content[:50]}"

class Level(models.Model):
    """关卡表"""
    DIFFICULTY_CHOICES = [
        (1, '入门级'),
        (2, '基础级'),
        (3, '进阶级'),
        (4, '高手级'),
        (5, '大师级'),
    ]
    
    CATEGORY_CHOICES = [
        ('origin', '起源知识'),
        ('inheritor', '传承人知识'),
        ('technique', '技法知识'),
        ('culture', '文化背景'),
        ('mixed', '综合知识'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="关卡名称")
    description = models.TextField(verbose_name="关卡描述")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='mixed', verbose_name="知识类型")
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, verbose_name="难度等级")
    required_score = models.IntegerField(default=60, verbose_name="通关所需分数")
    time_limit = models.IntegerField(default=300, verbose_name="限时（秒）")
    question_count = models.IntegerField(default=10, verbose_name="题目数量")
    order_index = models.IntegerField(default=0, verbose_name="排序索引")
    is_active = models.BooleanField(default=True, verbose_name="是否开启")
    icon = models.CharField(max_length=50, default='fa-star', verbose_name="图标")
    
    class Meta:
        verbose_name = "关卡"
        verbose_name_plural = "关卡"
        ordering = ['order_index']
    
    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.name}"

class LevelQuestion(models.Model):
    """关卡题目关联表"""
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='level_questions', verbose_name="关卡")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="题目")
    score = models.IntegerField(default=10, verbose_name="本题分值")
    order_index = models.IntegerField(default=0, verbose_name="排序索引")
    
    class Meta:
        verbose_name = "关卡题目关联"
        verbose_name_plural = "关卡题目关联"
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.level.name} - {self.question.content[:30]}"

class UserQuizRecord(models.Model):
    """用户答题记录表"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name="关卡")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    score = models.IntegerField(default=0, verbose_name="得分")
    is_passed = models.BooleanField(default=False, verbose_name="是否通过")
    total_questions = models.IntegerField(default=0, verbose_name="总题数")
    correct_answers = models.IntegerField(default=0, verbose_name="答对题数")
    wrong_answers = models.IntegerField(default=0, verbose_name="答错题数")
    
    # 进度追踪
    current_question_index = models.IntegerField(default=0, verbose_name="当前题目索引")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    
    class Meta:
        verbose_name = "用户答题记录"
        verbose_name_plural = "用户答题记录"
        ordering = ['-start_time']
    
    def __str__(self):
        status = '✓' if self.is_passed else '✗'
        return f"{status} {self.user.username} - {self.level.name} - {self.score}分"

class UserAnswerDetail(models.Model):
    """用户答题详情表"""
    quiz_record = models.ForeignKey(UserQuizRecord, on_delete=models.CASCADE, related_name='answer_details', verbose_name="答题记录")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="题目")
    user_answer = models.CharField(max_length=500, verbose_name="用户答案")
    is_correct = models.BooleanField(default=False, verbose_name="是否正确")
    time_spent = models.IntegerField(default=0, verbose_name="耗时（秒）")
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="答题时间")
    
    class Meta:
        verbose_name = "用户答题详情"
        verbose_name_plural = "用户答题详情"
    
    def __str__(self):
        return f"{self.quiz_record.user.username} - {self.question.content[:30]}"
