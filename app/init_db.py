import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from app import crud, schemas, models

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def init_data():
    db = SessionLocal()
    response = requests.get("https://615f5fb4f7254d0017068109.mockapi.io/api/v1/orders")
    data = response.json()
    for item in data:
        existing = db.query(models.Order).filter(models.Order.id == int(item['id'])).first()
        if not existing:
            customer_id = item.get('customerId') or item.get('customer_id')
            products = item.get('products', [])
            try:
                created_at = datetime.fromisoformat(item['createdAt'].replace('Z', '+00:00'))
            except (KeyError, ValueError):
                created_at = None
            
            order_data = schemas.OrderCreate(
                customer_id=str(customer_id) if customer_id is not None else None,
                products=products,
                created_at=created_at
            )
            crud.create_order(db, order_data)
    db.close()

if __name__ == "__main__":
    init_data()