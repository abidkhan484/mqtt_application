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

    data = ['0'] * 7
    if device_data:
        data[5] = device_data[6]
    if payload['data']:
        if payload['data'].get('switch_state'):
            data[5] = payload['data']['switch_state']
        else:
            data[0] = message.topic
            data[1] = device_id
            data[2] = str(payload['data']['voltage']) if payload['data'].get('voltage') else data[2]
            data[3] = str(payload['data']['current']) if payload['data'].get('current') else data[3]
            data[4] = str(payload['data']['power']) if payload['data'].get('power') else data[4]
            data[5] = str(device_data[5]) if device_data else data[5]

    now = datetime.now()
    data[6] = now.strftime("%m/%d/%Y, %H:%M:%S")
    filtered_data = '","'.join(data)
    sql = f'INSERT INTO sensors_data (topic, device_id, voltage, current, power, status, created_at) VALUES ("{filtered_data}")'
    # else:
    #     sql = f'UPDATE TABLE sensors_data (topic, device_id, voltage, current, power, status, created_at) VALUES ("{filtered_data}") WHERE device_id = {device_id}'
    cursor = db_conn.cursor()
    cursor.execute(sql)
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
    # mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
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

