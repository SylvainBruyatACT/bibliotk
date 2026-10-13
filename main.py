"""Point d'entrée principal de l'application BiblioTK."""

from database import DatabaseManager
from gui import BiblioApp
from library import LibraryService


def main() -> None:
    """Démarre l'application avec les dépendances correctement initialisées."""
    try:
        db = DatabaseManager()
        service = LibraryService(db)
        app = BiblioApp(service)
        app.mainloop()
    except Exception as exc:  # pragma: no cover - gestion des erreurs de démarrage
        # L'interface graphique ne doit pas "crasher" silencieusement.
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erreur de démarrage", str(exc))
            root.destroy()
        except Exception:
            # En environnement non-GUI, on ne peut pas afficher le messagebox.
            raise


if __name__ == "__main__":
    main()
