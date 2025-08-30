from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    orders = Column(JSON)  # Changé de 'products' à 'orders'
    created_at = Column(DateTime(timezone=True), server_default=func.now())