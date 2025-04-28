"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app_mentorlink import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('profil/', views.profil, name='profil'),
    path('depose_annonce/', views.depose_annonce, name='depose_annonce'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.loginperso, name='login'),
    path('admin/', admin.site.urls),
    path('depose_annonce/', views.depose_annonce, name='depose_annonce'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('liste_annonces/', views.liste_annonces, name='liste_annonces'),
    path('mes-annonces/', views.annonces_utilisateur, name='mes_annonces'),
    path('utilisateur/<int:user_id>/annonces/', views.annonces_utilisateur, name='annonces_utilisateur'),
    path('annonce/<int:annonce_id>/', views.annonce_detail, name='annonce_detail'),
    path('annonce/<int:annonce_id>/modifier/', views.modifier_annonce, name='modifier_annonce'),
    path('annonce/<int:annonce_id>/supprimer/', views.supprimer_annonce, name='supprimer_annonce'),
    path('messages/', views.conversation_list, name='conversation_list'),
    path('messages/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('messages/start/<int:user_id>/', views.start_conversation, name='start_conversation'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
