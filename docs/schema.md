# Schéma de la base BiblioTK

## 1. Entités et types SQLite

| Table | Colonne | Type | Contraintes |
|-------|---------|------|-------------|
| livres | id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| livres | titre | TEXT | NOT NULL, non vide |
| livres | auteur | TEXT | NOT NULL, non vide |
| livres | annee | INTEGER | NOT NULL, entre 0 et 2100 |
| livres | isbn | TEXT | NOT NULL, UNIQUE, non vide |
| livres | exemplaires_total | INTEGER | NOT NULL, >= 0, défaut 1 |
| livres | exemplaires_dispo | INTEGER | NOT NULL, >= 0, <= exemplaires_total, défaut 1 |
| lecteurs | id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| lecteurs | nom, prenom | TEXT | NOT NULL, non vides |
| lecteurs | email | TEXT | NOT NULL, UNIQUE, forme minimale `x@y` |
| emprunts | id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| emprunts | livre_id | INTEGER | NOT NULL, FK livres(id) ON DELETE RESTRICT |
| emprunts | lecteur_id | INTEGER | NOT NULL, FK lecteurs(id) ON DELETE RESTRICT |
| emprunts | date_emprunt | TEXT (ISO 8601) | NOT NULL |
| emprunts | date_retour_prevue | TEXT (ISO 8601) | NOT NULL, >= date_emprunt |
| emprunts | date_retour_reelle | TEXT (ISO 8601) | NULL tant que le livre n'est pas rendu, sinon >= date_emprunt |

## 2. Diagramme ASCII des relations

```
+-------------+         +----------------------+         +-------------+
|   livres    |         |       emprunts       |         |  lecteurs   |
+-------------+         +----------------------+         +-------------+
| id (PK)     |1      N | id (PK)              | N      1| id (PK)     |
| titre       |<--------| livre_id (FK)        |-------->| nom         |
| auteur      |         | lecteur_id (FK)      |         | prenom      |
| annee       |         | date_emprunt         |         | email (UQ)  |
| isbn (UQ)   |         | date_retour_prevue   |         +-------------+
| exemplaires_|         | date_retour_reelle   |
|   total     |         +----------------------+
| exemplaires_|   ON DELETE RESTRICT sur les deux clés étrangères
|   dispo     |
+-------------+
```

Un livre peut avoir plusieurs emprunts, un lecteur aussi. `emprunts` est la
table d'association (relation plusieurs-à-plusieurs entre livres et lecteurs).

## 3. Justification des contraintes

- **PRIMARY KEY AUTOINCREMENT** : identifiants jamais réutilisés après
  suppression, ce qui évite de confondre un ancien et un nouvel enregistrement.
- **isbn UNIQUE** : un ISBN identifie une édition ; un doublon serait une
  erreur de saisie. Plusieurs exemplaires d'un même livre se gèrent avec
  `exemplaires_total`, pas avec plusieurs lignes.
- **exemplaires_dispo >= 0** : on ne peut pas prêter plus d'exemplaires qu'il
  n'y en a ; un stock négatif signalerait un bug de la logique métier.
- **exemplaires_dispo <= exemplaires_total** : le disponible ne peut dépasser
  le stock (par exemple après un retour enregistré deux fois). Contrainte
  au niveau de la table, car elle compare deux colonnes.
- **exemplaires_total >= 0** : cohérence du stock.
- **ON DELETE RESTRICT** (livre_id, lecteur_id) : on ne supprime ni un livre
  ni un lecteur référencé par un emprunt, afin de conserver l'historique.
  Nécessite `PRAGMA foreign_keys = ON` à chaque connexion (désactivé par
  défaut dans SQLite) ; `database.py` devra l'exécuter.
- **NOT NULL sur livre_id, lecteur_id, date_emprunt, date_retour_prevue** :
  un emprunt sans livre, lecteur ou dates n'a pas de sens.
- **date_retour_reelle nullable** : NULL signifie « emprunt en cours ».
- **CHECK sur les dates** : le retour ne peut précéder l'emprunt. Le format
  ISO 8601 (AAAA-MM-JJ) rend la comparaison de textes chronologiquement correcte.
- **email UNIQUE** : un lecteur par adresse, évite les doublons de compte.
  Le CHECK `LIKE '%_@_%'` n'est qu'un garde-fou minimal ; la validation
  complète relève de `library.py`.
- **CHECK non vide (trim)** : refuse les chaînes vides ou d'espaces.
- **Index sur emprunts(livre_id) et emprunts(lecteur_id)** : accélèrent les
  recherches par livre ou lecteur et les vérifications RESTRICT.

## 4. Remarque

Aucun ORM : le schéma est du SQL SQLite 3 pur, appliqué par `database.py`.
