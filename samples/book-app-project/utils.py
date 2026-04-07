def print_menu():
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


def get_user_choice() -> str:
    return input("Choose an option (1-5): ").strip()


def parse_year(year_input: str):
    """Parse year input into an integer within allowed range.

    Returns a tuple (year, valid) where valid is False for invalid input.
    """
    from datetime import datetime
    current_year = datetime.now().year
    try:
        year = int(year_input)
    except (TypeError, ValueError):
        return None, False
    if 1450 <= year <= current_year:
        return year, True
    return None, False


def get_book_details():
    """Collect book details from user input and return (title, author, year, year_valid).

    This function does not perform any printing; callers should handle display.
    """
    title = input("Enter book title: ").strip()
    author = input("Enter author: ").strip()

    year_input = input("Enter publication year: ").strip()
    year, valid = parse_year(year_input)

    return title, author, year, valid


def display_invalid_year():
    from datetime import datetime
    current = datetime.now().year
    print(f"Invalid year. Please enter an integer between 1450 and {current}.")


def print_books(books):
    if not books:
        print("No books in your collection.")
        return

    print("\nYour Books:")
    for index, book in enumerate(books, start=1):
        status = "✅ Read" if book.read else "📖 Unread"
        print(f"{index}. {book.title} by {book.author} ({book.year}) - {status}")
