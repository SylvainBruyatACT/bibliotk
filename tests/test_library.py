"""Tests unitaires pour la logique métier de BiblioTK."""

import unittest
from unittest.mock import MagicMock

from library import LibraryService, LoanError


class TestAddBook(unittest.TestCase):
    """Tests de la méthode add_book_to_catalog."""

    def setUp(self):
        self.db = MagicMock()
        self.svc = LibraryService(self.db)

    def test_add_book_to_catalog_nominal(self):
        # Arrange
        self.db.add_book.return_value = 42

        # Act
        result = self.svc.add_book_to_catalog(
            titre="Dune",
            auteur="Frank Herbert",
            annee=1965,
            isbn="978-2-1234-5678-9",
            nb_exemplaires=3,
        )

        # Assert
        self.assertEqual(result, 42)
        self.db.add_book.assert_called_once_with(
            "Dune",
            "Frank Herbert",
            1965,
            "9782123456789",
            3,
        )

    def test_add_book_to_catalog_isbn_invalide_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc.add_book_to_catalog(
                titre="Dune",
                auteur="Frank Herbert",
                annee=1965,
                isbn="ABC",
                nb_exemplaires=1,
            )

        # Assert
        self.assertIn("ISBN", str(ctx.exception))
        self.db.add_book.assert_not_called()

    def test_add_book_to_catalog_isbn_10_chiffres(self):
        # Arrange
        self.db.add_book.return_value = 7

        # Act
        result = self.svc.add_book_to_catalog(
            titre="Le Hobbit",
            auteur="J.R.R. Tolkien",
            annee=1937,
            isbn="1234567890",
            nb_exemplaires=2,
        )

        # Assert
        self.assertEqual(result, 7)
        self.db.add_book.assert_called_once_with(
            "Le Hobbit",
            "J.R.R. Tolkien",
            1937,
            "1234567890",
            2,
        )

    def test_add_book_to_catalog_isbn_tirets_normalises(self):
        # Arrange
        self.db.add_book.return_value = 8

        # Act
        result = self.svc.add_book_to_catalog(
            titre="1984",
            auteur="George Orwell",
            annee=1949,
            isbn="978-0-14-103614-4",
            nb_exemplaires=1,
        )

        # Assert
        self.assertEqual(result, 8)
        self.db.add_book.assert_called_once_with(
            "1984",
            "George Orwell",
            1949,
            "9780141036144",
            1,
        )

    def test_add_book_to_catalog_annee_future_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc.add_book_to_catalog(
                titre="Livre futur",
                auteur="Auteur",
                annee=99999,
                isbn="9780123456789",
                nb_exemplaires=1,
            )

        # Assert
        self.assertIn("année", str(ctx.exception))
        self.db.add_book.assert_not_called()

    def test_add_book_to_catalog_exemplaires_zero_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc.add_book_to_catalog(
                titre="Livre",
                auteur="Auteur",
                annee=2020,
                isbn="9780123456789",
                nb_exemplaires=0,
            )

        # Assert
        self.assertIn("exemplaires", str(ctx.exception))
        self.db.add_book.assert_not_called()

    def test_add_book_to_catalog_titre_vide_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc.add_book_to_catalog(
                titre="   ",
                auteur="Auteur",
                annee=2020,
                isbn="9780123456789",
                nb_exemplaires=1,
            )

        # Assert
        self.assertIn("titre", str(ctx.exception))
        self.db.add_book.assert_not_called()


class TestBorrowBook(unittest.TestCase):
    """Tests de la méthode borrow_book."""

    def setUp(self):
        self.db = MagicMock()
        self.svc = LibraryService(self.db)

    def test_borrow_book_livre_disponible(self):
        # Arrange
        self.db.get_book.return_value = {"exemplaires_dispo": 2}
        self.db.borrow_book.return_value = 12

        # Act
        result = self.svc.borrow_book(1, 3)

        # Assert
        self.assertEqual(result, 12)
        self.db.get_book.assert_called_once_with(1)
        self.db.borrow_book.assert_called_once()

    def test_borrow_book_livre_zero_copie_raises_loan_error(self):
        # Arrange
        self.db.get_book.return_value = {"exemplaires_dispo": 0}

        # Act
        with self.assertRaises(LoanError) as ctx:
            self.svc.borrow_book(5, 2)

        # Assert
        self.assertIn("disponible", str(ctx.exception))
        self.db.borrow_book.assert_not_called()

    def test_borrow_book_livre_inexistant_raises_loan_error(self):
        # Arrange
        self.db.get_book.return_value = None

        # Act
        with self.assertRaises(LoanError) as ctx:
            self.svc.borrow_book(99, 2)

        # Assert
        self.assertIn("n'existe pas", str(ctx.exception))
        self.db.borrow_book.assert_not_called()


class TestReturnBook(unittest.TestCase):
    """Tests de la méthode return_book."""

    def setUp(self):
        self.db = MagicMock()
        self.svc = LibraryService(self.db)

    def test_return_book_appel_db_return_book(self):
        # Arrange
        self.db.return_book.return_value = True

        # Act
        result = self.svc.return_book(14)

        # Assert
        self.assertTrue(result)
        self.db.return_book.assert_called_once_with(14)


class TestSearchBooks(unittest.TestCase):
    """Tests de la méthode search_books."""

    def setUp(self):
        self.db = MagicMock()
        self.svc = LibraryService(self.db)

    def test_search_books_query_vide_appele_get_all_books(self):
        # Arrange
        self.db.get_all_books.return_value = [{"id": 1}]

        # Act
        result = self.svc.search_books("   ")

        # Assert
        self.assertEqual(result, [{"id": 1}])
        self.db.get_all_books.assert_called_once_with()
        self.db.search_books.assert_not_called()

    def test_search_books_query_non_vide_appele_search_books(self):
        # Arrange
        self.db.search_books.return_value = [{"id": 2, "titre": "1984"}]

        # Act
        result = self.svc.search_books("198")

        # Assert
        self.assertEqual(result, [{"id": 2, "titre": "1984"}])
        self.db.search_books.assert_called_once_with("198")
        self.db.get_all_books.assert_not_called()


class TestValidations(unittest.TestCase):
    """Tests des méthodes de validation statiques."""

    def setUp(self):
        self.db = MagicMock()
        self.svc = LibraryService(self.db)

    def test_validate_email_email_valide(self):
        # Arrange
        email = "lecteur@bibliotheque.fr"

        # Act
        result = self.svc._validate_email(email)

        # Assert
        self.assertEqual(result, email)

    def test_validate_email_sans_arobase_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc._validate_email("testexample.fr")

        # Assert
        self.assertIn("@", str(ctx.exception))

    def test_validate_email_sans_point_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc._validate_email("test@domain")

        # Assert
        self.assertIn("point", str(ctx.exception))

    def test_validate_isbn_12_chiffres_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc._validate_isbn("123456789012")

        # Assert
        self.assertIn("10 ou 13", str(ctx.exception))

    def test_validate_isbn_lettres_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc._validate_isbn("ABCD123456")

        # Assert
        self.assertIn("10 ou 13", str(ctx.exception))

    def test_validate_year_annee_zero_raises_value_error(self):
        # Arrange
        with self.assertRaises(ValueError) as ctx:
            # Act
            self.svc._validate_year(0)

        # Assert
        self.assertIn("1000", str(ctx.exception))

    def test_validate_year_annee_1000_ok(self):
        # Arrange

        # Act
        result = self.svc._validate_year(1000)

        # Assert
        self.assertEqual(result, 1000)


if __name__ == "__main__":
    unittest.main()
