from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


# Request schema: used for POST /api/notes and PUT /api/notes/{id}
class NoteRequest(BaseModel):
    title: str
    content: Optional[str] = ""

    # Ensure title is required, trimmed, and not blank (triggers 422 Unprocessable Entity)
    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Title is required and cannot be blank or whitespace only")
        return trimmed

    # Ensure content defaults to an empty string if null/None is provided
    @field_validator("content")
    @classmethod
    def validate_content(cls, value: Optional[str]) -> str:
        return value if value is not None else ""


# Response schema: used when returning note data to the client
class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    # Enable ORM mode so Pydantic can read data directly from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
