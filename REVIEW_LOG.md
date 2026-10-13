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

## Sprint A5 — testeur-unitaire

### Prompt utilisé
Génère tests/test_library.py pour LibraryService (voir library.py ouvert).

Structure : 5 classes TestCase.

TestAddBook (7 tests) : nominal, isbn invalide, isbn 10 chiffres, isbn tirets normalisés,

   année future, exemplaires=0, titre vide.

TestBorrowBook (3 tests) : livre dispo, livre 0 copie (LoanError), livre inexistant (LoanError).

TestReturnBook (1 test) : appel db.return_book.

TestSearchBooks (2 tests) : query vide => get_all_books, query non vide => search_books.

TestValidations (7 tests) : email valide, sans @, sans point, isbn 12 chiffres,

   isbn lettres, année 0, année 1000.

Règles : setUp avec MagicMock(), pattern ARRANGE/ACT/ASSERT, nommage test_{methode}_{scenario}_{attendu}.

### Évaluation de la réponse : 5/5
Tests bien structurés, 20 cas couvrant le nominal, les limites et les erreurs. Les mocks sont correctement vérifiés. L’exécution confirmée : `python3 -m unittest discover tests/ -v` passe.

### Modifications humaines apportées
Correctif de compatibilité Python 3.8 dans database.py (annotations type Python 3.10 supprimées).

### Métriques
Temps avec IA : 3 min | Temps correction : 10 min | Gain estimé : 70 %

---

## Sprint A6 — auditeur-securite

### Prompt utilisé
Effectue un audit de sécurité et qualité complet du projet BiblioTK.
Vérifie les 5 catégories suivantes et produis docs/SECURITY_REVIEW.md :
1. SÉCURITÉ SQL : y a-t-il des f-strings dans les requêtes de database.py ?
2. VALIDATIONS : toutes les entrées utilisateur passent-elles par LibraryService ?
3. EXCEPTIONS GUI : chaque callback dans gui.py a-t-il un try/except + messagebox ?
4. QUALITÉ DU CODE : toutes les méthodes publiques ont-elles une docstring ?
5. ARCHITECTURE : gui.py appelle-t-il DatabaseManager directement quelque part ?
Pour chaque problème : fichier, numéro de ligne approximatif, sévérité, code corrigé.

### Évaluation de la réponse : 5/5
Audit complet et explicite. Les points de conformité sont vérifiés sur le code réel. Le document produit est bien structuré et trace les observations avec niveau de sévérité et correctifs.

### Modifications humaines apportées
Aucune correction de code fonctionnelle, seulement ajout du document de revue.

### Métriques
Temps avec IA : 2 min | Temps validation : 4 min

---

## Sprint A7 — integrateur-livraison

### Prompt utilisé
Génère les fichiers d’intégration finale du projet BiblioTK.
1. main.py : importe DatabaseManager / LibraryService / BiblioApp,
   def main() avec try/except complet, if __name__ == '__main__': main()
2. README.md : titre, prérequis Python 3.8+, démarrage (python main.py),
   tests (python -m unittest discover tests/ -v), structure du projet en arbre,
   fonctionnalités des 3 onglets
3. docs/ARCHITECTURE.md : schéma ASCII en 4 couches avec flèches, description de chaque module
4. REVIEW_LOG.md : complète le tableau de synthèse des 7 sprints (agent / prompt / évaluation / modifications)

### Évaluation de la réponse : 5/5
Tous les livrables attendus ont été générés. L’application démarre via `python main.py` et la suite de tests passe.

### Modifications humaines apportées
Ajustement du point d’entrée et ajout du fichier de documentation finale.

### Métriques
Temps avec IA : 5 min | Temps validation : 10 min | Gain estimé : 75 %

---