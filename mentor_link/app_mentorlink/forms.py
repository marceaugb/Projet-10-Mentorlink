from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from .models import Annonce, Utilisateur
from datetime import date

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
    email = forms.EmailField(required=True, label="Email")
    civilite = forms.ChoiceField(choices=Utilisateur.GENRE_CHOICES, required=True, label="Genre")
    adresse = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 40}), required=True, label="Adresse")

    
    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'date_naissance', 'civilite', 'adresse']

    def clean_date_naissance(self):
        """Vérifie si la date de naissance correspond à un âge de 15 ans minimum."""
        date_naissance = self.cleaned_data.get("date_naissance")
        if not date_naissance:
            raise forms.ValidationError("La date de naissance est obligatoire.")
        
        today = date.today()
        age = today.year - date_naissance.year - ((today.month, today.day) < (date_naissance.month, date_naissance.day))

        if age < 18:
            raise forms.ValidationError("Vous devez avoir au moins 18 ans.")

        return date_naissance




