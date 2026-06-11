import re
import secrets

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from core.database import Base


def _generate_token() -> str:
    """Ստեղծում է cryptographically secure 32-բայթ token (URL-safe)."""
    return secrets.token_urlsafe(32)


def _slugify(text: str) -> str:
    """'Արամ և Աննա' → 'aram-ev-anna'  (ASCII fallback)."""
    text = text.lower().strip()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^\w-]", "", text, flags=re.ASCII)
    text = re.sub(r"-+", "-", text)
    return text or "wedding"


class Wedding(Base):
    __tablename__ = "weddings"

    id         = Column(Integer,      primary_key=True, autoincrement=True)
    title      = Column(String(255),  nullable=False)
    slug       = Column(String(255),  nullable=False, unique=True, index=True)
    token      = Column(String(64),   nullable=False, unique=True, index=True)
    created_at = Column(DateTime,     server_default=func.now())

    tables  = relationship("Table",  back_populates="wedding", cascade="all, delete-orphan")
    guests  = relationship("Guest",  back_populates="wedding", cascade="all, delete-orphan")