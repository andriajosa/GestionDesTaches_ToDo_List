-- Base de test compatible avec le contrat attendu par api_client.py de P4
CREATE DATABASE IF NOT EXISTS todo_p4 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE todo_p4;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(50) NOT NULL UNIQUE
);
INSERT INTO roles (role) VALUES ('admin'), ('membre');

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'membre'
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    couleur VARCHAR(20) DEFAULT '#3498db'
);

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(150) NOT NULL,
    description TEXT,
    priorite ENUM('basse','moyenne','haute') NOT NULL DEFAULT 'moyenne',
    statut ENUM('a_faire','en_cours','termine') NOT NULL DEFAULT 'a_faire',
    echeance DATE,
    id_categorie INT,
    id_utilisateur_createur INT NOT NULL,
    id_utilisateur_assigne INT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categorie) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (id_utilisateur_createur) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (id_utilisateur_assigne) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    id_tache INT,
    id_utilisateur INT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tache) REFERENCES tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES users(id) ON DELETE CASCADE
);
