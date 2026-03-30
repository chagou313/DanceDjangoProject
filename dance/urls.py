from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # 新闻资讯
    path('news/', views.news_list, name='news_list'),
    
    # 新增模块入口
    path('origin/', views.dance_origin_list, name='dance_origin_list'),
    path('origin/projects/', views.dance_project_list, name='dance_project_list'),
    path('origin/<str:project_code>/', views.project_detail, name='project_detail'),
    path('knowledge/', views.knowledge_map, name='knowledge_map'),
    path('quiz/', views.quiz_list, name='quiz_list'),
    
    # 个人主页相关
    path('profile/', views.profile, name='profile'),
    path('profile/liked/', views.user_liked_posts, name='user_liked_posts'),
    path('profile/collected/', views.user_collected_posts, name='user_collected_posts'),
    path('profile/comments/', views.user_comments, name='user_comments'),
    path('profile/posts/', views.user_posts, name='user_posts'),
    path('profile/edit-avatar/', views.edit_avatar, name='edit_avatar'),
]
