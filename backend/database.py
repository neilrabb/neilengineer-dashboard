import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# For development, we'll use a local SQLite database.
# The DATABASE_URL environment variable will be used to configure the database.
# If it's not set, we default to a local SQLite file.
# Example for PostgreSQL: DATABASE_URL="postgresql://user:password@host:port/database"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tonight-in-town.db")

# The connect_args are only needed for SQLite.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI routes to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
