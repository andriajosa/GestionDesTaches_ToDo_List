# ToDo_List

Frontend Tkinter pour l'authentification et la gestion des tâches.

## Fichiers principaux

- `main_app.py` : application Tkinter de connexion, inscription et gestion des tâches.
- `dashboard.py` : écran de tableau de bord (module existant).

## Lancement

1. Assure-toi que le backend tourne sur `http://localhost:5000`.
2. Lance l'application :

```bash
python main_app.py
```

## API attendue

- `POST /api/auth/login`
- `POST /api/auth/register`
- `GET /api/tasks`
- `POST /api/tasks`
- `PUT /api/tasks/<id>`
- `DELETE /api/tasks/<id>`

## Remarques

- Le token JWT est conservé en mémoire dans `ApiClient.token`.
- L'en-tête `Authorization: Bearer <token>` est ajouté automatiquement aux requêtes.
