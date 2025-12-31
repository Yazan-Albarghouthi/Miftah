"""
URL patterns for accounts app.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('following/', views.following_list, name='following_list'),
    path('u/<str:username>/', views.profile_view, name='profile'),
    path('u/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('u/<str:username>/toggle-follow/', views.toggle_follow, name='toggle_follow'),
]
