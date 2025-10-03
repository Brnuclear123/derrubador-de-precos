from sqlalchemy import Column, Integer, ForeignKey, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from ..core.db import Base

class Watch(Base):
    __tablename__ = "watches"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    channel = Column(String, nullable=False)  # email | webpush | telegram | discord
    target_price = Column(Float, nullable=True)
    drop_percent = Column(Float, nullable=True)  # ex: 10.0
    endpoint = Column(String, nullable=False)   # email, endpoint VAPID, etc.
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
