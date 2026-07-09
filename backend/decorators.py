from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models import Historique


def role_required(role_name):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != role_name:
                return jsonify({"erreur": "Accès refusé"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def log_activity(user_id, action, target_id=None, message=None):
    """Enregistre une entrée basique dans la table Historique si disponible.
    Ne doit pas lever d'exception si Historique ou db ne sont pas présents.
    """
    try:
        entree = Historique(user_id=user_id, action=f"{action} - {message or ''}")
        db.session.add(entree)
        db.session.commit()
    except Exception:
        # silencieux : journal interne non critique pour le fonctionnement de l'API
        pass
