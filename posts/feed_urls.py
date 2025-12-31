"""
URL patterns for feed pages.
"""

from django.urls import path
from . import feed_views

app_name = 'feed'

urlpatterns = [
    path('recent/', feed_views.recent_feed, name='recent'),
    path('following/', feed_views.following_feed, name='following'),
]
