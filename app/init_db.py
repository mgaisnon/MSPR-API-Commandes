import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from . import crud, schemas, models

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def init_data():
    db = SessionLocal()
    try:
        response = requests.get("https://615f5fb4f7254d0017068109.mockapi.io/api/v1/orders")
        response.raise_for_status()  # Vérifie si la requête a réussi
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
                
                # Adapter les produits pour correspondre au schéma attendu
                formatted_products = [
                    {
                        'name': product.get('name'),
                        'details': {
                            'price': float(product.get('details', {}).get('price', 0.0)),
                            'description': product.get('_details', {}).get('description', ''),
                            'color': product.get('details', {}).get('color', '')
                        },
                        'stock': int(product.get('stock', 0)),
                        'id': product.get('id'),
                        'orderId': product.get('orderId')
                    } for product in products
                ]
                
                order_data = schemas.OrderCreate(
                    customer_id=str(customer_id) if customer_id is not None else None,
                    orders=formatted_products,  # Utilisation de 'orders' pour correspondre au schéma
                    created_at=created_at
                )
                crud.create_order(db, order_data)
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des données : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_data()