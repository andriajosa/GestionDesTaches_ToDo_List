from datetime import datetime
from extensions import db

class Utilisateur(db.Model) : 
    #représente la table utilisateur de la base de données
    __tablename__ = "utilisateur"
    
    #colonne de la table
    id_utilisateur = db.Column(db.Integer, primary_key = True)
    nom_utilisateur = db.Column(db.String(50), nullable = False)
    prenom_utilisateur = db.Column(db.String(80), nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)
    role = db.Column(db.String(20), nullable = False, default = "user") #rôle par défaut : user
    
    def to_dict(self) : 
        #retourne un dictionnaire représentant l'utilisateur
        return{
            "id_utilisateur" : self.id_utilisateur, 
            "nom_utilisateur" : self.nom_utilisateur, 
            "prenom_utilisateur" : self.prenom_utilisateur,
            "email" : self.email, 
            "role" : self.role
        }
        
class Categories(db.Model) : 
    #représente la table categories de la base de données
    __tablename__ = "categories"
    
    #colonne de la table
    id_categories = db.Column(db.Integer, primary_key = True)
    nom_categorie = db.Column(db.String(50), nullable = False)
    
    #foreign key vers la table utilisateur
    created_by = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"), nullable = False)
    
    def to_dict(self) : 
        #retourne un dictionnaire représentant la catégorie
        return{
            "id_categories" : self.id_categories, 
            "nom_categorie" : self.nom_categorie,
            "created_by" : self.created_by
        }
        
class Taches(db.Model) :
    #représente la table taches de la base de données
    __tablename__ = "taches"
    
    #colonne de la table
    id_taches = db.Column(db.Integer, primary_key = True)
    titre = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = True)
    
    priority = db.Column(db.Enum("basse", "moyenne", "haute"), default = "moyenne", nullable = False)
    statut =  db.Column(db.Enum("a_faire", "en_cours", "termine"), default = "a_faire")
    
    due_date = db.Column(db.Date, nullable = True) #date d'échéance de la tâche
    categorie_id = db.Column(db.Integer, db.ForeignKey("categories.id_categories"), nullable = True)
    created_by = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"), nullable = True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"), nullable = True)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    
    
    def to_dict(self, description_claire = None) : #si la description est chiffrée avant d'être envoyé, on utilise ce texte ce texte déchiffré à la place de self.description
        #retourne un dictionnaire représentant la tâche
        return{
            "id_taches" : self.id_taches, 
            "titre" : self.titre,
            "description" : description_claire if description_claire else self.description,
            "priority" : self.priority, 
            "statut" : self.statut, 
            "due_date" : self.due_date.isoformat() if self.due_date else None, #convertit l'objet de type date en chaîne de caractères
            "categorie_id" : self.categorie_id,
            "created_by" : self.created_by,
            "assigned_to" : self.assigned_to,
            "created_at" : self.created_at.isoformat() #convertit l'objet de type datetime en chaîne de caractères.
        }
        
class Historique(db.Model):
    __tablename__ = "historique"

    id_historique = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("utilisateur.id_utilisateur"), nullable=True)
    action = db.Column(db.String(255), nullable=False)  # phrase libre, ex : "a créé la tâche 'Corriger bug'"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # date/heure automatique

    def to_dict(self):
        return {
            "id_historique": self.id_historique,
            "user_id": self.user_id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


   
   
    
    
        