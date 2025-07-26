from django.db import models
from users.models import User

class Transcript(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='transcripts/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    parsed_data = models.JSONField(null=True, blank=True)  # OCR 후 파싱된 데이터
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.student_id} - {self.status}"
