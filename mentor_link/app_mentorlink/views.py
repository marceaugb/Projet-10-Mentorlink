from django.shortcuts import render, redirect
from .models import Utilisateur, Annonce, Room
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.http import JsonResponse
from .models import Message
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator

def home(request):
    personnes = Utilisateur.objects.all()
    annonces = Annonce.objects.all().order_by('-id')  # Tri par ID décroissant (plus récentes en premier)
    
    # Pagination
    paginator = Paginator(annonces, 12)  # 12 annonces par page (3x4 sur desktop)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'personnes': personnes, 
        'annonces': page_obj,  # Remplace annonces par page_obj
        'page_obj': page_obj   # Ajout pour la navigation
    }
    return render(request, 'home.html', context)

def search(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Recherche dans les champs metier et description
        results = Annonce.objects.filter(
            Q(metier__icontains=query) | 
            Q(description__icontains=query)
        ).order_by('-id')
    
    # Pagination pour les résultats de recherche
    paginator = Paginator(results, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'results': page_obj,  # Remplace results par page_obj
        'page_obj': page_obj
    }
    
    return render(request, 'search.html', context)

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
            return redirect('home')  # Remplacez par le nom de votre vue
    else:
        form = AnnonceForm()
    
    return render(request, 'depose_annonce.html', {'form': form})

@login_required
def confirmation(request):
    return render(request, 'confirmation.html')

@login_required
def profil(request):
    if request.method == 'POST':
        user = request.user
        user.last_name = request.POST.get('nom')
        user.first_name = request.POST.get('prenom')
        user.civilite = request.POST.get('civilite')
        user.date_naissance = request.POST.get('date_naissance')  # avec mise à jour de l'âge
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

def annonces_utilisateur(request, user_id=None):
    """
    Affiche toutes les annonces d'un utilisateur spécifique.
    Si user_id n'est pas fourni, affiche les annonces de l'utilisateur connecté.
    """
    if user_id is None:
        # Si aucun ID n'est fourni, afficher les annonces de l'utilisateur connecté
        utilisateur = request.user
        titre = "Mes annonces"
    else:
        # Sinon, afficher les annonces de l'utilisateur spécifié
        try:
            utilisateur = Utilisateur.objects.get(id=user_id)
            titre = f"Annonces de {utilisateur.first_name} {utilisateur.last_name}"
        except Utilisateur.DoesNotExist:
            return render(request, 'erreur.html', {'message': "Cet utilisateur n'existe pas."})
    
    # Récupérer toutes les annonces de l'utilisateur
    annonces = Annonce.objects.filter(id_personnes=utilisateur).order_by('-id')
    
    # Pagination pour les annonces utilisateur
    paginator = Paginator(annonces, 8)  # 8 annonces par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'utilisateur': utilisateur,
        'annonces': page_obj,
        'page_obj': page_obj,
        'titre': titre,
    }
    
    return render(request, 'annonces_utilisateur.html', context)

def annonce_detail(request, annonce_id):
    """
    Affiche le détail d'une annonce spécifique.
    """
    try:
        annonce = Annonce.objects.get(id=annonce_id)
    except Annonce.DoesNotExist:
        return render(request, 'erreur.html', {'message': "Cette annonce n'existe pas."})
    
    context = {
        'annonce': annonce,
    }
    
    return render(request, 'annonce_detail.html', context)

@login_required
def modifier_annonce(request, annonce_id):
    """
    Permet à l'utilisateur de modifier son annonce.
    """
    try:
        annonce = Annonce.objects.get(id=annonce_id, id_personnes=request.user)
    except Annonce.DoesNotExist:
        return render(request, 'erreur.html', {'message': "Cette annonce n'existe pas ou vous n'avez pas le droit de la modifier."})
    
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES, instance=annonce)
        if form.is_valid():
            form.save()
            return redirect('annonce_detail', annonce_id=annonce.id)
    else:
        form = AnnonceForm(instance=annonce)
    
    context = {
        'form': form,
        'annonce': annonce,
        'titre': "Modifier mon annonce",
    }
    
    return render(request, 'depose_annonce.html', context)

@login_required
def supprimer_annonce(request, annonce_id):
    """
    Permet à l'utilisateur de supprimer son annonce.
    """
    try:
        # Vérifier que l'annonce existe et appartient à l'utilisateur connecté
        annonce = Annonce.objects.get(id=annonce_id, id_personnes=request.user)
    except Annonce.DoesNotExist:
        return render(request, 'erreur.html', {'message': "Cette annonce n'existe pas ou vous n'avez pas le droit de la supprimer."})
    
    # Si la requête est en POST, supprimer l'annonce
    if request.method == 'POST':
        annonce.delete()
        return redirect('mes_annonces')
    
    # Si la requête est en GET, afficher la page de confirmation
    context = {
        'annonce': annonce,
    }
    
    return render(request, 'confirmer_suppression.html', context)

@login_required
def room(request, slug):
    print(f"Room view called with slug: {slug}")
    room = get_object_or_404(Room, slug=slug)
    return render(request, 'room.html', {'room': room})

@login_required
def start_private_chat(request, annonce_id):
    annonce = get_object_or_404(Annonce, id=annonce_id)
    user = request.user
    author = annonce.id_personnes  # ForeignKey to Utilisateur

    # Check if a room exists between the two users
    room = Room.objects.filter(users=user).filter(users=author).first()
    if not room:
        # Create a room for the two users
        room_name = f"Chat: {user.username} - {author.username}"
        room_slug = f"room-{min(user.id, author.id)}-{max(user.id, author.id)}"  # Changed to "room-"
        room = Room.objects.create(name=room_name, slug=room_slug)
        room.users.add(user, author)

    return JsonResponse({'room_slug': room.slug})

def my_messages(request):
    return render(request, 'my_messages.html')
