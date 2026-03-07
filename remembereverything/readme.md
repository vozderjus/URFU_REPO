# Быстрый запуск


## 1. Клонировать и перейти в папку
```bash
cd email_client
```

## 2. Создать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# venv\Scripts\activate   # для Windows
```

## 3. Установить зависимости
```bash
pip install django djangorestframework
```

## 4. Применить миграции
```bash
python manage.py migrate
```

## 5. Создать тестовых пользователей
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.create_user('user1', 'user1@example.com', 'password123')
User.objects.create_user('user2', 'user2@example.com', 'password123')
print('Готово: user1/password123, user2/password123')"
```

## 6. Запустить сервер
```bash
python manage.py runserver
```
