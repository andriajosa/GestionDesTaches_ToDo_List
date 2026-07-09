# tools/seed_data.py
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models import User, Category, Task, TaskAssignment
from backend.security import hash_password, chiffrer_texte

app = create_app()

with app.app_context():
    print("🌱 Début de l'injection des données de test...")

    # 1. Création des utilisateurs (Rôles Admin et User)
    admin = User.query.filter_by(email="admin@test.com").first()
    if not admin:
        admin = User(nom="Admin Principal", email="admin@test.com", 
                     mot_de_passe_hash=hash_password("admin123"), role="admin")
        db.session.add(admin)

    user1 = User.query.filter_by(email="user1@test.com").first()
    if not user1:
        user1 = User(nom="Finaritra Fiderana", email="user1@test.com", 
                     mot_de_passe_hash=hash_password("user123"), role="user")
        db.session.add(user1)

    user2 = User.query.filter_by(email="user2@test.com").first()
    if not user2:
        user2 = User(nom="Collaborateur INSI", email="user2@test.com", 
                     mot_de_passe_hash=hash_password("user123"), role="user")
        db.session.add(user2)

    db.session.commit() # Sauvegarde pour générer les IDs utilisateurs

    # 2. Création des catégories
    cat_travail = Category.query.filter_by(nom="Travail").first()
    if not cat_travail:
        cat_travail = Category(nom="Travail", couleur="#e74c3c")
        db.session.add(cat_travail)

    cat_perso = Category.query.filter_by(nom="Personnel").first()
    if not cat_perso:
        cat_perso = Category(nom="Personnel", couleur="#2ecc71")
        db.session.add(cat_perso)

    db.session.commit()

    # 3. Création de tâches de test (avec description chiffrée via Fernet)
    if Task.query.count() == 0:
        tache1 = Task(
            titre="Finaliser l'interface Tkinter",
            description_chiffree=chiffrer_texte("Concevoir les fenêtres de formulaires et lier l'API Client."),
            priorite="haute",
            statut="en_cours",
            echeance=datetime.now().date() + timedelta(days=5),
            id_createur=user1.id,
            id_categorie=cat_travail.id
        )
        
        tache2 = Task(
            titre="Rédiger le rapport LaTeX",
            description_chiffree=chiffrer_texte("Préparer le document final d'architecture du projet de groupe."),
            priorite="moyenne",
            statut="a_faire",
            echeance=datetime.now().date() + timedelta(days=10),
            id_createur=user2.id,
            id_categorie=cat_perso.id
        )
        
        db.session.add_all([tache1, tache2])
        db.session.commit()

        # 4. Assignation de tâche (Collaboration)
        attribution = TaskAssignment(id_tache=tache1.id, id_utilisateur=user2.id)
        db.session.add(attribution)
        db.session.commit()

    print("🎉 Jeu de données complet injecté avec succès (utilisateurs, catégories, tâches chiffrées) !")