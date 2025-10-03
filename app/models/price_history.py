from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from ..core.db import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    price = Column(Float, nullable=False)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
