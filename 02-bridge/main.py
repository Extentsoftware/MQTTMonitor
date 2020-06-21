#!/usr/bin/env python3

"""A MQTT to InfluxDB Bridge

This script receives MQTT data and saves those to InfluxDB.

"""
import math
import json
from datetime import date
from datetime import time
from datetime import datetime
import re
from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

INFLUXDB_ADDRESS = 'influxdb'
#INFLUXDB_ADDRESS = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'home_db'
 
MQTT_PORT= 1883
MQTT_ADDRESS = 'mosquitto'
#MQTT_ADDRESS = 'localhost'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_TOPIC = 'bongo/+/+'  # bongo/[sensor]/[measurement]
MQTT_REGEX = 'bongo/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridgeA'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PASSWORD, None)

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    now = datetime.now()
    print(now)
    match = re.match(MQTT_REGEX, msg.topic)
    if match:
        sensor = match.group(1)
        measurement = match.group(2)
        payload = msg.payload.decode('utf-8')
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
        print( "got json" )
        influxdb_client.write_points(json_body)
    else:
        print( "bad pattern match on topic name" )

def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)


def main():
    _init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, MQTT_PORT)
    mqtt_client.loop_forever()

if __name__ == '__main__':
    print('MQTT to InfluxDB bridge v1.0')
    main()
