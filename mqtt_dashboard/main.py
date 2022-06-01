from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates

from typing import Optional, Any, List
from pathlib import Path

# DATABASE_URL = "sqlite:////infinity/codes/aws/mqtt/mqtt.db"

# import sqlalchemy
# import databases
# from pydantic import BaseModel

# database = databases.Database(DATABASE_URL)
# metadata = sqlalchemy.MetaData()

# sensor_data = sqlalchemy.Table(
#     "sensor_data",
#     metadata,
#     sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
#     sqlalchemy.Column("topic", sqlalchemy.String),
#     sqlalchemy.Column("payload", sqlalchemy.String),
#     sqlalchemy.Column("created_at", sqlalchemy.DateTime),
# )

# engine = sqlalchemy.create_engine(
#     DATABASE_URL, connect_args={"check_same_thread": False}
# )
# metadata.create_all(engine)


# class HomeIoTmodel(BaseModel):
#     id: int
#     topic: str
#     payload: str
#     created_at: str

BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="MIS MQTT Dashboard", openapi_url="/openapi.json")

## https://fastapi.tiangolo.com/tutorial/sql-databases/
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=engine)

import logging
import json

logging.basicConfig(filename='db.log')
# logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

@app.get("/")
def read_data(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_payload_data(db, skip=skip, limit=limit)

    sensor_data = []
    status = ""
    count = 0
    for item in data:
        if not count:
            status = item.status
            count += 1

        sensor_data.append({
            'topic': item.topic,
            'device_id': item.device_id,
            'voltage': item.voltage,
            'current': item.current,
            'power': item.power,
            'created_at': item.created_at,
        })
    
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "sensor_data": sensor_data, "status": status},
    )


@app.post("/update-device-status")
def update_device_status(request: Request):
    pass

# {"msg_id":1001,"id":"test123","data":{"switch_state":"off"}}
# {"msg_id":1006,"id":"test123","data":{"voltage":2222,"current":3,"power":0}}
# @app.get("/", status_code=200)
# def root(request: Request) -> dict:
#     query = sensor_data.select()
#     data = database.fetch_all(query)
#     # print(list(data))
#     return TEMPLATES.TemplateResponse(
#         "index.html",
#         {"request": request, "data": data},
#     )

