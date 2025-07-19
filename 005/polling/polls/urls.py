# polls/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_poll, name='create_poll'),
    path('poll/<uuid:poll_id>/', views.poll_detail, name='poll_detail'),
    path('vote/<uuid:option_id>/', views.vote, name='vote'),
]