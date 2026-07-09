from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import Taches, Utilisateur, Historique
from decorators import role_required, log_activity

collab_bp = Blueprint("collaboration", __name__)


@collab_bp.route("/collaboration/assign", methods=["POST"])
@jwt_required()
def assigner_utilisateur():
    """Assigne un utilisateur à une tâche. Seul le créateur ou un admin peut le faire."""
    id_actioneur = int(get_jwt_identity())
    claims = get_jwt()
    data = request.get_json() or {}
    id_tache = data.get("id_tache")
    user_id = data.get("user_id")

    if not id_tache or not user_id:
        return jsonify({"erreur": "id_tache et user_id requis"}), 400

    tache = Taches.query.get_or_404(id_tache)
    if not Utilisateur.query.get(user_id):
        return jsonify({"erreur": "Utilisateur introuvable"}), 400

    if claims.get("role") != "admin" and tache.created_by != id_actioneur:
        return jsonify({"erreur": "Accès refusé"}), 403

    tache.assigned_to = user_id
    db.session.commit()

    # journaliser
    log_activity(id_actioneur, "assignation", tache.id_taches, f"Assignation de l'utilisateur {user_id} à la tâche {tache.id_taches}")

    return jsonify(tache.to_dict()), 200


@collab_bp.route("/collaboration/tasks/<int:id_tache>/assign", methods=["DELETE"])
@jwt_required()
def retirer_assignment(id_tache):
    """Retire l'assignation d'une tâche (set assigned_to à None)."""
    id_actioneur = int(get_jwt_identity())
    claims = get_jwt()

    tache = Taches.query.get_or_404(id_tache)
    if claims.get("role") != "admin" and tache.created_by != id_actioneur:
        return jsonify({"erreur": "Accès refusé"}), 403

    tache.assigned_to = None
    db.session.commit()

    log_activity(id_actioneur, "desassignation", id_tache, f"Retrait de l'assignation de la tâche {id_tache}")
    return jsonify({"message": "Assignation retirée"}), 200


@collab_bp.route("/collaboration/tasks/<int:id_tache>/collaborator", methods=["GET"])
@jwt_required()
def get_collaborator(id_tache):
    """Renvoie l'utilisateur assigné à la tâche (si présent)."""
    tache = Taches.query.get_or_404(id_tache)
    if not tache.assigned_to:
        return jsonify({}), 204

    user = Utilisateur.query.get(tache.assigned_to)
    if not user:
        return jsonify({}), 404
    return jsonify(user.to_dict()), 200


@collab_bp.route("/collaboration/comment", methods=["POST"])
@jwt_required()
def ajouter_commentaire():
    """Ajoute un commentaire lié à une tâche dans le journal d'historique."""
    id_actioneur = int(get_jwt_identity())
    data = request.get_json() or {}
    id_tache = data.get("id_tache")
    commentaire = data.get("commentaire")

    if not id_tache or not commentaire:
        return jsonify({"erreur": "id_tache et commentaire requis"}), 400

    # garde une trace simple dans la table `historique`
    entree = Historique(user_id=id_actioneur, action=f"Commentaire sur tâche {id_tache}: {commentaire}")
    db.session.add(entree)
    db.session.commit()

    log_activity(id_actioneur, "commentaire", id_tache, f"Commentaire ajouté sur la tâche {id_tache}")

    return jsonify({"id": entree.id_historique, "user_id": entree.user_id, "action": entree.action}), 201
