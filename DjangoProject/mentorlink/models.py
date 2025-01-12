from django.db import models

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

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    genre = models.CharField(max_length=6, choices=GENRE_CHOICES)
    adresse = models.TextField()
    type_utilisateur = models.CharField(max_length=12, choices=TYPE_CHOICES)

    # Optionnel: définir une contrainte de vérification pour l'âge
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(age__gt=15), name='age_greater_than_15'),
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom}"
