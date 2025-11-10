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
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.edit_profile, name='profile'),
    path("edit-profile/", views.edit_profile, name="profile"),
    path('toggle-favorite/<int:vet_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('logout-page/', views.logout_page, name='logout_page'),
    path('vet/profile/', views.vet_profile, name='vet_profile'),
    path('vet/<int:vet_id>/', views.vet_detail, name='vet_detail'),
]

