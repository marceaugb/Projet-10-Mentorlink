# 📌 Nom du Projet

Application web permettant de mettre en liens les mentors et des mentorés dans un espace sécurisé et facile d'utilisation qui vont leurs permettre d'échanger grâce a une
messagerie en live. L'application fera aussi du scaling.

## 📖 Table des matières

- [📌 MentorLink](#-MentorLink)
- [🚀 Installation](#-installation)
- [▶️ Utilisation](#️-utilisation)
- [🛠 Technologies](#-technologies)
- [📂 Structure du projet](#-structure-du-projet)

---

## 🚀 Installation

### 1️⃣ Cloner le dépôt
```bash
git clone [https://github.com/utilisateur/](https://github.com/marceaugb/Projet-10-Mentorlink)
cd mon-projet-django
```

### 2️⃣ Créer un environnement virtuel et l'activer
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer la base de données
```bash
python manage.py migrate
```
---

## ▶️ Utilisation

### Démarrer le serveur Django
```bash
python manage.py runserver # il faut être dans le répertoire qui contient le fichier manage.py
```
Le projet sera accessible sur `http://127.0.0.1:8000/`.

### Exécuter les tests
```bash
python manage.py test
```

---

## 🛠 Technologies

- Django vX.Y.Z
- PostgreSQL / SQLite

---

## 📂 Structure du projet

```
MENTOR_LINK/
│── manage.py
│── urls.py
│── settings.py
│── __init_.py
│── wsgi.py
│── manage.py
│── _pycache_/
│── app_mentorlink/
│   │── models.py
│   │── views.py
│   │── _init_.py
│   │── admin.py
│   │── apps.py
│   │── forms.py
│   │── templates/
|   │── migrations/
|   │── _pycache_/
│── db.sqlite3
```

---
