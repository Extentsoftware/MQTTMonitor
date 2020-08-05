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

FARMOS_API_ENDPOINT = "https://Bongo.azurefd.net/farm/sensor/listener/"


influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PASSWORD, None)


def send_to_farmos(sensor, data):
    privatekey = '4665a2572dd9190b78eb19745a13b8b0'
    publickey = '44d91434490a4711a6dac50f5cc31dee'
    url = FARMOS_API_ENDPOINT + publickey + '?private_key=' + privatekey
    print(url)
    r = requests.post(url = url, data = data) 

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))
    now = datetime.now()
    print(now)
    process_message(msg.topic, msg.payload)
    
def process_message(topic, payload):
    """The callback for when a PUBLISH message is received from the server."""
    print(topic + ' ' + str(payload))
    now = datetime.now()
    print(now)
    match = re.match(MQTT_REGEX, topic)
    if match:
        sensor = match.group(1)
        measurement = match.group(2)
        payload = payload.decode('utf-8')
        payload = payload.replace('\\n', '')
        print(payload)
        try:
            js = json.loads(payload)
            geohash = None
            if 'geohash' in js:
                geohash = js["geohash"]
                print( 'geohash: ' + geohash )
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

            print('Write to Influx')
            print(json_body)
            influxdb_client.write_points(json_body)
        except Exception as e:
            print("Oops!  That was no valid number.  Try again...")        
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

def main():
    _init_influxdb_database()
    _init_mqtt()
    

if __name__ == '__main__':
    print('MQTT to InfluxDB bridge v1.2')
    main()
