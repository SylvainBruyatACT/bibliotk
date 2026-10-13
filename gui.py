"""Interface graphique Tkinter de l'application BiblioTK."""

from datetime import date
import tkinter as tk
from tkinter import messagebox, ttk


class BiblioApp(tk.Tk):
    """Fenêtre principale de l'application de gestion de bibliothèque."""

    def __init__(self, service):
        """Initialise l'application avec le service métier.

        Args:
            service: Instance de LibraryService injectée par l'application.
        """
        super().__init__()
        self.service = service

        self.title("BiblioTK")
        self.geometry("960x640")
        self.minsize(960, 640)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.books_tab = ttk.Frame(self.notebook)
        self.loans_tab = ttk.Frame(self.notebook)
        self.readers_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.books_tab, text="Livres")
        self.notebook.add(self.loans_tab, text="Emprunts")
        self.notebook.add(self.readers_tab, text="Lecteurs")

        self._build_books_tab()
        self._build_loans_tab()
        self._build_readers_tab()

        self.refresh_all()

    def _build_books_tab(self):
        """Construit l'onglet des livres."""
        form_frame = ttk.LabelFrame(self.books_tab, text="Ajouter un livre")
        form_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.book_title_var = tk.StringVar()
        self.book_author_var = tk.StringVar()
        self.book_year_var = tk.StringVar()
        self.book_isbn_var = tk.StringVar()
        self.book_copies_var = tk.StringVar(value="1")
        self.book_search_var = tk.StringVar()
        self.book_search_var.trace_add("write", lambda *_: self.refresh_books())

        fields = [
            ("Titre", self.book_title_var),
            ("Auteur", self.book_author_var),
            ("Année", self.book_year_var),
            ("ISBN", self.book_isbn_var),
            ("Exemplaires", self.book_copies_var),
        ]

        for index, (label_text, variable) in enumerate(fields):
            ttk.Label(form_frame, text=f"{label_text} :").grid(
                row=index, column=0, sticky="w", padx=(10, 5), pady=5
            )
            ttk.Entry(form_frame, textvariable=variable, width=30).grid(
                row=index, column=1, sticky="ew", padx=(0, 10), pady=5
            )

        self.add_book_btn = ttk.Button(
            form_frame, text="Ajouter", command=self.add_book
        )
        self.add_book_btn.grid(row=5, column=0, padx=(10, 5), pady=(10, 10), sticky="w")

        self.delete_book_btn = ttk.Button(
            form_frame, text="Supprimer", command=self.delete_book
        )
        self.delete_book_btn.grid(
            row=5, column=1, sticky="w", padx=(0, 10), pady=(10, 10)
        )

        search_frame = ttk.Frame(self.books_tab)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        ttk.Label(search_frame, text="Recherche :").pack(side="left", padx=(0, 5))
        ttk.Entry(search_frame, textvariable=self.book_search_var, width=40).pack(
            side="left", fill="x", expand=True
        )

        columns = (
            "id",
            "titre",
            "auteur",
            "annee",
            "isbn",
            "dispo_total",
        )
        self.books_tree = ttk.Treeview(
            self.books_tab,
            columns=columns,
            show="headings",
        )
        self.books_tree.heading("id", text="ID")
        self.books_tree.heading("titre", text="Titre")
        self.books_tree.heading("auteur", text="Auteur")
        self.books_tree.heading("annee", text="Année")
        self.books_tree.heading("isbn", text="ISBN")
        self.books_tree.heading("dispo_total", text="Dispo-Total")

        for column in columns:
            self.books_tree.column(column, width=100, anchor="center")

        self.books_tree.column("titre", width=190, anchor="w")
        self.books_tree.column("auteur", width=170, anchor="w")
        self.books_tree.column("isbn", width=130, anchor="center")
        self.books_tree.column("dispo_total", width=90, anchor="center")

        self.books_scroll = ttk.Scrollbar(
            self.books_tab, orient="vertical", command=self.books_tree.yview
        )
        self.books_tree.configure(yscrollcommand=self.books_scroll.set)
        self.books_scroll.pack(side="right", fill="y", padx=(0, 10))
        self.books_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_loans_tab(self):
        """Construit l'onglet des emprunts."""
        form_frame = ttk.LabelFrame(self.loans_tab, text="Gestion des emprunts")
        form_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.loan_book_id_var = tk.StringVar()
        self.loan_reader_id_var = tk.StringVar()

        ttk.Label(form_frame, text="Livre ID :").grid(
            row=0, column=0, sticky="w", padx=(10, 5), pady=8
        )
        ttk.Entry(form_frame, textvariable=self.loan_book_id_var, width=20).grid(
            row=0, column=1, sticky="w", padx=(0, 15), pady=8
        )

        ttk.Label(form_frame, text="Lecteur ID :").grid(
            row=0, column=2, sticky="w", padx=(0, 5), pady=8
        )
        ttk.Entry(form_frame, textvariable=self.loan_reader_id_var, width=20).grid(
            row=0, column=3, sticky="w", padx=(0, 10), pady=8
        )

        self.borrow_btn = ttk.Button(self.loans_tab, text="Emprunter", command=self.borrow_book)
        self.borrow_btn.pack(side="left", padx=(10, 10), pady=(0, 10))

        self.return_btn = ttk.Button(self.loans_tab, text="Retourner", command=self.return_book)
        self.return_btn.pack(side="left", padx=(0, 10), pady=(0, 10))

        columns = (
            "id",
            "livre_id",
            "lecteur_id",
            "date_emprunt",
            "date_retour_prevue",
            "date_retour_reelle",
        )
        self.loans_tree = ttk.Treeview(
            self.loans_tab,
            columns=columns,
            show="headings",
        )
        self.loans_tree.heading("id", text="ID")
        self.loans_tree.heading("livre_id", text="Livre ID")
        self.loans_tree.heading("lecteur_id", text="Lecteur ID")
        self.loans_tree.heading("date_emprunt", text="Date emprunt")
        self.loans_tree.heading("date_retour_prevue", text="Date retour prévue")
        self.loans_tree.heading("date_retour_reelle", text="Date retour réelle")

        for column in columns:
            self.loans_tree.column(column, width=110, anchor="center")

        self.loans_tree.column("date_retour_prevue", width=140, anchor="center")
        self.loans_tree.column("date_retour_reelle", width=140, anchor="center")
        self.loans_tree.tag_configure("overdue", foreground="red", font=("TkDefaultFont", 9, "bold"))

        self.loans_scroll = ttk.Scrollbar(
            self.loans_tab, orient="vertical", command=self.loans_tree.yview
        )
        self.loans_tree.configure(yscrollcommand=self.loans_scroll.set)
        self.loans_scroll.pack(side="right", fill="y", padx=(0, 10))
        self.loans_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_readers_tab(self):
        """Construit l'onglet des lecteurs."""
        form_frame = ttk.LabelFrame(self.readers_tab, text="Ajouter un lecteur")
        form_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.reader_lastname_var = tk.StringVar()
        self.reader_firstname_var = tk.StringVar()
        self.reader_email_var = tk.StringVar()

        fields = [
            ("Nom", self.reader_lastname_var),
            ("Prénom", self.reader_firstname_var),
            ("Email", self.reader_email_var),
        ]

        for index, (label_text, variable) in enumerate(fields):
            ttk.Label(form_frame, text=f"{label_text} :").grid(
                row=index, column=0, sticky="w", padx=(10, 5), pady=8
            )
            ttk.Entry(form_frame, textvariable=variable, width=35).grid(
                row=index, column=1, sticky="ew", padx=(0, 10), pady=8
            )

        ttk.Button(form_frame, text="Ajouter", command=self.add_reader).grid(
            row=3, column=0, sticky="w", padx=(10, 5), pady=(10, 10)
        )

        columns = ("id", "nom", "prenom", "email")
        self.readers_tree = ttk.Treeview(
            self.readers_tab,
            columns=columns,
            show="headings",
        )
        self.readers_tree.heading("id", text="ID")
        self.readers_tree.heading("nom", text="Nom")
        self.readers_tree.heading("prenom", text="Prénom")
        self.readers_tree.heading("email", text="Email")

        self.readers_tree.column("id", width=60, anchor="center")
        self.readers_tree.column("nom", width=140, anchor="w")
        self.readers_tree.column("prenom", width=140, anchor="w")
        self.readers_tree.column("email", width=220, anchor="w")

        self.readers_scroll = ttk.Scrollbar(
            self.readers_tab, orient="vertical", command=self.readers_tree.yview
        )
        self.readers_tree.configure(yscrollcommand=self.readers_scroll.set)
        self.readers_scroll.pack(side="right", fill="y", padx=(0, 10))
        self.readers_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_books(self):
        """Actualise la liste des livres."""
        self.books_tree.delete(*self.books_tree.get_children())
        query = self.book_search_var.get()
        books = self.service.search_books(query)
        for book in books:
            self.books_tree.insert(
                "",
                "end",
                values=(
                    book["id"],
                    book["titre"],
                    book["auteur"],
                    book["annee"],
                    book["isbn"],
                    f"{book['exemplaires_dispo']}-{book['exemplaires_total']}",
                ),
            )

    def refresh_loans(self):
        """Actualise la liste des emprunts et colore les retards en rouge."""
        self.loans_tree.delete(*self.loans_tree.get_children())
        loans = self.service.get_active_loans()
        today = date.today().isoformat()

        for loan in loans:
            due_date = loan["date_retour_prevue"]
            tags = ("overdue",) if due_date < today else ()
            self.loans_tree.insert(
                "",
                "end",
                values=(
                    loan["emprunt_id"],
                    loan["livre_id"],
                    loan["lecteur_id"],
                    loan["date_emprunt"],
                    due_date,
                    loan["date_retour_reelle"],
                ),
                tags=tags,
            )

    def refresh_readers(self):
        """Actualise la liste des lecteurs."""
        self.readers_tree.delete(*self.readers_tree.get_children())
        readers = self.service.get_all_readers()
        for reader in readers:
            self.readers_tree.insert(
                "",
                "end",
                values=(
                    reader["id"],
                    reader["nom"],
                    reader["prenom"],
                    reader["email"],
                ),
            )

    def refresh_all(self):
        """Actualise toutes les vues de l'application."""
        self.refresh_books()
        self.refresh_loans()
        self.refresh_readers()

    def add_book(self):
        """Ajoute un livre au catalogue."""
        try:
            titre = self.book_title_var.get()
            auteur = self.book_author_var.get()
            annee = int(self.book_year_var.get())
            isbn = self.book_isbn_var.get()
            exemplaires = int(self.book_copies_var.get())

            self.service.add_book_to_catalog(
                titre=titre,
                auteur=auteur,
                annee=annee,
                isbn=isbn,
                nb_exemplaires=exemplaires,
            )

            self.book_title_var.set("")
            self.book_author_var.set("")
            self.book_year_var.set("")
            self.book_isbn_var.set("")
            self.book_copies_var.set("1")
            self.refresh_books()
        except Exception as exc:  # pragma: no cover - interface feedback
            messagebox.showerror("Erreur", str(exc))

    def delete_book(self):
        """Supprime le livre sélectionné."""
        try:
            selected = self.books_tree.selection()
            if not selected:
                messagebox.showerror("Erreur", "Sélectionnez un livre à supprimer.")
                return

            book_id = int(self.books_tree.item(selected[0], "values")[0])
            self.service.delete_book(book_id)
            self.refresh_books()
        except Exception as exc:  # pragma: no cover - interface feedback
            messagebox.showerror("Erreur", str(exc))

    def borrow_book(self):
        """Emprunte un livre pour un lecteur."""
        try:
            livre_id = int(self.loan_book_id_var.get())
            lecteur_id = int(self.loan_reader_id_var.get())
            self.service.borrow_book(livre_id, lecteur_id)
            self.loan_book_id_var.set("")
            self.loan_reader_id_var.set("")
            self.refresh_loans()
            self.refresh_books()
        except Exception as exc:  # pragma: no cover - interface feedback
            messagebox.showerror("Erreur", str(exc))

    def return_book(self):
        """Retourne l'emprunt sélectionné."""
        try:
            selected = self.loans_tree.selection()
            if not selected:
                messagebox.showerror("Erreur", "Sélectionnez un emprunt à retourner.")
                return

            emprunt_id = int(self.loans_tree.item(selected[0], "values")[0])
            self.service.return_book(emprunt_id)
            self.refresh_loans()
            self.refresh_books()
        except Exception as exc:  # pragma: no cover - interface feedback
            messagebox.showerror("Erreur", str(exc))

    def add_reader(self):
        """Ajoute un lecteur."""
        try:
            nom = self.reader_lastname_var.get()
            prenom = self.reader_firstname_var.get()
            email = self.reader_email_var.get()

            self.service.add_reader(nom, prenom, email)
            self.reader_lastname_var.set("")
            self.reader_firstname_var.set("")
            self.reader_email_var.set("")
            self.refresh_readers()
        except Exception as exc:  # pragma: no cover - interface feedback
            messagebox.showerror("Erreur", str(exc))


if __name__ == "__main__":
    try:
        from database import DatabaseManager
        from library import LibraryService

        app = BiblioApp(LibraryService(DatabaseManager()))
        app.mainloop()
    except Exception as exc:  # pragma: no cover - startup diagnostics
        messagebox.showerror("Erreur de démarrage", str(exc))
