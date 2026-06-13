from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Ավելացվել են pool_pre_ping և pool_recycle
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency a session ստանալու համար
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()