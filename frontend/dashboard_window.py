# ============================================
# Fichier réalisé par : PERSONNE 4 (P4)
# Rôle : Interface Tkinter
# But : fenêtre principale (liste des tâches, filtres, actions CRUD et attribution)
# ============================================
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from api_client import api
from task_form import TaskForm


class DashboardWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Tableau de bord - {api.utilisateur['nom']} ({api.utilisateur['role']})")
        self.geometry("900x550")

        self.taches = []

        self.construire_barre_filtres()
        self.construire_tableau()
        self.construire_boutons()
        self.charger_taches()

    # ---------- UI ----------
    def construire_barre_filtres(self):
        cadre = tk.Frame(self)
        cadre.pack(fill="x", padx=10, pady=5)

        tk.Label(cadre, text="Statut :").pack(side="left")
        self.filtre_statut = ttk.Combobox(cadre, values=["", "a_faire", "en_cours", "termine"], width=12, state="readonly")
        self.filtre_statut.pack(side="left", padx=5)

        tk.Label(cadre, text="Priorité :").pack(side="left")
        self.filtre_priorite = ttk.Combobox(cadre, values=["", "basse", "moyenne", "haute"], width=12, state="readonly")
        self.filtre_priorite.pack(side="left", padx=5)

        tk.Button(cadre, text="Filtrer", command=self.charger_taches).pack(side="left", padx=10)
        tk.Button(cadre, text="Historique", command=self.afficher_historique).pack(side="right", padx=5)
        tk.Button(cadre, text="Déconnexion", command=self.deconnexion).pack(side="right", padx=5)

    def construire_tableau(self):
        colonnes = ("id", "titre", "priorite", "statut", "echeance")
        self.tableau = ttk.Treeview(self, columns=colonnes, show="headings", height=18)
        for col in colonnes:
            self.tableau.heading(col, text=col.capitalize())
        self.tableau.column("id", width=40)
        self.tableau.pack(fill="both", expand=True, padx=10, pady=5)

    def construire_boutons(self):
        cadre = tk.Frame(self)
        cadre.pack(fill="x", padx=10, pady=5)

        tk.Button(cadre, text="Nouvelle tâche", command=self.creer_tache, bg="#2ecc71", fg="white").pack(side="left", padx=5)
        tk.Button(cadre, text="Modifier", command=self.modifier_tache).pack(side="left", padx=5)
        tk.Button(cadre, text="Supprimer", command=self.supprimer_tache, bg="#e74c3c", fg="white").pack(side="left", padx=5)
        tk.Button(cadre, text="Attribuer à...", command=self.attribuer_tache).pack(side="left", padx=5)
        tk.Button(cadre, text="Actualiser", command=self.charger_taches).pack(side="right", padx=5)

    # ---------- Logique ----------
    def charger_taches(self):
        filtres = {}
        if self.filtre_statut.get():
            filtres["statut"] = self.filtre_statut.get()
        if self.filtre_priorite.get():
            filtres["priorite"] = self.filtre_priorite.get()

        self.taches = api.get_tasks(filtres)
        self.tableau.delete(*self.tableau.get_children())
        for t in self.taches:
            self.tableau.insert("", "end", iid=str(t["id"]),
                values=(t["id"], t["titre"], t["priorite"], t["statut"], t["echeance"] or "-"))

    def _tache_selectionnee(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showinfo("Info", "Sélectionnez une tâche.")
            return None
        id_tache = int(selection[0])
        return next((t for t in self.taches if t["id"] == id_tache), None)

    def creer_tache(self):
        TaskForm(self, on_save=self.charger_taches)

    def modifier_tache(self):
        tache = self._tache_selectionnee()
        if tache:
            TaskForm(self, on_save=self.charger_taches, tache=tache)

    def supprimer_tache(self):
        tache = self._tache_selectionnee()
        if tache and messagebox.askyesno("Confirmation", f"Supprimer '{tache['titre']}' ?"):
            if api.delete_task(tache["id"]):
                self.charger_taches()
            else:
                messagebox.showerror("Erreur", "Suppression impossible (droits insuffisants ?)")

    def attribuer_tache(self):
        tache = self._tache_selectionnee()
        if not tache:
            return
        id_utilisateur = simpledialog.askinteger("Attribution", "ID de l'utilisateur cible :", parent=self)
        if id_utilisateur:
            if api.assign_task(tache["id"], id_utilisateur):
                messagebox.showinfo("Succès", "Tâche attribuée.")
                self.charger_taches()
            else:
                messagebox.showerror("Erreur", "Attribution impossible.")

    def afficher_historique(self):
        logs = api.get_activity_log()
        fenetre = tk.Toplevel(self)
        fenetre.title("Historique des activités")
        fenetre.geometry("500x400")
        zone = tk.Text(fenetre)
        zone.pack(fill="both", expand=True)
        if not logs:
            zone.insert("end", "Aucune activité enregistrée.")
        for log in logs:
            zone.insert("end", f"[{log['date']}] Action={log['action']} Tâche={log['id_tache']} Détails={log['details']}\n")

    def deconnexion(self):
        api.token = None
        api.utilisateur = None
        self.destroy()
        from login_window import LoginWindow

        def relancer():
            DashboardWindow().mainloop()

        LoginWindow(on_success=relancer).mainloop()
