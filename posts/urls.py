from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('explore/', views.explore, name='explore'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/repost/', views.repost_post, name='repost_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]
