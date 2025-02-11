from django.shortcuts import render
from .models import Utilisateur, Annonces


def bdd(request):
    personnes = Utilisateur.objects.all()  # Récupère toutes les personnes
    annonces = Annonces.objects.all()  # Récupère toutes les annonces
    context = {'personnes': personnes,'annonces': annonces}

    return render(request, 'bdd.html', context)

def home(request):
   return render(request,'home.html')

def depose_annonce(request):
   return render(request, 'depose_annonce.html')

def messages(request):
   return render(request,'messages.html')

#def views(request):
#   return render(request,'home.html')

def search(request):
   return render(request,'search.html')

def profil(request):
   return render(request,'profil.html')

def signin(request):
   return render(request, "signin.html")

def login(request):
   return render(request, "login.html")

def logsign(request):
   return render(request,'logsign.html')

def liste_annonce(request):
    personnes = Utilisateur.objects.all()  # Récupère toutes les personnes
    annonces = Annonces.objects.all()  # Récupère toutes les annonces
    context = {'personnes': personnes,'annonces': annonces}
    
    return render(request, 'liste_annonce.html', context)

def annoncedetail(request):
   return render(request,'annonce_detail1.html')

def annoncedetaix(request):
   return render(request,'annonce_detailx.html')
