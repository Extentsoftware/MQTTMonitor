#!/usr/bin/env python3

"""A MQTT to InfluxDB Bridge

This script receives MQTT data and saves those to InfluxDB.

"""
import os
import math
import decimal
import json
from datetime import date
from datetime import time
from datetime import datetime
import re
from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import requests 

INFLUXDB_ADDRESS = os.environ.get('INFLUXDB_ADDRESS')
#INFLUXDB_ADDRESS = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'home_db'
 
MQTT_PORT= 1883
MQTT_ADDRESS = os.environ.get('MOSQUITTO_ADDRESS')
#MQTT_ADDRESS = 'localhost'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_TOPIC = 'bongo/+/+'  # bongo/[sensor]/[measurement]
MQTT_REGEX = 'bongo/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridgeA'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PASSWORD, None)

def get_sensor_geohash(sensor):
    if sensor in CONFIG["sensors"]:
        sensor_config = CONFIG["sensors"][sensor]
        if "geohash" in sensor_config:
            return sensor_config["geohash"]
    return None

def send_to_farmos(sensor, data):
    if CONFIG["farmos"]["enabled"]:
        if sensor in CONFIG["sensors"]:
            sensor_config = CONFIG["sensors"][sensor]
            if "farmos_privatekey" in sensor_config:
                privatekey = sensor_config["farmos_privatekey"]
                publickey = sensor_config["farmos_publickey"]
                endpoint = CONFIG["farmos"]["address"]
                url = endpoint + publickey + '?private_key=' + privatekey
                print(url)
                r = requests.post(url = url, data = data) 
            else:
                print(sensor, " not configure for farmos" )
        else:
            print(sensor, " does not exist in sensor config file" )

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    process_message(msg.topic, msg.payload)
    
def process_message(topic, payload):
    """The callback for when a PUBLISH message is received from the server."""
    now = datetime.now()
    match = re.match(MQTT_REGEX, topic)
    if match:
        sensor = match.group(1)
        measurement = match.group(2)
        payload = payload.decode('utf-8')
        payload = payload.replace('\\n', '')
        try:
            js = json.loads(payload)

            geohash = None
            if 'geohash' in js:
                geohash = js["geohash"]
            else:
                geohash = get_sensor_geohash(sensor)
            
            json_body = [
                {
                    "measurement": measurement,
                    "tags": {
                        "sensor": sensor,
                        "geohash": geohash
                    },
                    "time": str(now), 
                    "fields": js
                }
            ]        

            send_to_farmos(sensor, payload);

            print(json_body)
            influxdb_client.write_points(json_body)
        except Exception as e:
            print(e)        
    else:
        print( "bad pattern match on topic name" )

def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)

def _init_mqtt():
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message    
    mqtt_client.connect(MQTT_ADDRESS, MQTT_PORT)
    mqtt_client.loop_forever()

def _read_config():
    global CONFIG
    with open('sensors.json') as json_file:
        CONFIG = json.load(json_file)

def main():
    _read_config();
    _init_influxdb_database()
    _init_mqtt()
    

if __name__ == '__main__':
    print('MQTT to InfluxDB bridge v1.3')
    main()
