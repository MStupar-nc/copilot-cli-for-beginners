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
