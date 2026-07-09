from flask import Flask
from config import Config
from extensions import db, jwt

# On importe les "Blueprints" (groupes de routes) créés par chaque personne
from routes_auth import auth_bp
from routes_tasks import tasks_bp
from routes_collaboration import collab_bp


def create_app():

    app = Flask(__name__)

    # Charge tous les réglages définis dans config.py
    app.config.from_object(Config)

    # Branche les outils "db" et "jwt" sur cette application précise
    db.init_app(app)
    jwt.init_app(app)

    # Assemble les routes de chaque personne dans une seule application
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(collab_bp)


# Ce bloc ne s'exécute que si on lance CE fichier directement (python app.py)
# et pas si ce fichier est juste importé ailleurs
if __name__ == "__main__":
    app = create_app()
    # debug=True : affiche les erreurs détaillées pendant le développement
    # port=5000 : le serveur écoute sur http://127.0.0.1:5000
    app.run(debug=True, port=5000)