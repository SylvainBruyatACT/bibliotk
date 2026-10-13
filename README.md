# BiblioTK

Application de gestion de bibliothèque en Python 3.8+ avec SQLite et interface Tkinter.

## Prérequis

- Python 3.8 ou plus récent
- Module standard Python uniquement
- Tkinter installé avec l’environnement Python

## Démarrage

Pour lancer l’application :

```bash
python main.py
```

## Tests

Pour exécuter la suite de tests unitaires :

```bash
python -m unittest discover tests/ -v
```

## Structure du projet

```text
bibliotk/
├── database.py
├── gui.py
├── library.py
├── main.py
├── schema.sql
├── README.md
├── REVIEW_LOG.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── schema.md
│   └── SECURITY_REVIEW.md
├── tests/
│   └── test_library.py
└── .github/
    └── agents/
```

## Fonctionnalités

### Onglet Livres
- Ajouter un livre au catalogue avec titre, auteur, année, ISBN et nombre d’exemplaires
- Supprimer un livre sélectionné
- Rechercher un livre par mot-clé
- Visualiser les livres avec leur identifiant, auteur, année, ISBN et disponibilité

### Onglet Emprunts
- Emprunter un livre pour un lecteur donné
- Retourner un emprunt sélectionné
- Visualiser les emprunts actifs et détecter les retards en rouge

### Onglet Lecteurs
- Ajouter un lecteur avec nom, prénom et adresse email
- Consulter la liste des lecteurs enregistrés

## Architecture

Le projet suit une architecture en couches :

- `gui.py` : interface utilisateur Tkinter
- `library.py` : logique métier et validations
- `database.py` : accès SQLite et schéma
- `schema.sql` : définition des tables

## Notes

- Les requêtes SQL utilisent des paramètres `?` pour éviter les injections SQL.
- Les validations métier sont centralisées dans `LibraryService`.
- La GUI n’appelle pas directement `DatabaseManager` ; elle passe par `LibraryService`.
