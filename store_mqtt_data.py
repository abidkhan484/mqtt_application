#! /home/ubuntu/mqtt/env/bin/python3

import paho.mqtt.client as mqtt
import sqlite3
from time import time
from json import loads
from datetime import datetime

 
MQTT_HOST = '18.136.120.199'
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'Python MQTT client'
MQTT_USER = 'misl'
MQTT_PASSWORD = 'Mirinfosys'
TOPIC = '#'
 
DATABASE_FILE = 'mqtt.db'
DB = sqlite3.connect(DATABASE_FILE)
 
def on_connect(mqtt_client, user_data, flags, conn_result):
    mqtt_client.subscribe(TOPIC)
 

def check_if_device_id_exists(device_id):
    db_conn = DB
    sql = """
    SELECT * FROM sensors_data where device_id = ?
    """
    cursor = db_conn.cursor()
    cursor.execute(sql, (device_id,))
    row = cursor.fetchone()
    db_conn.commit()

    return row


def on_message(mqtt_client, user_data, message):
    payload = loads(message.payload.decode('utf-8'))
    db_conn = user_data['db_conn']

    device_id = payload['id']
    device_data = check_if_device_id_exists(device_id)

    data = [None] * 7
    if payload['data']:
        if payload['data'].get('switch_state'):
            data[5] = payload['data']['switch_state']
        else:
            data[1] = message.topic
            data[2] = payload['data']['voltage'] if payload['data'].get('voltage') else device_data[2]
            data[3] = payload['data']['current'] if payload['data'].get('current') else device_data[3]
            data[4] = payload['data']['power'] if payload['data'].get('power') else device_data[4]
            data[5] = device_data[5]

    now = datetime.now()
    device_data[6] = now.strftime("%m/%d/%Y, %H:%M:%S")
    if not device_data:
        sql = 'INSERT INTO sensors_data (topic, voltage, current, power, status, created_at) VALUES (?, ?, ?, ?, ?, ?)'
    else:
        data[0] = device_data[0]
        sql = 'UPDATE TABLE sensors_data (topic, voltage, current, power, status, created_at) VALUES (?, ?, ?, ?, ?, ?)'
    cursor = db_conn.cursor()
    cursor.execute(sql, device_data)
    db_conn.commit()
    cursor.close()
 
 
def main():
    db_conn = DB
    sql = """
    CREATE TABLE IF NOT EXISTS sensors_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        device_id TEXT NOT NULL,
        voltage INT NOT NULL,
        current INT NOT NULL,
        power INT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """
    cursor = db_conn.cursor()
    cursor.execute(sql)
    cursor.close()
 
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.user_data_set({'db_conn': db_conn})
 
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
 
    mqtt_client.connect(MQTT_HOST, MQTT_PORT)
    mqtt_client.loop_forever()
 
 
main()


# sensors_data:
#     id: int primary_key
#     device_id: string
#     topic: string
#     voltage: int
#     current: int
#     power: int
#     created_at: timestamp
# device_status:
#     id: int primary_key
#     device_id: string
#     status: enum (ON/ OFF)
#     created_at: timestamp

