# ============================================
# Fichier réalisé par : PERSONNE 4 (P4)
# Rôle : Interface Tkinter
# But : fenêtre de connexion / inscription
# ============================================
import tkinter as tk
from tkinter import messagebox
from api_client import api


class LoginWindow(tk.Tk):
    def __init__(self, on_success):
        super().__init__()
        self.title("Connexion - Gestion des Tâches")
        self.geometry("350x300")
        self.on_success = on_success

        tk.Label(self, text="Gestion des Tâches", font=("Arial", 16, "bold")).pack(pady=15)

        tk.Label(self, text="Email").pack()
        self.champ_email = tk.Entry(self, width=30)
        self.champ_email.pack(pady=5)

        tk.Label(self, text="Mot de passe").pack()
        self.champ_mdp = tk.Entry(self, width=30, show="*")
        self.champ_mdp.pack(pady=5)
        self.champ_mdp.bind("<Return>", lambda e: self.connexion())

        tk.Button(self, text="Se connecter", command=self.connexion, bg="#3498db", fg="white").pack(pady=10)
        tk.Button(self, text="Créer un compte", command=self.ouvrir_inscription).pack()

    def connexion(self):
        email = self.champ_email.get().strip()
        mot_de_passe = self.champ_mdp.get().strip()

        if not email or not mot_de_passe:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
            return

        succes, resultat = api.login(email, mot_de_passe)
        if succes:
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Erreur de connexion", str(resultat))

    def ouvrir_inscription(self):
        FenetreInscription(self)


class FenetreInscription(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Créer un compte")
        self.geometry("300x280")
        self.grab_set()  # rend la fenêtre modale (empêche de cliquer derrière)

        tk.Label(self, text="Nom").pack()
        self.champ_nom = tk.Entry(self, width=30)
        self.champ_nom.pack(pady=5)

        tk.Label(self, text="Email").pack()
        self.champ_email = tk.Entry(self, width=30)
        self.champ_email.pack(pady=5)

        tk.Label(self, text="Mot de passe").pack()
        self.champ_mdp = tk.Entry(self, width=30, show="*")
        self.champ_mdp.pack(pady=5)

        tk.Button(self, text="Créer le compte", command=self.creer, bg="#2ecc71", fg="white").pack(pady=15)

    def creer(self):
        nom = self.champ_nom.get().strip()
        email = self.champ_email.get().strip()
        mot_de_passe = self.champ_mdp.get().strip()

        if not nom or not email or not mot_de_passe:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
            return

        succes, resultat = api.register(nom, email, mot_de_passe)
        if succes:
            messagebox.showinfo("Succès", "Compte créé, vous pouvez vous connecter.")
            self.destroy()
        else:
            messagebox.showerror("Erreur", str(resultat.get("erreur", resultat) if isinstance(resultat, dict) else resultat))
