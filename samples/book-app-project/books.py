import json
import logging
import os
import tempfile
from dataclasses import dataclass, asdict
from typing import List, Optional

logger = logging.getLogger(__name__)

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False


class BookCollection:
    def __init__(self) -> None:
        self.books: List[Book] = []
        self.load_books()

    def load_books(self) -> None:
        """Load books from the JSON file if it exists.

        If the file is missing, start with an empty collection. If the file
        is corrupted, log a warning and start empty. Unexpected I/O errors
        surface as RuntimeError so callers can handle them.
        """
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
        except FileNotFoundError:
            # No data file yet; start with empty collection.
            self.books = []
        except json.JSONDecodeError:
            logger.warning("%s is corrupted or not valid JSON; starting empty.", DATA_FILE)
            self.books = []
        except Exception as exc:  # unexpected I/O or permission errors
            logger.exception("Unexpected error while loading books from %s", DATA_FILE)
            raise RuntimeError(f"Failed to load books from {DATA_FILE}: {exc}") from exc

    def save_books(self) -> None:
        """Atomically save the current book collection to JSON.

        Writes to a temporary file in the same directory and replaces the
        target path to avoid leaving a partially-written file.
        """
        try:
            dir_name = os.path.dirname(DATA_FILE) or "."
            with tempfile.NamedTemporaryFile("w", delete=False, dir=dir_name, encoding="utf-8") as tmp:
                json.dump([asdict(b) for b in self.books], tmp, indent=2, ensure_ascii=False)
                tmp_name = tmp.name
            os.replace(tmp_name, DATA_FILE)
        except Exception as exc:
            logger.exception("Failed to save books to %s", DATA_FILE)
            # Attempt to remove the temp file if it exists
            try:
                if 'tmp_name' in locals() and os.path.exists(tmp_name):
                    os.remove(tmp_name)
            except Exception:
                logger.debug("Could not remove temporary file %s", locals().get('tmp_name'))
            raise RuntimeError(f"Failed to save books to {DATA_FILE}: {exc}") from exc

    def add_book(self, title: str, author: str, year: int) -> Book:
        """Create and persist a new Book.

        Raises ValueError if title is empty or whitespace or year is invalid.
        """
        if not title or not title.strip():
            raise ValueError("Title must not be empty")
        # Validate year: must be an int between 1450 and current year (no coercion)
        from datetime import datetime
        current_year = datetime.now().year
        if not isinstance(year, int):
            raise ValueError(f"Year must be an integer between 1450 and {current_year}")
        y = year
        if not (1450 <= y <= current_year):
            raise ValueError(f"Year must be between 1450 and {current_year}")
        book = Book(title=title, author=author, year=y)
        self.books.append(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        """Return the list of books. Caller should not modify returned list."""
        return list(self.books)

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Return the first book matching title (case-insensitive), or None."""
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def mark_as_read(self, title: str) -> bool:
        """Mark a book as read by title. Returns True if updated.

        Raises ValueError if title is empty or whitespace.
        """
        if not title or not title.strip():
            raise ValueError("Title must not be empty")
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title. Returns True if removed.

        Raises ValueError if title is empty or whitespace.
        """
        if not title or not title.strip():
            raise ValueError("Title must not be empty")
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self.save_books()
            return True
        return False

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author (case-insensitive)."""
        return [b for b in self.books if b.author.lower() == author.lower()]

    def get_unread_books(self) -> List[Book]:
        """Return a new list of unread books (where read is False)."""
        return [b for b in self.books if not b.read]