from sqlalchemy.orm import Session

from . import models, schemas

def get_payload_data(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HomeIoTmodel).order_by(models.HomeIoTmodel.created_at.desc()).offset(skip).limit(limit).all()

def get_the_last_status(db: Session, limit: int = 1):
    return db.query(models.HomeIoTmodel).order_by(models.HomeIoTmodel.created_at.desc()).limit(limit).one()
