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
from flask_jwt_extended import get_jwt, get_identity, verify_jwt_in_request
from extensions import db
from models import ActivityLog


def role_required(*roles_autorises):
    """Décorateur : bloque l'accès si le rôle de l'utilisateur n'est pas dans roles_autorises."""
    def decorateur(fonction):
        @wraps(fonction)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles_autorises:
                return jsonify({"erreur": "Accès refusé : permissions insuffisantes"}), 403
            return fonction(*args, **kwargs)
        return wrapper
    return decorateur


def log_activity(id_utilisateur, action, id_tache=None, details=None):
    """
    Enregistre une action dans l'historique des activités.
    La table SQL `historique` ne contient que (user_id, action, timestamp):
    on compose donc un texte d'action complet incluant id_tache/details.
    """

    texte_action = action 
    if id_tache is not None:
        texte_action += f" [tache_id={id_tache}]"
    if details:
        texte_action += f" — {details}"

    entree = ActivityLog(
        id_utilisateur=id_utilisateur,
        action=texte_action
    )
    db.session.add(entree)
    db.session.commit()
