from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Email, EmailStatus

class EmailStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailStatus
        fields = ['folder', 'is_read', 'received_at']

class EmailSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipients_emails = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Email
        fields = ['id', 'subject', 'body', 'sender_username', 'recipients_emails', 
                 'created_at', 'sent_at', 'is_draft', 'status']

    def get_recipients_emails(self, obj):
        return [user.email for user in obj.recipients.all()]

    def get_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                status = obj.statuses.get(user=request.user)
                return EmailStatusSerializer(status).data
            except EmailStatus.DoesNotExist:
                return None
        return None

class EmailCreateSerializer(serializers.ModelSerializer):
    recipients = serializers.ListField(child=serializers.EmailField(), write_only=True)

    class Meta:
        model = Email
        fields = ['subject', 'body', 'recipients', 'is_draft']

    def validate_recipients(self, value):
        users = User.objects.filter(email__in=value)
        if len(users) != len(value):
            raise serializers.ValidationError("Some recipients not found")
        return users

    def create(self, validated_data):
        recipients = validated_data.pop('recipients')
        request = self.context.get('request')

        email = Email.objects.create(sender=request.user, **validated_data)
        email.recipients.set(recipients)

        if not validated_data.get('is_draft'):
            email.sent_at = timezone.now()
            email.save()

            EmailStatus.objects.create(email=email, user=request.user, folder=Email.Folder.OUTBOX, is_read=True)

            for recipient in recipients:
                EmailStatus.objects.create(email=email, user=recipient, folder=Email.Folder.INBOX)

        return email