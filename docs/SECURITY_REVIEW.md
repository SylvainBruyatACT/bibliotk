# Audit sécurité et qualité – BiblioTK

## Résumé exécutif

Le projet est globalement conforme aux exigences de sécurité et d’architecture demandées.

- Sécurité SQL : conforme
- Validations des entrées : conformes
- Gestion des exceptions GUI : conforme
- Qualité du code : conforme
- Architecture : conforme, avec une remarque mineure sur le point d’entrée de l’application

Aucun problème bloquant n’a été détecté sur la logique métier et la couche de données. Une seule remarque de niveau faible a été identifiée sur le bootstrap de la GUI.

---

## 1) Sécurité SQL

### Verdict
Conforme.

### Vérification
Aucune requête SQL interpolée avec f-string n’a été trouvée dans database.py.
Toutes les opérations utilisent des requêtes paramétrées avec `?` et des tuples de paramètres, par exemple :

- `INSERT INTO livres (...) VALUES (?, ?, ?, ?, ?, ?)`
- `SELECT * FROM livres WHERE id = ?`
- `UPDATE livres SET exemplaires_dispo = exemplaires_dispo - 1 WHERE id = ? AND exemplaires_dispo > 0`
- `DELETE FROM livres WHERE id = ?`

### Points vérifiés
- Fichier : database.py
- Lignes approximatives : 18-40, 70-100, 150-220, 260-330, 365-450
- Sévérité : aucune

### Correctif
Aucun correctif requis.

---

## 2) Validations des entrées utilisateur

### Verdict
Conforme.

### Vérification
Toutes les entrées de l’interface passent par LibraryService avant les appels aux méthodes du gestionnaire de données.

Exemples vérifiés :

- GUI => `self.service.add_book_to_catalog(...)` dans gui.py (approx. 300-324)
- GUI => `self.service.add_reader(...)` dans gui.py (approx. 368-382)
- GUI => `self.service.borrow_book(...)` dans gui.py (approx. 340-351)
- GUI => `self.service.search_books(...)` dans gui.py (approx. 236-252)

La validation est bien centralisée dans library.py :

- `LibraryService._validate_isbn()`
- `LibraryService._validate_year()`
- `LibraryService._validate_email()`
- `LibraryService.add_book_to_catalog()`
- `LibraryService.add_reader()`

### Points vérifiés
- Fichiers : gui.py, library.py
- Lignes approximatives : gui.py 300-382 ; library.py 25-214
- Sévérité : aucune

### Correctif
Aucun correctif requis.

---

## 3) Exceptions GUI

### Verdict
Conforme.

### Vérification
Chaque callback Tkinter principal est protégé par un bloc `try/except` et un `messagebox.showerror(...)`.

Callbacks vérifiés :

- `add_book()` : gui.py, approx. 300-324
- `delete_book()` : gui.py, approx. 326-338
- `borrow_book()` : gui.py, approx. 340-351
- `return_book()` : gui.py, approx. 353-366
- `add_reader()` : gui.py, approx. 368-382

### Points vérifiés
- Fichier : gui.py
- Lignes approximatives : 300-382
- Sévérité : aucune

### Correctif
Aucun correctif requis.

---

## 4) Qualité du code

### Verdict
Conforme.

### Vérification
Les méthodes publiques de la couche métier ont des docstrings, au format explicite et compréhensible, notamment :

- `LibraryService.__init__()`
- `LibraryService._validate_isbn()`
- `LibraryService._validate_year()`
- `LibraryService._validate_email()`
- `LibraryService.add_book_to_catalog()`
- `LibraryService.borrow_book()`
- `LibraryService.return_book()`
- `LibraryService.search_books()`
- `LibraryService.add_reader()`
- `LibraryService.get_all_books()`
- `LibraryService.delete_book()`
- `LibraryService.get_all_readers()`
- `LibraryService.get_active_loans()`
- `LibraryService.get_overdue_loans()`

### Points vérifiés
- Fichier : library.py
- Lignes approximatives : 13-239
- Sévérité : aucune

### Correctif
Aucun correctif requis.

---

## 5) Conformité d’architecture

### Verdict
Conforme, avec une remarque mineure de bootstrap.

### Vérification
La GUI ne manipule pas directement DatabaseManager dans ses méthodes de logique d’interface. Les méthodes de callback appellent uniquement LibraryService.

Le seul point de contact direct avec DatabaseManager est le point d’entrée de démarrage :

```python
if __name__ == "__main__":
    from database import DatabaseManager
    from library import LibraryService

    app = BiblioApp(LibraryService(DatabaseManager()))
    app.mainloop()
```

Fichier : gui.py, ligne approximative 385-389.

### Problème détecté (faible)

- Fichier : gui.py
- Ligne approximative : 385-389
- Sévérité : faible
- Observation : le bootstrap instancie directement DatabaseManager dans le fichier GUI. Ce n’est pas un appel SQL depuis les callbacks, mais cela crée un couplage technique dans le point d’entrée.

### Code corrigé

```python
if __name__ == "__main__":
    db = DatabaseManager()
    service = LibraryService(db)
    app = BiblioApp(service)
    app.mainloop()
```

Ce style garde la même architecture, mais rend le point d’entrée plus explicite et plus facile à tester.

---

## Conclusion

Le projet BiblioTK est globalement sain sur les cinq axes audités :

- pas de vulnérabilité SQL classique via interpolation de requêtes ;
- validation centralisée dans LibraryService ;
- gestion des erreurs bien traitée côté GUI ;
- méthodes publiques documentées ;
- architecture respectée dans les callbacks.

Le seul point à améliorer est un léger couplage de bootstrap dans le point d’entrée GUI, sans impact fonctionnel direct.
