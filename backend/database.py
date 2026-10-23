import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure backend directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Locate and load the backend/.env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Retrieve the DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Raise a clear error if DATABASE_URL is missing
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is missing. Please set it in backend/.env"
    )

# Convert legacy "postgres://" URLs to "postgresql://" for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# If no specific driver is provided in the URL and psycopg (v3) is not installed,
# specify psycopg2 so SQLAlchemy connects using psycopg2-binary
if DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    try:
        import psycopg  # noqa: F401
    except ImportError:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create the SQLAlchemy engine.
# pool_pre_ping=True tests connections before using them to prevent stale connection errors.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal is a factory for generating new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class from which all database models will inherit
Base = declarative_base()


# Dependency function to provide a database session to FastAPI endpoints.
# The session is automatically closed once the request finishes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
