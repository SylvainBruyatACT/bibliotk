# Instructions communes : projet BiblioTK

 

Application de gestion de bibliothèque en Python 3.8+ standard :

sqlite3 + tkinter/ttk + unittest. Aucune dépendance externe (pas de pip install).

 

## Architecture en couches (ne jamais la contourner)

gui.py -> library.py -> database.py -> SQLite (schema.sql)

Chaque couche appelle uniquement celle du dessous.

 

## Conventions

- Noms de tables et de colonnes en français (livres, lecteurs, emprunts)

- Commentaires, docstrings (format Google) et messages en français

- Code conforme PEP 8 : snake_case pour les fonctions, PascalCase pour les classes

- Aucune requête SQL construite avec une f-string : paramètres (?, ?) uniquement

- Aucun livrable généré par l'IA n'est commité sans relecture humaine