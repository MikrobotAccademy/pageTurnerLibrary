"""
Tests for PageTurner Library System.

Several of these tests fail out of the box — that's intentional.
Your job is to fix the application code so they pass.
You should also write additional tests where you see gaps.

Run with:
    python -m pytest tests/test_library.py -v
"""

import pytest
import os
import json
from library import Book, Library


# ── Book class ──────────────────────────────────────────────────────

class TestBook:

    def test_book_stores_title(self):
        """A Book should remember its title."""
        book = Book("Dune", "Frank Herbert", "978-0-441-01794-1")
        assert book.title == "Dune"

    def test_book_stores_author(self):
        book = Book("Dune", "Frank Herbert", "978-0-441-01794-1")
        assert book.author == "Frank Herbert"

    def test_book_default_available(self):
        book = Book("1984", "George Orwell", "000-1")
        assert book.is_checked_out is False
        assert book.borrower_name is None

    def test_checkout_marks_book_out(self):
        book = Book("Brave New World", "Aldous Huxley", "000-2")
        book.checkout("Alice")
        assert book.is_checked_out is True
        assert book.borrower_name == "Alice"
        assert book.due_date is not None

    def test_checkin_clears_borrower(self):
        book = Book("Fahrenheit 451", "Ray Bradbury", "000-3")
        book.checkout("Bob")
        book.checkin()
        assert book.is_checked_out is False
        assert book.borrower_name is None
        assert book.due_date is None

    def test_to_dict_and_from_dict(self):
        """Round-trip: a book serialised and deserialised should match."""
        original = Book("The Hobbit", "J.R.R. Tolkien", "000-4", genre="Fantasy")
        original.checkout("Carol")
        data = original.to_dict()

        restored = Book.from_dict(data)          # must be a classmethod
        assert restored.title == "The Hobbit"
        assert restored.author == "J.R.R. Tolkien"
        assert restored.is_checked_out is True
        assert restored.borrower_name == "Carol"

    def test_from_dict_is_classmethod(self):
        """Book.from_dict(data) should work without an instance."""
        data = {
            "title": "Moby Dick",
            "author": "Herman Melville",
            "isbn": "000-5",
            "genre": "Classic",
            "is_checked_out": False,
            "borrower_name": None,
            "checkout_date": None,
            "due_date": None,
        }
        book = Book.from_dict(data)
        assert book.title == "Moby Dick"


# ── Library class ───────────────────────────────────────────────────

class TestLibrary:

    def setup_method(self):
        Library.DATA_FILE = "data/test_catalogue.json"
        self.lib = Library()
        self.lib.books = []    # start clean

    def teardown_method(self):
        if os.path.exists("data/test_catalogue.json"):
            os.remove("data/test_catalogue.json")
        Library.DATA_FILE = "data/catalogue.json"

    # ── add / remove ──

    def test_add_book(self):
        book = self.lib.add_book("Neuromancer", "William Gibson", "001-1")
        assert book is not None
        assert len(self.lib.books) == 1

    def test_add_book_duplicate_isbn_rejected(self):
        self.lib.add_book("Book A", "Author A", "ISBN-1")
        result = self.lib.add_book("Book B", "Author B", "ISBN-1")
        assert result is None
        assert len(self.lib.books) == 1

    def test_add_book_empty_title_rejected(self):
        result = self.lib.add_book("", "Someone", "ISBN-2")
        assert result is None

    def test_remove_book(self):
        self.lib.add_book("Temporary", "Author", "TMP-1")
        removed = self.lib.remove_book("TMP-1")
        assert removed is True
        assert len(self.lib.books) == 0

    def test_cannot_remove_checked_out_book(self):
        self.lib.add_book("In Use", "Author", "USE-1")
        self.lib.checkout_book("USE-1", "Dan")
        result = self.lib.remove_book("USE-1")
        assert result is False

    # ── search ──

    def test_search_by_title(self):
        self.lib.add_book("The Great Gatsby", "F. Scott Fitzgerald", "GG-1")
        results = self.lib.search("gatsby")
        assert len(results) == 1

    def test_search_by_author(self):
        self.lib.add_book("Of Mice and Men", "John Steinbeck", "OM-1")
        results = self.lib.search("steinbeck")
        assert len(results) == 1

    def test_search_case_insensitive(self):
        """Search must be case-insensitive in both directions."""
        self.lib.add_book("To Kill a Mockingbird", "Harper Lee", "TKM-1")
        results = self.lib.search("MOCKINGBIRD")
        assert len(results) == 1

    # ── checkout / checkin ──

    def test_checkout_book(self):
        self.lib.add_book("Catch-22", "Joseph Heller", "C22-1")
        result = self.lib.checkout_book("C22-1", "Eve")
        assert result is True
        assert self.lib.books[0].is_checked_out is True

    def test_cannot_checkout_already_out(self):
        self.lib.add_book("Slaughterhouse-Five", "Kurt Vonnegut", "SH5-1")
        self.lib.checkout_book("SH5-1", "Frank")
        result = self.lib.checkout_book("SH5-1", "Grace")
        assert result is False

    def test_checkout_rejects_negative_loan_days(self):
        """A negative loan period should be rejected, not silently accepted."""
        self.lib.add_book("Lord of the Flies", "William Golding", "LOF-1")
        result = self.lib.checkout_book("LOF-1", "Hal", loan_days=-5)
        # The book should NOT be checked out with an invalid loan period
        book = self.lib.find_by_isbn("LOF-1")
        assert book.is_checked_out is False or result is False

    def test_checkin_book(self):
        self.lib.add_book("Animal Farm", "George Orwell", "AF-1")
        self.lib.checkout_book("AF-1", "Iris")
        result = self.lib.checkin_book("AF-1")
        assert result is True
        assert self.lib.books[0].is_checked_out is False

    # ── statistics ──

    def test_statistics_checked_out_count(self, capsys):
        self.lib.add_book("Book A", "Author", "STA-1")
        self.lib.add_book("Book B", "Author", "STA-2")
        self.lib.checkout_book("STA-1", "Jan")
        self.lib.statistics()
        captured = capsys.readouterr()
        assert "Checked out    : 1" in captured.out
        assert "Available      : 1" in captured.out

    # ── save / load ──

    def test_save_creates_file(self):
        self.lib.add_book("Persisted", "Author", "PRS-1")
        self.lib.save_catalogue()
        assert os.path.exists("data/test_catalogue.json")

    def test_save_requires_no_pre_existing_directory(self):
        """save_catalogue should create data/ if it doesn't exist."""
        if os.path.exists("data/test_catalogue.json"):
            os.remove("data/test_catalogue.json")
        # Test does not pre-create the directory — the method must handle it
        self.lib.add_book("New Book", "New Author", "NEW-1")
        try:
            self.lib.save_catalogue()
        except FileNotFoundError as e:
            pytest.fail(f"save_catalogue raised FileNotFoundError: {e}")

    def test_load_restores_books(self):
        self.lib.add_book("Remembered", "Author", "REM-1")
        self.lib.save_catalogue()

        fresh = Library()
        fresh.books = []
        fresh.load_catalogue()
        assert len(fresh.books) == 1
        assert fresh.books[0].title == "Remembered"

    def test_load_handles_corrupt_file(self):
        """Corrupted JSON must not crash the app — it should silently recover."""
        os.makedirs("data", exist_ok=True)
        with open("data/test_catalogue.json", "w") as f:
            f.write("{{{not valid json}}}")

        try:
            self.lib.load_catalogue()
        except Exception as e:
            pytest.fail(f"load_catalogue raised an exception on corrupt file: {e}")

        assert isinstance(self.lib.books, list)
