"""
URL patterns for posts app.
"""

from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('new/', views.create_post, name='create'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/delete/', views.delete_post, name='delete'),
    path('<int:pk>/react/', views.toggle_reaction, name='react'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('search/', views.search_posts, name='search'),
]
