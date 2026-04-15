from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.knowledge_map, name='knowledge_map'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('api/chat/', views.chat_with_ai, name='chat_with_ai'),
    path('api/project/<int:project_id>/', views.get_project_knowledge_graph, name='get_knowledge_graph'),
    path('api/learning-path/<int:project_id>/', views.generate_learning_path, name='generate_learning_path'),
    path('api/update-progress/<int:move_id>/', views.update_learning_progress, name='update_progress'),
    
    # 个性化推荐相关路由
    path('recommendations/', views.personalized_recommendations, name='recommendations'),
    path('api/recommendations/', views.get_recommendations_api, name='get_recommendations_api'),
    path('learning-path/<int:project_id>/', views.learning_path_view, name='learning_path'),
    
    # 学习进度
    path('my-progress/', views.my_progress, name='my_progress'),
]
