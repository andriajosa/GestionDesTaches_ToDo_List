from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from extensions import db
from models import Utilisateur
from security import hash_password, verifier_password
from decorators import role_required, log_activity

#un blueprint regroupe un ensemble de routes
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", method = ["POST"])
def register() : 
    #récupère les données envoyées par Tkinter
    data = request.get_json()
    nom = data.get("nom_utilisateur")
    prenom = data.get("prenom_utilisateur")
    email = data.get("email")
    mot_de_passe = data.get("mot_de_passe")
    
    #vérification : tous les champs sont rempli
    if not nom or not prenom or not email or not mot_de_passe : 
        return jsonify({"erreur" : "Nom, prénom, email et mot de passe de l'utilisateur sont requis"}), 400
    
    #vérification : est ce que cet email est déjà utilisé
    if Utilisateur.query.filter_by(email=email).first() :
        return jsonify({"erreur" : "Cet email est déjà utilisé"}), 409
    
    #création du nouvel utilisateur en mémoire
    nouvel_utilisateur = Utilisateur(
        nom_utilisateur = nom,
        prenom_utilisateur = prenom,
        email = email,
        #hash_password() brouille le mot de passe avant de le stocker
        password_hash = hash_password(mot_de_passe), 
        role = "user" #tout nouveau compte doit être en mode user
    )
    
    #envoie les données vers mysql
    db.session.add(nouvel_utilisateur) #prépare  l'ajout
    db.session.commit()
    
    #renvoie la fiche du nouvel utilisateur avec le code 201
    return jsonify(nouvel_utilisateur.to_dict()), 201

@auth_bp.route("/login", methods=["POST"])
def login() : 
    data = request.get_json()
    email = data.get("email")
    mot_de_passe = data.get("mot_de_passe")
    
    #chercher l'utilisateur correspondant à l'email dans la BDD
    utilisateur = Utilisateur.query.filter_by(email=email).first()
    
    #vérifie si l'utilisateur exite et le mot de passe correspond au mot de passe brouillé
    if not utilisateur or not verifier_password(mot_de_passe, utilisateur.password_hash):
        # Si l'une des deux conditions échoue -> refus, avec code 401 = "Non autorisé"
        return jsonify({"erreur": "Email ou mot de passe incorrect"}), 401
    
    token = create_access_token(
        identity=str(utilisateur.id_utilisateur), #qui est connecté
        additional_claims={
            "role" : utilisateur.role,
            "nom" : utilisateur.nom_utilisateur
        }
    )
    
    # On renvoie le ticket + les infos de l'utilisateur (utile pour afficher son nom dans Tkinter)
    return jsonify({
        "token": token,
        "utilisateur": utilisateur.to_dict()
    }), 200
    
@auth_bp.route("/users", methods=["GET"])
@role_required("admin")   # <-- seuls les utilisateurs avec le rôle "admin" peuvent utiliser cette route
def liste_utilisateurs():
    """Renvoie la liste de TOUS les utilisateurs. Réservé aux admins."""
    utilisateurs = Utilisateur.query.all()
    # Transforme chaque utilisateur en dictionnaire, dans une liste
    return jsonify([u.to_dict() for u in utilisateurs]), 200


@auth_bp.route("/users/<int:id_utilisateur>/role", methods=["PUT"])
@role_required("admin")
def modifier_role(id_utilisateur):
    """Permet à un admin de promouvoir/rétrograder un utilisateur (user <-> admin)."""
    data = request.get_json()
    nouveau_role = data.get("role")

    # On n'accepte que deux valeurs possibles pour éviter les erreurs
    if nouveau_role not in ("admin", "user"):
        return jsonify({"erreur": "Rôle invalide"}), 400

    # get_or_404 : cherche l'utilisateur, et renvoie automatiquement une erreur 404
    # ("introuvable") s'il n'existe pas -> évite d'avoir à vérifier nous-même
    utilisateur = Utilisateur.query.get_or_404(id_utilisateur)
    utilisateur.role = nouveau_role
    # sauvegarde le changement dans MySQL
    db.session.commit()

    return jsonify(utilisateur.to_dict()), 200