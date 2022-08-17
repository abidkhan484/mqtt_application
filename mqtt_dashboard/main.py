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
    device_id = "testdev"
    data = crud.get_payload_data(device_id, db, skip=skip, limit=limit)

    sensor_data = []
    status = crud.get_the_last_status(device_id, db).status
    count = 0
    for item in data:

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

@app.get("/api/device-data/{device_id}/get")
def read_data(device_id, request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_payload_data(device_id, db, skip=skip, limit=limit)

    sensor_data = []
    status = ""
    query_res = crud.get_the_last_status(device_id, db)
    if query_res:
        status = query_res.status
    count = 0
    for item in data:

        sensor_data.append({
            'topic': item.topic,
            'device_id': item.device_id,
            'voltage': item.voltage,
            'current': item.current,
            'power': item.power,
            'created_at': item.created_at,
        })
    return {"status": status, "sensor_data": sensor_data}

@app.get('/api/status/{device_id}/get')
def device_current_status(device_id, request: Request, db: Session = Depends(get_db)):
    result = crud.get_the_last_status(device_id, db)
    status = ''
    if result:
        status = result.status
    return {"status": status}


@app.get("/api/status/{device_id}/update")
def update_device_status(device_id, request: Request, db: Session = Depends(get_db)):
    result = crud.get_the_last_status(device_id, db)
    status = ''
    if result:
        status = result.status

    if status == 'off':
        updated_status = 'on'
    elif status == 'on':
        updated_status = 'off'

    switch_status_command = '''mosquitto_pub -m '{"msg_id":2001,"id":"testdev","data":{"switch_state":"'''+updated_status+'''"}}' -t "apptodev" -h 159.89.163.228 -u misl -P "Mirinfosys"'''

    print(f'command is {switch_status_command}')

    import os
    os.system(switch_status_command)
    return {"message":"Message published successfully."}

@app.get("/api/hourly-data/{date}/{device_id}/get")
def get_device_data_group_hourly(date, device_id, request: Request, db: Session = Depends(get_db)):
    """
    date: format MM-DD-YYYY (e.g 08-11-2022)\n
    device_id: String (e.g testdev)
    """
    result = crud.get_device_data_group_hourly(device_id, date, db)
    resp = dict((date.replace(",", ""), round(avg_voltage, 2)) for date, avg_voltage in result)
    return resp


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

