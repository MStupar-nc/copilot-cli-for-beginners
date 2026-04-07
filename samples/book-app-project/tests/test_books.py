import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pytest
import books
from books import BookCollection


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test by default."""
    temp_file = tmp_path / "data.json"
    # start tests with an empty list on disk
    temp_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    collection.add_book("1984", "George Orwell", 1949)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False


def test_find_by_title_case_insensitive():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    # different casing should still find the book
    found = collection.find_book_by_title("the hobbit")
    assert found is not None
    assert found.title == "The Hobbit"


def test_find_by_author_case_insensitive():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.add_book("The Lord of the Rings", "J.R.R. Tolkien", 1954)
    collection.add_book("Dune", "Frank Herbert", 1965)

    found = collection.find_by_author("j.r.r. tolkien")
    assert len(found) == 2
    titles = {b.title for b in found}
    assert {"The Hobbit", "The Lord of the Rings"} <= titles


def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result is True
    book = collection.find_book_by_title("Dune")
    assert book.read is True


def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert result is False


def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result is True
    book = collection.find_book_by_title("The Hobbit")
    assert book is None


def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert result is False


def test_add_book_empty_title_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book("", "Some Author", 2020)


def test_add_book_whitespace_title_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.add_book("   ", "Some Author", 2020)


def test_mark_as_read_empty_title_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.mark_as_read("")


def test_remove_book_empty_title_raises():
    collection = BookCollection()
    with pytest.raises(ValueError):
        collection.remove_book("")


def test_persistence_to_disk(tmp_path, monkeypatch):
    # Ensure added books are written to the configured DATA_FILE
    data_file = tmp_path / "persist.json"
    monkeypatch.setattr(books, "DATA_FILE", str(data_file))

    col = BookCollection()
    col.add_book("Frankenstein", "Mary Shelley", 1818)
    assert data_file.exists()

    payload = json.loads(data_file.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert payload[0]["title"] == "Frankenstein"


def test_missing_and_corrupted_data_file(tmp_path, monkeypatch, caplog):
    # Missing file -> starts empty
    missing = tmp_path / "missing.json"
    if missing.exists():
        missing.unlink()
    monkeypatch.setattr(books, "DATA_FILE", str(missing))
    col = BookCollection()
    assert col.list_books() == []

    # Corrupted file -> logs warning and starts empty
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("not a json", encoding="utf-8")
    monkeypatch.setattr(books, "DATA_FILE", str(corrupt))
    caplog.clear()
    col2 = BookCollection()
    assert col2.list_books() == []
    assert any("corrupt" in rec.message.lower() or "not valid json" in rec.message.lower() for rec in caplog.records)


def test_get_unread_books_returns_only_unread_books():
    # Arrange
    collection = BookCollection()
    collection.add_book("Book A", "Author 1", 2000)
    collection.add_book("Book B", "Author 2", 2001)
    collection.add_book("Book C", "Author 3", 2002)

    # Act: mark Book B as read
    assert collection.mark_as_read("Book B") is True
    unread = collection.get_unread_books()
    # Assert
    titles = [b.title for b in unread]
    assert titles == ["Book A", "Book C"]


def test_get_unread_books_empty_when_all_read():
    collection = BookCollection()
    collection.add_book("One", "X", 1999)
    collection.add_book("Two", "Y", 2005)
    # Mark all as read
    assert collection.mark_as_read("One") is True
    assert collection.mark_as_read("Two") is True
    assert collection.get_unread_books() == []


def test_get_unread_books_empty_when_no_books():
    collection = BookCollection()
    assert collection.get_unread_books() == []


def test_get_unread_books_preserves_insertion_order():
    collection = BookCollection()
    collection.add_book("First", "A", 2010)
    collection.add_book("Second", "B", 2011)
    collection.add_book("Third", "C", 2012)
    # Mark Second as read, so unread should be First then Third
    assert collection.mark_as_read("Second") is True
    unread_titles = [b.title for b in collection.get_unread_books()]
    assert unread_titles == ["First", "Third"]
