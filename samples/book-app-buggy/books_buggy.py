import json
from dataclasses import dataclass, asdict
from typing import List, Optional

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self.load_books()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            self.books = []
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []

    def save_books(self):
        """Save the current book collection to JSON."""
        # BUG 2: Doesn't handle file permission errors - crashes silently
        f = open(DATA_FILE, "w")
        json.dump([asdict(b) for b in self.books], f, indent=2)
        # Missing f.close() - file handle leak

    def add_book(self, title: str, author: str, year: int) -> Book:
        # BUG 3: Year validation accepts negative numbers and future years
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Find a book by title using a case-insensitive, trimmed comparison.

        This avoids mismatches from casing or extra whitespace.
        """
        if title is None:
            return None

        target = title.strip().lower()
        for book in self.books:
            if book.title.strip().lower() == target:
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        """Mark a single matching book as read. Returns True if updated."""
        if not title or not title.strip():
            raise ValueError("Title must not be empty")
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        # BUG 4: Uses 'in' check - removing "Dune" also matches "Dune Messiah"
        for book in self.books:
            if title in book.title:
                self.books.remove(book)
                self.save_books()
                return True
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author.

        Performs a case-insensitive substring match so partial names match
        (e.g., "Tolkien" matches "J.R.R. Tolkien").
        """
        if not author:
            return []
        target = author.strip().lower()
        return [b for b in self.books if target in b.author.strip().lower()]
