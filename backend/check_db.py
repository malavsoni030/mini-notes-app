import sys
from pathlib import Path
from sqlalchemy import text

# Ensure backend directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from database import SessionLocal
    from models import Note
except ImportError:
    from backend.database import SessionLocal
    from backend.models import Note


def main():
    """
    Standalone verification script:
    1. Connects to the database and runs 'SELECT 1'.
    2. Prints 'Database connection OK'.
    3. Queries and prints the number of rows in the 'notes' table.
    4. On failure, catches the exception and prints the error type and message.
    """
    try:
        # Open a database session
        db = SessionLocal()
        try:
            # Verify connectivity with a simple query
            db.execute(text("SELECT 1"))

            # Count rows in the notes table
            note_count = db.query(Note).count()

            print("Database connection OK")
            print(f"Number of rows in notes: {note_count}")
        finally:
            db.close()
    except Exception as exc:
        # Output error type and message on failure (credentials/DATABASE_URL are never logged)
        print(f"{type(exc).__name__}: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
