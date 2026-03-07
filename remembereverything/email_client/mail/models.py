from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Email(models.Model):
    class Folder(models.TextChoices):
        INBOX = 'INBOX', 'Входящие'
        OUTBOX = 'OUTBOX', 'Исходящие'
        ARCHIVE = 'ARCHIVE', 'Архив'
        TRASH = 'TRASH', 'Корзина'
        DRAFTS = 'DRAFTS', 'Черновики'  # Добавляем черновики
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    recipients = models.ManyToManyField(User, related_name='received_emails')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)

class EmailStatus(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_statuses')
    folder = models.CharField(max_length=10, choices=Email.Folder.choices, default=Email.Folder.INBOX)
    is_read = models.BooleanField(default=False)
    received_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['email', 'user']
