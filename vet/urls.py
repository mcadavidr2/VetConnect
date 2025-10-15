from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('chat/', views.chat_view, name='chat'),
    path('request-service/', views.request_veterinary_service, name='request_service'),
    path('request-success/', views.service_success, name='service_success'),
    path('veterinarios/cercanos/', views.veterinarios_cercanos, name='veterinarios_cercanos'),
    path('veterinarios/buscar/', views.veterinarios_por_especializacion, name='veterinarios_por_especializacion'),
    path('veterinarios/', views.veterinarios_list, name='veterinarios_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path("edit-profile/", views.edit_profile, name="profile"),
    path('toggle-favorite/<int:vet_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favoritos/', views.mis_favoritos, name='mis_favoritos'),
]

