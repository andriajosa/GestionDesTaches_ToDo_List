# ============================================
# Fichier réalisé par : PERSONNE 2 (P2)
# Rôle : Backend Tâches
# But : CRUD des tâches, catégories, priorités, statuts, filtres
# ============================================
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import Taches, Categories, Utilisateur
from security import chiffrer_texte, dechiffrer_texte
from decorators import log_activity, role_required

tasks_bp = Blueprint("tasks", __name__)

# Valeurs autorisées pour les champs à choix fermé (cohérent avec les Combobox du frontend Tkinter)
PRIORITES_VALIDES = ("basse", "moyenne", "haute")
STATUTS_VALIDES = ("a_faire", "en_cours", "termine")


# ---------- FONCTIONS UTILITAIRES ----------
def parser_echeance(valeur):
    """Convertit une chaîne 'AAAA-MM-JJ' en date, ou lève ValueError si le format est invalide."""
    if not valeur:
        return None
    return datetime.strptime(valeur, "%Y-%m-%d").date()


def utilisateur_peut_voir(tache, id_utilisateur, role):
    """Un utilisateur peut voir une tâche s'il est admin, créateur, ou assigné."""
    if role == "admin" or tache.created_by == id_utilisateur:
        return True
    return tache.assigned_to == id_utilisateur


def dechiffrer_description_ou_defaut(tache):
    """Déchiffre la description ; en cas de donnée corrompue ou de clé invalide, ne fait pas planter la requête."""
    try:
        return dechiffrer_texte(tache.description)
    except Exception:
        return None


# ---------- CATEGORIES ----------
@tasks_bp.route("/categories", methods=["GET"])
@jwt_required()
def liste_categories():
    categories = Categories.query.all()
    return jsonify([c.to_dict() for c in categories]), 200


@tasks_bp.route("/categories", methods=["POST"])
@jwt_required()
@role_required("admin")  # création de catégorie réservée aux admins (structure globale de l'app)
def creer_categorie():
    id_utilisateur = int(get_jwt_identity())
    data = request.get_json()
    nom = data.get("nom")
    if not nom:
        return jsonify({"erreur": "Le nom de la catégorie est requis"}), 400
    if Categories.query.filter_by(nom_categorie=nom).first():
        return jsonify({"erreur": "Cette catégorie existe déjà"}), 409

    categorie = Categories(nom_categorie=nom, created_by=id_utilisateur)
    db.session.add(categorie)
    db.session.commit()
    return jsonify(categorie.to_dict()), 201


# ---------- TACHES ----------
@tasks_bp.route("/tasks", methods=["POST"])
@jwt_required()
def creer_tache():
    id_utilisateur = int(get_jwt_identity())
    data = request.get_json()

    titre = data.get("titre")
    if not titre:
        return jsonify({"erreur": "Le titre est requis"}), 400

    priorite = data.get("priorite", "moyenne")
    if priorite not in PRIORITES_VALIDES:
        return jsonify({"erreur": f"Priorité invalide, valeurs possibles : {PRIORITES_VALIDES}"}), 400

    statut = data.get("statut", "a_faire")
    if statut not in STATUTS_VALIDES:
        return jsonify({"erreur": f"Statut invalide, valeurs possibles : {STATUTS_VALIDES}"}), 400

    id_categorie = data.get("id_categorie")
    if id_categorie and not Categories.query.get(id_categorie):
        return jsonify({"erreur": "Catégorie introuvable"}), 400

    assigned_to = data.get("assigned_to")
    if assigned_to and not Utilisateur.query.get(assigned_to):
        return jsonify({"erreur": "Utilisateur assigné introuvable"}), 400

    try:
        echeance_obj = parser_echeance(data.get("echeance"))
    except ValueError:
        return jsonify({"erreur": "Format d'échéance invalide, attendu AAAA-MM-JJ"}), 400

    tache = Taches(
        titre=titre,
        description=chiffrer_texte(data.get("description", "")),
        priority=priorite,
        statut=statut,
        due_date=echeance_obj,
        created_by=id_utilisateur,
        categorie_id=id_categorie,
        assigned_to=assigned_to
    )
    db.session.add(tache)
    db.session.commit()

    log_activity(id_utilisateur, "creation", tache.id_taches, f"Création de la tâche '{titre}'")

    return jsonify(tache.to_dict(description_claire=data.get("description", ""))), 201


@tasks_bp.route("/tasks", methods=["GET"])
@jwt_required()
def liste_taches():
    """Filtres possibles en query string : ?statut=...&priorite=...&id_categorie=..."""
    id_utilisateur = int(get_jwt_identity())
    claims = get_jwt()

    requete = Taches.query

    # Un utilisateur "user" ne voit que ses tâches créées OU qui lui sont assignées
    if claims.get("role") != "admin":
        requete = requete.filter(
            (Taches.created_by == id_utilisateur) | (Taches.assigned_to == id_utilisateur)
        )

    statut = request.args.get("statut")
    priorite = request.args.get("priorite")
    id_categorie = request.args.get("id_categorie")

    if statut:
        requete = requete.filter_by(statut=statut)
    if priorite:
        requete = requete.filter_by(priority=priorite)
    if id_categorie:
        requete = requete.filter_by(categorie_id=id_categorie)

    taches = requete.all()
    resultat = []
    for t in taches:
        resultat.append(t.to_dict(description_claire=dechiffrer_description_ou_defaut(t)))

    return jsonify(resultat), 200


@tasks_bp.route("/tasks/<int:id_tache>", methods=["GET"])
@jwt_required()
def obtenir_tache(id_tache):
    id_utilisateur = int(get_jwt_identity())
    claims = get_jwt()
    tache = Taches.query.get_or_404(id_tache)

    # Correctif : seul le créateur, l'assigné ou un admin peut consulter la tâche
    if not utilisateur_peut_voir(tache, id_utilisateur, claims.get("role")):
        return jsonify({"erreur": "Accès refusé"}), 403

    description_claire = dechiffrer_description_ou_defaut(tache)
    return jsonify(tache.to_dict(description_claire=description_claire)), 200


@tasks_bp.route("/tasks/<int:id_tache>", methods=["PUT"])
@jwt_required()
def modifier_tache(id_tache):
    id_utilisateur = int(get_jwt_identity())
    claims = get_jwt()
    tache = Taches.query.get_or_404(id_tache)

    # Seul le créateur ou un admin peut modifier
    if tache.created_by != id_utilisateur and claims.get("role") != "admin":
        return jsonify({"erreur": "Accès refusé"}), 403

    data = request.get_json()

    if "titre" in data:
        if not data["titre"]:
            return jsonify({"erreur": "Le titre ne peut pas être vide"}), 400
        tache.titre = data["titre"]

    if "description" in data:
        tache.description = chiffrer_texte(data["description"])

    if "priorite" in data:
        if data["priorite"] not in PRIORITES_VALIDES:
            return jsonify({"erreur": f"Priorité invalide, valeurs possibles : {PRIORITES_VALIDES}"}), 400
        tache.priority = data["priorite"]

    if "statut" in data:
        if data["statut"] not in STATUTS_VALIDES:
            return jsonify({"erreur": f"Statut invalide, valeurs possibles : {STATUTS_VALIDES}"}), 400
        tache.statut = data["statut"]

    if "echeance" in data:
        try:
            tache.due_date = parser_echeance(data["echeance"])
        except ValueError:
            return jsonify({"erreur": "Format d'échéance invalide, attendu AAAA-MM-JJ"}), 400

    if "id_categorie" in data:
        if data["id_categorie"] and not Categories.query.get(data["id_categorie"]):
            return jsonify({"erreur": "Catégorie introuvable"}), 400
        tache.categorie_id = data["id_categorie"]

    if "assigned_to" in data:
        if data["assigned_to"] and not Utilisateur.query.get(data["assigned_to"]):
            return jsonify({"erreur": "Utilisateur assigné introuvable"}), 400
        tache.assigned_to = data["assigned_to"]

    db.session.commit()
    log_activity(id_utilisateur, "modification", tache.id_taches, f"Modification de la tâche '{tache.titre}'")

    description_claire = dechiffrer_description_ou_defaut(tache)
    return jsonify(tache.to_dict(description_claire=description_claire)), 200


@tasks_bp.route("/tasks/<int:id_tache>", methods=["DELETE"])
@jwt_required()
def supprimer_tache(id_tache):
    id_utilisateur = int(get_jwt_identity())
    claims = get_jwt()
    tache = Taches.query.get_or_404(id_tache)

    if tache.created_by != id_utilisateur and claims.get("role") != "admin":
        return jsonify({"erreur": "Accès refusé"}), 403

    titre = tache.titre
    db.session.delete(tache)
    db.session.commit()

    log_activity(id_utilisateur, "suppression", id_tache, f"Suppression de la tâche '{titre}'")
    return jsonify({"message": "Tâche supprimée"}), 200
