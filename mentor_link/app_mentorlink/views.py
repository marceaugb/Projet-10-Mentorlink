from django.shortcuts import render
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

@login_required
def depose_annonce(request):
    if request.method == 'POST':
        form = AnnonceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('confirmation')
    else:
        form = AnnonceForm()
    return render(request, 'depose_annonce.html', {'form': form})


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

def liste_annonce(request):
    personnes = Utilisateur.objects.all()
    annonces = Annonces.objects.all()
    context = {'personnes': personnes,'annonces': annonces}
    
    return render(request, 'liste_annonce.html', context)

def annoncedetail(request):
   return render(request,'annonce_detail1.html')

def annoncedetaix(request):
   return render(request,'annonce_detailx.html')

def confirmation(request):
    return render(request, 'confirmation.html')
