from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.knowledge_map, name='knowledge_map'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('api/chat/', views.chat_with_ai, name='chat_with_ai'),
    path('api/project/<int:project_id>/', views.get_project_knowledge_graph, name='get_knowledge_graph'),
    path('api/learning-path/<int:project_id>/', views.generate_learning_path, name='generate_learning_path'),
]
