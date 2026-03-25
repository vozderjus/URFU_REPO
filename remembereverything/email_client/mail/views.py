from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.db.models import Q
from django.utils import timezone
import json

from .models import Email, EmailStatus
from django.contrib.auth.models import User


# Вход в систему

def login_view(request):
    """Страница входа"""
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
                next_url = request.GET.get('next', 'inbox')
                return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()
    
    return render(request, 'mail/login.html', {'form': form})

def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('login')


# Основные страницы
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
    email = get_object_or_404(
        Email.objects.filter(
            Q(sender=request.user) | Q(recipients=request.user)
        ).select_related('sender').prefetch_related('recipients'),
        id=email_id
    )
    
    # Отметка о прочтении
    if request.user in email.recipients.all():
        EmailStatus.objects.filter(email=email, user=request.user).update(is_read=True)
    
    # Получаем статус
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
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        recipients_str = request.POST.get('recipients', '').strip()
        is_draft = request.POST.get('is_draft') == 'on'
        
        # Ошибки
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
        
        # Разбираем получателей
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
        
        # Находим пользователей
        recipients = User.objects.filter(email__in=recipient_emails)
        
        if len(recipients) != len(recipient_emails):
            found_emails = set(recipients.values_list('email', flat=True))
            not_found = set(recipient_emails) - found_emails
            messages.error(request, f'Пользователи не найдены: {", ".join(not_found)}')
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


@login_required
@require_POST
def api_move_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        
        # Проверяем права доступа
        if email.sender != request.user and request.user not in email.recipients.all():
            return JsonResponse({'error': 'Access denied'}, status=403)
        
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
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def api_delete_email(request, email_id):
    """Удаление письма (AJAX)"""
    try:
        email = Email.objects.get(id=email_id)

        # Проверяем права доступа
        if email.sender != request.user and request.user not in email.recipients.all():
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        try:
            status = email.statuses.get(user=request.user)
            if status.folder == Email.Folder.TRASH:
                # Полное удаление из корзины
                status.delete()
                if email.statuses.count() == 0:
                    email.delete()
            else:
                # Перемещаем в корзину
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
def api_mark_read(request, email_id):
    """Отметка о прочтении (AJAX)"""
    try:
        email = Email.objects.get(id=email_id)
        
        # Проверяем права доступа
        if request.user not in email.recipients.all():
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        updated = EmailStatus.objects.filter(
            email_id=email_id, 
            user=request.user
        ).update(is_read=True)
        
        if updated:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'error': 'Status not found'}, status=404)
            
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def api_restore_email(request, email_id):
    """Восстановление письма из корзины (AJAX)"""
    try:
        email = Email.objects.get(id=email_id)
        
        email_status = email.statuses.get(user=request.user)
        
        if email_status.folder == Email.Folder.TRASH:
            email_status.folder = Email.Folder.INBOX
            email_status.save()
            return JsonResponse({'status': 'success', 'folder': 'INBOX'})
        else:
            return JsonResponse({'error': 'Email not in trash'}, status=400)
            
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Email not found'}, status=404)
    except EmailStatus.DoesNotExist:
        return JsonResponse({'error': 'Status not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def api_send_draft(request, draft_id):
    """Отправка черновика (AJAX)"""
    try:
        draft = Email.objects.get(
            id=draft_id,
            sender=request.user,
            is_draft=True
        )
        
        # Отправляем черновик
        draft.is_draft = False
        draft.sent_at = timezone.now()
        draft.save()
        
        # Обновляем статус отправителя
        sender_status, _ = EmailStatus.objects.get_or_create(
            email=draft,
            user=request.user,
            defaults={'folder': Email.Folder.OUTBOX}
        )
        sender_status.folder = Email.Folder.OUTBOX
        sender_status.is_read = True
        sender_status.save()
        
        # Создаем статусы для получателей
        for recipient in draft.recipients.all():
            status, created = EmailStatus.objects.get_or_create(
                email=draft,
                user=recipient,
                defaults={
                    'folder': Email.Folder.INBOX,
                    'is_read': False
                }
            )
            if not created:
                status.folder = Email.Folder.INBOX
                status.is_read = False
                status.received_at = timezone.now()
                status.save()
        
        return JsonResponse({'status': 'success'})
        
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Draft not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_search_users(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).filter(is_active=True).exclude(id=request.user.id)[:10]
    
    users_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name() or user.username
        }
        for user in users
    ]
    
    return JsonResponse({'users': users_data})


@login_required
def api_stats(request):
    stats = {
        'inbox_count': EmailStatus.objects.filter(
            user=request.user,
            folder=Email.Folder.INBOX
        ).count(),
        'unread_count': EmailStatus.objects.filter(
            user=request.user,
            folder=Email.Folder.INBOX,
            is_read=False
        ).count(),
        'outbox_count': EmailStatus.objects.filter(
            user=request.user,
            folder=Email.Folder.OUTBOX
        ).count(),
        'archive_count': EmailStatus.objects.filter(
            user=request.user,
            folder=Email.Folder.ARCHIVE
        ).count(),
        'trash_count': EmailStatus.objects.filter(
            user=request.user,
            folder=Email.Folder.TRASH
        ).count(),
        'drafts_count': Email.objects.filter(
            sender=request.user,
            is_draft=True
        ).count()
    }
    
    return JsonResponse(stats)