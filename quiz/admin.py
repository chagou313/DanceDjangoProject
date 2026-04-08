from django.contrib import admin
from .models import Question, Level, LevelQuestion, UserQuizRecord, UserAnswerDetail

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_short', 'question_type', 'difficulty', 'knowledge_point', 'dance_project']
    list_filter = ['question_type', 'difficulty', 'knowledge_point__category']
    search_fields = ['content', 'knowledge_point__name', 'dance_project__name']
    filter_horizontal = ['extension_knowledge_points']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = '题目内容'

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'difficulty', 'question_count', 'required_score', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['name', 'description']

@admin.register(LevelQuestion)
class LevelQuestionAdmin(admin.ModelAdmin):
    list_display = ['level', 'get_question_short', 'score', 'order_index']
    list_filter = ['level']
    
    def get_question_short(self, obj):
        return obj.question.content[:30] + '...' if len(obj.question.content) > 30 else obj.question.content
    get_question_short.short_description = '题目'

@admin.register(UserQuizRecord)
class UserQuizRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'score', 'is_passed', 'correct_answers', 'wrong_answers', 'start_time']
    list_filter = ['is_passed', 'level', 'start_time']
    search_fields = ['user__username', 'level__name']

@admin.register(UserAnswerDetail)
class UserAnswerDetailAdmin(admin.ModelAdmin):
    list_display = ['quiz_record', 'question_short', 'user_answer', 'is_correct', 'time_spent']
    list_filter = ['is_correct', 'quiz_record__level']
    
    def question_short(self, obj):
        return obj.question.content[:30] + '...' if len(obj.question.content) > 30 else obj.question.content
    question_short.short_description = '题目'
