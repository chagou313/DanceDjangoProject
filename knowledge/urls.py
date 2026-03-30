from django.urls import path
from . import views

urlpatterns = [
    path('', views.knowledge_map, name='knowledge_map'),
]
