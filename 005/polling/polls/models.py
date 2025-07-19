# polls/models.py
from django.db import models
import uuid

class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

class Vote(models.Model):
    option = models.ForeignKey(Option, related_name='votes', on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, related_name='votes', on_delete=models.CASCADE)  # Field langsung
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['poll', 'option']),  # Composite Index yang benar
        ]
        
    def save(self, *args, **kwargs):
        # Pastikan poll diisi dari option jika belum ada
        if not self.poll_id and self.option_id:
            self.poll = self.option.poll
        super().save(*args, **kwargs)