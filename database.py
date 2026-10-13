"""SQLite data access for the BiblioTK library."""

from contextlib import closing
from datetime import date
from pathlib import Path
import sqlite3


class DatabaseManager:
    """Manage SQLite connections and BiblioTK data operations."""

    def __init__(self, db_path: str | Path = "bibliotk.db") -> None:
        """Initialize the database manager and create the schema if needed.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a configured SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        """Create database tables from the adjacent schema.sql file."""
        schema_path = Path(__file__).with_name("schema.sql")
        schema = schema_path.read_text(encoding="utf-8")
        with closing(self._get_connection()) as conn:
            with conn:
                conn.executescript(schema)

    def add_book(
        self,
        titre: str,
        auteur: str,
        annee: int,
        isbn: str,
        exemplaires_total: int = 1,
    ) -> int:
        """Add a book and return its generated ID.

        Args:
            titre: Book title.
            auteur: Book author.
            annee: Publication year.
            isbn: Unique ISBN.
            exemplaires_total: Number of copies to add.

        Returns:
            The ID assigned to the new book.
        """
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO livres (
                        titre, auteur, annee, isbn,
                        exemplaires_total, exemplaires_dispo
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        titre,
                        auteur,
                        annee,
                        isbn,
                        exemplaires_total,
                        exemplaires_total,
                    ),
                )
                return cursor.lastrowid

    def get_book(self, book_id: int) -> sqlite3.Row | None:
        """Get a book by ID.

        Args:
            book_id: ID of the book to retrieve.

        Returns:
            The matching book row, or None if it does not exist.
        """
        with closing(self._get_connection()) as conn:
            return conn.execute(
                "SELECT * FROM livres WHERE id = ?",
                (book_id,),
            ).fetchone()

    def get_all_books(self) -> list[sqlite3.Row]:
        """Get all books ordered by title.

        Returns:
            A list of book rows.
        """
        with closing(self._get_connection()) as conn:
            return conn.execute(
                "SELECT * FROM livres ORDER BY titre, id"
            ).fetchall()

    def search_books(self, search_term: str) -> list[sqlite3.Row]:
        """Search books by title, author, or ISBN.

        Args:
            search_term: Text to match, case-insensitively.

        Returns:
            Matching book rows.
        """
        pattern = "%" + search_term + "%"
        with closing(self._get_connection()) as conn:
            return conn.execute(
                """
                SELECT * FROM livres
                WHERE titre LIKE ? OR auteur LIKE ? OR isbn LIKE ?
                ORDER BY titre, id
                """,
                (pattern, pattern, pattern),
            ).fetchall()

    def update_book(
        self,
        book_id: int,
        titre: str | None = None,
        auteur: str | None = None,
        annee: int | None = None,
        isbn: str | None = None,
        exemplaires_total: int | None = None,
        exemplaires_dispo: int | None = None,
    ) -> bool:
        """Update the supplied fields for a book.

        If the total copy count changes without an explicit available count,
        the number of copies currently on loan is preserved.

        Args:
            book_id: ID of the book to update.
            titre: Replacement title, if provided.
            auteur: Replacement author, if provided.
            annee: Replacement publication year, if provided.
            isbn: Replacement ISBN, if provided.
            exemplaires_total: Replacement total copy count, if provided.
            exemplaires_dispo: Replacement available copy count, if provided.

        Returns:
            True if a book was updated, otherwise False.

        Raises:
            ValueError: If no update fields are provided or the new total is
                less than the number of copies currently on loan.
        """
        with closing(self._get_connection()) as conn:
            with conn:
                current = conn.execute(
                    """
                    SELECT exemplaires_total, exemplaires_dispo
                    FROM livres WHERE id = ?
                    """,
                    (book_id,),
                ).fetchone()
                if current is None:
                    return False

                if all(
                    value is None
                    for value in (
                        titre,
                        auteur,
                        annee,
                        isbn,
                        exemplaires_total,
                        exemplaires_dispo,
                    )
                ):
                    raise ValueError("At least one book field must be provided.")

                if exemplaires_total is not None:
                    if exemplaires_dispo is None:
                        copies_on_loan = (
                            current["exemplaires_total"]
                            - current["exemplaires_dispo"]
                        )
                        exemplaires_dispo = exemplaires_total - copies_on_loan
                        if exemplaires_dispo < 0:
                            raise ValueError(
                                "Total copies cannot be less than copies on loan."
                            )

                cursor = conn.execute(
                    """
                    UPDATE livres SET
                        titre = COALESCE(?, titre),
                        auteur = COALESCE(?, auteur),
                        annee = COALESCE(?, annee),
                        isbn = COALESCE(?, isbn),
                        exemplaires_total = COALESCE(?, exemplaires_total),
                        exemplaires_dispo = COALESCE(?, exemplaires_dispo)
                    WHERE id = ?
                    """,
                    (
                        titre,
                        auteur,
                        annee,
                        isbn,
                        exemplaires_total,
                        exemplaires_dispo,
                        book_id,
                    ),
                )
                return cursor.rowcount > 0

    def delete_book(self, book_id: int) -> bool:
        """Delete a book by ID.

        Args:
            book_id: ID of the book to delete.

        Returns:
            True if a book was deleted, otherwise False.

        Raises:
            sqlite3.IntegrityError: If the book has associated loan records.
        """
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    "DELETE FROM livres WHERE id = ?",
                    (book_id,),
                )
                return cursor.rowcount > 0

    def add_reader(self, nom: str, prenom: str, email: str) -> int:
        """Add a reader and return the generated ID.

        Args:
            nom: Reader's family name.
            prenom: Reader's given name.
            email: Reader's unique email address.

        Returns:
            The ID assigned to the new reader.
        """
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO lecteurs (nom, prenom, email) VALUES (?, ?, ?)",
                    (nom, prenom, email),
                )
                return cursor.lastrowid

    def get_all_readers(self) -> list[sqlite3.Row]:
        """Get all readers ordered by family and given name.

        Returns:
            A list of reader rows.
        """
        with closing(self._get_connection()) as conn:
            return conn.execute(
                "SELECT * FROM lecteurs ORDER BY nom, prenom, id"
            ).fetchall()

    def borrow_book(
        self,
        livre_id: int,
        lecteur_id: int,
        date_emprunt: str,
        date_retour_prevue: str,
    ) -> int:
        """Create a loan and decrement the book's available copy count.

        Args:
            livre_id: ID of the book to borrow.
            lecteur_id: ID of the borrowing reader.
            date_emprunt: Loan date in ISO 8601 format.
            date_retour_prevue: Due date in ISO 8601 format.

        Returns:
            The ID assigned to the new loan.

        Raises:
            ValueError: If the book does not exist or has no available copies.
            sqlite3.IntegrityError: If the reader does not exist or a schema
                constraint is violated.
        """
        with closing(self._get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    """
                    UPDATE livres
                    SET exemplaires_dispo = exemplaires_dispo - 1
                    WHERE id = ? AND exemplaires_dispo > 0
                    """,
                    (livre_id,),
                )
                if cursor.rowcount == 0:
                    raise ValueError(
                        f"Book {livre_id} does not exist or has no available copies."
                    )

                cursor = conn.execute(
                    """
                    INSERT INTO emprunts (
                        livre_id, lecteur_id, date_emprunt, date_retour_prevue
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (livre_id, lecteur_id, date_emprunt, date_retour_prevue),
                )
                return cursor.lastrowid

    def return_book(
        self,
        emprunt_id: int,
        date_retour_reelle: str | None = None,
    ) -> bool:
        """Record a loan return and increment the book's available copies.

        Args:
            emprunt_id: ID of the loan to return.
            date_retour_reelle: Return date in ISO 8601 format. Defaults to
                today's date.

        Returns:
            True when the active loan was returned.

        Raises:
            ValueError: If the loan does not exist or has already been returned.
        """
        return_date = (
            date.today().isoformat()
            if date_retour_reelle is None
            else date_retour_reelle
        )
        with closing(self._get_connection()) as conn:
            with conn:
                loan = conn.execute(
                    """
                    SELECT livre_id FROM emprunts
                    WHERE id = ? AND date_retour_reelle IS NULL
                    """,
                    (emprunt_id,),
                ).fetchone()
                if loan is None:
                    raise ValueError(
                        f"Active loan {emprunt_id} does not exist."
                    )

                cursor = conn.execute(
                    """
                    UPDATE emprunts SET date_retour_reelle = ?
                    WHERE id = ? AND date_retour_reelle IS NULL
                    """,
                    (return_date, emprunt_id),
                )
                if cursor.rowcount == 0:
                    raise ValueError(
                        f"Active loan {emprunt_id} does not exist."
                    )

                conn.execute(
                    """
                    UPDATE livres
                    SET exemplaires_dispo = exemplaires_dispo + 1
                    WHERE id = ?
                    """,
                    (loan["livre_id"],),
                )
                return True

    def get_active_loans(self) -> list[sqlite3.Row]:
        """Get active loans joined with their books and readers.

        Returns:
            Active loan rows with loan, book, and reader details.
        """
        with closing(self._get_connection()) as conn:
            return conn.execute(
                """
                SELECT
                    e.id AS emprunt_id,
                    e.livre_id,
                    e.lecteur_id,
                    e.date_emprunt,
                    e.date_retour_prevue,
                    e.date_retour_reelle,
                    l.titre,
                    l.auteur,
                    l.isbn,
                    r.nom,
                    r.prenom,
                    r.email
                FROM emprunts AS e
                JOIN livres AS l ON l.id = e.livre_id
                JOIN lecteurs AS r ON r.id = e.lecteur_id
                WHERE e.date_retour_reelle IS NULL
                ORDER BY e.date_retour_prevue, e.id
                """
            ).fetchall()

    def get_overdue_loans(
        self,
        as_of: str | date | None = None,
    ) -> list[sqlite3.Row]:
        """Get active loans whose due date has passed.

        Args:
            as_of: ISO date or date to use as the comparison date.
                Defaults to today's date.

        Returns:
            Overdue loan rows with loan, book, and reader details.
        """
        if isinstance(as_of, date):
            comparison_date = as_of.isoformat()
        elif as_of is None:
            comparison_date = date.today().isoformat()
        else:
            comparison_date = as_of
        with closing(self._get_connection()) as conn:
            return conn.execute(
                """
                SELECT
                    e.id AS emprunt_id,
                    e.livre_id,
                    e.lecteur_id,
                    e.date_emprunt,
                    e.date_retour_prevue,
                    e.date_retour_reelle,
                    l.titre,
                    l.auteur,
                    l.isbn,
                    r.nom,
                    r.prenom,
                    r.email
                FROM emprunts AS e
                JOIN livres AS l ON l.id = e.livre_id
                JOIN lecteurs AS r ON r.id = e.lecteur_id
                WHERE e.date_retour_reelle IS NULL
                    AND e.date_retour_prevue < ?
                ORDER BY e.date_retour_prevue, e.id
                """,
                (comparison_date,),
            ).fetchall()