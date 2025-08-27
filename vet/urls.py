from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('chat/', views.chat_view, name='chat'),
    path('request-service/', views.request_veterinary_service, name='request_service'),
    path('request-success/', views.service_success, name='service_success'),
    path('veterinarios/cercanos/', views.veterinarios_cercanos, name='veterinarios_cercanos'),
]

