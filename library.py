"""
PageTurner Library System — Internal Book Management Tool
=========================================================
Original developer: Jordan (no longer with us. Don't ask.)
Current maintainer: YOU

This system lets library staff:
  - Add books to the catalogue
  - Check books in and out
  - Search and list the collection
  - See which books are overdue
  - Save and load catalogue data from disk
  - View borrowing statistics

Good luck. Jordan left no comments and exactly one sticky note
that read "it mostly works".
"""

import json
import os
from datetime import datetime, timedelta


# ──────────────────────────────────────────────────
# DATA MODELS
# ──────────────────────────────────────────────────

class Book:
    """Represents a single book in the library catalogue."""

    # BUG #1 (OOP — __init__ assigns to local variable, not self)
    # self.title is never set; accessing it later raises AttributeError.
    def __init__(self, title, author, isbn, genre="General"):
        self.title = title         # ← should be self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.is_checked_out = False
        self.borrower_name = None
        self.checkout_date = None
        self.due_date = None

    def checkout(self, borrower_name, loan_days=14):
        """Mark the book as checked out."""
        self.is_checked_out = True
        self.borrower_name = borrower_name
        self.checkout_date = datetime.now().strftime("%Y-%m-%d")
        due = datetime.now() + timedelta(days=loan_days)
        self.due_date = due.strftime("%Y-%m-%d")

    def checkin(self):
        """Return the book to the library."""
        self.is_checked_out = False
        self.borrower_name = None
        self.checkout_date = None
        self.due_date = None

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "genre": self.genre,
            "is_checked_out": self.is_checked_out,
            "borrower_name": self.borrower_name,
            "checkout_date": self.checkout_date,
            "due_date": self.due_date,
        }

    # BUG #2 (OOP — missing @classmethod; called as Book.from_dict(data) but
    # Python passes `data` as `self`, so the method receives wrong arguments.)
    @classmethod
    def from_dict(cls, data):
        book = cls(
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            genre=data.get("genre", "General"),
        )
        book.is_checked_out = data.get("is_checked_out", False)
        book.borrower_name = data.get("borrower_name")
        book.checkout_date = data.get("checkout_date")
        book.due_date = data.get("due_date")
        return book

    def __str__(self):
        status = (f"OUT → {self.borrower_name} (due {self.due_date})" 
            if self.is_checked_out 
            else "Available"
        )
        return f'"{self.title}" by {self.author} [{self.isbn}] — {status}'


class Library:
    """Manages the full book catalogue and borrowing records."""

    DATA_FILE = "data/catalogue.json"

    def __init__(self):
        self.books = []     # list of Book objects
        self.load_catalogue()

    # ──────────────────────────────────────
    # CATALOGUE MANAGEMENT
    # ──────────────────────────────────────

    def add_book(self, title, author, isbn, genre="General"):
        """Add a new book to the catalogue."""
        if not title.strip() or not author.strip():
            print("Error: Title and author cannot be empty.")
            return None

        if self.find_by_isbn(isbn):
            print(f"A book with ISBN {isbn} already exists.")
            return None

        book = Book(title.strip(), author.strip(), isbn.strip(), genre.strip())
        self.books.append(book)
        print(f'Added: "{title}" by {author}')
        return book

    def remove_book(self, isbn):
        """Remove a book from the catalogue by ISBN."""
        book = self.find_by_isbn(isbn)
        if not book:
            print(f"No book found with ISBN {isbn}.")
            return False
        if book.is_checked_out:
            print(f'Cannot remove "{book.title}" — it is currently checked out.')
            return False
        self.books.remove(book)
        print(f'Removed "{book.title}" from the catalogue.')
        return True

    # ──────────────────────────────────────
    # SEARCH & LIST
    # ──────────────────────────────────────

    def find_by_isbn(self, isbn):
        """Return the book matching the given ISBN, or None."""
        for book in self.books:
            if book.isbn == isbn.strip():
                return book
        return None

    def search(self, keyword):
        """Search titles and authors by keyword (case-insensitive)."""
        # BUG #3 (Logic — search is case-sensitive because neither title nor
        # author is lowercased before comparison; keyword IS lowercased but
        # that doesn't help if the fields being searched are not.)
        keyword = keyword.lower()
        return [
            b for b in self.books
            if keyword in b.title or keyword in b.author
        ]

    def list_all(self, available_only=False):
        """Print all books, optionally filtered to available only."""
        if not self.books:
            print("The catalogue is empty.")
            return

        shown = 0
        print("\n── Catalogue ──")
        for i, book in enumerate(self.books, start=1):
            if available_only and book.is_checked_out:
                continue
            print(f"  {i}. {book}")
            shown += 1

        if shown == 0:
            print("  No books match the current filter.")
        print()

    # ──────────────────────────────────────
    # CHECKOUT & CHECKIN
    # ──────────────────────────────────────

    def checkout_book(self, isbn, borrower_name, loan_days=14):
        """Check out a book to a borrower."""
        book = self.find_by_isbn(isbn)
        if not book:
            print(f"Book with ISBN {isbn} not found.")
            return False
        if book.is_checked_out:
            print(f'"{book.title}" is already checked out by {book.borrower_name}.')
            return False

        # BUG #4 (Logic — loan_days is never validated; a negative or zero value
        # creates a due date in the past, silently making the book "overdue"
        # immediately. Students must add a guard clause here.)
        book.checkout(borrower_name, loan_days)
        print(f'Checked out "{book.title}" to {borrower_name}. Due: {book.due_date}')
        return True

    def checkin_book(self, isbn):
        """Return a book to the library."""
        book = self.find_by_isbn(isbn)
        if not book:
            print(f"Book with ISBN {isbn} not found.")
            return False
        if not book.is_checked_out:
            print(f'"{book.title}" is not currently checked out.')
            return False
        name = book.borrower_name
        book.checkin()
        print(f'"{book.title}" returned by {name}. Thank you!')
        return True

    # ──────────────────────────────────────
    # OVERDUE REPORTS
    # ──────────────────────────────────────

    def overdue_books(self):
        """Return a list of books that are past their due date."""
        today = datetime.now().strftime("%Y-%m-%d")
        overdue = []
        for book in self.books:
            if book.is_checked_out and book.due_date:
                if book.due_date < today:
                    overdue.append(book)
        return overdue

    # ──────────────────────────────────────
    # STATISTICS
    # ──────────────────────────────────────

    def statistics(self):
        """Print borrowing statistics."""
        total = len(self.books)
        # BUG #5 (Logic — counts books that are NOT checked out as "checked out";
        # the condition is inverted. `not b.is_checked_out` should be
        # `b.is_checked_out`.)
        checked_out = sum(1 for b in self.books if not b.is_checked_out)
        available = total - checked_out

        genres = {}
        for book in self.books:
            genres[book.genre] = genres.get(book.genre, 0) + 1

        print("\n── Library Statistics ──")
        print(f"  Total books    : {total}")
        print(f"  Checked out    : {checked_out}")
        print(f"  Available      : {available}")
        print(f"  Overdue        : {len(self.overdue_books())}")
        print(f"\n  Books by genre:")
        for genre, count in sorted(genres.items()):
            print(f"    {genre:<20} {count}")
        print()

    # ──────────────────────────────────────
    # PERSISTENCE
    # ──────────────────────────────────────

    def save_catalogue(self):
        """Save all books to a JSON file."""
        # BUG #6 (File I/O — `data/` directory is never created; on a fresh clone
        # this raises FileNotFoundError. os.makedirs(..., exist_ok=True) is needed
        # before the open() call.)
        with open(self.DATA_FILE, "w") as f:
            json.dump([b.to_dict() for b in self.books], f, indent=2)
        print(f"Catalogue saved ({len(self.books)} books).")

    def load_catalogue(self):
        """Load books from the JSON file."""
        if not os.path.exists(self.DATA_FILE):
            return

        # BUG #7 (Error Handling — no try/except; a corrupted or empty JSON file
        # raises json.JSONDecodeError and crashes the app on startup. Students
        # must wrap this in try/except and fall back to an empty catalogue.)
        with open(self.DATA_FILE, "r") as f:
            data = json.load(f)

        self.books = [Book.from_dict(item) for item in data]


# ──────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────

def print_menu():
    print("""
╔════════════════════════════════╗
║    PageTurner Library System   ║
╠════════════════════════════════╣
║  1. List all books             ║
║  2. List available books       ║
║  3. Add a book                 ║
║  4. Remove a book              ║
║  5. Check out a book           ║
║  6. Return a book              ║
║  7. Search catalogue           ║
║  8. Overdue report             ║
║  9. Statistics                 ║
║  0. Save & quit                ║
╚════════════════════════════════╝
""")


def main():
    library = Library()

    while True:
        print_menu()
        try:
            choice = input("Choose an option: ").strip()
        except EOFError:
            library.save_catalogue()
            print("\nGoodbye!")
            break

        if choice == "1":
            library.list_all()

        elif choice == "2":
            library.list_all(available_only=True)

        elif choice == "3":
            title  = input("Title  : ").strip()
            author = input("Author : ").strip()
            isbn   = input("ISBN   : ").strip()
            genre  = input("Genre  [General]: ").strip() or "General"
            library.add_book(title, author, isbn, genre)

        elif choice == "4":
            isbn = input("ISBN of book to remove: ").strip()
            library.remove_book(isbn)

        elif choice == "5":
            isbn     = input("ISBN          : ").strip()
            borrower = input("Borrower name : ").strip()
            try:
                days = int(input("Loan period (days) [14]: ").strip() or "14")
            except ValueError:
                print("Invalid number of days. Defaulting to 14.")
                days = 14
            library.checkout_book(isbn, borrower, days)

        elif choice == "6":
            isbn = input("ISBN of book being returned: ").strip()
            library.checkin_book(isbn)

        elif choice == "7":
            keyword = input("Search keyword: ").strip()
            results = library.search(keyword)
            if results:
                print(f"\n── Results for '{keyword}' ──")
                for book in results:
                    print(" ", book)
                print()
            else:
                print(f"No books found matching '{keyword}'.")

        elif choice == "8":
            overdue = library.overdue_books()
            if overdue:
                print("\n── Overdue Books ──")
                for book in overdue:
                    print(" ", book)
                print()
            else:
                print("No overdue books. Great news!")

        elif choice == "9":
            library.statistics()

        elif choice == "0":
            library.save_catalogue()
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 0–9.")


if __name__ == "__main__":
    main()
