from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class UploadedImage(models.Model):
    original_name = models.CharField(max_length=255)
    original_size = models.PositiveIntegerField()
    compressed_size = models.PositiveIntegerField()
    original_url = models.URLField(max_length=500)
    compressed_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name

    def delete(self, *args, **kwargs):
        # Hapus file fisik saat objek dihapus
        fs = FileSystemStorage()
        if self.original_url:
            original_path = os.path.join(settings.MEDIA_ROOT, self.original_url.split('/media/')[-1])
            if os.path.exists(original_path):
                os.remove(original_path)
        if self.compressed_url:
            compressed_path = os.path.join(settings.MEDIA_ROOT, self.compressed_url.split('/media/')[-1])
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
        super().delete(*args, **kwargs)