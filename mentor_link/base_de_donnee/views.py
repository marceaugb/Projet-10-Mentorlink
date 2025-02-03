from django.shortcuts import render
from .models import Utilisateur, Annonces


def index(request):
    personnes = Utilisateur.objects.all()  # Récupère toutes les personnes
    annonces = Annonces.objects.all()  # Récupère toutes les annonces
    context = {'personnes': personnes,'annonces': annonces}
    
    return render(request, 'index.html', context)

def index_home(request):
   return render(request,'index_home.html')

def annonce(request):
   return render(request,'annonce.html')

def messages(request):
   return render(request,'messages.html')

#def views(request):
#   return render(request,'index_home.html')

def search(request):
   return render(request,'search.html')

def profil(request):
   return render(request,'profil.html')

def home(request):
    personnes = Utilisateur.objects.all()  # Récupère toutes les personnes
    annonces = Annonces.objects.all()  # Récupère toutes les annonces
    context = {'personnes': personnes,'annonces': annonces}
    
    return render(request, 'home.html', context)

def annoncedetail(request):
   return render(request,'annonce_detail1.html')

def annoncedetaix(request):
   return render(request,'annonce_detailx.html')
