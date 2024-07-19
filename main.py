import json
import time

import wificonnect

# GET CONFIG
f = open('files/config.json', 'r');
config = json.load(f)

ZONES = config['zones'];
SENSORS = config['sensors'];
SOLENOIDS = config['solenoids'];

# CONNECT TO WIFI
WIFI = config['wifi'];

if WIFI['connect']:
    wificonnect.connect_to_wifi(WIFI['ssid'], WIFI['pass'])


def get_sensor_reading(key):
    if not key: return False

    # GET DATA
    if not key in SENSORS:
        print('Sensor with key: '+str(key)+ ' not found')
        return False

    sensor = SENSORS[key]

    if sensor['active'] == False:
        print('Sensor with key: '+ str(key) + ' not active')
        return False
    
    if not 'pin' in sensor:
        print('Sensor with key: '+str(key)+ ' PIN not defined')
        return False

    PIN = sensor['pin'];

    if not PIN: return False
    
    # GET VALUE WITH PIN
    print('Getting moisture value')
    return 20


def activate_solenoid(key, openTime):
    if not key: return False

    # GET DATA
    if not key in SOLENOIDS:
        print('Solenoid with key: '+str(key)+ ' not found')
        return False

    solenoid = SOLENOIDS[key]

    if solenoid['active'] == False:
        print('Solenoid with key: '+ str(key) + ' not active')
        return False

    if not openTime:
        if 'openTime' in solenoid:
            openTime = solenoid['openTime']
        else:
            print('Solenoid with key: '+str(key)+ ' time not defined')
            return False
    
    if not 'pin' in solenoid:
        print('Solenoid with key: '+str(key)+ ' PIN not defined')
        return False

    PIN = solenoid['pin']

    if not PIN: return False

    # ACTIVATE SENSOR AND WHILE FLOW SENSOR IS ALSO ACTIVE
    flow = get_flow()
    # ACTIVATE SOLENOID
    print('Activating solenoid')
    time.sleep(openTime)

    # DEACTIVATE SOLENOID
    print('Deactivating solenoid')

    return flow

def get_flow():
    if not 'flow0' in SENSORS:
        print('Flow sensor not found in config')
        return False
    
    data = SENSORS['flow0']

    if data['active'] == False:
        print('Flow sensor not active')
        return False
    
    if not 'pin' in data:
        print('Flow sensor PIN not defined')
        return False

    PIN = data['pin']

    # GET DATA - HOW MUCH FLOWED WATER
    return 12

# LOOP THROUGH ZONES

if len(ZONES) == 0 or len(SENSORS) == 0 or len(SOLENOIDS) == 0:
    print('Not all data found. Exiting')
    exit()

inactiveZones = 0;
for zoneKey in ZONES:
    zone = ZONES[zoneKey]
    
    if zone['active'] == False:
        inactiveZones =+ 1
        continue

    # LOAD SENSORS
    zoneSensors = zone['sensors']

    if len(zoneSensors) == 0:
        inactiveZones =+ 1
        continue

    sensorReadings = 0
    for sensorKey in zoneSensors:
        val = get_sensor_reading(sensorKey)

        if not val:
            break

        sensorReadings =+ val

    if not sensorReadings > 0: 
        print('Sensor reading all 0')
        break

    
    # GET AVARAGE READING OF MULTIPLE SENSORS
    moisture = sensorReadings / len(zoneSensors);

    # GET MIN MOISTURE OF THE ZONE
    minMoisture = zone['minMoisture']

    if moisture > minMoisture:
        print('Moisture OK')
        continue

    # ACTIVATE SOLENOIDS
    solenoids = zone['solenoids']

    if len(solenoids) == 0:
        print('No defined solenoids for zone')
        break

    totalFlow = 0
    for solenoidKey in solenoids:
        solenoid = solenoids[solenoidKey]

        openTime = 100
        if 'openTime' in solenoid: openTime = solenoid['openTime']

        flow = activate_solenoid(solenoidKey, openTime)

        if not flow:
            break

        totalFlow =+ flow

    if totalFlow == 0:
        print('No water dispensed!')
        break

    # CHECK MIN MAX FLOW
    minFlow = zone['minFlow']
    maxFlow = zone['maxFlow']

    if totalFlow < minFlow:
        print('Shortage of flow with dif: '+ str(totalFlow - minFlow))
    elif totalFlow > maxFlow:
        print('Too much water dispensed with diff: '+ str(totalFlow - maxFlow))


        

# IF NO ACTIVE ZONES
if len(ZONES) == inactiveZones:
    print('All zones inactive')
    exit();



# CHECK TEMP