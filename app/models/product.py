from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from ..core.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    domain = Column(String, index=True)
    title = Column(String)
    currency = Column(String, default="BRL")
    current_price = Column(Float)
    in_stock = Column(Boolean, default=True)
    last_checked_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
