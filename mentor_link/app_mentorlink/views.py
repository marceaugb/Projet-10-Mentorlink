from django.shortcuts import render, redirect
from .models import Utilisateur, Annonces
from django.contrib.auth.decorators import login_required
from .forms import UtilisateurForm, AnnonceForm
from django.contrib.auth import authenticate, login

def home(request):
    personnes = Utilisateur.objects.all()  # Récupère toutes les personnes
    annonces = Annonces.objects.all()  # Récupère toutes les annonces
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
        # Retrieve form data
        try:
            prix = int(request.POST.get('prix'))  # Convert to integer
        except (ValueError, TypeError):
            return render(request, 'error.html', {'message': 'Le prix doit être un nombre valide'})

        metier = request.POST.get('metier')
        adresse = request.POST.get('adresse')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        # Create new Annonce
        try:
            nouvelle_annonce = Annonces.objects.create(
                prix=prix,
                metier=metier,
                adresse=adresse,
                description=description,
                image=image,
                #id_personnes=utilisateur
            )
            # Redirect to a success page or the list of annonces
            return redirect('liste_annonce')  # Replace with your actual URL name
        
        except Exception as e:
            # Handle any errors in creating the annonce
            return render(request, 'error.html', {'message': str(e)})

    # If not a POST request, just render the form
    return render(request, 'depose_annonce.html')

@login_required
def confirmation(request):
    return render(request, 'confirmation.html')

@login_required
def search(request):
   return render(request,'search.html')

@login_required
def profil(request):
    if request.method == 'POST':
        user = request.user
        user.nom = request.POST.get('nom')
        user.prenom = request.POST.get('prenom')
        user.civilite = request.POST.get('civilite')
        user.role = request.POST.get('role')
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
            user = form.save(commit=False)
            user.nom = form.cleaned_data['nom']
            user.prenom = form.cleaned_data['prenom']
            user.civilite = form.cleaned_data['civilite']
            user.save()
            print("Utilisateur enregistré:", user.username)
            login(request, user)
            return redirect('profil')
        else:
            print("Formulaire invalide:", form.errors)  # Affiche les erreurs du formulaire
    else:
        form = UtilisateurForm()
    return render(request, 'signup.html', {'form': form})

def loginperso(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige vers la page d'accueil
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def afficher_annonces(request):
    annonces = Annonces.objects.all()
    return render(request, 'annonces.html', {'annonces': annonces})
