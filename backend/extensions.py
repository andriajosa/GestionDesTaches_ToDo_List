#créer des outils utilisés par tout le monde dans le projet

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

#db est l'outil qui permet de gérer la base de données
db = SQLAlchemy()

jwt = JWTManager()

