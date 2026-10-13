-- Schéma SQLite 3 de BiblioTK (gestion de bibliothèque).
-- Les clés étrangères doivent être activées à chaque connexion :
--   PRAGMA foreign_keys = ON;

PRAGMA foreign_keys = ON;

-- Table des livres.
CREATE TABLE IF NOT EXISTS livres (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    titre             TEXT    NOT NULL CHECK (length(trim(titre)) > 0),
    auteur            TEXT    NOT NULL CHECK (length(trim(auteur)) > 0),
    annee             INTEGER NOT NULL CHECK (annee BETWEEN 0 AND 2100),
    isbn              TEXT    NOT NULL UNIQUE CHECK (length(trim(isbn)) > 0),
    exemplaires_total INTEGER NOT NULL DEFAULT 1 CHECK (exemplaires_total >= 0),
    exemplaires_dispo INTEGER NOT NULL DEFAULT 1 CHECK (exemplaires_dispo >= 0),
    CHECK (exemplaires_dispo <= exemplaires_total)
);

-- Table des lecteurs.
CREATE TABLE IF NOT EXISTS lecteurs (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nom    TEXT NOT NULL CHECK (length(trim(nom)) > 0),
    prenom TEXT NOT NULL CHECK (length(trim(prenom)) > 0),
    email  TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%')
);

-- Table des emprunts (dates au format ISO 8601 : AAAA-MM-JJ).
CREATE TABLE IF NOT EXISTS emprunts (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id           INTEGER NOT NULL,
    lecteur_id         INTEGER NOT NULL,
    date_emprunt       TEXT    NOT NULL,
    date_retour_prevue TEXT    NOT NULL,
    date_retour_reelle TEXT,
    FOREIGN KEY (livre_id)   REFERENCES livres (id)   ON DELETE RESTRICT,
    FOREIGN KEY (lecteur_id) REFERENCES lecteurs (id) ON DELETE RESTRICT,
    CHECK (date_retour_prevue >= date_emprunt),
    CHECK (date_retour_reelle IS NULL OR date_retour_reelle >= date_emprunt)
);

-- Index sur les clés étrangères (recherches et vérifications RESTRICT).
CREATE INDEX IF NOT EXISTS idx_emprunts_livre_id   ON emprunts (livre_id);
CREATE INDEX IF NOT EXISTS idx_emprunts_lecteur_id ON emprunts (lecteur_id);
