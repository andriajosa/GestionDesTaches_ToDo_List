import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 10  # secondes


class ApiClient:
    def __init__(self):
        self.token = None
        self.utilisateur = None

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _safe_json(self, r):
        try:
            return r.json()
        except ValueError:
            return {}

    def login(self, email, mot_de_passe):
        try:
            r = requests.post(f"{BASE_URL}/login",
                json={"email": email, "mot_de_passe": mot_de_passe},
                timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return False, "Impossible de contacter le serveur. Le backend Flask est-il lancé ?"
        except requests.exceptions.Timeout:
            return False, "Le serveur ne répond pas (timeout)."

        data = self._safe_json(r)
        if r.status_code == 200:
            self.token = data["token"]
            self.utilisateur = data["utilisateur"]
            return True, data
        return False, data.get("erreur", "Erreur inconnue")

    def register(self, nom, email, mot_de_passe):
        try:
            r = requests.post(f"{BASE_URL}/register", json={
                "nom": nom, "email": email, "mot_de_passe": mot_de_passe
            }, timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return False, {"erreur": "Impossible de contacter le serveur."}
        return r.status_code == 201, self._safe_json(r)

    def get_tasks(self, filtres=None):
        try:
            r = requests.get(f"{BASE_URL}/tasks", headers=self._headers(),
                params=filtres or {}, timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return []
        return self._safe_json(r) if r.status_code == 200 else []

    def create_task(self, data):
        try:
            r = requests.post(f"{BASE_URL}/tasks", json=data, headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return False, {"erreur": "Impossible de contacter le serveur."}
        return r.status_code == 201, self._safe_json(r)

    def update_task(self, id_tache, data):
        try:
            r = requests.put(f"{BASE_URL}/tasks/{id_tache}", json=data, headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return False, {"erreur": "Impossible de contacter le serveur."}
        return r.status_code == 200, self._safe_json(r)

    def delete_task(self, id_tache):
        try:
            r = requests.delete(f"{BASE_URL}/tasks/{id_tache}", headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return False
        return r.status_code == 200

    def get_categories(self):
        try:
            r = requests.get(f"{BASE_URL}/categories", headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return []
        return self._safe_json(r) if r.status_code == 200 else []

    def create_category(self, nom, couleur="#3498db"):
        try:
            r = requests.post(f"{BASE_URL}/categories", json={"nom": nom, "couleur": couleur},
                headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return False
        return r.status_code == 201

    def get_users(self):
        try:
            r = requests.get(f"{BASE_URL}/users", headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return []
        return self._safe_json(r) if r.status_code == 200 else []

    def assign_task(self, id_tache, id_utilisateur):
        try:
            r = requests.post(f"{BASE_URL}/tasks/{id_tache}/assign",
                json={"id_utilisateur": id_utilisateur}, headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return False
        return r.status_code == 201

    def get_activity_log(self):
        try:
            r = requests.get(f"{BASE_URL}/activity-log", headers=self._headers(), timeout=TIMEOUT)
        except requests.exceptions.ConnectionError:
            return []
        return self._safe_json(r) if r.status_code == 200 else []


api = ApiClient()
