from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class OrderBase(BaseModel):
    customer_id: Optional[str] = None
    orders: List[Dict] = Field(default_factory=list)

class OrderCreate(OrderBase):
    created_at: Optional[datetime] = None

class OrderUpdate(BaseModel):
    customer_id: Optional[str] = None
    orders: Optional[List[Dict]] = None

class Order(OrderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
