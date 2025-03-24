from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from .models import Annonce, Utilisateur


class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = ['prix', 'image', 'metier', 'adresse', 'description']
        
    def clean_prix(self):
        prix = self.cleaned_data.get('prix')
        if prix is not None and prix <= 0:
            raise forms.ValidationError("Le prix doit être un nombre positif.")
        return prix
    
    def clean_metier(self):
        metier = self.cleaned_data.get('metier')
        if metier and len(metier) > 50:
            raise forms.ValidationError("Le métier ne doit pas dépasser 50 caractères.")
        return metier
    
    def clean_adresse(self):
        adresse = self.cleaned_data.get('adresse')
        if adresse and len(adresse) > 100:
            raise forms.ValidationError("L'adresse ne doit pas dépasser 100 caractères.")
        return adresse
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 500:
            raise forms.ValidationError("La description ne doit pas dépasser 500 caractères.")
        return description

class UtilisateurForm(UserCreationForm):
    nom = forms.CharField(max_length=30, required=True, label="Nom")
    prenom = forms.CharField(max_length=30, required=True, label="Prénom")
    email = forms.EmailField(required=True, label="Email")
    age = forms.IntegerField(required=True, label="Âge")
    civilite = forms.ChoiceField(choices=Utilisateur.GENRE_CHOICES, required=True, label="Genre")
    adresse = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 40}), required=True, label="Adresse")
    role = forms.ChoiceField(choices=Utilisateur.TYPE_CHOICES, required=True, label="Rôle")

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password1', 'password2', 'nom', 'prenom', 'age', 'civilite', 'adresse', 'role']

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 15:
            raise ValidationError("L'âge doit être supérieur ou égal à 15 ans.")
        return age