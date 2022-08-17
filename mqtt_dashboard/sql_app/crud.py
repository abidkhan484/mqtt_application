from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from . import models, schemas

def get_payload_data(device_id, db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HomeIoTmodel).filter(models.HomeIoTmodel.device_id==device_id).order_by(models.HomeIoTmodel.created_at.desc()).offset(skip).limit(limit).all()

def get_the_last_status(device_id, db: Session, limit: int = 1):
    return db.query(models.HomeIoTmodel).filter(models.HomeIoTmodel.device_id==device_id).order_by(models.HomeIoTmodel.created_at.desc()).limit(limit).first()

def get_device_data_group_hourly(device_id, date, db: Session):
    date = date.replace('-', '/')
    query = db.query(func.substr(models.HomeIoTmodel.created_at,0,15), func.avg(models.HomeIoTmodel.voltage)).filter(func.substr(models.HomeIoTmodel.created_at,0,11)==date).group_by(func.substr(models.HomeIoTmodel.created_at,0,15)).order_by(models.HomeIoTmodel.created_at.desc()).filter(models.HomeIoTmodel.device_id==device_id)
    result = query.all()
    return result
