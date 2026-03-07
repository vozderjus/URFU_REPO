# mail/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # HTML интерфейс
    path('', views.inbox, name='inbox'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inbox/', views.inbox, name='inbox'),
    path('outbox/', views.outbox, name='outbox'),
    path('archive/', views.archive, name='archive'),
    path('trash/', views.trash, name='trash'),
    path('drafts/', views.drafts, name='drafts'),
    path('compose/', views.compose, name='compose'),
    path('email/<int:email_id>/', views.email_detail, name='email_detail'),
    
    # API для AJAX (эти маршруты будут обрабатывать запросы из HTML)
    path('api/email/<int:email_id>/move/', views.api_move_email, name='api_move_email'),
    path('api/email/<int:email_id>/delete/', views.api_delete_email, name='api_delete_email'),
    path('api/email/<int:email_id>/read/', views.api_mark_read, name='api_mark_read'),
]