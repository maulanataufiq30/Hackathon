from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    # Halaman utama
    path('', views.index, name='index'),
    
    # Membuat poll baru
    path('create/', views.create_poll, name='create'),
    
    # Detail poll dan voting
    path('poll/<uuid:poll_id>/', views.poll_detail, name='detail'),
    
    # API endpoints
    path('api/vote/<uuid:poll_id>/', views.vote, name='vote_api'),
    path('api/results/<uuid:poll_id>/', views.poll_results_api, name='results_api'),
    
    # Server-Sent Events untuk real-time updates
    path('stream/<uuid:poll_id>/', views.poll_stream, name='stream'),
]

