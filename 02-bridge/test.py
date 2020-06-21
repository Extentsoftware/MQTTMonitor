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


def main():
    
    data = '{ "key": 1,"yes":1 }'
    js = json.loads(data)
    print(js);
    geohash = None
    
    if "yes" in js:
        geohash = js["yes"]
    print(geohash)

if __name__ == '__main__':
    print('MQTT to InfluxDB bridge v1.0')
    main()
