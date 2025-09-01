from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_order(db: Session, order_id: int):
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if order:
            logger.info(f"Recherche de la commande avec ID {order_id}: trouvé")
            if isinstance(order.orders, str):
                try:
                    order.orders = json.loads(order.orders)
                except Exception:
                    logger.warning(f"Champ 'orders' n'est pas un JSON valide pour la commande {order_id}")
        else:
            logger.info(f"Recherche de la commande avec ID {order_id}: non trouvé")
        return order
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de la commande avec ID {order_id}: {str(e)}")
        raise

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    try:
        orders = db.query(models.Order).offset(skip).limit(limit).all()
        logger.info(f"Récupération des commandes (skip={skip}, limit={limit}): {len(orders)} trouvées")
        for order in orders:
            if isinstance(order.orders, str):
                try:
                    order.orders = json.loads(order.orders)
                except Exception:
                    logger.warning(f"Champ 'orders' n'est pas un JSON valide pour la commande {order.id}")
        return orders
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des commandes: {str(e)}")
        raise

def create_order(db: Session, order: schemas.OrderCreate):
    try:
        data = order.dict(exclude_unset=True)
        if "orders" in data and not isinstance(data["orders"], str):
            data["orders"] = json.dumps(data["orders"])
        db_order = models.Order(**data)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        logger.info(f"Commande créée avec ID {db_order.id}")
        return db_order
    except IntegrityError:
        db.rollback()
        logger.warning("Erreur d'intégrité lors de la création de la commande")
        raise ValueError("Erreur lors de la création de la commande")
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la création de la commande: {str(e)}")
        raise

def update_order(db: Session, order_id: int, order: schemas.OrderUpdate):
    try:
        db_order = get_order(db, order_id)
        if not db_order:
            logger.info(f"Commande avec ID {order_id} non trouvée pour la mise à jour")
            return None
        updates = order.dict(exclude_unset=True)
        if "orders" in updates and not isinstance(updates["orders"], str):
            updates["orders"] = json.dumps(updates["orders"])
        for key, value in updates.items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
        logger.info(f"Commande avec ID {order_id} mise à jour avec succès")
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la mise à jour de la commande avec ID {order_id}: {str(e)}")
        raise

def delete_order(db: Session, order_id: int):
    try:
        db_order = get_order(db, order_id)
        if db_order:
            db.delete(db_order)
            db.commit()
            logger.info(f"Commande avec ID {order_id} supprimée avec succès")
            return db_order
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la suppression de la commande avec ID {order_id}: {str(e)}")
        raise