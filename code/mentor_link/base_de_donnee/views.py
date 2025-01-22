from django.shortcuts import render
from .models import Utilisateur, Annonces

def index(request):
    personnes = Utilisateur.objects.all()
    annonces = Annonces.objects.all()  # Récupère toutes les annonces
    context = {'personnes': personnes, 'annonces': annonces}
    return render(request, 'index.html', context)
