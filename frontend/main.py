# ============================================
# Fichier réalisé par : PERSONNE 4 (P4)
# Rôle : Interface Tkinter
# But : point d'entrée de l'application Tkinter
# ============================================
from login_window import LoginWindow
from dashboard_window import DashboardWindow


def lancer_dashboard():
    DashboardWindow().mainloop()


if __name__ == "__main__":
    LoginWindow(on_success=lancer_dashboard).mainloop()
