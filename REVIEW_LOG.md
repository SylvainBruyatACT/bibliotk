# REVIEW_LOG.md — BiblioTK Squad Agents
 
## Sprint A1 — architecte-schema-sql

### Prompt utilisé
Génère le schéma SQLite complet pour une application de gestion de bibliothèque. Entités : livres (id, titre, auteur, annee, isbn, exemplaires_total, exemplaires_dispo), lecteurs (id, nom, prenom, email), emprunts (id, livre_id, lecteur_id, date_emprunt, date_retour_prevue, date_retour_reelle). Contraintes métier : ISBN unique ; exemplaires_dispo >= 0 ; exemplaires_dispo <= exemplaires_total ; ON DELETE RESTRICT. Produis : schema.sql + docs/schema.md (diagramme ASCII + justification des contraintes).

### Évaluation de la réponse : 4/5
Points forts : 3 tables avec CREATE TABLE IF NOT EXISTS ; UNIQUE sur isbn ; CHECK dispo >= 0 et dispo <= total ; ON DELETE RESTRICT sur les 2 clés étrangères ; index sur les clés étrangères ; diagramme ASCII et justification de chaque contrainte. Vérifié en exécutant le schéma : doublon d'ISBN, stock négatif, dispo > total et suppression d'un livre ou lecteur emprunté sont bien refusés.
Points faibles : la colonne annee était facultative (NULL accepté), alors que le point de validation impose NOT NULL partout sauf date_retour_reelle. Ajouts non demandés : email UNIQUE avec un CHECK minimal, CHECK sur les dates, PRAGMA foreign_keys dans schema.sql.

### Modifications humaines apportées
1. schema.sql : annee passée en NOT NULL (CHECK annee BETWEEN 0 AND 2100 conservé) ; docs/schema.md mis à jour.
2. Revérifié : une année NULL est désormais refusée (NOT NULL constraint failed).

### Métriques
Temps avec IA : 2 min | Temps correction : 2 min | Gain estimé : 80 % (4 min au lieu des 20 min prévues)

---
## Sprint A2 — dev-acces-donnees
...
