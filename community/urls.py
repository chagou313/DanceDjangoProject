from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_posts, name='community_posts'),
    path('topics/', views.topics_list, name='topics_list'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('drafts/', views.my_drafts, name='my_drafts'),
    path('draft/<int:post_id>/delete/', views.delete_draft, name='delete_draft'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/collect/', views.toggle_collection, name='toggle_collection'),
    path('post/<int:post_id>/comment/', views.create_comment, name='create_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('report/', views.report_content, name='report_content'),
]
