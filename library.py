"""Règles métier et services de gestion de la bibliothèque BiblioTK."""

from datetime import date, timedelta
import re

import database


class LoanError(Exception):
    """Erreur levée lorsqu'une opération d'emprunt ne respecte pas les règles."""


class LibraryService:
    """Applique les règles métier et délègue les données à DatabaseManager."""

    def __init__(self, db_manager: database.DatabaseManager) -> None:
        """Initialise le service avec son gestionnaire de base de données.

        Args:
            db_manager: Gestionnaire utilisé pour toutes les opérations de données.
        """
        self.db_manager = db_manager

    @staticmethod
    def _validate_isbn(isbn: str) -> str:
        """Normalise et valide un ISBN de 10 ou 13 chiffres.

        Les tirets et espaces sont supprimés avant la validation.

        Args:
            isbn: ISBN à valider.

        Returns:
            L'ISBN normalisé, sans tirets ni espaces.

        Raises:
            ValueError: Si l'ISBN n'est pas composé de 10 ou 13 chiffres.
        """
        if not isinstance(isbn, str):
            raise ValueError("L'ISBN doit être une chaîne de caractères.")

        isbn_normalise = re.sub(r"[-\s]", "", isbn)
        if re.fullmatch(r"(?:[0-9]{10}|[0-9]{13})", isbn_normalise) is None:
            raise ValueError("L'ISBN doit contenir 10 ou 13 chiffres.")
        return isbn_normalise

    @staticmethod
    def _validate_year(annee: int) -> int:
        """Vérifie qu'une année est un entier compris entre 1000 et aujourd'hui.

        Args:
            annee: Année de publication à vérifier.

        Returns:
            L'année validée.

        Raises:
            ValueError: Si l'année n'est pas un entier dans l'intervalle autorisé.
        """
        if (
            isinstance(annee, bool)
            or not isinstance(annee, int)
            or not 1000 <= annee <= date.today().year
        ):
            raise ValueError(
                "L'année doit être un entier compris entre 1000 et l'année actuelle."
            )
        return annee

    @staticmethod
    def _validate_email(email: str) -> str:
        """Vérifie qu'une adresse contient un arobase et un point après celui-ci.

        Args:
            email: Adresse électronique à vérifier.

        Returns:
            L'adresse électronique débarrassée des espaces périphériques.

        Raises:
            ValueError: Si l'adresse ne respecte pas le format minimal attendu.
        """
        if not isinstance(email, str):
            raise ValueError("L'adresse e-mail doit être une chaîne de caractères.")

        email_normalise = email.strip()
        position_arobase = email_normalise.find("@")
        if (
            position_arobase < 0
            or "." not in email_normalise[position_arobase + 1 :]
        ):
            raise ValueError(
                "L'adresse e-mail doit contenir un '@' et un point après celui-ci."
            )
        return email_normalise

    def add_book_to_catalog(
        self,
        titre: str,
        auteur: str,
        annee: int,
        isbn: str,
        nb_exemplaires: int = 1,
    ) -> int:
        """Valide puis ajoute un livre au catalogue.

        Args:
            titre: Titre du livre.
            auteur: Auteur du livre.
            annee: Année de publication.
            isbn: ISBN du livre.
            nb_exemplaires: Nombre d'exemplaires à ajouter.

        Returns:
            L'identifiant attribué au livre.

        Raises:
            ValueError: Si le titre, l'auteur, l'année, l'ISBN ou le nombre
                d'exemplaires est invalide.
        """
        if not isinstance(titre, str) or not titre.strip():
            raise ValueError("Le titre du livre ne peut pas être vide.")
        if not isinstance(auteur, str) or not auteur.strip():
            raise ValueError("L'auteur du livre ne peut pas être vide.")
        if (
            isinstance(nb_exemplaires, bool)
            or not isinstance(nb_exemplaires, int)
            or nb_exemplaires < 1
        ):
            raise ValueError("Le nombre d'exemplaires doit être un entier positif.")

        annee_validee = self._validate_year(annee)
        isbn_normalise = self._validate_isbn(isbn)
        return self.db_manager.add_book(
            titre.strip(),
            auteur.strip(),
            annee_validee,
            isbn_normalise,
            nb_exemplaires,
        )

    def borrow_book(self, livre_id: int, lecteur_id: int) -> int:
        """Emprunte un exemplaire disponible d'un livre existant.

        Args:
            livre_id: Identifiant du livre.
            lecteur_id: Identifiant du lecteur.

        Returns:
            L'identifiant attribué à l'emprunt.

        Raises:
            LoanError: Si le livre n'existe pas ou n'a aucun exemplaire disponible.
        """
        livre = self.db_manager.get_book(livre_id)
        if livre is None:
            raise LoanError("Le livre demandé n'existe pas.")
        if livre["exemplaires_dispo"] < 1:
            raise LoanError("Aucun exemplaire de ce livre n'est disponible.")

        date_emprunt = date.today()
        date_retour_prevue = date_emprunt + timedelta(days=14)
        return self.db_manager.borrow_book(
            livre_id,
            lecteur_id,
            date_emprunt.isoformat(),
            date_retour_prevue.isoformat(),
        )

    def return_book(self, emprunt_id: int) -> bool:
        """Enregistre le retour d'un emprunt.

        Args:
            emprunt_id: Identifiant de l'emprunt à clôturer.

        Returns:
            True si le retour a été enregistré.
        """
        return self.db_manager.return_book(emprunt_id)

    def search_books(self, query: str):
        """Recherche les livres ou retourne tout le catalogue si la requête est vide.

        Args:
            query: Texte recherché dans le catalogue.

        Returns:
            Les livres correspondants, ou tous les livres si la requête est vide.
        """
        if not query or not query.strip():
            return self.db_manager.get_all_books()
        return self.db_manager.search_books(query.strip())

    def add_reader(self, nom: str, prenom: str, email: str) -> int:
        """Valide puis ajoute un lecteur.

        Args:
            nom: Nom du lecteur.
            prenom: Prénom du lecteur.
            email: Adresse électronique du lecteur.

        Returns:
            L'identifiant attribué au lecteur.

        Raises:
            ValueError: Si le nom, le prénom ou l'adresse e-mail est invalide.
        """
        if not isinstance(nom, str) or not nom.strip():
            raise ValueError("Le nom du lecteur ne peut pas être vide.")
        if not isinstance(prenom, str) or not prenom.strip():
            raise ValueError("Le prénom du lecteur ne peut pas être vide.")

        email_valide = self._validate_email(email)
        return self.db_manager.add_reader(nom.strip(), prenom.strip(), email_valide)

    def get_all_books(self):
        """Retourne tous les livres du catalogue."""
        return self.db_manager.get_all_books()

    def delete_book(self, livre_id: int) -> bool:
        """Supprime un livre du catalogue.

        Args:
            livre_id: Identifiant du livre à supprimer.

        Returns:
            True si le livre a été supprimé.
        """
        return self.db_manager.delete_book(livre_id)

    def get_all_readers(self):
        """Retourne tous les lecteurs."""
        return self.db_manager.get_all_readers()

    def get_active_loans(self):
        """Retourne les emprunts encore en cours."""
        return self.db_manager.get_active_loans()

    def get_overdue_loans(self):
        """Retourne les emprunts en retard."""
        return self.db_manager.get_overdue_loans()