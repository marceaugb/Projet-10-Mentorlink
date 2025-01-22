"""
URL configuration for mentor_link project.

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
from base_de_donnee.views import index
from mentorlink import views


urlpatterns = [
    path('', index, name='index'),  # Page d'accueil
    path('', views.index_home, name='index_home'),  # Page d'accueil
    path('messages/', views.messages, name='messages'),  # Page des messages
    path('search/', views.search, name='search'),  # Page de recherche
    path('profil/', views.profil, name='profil'),  # Page de profil
    path('annonce/', views.annonce, name='annonce'),  # Page des annonces
    path('annoncedetail/', views.annoncedetail, name='annoncedetail'),  # Page des détails de l'annonce
]
