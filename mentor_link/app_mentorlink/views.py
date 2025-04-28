from django.shortcuts import render, redirect
from .models import Utilisateur, Annonce
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
from .models import Conversation, Message
from django.contrib.auth.decorators import login_required

def home(request):
    personnes = Utilisateur.objects.all()  # Récupère toutes les personnes
    annonces = Annonce.objects.all()  # Récupère toutes les annonces
    context = {'personnes': personnes, 'annonces': annonces}
    return render(request, 'home.html', context)

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

def liste_annonces(request):
    annonces = Annonce.objects.all()
    return render(request, 'liste_annonces.html', {'annonces': annonces})


@login_required
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
    
    context = {
        'utilisateur': utilisateur,
        'annonces': annonces,
        'titre': titre,
    }
    
    return render(request, 'annonces_utilisateur.html', context)


@login_required
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
def chat_view(request, other_user_username):
    other_user = User.objects.get(username=other_user_username)
    messages = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(sender=other_user, receiver=request.user)
    messages = messages.order_by('timestamp')
    
    # On renvoie les messages dans un format de mise à jour partielle pour HTMX
    return render(request, 'chat/chat_log.html', {'messages': messages})

@login_required
def send_message(request, other_user_username):
    if request.method == 'POST':
        message_content = request.POST['message']
        other_user = User.objects.get(username=other_user_username)
        
        # Créer un message et le sauvegarder
        message = Message.objects.create(
            sender=request.user,
            receiver=other_user,
            content=message_content
        )
        
        # Pour HTMX, on renvoie une mise à jour du chat_log
        return render(request, 'chat/chat_log.html', {'messages': [message]})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'conversation_list.html', {'conversations': conversations})

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    return render(request, 'conversation_detail.html', {
        'conversation': conversation,
        'messages': conversation.messages.order_by('timestamp')
    })

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    return redirect('conversation_detail', pk=conversation.pk)
