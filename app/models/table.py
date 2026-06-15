from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, func
from sqlalchemy.orm import relationship
from core.database import Base


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wedding_id = Column(Integer, ForeignKey("weddings.id", ondelete="CASCADE"), nullable=False)
    table_number = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)  # 'presidium', 'rectangle', 'double_rectangle', 'round'
    capacity = Column(Integer, nullable=False)
    side = Column(String(50), nullable=False, default='mutual')  # 'bride', 'groom', 'mutual'
    x_pos = Column(Float, nullable=True)   # Դիրք սրահի կտավում (px)
    y_pos = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    wedding = relationship("Wedding", back_populates="tables")
    members = relationship("GuestMember", back_populates="table")