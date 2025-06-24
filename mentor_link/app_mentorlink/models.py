from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_birthdate(value):
    """Vérifie si l'utilisateur a au moins 15 ans."""
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 15:
        raise ValidationError("Vous devez avoir au moins 15 ans.")
    
class Utilisateur(AbstractUser):
    GENRE_CHOICES = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
        ('Autre', 'Autre'),
    ]

    date_naissance = models.DateField(
        blank=True,
        null=True,
        validators=[validate_birthdate]
    )

    civilite = models.CharField(max_length=10, choices=GENRE_CHOICES, null=True, blank=True)
    adresse = models.TextField()

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'date_naissance', 'civilite', 'adresse']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name="utilisateur_groups",
        related_query_name="utilisateur",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name="utilisateur_permissions",
        related_query_name="utilisateur",
    )

class Room(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    users = models.ManyToManyField('Utilisateur', blank=True)  # Associe les utilisateurs au salon

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.timestamp}"

class Annonce(models.Model):
    id = models.IntegerField(primary_key=True)
    prix = models.IntegerField()
    
    image = models.ImageField(upload_to='annonces/', null=True, blank=True)
    
    metier = models.CharField(max_length=1000)
    adresse = models.TextField()
    description = models.TextField(max_length=100000, null=True, blank=True)
    id_personnes = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, null=True, blank=True)
   
    def __str__(self):
        return (f"Métier= {self.metier}, Prix= {self.prix}, Adresse= {self.adresse}")
    
