"""
URL patterns for admin panel.
"""

from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Reports management
    path('reports/', views.reports_list, name='reports_list'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/<int:pk>/approve/', views.approve_report, name='approve_report'),
    path('reports/<int:pk>/dismiss/', views.dismiss_report, name='dismiss_report'),

    # Report submission (for users)
    path('report/submit/', views.submit_report, name='submit_report'),
]
