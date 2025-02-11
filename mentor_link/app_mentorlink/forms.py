from django import forms
from .models import Annonces

class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonces
        fields = ['prix', 'url_photo', 'metier', 'adresse', 'description', 'id_personnes']