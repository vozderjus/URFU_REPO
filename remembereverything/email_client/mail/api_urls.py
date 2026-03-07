from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'emails', api_views.EmailViewSet, basename='email-api')

urlpatterns = [
    path('', include(router.urls)),
]