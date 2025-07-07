"""
URL configuration for main project.
"""
from django.contrib import admin
from django.urls import path
from app_mentorlink import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from app_mentorlink.views import custom_404, custom_500, custom_403, custom_400

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('profil/', views.profil, name='profil'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.loginperso, name='login'),
    path('admin/', admin.site.urls),
    path('depose_annonce/', views.depose_annonce, name='depose_annonce'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('mes_annonces/', views.annonces_utilisateur, name='mes_annonces'),
    path('utilisateur/<int:user_id>/annonces/', views.annonces_utilisateur, name='annonces_utilisateur'),
    path('annonce/<int:annonce_id>/', views.annonce_detail, name='annonce_detail'),
    path('annonce/<int:annonce_id>/modifier/', views.modifier_annonce, name='modifier_annonce'),
    path('annonce/<int:annonce_id>/supprimer/', views.supprimer_annonce, name='supprimer_annonce'),
    path('annonce/<int:annonce_id>/start-chat/', views.start_private_chat, name='start_private_chat'),
    path('api/unread-count/', views.get_unread_count, name='unread_count'),
    # Ajoutez SEULEMENT cette ligne pour les messages :
    path('messages/', views.all_messages, name='all_messages'),
    
    # Gardez votre room original à la fin :
    path('<slug:slug>/', views.room, name='room'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = custom_404
handler500 = custom_500
handler403 = custom_403
handler400 = custom_400