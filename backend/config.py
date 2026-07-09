import os
#dotenv permet de charger automatiquement des variables d'environnement depuis un fichier .env
from dotenv import load_dotenv

load_dotenv()  # Charger les variables d'environnement depuis le fichier .env

class Config : 
    #clé secrète de l'application FLASK
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    
    #clé spécifique aux tokens (JWT)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt")
    
    #adresse de la base de données : où Flask doit se connecter pour lire/écrire les données
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", 
        "mysql+pymysql://root:password@localhost/todolist"
    )
    
    #désactive une fonctionnalité qui ralentit l'application
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #durée de vie des tokens JWT (en secondes)
    JWT_ACCESS_TOKEN_EXPIRES = 3600 #après 1 heures, l'utilisateur doit se reconnecter
    
    #clé utilisé pour chiffrer et déchiffrer certaines données sensibles
    FERNET_KEY = os.getenv("FERNET_KEY")