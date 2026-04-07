# Plan: Add "list unread" command to Book App

Problem:
- Add a CLI command that shows only unread books (where read is False).

Proposed approach:
1. Add a BookCollection.list_unread() method that returns books with read == False.
2. Add a CLI handler in samples/book-app-project/book_app.py (handle_unread) and map a new command name ("unread" and alias "list-unread") to it. Use existing show_books() to render.
3. Add unit tests verifying BookCollection.list_unread() and CLI behavior.
4. Update README.md to document the new command.

Files to change:
- samples/book-app-project/books.py  (add list_unread())
- samples/book-app-project/book_app.py  (add handler, update commands map and help text)
- samples/book-app-project/tests/test_books.py  (add test_list_unread)
- samples/book-app-project/README.md  (document usage)

Todos:
- add-list-unread-method: Add BookCollection.list_unread() returning unread books
- add-unread-cli-command: Add CLI handler and command mapping for "unread"/"list-unread"
- add-tests-list-unread: Add pytest tests covering list_unread behavior
- update-readme-list-unread: Update README.md to include the new command and examples

Notes/decisions:
- Prefer adding a small collection-level method rather than filtering in CLI to keep logic testable.
- Reuse existing show_books() printing; no changes to utils.py required.
- Keep command name user-friendly: "unread" (short) and support "list-unread" as a longer alias.

Status: Saved to samples/book-app-project/plan.md inside the repository.

Next step: implement the changes after you approve this plan.
