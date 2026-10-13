# REVIEW_LOG.md — BiblioTK Squad Agents
 
## Sprint A1 — architecte-schema-sql

### Prompt utilisé
Génère le schéma SQLite complet pour une application de gestion de bibliothèque. Entités : livres (id, titre, auteur, annee, isbn, exemplaires_total, exemplaires_dispo), lecteurs (id, nom, prenom, email), emprunts (id, livre_id, lecteur_id, date_emprunt, date_retour_prevue, date_retour_reelle). Contraintes métier : ISBN unique ; exemplaires_dispo >= 0 ; exemplaires_dispo <= exemplaires_total ; ON DELETE RESTRICT. Produis : schema.sql + docs/schema.md (diagramme ASCII + justification des contraintes).

### Évaluation de la réponse : 4/5
Points forts : 3 tables avec CREATE TABLE IF NOT EXISTS ; UNIQUE sur isbn ; CHECK dispo >= 0 et dispo <= total ; ON DELETE RESTRICT sur les 2 clés étrangères ; index sur les clés étrangères ; diagramme ASCII et justification de chaque contrainte. Vérifié en exécutant le schéma : doublon d'ISBN, stock négatif, dispo > total et suppression d'un livre ou lecteur emprunté sont bien refusés.
Points faibles : la colonne annee était facultative (NULL accepté), alors que le point de validation impose NOT NULL partout sauf date_retour_reelle. Ajouts non demandés : email UNIQUE avec un CHECK minimal, CHECK sur les dates, PRAGMA foreign_keys dans schema.sql.

### Modifications humaines apportées
Aucune

### Métriques
Temps avec IA : 2 min | Temps correction : 2 min | Gain estimé : 80 % (4 min au lieu des 20 min prévues)

---
## Sprint A2 — dev-acces-donnees
### Prompt utilisé
Génère database.py avec la classe DatabaseManager en te basant sur schema.sql (fichier ouvert).
Constructeur : DatabaseManager(db_path="bibliotk.db")
Méthodes requises :
LIVRES : add_book, get_book (par id), get_all_books, search_books, update_book, delete_book
LECTEURS : add_reader, get_all_readers
EMPRUNTS : borrow_book (insère + décrémente dispo), return_book (met à jour + incrémente),
get_active_loans (JOIN livres + lecteurs), get_overdue_loans
Règles absolues : row_factory = sqlite3.Row, PRAGMA foreign_keys = ON,
requêtes (?, ?), context manager with conn:

### Évaluation de la réponse : 5/5
Code correct. Pas de problème de sécurité identifié

### Modifications humaines apportées
Aucune


## Sprint A3 — dev-logique-metier
### Prompt utilisé
Génère library.py avec la classe LibraryService(db_manager).
Exceptions : class LoanError(Exception) pour les erreurs métier.
Validations (@staticmethod) :
_validate_isbn : 10 ou 13 chiffres (tirets/espaces acceptés, normalisés)
_validate_year : entier entre 1000 et année courante
_validate_email : contient '@' et '.' après le @
Méthodes métier :
add_book_to_catalog(titre, auteur, annee, isbn, nb_exemplaires=1) -> int
   (ValueError si titre ou auteur vide, nb_exemplaires < 1, isbn ou année invalide)
borrow_book(livre_id, lecteur_id) -> lève LoanError si le livre est inexistant ou indisponible
return_book(emprunt_id)
search_books(query) -> db.get_all_books() si query vide, sinon db.search_books(query)
add_reader(nom, prenom, email) -> int
Méthodes de passage (la GUI ne doit jamais appeler DatabaseManager) :
get_all_books, delete_book, get_all_readers, get_active_loans, get_overdue_loans
Contrainte : zéro import externe, seulement re, datetime et database local.

### Évaluation de la réponse : 4.5/5
Instructions suivies correctement.
Tous les points de validation sont corrects.
Probablement un peu de code imparfait

### Modifications humaines apportées
Aucune

### Métriques
Temps exécution IA : 1 min


## Sprint A4 — dev-interface-tkinter

### Prompt utilisé
Génère gui.py avec la classe BiblioApp(tk.Tk) qui utilise LibraryService (voir library.py ouvert).

Structure : fenêtre 960x640, ttk.Notebook avec 3 onglets.

Onglet Livres : ttk.LabelFrame formulaire (Titre/Auteur/Année/ISBN/Exemplaires) +

   boutons Ajouter et Supprimer + barre de recherche avec trace_add + ttk.Treeview

   avec colonnes (ID/Titre/Auteur/Année/ISBN/Dispo-Total) + ttk.Scrollbar.

Onglet Emprunts : formulaire (Livre ID / Lecteur ID) + boutons Emprunter / Retourner +

   Treeview avec tag overdue (foreground rouge, bold) + Scrollbar.

Onglet Lecteurs : formulaire (Nom/Prénom/Email) + bouton Ajouter + Treeview + Scrollbar.

Méthodes refresh_books, refresh_loans, refresh_readers, refresh_all.

### Évaluation de la réponse : 5/5
Rien à redire

### Modifications humaines apportées
Aucune

### Métriques
Temps avec IA : 1 min | Temps correction : 3 min | 
Pas testable sans installer python3-tk

---