import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read the DATABASE_URL from environment variable or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zena.db")

# Create the SQLAlchemy engine
# ONLY use connect_args for SQLite. Remove it for PostgreSQL/MySQL.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Production path for PostgreSQL, etc.
    engine = create_engine(DATABASE_URL)
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for model definitions
Base = declarative_base()

def get_db():
    """Dependency to yield a new database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()