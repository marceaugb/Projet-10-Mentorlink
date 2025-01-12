from django.shortcuts import render

def index(request):
   return render(request,'index.html')

def annonce(request):
   return render(request,'annonce.html')

def messages(request):
   return render(request,'messages.html')

def views(request):
   return render(request,'index.html')

def search(request):
   return render(request,'search.html')

def profil(request):
   return render(request,'profil.html')
def home(request):
   return render(request,'home.html')

def annoncedetail(request):
   return render(request,'annonce_detail1.html')

