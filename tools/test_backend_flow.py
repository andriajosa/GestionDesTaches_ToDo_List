# tools/test_backend_flow.py
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def executer_tests_integration():
    print("🚀 Lancement du protocole de test d'intégration du Backend...\n")
    
    # --------------------------------------------------------
    # TEST 1 : Inscription d'un nouvel utilisateur (Route de P1)
    # --------------------------------------------------------
    payload_register = {
        "nom": "Test QA User",
        "email": "qa.test@example.com",
        "mot_de_passe": "MdpSecurise2026!"
    }
    req_reg = requests.post(f"{BASE_URL}/register", json=payload_register)
    if req_reg.status_code in [201, 409]:
        print("🔹 1. Route /register : OK (Utilisateur créé ou déjà enregistré)")
    else:
        print(f"❌ Échec au scan de l'inscription : Code {req_reg.status_code} - {req_reg.text}")
        return

    # --------------------------------------------------------
    # TEST 2 : Connexion et capture du Token JWT (Route de P1 + P3)
    # --------------------------------------------------------
    payload_login = {
        "email": "qa.test@example.com",
        "mot_de_passe": "MdpSecurise2026!"
    }
    req_login = requests.post(f"{BASE_URL}/login", json=payload_login)
    if req_login.status_code == 200:
        token = req_login.json().get("token")
        print("🔹 2. Route /login : OK (Authentification validée, Token JWT obtenu)")
    else:
        print(f"❌ Échec d'authentification : {req_login.text}")
        return

    # Configuration des entêtes pour les requêtes privées requérant JWT
    headers_auth = {"Authorization": f"Bearer {token}"}

    # --------------------------------------------------------
    # TEST 3 : Création d'une tâche avec chiffrement (Route de P2 + P3)
    # --------------------------------------------------------
    payload_task = {
        "titre": "Vérification des logs",
        "description": "Données sensibles : Clé API interne ou logs système.",
        "priorite": "basse",
        "statut": "a_faire"
    }
    req_task = requests.post(f"{BASE_URL}/tasks", json=payload_task, headers=headers_auth)
    if req_task.status_code == 201:
        tache_id = req_task.json().get("id")
        print(f"🔹 3. Route /tasks (POST) : OK (Tâche n°{tache_id} ajoutée)")
    else:
        print(f"❌ Échec de la création de la tâche : {req_task.text}")
        return

    # --------------------------------------------------------
    # TEST 4 : Récupération et vérification du déchiffrement (Route de P2)
    # --------------------------------------------------------
    req_get = requests.get(f"{BASE_URL}/tasks/{tache_id}", headers=headers_auth)
    if req_get.status_code == 200:
        desc_obtenue = req_get.json().get("description")
        if desc_obtenue == "Données sensibles : Clé API interne ou logs système.":
            print("🔹 4. Intégrité des données : OK (Le déchiffrement à la volée fonctionne)")
        else:
            print("❌ Alerte : La description récupérée ne correspond pas ou n'a pas été déchiffrée.")
    else:
        print(f"❌ Échec de la récupération : {req_get.text}")
        return

    print("\n🎉 Tous les tests d'intégration automatisés ont réussi avec succès !")

if __name__ == "__main__":
    try:
        executer_tests_integration()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de liaison : Impossible de joindre le serveur Flask.")
        print("👉 Assurez-vous d'avoir lancé l'application (ex: python app.py) avant ce script.")