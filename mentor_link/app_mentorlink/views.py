# Mettre à jour la fonction search dans views.py
from django.shortcuts import render, redirect
from .models import Utilisateur, Annonce
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm

def home(request):
    personnes = Utilisateur.objects.all()  # Récupère toutes les personnes
    annonces = Annonce.objects.all()  # Récupère toutes les annonces
    context = {'personnes': personnes, 'annonces': annonces}
    if request.user.is_authenticated:
        return render(request, 'home.html', context)
    else:
        return render(request, 'home_nonconnecte.html', context)

@login_required
def messages(request):
   return render(request,'messages.html')

@login_required
def depose_annonce(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES)
        if form.is_valid():
            # Ne pas sauvegarder le formulaire immédiatement
            annonce = form.save(commit=False)
            
            # Associer l'utilisateur connecté à l'annonce
            annonce.id_personnes = request.user
            
            # Maintenant sauvegarder l'annonce
            annonce.save()
            
            # Rediriger vers une page de succès ou la liste des annonces
            return redirect('liste_annonces')  # Remplacez par le nom de votre vue
    else:
        form = AnnonceForm()
    
    return render(request, 'depose_annonce.html', {'form': form})

@login_required
def confirmation(request):
    return render(request, 'confirmation.html')

@login_required
def search(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Recherche dans les champs metier et description
        results = Annonce.objects.filter(
            Q(metier__icontains=query) | 
            Q(description__icontains=query)
        )
    
    context = {
        'query': query,
        'results': results
    }
    
    return render(request, 'search.html', context)

@login_required
def profil(request):
    if request.method == 'POST':
        user = request.user
        user.nom = request.POST.get('nom')
        user.prenom = request.POST.get('prenom')
        user.civilite = request.POST.get('civilite')
        user.age = request.POST.get('naissance')  # Mise à jour de l'âge
        user.adresse = request.POST.get('adresse')
        user.email = request.POST.get('email')
        user.save()
        return redirect('profil') # Redirige vers la page profil après enregistrement
    return render(request, 'profil.html', {'user': request.user})

def signup(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            print("Formulaire valide")
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            print("Formulaire invalide:", form.errors)  # Affiche les erreurs du formulaire
    else:
        form = UtilisateurForm()

    return render(request, 'signup.html', {'form': form})


def loginperso(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)  # Vérifie les identifiants

            if user is not None:
                print(f"Utilisateur {user} authentifié avec succès.")  # Debug
                login(request, user)  # Connecte l'utilisateur
                return redirect('home')  # Redirection après connexion réussie
            else:
                print("Échec de l'authentification : Mot de passe incorrect.")  # Debug
        else:
            print("Échec de l'authentification : Formulaire non valide.")  # Debug

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def liste_annonces(request):
    annonces = Annonce.objects.all()
    return render(request, 'liste_annonces.html', {'annonces': annonces})