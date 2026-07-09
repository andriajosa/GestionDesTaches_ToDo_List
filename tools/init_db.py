# tools/init_db.py
import sys
import os

# Ajouter le dossier parent au chemin de recherche pour importer le backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.app import create_app
    from backend.extensions import db
    import backend.models  # Force le chargement des modèles SQLAlchemy
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    print("Assurez-vous que le dossier 'backend' est bien au même niveau que le dossier 'tools'.")
    sys.exit(1)

app = create_app()

with app.app_context():
    print("🔄 Suppression des anciennes tables de la base de données...")
    db.drop_all()
    
    print("🏗️ Création des nouvelles tables synchronisées avec les modèles Python...")
    db.create_all()
    
    print("✅ Base de données initialisée et nettoyée avec succès !")