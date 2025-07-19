# imgs/apps.py
from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'imgs'
    verbose_name = 'Aplikasi gambar'