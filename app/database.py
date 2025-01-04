from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# SQLite database URL
DATABASE_URL = "postgresql://J:123@localhost/music"

# Create the SQLAlchemy engine for the database
engine = create_engine(DATABASE_URL)

# Create a sessionmaker factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all database tables based on the models
Base.metadata.create_all(bind=engine)

# Dependency to manage database sessions in FastAPI


def get_db():
    """
    Dependency to handle database sessions.
    """
    db = SessionLocal()
    try:
        yield db  # Yield the session to the route handler
    finally:
        db.close()
