# mail/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required  # ЭТОТ ИМПОРТ ДОЛЖЕН БЫТЬ ПЕРВЫМ!
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
import json

from .models import Email, EmailStatus
from django.contrib.auth.models import User

# HTML Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('inbox')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inbox')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()
    
    return render(request, 'mail/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def inbox(request):
    """Входящие письма"""
    emails = Email.objects.filter(
        recipients=request.user,
        statuses__user=request.user,
        statuses__folder=Email.Folder.INBOX
    ).select_related('sender').order_by('-statuses__received_at')
    
    unread_count = emails.filter(statuses__is_read=False).count()
    
    return render(request, 'mail/inbox.html', {
        'emails': emails,
        'unread_count': unread_count,
        'folder': 'inbox'
    })

@login_required
def outbox(request):
    """Исходящие письма"""
    emails = Email.objects.filter(
        sender=request.user,
        statuses__user=request.user,
        statuses__folder=Email.Folder.OUTBOX
    ).select_related('sender').order_by('-sent_at')
    
    return render(request, 'mail/outbox.html', {
        'emails': emails,
        'folder': 'outbox'
    })

@login_required
def archive(request):
    """Архив"""
    emails = Email.objects.filter(
        Q(sender=request.user) | Q(recipients=request.user),
        statuses__user=request.user,
        statuses__folder=Email.Folder.ARCHIVE
    ).select_related('sender').order_by('-statuses__received_at')
    
    return render(request, 'mail/folder.html', {
        'emails': emails,
        'folder': 'archive',
        'folder_name': 'Архив'
    })

@login_required
def trash(request):
    """Корзина"""
    emails = Email.objects.filter(
        Q(sender=request.user) | Q(recipients=request.user),
        statuses__user=request.user,
        statuses__folder=Email.Folder.TRASH
    ).select_related('sender').order_by('-statuses__received_at')
    
    return render(request, 'mail/folder.html', {
        'emails': emails,
        'folder': 'trash',
        'folder_name': 'Корзина'
    })

@login_required
def drafts(request):
    """Черновики"""
    emails = Email.objects.filter(
        sender=request.user,
        is_draft=True,
        statuses__user=request.user,
        statuses__folder=Email.Folder.DRAFTS
    ).select_related('sender').order_by('-created_at')
    
    return render(request, 'mail/folder.html', {
        'emails': emails,
        'folder': 'drafts',
        'folder_name': 'Черновики'
    })

@login_required
def email_detail(request, email_id):
    """Просмотр письма"""
    email = get_object_or_404(
        Email.objects.filter(
            Q(sender=request.user) | Q(recipients=request.user)
        ).select_related('sender').prefetch_related('recipients'),
        id=email_id
    )
    
    # Отметка о прочтении
    if request.user in email.recipients.all():
        EmailStatus.objects.filter(email=email, user=request.user).update(is_read=True)
    
    # Получаем статус для текущего пользователя
    try:
        status = email.statuses.get(user=request.user)
    except EmailStatus.DoesNotExist:
        status = None
    
    return render(request, 'mail/email_detail.html', {
        'email': email,
        'status': status,
        'recipients_list': ', '.join([u.email for u in email.recipients.all()])
    })

@login_required
def compose(request):
    """Написание письма"""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        recipients_str = request.POST.get('recipients', '').strip()
        is_draft = request.POST.get('is_draft') == 'on'
        
        # Валидация полей
        if not subject:
            messages.error(request, 'Укажите тему письма')
            return render(request, 'mail/compose.html', {
                'body': body,
                'recipients_str': recipients_str
            })
        
        if not body:
            messages.error(request, 'Напишите текст письма')
            return render(request, 'mail/compose.html', {
                'subject': subject,
                'recipients_str': recipients_str
            })
        
        # Разбираем получателей (через запятую или пробел)
        recipient_emails = []
        for part in recipients_str.replace(',', ' ').split():
            email = part.strip()
            if email:
                recipient_emails.append(email)
        
        if not recipient_emails:
            messages.error(request, 'Укажите хотя бы одного получателя')
            return render(request, 'mail/compose.html', {
                'subject': subject,
                'body': body
            })
        
        # Находим пользователей по email
        recipients = User.objects.filter(email__in=recipient_emails)
        
        if len(recipients) != len(recipient_emails):
            found_emails = set(recipients.values_list('email', flat=True))
            not_found = set(recipient_emails) - found_emails
            messages.error(request, f'Пользователи с email {", ".join(not_found)} не найдены')
            return render(request, 'mail/compose.html', {
                'subject': subject,
                'body': body,
                'recipients_str': recipients_str
            })
        
        try:
            # Создаем письмо
            email = Email.objects.create(
                sender=request.user,
                subject=subject,
                body=body,
                is_draft=is_draft
            )
            email.recipients.set(recipients)
            
            if not is_draft:
                email.sent_at = timezone.now()
                email.save()
                
                # Статус для отправителя
                EmailStatus.objects.create(
                    email=email,
                    user=request.user,
                    folder=Email.Folder.OUTBOX,
                    is_read=True
                )
                
                # Статусы для получателей
                for recipient in recipients:
                    EmailStatus.objects.create(
                        email=email,
                        user=recipient,
                        folder=Email.Folder.INBOX
                    )
                
                messages.success(request, 'Письмо успешно отправлено!')
                return redirect('outbox')
            else:
                # Статус для черновика
                EmailStatus.objects.create(
                    email=email,
                    user=request.user,
                    folder=Email.Folder.DRAFTS,
                    is_read=True
                )
                messages.success(request, 'Черновик сохранен')
                return redirect('drafts')
                
        except Exception as e:
            messages.error(request, f'Ошибка при отправке: {str(e)}')
            return render(request, 'mail/compose.html', {
                'subject': subject,
                'body': body,
                'recipients_str': recipients_str
            })
    
    return render(request, 'mail/compose.html')

# API Views для AJAX запросов
@login_required
@require_POST
@csrf_exempt
def api_move_email(request, email_id):
    """API для перемещения письма"""
    try:
        email = Email.objects.get(id=email_id)
        data = json.loads(request.body)
        folder = data.get('folder')
        
        if folder not in dict(Email.Folder.choices):
            return JsonResponse({'error': 'Invalid folder'}, status=400)
        
        email_status = email.statuses.get(user=request.user)
        email_status.folder = folder
        email_status.save()
        
        return JsonResponse({'status': 'success', 'folder': folder})
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=404)
    except EmailStatus.DoesNotExist:
        return JsonResponse({'error': 'Status not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
@csrf_exempt
def api_delete_email(request, email_id):
    """API для удаления письма"""
    try:
        email = Email.objects.get(id=email_id)
        
        try:
            status = email.statuses.get(user=request.user)
            if status.folder == Email.Folder.TRASH:
                status.delete()
                if email.statuses.count() == 0:
                    email.delete()
            else:
                status.folder = Email.Folder.TRASH
                status.save()
        except EmailStatus.DoesNotExist:
            email.delete()
        
        return JsonResponse({'status': 'success'})
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
@csrf_exempt
def api_mark_read(request, email_id):
    """API для отметки о прочтении"""
    try:
        EmailStatus.objects.filter(email_id=email_id, user=request.user).update(is_read=True)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)