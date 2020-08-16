# Thermoberry
Heizungsprogramm für 3 Warmwasserpuffer, Mischer und 2 Pumpen


This Programm runs on 2 Raspberries. 
It takes Data from 1-Wire-Temperature Sensors and controls the heating Temperature.

visit the Heater-Website at http://weber.noip.me:62001/website/heizung.html

... More Information will follow ...


## Configuration Files

There are following configuration files

### settings.ini
Contains server an machine information

```ini
; settings.ini
[DEFAULT]
MACHINE_NAME = raspi2
DATA_SERVER_ADDRESS = raspi2
DATA_SERVER_PORT = 7070
PATH_TO_SOFTWARE = /media/mainusb

; Achtung bezueglich der Reihenfolge!
[MODULES] ; all the modules to start
Datenserver = True
SensorAuswertung = True
Mischer = True
PufferSteuerung = True
PufferSteuerungRaspi1 = False
DatenbankModul = False

```

### sensor_mapping.ini
Contains sensor id to name assignments

```ini
; sensor_mapping.ini
; Diese Datei enthält das mapping zwischen den ids der sensoren und ihrem Namen bzw. Zuständigkeit
[DEFAULT]
28-0004633651ff = SensorAussentemperatur
28-00044a21bcff = SensorMischerKeller
28-0004641778ff = SensorPufferHeizraum1
28-00044c86b7ff = SensorPufferHeizraum2
28-0004633961ff = SensorPufferHeizraum3
28-0004612509ff = SensorPufferHeizraum4
28-0004633827ff = SensorPufferHeizung1
28-00046335f6ff = SensorPufferHeizung2
28-00044e6b6dff = SensorPufferHeizung3
28-00044c86c8ff = SensorPufferHeizung4
28-00044e6cc1ff = SensorPufferHygiene1
28-00044e7371ff = SensorPufferHygiene2
28-00044e7edbff = SensorPufferHygiene3
28-00044e75daff = SensorPufferHygiene4
```

