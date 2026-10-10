"""
Database connection and session management.

Supports both SQLite (development) and PostgreSQL (production).
Switch by changing DATABASE_URL in .env file.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# ─── Create SQLAlchemy Engine ───
# For SQLite, we need connect_args={"check_same_thread": False}
# For PostgreSQL, remove this argument
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
    )

# ─── Session Factory ───
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ─── Base Class for All Models ───
class Base(DeclarativeBase):
    """Base class that all ORM models inherit from."""
    pass


# ─── FastAPI Dependency ───
def get_db():
    """
    Dependency function to get database session.

    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
