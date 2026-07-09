# ============================================
# Fichier réalisé par : PERSONNE 4 (P4)
# Rôle : Interface Tkinter
# But : formulaire de création / modification d'une tâche
# ============================================
import tkinter as tk
from tkinter import ttk, messagebox
from api_client import api


class TaskForm(tk.Toplevel):
    def __init__(self, parent, on_save, tache=None):
        super().__init__(parent)
        self.on_save = on_save
        self.tache = tache  # None = création, sinon = modification
        self.title("Modifier la tâche" if tache else "Nouvelle tâche")
        self.geometry("350x460")
        self.grab_set()

        tk.Label(self, text="Titre").pack()
        self.champ_titre = tk.Entry(self, width=35)
        self.champ_titre.pack(pady=3)

        tk.Label(self, text="Description").pack()
        self.champ_description = tk.Text(self, width=35, height=5)
        self.champ_description.pack(pady=3)

        tk.Label(self, text="Priorité").pack()
        self.combo_priorite = ttk.Combobox(self, values=["basse", "moyenne", "haute"], state="readonly")
        self.combo_priorite.set("moyenne")
        self.combo_priorite.pack(pady=3)

        tk.Label(self, text="Statut").pack()
        self.combo_statut = ttk.Combobox(self, values=["a_faire", "en_cours", "termine"], state="readonly")
        self.combo_statut.set("a_faire")
        self.combo_statut.pack(pady=3)

        tk.Label(self, text="Échéance (AAAA-MM-JJ)").pack()
        self.champ_echeance = tk.Entry(self, width=20)
        self.champ_echeance.pack(pady=3)

        tk.Label(self, text="Catégorie (id, optionnel)").pack()
        self.champ_categorie = tk.Entry(self, width=10)
        self.champ_categorie.pack(pady=3)

        if tache:
            self.champ_titre.insert(0, tache.get("titre", ""))
            self.champ_description.insert("1.0", tache.get("description", "") or "")
            self.combo_priorite.set(tache.get("priorite", "moyenne"))
            self.combo_statut.set(tache.get("statut", "a_faire"))
            if tache.get("echeance"):
                self.champ_echeance.insert(0, tache["echeance"])
            if tache.get("id_categorie"):
                self.champ_categorie.insert(0, str(tache["id_categorie"]))

        tk.Button(self, text="Enregistrer", command=self.enregistrer, bg="#3498db", fg="white").pack(pady=15)

    def enregistrer(self):
        titre = self.champ_titre.get().strip()
        if not titre:
            messagebox.showwarning("Champ manquant", "Le titre est obligatoire.")
            return

        echeance = self.champ_echeance.get().strip()
        if echeance:
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", echeance):
                messagebox.showwarning("Format invalide", "L'échéance doit être au format AAAA-MM-JJ.")
                return

        donnees = {
            "titre": titre,
            "description": self.champ_description.get("1.0", tk.END).strip(),
            "priorite": self.combo_priorite.get(),
            "statut": self.combo_statut.get(),
            "echeance": echeance or None,
        }
        id_categorie = self.champ_categorie.get().strip()
        if id_categorie:
            if not id_categorie.isdigit():
                messagebox.showwarning("Champ invalide", "L'id de catégorie doit être un nombre.")
                return
            donnees["id_categorie"] = int(id_categorie)

        if self.tache:
            succes, resultat = api.update_task(self.tache["id"], donnees)
        else:
            succes, resultat = api.create_task(donnees)

        if succes:
            self.destroy()
            self.on_save()
        else:
            erreur = resultat.get("erreur", resultat) if isinstance(resultat, dict) else resultat
            messagebox.showerror("Erreur", str(erreur))
