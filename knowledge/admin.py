from django.contrib import admin
from .models import (
    DanceProject, ActionModule, SpecificMove, MoveAttribute,
    LearningResource, KnowledgePoint, AIQuestion,
    UserLearningProgress, UserKnowledgeMastery, RecommendationLog
)

@admin.register(DanceProject)
class DanceProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty_level', 'created_at']
    list_filter = ['category', 'difficulty_level']
    search_fields = ['name', 'description']

@admin.register(ActionModule)
class ActionModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'dance_project', 'order_index']
    list_filter = ['dance_project']
    search_fields = ['name', 'description']

@admin.register(SpecificMove)
class SpecificMoveAdmin(admin.ModelAdmin):
    list_display = ['name', 'action_module', 'difficulty', 'duration', 'order_index']
    list_filter = ['action_module__dance_project', 'difficulty']
    search_fields = ['name', 'description']

@admin.register(MoveAttribute)
class MoveAttributeAdmin(admin.ModelAdmin):
    list_display = ['specific_move', 'force_parts']
    search_fields = ['specific_move__name', 'key_points']

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'specific_move', 'resource_type', 'duration']
    list_filter = ['resource_type', 'specific_move__action_module__dance_project']
    search_fields = ['title', 'description']

@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'importance_level', 'specific_move']
    list_filter = ['category', 'importance_level']
    search_fields = ['name', 'description']

@admin.register(AIQuestion)
class AIQuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'question_short', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['user__username', 'question', 'answer']
    
    def question_short(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_short.short_description = '问题'

@admin.register(UserLearningProgress)
class UserLearningProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'specific_move', 'dance_project', 'status', 'proficiency_score', 'practice_count', 'updated_at']
    list_filter = ['status', 'dance_project', 'updated_at']
    search_fields = ['user__username', 'specific_move__name', 'dance_project__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserKnowledgeMastery)
class UserKnowledgeMasteryAdmin(admin.ModelAdmin):
    list_display = ['user', 'knowledge_point', 'mastery_level', 'quiz_correct_rate', 'quiz_attempts', 'updated_at']
    list_filter = ['knowledge_point__category', 'updated_at']
    search_fields = ['user__username', 'knowledge_point__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommended_project', 'recommendation_algorithm', 'recommendation_score', 'is_clicked', 'feedback_rating', 'created_at']
    list_filter = ['recommendation_algorithm', 'is_clicked', 'is_completed', 'feedback_rating', 'created_at']
    search_fields = ['user__username', 'recommended_project__name', 'recommendation_reason']
    readonly_fields = ['created_at']
