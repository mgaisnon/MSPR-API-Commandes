import os
from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
from . import crud, models, schemas
from .database import SessionLocal, engine
from .rabbitmq import publish_event

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
Instrumentator().instrument(app).expose(app)

API_KEY = os.getenv("API_KEY") 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Clé API invalide")

@app.get("/orders/", response_model=list[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    order = crud.get_order(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order

@app.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    new_order = crud.create_order(db, order)
    try:
        event_data = {key: value for key, value in new_order.__dict__.items() if not key.startswith('_')}
        publish_event("order_created", event_data)
    except Exception as e:
        pass
    return new_order

@app.put("/orders/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    updated = crud.update_order(db, order_id, order)
    if updated is None:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    try:
        event_data = {key: value for key, value in updated.__dict__.items() if not key.startswith('_')}
        publish_event("order_updated", event_data)
    except Exception as e:
        pass
    return updated

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    deleted = crud.delete_order(db, order_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    try:
        publish_event("order_deleted", {"id": order_id})
    except Exception as e:
        pass
    return {"detail": "Commande supprimée"}