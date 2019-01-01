#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'

import Communicator
from GlobalVariables import *
import socket
import time

class TemperatureError(Exception):
    pass


class Sensor(object):
    #todo Temperaturvorhersage(time)
    def __init__(self, name=None, identifier=None, temperatur=None, memorysize = SENSOR_MEMORYSIZE):
        self._name = None
        self.setName(newname=name)
        self._id = identifier
        self._location = SENSOR_DEVICES_LOCATION + str(identifier) + '/'
        self._temperatur = temperatur
        self.memory = []
        self._memorysize = memorysize
        self.master = None


    def __gt__(self, other):
        """greater than"""
        if type(other) is type(Sensor()):
            return self._name > other.getName()
        elif type(other) is float or type(other) is int or type(other) is long:
            return self.getTemperatur() > other
        else:
            return self._name > other

    def __lt__(self, other):
        """lower than"""
        try:
            comparison = other.getName()
        except AttributeError:
            comparison = other
        return self._name < comparison

    def __eq__(self, other):
        """equal"""
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """not equal"""
        return not self.__eq__(other)

    def __str__(self):
        """returns Sensorname and Temperature"""
        return str("{name:25s}: Temperatur: {temperatur:12s} ID: {id:17s} Master: {master}".format(name=self._name, temperatur=str(self.getTemperatur()), id=str(self._id), master=str(self.master)))

    def html(self):
        """Gibt den Sensor als HTML string zurueck"""
        html = ""
        html +=  '<td>{name}</td>'.format(name=self._name)
        try:
            # Zelle rot faerben, falls sich der wert geaendert hat
            if self.getTemperatur() != self.memory[1][0]:
                html +=  '<td class="BlinkOnChange">{temperatur}</td>'.format(temperatur=self.getTemperatur())
            else:
                html +=  '<td>{temperatur}</td>'.format(temperatur=self.getTemperatur())
        except:
            html +=  '<td>{temperatur}</td>'.format(temperatur=self.getTemperatur())
        html +=  '<td class="identifier">{id}</td>'.format(id=self._id)
        html +=  '<td>{master}</td>'.format(master=self.master)
        return html

    def memoryInsert(self,temperatur):
        """Eintragen der temperatur in ein tuple mit Zeitstempel in eine Memoryliste """
        #Vorübergehend Benötigt durch Klassenänderung (Variable in alter klasse noch nicht vorhanden:
        try:
            self._memorysize is None #Falls fehler durch aufrufen von _memorysize auftritt
        except:
            self._memorysize = SENSOR_MEMORYSIZE
        self.memory.insert(0,(temperatur,time.time()))
        if len(self.memory)>= self._memorysize:
            self.memory = self.memory[:self._memorysize]

    def setID(self,newIdentifier):
        self._id = newIdentifier
        self._location = SENSOR_DEVICES_LOCATION + str(newIdentifier) + '/'

    def setTemperatur(self, newTemperatur):
        # self.temperatur ist eine alte Variable, die jedoch teilweise noch nicht überschrieben wurde
        try:
            del self.temperatur
        except:
            pass
        if type(newTemperatur) is str:
            self._temperatur = newTemperatur
        elif newTemperatur is not None:
            self._temperatur = round(float(newTemperatur),ROUNDED_TEMPERATURE_DIGITS)
            #del temperatur

    def getTemperatur(self):
        # self.temperatur ist eine alte Variable, die jedoch teilweise noch nicht überschrieben wurde
        try:
            return self._temperatur
        except:
            self._temperatur = self.temperatur
            return self._temperatur

    def getID(self):
        return self._id

    def setName(self, newname):
        if newname is None:
            self._name = None
        elif str(newname):
            self._name = str(newname)
        else:
            raise ValueError

    def getName(self):
        return self._name

    def reload_name(self):
        """Reloads the sensor name from the sensor mappings file"""
        sensor_name_exptected = Communicator.load_sensor_name(self.getID())
        self.setName(sensor_name_exptected)

    def refreshTemperatur(self):
        self.setTemperatur(Communicator.GetSensorTemperatur(self.getName()))

    def reset(self):
        self._id = None
        self._location = SENSOR_DEVICES_LOCATION + str(self._id) + '/'
        self._temperatur = None
        self.memory = []
        self.master = None

    def measure(self, msg=False):
        """temperaturmessung"""
        try:
            self._memorysize = SENSOR_MEMORYSIZE
        except Exception as e:
            Communicator.SchreibeFehler(e, 'measure@Sensor')
            print ' Set memorysize hod ned funktionert'
        try:
            # Zeilen aus Datei einlesen !!! DAUERT 0.8 SEKUNDEN pro Sensor!!!!
            messdaten = Communicator.fileReader(dateiName=DATEINAME_MESSDATEN, ordner=self._location, createIfNotExisting=False)
            if "YES" in messdaten[0]:  # Teste ob uebertragung erfolgreich war
                pos = messdaten[1].find("t=") + 2  # Startort des Temperaturwerts ermitteln
                Temperatur = float(messdaten[1][pos:-1]) / 1000  #Temperatur ermitteln
                self.setTemperatur(Temperatur)
            else:
                self.setTemperatur(SENSOR_TRANSMIT_ERROR)
            self.master = socket.gethostname()
        except IOError:
            self.setTemperatur(SENSOR_OFFLINE)
            self.master = None
        finally:
            self.memoryInsert(self.getTemperatur())

        if msg:
            print (self)

    def isLinked(self):
        """testet ob der Sensor am aktuellen raspi angeschlossen ist"""
        w1_master_slaves = Communicator.getSlaveList()  # liest SensorePfade ein
        for line in w1_master_slaves:
            line = Communicator.LineClean(line)
            if line == "notfound.":
                print("Keine Sensoren gefunden!")

        if self.getID() in w1_master_slaves:
            return True
        else:
            return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
