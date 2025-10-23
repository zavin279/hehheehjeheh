# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read the DATABASE_URL from environment variable or default to SQLite
# NOTE: The default SQLite URL will only work in a local environment!
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zena.db")

# Create the SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    # This block is for local development only
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # This block will run on Vercel with a remote database URL
    # Use 'postgresql+psycopg2' for explicit driver
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