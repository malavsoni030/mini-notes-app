import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import List
import uuid
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Ensure backend directory is in sys.path so modules import reliably
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Load environment variables from backend/.env if available
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

try:
    from auth import get_current_user_id
    from database import get_db
    from models import Note
    from schemas import NoteRequest, NoteResponse
except ImportError:
    from backend.auth import get_current_user_id
    from backend.database import get_db
    from backend.models import Note
    from backend.schemas import NoteRequest, NoteResponse

# --- Application Setup ---
app = FastAPI(title="Notes API")

# Default allowed origins if CORS_ORIGINS is not set or empty
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def get_allowed_origins() -> List[str]:
    """
    Parse allowed origins from the CORS_ORIGINS environment variable.
    - Expects a comma-separated list of origins.
    - Trims spaces, removes trailing slashes, and ignores empty items.
    - Disallows wildcard '*' for security.
    - Defaults to http://localhost:5173 and http://127.0.0.1:5173 if not set.
    """
    cors_env = os.getenv("CORS_ORIGINS")
    if not cors_env:
        return DEFAULT_ALLOWED_ORIGINS

    origins: List[str] = []
    for item in cors_env.split(","):
        cleaned = item.strip().rstrip("/")
        # Ignore empty items and strictly disallow wildcard "*" for security
        if cleaned and cleaned != "*":
            origins.append(cleaned)

    return origins if origins else DEFAULT_ALLOWED_ORIGINS


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    # Explicitly allow Authorization (for Bearer JWT tokens) and Content-Type (for JSON bodies)
    allow_headers=["Authorization", "Content-Type", "*"],
)


# --- API Endpoints ---

# Health check endpoint (remains public)
@app.get("/")
def health_check():
    """Simple health check endpoint returning status ok (public)."""
    return {"status": "ok"}


# Get all notes belonging to the logged-in user
@app.get("/api/notes", response_model=List[NoteResponse], status_code=status.HTTP_200_OK)
def get_all_notes(
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Fetch all notes belonging to the authenticated user."""
    notes = (
        db.query(Note)
        .filter(Note.user_id == current_user_id)
        .order_by(Note.id.asc())
        .all()
    )
    return notes


# Create a new note
@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new note in the database.
    user_id is set directly from the validated token and cannot be supplied by the client.
    """
    now = datetime.now(timezone.utc)
    new_note = Note(
        title=note_data.title,
        content=note_data.content,
        user_id=current_user_id,
        created_at=now,
        updated_at=now,
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


# Update an existing note
@app.put("/api/notes/{id}", response_model=NoteResponse, status_code=status.HTTP_200_OK)
def update_note(
    id: int,
    note_data: NoteRequest,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update title and content of an existing note by ID.
    Finds the note matching both id AND user_id. Returns 404 if not found.
    Refreshes updated_at to the current UTC time.
    """
    note = (
        db.query(Note)
        .filter(Note.id == id, Note.user_id == current_user_id)
        .first()
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {id} not found",
        )

    note.title = note_data.title
    note.content = note_data.content
    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(note)
    return note


# Delete a note
@app.delete("/api/notes/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    id: int,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Delete a note from the database by its ID.
    Finds the note matching both id AND user_id. Returns 404 if not found.
    """
    note = (
        db.query(Note)
        .filter(Note.id == id, Note.user_id == current_user_id)
        .first()
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {id} not found",
        )

    db.delete(note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
