from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_view, name='upload'),
    path('image/<str:signed_data>/', views.serve_signed_image, name='signed_image'),
    path('', views.serve_signed_image, name='signed_image'),
]