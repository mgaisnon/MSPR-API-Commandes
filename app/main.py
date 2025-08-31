import os
from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
from . import crud, models, schemas
from .database import SessionLocal, engine
from .rabbitmq import publish_event
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"Vérification de la clé API: {x_api_key}")
    if x_api_key != API_KEY:
        logger.error(f"Clé API invalide: {x_api_key}")
        raise HTTPException(status_code=403, detail="Clé API invalide")
    logger.info("Clé API valide")
    return x_api_key

@app.get("/")
def read_root():
    return {"message": "Bienvenue dans l'API commandes"}

@app.get("/orders/", response_model=list[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    logger.info(f"Requête GET /orders/ reçue avec skip={skip}, limit={limit}")
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders

@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    logger.info(f"Requête GET /orders/{order_id} reçue")
    order = crud.get_order(db, order_id)
    if order is None:
        logger.warning(f"Commande avec ID {order_id} non trouvée")
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return order

@app.post("/orders/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    logger.info(f"Requête POST /orders/ reçue avec données: {order.dict()}")
    new_order = crud.create_order(db, order)
    # Convertir orders en liste si c'est une chaîne JSON
    if isinstance(new_order.orders, str):
        try:
            new_order.orders = json.loads(new_order.orders)
        except Exception as e:
            logger.warning(f"Erreur lors de la conversion JSON de orders pour commande ID {new_order.id}: {str(e)}")
            new_order.orders = []
    try:
        event_data = {key: value for key, value in new_order.__dict__.items() if not key.startswith('_')}
        publish_event("order_created", event_data)
        logger.info(f"Événement order_created publié pour commande ID {new_order.id}")
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement order_created: {str(e)}")
    return new_order

@app.put("/orders/{order_id}", response_model=schemas.Order)
def update_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    logger.info(f"Requête PUT /orders/{order_id} reçue avec données: {order.dict()}")
    updated = crud.update_order(db, order_id, order)
    if updated is None:
        logger.warning(f"Commande avec ID {order_id} non trouvée")
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    # Convertir orders en liste si c'est une chaîne JSON
    if isinstance(updated.orders, str):
        try:
            updated.orders = json.loads(updated.orders)
        except Exception as e:
            logger.warning(f"Erreur lors de la conversion JSON de orders pour commande ID {order_id}: {str(e)}")
            updated.orders = []
    try:
        event_data = {key: value for key, value in updated.__dict__.items() if not key.startswith('_')}
        publish_event("order_updated", event_data)
        logger.info(f"Événement order_updated publié pour commande ID {order_id}")
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement order_updated: {str(e)}")
    return updated

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    logger.info(f"Requête DELETE /orders/{order_id} reçue")
    deleted = crud.delete_order(db, order_id)
    if deleted is None:
        logger.warning(f"Commande avec ID {order_id} non trouvée")
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    try:
        publish_event("order_deleted", {"id": order_id})
        logger.info(f"Événement order_deleted publié pour commande ID {order_id}")
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement order_deleted: {str(e)}")
    return {"detail": "Commande supprimée"}