import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_client.settings')
django.setup()

from django.contrib.auth.models import User
from mail.models import Email, EmailStatus

def create_test_users():
    """Создание тестовых пользователей"""
    print("Создание тестовых пользователей...")
    
    # Удаляем старых пользователей
    User.objects.filter(username='user1').delete()
    User.objects.filter(username='user2').delete()
    
    # Создаем новых
    user1 = User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='password123',
        first_name='Иван',
        last_name='Петров'
    )
    
    user2 = User.objects.create_user(
        username='user2',
        email='user2@example.com',
        password='password123',
        first_name='Мария',
        last_name='Сидорова'
    )
    
    print(f"✓ Создан пользователь: {user1.username} ({user1.email})")
    print(f"✓ Создан пользователь: {user2.username} ({user2.email})")
    
    return user1, user2

def create_test_emails(user1, user2):
    """Создание тестовых писем"""
    print("\nСоздание тестовых писем...")
    
    # Письмо от user1 к user2
    email1 = Email.objects.create(
        sender=user1,
        subject="Привет от user1",
        body="Привет! Это тестовое письмо от user1 к user2.",
        sent_at=timezone.now()
    )
    email1.recipients.set([user2])
    
    EmailStatus.objects.create(
        email=email1,
        user=user1,
        folder=Email.Folder.OUTBOX,
        is_read=True
    )
    
    EmailStatus.objects.create(
        email=email1,
        user=user2,
        folder=Email.Folder.INBOX,
        is_read=False
    )
    print(f"✓ Создано письмо: '{email1.subject}' от user1 к user2")
    
    # Письмо от user2 к user1
    email2 = Email.objects.create(
        sender=user2,
        subject="Ответ от user2",
        body="Привет! Получил твое письмо. Как дела?",
        sent_at=timezone.now()
    )
    email2.recipients.set([user1])
    
    EmailStatus.objects.create(
        email=email2,
        user=user2,
        folder=Email.Folder.OUTBOX,
        is_read=True
    )
    
    EmailStatus.objects.create(
        email=email2,
        user=user1,
        folder=Email.Folder.INBOX,
        is_read=False
    )
    print(f"✓ Создано письмо: '{email2.subject}' от user2 к user1")
    
    # Черновик от user1
    draft = Email.objects.create(
        sender=user1,
        subject="Черновик письма",
        body="Это черновик письма, которое я допишу позже...",
        is_draft=True
    )
    draft.recipients.set([user2])
    
    EmailStatus.objects.create(
        email=draft,
        user=user1,
        folder=Email.Folder.DRAFTS,
        is_read=True
    )
    print(f"✓ Создан черновик: '{draft.subject}'")

def main():
    print("=" * 50)
    print("Создание тестовых данных для почтового клиента")
    print("=" * 50)
    
    user1, user2 = create_test_users()
    create_test_emails(user1, user2)
    
    print("\n" + "=" * 50)
    print("Готово! Тестовые данные созданы.")
    print("=" * 50)
    print("\nВход в систему:")
    print("  user1 / password123 (user1@example.com)")
    print("  user2 / password123 (user2@example.com)")
    print("\nТестовые письма созданы:")
    print("  - У user1: 1 письмо во входящих, 1 в отправленных, 1 черновик")
    print("  - У user2: 1 письмо во входящих, 1 в отправленных")

if __name__ == '__main__':
    main()