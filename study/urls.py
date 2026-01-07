"""
URL patterns for study app.
"""

from django.urls import path
from . import views

app_name = 'study'

urlpatterns = [
    path('generate/<str:set_type>/', views.generate_view, name='generate'),
    path('history/', views.history_view, name='history'),
    path('<int:pk>/', views.study_set_detail, name='detail'),
    path('<int:pk>/delete/', views.delete_study_set, name='delete'),
    path('<int:pk>/json/', views.study_set_json, name='json'),
]
