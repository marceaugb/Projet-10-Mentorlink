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

    id = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    genre = models.CharField(max_length=6, choices=GENRE_CHOICES)
    adresse = models.TextField()
    role = models.CharField(max_length=14, choices=TYPE_CHOICES)

    # Optionnel: définir une contrainte de vérification pour l'âge
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(age__gt=15), name='age_greater_than_15'),
        ]

    def __str__(self):
        return (f"Id:{self.id}, Nom :{self.nom}, Prénom:{self.prenom}, Age:{self.age}, Genre:{self.genre}, Adresse:{self.adresse}, Type:{self.role}")


class Annonces(models.Model):

    id = models.IntegerField(primary_key=True)
    prix = models.IntegerField()
    url_photo = models.CharField(max_length=1000)
    metier = models.CharField(max_length=1000)
    adresse = models.TextField()
    id_personnes = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, null=True, blank=True)
    

    def __str__(self):
        return (f"Métier= {self.metier}, Prix= {self.prix}, Adresse= {self.adresse}")
