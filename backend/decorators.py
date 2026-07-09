from functools import wraps
from flask import jsonify
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