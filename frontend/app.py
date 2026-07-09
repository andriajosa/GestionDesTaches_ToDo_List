"""
Backend de TEST pour valider l'intégration avec le frontend de PERSONNE 4.
Respecte exactement le contrat attendu par p4-frontend/api_client.py :
- POST /login {email, mot_de_passe} -> {token, utilisateur}
- POST /register {nom, email, mot_de_passe}
- GET/POST /tasks, PUT/DELETE /tasks/<id>
- GET/POST /categories
- GET /users
- POST /tasks/<id>/assign {id_utilisateur}
- GET /activity-log
"""
import datetime
import jwt as pyjwt
from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:Nike@localhost:3306/todo_p4?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SECRET_KEY = "cle_secrete_test_p4"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="membre")

    def to_dict(self):
        return {"id": self.id, "nom": self.nom, "email": self.email, "role": self.role}


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    couleur = db.Column(db.String(20), default="#3498db")

    def to_dict(self):
        return {"id": self.id, "nom": self.nom, "couleur": self.couleur}


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    priorite = db.Column(db.Enum("basse", "moyenne", "haute"), default="moyenne", nullable=False)
    statut = db.Column(db.Enum("a_faire", "en_cours", "termine"), default="a_faire", nullable=False)
    echeance = db.Column(db.Date)
    id_categorie = db.Column(db.Integer, db.ForeignKey("categories.id"))
    id_utilisateur_createur = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    id_utilisateur_assigne = db.Column(db.Integer, db.ForeignKey("users.id"))
    date_creation = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "priorite": self.priorite,
            "statut": self.statut,
            "echeance": self.echeance.isoformat() if self.echeance else None,
            "id_categorie": self.id_categorie,
            "id_utilisateur_createur": self.id_utilisateur_createur,
            "id_utilisateur_assigne": self.id_utilisateur_assigne,
        }


class ActivityLog(db.Model):
    __tablename__ = "activity_log"
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    id_tache = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    id_utilisateur = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id, "action": self.action, "details": self.details,
            "id_tache": self.id_tache, "id_utilisateur": self.id_utilisateur,
            "date": self.date.isoformat() if self.date else None,
        }


def log(action, details, id_tache, id_utilisateur):
    db.session.add(ActivityLog(action=action, details=details, id_tache=id_tache, id_utilisateur=id_utilisateur))
    db.session.commit()


def _parse_echeance(value):
    """Convertit la date attendue par le frontend (YYYY-MM-DD) vers datetime.date."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            raise ValueError("echeance invalide (attendu: YYYY-MM-DD)")
    raise ValueError("echeance invalide")


def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"erreur": "Token manquant"}), 401
        token = auth.split(" ", 1)[1]
        try:
            payload = pyjwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.id_utilisateur = payload["id"]
        except pyjwt.ExpiredSignatureError:
            return jsonify({"erreur": "Token expiré"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"erreur": "Token invalide"}), 401
        return f(*args, **kwargs)
    return wrapper


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    nom, email, mdp = data.get("nom"), data.get("email"), data.get("mot_de_passe")
    if not all([nom, email, mdp]):
        return jsonify({"erreur": "Champs requis manquants"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"erreur": "Cet email est déjà utilisé"}), 409
    hashed = bcrypt.generate_password_hash(mdp).decode("utf-8")
    user = User(nom=nom, email=email, mot_de_passe_hash=hashed, role="membre")
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email, mdp = data.get("email"), data.get("mot_de_passe")
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.mot_de_passe_hash, mdp):
        return jsonify({"erreur": "Identifiants invalides"}), 401
    token = pyjwt.encode(
        {"id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)},
        SECRET_KEY, algorithm="HS256"
    )
    return jsonify({"token": token, "utilisateur": user.to_dict()}), 200


@app.route("/tasks", methods=["GET"])
@jwt_required
def get_tasks():
    query = Task.query
    if request.args.get("statut"):
        query = query.filter_by(statut=request.args["statut"])
    if request.args.get("priorite"):
        query = query.filter_by(priorite=request.args["priorite"])
    return jsonify([t.to_dict() for t in query.all()]), 200


@app.route("/tasks", methods=["POST"])
@jwt_required
def create_task():
    data = request.get_json() or {}
    if not data.get("titre"):
        return jsonify({"erreur": "Le titre est requis"}), 400
    try:
        echeance = _parse_echeance(data.get("echeance"))
    except ValueError as e:
        return jsonify({"erreur": str(e)}), 400

    task = Task(
        titre=data["titre"], description=data.get("description"),
        priorite=data.get("priorite", "moyenne"), statut=data.get("statut", "a_faire"),
        echeance=echeance, id_categorie=data.get("id_categorie"),
        id_utilisateur_createur=request.id_utilisateur,
    )
    db.session.add(task)
    db.session.commit()
    log("creation", f"Tâche '{task.titre}' créée", task.id, request.id_utilisateur)
    return jsonify(task.to_dict()), 201


@app.route("/tasks/<int:id_tache>", methods=["PUT"])
@jwt_required
def update_task(id_tache):
    task = Task.query.get_or_404(id_tache)
    data = request.get_json() or {}
    for field in ["titre", "description", "priorite", "statut", "id_categorie"]:
        if field in data:
            setattr(task, field, data[field])

    if "echeance" in data:
        try:
            task.echeance = _parse_echeance(data.get("echeance"))
        except ValueError as e:
            return jsonify({"erreur": str(e)}), 400
    db.session.commit()
    log("modification", f"Tâche '{task.titre}' modifiée", task.id, request.id_utilisateur)
    return jsonify(task.to_dict()), 200


@app.route("/tasks/<int:id_tache>", methods=["DELETE"])
@jwt_required
def delete_task(id_tache):
    task = Task.query.get_or_404(id_tache)
    titre = task.titre
    db.session.delete(task)
    db.session.commit()
    log("suppression", f"Tâche '{titre}' supprimée", None, request.id_utilisateur)
    return jsonify({"message": "Tâche supprimée"}), 200


@app.route("/tasks/<int:id_tache>/assign", methods=["POST"])
@jwt_required
def assign_task(id_tache):
    task = Task.query.get_or_404(id_tache)
    data = request.get_json() or {}
    id_utilisateur = data.get("id_utilisateur")
    if not User.query.get(id_utilisateur):
        return jsonify({"erreur": "Utilisateur cible inexistant"}), 400
    task.id_utilisateur_assigne = id_utilisateur
    db.session.commit()
    log("attribution", f"Tâche '{task.titre}' attribuée à l'utilisateur {id_utilisateur}", task.id, request.id_utilisateur)
    return jsonify(task.to_dict()), 201


@app.route("/categories", methods=["GET"])
@jwt_required
def get_categories():
    return jsonify([c.to_dict() for c in Category.query.all()]), 200


@app.route("/categories", methods=["POST"])
@jwt_required
def create_category():
    data = request.get_json() or {}
    if not data.get("nom"):
        return jsonify({"erreur": "Le nom est requis"}), 400
    cat = Category(nom=data["nom"], couleur=data.get("couleur", "#3498db"))
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@app.route("/users", methods=["GET"])
@jwt_required
def get_users():
    return jsonify([u.to_dict() for u in User.query.all()]), 200


@app.route("/activity-log", methods=["GET"])
@jwt_required
def get_activity_log():
    logs = ActivityLog.query.order_by(ActivityLog.date.desc()).all()
    return jsonify([l.to_dict() for l in logs]), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False)
