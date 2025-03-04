from django.shortcuts import render, redirect
from .models import Utilisateur, Annonces
from django.contrib.auth.decorators import login_required
from .forms import AnnonceForm

def bdd(request):
    personnes = Utilisateur.objects.all()
    annonces = Annonces.objects.all()
    context = {'personnes': personnes,'annonces': annonces}

    return render(request, 'bdd.html', context)

def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return render(request, 'home_nonconnecte.html')

@login_required
def messages(request):
   return render(request,'messages.html')

"""
@login_required
def depose_annonce(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES)  # Important: request.FILES handles file uploads
        if form.is_valid():
            form.save()
            return redirect('confirmation')  # Redirect after successful submission
    else:
        form = AnnonceForm()

    return render(request, 'depose_annonce.html', {'form': form})
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Annonces, Utilisateur

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

        # Get the current user's Utilisateur instance
        try:
            utilisateur = Utilisateur.objects.get(id=request.user.id)
        except Utilisateur.DoesNotExist:
            # Handle case where user doesn't have a corresponding Utilisateur
            return render(request, 'error.html', {'message': 'Utilisateur non trouvé'})

        # Create new Annonce
        try:
            nouvelle_annonce = Annonces.objects.create(
                prix=prix,
                metier=metier,
                adresse=adresse,
                description=description,
                image=image,
                id_personnes=utilisateur
            )
            # Redirect to a success page or the list of annonces
            return redirect('liste_annonce')  # Replace with your actual URL name
        
        except Exception as e:
            # Handle any errors in creating the annonce
            return render(request, 'error.html', {'message': str(e)})

    # If not a POST request, just render the form
    return render(request, 'depose_annonce.html')

def confirmation(request):
    return render(request, 'confirmation.html')


@login_required
def search(request):
   return render(request,'search.html')

@login_required
def profil(request):
   return render(request,'profil.html')

def signup(request):
   return render(request, "signup.html")

def login(request):
   return render(request, "login.html")

"""
def liste_annonce(request):
    personnes = Utilisateur.objects.all()
    annonces = Annonces.objects.all()
    context = {'personnes': personnes,'annonces': annonces}
    
    return render(request, 'liste_annonce.html', context)
"""
def liste_annonce(request):
    # Use select_related to optimize database queries
    annonces = Annonces.objects.all().select_related('id_personnes')
    personnes = Utilisateur.objects.all()
    context = {'personnes': personnes,'annonces': annonces}
    
    # Optional: Filter out announcements without images if needed
    # annonces = annonces.filter(image__isnull=False)
    
    return render(request, 'liste_annonce.html', context)


def annoncedetail(request):
   return render(request,'annonce_detail1.html')

def annoncedetaix(request):
   return render(request,'annonce_detailx.html')

def confirmation(request):
    return render(request, 'confirmation.html')

def afficher_annonces(request):
    annonces = Annonces.objects.all()
    return render(request, 'annonces.html', {'annonces': annonces})
