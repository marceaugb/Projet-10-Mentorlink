from django.shortcuts import render, redirect, get_object_or_404
from .models import Utilisateur, Annonce, Room, Message, MessageReadStatus
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth import authenticate, login
from django.db.models import Q, Max, Count, Case, When, IntegerField
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


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
            return redirect('home')  # Remplacez par le nom de votre vue
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
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Récupérer l'URL de redirection depuis le paramètre next
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('home')
            else:
                print("Échec de l'authentification : Mot de passe incorrect.")
        else:
            print("Échec de l'authentification : Formulaire non valide.")
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
    
    context = {
        'utilisateur': utilisateur,
        'annonces': annonces,
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


@login_required(login_url='/login/')
def start_private_chat(request, annonce_id):
    annonce = get_object_or_404(Annonce, id=annonce_id)
    user = request.user
    author = annonce.id_personnes
    
    # Empêcher un utilisateur de se contacter lui-même
    if user == author:
        return redirect('annonce_detail', annonce_id=annonce_id)
    
    # Vérifier si une room existe entre les deux utilisateurs
    room = Room.objects.filter(users=user).filter(users=author).first()
    
    if not room:
        # Créer une room pour les deux utilisateurs
        room_name = f"Chat: {user.username} - {author.username}"
        room_slug = f"room-{min(user.id, author.id)}-{max(user.id, author.id)}"
        room = Room.objects.create(
            name=room_name,
            slug=room_slug,
            last_activity=timezone.now()
        )
        room.users.add(user, author)
    
    # Rediriger vers la room de chat
    return redirect('room', slug=room.slug)

def my_messages(request):
    return render(request, 'my_messages.html')

def custom_404(request, exception):
    """Vue personnalisée pour l'erreur 404"""
    return HttpResponseNotFound(render(request, '404.html'))

def custom_500(request):
    """Vue personnalisée pour l'erreur 500"""
    return HttpResponseServerError(render(request, '500.html'))

def custom_403(request, exception):
    """Vue personnalisée pour l'erreur 403"""
    return HttpResponseForbidden(render(request, '403.html'))

def custom_400(request, exception):
    """Vue personnalisée pour l'erreur 400"""
    return HttpResponseBadRequest(render(request, '400.html'))

def test_errors(request):
    """Vue pour tester les pages d'erreur - À supprimer en production"""
    error_type = request.GET.get('type', '404')
    
    if error_type == '404':
        from django.http import Http404
        raise Http404("Page de test 404")
    elif error_type == '500':
        raise Exception("Erreur de test 500")
    elif error_type == '403':
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Test erreur 403")
    elif error_type == '400':
        from django.core.exceptions import BadRequest
        raise BadRequest("Test erreur 400")
    
    return render(request, 'home.html')


@login_required
def get_conversations_api(request):
    """API pour récupérer les conversations - version simplifiée"""
    user = request.user
    
    # Récupérer les rooms où l'utilisateur participe
    user_rooms = Room.objects.filter(users=user).order_by('-id')
    
    conversations = []
    for room in user_rooms:
        # Trouver l'autre utilisateur dans la conversation
        other_user = room.users.exclude(id=user.id).first()
        if not other_user:
            continue
            
        conversations.append({
            'id': room.id,
            'slug': room.slug,
            'participant_name': f"{other_user.first_name} {other_user.last_name}",
            'participant_username': other_user.username,
        })
    
    return JsonResponse({
        'conversations': conversations,
    })


@login_required
def all_messages(request):
    """Affiche toutes les conversations de l'utilisateur connecté avec les derniers messages"""
    user = request.user
    
    # Récupérer toutes les rooms avec annotations
    user_rooms = Room.objects.filter(users=user).annotate(
        last_message_time=Max('messages__timestamp'),
        total_messages=Count('messages')
    ).order_by('-last_message_time')
    
    conversations = []
    for room in user_rooms:
        other_user = room.get_other_user(user)
        if other_user:
            # Récupérer le dernier message
            last_message = room.messages.order_by('-timestamp').first()
            
            # Compter les messages non lus
            unread_count = Message.objects.filter(
                room=room
            ).exclude(
                user=user
            ).exclude(
                id__in=MessageReadStatus.objects.filter(user=user).values_list('message_id', flat=True)
            ).count()
            
            conversations.append({
                'room': room,
                'other_user': other_user,
                'last_message': last_message,
                'last_message_time': last_message.timestamp if last_message else None,
                'unread_count': unread_count,
            })
    
    return render(request, 'all_messages.html', {
        'conversations': conversations,
        'user': user
    })


@login_required
def get_unread_count(request):
    """API pour récupérer le nombre de messages non lus"""
    user = request.user
    
    # Compter les messages non lus pour cet utilisateur
    unread_count = Message.objects.filter(
        room__users=user  # Messages dans les rooms où l'utilisateur participe
    ).exclude(
        user=user  # Exclure les messages envoyés par l'utilisateur lui-même
    ).exclude(
        id__in=MessageReadStatus.objects.filter(user=user).values_list('message_id', flat=True)
    ).count()
    
    return JsonResponse({'unread_count': unread_count})


@login_required
def get_conversations_api(request):
    """API pour récupérer les conversations avec le dernier message"""
    user = request.user

    user_rooms = Room.objects.filter(users=user).annotate(
        last_message_time=Max('messages__timestamp'),
        total_messages=Count('messages')
    ).order_by('-last_message_time')

    conversations = []
    total_unread = 0

    for room in user_rooms:
        other_user = room.get_other_user(user)
        if not other_user:
            continue

        last_message = room.messages.order_by('-timestamp').first()
        
        # Compter les messages non lus
        unread_count = Message.objects.filter(
            room=room
        ).exclude(
            user=user
        ).exclude(
            id__in=MessageReadStatus.objects.filter(user=user).values_list('message_id', flat=True)
        ).count()

        total_unread += unread_count

        conversations.append({
            'id': room.id,
            'slug': room.slug,
            'participant_name': f"{other_user.first_name} {other_user.last_name}",
            'participant_username': other_user.username,
            'last_message': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else 'Aucun message'),
            'last_message_from_current_user': last_message.user == user if last_message else False,
            'timestamp': last_message.timestamp.strftime('%d/%m %H:%M') if last_message else '',
            'unread_count': unread_count,
            'total_messages': room.total_messages,
        })

    return JsonResponse({
        'conversations': conversations,
        'total_unread': total_unread
    })



@login_required
def mark_messages_as_read(request, room_slug):
    """Marquer tous les messages d'une conversation comme lus"""
    if request.method == 'POST':
        room = get_object_or_404(Room, slug=room_slug, users=request.user)

        # Récupérer tous les messages de la room qui ne sont pas de l'utilisateur actuel
        messages_to_mark = Message.objects.filter(
            room=room
        ).exclude(user=request.user)

        # Marquer comme lus
        for message in messages_to_mark:
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=request.user
            )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def room(request, slug):
    """Vue pour afficher une conversation spécifique"""
    room = get_object_or_404(Room, slug=slug, users=request.user)

    # Marquer tous les messages de cette conversation comme lus
    messages_to_mark = Message.objects.filter(
        room=room
    ).exclude(user=request.user)

    for message in messages_to_mark:
        MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )

    # Récupérer les messages de la conversation
    messages = Message.objects.filter(room=room).order_by('timestamp')

    return render(request, 'room.html', {
        'room': room,
        'messages': messages
    })

@csrf_exempt
def health(request):
    return HttpResponse("ok", status=200)
