#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'

import Communicator
import Sensor

class SensorListe(list, object):
    def __init__(self, iterableInput=None):
        if not iterableInput:
            iterableInput = []
        for element in iterableInput:
            self.append(element)
            if iterableInput.count(element) > 1: # entferne doppelten input
                iterableInput.remove(element)
        iterableInput.sort()
        super(SensorListe,self).__init__(iterableInput) #CHECK ICH NEEED

    def __contains__(self, item):
        """Gibt True zurueck falls name oder Id der uebereinstimmt"""
        try:
            if item.getID() in self.getAllIDs():
                return True
        except:
            pass
        try:
            if item.getName() in self.getAllNames():
                return True
        except:
            pass
        if item in self.getAllIDs():
            return True
        elif item in self.getAllNames():
            return True
        elif super(SensorListe,self).__contains__(item):
            return True

        return False

    def __str__(self):
        """Gibt einen String des Inhaltes zurueck"""
        string = ""
        for sensor in self:
            string += str(sensor) + "\n"
        return string

    def append(self, p_object):
        """fuegt Sensor hinzu, falls dessen name noch nicht existiert, ansonsten wird der existierende ueberschrieben"""
        # Test ob das Eingangsobjekt von der Klasse Sensor ist
        if not p_object.__class__.__name__ == Sensor.Sensor.__name__:
            print ("Typen in SensorListe.append passen nicht zusammen: ")
            print (Sensor.Sensor.__name__)
            print (p_object.__class__.__name__)
            raise TypeError
        # Falls SensorID bereits vorhanden ist: nicht aufnehmen
        if p_object.getID() in self:
            oldSensor = self.getSensor(identifier=p_object.getID())
            self[self.index(oldSensor)]=p_object
        else:
            super(SensorListe,self).append(p_object)

    def getSensorName(self, identifier = None, sensor = None, name = None):
        """gibt den Namen zu einer SensorId zurueck"""
        # Erst absuchen nach normalen Werten
        if identifier is not None:
            for listedSensor in self:
                if listedSensor.getID() == identifier:
                    return listedSensor.getName()
        elif sensor is not None:
            for listedSensor in self:
                if listedSensor is sensor:
                    return sensor.getName()
        elif name is not None:
            for listedSensor in self:
                if listedSensor.getName() == name:
                    return listedSensor.getName()
        # Dann absuchen ob vllt nach None gesucht wird
        try:
            for listedSensor in self:
                if listedSensor.getID() == identifier:
                    return listedSensor.getName()
        except:
            pass
        try:
            for listedSensor in self:
                if listedSensor is sensor:
                    return listedSensor.getName()
        except:
            pass
        try:
            for listedSensor in self:
                if listedSensor.getName() == name:
                    return listedSensor.getName()
        except:
            pass
        raise KeyError()

    def getSensorID(self, identifier = None, sensor = None, name = None):
        """gibt die ID zu einer SensorId zurueck"""
        # Erst absuchen nach normalen Werten
        if identifier is not None:
            for listedSensor in self:
                if listedSensor.getID() == identifier:
                    return listedSensor.getID()
        elif sensor is not None:
            for listedSensor in self:
                if listedSensor is sensor:
                    return sensor.getID()
        elif name is not None:
            for listedSensor in self:
                if listedSensor.getName() == name:
                    return listedSensor.getID()
        # Dann absuchen ob vllt nach None gesucht wird
        try:
            for listedSensor in self:
                if listedSensor.getID() == identifier:
                    return listedSensor.getID()
        except:
            pass
        try:
            for listedSensor in self:
                if listedSensor is sensor:
                    return listedSensor.getID()
        except:
            pass
        try:
            for listedSensor in self:
                if listedSensor.getName() == name:
                    return listedSensor.getID()
        except:
            pass
        raise KeyError()

    def getSensor(self, identifier=None, sensor=None, name=None):
        """gibt die ID zu einer SensorId zurueck"""
        assert identifier is None or sensor is None or name is None, "Only 1 identification argument allowed"

        # Erst absuchen nach normalen Werten
        if identifier is not None:
            for listedSensor in self:
                if listedSensor.getID() == identifier:
                    return listedSensor
        elif sensor is not None:
            for listedSensor in self:
                if listedSensor is sensor:
                    return sensor
        elif name is not None:
            for listedSensor in self:
                if listedSensor.getName() == name:
                    return listedSensor
                    
        raise KeyError("Sensor id:{id} name:{name} obj:{obj} not found in sensorlist".format(id=identifier, name=name, obj=sensor))

    def getAllIDs(self):
        """gibt alle SensorIDs als Liste zurueck"""
        IDList = []
        for sensor in self:
            IDList.append(sensor.getID())
        return IDList

    def getAllNames(self):
        """gibt alle SensorNamen als Liste zurueck"""
        NameList = []
        for sensor in self:
            NameList.append(sensor.getName())
        return NameList

    def getAllSensors(self):
        sensorList = []
        for sensor in self:
            sensorList.append(sensor)
        return sensorList

    def getAllTemperatures(self):
        """Gibt alle Temperaturen als Liste mit absteigenden werten zurueck"""
        # self.refreshAllSensorTemperatures()
        TemperaturList = []
        for sensor in [sensor for sensor in self if sensor.getTemperatur() is not None] :
            try:
                TemperaturList.append(float(sensor.getTemperatur()))
            except ValueError:
                pass
            except TypeError as e:
                print (str(e), 'at: {sensorwert}'.format(sensorwert=sensor.getTemperatur()))

        TemperaturList.sort(reverse=True)
        return TemperaturList

    def refreshAllSensorTemperatures(self):
        """Diese Funktion muss aufgerufen werden, damit die Sensoren ihre Temperaturen aktualisieren"""
        for sensor in self:
            sensor.refreshTemperatur()

    def html(self):
        """Gibt die Sensor als HTML string zurueck"""
        html = ''
        for sensor in sorted(self):
            html += ('<tr id="{sensorname}">{sensor}</tr>\n'.format(sensorname=sensor.getName() , sensor=sensor.html()))
        return html

def main():
    pass

if __name__ == "__main__":
    main()