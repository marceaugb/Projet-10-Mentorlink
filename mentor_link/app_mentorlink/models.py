from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Max, Count, Case, When, IntegerField


def validate_birthdate(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Vous devez avoir au moins 18 ans.")
    
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
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    users = models.ManyToManyField('Utilisateur', related_name='rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=timezone.now)  # ✅ Valeur par défaut
    
    def get_other_user(self, current_user):
        """Retourne l'autre utilisateur de la conversation"""
        return self.users.exclude(id=current_user.id).first()
    
    def get_last_activity(self):
        """Retourne le timestamp du dernier message"""
        last_message = self.messages.order_by('-timestamp').first()
        return last_message.timestamp if last_message else self.created_at
    
    @property
    def last_activity_computed(self):
        return self.get_last_activity()

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Nouveau champ pour marquer comme lu

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username} -> {self.timestamp}"

class MessageReadStatus(models.Model):
    """Modèle pour suivre quels messages ont été lus par quels utilisateurs"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_status')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user']

class Annonce(models.Model):
    prix = models.IntegerField()
    
    image = models.ImageField(upload_to='annonces/', null=True, blank=True)
    
    metier = models.CharField(max_length=1000)
    adresse = models.TextField()
    description = models.TextField(max_length=100000, null=True, blank=True)
    id_personnes = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, null=True, blank=True)
   
    def __str__(self):
        return (f"Métier= {self.metier}, Prix= {self.prix}, Adresse= {self.adresse}")
