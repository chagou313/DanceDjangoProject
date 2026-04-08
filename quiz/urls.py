from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('game/<int:level_id>/', views.quiz_game, name='quiz_game'),
    path('api/start/<int:level_id>/', views.start_quiz, name='start_quiz'),
    path('api/submit/', views.submit_answer, name='submit_answer'),
    path('result/<int:record_id>/', views.quiz_result, name='quiz_result'),
    path('progress/', views.user_progress, name='user_progress'),
    path('wrong/', views.wrong_questions, name='wrong_questions'),
    path('wrong/retry/', views.retry_wrong_questions, name='retry_wrong_questions'),
]
