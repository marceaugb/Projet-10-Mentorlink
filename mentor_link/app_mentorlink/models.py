from django.db import models
import os

class Utilisateur(models.Model):
    GENRE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
        ('Autre', 'Autre'),
    ]

    TYPE_CHOICES = [
        ('Mentor', 'Mentor'),
        ('Mentoré', 'Mentoré'),
        ('Administrateur', 'Administrateur'),
    ]

    id = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    genre = models.CharField(max_length=6, choices=GENRE_CHOICES)
    adresse = models.TextField()
    role = models.CharField(max_length=14, choices=TYPE_CHOICES)

    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(age__gt=15), name='age_greater_than_15'),
        ]

    def __str__(self):
        return (f"Id:{self.id}, Nom :{self.nom}, Prénom:{self.prenom}, Age:{self.age}, Genre:{self.genre}, Adresse:{self.adresse}, Type:{self.role}")


class Annonces(models.Model):
    id = models.IntegerField(primary_key=True)
    prix = models.IntegerField()
    
    # Use os.path.join to create a path to the desktop
    def get_image_path(instance, filename):
        # This will work cross-platform (Windows, Mac, Linux)
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'mentorlink_photos')
        
        # Create the directory if it doesn't exist
        os.makedirs(desktop_path, exist_ok=True)
        
        return os.path.join(desktop_path, filename)
    
    image = models.ImageField(upload_to='photos/', null=True, blank=True)
    metier = models.CharField(max_length=1000)
    adresse = models.TextField()
    description = models.TextField(max_length=100000, null=True, blank=True)
    id_personnes = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, null=True, blank=True)
   
    def __str__(self):
        return (f"Métier= {self.metier}, Prix= {self.prix}, Adresse= {self.adresse}")
