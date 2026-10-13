# Architecture BiblioTK

## Vue d’ensemble

Le projet suit une architecture logicielle en 4 couches :

```text
+---------------------------+
|  Couche 4 : Interface    |
|  gui.py                  |
|  Tkinter / ttk           |
|  BiblioApp               |
+---------------------------+
             |
             v
+---------------------------+
|  Couche 3 : Métier       |
|  library.py               |
|  LibraryService          |
|  LoanError                |
|  validations + règles     |
+---------------------------+
             |
             v
+---------------------------+
|  Couche 2 : Accès données |
|  database.py             |
|  DatabaseManager         |
|  SQLite + SQL paramétré  |
+---------------------------+
             |
             v
+---------------------------+
|  Couche 1 : Persistance  |
|  schema.sql               |
|  SQLite file             |
|  bibliotk.db             |
+---------------------------+
```

## Description des modules

### 1. `main.py`
Point d’entrée de l’application.

- instancie `DatabaseManager`
- instancie `LibraryService`
- crée `BiblioApp`
- lance `mainloop()`

### 2. `gui.py`
Interface utilisateur Tkinter.

- affiche 3 onglets : Livres, Emprunts, Lecteurs
- délègue les actions à `LibraryService`
- interagit uniquement avec les méthodes métier
- affiche les erreurs utilisateur via `messagebox`

### 3. `library.py`
Cœur de la logique métier.

- valide les entrées utilisateur
- applique les règles de gestion des emprunts
- oriente les appels vers `DatabaseManager`
- lève `LoanError` dans les cas métiers

### 4. `database.py`
Couche d’accès aux données.

- ouvre les connexions SQLite
- applique `PRAGMA foreign_keys = ON`
- exécute les requêtes avec paramètres `?`
- gère les opérations de lecture, écriture et retour des emprunts

### 5. `schema.sql`
Définition du schéma SQLite.

- table `livres`
- table `lecteurs`
- table `emprunts`
- contraintes d’intégrité et index d’optimisation

## Règles d’architecture

- `gui.py` ne doit pas appeler directement `DatabaseManager`
- `library.py` est la seule couche de validation métier
- `database.py` ne contient pas de logique métier
- toutes les requêtes SQL doivent être paramétrées

## Flux de fonctionnement

1. L’utilisateur agit dans la fenêtre Tkinter.
2. La GUI appelle `LibraryService`.
3. `LibraryService` valide les données et applique les règles métier.
4. `DatabaseManager` exécute les requêtes SQLite.
5. Les résultats remontent à la GUI pour affichage.
