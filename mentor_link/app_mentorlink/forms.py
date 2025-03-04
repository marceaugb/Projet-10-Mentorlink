from django import forms
from .models import Annonces  # Adjust the import based on your actual model location

class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonces
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
