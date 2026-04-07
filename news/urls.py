from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    path('<int:news_id>/like/', views.news_like, name='news_like'),
    path('<int:news_id>/collect/', views.news_collect, name='news_collect'),
]
