# TODO - Sync frontend/backend/database

## Plan de correction (à valider)
1. Vérifier le rôle de `frontend/app.py` : actuellement c’est un **backend Flask** (routes/login/tasks/...).
2. Vérifier le point d’entrée réellement utilisé par l’interface Tkinter (`frontend/main.py`).
3. Définir clairement deux exécutables :
   - backend: `python p4-backend-test/app.py` (ou un backend unique)
   - frontend: `python frontend/main.py`
4. Corriger si le frontend n’appelle pas le bon backend (URL/port) ou si des champs JSON ne correspondent pas.
5. Ajouter un mécanisme de “synchronisation” :
   - même noms de champs (mot_de_passe, etc.)
   - même structure JSON tasks/categories/users
6. Tester manuellement :
   - POST /register puis POST /login
   - GET /tasks
   - POST /tasks puis PUT/DELETE
7. (Optionnel) Nettoyage : supprimer/renommer les fichiers qui mélangent backend et frontend si nécessaire.

