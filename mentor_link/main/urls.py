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


urlpatterns = [
    path('', views.home, name='home'),
    path('messages/', views.messages, name='messages'),
    path('search/', views.search, name='search'),
    path('profil/', views.profil, name='profil'),
    path('depose_annonce/', views.depose_annonce, name='depose_annonce'),
    path('annoncedetail/', views.annoncedetail, name='annoncedetail'),
    path('liste_annonce/', views.liste_annonce, name='liste_annonce'),
    path('logsign/', views.logsign, name='logsign'),  # Page log ou sign in
    path('signin/', views.signin, name='signin'),  # Page sign in
    path('login/', views.login, name='login'),  # Page log in
]
