from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, Integer, Text, Uuid

try:
    from database import Base
except ImportError:
    from backend.database import Base


class Note(Base):
    """
    SQLAlchemy ORM model mapping to the existing Supabase 'notes' table.
    Columns:
      - id: bigint identity primary key
      - title: text, not null
      - content: text, not null (defaults to empty string)
      - created_at: timestamptz, not null
      - updated_at: timestamptz, not null
      - user_id: uuid, nullable (foreign key to auth.users in Supabase)
    """
    __tablename__ = "notes"

    # In PostgreSQL/Supabase this is bigint identity primary key.
    # with_variant(Integer, "sqlite") ensures compatibility if tested locally with SQLite.
    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False, default="")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    user_id = Column(Uuid, nullable=True, index=True)
