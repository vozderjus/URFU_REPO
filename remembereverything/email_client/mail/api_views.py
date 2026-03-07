from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .models import Email, EmailStatus
from .serializers import EmailSerializer, EmailCreateSerializer

class EmailViewSet(viewsets.ModelViewSet):
    """API ViewSet для работы с письмами"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmailCreateSerializer
        return EmailSerializer
    
    def get_queryset(self):
        user = self.request.user
        folder = self.request.query_params.get('folder')
        
        queryset = Email.objects.filter(
            Q(sender=user) | Q(recipients=user)
        ).select_related('sender').prefetch_related('recipients', 'statuses').distinct()
        
        if folder:
            queryset = queryset.filter(statuses__user=user, statuses__folder=folder)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Отметка о прочтении
        if request.user in instance.recipients.all():
            EmailStatus.objects.filter(email=instance, user=request.user).update(is_read=True)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        email = self.get_object()
        folder = request.data.get('folder')
        
        if folder not in dict(Email.Folder.choices):
            return Response({'error': 'Invalid folder'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            email_status = email.statuses.get(user=request.user)
            email_status.folder = folder
            email_status.save()
            return Response({'status': 'moved', 'folder': folder})
        except EmailStatus.DoesNotExist:
            return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        return self.move(request, pk, folder=Email.Folder.ARCHIVE)
    
    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        return self.move(request, pk, folder=Email.Folder.TRASH)
    
    def perform_destroy(self, instance):
        try:
            status = instance.statuses.get(user=self.request.user)
            if status.folder == Email.Folder.TRASH:
                status.delete()
                if instance.statuses.count() == 0:
                    instance.delete()
            else:
                status.folder = Email.Folder.TRASH
                status.save()
        except EmailStatus.DoesNotExist:
            instance.delete()
    
    @action(detail=False, methods=['get'])
    def inbox(self, request):
        emails = Email.objects.filter(
            recipients=request.user,
            statuses__user=request.user,
            statuses__folder=Email.Folder.INBOX
        ).select_related('sender').order_by('-statuses__received_at')
        
        serializer = self.get_serializer(emails, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def outbox(self, request):
        emails = Email.objects.filter(
            sender=request.user,
            statuses__user=request.user,
            statuses__folder=Email.Folder.OUTBOX
        ).select_related('sender').order_by('-sent_at')
        
        serializer = self.get_serializer(emails, many=True)
        return Response(serializer.data)