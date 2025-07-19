from django.db import models
from django.urls import reverse
import uuid


class Poll(models.Model):
    """Model untuk poll/survei"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Judul Poll")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Poll"
        verbose_name_plural = "Polls"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('polls:detail', kwargs={'poll_id': self.id})
    
    def total_votes(self):
        """Menghitung total votes untuk poll ini"""
        return Vote.objects.filter(option__poll=self).count()


class Option(models.Model):
    """Model untuk opsi dalam poll"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200, verbose_name="Teks Opsi")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Opsi"
        verbose_name_plural = "Opsi"
        # Composite index untuk optimasi query
        indexes = [
            models.Index(fields=['poll', 'id'], name='poll_option_idx'),
        ]
    
    def __str__(self):
        return f"{self.poll.title} - {self.text}"
    
    def vote_count(self):
        """Menghitung jumlah vote untuk opsi ini"""
        return self.votes.count()
    
    def vote_percentage(self):
        """Menghitung persentase vote untuk opsi ini"""
        total = self.poll.total_votes()
        if total == 0:
            return 0
        return round((self.vote_count() / total) * 100, 1)


class Vote(models.Model):
    """Model untuk vote/suara"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='votes')
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        # Index untuk optimasi query
        indexes = [
            models.Index(fields=['option', 'created_at'], name='option_created_idx'),
        ]
    
    def __str__(self):
        return f"Vote untuk {self.option.text} dari {self.ip_address}"
    
    @property
    def poll(self):
        """Shortcut untuk mengakses poll dari vote"""
        return self.option.poll

