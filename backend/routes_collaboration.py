from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import Task, User
from decorators import log_activity

collab_bp = Blueprint("collab", __name__)


@collab_bp.route("/tasks/<int:id_tache>/assign", methods=["POST"])
@jwt_required()
def assigner_tache(id_tache):
    id_utilisateur_courant = int(get_jwt_identity())
    claims = get_jwt()
    tache = Task.query.get_or_404(id_tache)

    
    if tache.id_createur != id_utilisateur_courant and claims.get("role") != "admin":
        return jsonify({"erreur": "Accès refusé"}), 403

    data = request.get_json()
    id_cible = data.get("id_utilisateur")

    utilisateur_cible = User.query.get(id_cible)
    if not utilisateur_cible:
        return jsonify({"erreur": "Utilisateur cible introuvable"}), 404

    if tache.id_assigne == id_cible:
        return jsonify({"erreur": "Cette tâche est déjà attribuée à cet utilisateur"}), 409

    
    tache.id_assigne = id_cible
    db.session.commit()

    log_activity(
        id_utilisateur_courant, "attribution", id_tache,
        f"Tâche attribuée à {utilisateur_cible.nom}"
    )

    return jsonify({"message": f"Tâche attribuée à {utilisateur_cible.nom}"}), 201


@collab_bp.route("/tasks/<int:id_tache>/assignees", methods=["GET"])
@jwt_required()
def liste_assignations(id_tache):
    """Renvoie l'unique assigné de la tâche (liste à 0 ou 1 élément, pour rester
    compatible avec un frontend qui attend un tableau)."""
    tache = Task.query.get_or_404(id_tache)
    if not tache.id_assigne:
        return jsonify([]), 200
    return jsonify([{
        "id_utilisateur": tache.assigne.id,
        "nom": tache.assigne.nom
    }]), 200


@collab_bp.route("/tasks/<int:id_tache>/unassign", methods=["POST"])
@jwt_required()
def retirer_assignation(id_tache):
    """Retire l'assignation en cours (utile puisqu'une seule personne à la fois)."""
    id_utilisateur_courant = int(get_jwt_identity())
    claims = get_jwt()
    tache = Task.query.get_or_404(id_tache)

    if tache.id_createur != id_utilisateur_courant and claims.get("role") != "admin":
        return jsonify({"erreur": "Accès refusé"}), 403

    tache.id_assigne = None
    db.session.commit()
    log_activity(id_utilisateur_courant, "desattribution", id_tache, "Assignation retirée")

    return jsonify({"message": "Assignation retirée"}), 200


@collab_bp.route("/activity-log", methods=["GET"])
@jwt_required()
def historique_activites():
    from models import ActivityLog
    id_utilisateur = int(get_jwt_identity())
    claims = get_jwt()

    if claims.get("role") == "admin":
        logs = ActivityLog.query.order_by(ActivityLog.date.desc()).all()
    else:
        logs = ActivityLog.query.filter_by(id_utilisateur=id_utilisateur).order_by(ActivityLog.date.desc()).all()

    return jsonify([l.to_dict() for l in logs]), 200
