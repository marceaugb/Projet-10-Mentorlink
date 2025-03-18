from django.db import models
import os
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    GENRE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
        ('Autre', 'Autre'),
    ]

    age = models.IntegerField()
    civilite = models.CharField(max_length=10, choices=GENRE_CHOICES)
    adresse = models.TextField()
    role = models.CharField(max_length=14, choices=TYPE_CHOICES)

    # Ajoutez des related_name personnalisés pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="utilisateur_groups",  # Nom personnalisé pour éviter les conflits
        related_query_name="utilisateur",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="utilisateur_permissions",  # Nom personnalisé pour éviter les conflits
        related_query_name="utilisateur",
    )

    REQUIRED_FIELDS = ['nom', 'prenom', 'email', 'age', 'civilite', 'adresse', 'role']


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
