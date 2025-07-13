# Utiliser une image Python officielle comme base
FROM python:3.13-slim

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=main.settings

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système requises
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libpng-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Créer et activer l'environnement virtuel
RUN pip install --upgrade pip

# Copier les fichiers de dépendances
COPY requirements.txt /app/

# Installer les dépendances
RUN pip install -r requirements.txt && \
    pip install daphne

# Copier le reste du projet
COPY . /app/

# Créer le répertoire pour les fichiers média et statiques
RUN mkdir -p /app/media /app/static /app/db

# Exposer le port sur lequel Django va s'exécuter
EXPOSE 8080

# Commande pour démarrer l'application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8080", "main.asgi:application"]
